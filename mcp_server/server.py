"""
FastMCP Server for SUSE Multi-Linux Manager (MLM) / Uyuni Security & Compliance.
Exposes standard MCP tools wrapping XML-RPC endpoints.
"""
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP
from mcp_server.mlm_client import mlm_client, MLMClientException
import os

mcp = FastMCP("suse-mlm-security")

@mcp.tool()
def auth_login(username: str = "admin", password: str = "linux") -> Dict[str, Any]:
    """Authenticate with SUSE MLM XML-RPC and obtain an active session key."""
    try:
        token = mlm_client.login(username, password)
        return {"status": "success", "session_token": token, "username": username}
    except MLMClientException as e:
        return {"status": "error", "code": e.code, "message": e.message}

@mcp.tool()
def auth_logout(session_token: str) -> Dict[str, Any]:
    """Terminate the active SUSE MLM session."""
    try:
        success = mlm_client.logout(session_token)
        return {"status": "success", "logged_out": success}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def system_list_systems(session_token: str = "") -> Dict[str, Any]:
    """List all managed Linux servers registered in SUSE MLM / Uyuni."""
    try:
        systems = mlm_client.list_systems(session_token)
        return {"status": "success", "count": len(systems), "systems": systems}
    except MLMClientException as e:
        return {"status": "error", "code": e.code, "message": e.message}

@mcp.tool()
def system_get_details(session_token: str = "", server_id: int = 1000010000) -> Dict[str, Any]:
    """Get system metadata, kernel, OS, and status for a specific server."""
    try:
        details = mlm_client.get_system_details(session_token, server_id)
        return {"status": "success", "details": details}
    except MLMClientException as e:
        return {"status": "error", "code": e.code, "message": e.message}

@mcp.tool()
def system_list_installed_packages(session_token: str = "", server_id: int = 1000010000) -> Dict[str, Any]:
    """List installed RPM packages and versions for a given server."""
    try:
        packages = mlm_client.list_installed_packages(session_token, server_id)
        return {"status": "success", "server_id": server_id, "packages": packages}
    except MLMClientException as e:
        return {"status": "error", "code": e.code, "message": e.message}

@mcp.tool()
def audit_list_scap_profiles(session_token: str = "") -> Dict[str, Any]:
    """List native OpenSCAP security benchmark profiles available in SUSE MLM (e.g. CIS, DISA STIG, HIPAA)."""
    try:
        profiles = mlm_client.list_scap_profiles(session_token)
        return {"status": "success", "count": len(profiles), "profiles": profiles}
    except MLMClientException as e:
        return {"status": "error", "code": e.code, "message": e.message}

@mcp.tool()
def audit_schedule_xccdf_scan(
    session_token: str = "",
    server_id: int = 1000010000,
    profile_name: str = "xccdf_org.ssgproject.content_profile_cis",
    path: str = "/usr/share/xml/scap/ssg/content/ssg-sle15-xccdf.xml"
) -> Dict[str, Any]:
    """Schedule an asynchronous OpenSCAP XCCDF compliance audit scan on a managed host."""
    try:
        action_id = mlm_client.schedule_xccdf_scan(session_token, server_id, profile_name, path)
        return {"status": "success", "action_id": action_id, "server_id": server_id, "profile": profile_name}
    except MLMClientException as e:
        return {"status": "error", "code": e.code, "message": e.message}

@mcp.tool()
def audit_get_xccdf_scan_details(session_token: str = "", server_id: int = 1000010000) -> Dict[str, Any]:
    """Retrieve detailed pass/fail rule results and compliance score for a server's latest OpenSCAP audit."""
    try:
        details = mlm_client.get_xccdf_scan_details(session_token, server_id)
        return {"status": "success", "scan_details": details}
    except MLMClientException as e:
        return {"status": "error", "code": e.code, "message": e.message}

@mcp.tool()
def errata_find_by_cve(session_token: str = "", cve_id: str = "CVE-2024-6387") -> Dict[str, Any]:
    """Lookup SUSE Errata advisories addressing a specific CVE identifier (e.g. CVE-2024-3094)."""
    try:
        advisories = mlm_client.find_errata_by_cve(session_token, cve_id)
        return {"status": "success", "cve_id": cve_id, "advisories": advisories}
    except MLMClientException as e:
        return {"status": "error", "code": e.code, "message": e.message}

@mcp.tool()
def system_get_relevant_errata(session_token: str = "", server_id: int = 1000010000) -> Dict[str, Any]:
    """Fetch all pending security, bugfix, and enhancement errata applicable to a server."""
    try:
        errata = mlm_client.get_relevant_errata(session_token, server_id)
        return {"status": "success", "server_id": server_id, "count": len(errata), "errata": errata}
    except MLMClientException as e:
        return {"status": "error", "code": e.code, "message": e.message}

@mcp.tool()
def system_schedule_apply_errata(session_token: str = "", server_id: int = 1000010000, errata_ids: List[int] = []) -> Dict[str, Any]:
    """Schedule installation of selected errata advisories on a target server."""
    try:
        action_id = mlm_client.schedule_apply_errata(session_token, server_id, errata_ids)
        return {"status": "success", "action_id": action_id, "server_id": server_id, "errata_ids": errata_ids}
    except MLMClientException as e:
        return {"status": "error", "code": e.code, "message": e.message}

@mcp.tool()
def schedule_get_action_status(session_token: str = "", action_id: int = 90001) -> Dict[str, Any]:
    """Check the execution status of a scheduled scan or patch action in SUSE MLM."""
    try:
        status_info = mlm_client.get_action_status(session_token, action_id)
        return {"status": "success", "action": status_info}
    except MLMClientException as e:
        return {"status": "error", "code": e.code, "message": e.message}

if __name__ == "__main__":
    mcp.run()
