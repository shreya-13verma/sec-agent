from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class RemediationStepResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    plan_id: int
    step_number: int
    action_type: str
    target_package_or_errata: str
    parameters: str
    status: str
    mlm_action_id: Optional[int] = None
    execution_log: Optional[str] = None

class RemediationPlanSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    analysis_id: Optional[int] = None
    host_id: int
    title: str
    status: str
    risk_level: str
    total_steps_count: int
    approved_by_user_id: Optional[int] = None
    approval_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    executed_at: Optional[datetime] = None

class RemediationPlanDetail(RemediationPlanSummary):
    model_config = ConfigDict(from_attributes=True)
    steps: List[RemediationStepResponse] = []

class PlanApproveRequest(BaseModel):
    approval_notes: Optional[str] = "Approved for execution"

class PlanRejectRequest(BaseModel):
    rejection_reason: str

class PlanExecuteResponse(BaseModel):
    plan_id: int
    status: str
    message: str
    dispatched_steps_count: int
