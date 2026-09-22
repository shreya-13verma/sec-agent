"""Reports API endpoints."""
import os
import uuid
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.app.core.database import get_db
from backend.app.models.report import ComplianceReport
from backend.app.models.audit import AuditLog
from backend.app.schemas.report import ReportGenerateRequest, ReportResponse
from backend.app.services.report_service import report_service

router = APIRouter()

@router.get("", response_model=list[ReportResponse])
async def list_reports(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ComplianceReport).order_by(desc(ComplianceReport.created_at)))
    return result.scalars().all()

@router.post("/generate", response_model=ReportResponse)
async def generate_report(request: ReportGenerateRequest, db: AsyncSession = Depends(get_db)):
    try:
        report_data = report_service.generate_compliance_data(request.scope, request.target_id)
        prefix = f"report_{uuid.uuid4().hex[:8]}"

        json_p = report_service.export_json(report_data, prefix) if "json" in request.formats else ""
        csv_p = report_service.export_csv(report_data, prefix) if "csv" in request.formats else ""
        pdf_p = report_service.export_pdf(report_data, prefix) if "pdf" in request.formats else ""

        report_id = str(uuid.uuid4())
        report_record = ComplianceReport(
            id=report_id,
            title=request.title or "Fleet Compliance Report",
            report_scope=request.scope,
            target_id=request.target_id,
            pdf_path=pdf_p,
            csv_path=csv_p,
            json_path=json_p,
            generated_by="SecOps Lead"
        )
        db.add(report_record)

        audit = AuditLog(
            event_type="REPORT_GENERATED",
            operator="SecOps Lead",
            resource_type="Report",
            resource_id=report_id,
            action_details=f"Generated {request.scope} compliance report across formats: {', '.join(request.formats)}"
        )
        db.add(audit)
        await db.commit()
        await db.refresh(report_record)
        return report_record
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{report_id}/download/{format_type}")
async def download_report_file(report_id: str, format_type: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ComplianceReport).where(ComplianceReport.id == report_id))
    report = result.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    fmt = format_type.lower()
    path_map = {
        "pdf": (report.pdf_path, "application/pdf"),
        "csv": (report.csv_path, "text/csv"),
        "json": (report.json_path, "application/json")
    }

    if fmt not in path_map or not path_map[fmt][0] or not os.path.exists(path_map[fmt][0]):
        raise HTTPException(status_code=404, detail=f"File for format '{format_type}' is not available")

    filepath, media_type = path_map[fmt]
    filename = os.path.basename(filepath)
    return FileResponse(filepath, media_type=media_type, filename=filename)
