from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class ComplianceRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    framework_id: int
    rule_identifier: str
    title: str
    description: str
    severity: str
    remediation_instructions: str
    check_type: str
    check_target: str
    expected_value: str

class ComplianceFrameworkSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    code: str
    version: str
    description: str
    rule_count: int

class ComplianceFrameworkDetail(ComplianceFrameworkSummary):
    model_config = ConfigDict(from_attributes=True)
    rules: List[ComplianceRuleResponse] = []

class ComplianceFindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    scan_id: int
    host_id: int
    rule_id: int
    status: str # PASS, FAIL, ERROR, SKIPPED
    observed_value: str
    finding_details: str
    detected_at: datetime
    rule: Optional[ComplianceRuleResponse] = None

class ComplianceScanCreate(BaseModel):
    framework_id: int
    host_ids: Optional[List[int]] = None # None means all registered hosts

class ComplianceScanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    framework_id: int
    initiated_by_user_id: Optional[int] = None
    scan_status: str
    hosts_scanned_count: int
    passed_rules_count: int
    failed_rules_count: int
    overall_score: float
    started_at: datetime
    completed_at: Optional[datetime] = None
    framework: Optional[ComplianceFrameworkSummary] = None

class ComplianceScanDetail(ComplianceScanResponse):
    model_config = ConfigDict(from_attributes=True)
    findings: List[ComplianceFindingResponse] = []
