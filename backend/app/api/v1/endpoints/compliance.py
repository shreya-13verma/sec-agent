"""Compliance and OpenSCAP Endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from backend.app.agent.mcp_client import mcp_bridge

router = APIRouter()

@router.get("/scap-profiles")
async def list_scap_profiles():
    """List native OpenSCAP profiles."""
    try:
        profiles = mcp_bridge.list_scap_profiles()
        return {"profiles": profiles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scans/{server_id}")
async def get_server_scap_scan(server_id: int):
    """Get latest OpenSCAP scan details for a server."""
    try:
        scan_details = mcp_bridge.get_xccdf_scan_details(server_id)
        return scan_details
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/errata/{server_id}")
async def get_server_errata(server_id: int):
    """Get pending errata advisories for a server."""
    try:
        errata = mcp_bridge.get_relevant_errata(server_id)
        return {"server_id": server_id, "count": len(errata), "errata": errata}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scans/schedule")
async def schedule_scan(server_id: int, profile_name: str = "xccdf_org.ssgproject.content_profile_cis"):
    """Schedule an OpenSCAP scan via FastMCP."""
    try:
        res = mcp_bridge.schedule_xccdf_scan(server_id, profile_name)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
