"""Compliance Report models (Normalized, strictly 0 JSON columns)."""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from backend.app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class ComplianceReport(Base):
    __tablename__ = "compliance_reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    report_scope = Column(String(50), nullable=False)  # all | system | group
    target_id = Column(String(100), nullable=False, default="all")
    pdf_path = Column(String(500), nullable=False, default="")
    csv_path = Column(String(500), nullable=False, default="")
    json_path = Column(String(500), nullable=False, default="")
    generated_by = Column(String(100), nullable=False, default="Security Operator")
    created_at = Column(DateTime(timezone=True), default=utc_now)


class RemediationApproval(Base):
    __tablename__ = "remediation_approvals"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    approval_token = Column(String(128), unique=True, nullable=False, index=True)
    session_id = Column(String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    server_id = Column(BigInteger, ForeignKey("managed_servers.id", ondelete="CASCADE"), nullable=False)
    action_type = Column(String(100), nullable=False, default="Apply Errata Remediation")
    proposed_errata_ids = Column(Text, nullable=False)  # Comma-delimited list of IDs
    status = Column(String(50), nullable=False, default="pending")  # pending | approved | rejected | expired
    operator = Column(String(100), nullable=True)
    operator_comment = Column(Text, nullable=True)
    mlm_action_id = Column(BigInteger, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    session = relationship("ChatSession", back_populates="approvals")
    server = relationship("ManagedServer", back_populates="approvals")
