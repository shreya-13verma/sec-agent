from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class AgentAnalysis(Base):
    __tablename__ = "agent_analyses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    host_id = Column(Integer, ForeignKey("hosts.id", ondelete="CASCADE"), nullable=False, index=True)
    framework_id = Column(Integer, ForeignKey("compliance_frameworks.id", ondelete="CASCADE"), nullable=False, index=True)
    analysis_status = Column(String(32), nullable=False, default="ANALYZING", index=True) # ANALYZING, PLAN_GENERATED, COMPLETED, FAILED
    drift_detected = Column(Boolean, nullable=False, default=False)
    root_cause_summary = Column(String(1024), nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    host = relationship("Host", back_populates="agent_analyses")
    framework = relationship("ComplianceFramework", back_populates="agent_analyses")
    thought_steps = relationship("AgentThoughtStep", back_populates="analysis", cascade="all, delete-orphan")
    remediation_plans = relationship("RemediationPlan", back_populates="analysis")

class AgentThoughtStep(Base):
    __tablename__ = "agent_thought_steps"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    analysis_id = Column(Integer, ForeignKey("agent_analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    step_order = Column(Integer, nullable=False)
    thought_type = Column(String(64), nullable=False) # OBSERVATION, CORRELATION, RISK_EVALUATION, DECISION
    thought_content = Column(String(1024), nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    analysis = relationship("AgentAnalysis", back_populates="thought_steps")
