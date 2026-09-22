"""Compliance and OpenSCAP Schemas."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class RuleResultSchema(BaseModel):
    rule_identifier: str
    rule_title: str
    result: str
    severity: str

class OpenSCAPScanResponse(BaseModel):
    id: str
    mlm_test_result_id: int
    server_id: int
    profile_name: str
    scan_timestamp: datetime
    pass_count: int
    fail_count: int
    error_count: int
    other_count: int
    score: float
    rules: Optional[List[RuleResultSchema]] = None

    class Config:
        from_attributes = True

class ErrataAdvisorySchema(BaseModel):
    id: str
    server_id: int
    advisory_name: str
    advisory_type: str
    cve_id: str
    synopsis: str
    issue_date: datetime
    remediation_status: str

    class Config:
        from_attributes = True
