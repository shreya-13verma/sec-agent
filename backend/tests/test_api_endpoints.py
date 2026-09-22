"""API Endpoints and Approval Security Tests (TC-008, TC-009, TC-010)."""
import pytest

def test_tc_008_systems_and_compliance_endpoints(test_client):
    # Test systems listing
    res = test_client.get("/api/v1/systems")
    assert res.status_code == 200
    systems = res.json()
    assert len(systems) >= 4
    assert systems[0]["hostname"].startswith("sles15")

    # Test server details
    server_id = systems[0]["id"]
    detail_res = test_client.get(f"/api/v1/systems/{server_id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["id"] == server_id

    # Test SCAP profiles
    scap_res = test_client.get("/api/v1/compliance/scap-profiles")
    assert scap_res.status_code == 200
    assert len(scap_res.json()["profiles"]) > 0

    # Test server scan details
    scan_res = test_client.get(f"/api/v1/compliance/scans/{server_id}")
    assert scan_res.status_code == 200
    assert "score" in scan_res.json()

def test_tc_009_chat_streaming_and_approval_resolution(test_client):
    # Post chat message requesting patch
    chat_payload = {
        "message": "Apply security errata to server 1001"
    }
    res = test_client.post("/api/v1/chat/message", json=chat_payload)
    assert res.status_code == 200
    content = res.text

    # Verify SSE events
    assert "event: session_id" in content
    assert "event: thought" in content
    assert "event: approval_required" in content

    # Fetch pending approvals
    pending_res = test_client.get("/api/v1/approvals/pending")
    assert pending_res.status_code == 200
    pending_list = pending_res.json()
    assert len(pending_list) > 0

    token = pending_list[0]["approval_token"]

    # TC-009: Approve the remediation
    approve_res = test_client.post(f"/api/v1/approvals/{token}/action", json={
        "approved": True,
        "operator": "Senior SecOps Engineer",
        "comment": "Approved during maintenance window."
    })
    assert approve_res.status_code == 200
    approved_data = approve_res.json()
    assert approved_data["status"] == "approved"
    assert approved_data["mlm_action_id"] is not None

def test_tc_010_approval_security_and_invalid_token(test_client):
    # TC-010: Invalid approval token rejected
    res = test_client.post("/api/v1/approvals/invalid_fake_token_999/action", json={
        "approved": True,
        "operator": "Attacker",
        "comment": "Unauthorized attempt"
    })
    assert res.status_code == 404

    # Post message to get a fresh token then reject
    chat_payload = {"message": "Remediate vulnerabilities on host 1004"}
    chat_res = test_client.post("/api/v1/chat/message", json=chat_payload)
    assert chat_res.status_code == 200

    pending_res = test_client.get("/api/v1/approvals/pending")
    token = pending_res.json()[0]["approval_token"]

    # Reject
    reject_res = test_client.post(f"/api/v1/approvals/{token}/action", json={
        "approved": False,
        "operator": "Security Auditor",
        "comment": "Host is undergoing freeze"
    })
    assert reject_res.status_code == 200
    assert reject_res.json()["status"] == "rejected"

    # Attempt re-approval on already resolved token should fail
    dup_res = test_client.post(f"/api/v1/approvals/{token}/action", json={
        "approved": True
    })
    assert dup_res.status_code == 400
