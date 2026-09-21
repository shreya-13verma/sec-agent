def test_auditor_cannot_execute_remediation(client, auditor_headers, operator_headers):
    """TC-004: Auditor role is strictly read-only and cannot trigger remediation execution."""
    hosts_res = client.get("/api/v1/hosts", headers=operator_headers)
    host_id = hosts_res.json()["items"][0]["id"]
    analyze_res = client.post("/api/v1/agent/analyze", json={"host_id": host_id}, headers=operator_headers)
    plan_id = analyze_res.json()["proposed_plan_id"]

    # Auditor tries to approve
    approve_res = client.post(f"/api/v1/remediations/plans/{plan_id}/approve", json={"approval_notes": "test"}, headers=auditor_headers)
    assert approve_res.status_code == 403

    # Auditor tries to execute
    exec_res = client.post(f"/api/v1/remediations/plans/{plan_id}/execute", headers=auditor_headers)
    assert exec_res.status_code == 403

def test_sql_injection_protection(client, operator_headers):
    """TC-014: SQL injection payload in query parameters is sanitized without database errors."""
    sql_injection_payload = "' OR 1=1; DROP TABLE hosts; --"
    response = client.get(f"/api/v1/hosts?search={sql_injection_payload}", headers=operator_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []

    # Verify hosts table still exists and is intact
    healthy_res = client.get("/api/v1/hosts", headers=operator_headers)
    assert healthy_res.status_code == 200
    assert healthy_res.json()["total"] > 0

def test_audit_logs_recorded_and_queryable(client, admin_headers):
    """Audit logs recorded on user actions and queryable via API."""
    # Trigger an action that creates an audit log
    client.post("/api/v1/hosts/sync", json={"force_full_sync": True}, headers=admin_headers)

    response = client.get("/api/v1/audit-logs", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert data["total"] >= 1
    log_item = data["items"][0]
    assert "action" in log_item
    assert "resource_type" in log_item
    assert "timestamp" in log_item
