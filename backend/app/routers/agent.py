from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from backend.app.database import get_db
from backend.app.models.agent import AgentAnalysis, AgentThoughtStep
from backend.app.models.remediation import RemediationPlan
from backend.app.models.user import User
from backend.app.schemas.agent import (
    AgentAnalysisCreate, AgentAnalysisResponse, ThoughtStepResponse,
    DriftSummaryResponse
)
from backend.app.services.agent_engine import agent_engine
from backend.app.services.auth_service import get_current_user, require_roles

router = APIRouter(prefix="/agent", tags=["Autonomous Agent Engine"])

@router.post("/analyze", response_model=AgentAnalysisResponse)
def analyze_host(
    req: AgentAnalysisCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Security_Officer", "Operator"]))
):
    try:
        analysis = agent_engine.analyze_host(
            db=db,
            host_id=req.host_id,
            framework_id=req.framework_id,
            user=current_user
        )
        # Find staged plan id
        plan = db.query(RemediationPlan).filter(RemediationPlan.analysis_id == analysis.id).first()
        proposed_plan_id = plan.id if plan else None

        response_obj = AgentAnalysisResponse(
            id=analysis.id,
            host_id=analysis.host_id,
            framework_id=analysis.framework_id,
            analysis_status=analysis.analysis_status,
            drift_detected=analysis.drift_detected,
            root_cause_summary=analysis.root_cause_summary,
            created_at=analysis.created_at,
            thought_steps=[
                ThoughtStepResponse(
                    id=t.id,
                    step_order=t.step_order,
                    thought_type=t.thought_type,
                    thought_content=t.thought_content,
                    created_at=t.created_at
                ) for t in analysis.thought_steps
            ],
            proposed_plan_id=proposed_plan_id
        )
        return response_obj
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent analysis failed: {str(e)}"
        )

@router.get("/analyses/{analysis_id}", response_model=AgentAnalysisResponse)
def get_analysis_detail(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    analysis = db.query(AgentAnalysis).options(
        joinedload(AgentAnalysis.thought_steps)
    ).filter(AgentAnalysis.id == analysis_id).first()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent analysis {analysis_id} not found"
        )
    plan = db.query(RemediationPlan).filter(RemediationPlan.analysis_id == analysis.id).first()
    proposed_plan_id = plan.id if plan else None

    return AgentAnalysisResponse(
        id=analysis.id,
        host_id=analysis.host_id,
        framework_id=analysis.framework_id,
        analysis_status=analysis.analysis_status,
        drift_detected=analysis.drift_detected,
        root_cause_summary=analysis.root_cause_summary,
        created_at=analysis.created_at,
        thought_steps=[
            ThoughtStepResponse(
                id=t.id,
                step_order=t.step_order,
                thought_type=t.thought_type,
                thought_content=t.thought_content,
                created_at=t.created_at
            ) for t in analysis.thought_steps
        ],
        proposed_plan_id=proposed_plan_id
    )

@router.get("/drift-detection", response_model=DriftSummaryResponse)
def get_fleet_drift(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return agent_engine.get_drift_summary(db)
