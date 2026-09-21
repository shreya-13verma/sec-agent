from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from backend.app.database import get_db
from backend.app.models.remediation import RemediationPlan, RemediationStep
from backend.app.models.user import User
from backend.app.schemas.remediation import (
    RemediationPlanSummary, RemediationPlanDetail,
    PlanApproveRequest, PlanRejectRequest, PlanExecuteResponse
)
from backend.app.services.remediation_service import remediation_service
from backend.app.services.auth_service import get_current_user, require_roles

router = APIRouter(prefix="/remediations", tags=["Controlled Remediation Engine"])

@router.get("/plans", response_model=List[RemediationPlanSummary])
def list_remediation_plans(
    status_filter: Optional[str] = Query(None, alias="status"),
    host_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(RemediationPlan)
    if status_filter:
        query = query.filter(RemediationPlan.status == status_filter)
    if host_id:
        query = query.filter(RemediationPlan.host_id == host_id)
    return query.order_by(RemediationPlan.id.desc()).offset(offset).limit(limit).all()

@router.get("/plans/{plan_id}", response_model=RemediationPlanDetail)
def get_remediation_plan_detail(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plan = db.query(RemediationPlan).options(
        joinedload(RemediationPlan.steps)
    ).filter(RemediationPlan.id == plan_id).first()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Remediation plan {plan_id} not found"
        )
    return plan

@router.post("/plans/{plan_id}/approve", response_model=RemediationPlanSummary)
def approve_plan(
    plan_id: int,
    approve_req: PlanApproveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Security_Officer"]))
):
    try:
        plan = remediation_service.approve_plan(
            db=db,
            plan_id=plan_id,
            approval_notes=approve_req.approval_notes,
            user=current_user
        )
        return plan
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/plans/{plan_id}/reject", response_model=RemediationPlanSummary)
def reject_plan(
    plan_id: int,
    reject_req: PlanRejectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Security_Officer"]))
):
    try:
        plan = remediation_service.reject_plan(
            db=db,
            plan_id=plan_id,
            rejection_reason=reject_req.rejection_reason,
            user=current_user
        )
        return plan
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/plans/{plan_id}/execute", response_model=PlanExecuteResponse, status_code=status.HTTP_202_ACCEPTED)
def execute_approved_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Security_Officer", "Operator"]))
):
    try:
        result = remediation_service.execute_plan(
            db=db,
            plan_id=plan_id,
            user=current_user
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Execution failed: {str(e)}"
        )
