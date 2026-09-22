"""LangGraph Agent Nodes with deterministic intent routing and FastMCP execution."""
import re
import uuid
import secrets
from typing import Dict, Any, List
from backend.app.agent.state import AgentState
from backend.app.agent.mcp_client import mcp_bridge

def analyze_intent(state: AgentState) -> Dict[str, Any]:
    """Classify user query into actionable security/compliance intent."""
    query = state["user_query"].lower()
    thoughts = list(state.get("thought_log", []))

    if any(k in query for k in ["apply", "patch", "remediate", "fix vulnerability", "update package", "schedule apply"]):
        intent = "remediation_request"
        thoughts.append("Identified state-altering intent: Errata remediation proposal requires human-in-the-loop approval.")
    elif any(k in query for k in ["cve-", "cve", "advisory", "errata"]):
        intent = "errata_cve_query"
        thoughts.append("Identified read-only intent: Vulnerability & Errata lookup via FastMCP.")
    elif any(k in query for k in ["cis", "disa", "stig", "hipaa", "scap", "openscap", "benchmark", "failed rule", "audit"]):
        intent = "compliance_scan_query"
        thoughts.append("Identified read-only intent: OpenSCAP compliance & rule failure evaluation.")
    elif any(k in query for k in ["report", "export", "pdf", "csv", "summary"]):
        intent = "report_export_query"
        thoughts.append("Identified intent: Compliance report generation and download request.")
    else:
        intent = "inventory_query"
        thoughts.append("Identified read-only intent: Managed server fleet inventory inquiry.")

    return {
        "intent": intent,
        "thought_log": thoughts
    }

def execute_tools(state: AgentState) -> Dict[str, Any]:
    """Execute read-only FastMCP tools based on classified intent."""
    intent = state.get("intent")
    query = state.get("user_query", "")
    thoughts = list(state.get("thought_log", []))
    tool_calls = list(state.get("tool_calls", []))

    # Extract target server ID if present
    server_match = re.search(r"\b(100[1-4])\b", query)
    server_id = int(server_match.group(1)) if server_match else None

    # Extract CVE ID if present
    cve_match = re.search(r"(CVE-\d{4}-\d{4,7})", query, re.IGNORECASE)
    cve_id = cve_match.group(1).upper() if cve_match else None

    if intent == "compliance_scan_query":
        thoughts.append("Calling FastMCP `audit_list_scap_profiles` & `audit_get_xccdf_scan_details`...")
        profiles = mcp_bridge.list_scap_profiles()
        target_sid = server_id or 1001
        scan_data = mcp_bridge.get_xccdf_scan_details(target_sid)
        tool_calls.append({
            "tool": "audit_get_xccdf_scan_details",
            "server_id": target_sid,
            "result": scan_data
        })
    elif intent == "errata_cve_query":
        if cve_id:
            thoughts.append(f"Calling FastMCP `errata_find_by_cve` for identifier {cve_id}...")
            advisories = mcp_bridge.find_errata_by_cve(cve_id)
            tool_calls.append({
                "tool": "errata_find_by_cve",
                "cve_id": cve_id,
                "result": advisories
            })
        else:
            target_sid = server_id or 1001
            thoughts.append(f"Calling FastMCP `system_get_relevant_errata` for server ID {target_sid}...")
            errata = mcp_bridge.get_relevant_errata(target_sid)
            tool_calls.append({
                "tool": "system_get_relevant_errata",
                "server_id": target_sid,
                "result": errata
            })
    elif intent == "inventory_query":
        thoughts.append("Calling FastMCP `system_list_systems`...")
        systems = mcp_bridge.list_systems()
        tool_calls.append({
            "tool": "system_list_systems",
            "result": systems
        })

    return {
        "thought_log": thoughts,
        "tool_calls": tool_calls
    }

def plan_remediation(state: AgentState) -> Dict[str, Any]:
    """Generate remediation plan and trigger human-in-the-loop approval gate."""
    query = state.get("user_query", "")
    thoughts = list(state.get("thought_log", []))
    tool_calls = list(state.get("tool_calls", []))

    server_match = re.search(r"\b(100[1-4])\b", query)
    server_id = int(server_match.group(1)) if server_match else 1001

    thoughts.append(f"Inspecting pending errata for server ID {server_id} via FastMCP...")
    errata = mcp_bridge.get_relevant_errata(server_id)
    errata_ids = [e["id"] for e in errata]

    approval_token = f"appr_tok_{secrets.token_hex(16)}"
    thoughts.append(f"Generated single-use cryptographic approval token: {approval_token}")

    remediation_plan = {
        "server_id": server_id,
        "errata_count": len(errata),
        "errata_ids": errata_ids,
        "advisories": [e["advisory_name"] for e in errata],
        "cves": [e["cve_id"] for e in errata if e.get("cve_id") != "N/A"]
    }

    return {
        "thought_log": thoughts,
        "approval_required": True,
        "approval_token": approval_token,
        "remediation_plan": remediation_plan,
        "status": "AWAITING_HUMAN_APPROVAL"
    }

