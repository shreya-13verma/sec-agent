from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from backend.app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(128), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(128), nullable=False)
    role = Column(String(32), nullable=False, default="Operator") # Admin, Security_Officer, Operator, Auditor
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    scans_initiated = relationship("ComplianceScan", back_populates="initiated_by", cascade="all, delete-orphan")
    plans_approved = relationship("RemediationPlan", back_populates="approved_by_user", cascade="all, delete-orphan")
    audit_events = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
