import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.models.compliance import ComplianceFramework, ComplianceRule
from backend.app.models.host import Host, HostChannel, HostPackage, HostMissingErrata
from backend.app.models.errata import ErrataAdvisory
from backend.app.utils.security import hash_password
from backend.app.services.suse_mlm_client import mlm_client

logger = logging.getLogger(__name__)

def seed_database(db: Session):
    # 1. Seed Users
    existing_admin = db.query(User).filter(User.username == "admin").first()
    if not existing_admin:
        users = [
            User(
                username="admin",
                email="admin@compliance.corp",
                hashed_password=hash_password("admin123"),
                full_name="Enterprise Administrator",
                role="Admin",
                is_active=True
            ),
            User(
                username="sec_officer",
                email="secofficer@compliance.corp",
                hashed_password=hash_password("sec123"),
                full_name="Chief Security Officer",
                role="Security_Officer",
                is_active=True
            ),
            User(
                username="operator",
                email="operator@compliance.corp",
                hashed_password=hash_password("op123"),
                full_name="Fleet Operations Engineer",
                role="Operator",
                is_active=True
            ),
            User(
                username="auditor",
                email="auditor@compliance.corp",
                hashed_password=hash_password("audit123"),
                full_name="External Compliance Auditor",
                role="Auditor",
                is_active=True
            ),
        ]
        db.add_all(users)
        db.commit()
        logger.info("Default users seeded.")

    # 2. Seed Compliance Frameworks & Rules
    if db.query(ComplianceFramework).count() == 0:
        cis = ComplianceFramework(
            name="CIS SLES 15 Benchmark",
            code="CIS_SLES_15",
            version="v1.2.0",
            description="Center for Internet Security benchmark for SUSE Linux Enterprise Server 15.",
            rule_count=5
        )
        hipaa = ComplianceFramework(
            name="HIPAA Security Rule",
            code="HIPAA",
            version="2024",
            description="Health Insurance Portability and Accountability Act Technical Safeguards.",
            rule_count=4
        )
        pci = ComplianceFramework(
            name="PCI-DSS v4.0",
            code="PCI_DSS_V4",
            version="v4.0.1",
            description="Payment Card Industry Data Security Standard Requirements.",
            rule_count=4
        )
        db.add_all([cis, hipaa, pci])
        db.commit()

        # Rules for CIS
        cis_rules = [
            ComplianceRule(
                framework_id=cis.id,
                rule_identifier="CIS-1.1.1",
                title="Ensure audit service package is installed",
                description="The audit daemon provides system event monitoring and auditing.",
                severity="HIGH",
                remediation_instructions="Install package 'audit' via SUSE MLM.",
                check_type="PACKAGE_REQUIRED",
                check_target="audit",
                expected_value="installed"
            ),
            ComplianceRule(
                framework_id=cis.id,
                rule_identifier="CIS-1.2.1",
                title="Ensure unencrypted telnet client is not installed",
                description="Telnet transfers credentials in plaintext and must be prohibited.",
                severity="CRITICAL",
                remediation_instructions="Remove package 'telnet' via SUSE MLM.",
                check_type="PACKAGE_PROHIBITED",
                check_target="telnet",
                expected_value="absent"
            ),
            ComplianceRule(
                framework_id=cis.id,
                rule_identifier="CIS-1.3.1",
                title="Ensure firewalld is installed and enabled",
                description="Firewalld manages host-level packet filtering.",
                severity="HIGH",
                remediation_instructions="Install package 'firewalld' via SUSE MLM.",
                check_type="PACKAGE_REQUIRED",
                check_target="firewalld",
                expected_value="installed"
            ),
            ComplianceRule(
                framework_id=cis.id,
                rule_identifier="CIS-1.4.1",
                title="Ensure legacy rsh-server is not installed",
                description="RSH server uses insecure cleartext communication.",
                severity="CRITICAL",
                remediation_instructions="Remove package 'rsh-server' via SUSE MLM.",
                check_type="PACKAGE_PROHIBITED",
                check_target="rsh-server",
                expected_value="absent"
            ),
            ComplianceRule(
                framework_id=cis.id,
                rule_identifier="CIS-2.1.1",
                title="Ensure critical OpenSSL vulnerability (CVE-2026-2144) is patched",
                description="Mitigates critical remote code execution flaw in TLS buffer validation.",
                severity="CRITICAL",
                remediation_instructions="Apply security errata SUSE-SU-2026:1042-1.",
                check_type="ERRATA_ABSENT",
                check_target="SUSE-SU-2026:1042-1",
                expected_value="applied"
            ),
        ]

        # Rules for HIPAA
        hipaa_rules = [
            ComplianceRule(
                framework_id=hipaa.id,
                rule_identifier="HIPAA-164.312.a",
                title="Transmission Security - OpenSSL Vulnerabilities Patched",
                description="Ensures all ePHI transmission channels use patched cryptographic libraries.",
                severity="CRITICAL",
                remediation_instructions="Apply advisory SUSE-SU-2026:1042-1.",
                check_type="ERRATA_ABSENT",
                check_target="SUSE-SU-2026:1042-1",
                expected_value="applied"
            ),
            ComplianceRule(
                framework_id=hipaa.id,
                rule_identifier="HIPAA-164.312.b",
                title="Audit Controls - Audit Package Required",
                description="Mechanisms to record and examine activity in systems containing ePHI.",
                severity="HIGH",
                remediation_instructions="Install package 'audit'.",
                check_type="PACKAGE_REQUIRED",
                check_target="audit",
                expected_value="installed"
            ),
            ComplianceRule(
                framework_id=hipaa.id,
                rule_identifier="HIPAA-164.312.c",
                title="Insecure Legacy Services Prohibited",
                description="Telnet must not be present on ePHI-processing infrastructure.",
                severity="CRITICAL",
                remediation_instructions="Remove package 'telnet'.",
                check_type="PACKAGE_PROHIBITED",
                check_target="telnet",
                expected_value="absent"
            ),
            ComplianceRule(
                framework_id=hipaa.id,
                rule_identifier="HIPAA-164.312.d",
                title="Host Firewall Installed",
                description="Host perimeter boundary protection active.",
                severity="MEDIUM",
                remediation_instructions="Install package 'firewalld'.",
                check_type="PACKAGE_REQUIRED",
                check_target="firewalld",
                expected_value="installed"
            ),
        ]

        # Rules for PCI-DSS
        pci_rules = [
            ComplianceRule(
                framework_id=pci.id,
                rule_identifier="PCI-6.3.3",
                title="Patch all known Critical Security Errata",
                description="Critical vulnerabilities must be patched within 30 days of release.",
                severity="CRITICAL",
                remediation_instructions="Apply all critical errata including SUSE-SU-2026:1042-1.",
                check_type="ERRATA_ABSENT",
                check_target="SUSE-SU-2026:1042-1",
                expected_value="applied"
            ),
            ComplianceRule(
                framework_id=pci.id,
                rule_identifier="PCI-8.2.1",
                title="Ensure unencrypted remote access (rsh/telnet) is disabled",
                description="Telnet and rsh protocols must be purged from cardholder data environments.",
                severity="CRITICAL",
                remediation_instructions="Remove packages 'telnet' and 'rsh-server'.",
                check_type="PACKAGE_PROHIBITED",
                check_target="telnet",
                expected_value="absent"
            ),
            ComplianceRule(
                framework_id=pci.id,
                rule_identifier="PCI-10.2.1",
                title="Audit Trail Logging Active",
                description="Audit logging must capture all administrative and security actions.",
                severity="HIGH",
                remediation_instructions="Install package 'audit'.",
                check_type="PACKAGE_REQUIRED",
                check_target="audit",
                expected_value="installed"
            ),
            ComplianceRule(
                framework_id=pci.id,
                rule_identifier="PCI-1.2.1",
                title="Host-Based Firewall Protection",
                description="Restrict inbound and outbound traffic to necessary protocols.",
                severity="HIGH",
                remediation_instructions="Install and enable package 'firewalld'.",
                check_type="PACKAGE_REQUIRED",
                check_target="firewalld",
                expected_value="installed"
            ),
        ]

        db.add_all(cis_rules + hipaa_rules + pci_rules)
        db.commit()
        logger.info("Compliance frameworks and rules seeded.")

    # 3. Synchronize Initial Hosts from SUSE MLM
    if db.query(Host).count() == 0:
        sync_hosts_from_mlm(db)

