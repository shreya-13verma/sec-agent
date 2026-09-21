def test_list_compliance_frameworks(client, admin_headers):
    """List seeded compliance frameworks."""
    response = client.get("/api/v1/compliance/frameworks", headers=admin_headers)
    assert response.status_code == 200
    frameworks = response.json()
    assert len(frameworks) >= 3
    codes = [f["code"] for f in frameworks]
    assert "CIS_SLES_15" in codes
    assert "HIPAA" in codes
    assert "PCI_DSS_V4" in codes

def test_get_framework_detail_with_rules(client, admin_headers):
    """Get framework detail with its rule definitions."""
    res_list = client.get("/api/v1/compliance/frameworks", headers=admin_headers)
    framework_id = res_list.json()[0]["id"]

    res_detail = client.get(f"/api/v1/compliance/frameworks/{framework_id}", headers=admin_headers)
    assert res_detail.status_code == 200
    data = res_detail.json()
    assert "rules" in data
    assert len(data["rules"]) > 0
    rule = data["rules"][0]
    assert "rule_identifier" in rule
    assert "check_type" in rule
    assert "severity" in rule

def test_trigger_compliance_scan_and_inspect_findings(client, sec_officer_headers):
    """TC-006: Trigger a compliance audit scan against CIS framework."""
    # Get CIS framework id
    res_fw = client.get("/api/v1/compliance/frameworks", headers=sec_officer_headers)
    cis_fw = next(f for f in res_fw.json() if f["code"] == "CIS_SLES_15")

    # Trigger scan
    scan_res = client.post(
        "/api/v1/compliance/scans",
        json={"framework_id": cis_fw["id"]},
        headers=sec_officer_headers
    )
    assert scan_res.status_code == 202
    scan_data = scan_res.json()
    assert scan_data["scan_status"] == "COMPLETED"
    assert scan_data["hosts_scanned_count"] >= 1
    assert scan_data["overall_score"] > 0
    scan_id = scan_data["id"]

    # Get scan detail with findings
    detail_res = client.get(f"/api/v1/compliance/scans/{scan_id}", headers=sec_officer_headers)
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert len(detail_data["findings"]) > 0

    # Query findings endpoint with filter
    findings_res = client.get(f"/api/v1/compliance/findings?scan_id={scan_id}&status=FAIL", headers=sec_officer_headers)
    assert findings_res.status_code == 200
    failed_findings = findings_res.json()
    assert all(f["status"] == "FAIL" for f in failed_findings)

def test_scan_nonexistent_framework(client, sec_officer_headers):
    """Scanning non-existent framework returns 400 Bad Request."""
    res = client.post("/api/v1/compliance/scans", json={"framework_id": 99999}, headers=sec_officer_headers)
    assert res.status_code == 400
