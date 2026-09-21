from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from backend.app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class ErrataAdvisory(Base):
    __tablename__ = "errata_advisories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    advisory_name = Column(String(128), unique=True, index=True, nullable=False) # e.g. SUSE-SU-2026:1042-1
    advisory_type = Column(String(32), nullable=False) # Security Advisory, Bug Fix, Enhancement
    severity = Column(String(32), nullable=False, index=True) # Critical, Important, Moderate, Low
    synopsis = Column(String(512), nullable=False)
    cve_identifier = Column(String(128), nullable=True, index=True) # e.g. CVE-2026-2144
    issued_date = Column(DateTime, default=utc_now, nullable=False)

    missing_on_hosts = relationship("HostMissingErrata", back_populates="errata", cascade="all, delete-orphan")
