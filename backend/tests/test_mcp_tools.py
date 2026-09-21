import pytest
from backend.app.mcp_server import (
    suse_mlm_list_systems,
    suse_mlm_get_system_details,
    suse_mlm_list_installed_packages,
    suse_mlm_list_subscribed_channels,
    suse_mlm_list_applicable_errata,
    suse_mlm_schedule_apply_errata,
    suse_mlm_schedule_package_install,
    suse_mlm_schedule_package_remove
)

def test_mcp_list_systems():
    """Test FastMCP tool suse_mlm_list_systems returns registered systems."""
    systems = suse_mlm_list_systems()
    assert isinstance(systems, list)
    assert len(systems) >= 1
    sys0 = systems[0]
    assert "id" in sys0
    assert "name" in sys0

def test_mcp_get_system_details():
    """Test FastMCP tool suse_mlm_get_system_details."""
    systems = suse_mlm_list_systems()
    sys_id = systems[0]["id"]
    details = suse_mlm_get_system_details(system_id=sys_id)
    assert isinstance(details, dict)
    assert details["id"] == sys_id
    assert "hostname" in details
    assert "release" in details

def test_mcp_list_installed_packages():
    """Test FastMCP tool suse_mlm_list_installed_packages."""
    systems = suse_mlm_list_systems()
    sys_id = systems[0]["id"]
    packages = suse_mlm_list_installed_packages(system_id=sys_id)
    assert isinstance(packages, list)
    assert len(packages) >= 1
    assert "name" in packages[0]
    assert "version" in packages[0]

def test_mcp_list_subscribed_channels():
    """Test FastMCP tool suse_mlm_list_subscribed_channels."""
    systems = suse_mlm_list_systems()
    sys_id = systems[0]["id"]
    channels = suse_mlm_list_subscribed_channels(system_id=sys_id)
    assert isinstance(channels, list)

def test_mcp_list_applicable_errata():
    """Test FastMCP tool suse_mlm_list_applicable_errata."""
    systems = suse_mlm_list_systems()
    sys_id = systems[0]["id"]
    errata = suse_mlm_list_applicable_errata(system_id=sys_id)
    assert isinstance(errata, list)

def test_mcp_schedule_actions():
    """Test FastMCP action scheduling tools."""
    systems = suse_mlm_list_systems()
    sys_id = systems[0]["id"]

    # Test errata schedule
    res_errata = suse_mlm_schedule_apply_errata(system_id=sys_id, advisory_name="SUSE-15-SP7-2026-4264")
    assert res_errata["status"] in ("SCHEDULED", "SUCCESS")
    assert "action_id" in res_errata

    # Test package install schedule
    res_pkg = suse_mlm_schedule_package_install(system_id=sys_id, package_name="audit")
    assert res_pkg["status"] == "SCHEDULED"
    assert "action_id" in res_pkg

    # Test package remove schedule
    res_rm = suse_mlm_schedule_package_remove(system_id=sys_id, package_name="telnet")
    assert res_rm["status"] == "SCHEDULED"
    assert "action_id" in res_rm