def sync_hosts_from_mlm(db: Session):
    """Synchronize hosts, packages, and errata from SUSE MLM into normalized tables."""
    systems = mlm_client.list_systems()
    for sys_info in systems:
        host = db.query(Host).filter(Host.mlm_system_id == sys_info["id"]).first()
        if not host:
            host = Host(
                mlm_system_id=sys_info["id"],
                hostname=sys_info["name"],
                ip_address=sys_info["ip_address"],
                os_family=sys_info["os_family"],
                os_version=sys_info["os_version"],
                kernel_release=sys_info["kernel_release"],
                architecture=sys_info["architecture"],
                last_checkin_time=datetime.now(timezone.utc),
                compliance_status="UNKNOWN",
                compliance_score=0.0,
                critical_errata_count=0
            )
            db.add(host)
            db.flush()

        # Update channels
        db.query(HostChannel).filter(HostChannel.host_id == host.id).delete()
        for ch in sys_info.get("channels", []):
            host_ch = HostChannel(
                host_id=host.id,
                channel_label=ch["label"],
                channel_name=ch["name"]
            )
            db.add(host_ch)

        # Update packages
        db.query(HostPackage).filter(HostPackage.host_id == host.id).delete()
        for pkg in sys_info.get("packages", []):
            host_pkg = HostPackage(
                host_id=host.id,
                package_name=pkg["name"],
                package_version=pkg["version"],
                package_release=pkg["release"],
                package_arch=pkg["arch"]
            )
            db.add(host_pkg)

        # Update missing errata
        db.query(HostMissingErrata).filter(HostMissingErrata.host_id == host.id).delete()
        crit_count = 0
        for err in sys_info.get("missing_errata", []):
            if err.get("severity") == "Critical":
                crit_count += 1
            # Check or create advisory
            advisory = db.query(ErrataAdvisory).filter(ErrataAdvisory.advisory_name == err["advisory_name"]).first()
            if not advisory:
                issued = datetime.now(timezone.utc)
                if "issued_date" in err:
                    try:
                        issued = datetime.fromisoformat(err["issued_date"].replace("Z", "+00:00"))
                    except Exception:
                        pass
                advisory = ErrataAdvisory(
                    advisory_name=err["advisory_name"],
                    advisory_type=err.get("advisory_type", "Security Advisory"),
                    severity=err.get("severity", "Important"),
                    synopsis=err.get("synopsis", ""),
                    cve_identifier=err.get("cve_identifier"),
                    issued_date=issued
                )
                db.add(advisory)
                db.flush()

            missing = HostMissingErrata(
                host_id=host.id,
                errata_id=advisory.id,
                detected_at=datetime.now(timezone.utc)
            )
            db.add(missing)

        host.critical_errata_count = crit_count
        db.commit()
    logger.info("Host synchronization completed.")
