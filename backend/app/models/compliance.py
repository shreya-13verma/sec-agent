from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class ComplianceFramework(Base):
    __tablename__ = "compliance_frameworks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(64), unique=True, index=True, nullable=False) # CIS SLES 15 Benchmark, HIPAA Security Rule, PCI-DSS v4.0
    code = Column(String(32), unique=True, index=True, nullable=False) # CIS_SLES_15, HIPAA, PCI_DSS_V4
    version = Column(String(32), nullable=False)
    description = Column(String(512), nullable=False)
    rule_count = Column(Integer, nullable=False, default=0)

    rules = relationship("ComplianceRule", back_populates="framework", cascade="all, delete-orphan")
    scans = relationship("ComplianceScan", back_populates="framework", cascade="all, delete-orphan")
    agent_analyses = relationship("AgentAnalysis", back_populates="framework", cascade="all, delete-orphan")

class ComplianceRule(Base):
    __tablename__ = "compliance_rules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    framework_id = Column(Integer, ForeignKey("compliance_frameworks.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_identifier = Column(String(64), nullable=False, index=True) # CIS-1.1.1.1, PCI-8.2.3
    title = Column(String(255), nullable=False)
    description = Column(String(1024), nullable=False)
    severity = Column(String(32), nullable=False, index=True) # CRITICAL, HIGH, MEDIUM, LOW
    remediation_instructions = Column(String(1024), nullable=False)
    check_type = Column(String(64), nullable=False) # PACKAGE_REQUIRED, PACKAGE_PROHIBITED, CONFIG_PROPERTY, ERRATA_ABSENT, SERVICE_STATE
    check_target = Column(String(255), nullable=False)
    expected_value = Column(String(255), nullable=False)

    framework = relationship("ComplianceFramework", back_populates="rules")
    findings = relationship("ComplianceFinding", back_populates="rule", cascade="all, delete-orphan")

class ComplianceScan(Base):
    __tablename__ = "compliance_scans"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    framework_id = Column(Integer, ForeignKey("compliance_frameworks.id", ondelete="CASCADE"), nullable=False, index=True)
    initiated_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    scan_status = Column(String(32), nullable=False, default="PENDING", index=True) # PENDING, RUNNING, COMPLETED, FAILED
    hosts_scanned_count = Column(Integer, nullable=False, default=0)
    passed_rules_count = Column(Integer, nullable=False, default=0)
    failed_rules_count = Column(Integer, nullable=False, default=0)
    overall_score = Column(Float, nullable=False, default=0.0)
    started_at = Column(DateTime, default=utc_now, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    framework = relationship("ComplianceFramework", back_populates="scans")
    initiated_by = relationship("User", back_populates="scans_initiated")
    findings = relationship("ComplianceFinding", back_populates="scan", cascade="all, delete-orphan")

class ComplianceFinding(Base):
    __tablename__ = "compliance_findings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    scan_id = Column(Integer, ForeignKey("compliance_scans.id", ondelete="CASCADE"), nullable=False, index=True)
    host_id = Column(Integer, ForeignKey("hosts.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_id = Column(Integer, ForeignKey("compliance_rules.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(32), nullable=False, index=True) # PASS, FAIL, ERROR, SKIPPED
    observed_value = Column(String(255), nullable=False)
    finding_details = Column(String(1024), nullable=False)
    detected_at = Column(DateTime, default=utc_now, nullable=False)

    scan = relationship("ComplianceScan", back_populates="findings")
    host = relationship("Host", back_populates="findings")
    rule = relationship("ComplianceRule", back_populates="findings")
