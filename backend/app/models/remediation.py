from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class RemediationPlan(Base):
    __tablename__ = "remediation_plans"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    analysis_id = Column(Integer, ForeignKey("agent_analyses.id", ondelete="SET NULL"), nullable=True, index=True)
    host_id = Column(Integer, ForeignKey("hosts.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    status = Column(String(32), nullable=False, default="STAGED", index=True) # DRAFT, STAGED, APPROVED, REJECTED, IN_PROGRESS, COMPLETED, FAILED
    risk_level = Column(String(32), nullable=False, default="MEDIUM") # LOW, MEDIUM, HIGH, CRITICAL
    total_steps_count = Column(Integer, nullable=False, default=0)
    approved_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approval_notes = Column(String(512), nullable=True)
    rejection_reason = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    executed_at = Column(DateTime, nullable=True)

    host = relationship("Host", back_populates="remediation_plans")
    analysis = relationship("AgentAnalysis", back_populates="remediation_plans")
    approved_by_user = relationship("User", back_populates="plans_approved")
    steps = relationship("RemediationStep", back_populates="plan", cascade="all, delete-orphan")

class RemediationStep(Base):
    __tablename__ = "remediation_steps"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    plan_id = Column(Integer, ForeignKey("remediation_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    step_number = Column(Integer, nullable=False)
    action_type = Column(String(64), nullable=False) # APPLY_ERRATA, INSTALL_PACKAGE, REMOVE_PACKAGE, SET_CONFIG_PARAMETER, RESTART_SERVICE
    target_package_or_errata = Column(String(255), nullable=False)
    parameters = Column(String(512), nullable=False, default="")
    status = Column(String(32), nullable=False, default="QUEUED", index=True) # QUEUED, DISPATCHED, RUNNING, SUCCESS, FAILED, SKIPPED
    mlm_action_id = Column(Integer, nullable=True)
    execution_log = Column(String(1024), nullable=True)

    plan = relationship("RemediationPlan", back_populates="steps")
