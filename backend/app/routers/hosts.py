from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from backend.app.database import get_db
from backend.app.models.host import Host, HostPackage, HostMissingErrata, HostChannel
from backend.app.models.user import User
from backend.app.schemas.host import HostSummary, HostDetail, HostListResponse, SyncRequest, SyncResponse
from backend.app.services.auth_service import get_current_user, require_roles
from backend.app.services.audit_service import log_audit_event
from backend.app.utils.seed_data import sync_hosts_from_mlm

router = APIRouter(prefix="/hosts", tags=["Host Inventory & MLM Sync"])

@router.get("", response_model=HostListResponse)
def list_hosts(
    search: Optional[str] = Query(None, description="Search by hostname or IP"),
    compliance_status: Optional[str] = Query(None, description="Filter by status (COMPLIANT, NON_COMPLIANT, CRITICAL, UNKNOWN)"),
    os_family: Optional[str] = Query(None, description="Filter by OS (SLES, RHEL, openSUSE)"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Host)
    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            (Host.hostname.ilike(search_pattern)) | (Host.ip_address.ilike(search_pattern))
        )
    if compliance_status:
        query = query.filter(Host.compliance_status == compliance_status)
    if os_family:
        query = query.filter(Host.os_family == os_family)

    total = query.count()
    items = query.order_by(Host.id.asc()).offset(offset).limit(limit).all()
    return {"total": total, "items": items}

@router.get("/{host_id}", response_model=HostDetail)
def get_host_detail(
    host_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    host = db.query(Host).options(
        joinedload(Host.channels),
        joinedload(Host.packages),
        joinedload(Host.missing_errata).joinedload(HostMissingErrata.errata)
    ).filter(Host.id == host_id).first()

    if not host:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Host with ID {host_id} not found"
        )
    return host

@router.post("/sync", response_model=SyncResponse, status_code=status.HTTP_202_ACCEPTED)
def trigger_mlm_inventory_sync(
    sync_req: SyncRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Security_Officer", "Operator"]))
):
    try:
        sync_hosts_from_mlm(db)
        total_hosts = db.query(Host).count()
        total_errata = db.query(HostMissingErrata).count()

        log_audit_event(
            db=db,
            action="MLM_INVENTORY_SYNC",
            resource_type="HOST_FLEET",
            resource_id="ALL",
            details=f"Synchronized {total_hosts} hosts and {total_errata} errata associations from SUSE MLM",
            user=current_user
        )

        return {
            "status": "SUCCESS",
            "message": "SUSE Multi-Linux Manager host inventory successfully synchronized.",
            "synced_hosts_count": total_hosts,
            "synced_errata_count": total_errata
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inventory synchronization failed: {str(e)}"
        )

@router.delete("/{host_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_host(
    host_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin"]))
):
    host = db.query(Host).filter(Host.id == host_id).first()
    if not host:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Host with ID {host_id} not found"
        )
    hostname = host.hostname
    db.delete(host)
    db.commit()

    log_audit_event(
        db=db,
        action="HOST_DELETED",
        resource_type="HOST",
        resource_id=str(host_id),
        details=f"Host '{hostname}' removed by Admin '{current_user.username}'",
        user=current_user
    )
    return None
