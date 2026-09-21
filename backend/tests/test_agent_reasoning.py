def test_agent_analyze_host_and_generate_staged_plan(client, operator_headers):
    """TC-007: Autonomous Agent multi-step reasoning, drift detection, and plan staging."""
    # Find host with missing errata / drift (e.g. sles15-prod-db01)
    hosts_res = client.get("/api/v1/hosts", headers=operator_headers)
    host_id = hosts_res.json()["items"][0]["id"]

    # Trigger agent analysis
    analyze_res = client.post(
        "/api/v1/agent/analyze",
        json={"host_id": host_id},
        headers=operator_headers
    )
    assert analyze_res.status_code == 200
    data = analyze_res.json()
    assert data["host_id"] == host_id
    assert data["analysis_status"] == "PLAN_GENERATED"
    assert "thought_steps" in data
    assert len(data["thought_steps"]) >= 4

    # Verify structured thought types (OBSERVATION, CORRELATION, RISK_EVALUATION, DECISION)
    thought_types = [t["thought_type"] for t in data["thought_steps"]]
    assert "OBSERVATION" in thought_types
    assert "CORRELATION" in thought_types
    assert "RISK_EVALUATION" in thought_types
    assert "DECISION" in thought_types

    # Verify proposed plan id was created
    assert data["proposed_plan_id"] is not None

def test_get_analysis_detail(client, operator_headers):
    """Retrieve existing agent analysis by ID."""
    hosts_res = client.get("/api/v1/hosts", headers=operator_headers)
    host_id = hosts_res.json()["items"][0]["id"]

    analyze_res = client.post("/api/v1/agent/analyze", json={"host_id": host_id}, headers=operator_headers)
    analysis_id = analyze_res.json()["id"]

    detail_res = client.get(f"/api/v1/agent/analyses/{analysis_id}", headers=operator_headers)
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["id"] == analysis_id
    assert len(detail["thought_steps"]) > 0

def test_fleet_drift_detection(client, operator_headers):
    """Calculate fleet-wide drift summary."""
    drift_res = client.get("/api/v1/agent/drift-detection", headers=operator_headers)
    assert drift_res.status_code == 200
    data = drift_res.json()
    assert "total_hosts" in data
    assert "drifting_hosts_count" in data
    assert "drift_summary" in data
    assert len(data["drift_summary"]) >= 1
    assert "drift_level" in data["drift_summary"][0]
