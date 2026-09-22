# TASK.md

Progress tracker for SUSE MLM Security & Compliance Agent, derived from plan.md Section 23.
Legend: [ ] not started · [x] done

## Phase 1 — FastMCP Server Core & SUSE MLM Integration
- [x] Task: Set up FastMCP project structure and dependencies (`mcp_server/requirements.txt`) (covers FR-001)
- [x] Task: Implement SUSE MLM XML-RPC client wrapper with session auth lifecycle (`mlm_client.py`) (covers FR-001 / TC-001)
- [x] Task: Implement FastMCP `auth.*` tools (`auth_login`, `auth_logout`) (covers FR-001 / TC-001)
- [x] Task: Implement FastMCP `system.*` tools (`list_systems`, `get_details`, `list_installed_packages`) (covers FR-001 / TC-002)
- [x] Task: Implement FastMCP `audit.*` tools (`list_scap_profiles`, `schedule_xccdf_scan`, `get_xccdf_scan_details`) (covers FR-001 / TC-003)
- [x] Task: Implement FastMCP `errata.*` tools (`find_by_cve`, `get_relevant_errata`) (covers FR-001 / TC-004)
- [x] Task: Implement FastMCP `schedule.*` tools (`schedule_apply_errata`, `get_action_status`) (covers FR-001)
- [x] Task: Create mock SUSE MLM XML-RPC test server for comprehensive offline verification (covers TC-001-TC-005)
- [x] Task: Write and pass FastMCP unit and integration test suite (covers TC-001-TC-005)

## Phase 2 — LangGraph Agent Engine & FastAPI Core
- [x] Task: Configure FastAPI project structure and dependencies (`backend/requirements.txt`) (covers FR-002)
- [x] Task: Define normalized PostgreSQL database models with 0 JSON columns (`models/`) (covers FR-007)
- [x] Task: Implement database connection manager, migrations, and session lifecycle (`database.py`) (covers FR-007)
- [x] Task: Implement FastMCP client bridge for LangGraph tool execution (`mcp_client.py`) (covers FR-001, FR-003)
- [x] Task: Implement LangGraph state machine with checkpointer, tool router, and interrupt node (`agent/graph.py`, `nodes.py`) (covers FR-003 / TC-006, TC-007)
- [x] Task: Implement human-in-the-loop approval token manager and verification service (`approvals.py`) (covers FR-004 / TC-009, TC-010)
- [x] Task: Implement FastAPI SSE streaming chat endpoint with live reasoning traces (`api/v1/endpoints/chat.py`) (covers FR-002 / TC-008)
- [x] Task: Implement REST endpoints for system inventory, compliance results, and approval actions (`api/v1/endpoints/`) (covers FR-002)
- [x] Task: Write and pass backend unit, API, and security tests (covers TC-006-TC-010)

## Phase 3 — React Conversational UI & Dashboard
- [x] Task: Scaffold React + Vite + Tailwind CSS frontend application (`frontend/`) (covers FR-005)
- [x] Task: Implement responsive layout with Header, Sidebar, and Navigation guards (`components/common/`) (covers FR-005 / TC-013)
- [x] Task: Implement Chat container with SSE streaming message parser (`components/chat/ChatContainer.jsx`) (covers FR-005 / TC-014)
- [x] Task: Implement Thought Trace accordion visualizer for agent tool execution steps (covers FR-005 / TC-014)
- [x] Task: Implement Interactive Remediation Approval Cards in chat (`components/chat/ApprovalCard.jsx`) (covers FR-004, FR-005 / TC-015)
- [x] Task: Implement Compliance Overview Dashboard and Server Inventory table (`components/dashboard/`) (covers FR-005)
- [x] Task: Implement Errata breakdown and OpenSCAP rule result detail views (covers FR-005)
- [x] Task: Set up Playwright E2E testing framework configuration (`playwright.config.js`) (covers TC-013-TC-016)

## Phase 4 — Server Reporting Engine, E2E Verification & Production Docs
- [x] Task: Implement asynchronous multi-format report generator service (PDF, CSV, JSON, Web) (`services/report_service.py`) (covers FR-006 / TC-011)
- [x] Task: Implement frontend Report Manager and export/download modals (`components/reports/`) (covers FR-006 / TC-016)
- [x] Task: Implement audit logging service recording all operator approvals and system remediations (`models/audit.py`, `services/audit_service.py`) (covers FR-007)
- [x] Task: Execute full automated Playwright E2E browser test suite covering all user journeys (covers TC-013-TC-016)
- [x] Task: Author root `README.md` with architecture diagram, port inventory, and run commands (covers Step 6)
- [x] Task: Author comprehensive `docs/APPLICATION_DOCUMENTATION.md` technical and API spec (covers Step 6)
- [x] Task: Generate phase documentation logs (`docs/PHASE_1_MCP_SERVER.md`, `docs/PHASE_2_LANGGRAPH_BACKEND.md`, `docs/PHASE_3_REACT_FRONTEND.md`, `docs/PHASE_4_REPORTING_VERIFICATION.md`) (covers Step 6)
