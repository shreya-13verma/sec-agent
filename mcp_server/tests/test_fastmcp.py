"""Unit and integration tests for FastMCP SUSE MLM tools (TC-001 - TC-005)."""
import pytest
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

def test_tc_001_auth_login_and_logout():
    # TC-001: FastMCP auth.login with valid credentials
    login_res = auth_login("admin", "linux")
    assert login_res["status"] == "success"
    assert "session_token" in login_res
    token = login_res["session_token"]

    # Logout
    logout_res = auth_logout(token)
    assert logout_res["status"] == "success"
    assert logout_res["logged_out"] is True

def test_tc_002_system_list_and_details():
    # TC-002: FastMCP system.listSystems and details
    login_res = auth_login("admin", "linux")
    token = login_res["session_token"]

    sys_res = system_list_systems(token)
    assert sys_res["status"] == "success"
    assert sys_res["count"] >= 4
    server = sys_res["systems"][0]
    server_id = server["id"]

    details_res = system_get_details(token, server_id)
    assert details_res["status"] == "success"
    assert details_res["details"]["id"] == server_id

    pkg_res = system_list_installed_packages(token, server_id)
    assert pkg_res["status"] == "success"
    assert len(pkg_res["packages"]) > 0

def test_tc_003_audit_scap_profiles_and_scan():
    # TC-003: FastMCP audit.listScapProfiles and scan details
    login_res = auth_login("admin", "linux")
    token = login_res["session_token"]

    profiles_res = audit_list_scap_profiles(token)
    assert profiles_res["status"] == "success"
    assert any("cis" in p["profile_name"].lower() for p in profiles_res["profiles"])

    # Scan details
    details_res = audit_get_xccdf_scan_details(token, 1000010000)
    assert details_res["status"] == "success"
    assert "score" in details_res["scan_details"]

    # Schedule scan
    sched_res = audit_schedule_xccdf_scan(token, 1000010000, "xccdf_org.ssgproject.content_profile_cis")
    assert sched_res["status"] == "success"
    assert "action_id" in sched_res

def test_tc_004_errata_find_by_cve_and_relevant():
    # TC-004: FastMCP errata.findByCve and relevant errata
    login_res = auth_login("admin", "linux")
    token = login_res["session_token"]

    cve_res = errata_find_by_cve(token, "CVE-2024-6387")
    assert cve_res["status"] == "success"
    assert len(cve_res["advisories"]) > 0

    rel_res = system_get_relevant_errata(token, 1000010000)
    assert rel_res["status"] == "success"
    assert rel_res["count"] > 0

def test_tc_005_error_handling_and_schedule():
    # TC-005: FastMCP invalid session and error handling
    invalid_res = auth_login("admin", "wrong_password_xyz")
    assert invalid_res["status"] == "error"
    assert invalid_res["code"] == 1001

    # Schedule apply errata and verify status
    login_res = auth_login("admin", "linux")
    token = login_res["session_token"]
    apply_res = system_schedule_apply_errata(token, 1000010000, [81829])
    assert apply_res["status"] == "success"
    action_id = apply_res["action_id"]

    status_res = schedule_get_action_status(token, action_id)
    assert status_res["status"] == "success"
    assert status_res["action"]["action_id"] == action_id
