"""Managed Server models (Normalized, strictly 0 JSON columns)."""
from sqlalchemy import Column, String, Float, Integer, DateTime, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.app.core.database import Base

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class ManagedServer(Base):
    __tablename__ = "managed_servers"

    id = Column(BigInteger, primary_key=True, autoincrement=False)  # SUSE MLM Server ID
    hostname = Column(String(255), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False)
    os_release = Column(String(100), nullable=False)
    kernel_version = Column(String(100), nullable=False)
    last_checkin = Column(DateTime(timezone=True), default=utc_now)
    compliance_score = Column(Float, nullable=False, default=0.0)
    security_errata_count = Column(Integer, nullable=False, default=0)
    bugfix_errata_count = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    scans = relationship("OpenSCAPScan", back_populates="server", cascade="all, delete-orphan")
    errata_items = relationship("SystemErrataAdvisory", back_populates="server", cascade="all, delete-orphan")
    approvals = relationship("RemediationApproval", back_populates="server")
