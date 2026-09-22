"""Approval and Remediation Schemas."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ApprovalActionRequest(BaseModel):
    approved: bool
    operator: str = "SecOps Lead"
    comment: Optional[str] = None

class ApprovalResponse(BaseModel):
    id: str
    approval_token: str
    session_id: str
    server_id: int
    action_type: str
    proposed_errata_ids: str
    status: str
    operator: Optional[str] = None
    operator_comment: Optional[str] = None
    mlm_action_id: Optional[int] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True
