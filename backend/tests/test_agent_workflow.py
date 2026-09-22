"""Agent Workflow and Human-in-the-Loop Tests (TC-006, TC-007) with live SUSE MLM."""
import pytest
from backend.app.agent.graph import compliance_agent

def test_tc_006_read_only_compliance_evaluation():
    # User queries compliance for a live server
    initial_state = {
        "session_id": "test_sess_01",
        "user_query": "Which rules failed CIS benchmark audit for server hana-node1?",
        "intent": None,
        "thought_log": [],
        "tool_calls": [],
        "approval_required": False,
        "approval_token": None,
        "remediation_plan": None,
        "final_response": "",
        "status": "INIT"
    }

    result = compliance_agent.invoke(initial_state)

    assert result["intent"] == "compliance_scan_query"
    assert result["approval_required"] is False
    assert len(result["thought_log"]) > 0
    assert any(tc["tool"] == "audit_get_xccdf_scan_details" for tc in result["tool_calls"])
    assert "OpenSCAP Compliance Audit Results" in result["final_response"]
    assert "Passed" in result["final_response"]

def test_tc_007_remediation_intent_triggers_interrupt_token():
    # User requests state-modifying action (patch/remediate) on live host trento-server
    initial_state = {
        "session_id": "test_sess_02",
        "user_query": "Please patch and remediate pending security errata on server 1000010000",
        "intent": None,
        "thought_log": [],
        "tool_calls": [],
        "approval_required": False,
        "approval_token": None,
        "remediation_plan": None,
        "final_response": "",
        "status": "INIT"
    }

    result = compliance_agent.invoke(initial_state)

    assert result["intent"] == "remediation_request"
    assert result["approval_required"] is True
    assert result["approval_token"] is not None
    assert result["approval_token"].startswith("appr_tok_")
    assert result["remediation_plan"]["server_id"] == 1000010000
    assert result["remediation_plan"]["errata_count"] > 0
    assert "Operator Approval Required" in result["final_response"]
