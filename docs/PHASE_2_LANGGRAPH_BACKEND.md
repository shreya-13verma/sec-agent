# Phase 2 Documentation: LangGraph Agent Engine & FastAPI Core

## 1. Overview & Scope
Phase 2 implemented the application core combining **FastAPI**, **LangGraph** multi-agent stateful workflow, normalized **PostgreSQL / SQLAlchemy** relational schema (0 JSON columns), FastMCP bridge client, and human-in-the-loop remediation gates with single-use cryptographic approval tokens.

## 2. Implemented Components
- **Database Layer (`backend/app/models/`)**: Fully normalized relational schema with 0 JSON/JSONB columns across all models:
  - `ChatSession`, `ChatMessage`
  - `ManagedServer`
  - `OpenSCAPScan`, `OpenSCAPRuleResult`
  - `SystemErrataAdvisory`
  - `RemediationApproval`
  - `ComplianceReport`, `AuditLog`
- **Agent Orchestrator (`backend/app/agent/`)**:
  - `graph.py`: StateGraph with `intent_analyzer`, `tool_executor`, `remediation_planner`, and `synthesizer`.
  - `nodes.py`: Intent classification, FastMCP tool execution, remediation planning with interrupt gate and approval token generation.
  - `mcp_client.py`: Client bridge communicating with FastMCP server.
- **REST & SSE Endpoints (`backend/app/api/v1/endpoints/`)**:
  - `chat.py`: Real-time SSE token, thought, and tool execution streaming (`POST /api/v1/chat/message`).
  - `systems.py`: Managed servers inventory and packages (`GET /api/v1/systems`).
  - `compliance.py`: OpenSCAP scans, errata queries, and scan scheduling.
  - `approvals.py`: Human-in-the-loop review and execution (`POST /api/v1/approvals/{token}/action`).
  - `reports.py`: Asynchronous compliance report generation (PDF, CSV, JSON) and download.

## 3. Loop Engineering & Test Execution Log
- **Iteration 1**: Initial test run surfaced an intent classification boundary and a UUID generation ordering in report creation.
- **Iteration 2 (Diagnosis & Refinement)**:
  - Refined regex and intent matcher priority in `analyze_intent` to prioritize `apply` / `patch` / `remediate` requests into the human-in-the-loop approval branch.
  - Explicitly initialized primary key UUIDs before persisting audit logs.
- **Converged Execution**:
  ```
  backend/tests/test_agent_workflow.py::test_tc_006_read_only_compliance_evaluation PASSED [  8%]
  backend/tests/test_agent_workflow.py::test_tc_007_remediation_intent_triggers_interrupt_token PASSED [ 16%]
  backend/tests/test_api_endpoints.py::test_tc_008_systems_and_compliance_endpoints PASSED [ 25%]
  backend/tests/test_api_endpoints.py::test_tc_009_chat_streaming_and_approval_resolution PASSED [ 33%]
  backend/tests/test_api_endpoints.py::test_tc_010_approval_security_and_invalid_token PASSED [ 41%]
  backend/tests/test_reports_service.py::test_tc_011_and_012_report_generation_and_download PASSED [ 50%]
  backend/tests/test_schema_constraints.py::test_strictly_zero_json_columns PASSED [ 58%]
  mcp_server/tests/test_fastmcp.py::test_tc_001_auth_login_and_logout PASSED [ 66%]
  mcp_server/tests/test_fastmcp.py::test_tc_002_system_list_and_details PASSED [ 75%]
  mcp_server/tests/test_fastmcp.py::test_tc_003_audit_scap_profiles_and_scan PASSED [ 83%]
  mcp_server/tests/test_fastmcp.py::test_tc_004_errata_find_by_cve_and_relevant PASSED [ 91%]
  mcp_server/tests/test_fastmcp.py::test_tc_005_error_handling_and_schedule PASSED [100%]
  12 passed in 1.63s
  ```

## 4. Test Matrix Coverage
| Test ID | Scenario | Result |
|---|---|---|
| TC-006 | LangGraph intent routing & OpenSCAP compliance read query | PASS |
| TC-007 | LangGraph remediation proposal & interrupt approval token generation | PASS |
| TC-008 | FastAPI systems inventory and compliance scan endpoints | PASS |
| TC-009 | FastAPI SSE streaming chat & approval resolution | PASS |
| TC-010 | Approval security & invalid token rejection | PASS |
| TC-011 | Multi-format (PDF, CSV, JSON) report generation | PASS |
| TC-012 | Multi-format report downloads | PASS |
