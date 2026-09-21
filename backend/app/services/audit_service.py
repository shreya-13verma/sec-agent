from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional
from backend.app.models.audit_log import AuditLog
from backend.app.models.user import User

def log_audit_event(
    db: Session,
    action: str,
    resource_type: str,
    resource_id: str,
    details: str,
    user: Optional[User] = None,
    ip_address: str = "127.0.0.1"
) -> AuditLog:
    user_id = user.id if user else None
    username = user.username if user else "SYSTEM"
    
    log = AuditLog(
        user_id=user_id,
        user_username=username,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id),
        details=details,
        ip_address=ip_address,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(log)
    db.commit()
    return log
