"""System and Inventory Schemas."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ServerSummary(BaseModel):
    id: int
    hostname: str
    ip_address: str
    os_release: str
    kernel_version: str
    last_checkin: Optional[datetime] = None
    compliance_score: float
    security_errata_count: int
    bugfix_errata_count: int
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PackageInfo(BaseModel):
    name: str
    version: str
    release: str
    arch: str
