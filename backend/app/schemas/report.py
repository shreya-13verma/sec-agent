from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class ComplianceSummaryReportItem(BaseModel):
    framework_name: str
    framework_code: str
    total_scans: int
    latest_score: float
    hosts_compliant_count: int
    hosts_non_compliant_count: int

class HostComplianceReportItem(BaseModel):
    hostname: str
    ip_address: str
    os_info: str
    compliance_status: str
    compliance_score: float
    critical_errata_count: int
    missing_cves: List[str] = []

class ExecutiveComplianceReportResponse(BaseModel):
    generated_at: datetime
    fleet_total_hosts: int
    fleet_average_score: float
    fleet_critical_hosts_count: int
    framework_summaries: List[ComplianceSummaryReportItem] = []
    host_details: List[HostComplianceReportItem] = []

class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: Optional[int] = None
    user_username: str
    action: str
    resource_type: str
    resource_id: str
    details: str
    ip_address: str
    timestamp: datetime

class AuditLogListResponse(BaseModel):
    total: int
    items: List[AuditLogResponse]
