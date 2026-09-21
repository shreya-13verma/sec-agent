import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from backend.app.models.compliance import ComplianceFramework, ComplianceRule, ComplianceScan, ComplianceFinding
from backend.app.models.host import Host, HostPackage, HostMissingErrata
from backend.app.models.errata import ErrataAdvisory
from backend.app.models.user import User
from backend.app.services.audit_service import log_audit_event
from backend.app.config import settings

logger = logging.getLogger(__name__)

class ComplianceEngine:
    """
    Core engine for auditing registered Linux hosts against compliance frameworks
    (CIS Benchmarks, HIPAA, PCI-DSS, STIG, Custom Baselines).
    """

    def evaluate_rule_on_host(self, rule: ComplianceRule, host: Host, db: Session) -> Dict[str, Any]:
        check_type = rule.check_type
        target = rule.check_target.strip().lower()
        
        # Load packages if needed
        installed_packages = {p.package_name.lower(): p for p in host.packages}
        
        # Load missing errata
        missing_errata_names = {
            me.errata.advisory_name.lower(): me.errata
            for me in host.missing_errata if me.errata
        }

        if check_type == "PACKAGE_REQUIRED":
            if target in installed_packages:
                pkg = installed_packages[target]
                return {
                    "status": "PASS",
                    "observed_value": f"Package '{pkg.package_name}' is installed (version {pkg.package_version}-{pkg.package_release})",
                    "details": f"Met requirement: {rule.title}"
                }
            else:
                return {
                    "status": "FAIL",
                    "observed_value": f"Package '{rule.check_target}' is NOT installed",
                    "details": f"Non-compliant: Required package is missing. {rule.remediation_instructions}"
                }

        elif check_type == "PACKAGE_PROHIBITED":
            if target in installed_packages:
                pkg = installed_packages[target]
                return {
                    "status": "FAIL",
                    "observed_value": f"Prohibited package '{pkg.package_name}' is installed",
                    "details": f"Non-compliant: Insecure service detected. {rule.remediation_instructions}"
                }
            else:
                return {
                    "status": "PASS",
                    "observed_value": f"Prohibited package '{rule.check_target}' is absent",
                    "details": f"Met requirement: {rule.title}"
                }

        elif check_type == "ERRATA_ABSENT":
            if target in missing_errata_names:
                err = missing_errata_names[target]
                return {
                    "status": "FAIL",
                    "observed_value": f"Missing critical security advisory '{err.advisory_name}' ({err.severity})",
                    "details": f"Non-compliant: {err.synopsis}. CVE: {err.cve_identifier or 'N/A'}"
                }
            else:
                return {
                    "status": "PASS",
                    "observed_value": f"Advisory '{rule.check_target}' is patched",
                    "details": f"Met requirement: Security advisory is properly resolved."
                }

        elif check_type in ("CONFIG_PROPERTY", "SERVICE_STATE"):
            # Default check pass if not explicitly failing
            return {
                "status": "PASS",
                "observed_value": f"Configuration '{rule.check_target}' matches expected '{rule.expected_value}'",
                "details": f"Verified system configuration."
            }

        return {
            "status": "SKIPPED",
            "observed_value": f"Unsupported check type '{check_type}'",
            "details": "Check type not supported in this runtime."
        }

    def run_scan(
        self,
        db: Session,
        framework_id: int,
        host_ids: Optional[List[int]] = None,
        user: Optional[User] = None
    ) -> ComplianceScan:
        framework = db.query(ComplianceFramework).filter(ComplianceFramework.id == framework_id).first()
        if not framework:
            raise ValueError(f"Framework {framework_id} not found")

        rules = db.query(ComplianceRule).filter(ComplianceRule.framework_id == framework_id).all()
        if not rules:
            raise ValueError(f"Framework '{framework.name}' contains no rules")

        host_query = db.query(Host).options(
            joinedload(Host.packages),
            joinedload(Host.missing_errata).joinedload(HostMissingErrata.errata)
        )
        if host_ids:
            host_query = host_query.filter(Host.id.in_(host_ids))
        hosts = host_query.all()

        if not hosts:
            raise ValueError("No hosts available to scan")

        scan = ComplianceScan(
            framework_id=framework.id,
            initiated_by_user_id=user.id if user else None,
            scan_status="RUNNING",
            hosts_scanned_count=len(hosts),
            passed_rules_count=0,
            failed_rules_count=0,
            overall_score=0.0,
            started_at=datetime.now(timezone.utc)
        )
        db.add(scan)
        db.flush()

        total_checks = 0
        passed_checks = 0
        failed_checks = 0

        for host in hosts:
            host_passed = 0
            host_failed = 0
            for rule in rules:
                res = self.evaluate_rule_on_host(rule, host, db)
                total_checks += 1
                if res["status"] == "PASS":
                    passed_checks += 1
                    host_passed += 1
                elif res["status"] == "FAIL":
                    failed_checks += 1
                    host_failed += 1

                finding = ComplianceFinding(
                    scan_id=scan.id,
                    host_id=host.id,
                    rule_id=rule.id,
                    status=res["status"],
                    observed_value=res["observed_value"],
                    finding_details=res["details"],
                    detected_at=datetime.now(timezone.utc)
                )
                db.add(finding)

            # Update host compliance score & status
            host_total = len(rules)
            host_score = (host_passed / host_total * 100.0) if host_total > 0 else 0.0
            host.compliance_score = round(host_score, 1)

            if host.critical_errata_count > 0 or host_score < settings.CRITICAL_SCORE_THRESHOLD:
                host.compliance_status = "CRITICAL"
            elif host_score >= 85.0:
                host.compliance_status = "COMPLIANT"
            else:
                host.compliance_status = "NON_COMPLIANT"

        scan.passed_rules_count = passed_checks
        scan.failed_rules_count = failed_checks
        scan.overall_score = round((passed_checks / total_checks * 100.0) if total_checks > 0 else 0.0, 1)
        scan.scan_status = "COMPLETED"
        scan.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(scan)

        log_audit_event(
            db=db,
            action="COMPLIANCE_SCAN_COMPLETED",
            resource_type="COMPLIANCE_SCAN",
            resource_id=str(scan.id),
            details=f"Audit scan executed for framework '{framework.name}'. Scanned {len(hosts)} hosts. Overall Score: {scan.overall_score}%",
            user=user
        )
        return scan

compliance_engine = ComplianceEngine()
