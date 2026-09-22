"""OpenSCAP and Errata compliance models (Normalized, strictly 0 JSON columns)."""
from sqlalchemy import Column, String, Float, Integer, Text, DateTime, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from backend.app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class OpenSCAPScan(Base):
    __tablename__ = "openscap_scans"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    mlm_test_result_id = Column(BigInteger, unique=True, nullable=False, index=True)
    server_id = Column(BigInteger, ForeignKey("managed_servers.id", ondelete="CASCADE"), nullable=False)
    profile_name = Column(String(255), nullable=False)
    scan_timestamp = Column(DateTime(timezone=True), default=utc_now)
    pass_count = Column(Integer, nullable=False, default=0)
    fail_count = Column(Integer, nullable=False, default=0)
    error_count = Column(Integer, nullable=False, default=0)
    other_count = Column(Integer, nullable=False, default=0)
    score = Column(Float, nullable=False, default=0.0)

    server = relationship("ManagedServer", back_populates="scans")
    rule_results = relationship("OpenSCAPRuleResult", back_populates="scan", cascade="all, delete-orphan")


class OpenSCAPRuleResult(Base):
    __tablename__ = "openscap_rule_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    scan_id = Column(String(36), ForeignKey("openscap_scans.id", ondelete="CASCADE"), nullable=False)
    rule_identifier = Column(String(255), nullable=False, index=True)
    rule_title = Column(String(500), nullable=False)
    result = Column(String(50), nullable=False)  # pass | fail | error | notapplicable
    severity = Column(String(50), nullable=False)  # low | medium | high | critical

    scan = relationship("OpenSCAPScan", back_populates="rule_results")


class SystemErrataAdvisory(Base):
    __tablename__ = "system_errata_advisories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    server_id = Column(BigInteger, ForeignKey("managed_servers.id", ondelete="CASCADE"), nullable=False)
    advisory_name = Column(String(100), nullable=False, index=True)
    advisory_type = Column(String(50), nullable=False)  # Security Advisory | Bug Fix Advisory | Enhancement
    cve_id = Column(String(100), nullable=False, index=True, default="N/A")
    synopsis = Column(Text, nullable=False)
    issue_date = Column(DateTime(timezone=True), default=utc_now)
    remediation_status = Column(String(50), nullable=False, default="pending")  # pending | scheduled | applied | ignored

    server = relationship("ManagedServer", back_populates="errata_items")
