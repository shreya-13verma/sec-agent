"""Human-in-the-Loop Remediation Approval Endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime, timezone
import json
import uuid

from backend.app.core.database import get_db
from backend.app.models.report import RemediationApproval
from backend.app.models.audit import AuditLog
from backend.app.schemas.approval import ApprovalActionRequest, ApprovalResponse
from backend.app.agent.mcp_client import mcp_bridge
from backend.app.core.config import settings

router = APIRouter()

@router.get("/pending", response_model=list[ApprovalResponse])
async def list_pending_approvals(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(RemediationApproval).where(RemediationApproval.status == "pending").order_by(desc(RemediationApproval.created_at))
    )
    return result.scalars().all()

@router.post("/{token}/action", response_model=ApprovalResponse)
async def process_approval_action(
    token: str,
    action: ApprovalActionRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(RemediationApproval).where(RemediationApproval.approval_token == token)
    )
    approval = result.scalars().first()

    if not approval:
        raise HTTPException(status_code=404, detail="Approval token not found")

    if approval.status != "pending":
        raise HTTPException(status_code=400, detail=f"Approval token has already been resolved with status: {approval.status}")

    # Check token expiration
    now = datetime.now(timezone.utc)
    token_age = (now - approval.created_at.replace(tzinfo=timezone.utc)).total_seconds()
    if token_age > settings.APPROVAL_TOKEN_TTL_SECONDS:
        approval.status = "expired"
        approval.resolved_at = now
        await db.commit()
        raise HTTPException(status_code=400, detail="Approval token has expired. Please generate a new proposal.")

    approval.operator = action.operator
    approval.operator_comment = action.comment
    approval.resolved_at = now

    if action.approved:
        approval.status = "approved"
        # Parse proposed errata IDs
        errata_ids = [int(i.strip()) for i in approval.proposed_errata_ids.split(",") if i.strip().isdigit()]
        
        # Dispatch to FastMCP
        res = mcp_bridge.schedule_apply_errata(approval.server_id, errata_ids)
        approval.mlm_action_id = res.get("action_id")

        # Record in Audit Log
        audit = AuditLog(
            id=str(uuid.uuid4()),
            event_type="REMEDIATION_APPROVED",
            operator=action.operator,
            resource_type="Server",
            resource_id=str(approval.server_id),
            action_details=f"Approved errata installation ({approval.proposed_errata_ids}) on server {approval.server_id}. MLM Action ID: {approval.mlm_action_id}"
        )
        db.add(audit)
    else:
        approval.status = "rejected"
        audit = AuditLog(
            id=str(uuid.uuid4()),
            event_type="REMEDIATION_REJECTED",
            operator=action.operator,
            resource_type="Server",
            resource_id=str(approval.server_id),
            action_details=f"Rejected errata installation on server {approval.server_id}. Reason: {action.comment or 'None provided'}"
        )
        db.add(audit)

    await db.commit()
    await db.refresh(approval)
    return approval
