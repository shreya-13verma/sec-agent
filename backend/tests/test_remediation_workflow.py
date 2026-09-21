def test_remediation_approval_and_execution_lifecycle(client, sec_officer_headers, operator_headers):
    """TC-008, TC-010: Complete controlled remediation lifecycle (Stage -> Approve -> Execute -> Post-verification)."""
    # 1. Analyze host to stage a plan
    hosts_res = client.get("/api/v1/hosts", headers=operator_headers)
    host_id = hosts_res.json()["items"][0]["id"]

    analyze_res = client.post("/api/v1/agent/analyze", json={"host_id": host_id}, headers=operator_headers)
    assert analyze_res.status_code == 200
    plan_id = analyze_res.json()["proposed_plan_id"]
    assert plan_id is not None

    # 2. Verify cannot execute unapproved plan
    exec_fail_res = client.post(f"/api/v1/remediations/plans/{plan_id}/execute", headers=operator_headers)
    assert exec_fail_res.status_code == 400
    assert "Cannot execute unapproved plan" in exec_fail_res.json()["detail"]

    # 3. Approve plan as Security Officer (TC-008)
    approve_res = client.post(
        f"/api/v1/remediations/plans/{plan_id}/approve",
        json={"approval_notes": "Security approved for off-peak deployment"},
        headers=sec_officer_headers
    )
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "APPROVED"

    # 4. Execute approved plan (TC-010)
    exec_res = client.post(f"/api/v1/remediations/plans/{plan_id}/execute", headers=operator_headers)
    assert exec_res.status_code == 202
    exec_data = exec_res.json()
    assert exec_data["status"] == "COMPLETED"
    assert exec_data["dispatched_steps_count"] >= 1

    # 5. Check plan detail has SUCCESS steps
    plan_detail_res = client.get(f"/api/v1/remediations/plans/{plan_id}", headers=operator_headers)
    assert plan_detail_res.status_code == 200
    plan_detail = plan_detail_res.json()
    assert plan_detail["status"] == "COMPLETED"
    assert all(s["status"] == "SUCCESS" for s in plan_detail["steps"])

def test_reject_staged_remediation_plan(client, sec_officer_headers, operator_headers):
    """TC-009: Reject staged remediation plan with reason."""
    hosts_res = client.get("/api/v1/hosts", headers=operator_headers)
    host_id = hosts_res.json()["items"][1]["id"]

    analyze_res = client.post("/api/v1/agent/analyze", json={"host_id": host_id}, headers=operator_headers)
    plan_id = analyze_res.json()["proposed_plan_id"]

    reject_res = client.post(
        f"/api/v1/remediations/plans/{plan_id}/reject",
        json={"rejection_reason": "Maintenance window postponed"},
        headers=sec_officer_headers
    )
    assert reject_res.status_code == 200
    data = reject_res.json()
    assert data["status"] == "REJECTED"
    assert data["rejection_reason"] == "Maintenance window postponed"
