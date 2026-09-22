"""Systems and Fleet Inventory Endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from backend.app.schemas.system import ServerSummary, PackageInfo
from backend.app.agent.mcp_client import mcp_bridge

router = APIRouter()

@router.get("", response_model=List[ServerSummary])
async def get_systems():
    """Retrieve all managed servers from SUSE MLM via FastMCP."""
    try:
        systems = mcp_bridge.list_systems()
        return [
            ServerSummary(
                id=s["id"],
                hostname=s["name"],
                ip_address=s["ip_address"],
                os_release=s["os_release"],
                kernel_version=s["kernel_version"],
                compliance_score=s.get("compliance_score", 0.0),
                security_errata_count=s.get("security_errata_count", 0),
                bugfix_errata_count=s.get("bugfix_errata_count", 0)
            ) for s in systems
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{server_id}")
async def get_system_detail(server_id: int):
    """Retrieve detailed metadata for a single server."""
    try:
        details = mcp_bridge.get_system_details(server_id)
        if not details:
            raise HTTPException(status_code=404, detail=f"Server {server_id} not found")
        return details
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{server_id}/packages", response_model=List[PackageInfo])
async def get_system_packages(server_id: int):
    """Retrieve installed RPM packages for a server."""
    try:
        packages = mcp_bridge.list_installed_packages(server_id)
        return packages
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
