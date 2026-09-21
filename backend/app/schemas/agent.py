from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class ThoughtStepResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    step_order: int
    thought_type: str
    thought_content: str
    created_at: datetime

class AgentAnalysisCreate(BaseModel):
    host_id: int
    framework_id: Optional[int] = None

class AgentAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    host_id: int
    framework_id: int
    analysis_status: str
    drift_detected: bool
    root_cause_summary: str
    created_at: datetime
    thought_steps: List[ThoughtStepResponse] = []
    proposed_plan_id: Optional[int] = None

class HostDriftItem(BaseModel):
    host_id: int
    hostname: str
    compliance_score: float
    critical_errata_count: int
    drift_level: str # STABLE, MINOR_DRIFT, CRITICAL_DRIFT
    recommended_action: str

class DriftSummaryResponse(BaseModel):
    total_hosts: int
    drifting_hosts_count: int
    drift_summary: List[HostDriftItem]
