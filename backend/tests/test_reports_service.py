"""Reports Generation and Download Tests (TC-011, TC-012)."""
import pytest
import os

def test_tc_011_and_012_report_generation_and_download(test_client):
    # TC-011: Generate multi-format compliance report
    gen_payload = {
        "title": "Production Fleet Q3 Security Audit",
        "scope": "all",
        "target_id": "all",
        "formats": ["json", "csv", "pdf"]
    }
    gen_res = test_client.post("/api/v1/reports/generate", json=gen_payload)
    assert gen_res.status_code == 200
    report_data = gen_res.json()
    report_id = report_data["id"]

    assert os.path.exists(report_data["pdf_path"])
    assert os.path.exists(report_data["csv_path"])
    assert os.path.exists(report_data["json_path"])

    # TC-012: Download reports
    # Download JSON
    json_dl = test_client.get(f"/api/v1/reports/{report_id}/download/json")
    assert json_dl.status_code == 200
    assert json_dl.headers["content-type"] == "application/json"
    assert "SUSE MLM Security & Compliance Audit Report" in json_dl.text

    # Download CSV
    csv_dl = test_client.get(f"/api/v1/reports/{report_id}/download/csv")
    assert csv_dl.status_code == 200
    assert "text/csv" in csv_dl.headers["content-type"]
    assert "Server ID,Hostname,IP Address" in csv_dl.text

    # Download PDF
    pdf_dl = test_client.get(f"/api/v1/reports/{report_id}/download/pdf")
    assert pdf_dl.status_code == 200
    assert pdf_dl.headers["content-type"] == "application/pdf"
    assert pdf_dl.content.startswith(b"%PDF")
