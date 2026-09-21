from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from backend.app.database import get_db
from backend.app.models.audit_log import AuditLog
from backend.app.models.user import User
from backend.app.schemas.report import AuditLogListResponse
from backend.app.services.auth_service import get_current_user

router = APIRouter(prefix="/audit-logs", tags=["Immutable Audit Trail"])

@router.get("", response_model=AuditLogListResponse)
def list_audit_logs(
    action: Optional[str] = Query(None, description="Filter by action type"),
    resource_type: Optional[str] = Query(None, description="Filter by resource"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action)
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)

    total = query.count()
    items = query.order_by(AuditLog.id.desc()).offset(offset).limit(limit).all()
    return {"total": total, "items": items}
