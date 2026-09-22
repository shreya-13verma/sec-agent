"""Chat Session and Message models (Normalized, strictly 0 JSON columns)."""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from backend.app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False, default="Security & Compliance Session")
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    approvals = relationship("RemediationApproval", back_populates="session")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    sender = Column(String(50), nullable=False)  # user | agent | system
    content = Column(Text, nullable=False)
    thought_log = Column(Text, nullable=True, default="")
    created_at = Column(DateTime(timezone=True), default=utc_now)

    session = relationship("ChatSession", back_populates="messages")
