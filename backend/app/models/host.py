from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class Host(Base):
    __tablename__ = "hosts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    mlm_system_id = Column(Integer, unique=True, index=True, nullable=False)
    hostname = Column(String(255), index=True, nullable=False)
    ip_address = Column(String(64), nullable=False)
    os_family = Column(String(64), nullable=False) # SLES, RHEL, openSUSE
    os_version = Column(String(64), nullable=False)
    kernel_release = Column(String(128), nullable=False)
    architecture = Column(String(32), nullable=False)
    last_checkin_time = Column(DateTime, nullable=True)
    compliance_status = Column(String(32), nullable=False, default="UNKNOWN", index=True) # COMPLIANT, NON_COMPLIANT, CRITICAL, UNKNOWN
    compliance_score = Column(Float, nullable=False, default=0.0)
    critical_errata_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    channels = relationship("HostChannel", back_populates="host", cascade="all, delete-orphan")
    packages = relationship("HostPackage", back_populates="host", cascade="all, delete-orphan")
    missing_errata = relationship("HostMissingErrata", back_populates="host", cascade="all, delete-orphan")
    findings = relationship("ComplianceFinding", back_populates="host", cascade="all, delete-orphan")
    agent_analyses = relationship("AgentAnalysis", back_populates="host", cascade="all, delete-orphan")
    remediation_plans = relationship("RemediationPlan", back_populates="host", cascade="all, delete-orphan")

class HostChannel(Base):
    __tablename__ = "host_channels"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    host_id = Column(Integer, ForeignKey("hosts.id", ondelete="CASCADE"), nullable=False, index=True)
    channel_label = Column(String(128), nullable=False)
    channel_name = Column(String(255), nullable=False)

    host = relationship("Host", back_populates="channels")

class HostPackage(Base):
    __tablename__ = "host_packages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    host_id = Column(Integer, ForeignKey("hosts.id", ondelete="CASCADE"), nullable=False, index=True)
    package_name = Column(String(128), nullable=False, index=True)
    package_version = Column(String(64), nullable=False)
    package_release = Column(String(64), nullable=False)
    package_arch = Column(String(32), nullable=False)

    host = relationship("Host", back_populates="packages")

class HostMissingErrata(Base):
    __tablename__ = "host_missing_errata"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    host_id = Column(Integer, ForeignKey("hosts.id", ondelete="CASCADE"), nullable=False, index=True)
    errata_id = Column(Integer, ForeignKey("errata_advisories.id", ondelete="CASCADE"), nullable=False, index=True)
    detected_at = Column(DateTime, default=utc_now, nullable=False)

    host = relationship("Host", back_populates="missing_errata")
    errata = relationship("ErrataAdvisory", back_populates="missing_on_hosts")
