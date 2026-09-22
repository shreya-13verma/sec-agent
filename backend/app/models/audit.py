"""Audit Log model (Normalized, strictly 0 JSON columns)."""
from sqlalchemy import Column, String, Text, DateTime
from datetime import datetime, timezone
import uuid
from backend.app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    event_type = Column(String(100), nullable=False, index=True)  # SCAN_SCHEDULED | REMEDIATION_APPROVED | REMEDIATION_REJECTED | REPORT_GENERATED
    operator = Column(String(100), nullable=False, default="System")
    resource_type = Column(String(100), nullable=False)  # Server | Scan | Report | Errata
    resource_id = Column(String(100), nullable=False)
    action_details = Column(Text, nullable=False)
    ip_address = Column(String(45), nullable=False, default="127.0.0.1")
    timestamp = Column(DateTime(timezone=True), default=utc_now)