def synthesize_response(state: AgentState) -> Dict[str, Any]:
    """Synthesize final formatted response for the user."""
    intent = state.get("intent")
    tool_calls = state.get("tool_calls", [])
    approval_required = state.get("approval_required", False)

    if approval_required:
        plan = state.get("remediation_plan", {})
        sid = plan.get("server_id", 1001)
        cve_list = ", ".join(plan.get("cves", [])) or "None"
        adv_list = ", ".join(plan.get("advisories", []))
        response = (
            f"### 🛡️ Remediation Proposal Prepared\n\n"
            f"A state-modifying remediation action has been proposed for **Server ID {sid}**:\n"
            f"- **Target Advisories:** `{adv_list}`\n"
            f"- **Associated CVEs:** `{cve_list}`\n"
            f"- **Total Errata Packages:** {plan.get('errata_count', 0)}\n\n"
            f"> ⚠️ **Operator Approval Required:** Please inspect the proposal details in the interactive approval card below and click **Approve** or **Reject** to proceed."
        )
    elif intent == "compliance_scan_query":
        scan = next((tc["result"] for tc in tool_calls if tc["tool"] == "audit_get_xccdf_scan_details"), {})
        sid = scan.get("server_id", 1001)
        score = scan.get("score", 0.0)
        passes = scan.get("pass_count", 0)
        fails = scan.get("fail_count", 0)
        failed_rules = scan.get("failed_rules", [])

        rule_table = "\n".join(
            [f"| `{r['severity'].upper()}` | **{r['title']}** | `{r['rule_identifier']}` |" for r in failed_rules]
        ) or "| INFO | No critical rule failures recorded | N/A |"

        response = (
            f"### 📊 OpenSCAP Compliance Audit Results for Server {sid}\n\n"
            f"- **Benchmark Profile:** `CIS SUSE Linux Enterprise Server 15 Benchmark`\n"
            f"- **Compliance Score:** **{score}%** ({'PASS' if score >= 80 else 'FAIL - ACTION REQUIRED'})\n"
            f"- **Rule Summary:** ✅ **{passes} Passed** | ❌ **{fails} Failed**\n\n"
            f"#### Failed Benchmark Rules:\n"
            f"| Severity | Rule Title | Identifier |\n"
            f"|---|---|---|\n"
            f"{rule_table}\n"
        )
    elif intent == "errata_cve_query":
        advisories = []
        for tc in tool_calls:
            if tc["tool"] in ["errata_find_by_cve", "system_get_relevant_errata"]:
                advisories = tc.get("result", [])

        if advisories:
            rows = "\n".join(
                [f"| `{a.get('cve_id', 'N/A')}` | **{a.get('advisory_name')}** | {a.get('advisory_type')} | {a.get('synopsis')} |" for a in advisories]
            )
            response = (
                f"### 🔍 SUSE Errata & Vulnerability Report\n\n"
                f"Found **{len(advisories)}** relevant security advisories:\n\n"
                f"| CVE ID | Advisory Name | Type | Synopsis |\n"
                f"|---|---|---|---|\n"
                f"{rows}\n"
            )
        else:
            response = "### 🔍 SUSE Errata Report\n\nNo active vulnerabilities or pending errata matched your query."
    elif intent == "inventory_query":
        systems = next((tc["result"] for tc in tool_calls if tc["tool"] == "system_list_systems"), [])
        rows = "\n".join(
            [f"| `{s['id']}` | **{s['name']}** | `{s['ip_address']}` | {s['os_release']} | **{s['compliance_score']}%** | ⚠️ {s['security_errata_count']} Sec |" for s in systems]
        )
        response = (
            f"### 🖥️ Managed Server Fleet Inventory\n\n"
            f"Discovered **{len(systems)}** registered Linux servers in SUSE Multi-Linux Manager:\n\n"
            f"| ID | Hostname | IP Address | OS Release | Compliance | Errata |\n"
            f"|---|---|---|---|---|---|\n"
            f"{rows}\n"
        )
    elif intent == "report_export_query":
        response = (
            f"### 📄 Compliance Report Ready\n\n"
            f"You can export the complete fleet compliance summary in **PDF**, **CSV**, or **JSON** format using the Report Center in the top navigation bar."
        )
    else:
        response = "I have queried SUSE Multi-Linux Manager. Let me know if you would like to run an OpenSCAP audit, review errata, or generate reports."

    return {
        "final_response": response,
        "status": "COMPLETED"
    }
