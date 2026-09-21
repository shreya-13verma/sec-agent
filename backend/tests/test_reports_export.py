def test_get_executive_compliance_data(client, auditor_headers):
    """Retrieve structured JSON executive compliance report."""
    response = client.get("/api/v1/reports/compliance", headers=auditor_headers)
    assert response.status_code == 200
    data = response.json()
    assert "fleet_total_hosts" in data
    assert "fleet_average_score" in data
    assert "framework_summaries" in data
    assert "host_details" in data
    assert len(data["framework_summaries"]) >= 1

def test_export_compliance_csv(client, auditor_headers):
    """TC-012: Export compliance report in CSV format."""
    response = client.get("/api/v1/reports/export/csv", headers=auditor_headers)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    csv_text = response.text
    assert "SUSE MLM Security & Compliance Audit Report" in csv_text
    assert "Fleet Total Hosts" in csv_text
    assert "Hostname" in csv_text

def test_export_compliance_pdf(client, auditor_headers):
    """TC-011: Export compliance report in PDF format."""
    response = client.get("/api/v1/reports/export/pdf", headers=auditor_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    content = response.content
    assert content.startswith(b"%PDF")
    assert len(content) > 1000
