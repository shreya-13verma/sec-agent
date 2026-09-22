"""
FastMCP Client Bridge for LangGraph Agent.
Dispatches tool invocations to FastMCP tools with session handling.
"""
from typing import Dict, Any, List, Optional
import logging
from mcp_server.server import (
    auth_login,
    auth_logout,
    system_list_systems,
    system_get_details,
    system_list_installed_packages,
    audit_list_scap_profiles,
    audit_schedule_xccdf_scan,
    audit_get_xccdf_scan_details,
    errata_find_by_cve,
    system_get_relevant_errata,
    system_schedule_apply_errata,
    schedule_get_action_status
)

logger = logging.getLogger("backend.agent.mcp_client")

class FastMCPBridge:
    def __init__(self):
        self._session_token: Optional[str] = None

    def ensure_authenticated(self) -> str:
        """Authenticate with SUSE MLM FastMCP server."""
        if not self._session_token:
            res = auth_login("admin", "linux")
            if res.get("status") == "success":
                self._session_token = res["session_token"]
            else:
                raise RuntimeError(f"FastMCP Auth failed: {res.get('message')}")
        return self._session_token

    def list_systems(self) -> List[Dict[str, Any]]:
        token = self.ensure_authenticated()
        res = system_list_systems(token)
        return res.get("systems", [])

    def get_system_details(self, server_id: int) -> Dict[str, Any]:
        token = self.ensure_authenticated()
        res = system_get_details(token, server_id)
        return res.get("details", {})

    def list_installed_packages(self, server_id: int) -> List[Dict[str, Any]]:
        token = self.ensure_authenticated()
        res = system_list_installed_packages(token, server_id)
        return res.get("packages", [])

    def list_scap_profiles(self) -> List[Dict[str, Any]]:
        token = self.ensure_authenticated()
        res = audit_list_scap_profiles(token)
        return res.get("profiles", [])

    def get_xccdf_scan_details(self, server_id: int) -> Dict[str, Any]:
        token = self.ensure_authenticated()
        res = audit_get_xccdf_scan_details(token, server_id)
        return res.get("scan_details", {})

    def schedule_xccdf_scan(self, server_id: int, profile_name: str) -> Dict[str, Any]:
        token = self.ensure_authenticated()
        return audit_schedule_xccdf_scan(token, server_id, profile_name)

    def find_errata_by_cve(self, cve_id: str) -> List[Dict[str, Any]]:
        token = self.ensure_authenticated()
        res = errata_find_by_cve(token, cve_id)
        return res.get("advisories", [])

    def get_relevant_errata(self, server_id: int) -> List[Dict[str, Any]]:
        token = self.ensure_authenticated()
        res = system_get_relevant_errata(token, server_id)
        return res.get("errata", [])

    def schedule_apply_errata(self, server_id: int, errata_ids: List[int]) -> Dict[str, Any]:
        token = self.ensure_authenticated()
        return system_schedule_apply_errata(token, server_id, errata_ids)

    def get_action_status(self, action_id: int) -> Dict[str, Any]:
        token = self.ensure_authenticated()
        res = schedule_get_action_status(token, action_id)
        return res.get("action", {})

mcp_bridge = FastMCPBridge()
