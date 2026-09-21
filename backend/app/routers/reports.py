from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from typing import Optional
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.schemas.report import ExecutiveComplianceReportResponse
from backend.app.services.report_service import report_service
from backend.app.services.auth_service import get_current_user

router = APIRouter(prefix="/reports", tags=["Reporting & Export"])

@router.get("/compliance", response_model=ExecutiveComplianceReportResponse)
def get_compliance_report(
    framework_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return report_service.generate_executive_data(db, framework_id)

@router.get("/export/csv")
def export_compliance_csv(
    framework_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    csv_content = report_service.generate_csv_report(db, framework_id)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=suse-mlm-compliance-report.csv"}
    )

@router.get("/export/pdf")
def export_compliance_pdf(
    framework_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pdf_content = report_service.generate_pdf_report(db, framework_id)
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=suse-mlm-compliance-report.pdf"}
    )
