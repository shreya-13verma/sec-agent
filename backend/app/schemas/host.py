from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class HostChannelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    channel_label: str
    channel_name: str

class HostPackageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    package_name: str
    package_version: str
    package_release: str
    package_arch: str

class ErrataSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    advisory_name: str
    advisory_type: str
    severity: str
    synopsis: str
    cve_identifier: Optional[str] = None
    issued_date: datetime

class HostMissingErrataResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    errata_id: int
    detected_at: datetime
    errata: ErrataSummary

class HostSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    mlm_system_id: int
    hostname: str
    ip_address: str
    os_family: str
    os_version: str
    kernel_release: str
    architecture: str
    last_checkin_time: Optional[datetime] = None
    compliance_status: str
    compliance_score: float
    critical_errata_count: int
    created_at: datetime

class HostDetail(HostSummary):
    model_config = ConfigDict(from_attributes=True)
    channels: List[HostChannelResponse] = []
    packages: List[HostPackageResponse] = []
    missing_errata: List[HostMissingErrataResponse] = []

class HostListResponse(BaseModel):
    total: int
    items: List[HostSummary]

class SyncRequest(BaseModel):
    force_full_sync: bool = False

class SyncResponse(BaseModel):
    status: str
    message: str
    synced_hosts_count: int
    synced_errata_count: int
