import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session, joinedload
from backend.app.models.agent import AgentAnalysis, AgentThoughtStep
from backend.app.models.remediation import RemediationPlan, RemediationStep
from backend.app.models.compliance import ComplianceFramework, ComplianceRule, ComplianceFinding
from backend.app.models.host import Host, HostMissingErrata, HostPackage
from backend.app.models.user import User
from backend.app.services.audit_service import log_audit_event

logger = logging.getLogger(__name__)

class AutonomousAgentEngine:
    """
    Multi-step Autonomous Reasoning Engine for Linux Fleet Security Posture,
    Drift Detection, and Remediation Plan Synthesis.
    """

    def analyze_host(
        self,
        db: Session,
        host_id: int,
        framework_id: Optional[int] = None,
        user: Optional[User] = None
    ) -> AgentAnalysis:
        host = db.query(Host).options(
            joinedload(Host.packages),
            joinedload(Host.missing_errata).joinedload(HostMissingErrata.errata),
            joinedload(Host.channels)
        ).filter(Host.id == host_id).first()

        if not host:
            raise ValueError(f"Host with ID {host_id} not found")

        # Pick default framework if not provided
        if not framework_id:
            framework = db.query(ComplianceFramework).filter(ComplianceFramework.code == "CIS_SLES_15").first()
            if not framework:
                framework = db.query(ComplianceFramework).first()
            if not framework:
                raise ValueError("No compliance framework configured")
            framework_id = framework.id
        else:
            framework = db.query(ComplianceFramework).filter(ComplianceFramework.id == framework_id).first()
            if not framework:
                raise ValueError(f"Framework {framework_id} not found")

        # Create Agent Analysis Session
        analysis = AgentAnalysis(
            host_id=host.id,
            framework_id=framework.id,
            analysis_status="ANALYZING",
            drift_detected=False,
            root_cause_summary="",
            created_at=datetime.now(timezone.utc)
        )
        db.add(analysis)
        db.flush()

        thought_steps: List[AgentThoughtStep] = []
        step_order = 1

        # Step 1: Observation
        installed_names = [p.package_name.lower() for p in host.packages]
        missing_errata_list = [me.errata for me in host.missing_errata if me.errata]
        
        obs_text = (
            f"Observed Host '{host.hostname}' (OS: {host.os_family} {host.os_version}, IP: {host.ip_address}). "
            f"Identified {len(host.packages)} installed packages, {len(host.channels)} active channels, "
            f"and {len(missing_errata_list)} missing errata advisories."
        )
        thought_steps.append(
            AgentThoughtStep(
                analysis_id=analysis.id,
                step_order=step_order,
                thought_type="OBSERVATION",
                thought_content=obs_text,
                created_at=datetime.now(timezone.utc)
            )
        )
        step_order += 1

        # Step 2: Correlation & Drift Detection
        drift_items = []
        crit_errata = [e for e in missing_errata_list if e.severity == "Critical"]
        if crit_errata:
            drift_items.append(f"{len(crit_errata)} unpatched Critical Errata ({', '.join(e.advisory_name for e in crit_errata)})")
        
        insecure_services = []
        for pkg_name in ["telnet", "rsh-server", "rsh"]:
            if pkg_name in installed_names:
                insecure_services.append(pkg_name)
        if insecure_services:
            drift_items.append(f"Insecure legacy services detected: {', '.join(insecure_services)}")

        missing_security_tools = []
        for sec_tool in ["audit", "firewalld"]:
            if sec_tool not in installed_names:
                missing_security_tools.append(sec_tool)
        if missing_security_tools:
            drift_items.append(f"Required security baselines missing: {', '.join(missing_security_tools)}")

        has_drift = len(drift_items) > 0
        analysis.drift_detected = has_drift
        
        corr_text = (
            f"Correlation analysis against {framework.name}: "
            + (f"Drift detected with {len(drift_items)} core anomalies: {'; '.join(drift_items)}." if has_drift else "Host configuration matches desired security baseline.")
        )
        thought_steps.append(
            AgentThoughtStep(
                analysis_id=analysis.id,
                step_order=step_order,
                thought_type="CORRELATION",
                thought_content=corr_text,
                created_at=datetime.now(timezone.utc)
            )
        )
        step_order += 1

        # Step 3: Risk Evaluation
        risk_level = "LOW"
        if crit_errata or "telnet" in insecure_services or "rsh-server" in insecure_services:
            risk_level = "CRITICAL"
        elif missing_security_tools or missing_errata_list:
            risk_level = "HIGH"

        risk_text = (
            f"Risk Assessment: Calculated overall host threat level as {risk_level}. "
            f"CVSS impact is heightened by exposed network services and missing cryptographic patches."
        )
        thought_steps.append(
            AgentThoughtStep(
                analysis_id=analysis.id,
                step_order=step_order,
                thought_type="RISK_EVALUATION",
                thought_content=risk_text,
                created_at=datetime.now(timezone.utc)
            )
        )
        step_order += 1

        # Step 4: Decision & Staged Remediation Plan Synthesis
        remediation_actions = []
        
        # Action 1: Remove insecure services first
        for svc in insecure_services:
            remediation_actions.append({
                "type": "REMOVE_PACKAGE",
                "target": svc,
                "params": "purge_config=true",
                "desc": f"Purge insecure package '{svc}' to close cleartext authentication risk"
            })

        # Action 2: Install required security modules
        for tool in missing_security_tools:
            remediation_actions.append({
                "type": "INSTALL_PACKAGE",
                "target": tool,
                "params": "auto_enable_service=true",
                "desc": f"Install and activate required compliance tool '{tool}'"
            })

        # Action 3: Apply errata
        for err in missing_errata_list:
            remediation_actions.append({
                "type": "APPLY_ERRATA",
                "target": err.advisory_name,
                "params": f"cve={err.cve_identifier or 'none'}",
                "desc": f"Apply security advisory '{err.advisory_name}' ({err.severity})"
            })

        decision_text = (
            f"Decision: Synthesized structured remediation strategy with {len(remediation_actions)} actionable steps. "
            f"Plan is staged for human review per controlled remediation policy."
        )
        thought_steps.append(
            AgentThoughtStep(
                analysis_id=analysis.id,
                step_order=step_order,
                thought_type="DECISION",
                thought_content=decision_text,
                created_at=datetime.now(timezone.utc)
            )
        )

        db.add_all(thought_steps)
        analysis.root_cause_summary = "; ".join(drift_items) if drift_items else "No drift detected."
        analysis.analysis_status = "PLAN_GENERATED"

        # Create Staged Remediation Plan
        plan = RemediationPlan(
            analysis_id=analysis.id,
            host_id=host.id,
            title=f"Autonomous Remediation for {host.hostname} ({framework.code})",
            status="STAGED",
            risk_level=risk_level,
            total_steps_count=len(remediation_actions),
            created_at=datetime.now(timezone.utc)
        )
        db.add(plan)
        db.flush()

        # Add steps
        for idx, act in enumerate(remediation_actions, 1):
            step = RemediationStep(
                plan_id=plan.id,
                step_number=idx,
                action_type=act["type"],
                target_package_or_errata=act["target"],
                parameters=act["params"],
                status="QUEUED",
                execution_log=act["desc"]
            )
            db.add(step)

        db.commit()
        db.refresh(analysis)

        log_audit_event(
            db=db,
            action="AGENT_ANALYSIS_COMPLETED",
            resource_type="HOST",
            resource_id=str(host.id),
            details=f"Autonomous agent analyzed host '{host.hostname}'. Staged remediation plan #{plan.id} with {len(remediation_actions)} steps.",
            user=user
        )

        return analysis

    def get_drift_summary(self, db: Session) -> Dict[str, Any]:
        """Fleet-wide drift calculation across all hosts."""
        hosts = db.query(Host).all()
        drift_items = []
        drifting_count = 0

        for host in hosts:
            level = "STABLE"
            rec = "Maintain periodic audit schedule."
            if host.compliance_status == "CRITICAL" or host.critical_errata_count > 0:
                level = "CRITICAL_DRIFT"
                drifting_count += 1
                rec = "Execute immediate autonomous remediation for critical errata."
            elif host.compliance_status == "NON_COMPLIANT" or host.compliance_score < 85.0:
                level = "MINOR_DRIFT"
                drifting_count += 1
                rec = "Review missing security packages and harden host baselines."

            drift_items.append({
                "host_id": host.id,
                "hostname": host.hostname,
                "compliance_score": host.compliance_score,
                "critical_errata_count": host.critical_errata_count,
                "drift_level": level,
                "recommended_action": rec
            })

        return {
            "total_hosts": len(hosts),
            "drifting_hosts_count": drifting_count,
            "drift_summary": drift_items
        }

agent_engine = AutonomousAgentEngine()
