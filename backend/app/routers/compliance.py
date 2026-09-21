from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from backend.app.database import get_db
from backend.app.models.compliance import ComplianceFramework, ComplianceRule, ComplianceScan, ComplianceFinding
from backend.app.models.user import User
from backend.app.schemas.compliance import (
    ComplianceFrameworkSummary, ComplianceFrameworkDetail,
    ComplianceScanCreate, ComplianceScanResponse, ComplianceScanDetail,
    ComplianceFindingResponse
)
from backend.app.services.compliance_engine import compliance_engine
from backend.app.services.auth_service import get_current_user, require_roles

router = APIRouter(prefix="/compliance", tags=["Compliance & Hardening Audits"])

@router.get("/frameworks", response_model=List[ComplianceFrameworkSummary])
def list_frameworks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    frameworks = db.query(ComplianceFramework).all()
    return frameworks

@router.get("/frameworks/{framework_id}", response_model=ComplianceFrameworkDetail)
def get_framework_detail(
    framework_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    framework = db.query(ComplianceFramework).options(
        joinedload(ComplianceFramework.rules)
    ).filter(ComplianceFramework.id == framework_id).first()
    if not framework:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Framework {framework_id} not found"
        )
    return framework

@router.post("/scans", response_model=ComplianceScanResponse, status_code=status.HTTP_202_ACCEPTED)
def trigger_compliance_scan(
    scan_create: ComplianceScanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Security_Officer", "Operator"]))
):
    try:
        scan = compliance_engine.run_scan(
            db=db,
            framework_id=scan_create.framework_id,
            host_ids=scan_create.host_ids,
            user=current_user
        )
        return scan
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute compliance scan: {str(e)}"
        )

@router.get("/scans", response_model=List[ComplianceScanResponse])
def list_scans(
    framework_id: Optional[int] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(ComplianceScan).options(
        joinedload(ComplianceScan.framework)
    )
    if framework_id:
        query = query.filter(ComplianceScan.framework_id == framework_id)
    return query.order_by(ComplianceScan.id.desc()).offset(offset).limit(limit).all()

@router.get("/scans/{scan_id}", response_model=ComplianceScanDetail)
def get_scan_detail(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    scan = db.query(ComplianceScan).options(
        joinedload(ComplianceScan.framework),
        joinedload(ComplianceScan.findings).joinedload(ComplianceFinding.rule)
    ).filter(ComplianceScan.id == scan_id).first()

    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Compliance scan {scan_id} not found"
        )
    return scan

@router.get("/findings", response_model=List[ComplianceFindingResponse])
def list_findings(
    scan_id: Optional[int] = Query(None),
    host_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(ComplianceFinding).options(
        joinedload(ComplianceFinding.rule)
    )
    if scan_id:
        query = query.filter(ComplianceFinding.scan_id == scan_id)
    if host_id:
        query = query.filter(ComplianceFinding.host_id == host_id)
    if status_filter:
        query = query.filter(ComplianceFinding.status == status_filter)

    return query.order_by(ComplianceFinding.id.desc()).offset(offset).limit(limit).all()
