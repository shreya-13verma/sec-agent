"""Report Schemas."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ReportGenerateRequest(BaseModel):
    title: Optional[str] = "Fleet Compliance & Vulnerability Audit Report"
    scope: str = "all"  # all | system
    target_id: str = "all"
    formats: List[str] = ["json", "csv", "pdf"]

class ReportResponse(BaseModel):
    id: str
    title: str
    report_scope: str
    target_id: str
    pdf_path: str
    csv_path: str
    json_path: str
    generated_by: str
    created_at: datetime

    class Config:
        from_attributes = True
