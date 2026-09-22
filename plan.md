# PLAN.md

## 1. Overview
- **Project / Feature Name:** SUSE MLM Security & Compliance Agent
- **Problem Statement:** Infrastructure and security teams managing Linux fleets via SUSE Multi-Linux Manager (MLM) / Uyuni lack an autonomous, conversational interface to audit OpenSCAP compliance, analyze security errata/CVE vulnerabilities, generate compliance reports, and safely orchestrate remediations with human-in-the-loop safeguards.
- **Goal:** Deliver an enterprise-grade, decoupled application combining a React frontend, FastAPI backend, LangGraph stateful agent orchestrator, FastMCP integration server wrapping SUSE MLM XML-RPC APIs, and a PostgreSQL persistence store.
- **Non-Goals:** 
  - Direct connection from frontend or backend to SUSE MLM XML-RPC endpoints bypassing the FastMCP layer.
  - Inventing non-native synthetic compliance benchmarks outside of SUSE MLM OpenSCAP profiles and vendor errata channels.
  - Unattended autonomous execution of destructive or state-modifying actions without explicit human-in-the-loop approval tokens.
- **Success Criteria:**
  - 100% of MLM API interactions routed through the dedicated FastMCP server.
  - Real-time streaming chat with step-by-step agent reasoning and tool invocation visibility.
  - Complete compliance reporting in Web view, PDF, CSV, and JSON formats.
  - Interactive approval cards for state-altering remediation actions with fail-closed audit tracking.
  - Comprehensive automated test coverage across Backend (Unit, Integration, API, Security) and Frontend (Playwright E2E).

---

## 2. Requirements

### Functional Requirements
- **FR-001 (FastMCP Server Core):** Implement FastMCP server wrapping SUSE MLM XML-RPC endpoints for authentication (`auth.login`, `auth.logout`), system inventory (`system.listSystems`, `system.getDetails`, `system.listPackages`), OpenSCAP audits (`audit.listScapProfiles`, `audit.scheduleXccdfScan`, `audit.getScanStatus`, `audit.getXccdfScanDetails`), errata management (`errata.findByCve`, `system.getRelevantErrata`, `errata.getDetails`), and remediation scheduling (`system.scheduleApplyErrata`, `schedule.listCompletedActions`).
- **FR-002 (FastAPI Core & Streaming):** Expose REST and WebSocket/SSE endpoints for session management, conversation history, asynchronous report export (PDF, CSV, JSON), server inventory querying, and human-in-the-loop approval handling.
- **FR-003 (LangGraph Autonomous Agent Workflow):** Construct stateful multi-agent LangGraph workflow featuring intent analysis, automated MCP tool discovery, read-only compliance evaluation, and an interruptible human-in-the-loop state machine for remediation proposals.
- **FR-004 (Human-in-the-Loop Remediation Approval):** Generate cryptographic single-use approval tokens for remediation plans; enforce fail-closed gate where state-altering MCP tools cannot execute until token approval is received.
- **FR-005 (React Conversational & Compliance UI):** Provide a responsive dashboard with real-time streaming chat, collapsible agent thought/tool-call traces, interactive approval cards, inventory filters, and report viewer/downloader.
- **FR-006 (Server Compliance & Vulnerability Reporting):** Asynchronous report generation engine producing PDF (via ReportLab/Weasyprint), CSV, JSON, and Web view summarizing OpenSCAP pass/fail statistics, errata classifications (Security, Bugfix, Enhancement), CVE mappings, and operator audit trail.
- **FR-007 (Audit & State Persistence):** Persist all scan records, agent chat sessions, reasoning traces, operator decisions, and remediation actions in normalized PostgreSQL relational tables.

### User Stories & Complete Lifecycle Scenarios
- **US-001 (Compliance Audit Exploration):** As a Security Engineer, I want to query server compliance posture in natural language so that I can identify non-compliant systems across our fleet.
  - *Scenario A (Happy Path):* Given an authenticated engineer asking "Which production servers failed CIS benchmark audits?", when the agent queries FastMCP audit tools, then the agent streams its reasoning, identifies non-compliant hosts, and presents detailed rule failure counts in chat and dashboard.
  - *Scenario B (Negative/Edge Path):* Given a query for a non-existent or unmanaged host, when the agent invokes FastMCP system tools, then it returns a clear explanatory message with suggestions of existing registered hosts.
- **US-002 (Vulnerability & Errata Assessment):** As a SecOps Analyst, I want to search for specific CVEs affecting our servers so that I can prioritize patching.
  - *Scenario A (Happy Path):* Given an analyst asking "Summarize pending security errata and CVE-2024-XXXX on web servers", when the agent invokes FastMCP errata tools, then the agent tabulates relevant advisories, severity levels, and affected package versions.
  - *Scenario B (Edge Path):* Given a CVE with no matching errata in MLM channels, when queried, then the agent reports zero matching advisories without hallucinating vulnerabilities.
- **US-003 (Remediation Plan & Safe Operator Approval):** As a DevOps Lead, I want to review proposed errata remediation actions before execution so that production stability is protected.
  - *Scenario A (Happy Path):* Given an agent remediation proposal to apply errata to server ID 101, when an interactive approval card renders, then upon the operator clicking "Approve", the agent resumes from the LangGraph interrupt state, executes `system.scheduleApplyErrata`, and records the action ID and approval audit trail.
  - *Scenario B (Rejection/Negative Path):* Given a proposed remediation, when the operator clicks "Reject", then the agent aborts execution, leaves the system state untouched, and logs the operator rejection in the audit trail.
- **US-004 (Compliance Report Lifecycle):** As a Compliance Officer, I want to generate and download comprehensive audit reports so that I can submit regulatory compliance evidence.
  - *Scenario A (Happy Path):* Given a request to generate a compliance report for System Group "DB-Cluster", when the report engine runs, then it compiles OpenSCAP results, CVE counts, and audit logs into downloadable PDF, CSV, and JSON files and stores metadata in PostgreSQL.
  - *Scenario B (Download & Inspection):* Given a completed report, when the officer accesses the report URL or web viewer, then the data is rendered accurately and file downloads complete without corruption.

### Non-Functional Requirements
- **Performance:** Chat first-token streaming latency < 800ms; MCP tool execution dispatch < 500ms; Report generation < 3.0s for standard 100-node fleets.
- **Scalability:** Handles 50+ concurrent operator sessions and 10,000+ managed server inventory records.
- **Availability:** Service uptime target 99.9%; resilient reconnection to FastMCP server on transient drops.
- **Reliability:** All LangGraph state check-pointed to PostgreSQL; uninterrupted resumption from human approval interrupts.
- **Security:** Strict separation of privileges; no credential exposure in logs or UI; fail-closed approval tokens; parameterized SQL queries.
- **Observability:** Structured JSON logging, Prometheus metrics endpoints (`/metrics`), OpenTelemetry tracing support, and health checks (`/health/live`, `/health/ready`).
- **Maintainability:** Fully typed Python codebases (FastAPI, FastMCP, LangGraph) with Pydantic v2 schemas and modular React component architecture.

---

## 3. Scope

### In Scope
- FastMCP Server with tools for SUSE MLM XML-RPC (`auth`, `system`, `audit`, `errata`, `schedule`).
- LangGraph agent workflow with checkpointing, tool routing, memory, and interrupt-based human-in-the-loop approvals.
- FastAPI backend serving chat WebSocket/SSE, REST APIs for inventory, scans, approvals, and report generation.
- React frontend with chat stream, reasoning visualizer, remediation approval cards, compliance dashboards, and report downloaders.
- PostgreSQL normalized database schema for sessions, messages, tool executions, scan summaries, errata items, reports, and audit logs.
- PDF, CSV, JSON, and Web view report generation engines.
- Automated Backend test suite (Unit, Integration, API, Security) and Frontend Playwright E2E test suite.

### Out of Scope
- Direct modification of SUSE MLM server-side database tables (must only interact via official XML-RPC API).
- Direct SSH execution on target client hosts (all actions dispatched via MLM agent daemon).

---

## 4. User / System Flows
- **Flow 1: Natural Language Compliance Inquiry:** User queries chat -> FastAPI streams to LangGraph -> Agent routes to FastMCP `audit.*` / `system.*` tools -> FastMCP queries MLM XML-RPC -> Results returned to Agent -> Agent formats markdown response with structured tables -> Streamed to React UI.
- **Flow 2: Remediation Proposal & Approval Lifecycle:** User requests patch -> Agent creates remediation proposal & LangGraph enters `interrupt()` -> FastAPI generates approval token & sends interactive card to UI -> User inspects affected packages & clicks Approve -> FastAPI validates token -> LangGraph resumes -> FastMCP `system.scheduleApplyErrata` called -> Action ID stored in PostgreSQL -> Confirmation streamed to UI.
- **Flow 3: Report Generation & Download:** User triggers export -> Backend queues generation task -> Aggregates scan stats, errata list, and audit logs -> Generates PDF/CSV/JSON -> Persists artifact -> Frontend displays completed download link.
- **Flow 4: Error & Disconnect Recovery:** FastMCP or MLM unreachable -> FastMCP emits structured error -> Agent informs user gracefully without crashing -> Logs incident in PostgreSQL audit log.

---

## 5. Architecture

### Components
1. **Frontend (React + Vite):** SPA providing Conversational Chat UI, Live Stream Tracing, Interactive Approval Cards, Compliance Posture Dashboards, and Report Manager.
2. **Backend Application (FastAPI):** Application core providing REST API, SSE/WebSocket streaming, LangGraph runtime host, report generators, and security gatekeeper.
3. **Agent Graph (LangGraph):** Stateful workflow with intent parser, tool discovery node, execution node, interrupt gate for remediation, and output synthesis node.
4. **Integration Layer (FastMCP Server):** Python FastMCP server communicating with SUSE MLM XML-RPC API (`/rpc/api`) over HTTP/HTTPS with session cookie lifecycle.
5. **Database (PostgreSQL):** Normalized relational persistence for chat sessions, agent checkpoints, server cache, scan histories, audit events, and generated reports.

### Architecture Diagram
```
+------------------------------------------------------------------------------------+
|                                React Frontend (Vite)                              |
|  [Chat Stream & Traces]  [Approval Cards]  [Compliance Dashboard]  [Report Center] |
+------------------------------------------+-----------------------------------------+
                                           | HTTP / SSE / WebSocket
                                           v
+------------------------------------------------------------------------------------+
|                                FastAPI Application                                |
|   /api/v1/chat       /api/v1/systems       /api/v1/reports       /api/v1/approvals |
+---------------------+--------------------+--------------------+--------------------+
                      |                    |                    |
                      v                    v                    v
          +----------------------+ +---------------+ +-----------------------+
          |   LangGraph Agent    | | PostgreSQL DB | | Report Engine         |
          |  Stateful Workflows  | | Normalized    | | (PDF, CSV, JSON, Web) |
          |  Human-in-the-Loop   | | Entities      | +-----------------------+
          +-----------+----------+ +---------------+
                      |
                      v MCP Protocol (Stdio / SSE)
+------------------------------------------------------------------------------------+
|                         SUSE MLM FastMCP Server                                    |
|   auth.*    |    system.*    |    audit.*    |    errata.*    |    schedule.*     |
+------------------------------------------+-----------------------------------------+
                                           | XML-RPC (/rpc/api)
                                           v
+------------------------------------------------------------------------------------+
|                   SUSE Multi-Linux Manager (MLM) / Uyuni Server                    |
+------------------------------------------------------------------------------------+
```

### Project Directory Structure
```
/home/shreya/sec-agent/
├── backend/                              (new)
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── auth.py           (new)
│   │   │   │   │   ├── chat.py           (new)
│   │   │   │   │   ├── systems.py        (new)
│   │   │   │   │   ├── compliance.py     (new)
│   │   │   │   │   ├── reports.py        (new)
│   │   │   │   │   └── approvals.py      (new)
│   │   │   │   └── router.py             (new)
│   │   ├── core/
│   │   │   ├── config.py                 (new)
│   │   │   ├── database.py               (new)
│   │   │   ├── security.py               (new)
│   │   │   └── logging.py                (new)
│   │   ├── models/
│   │   │   ├── chat.py                   (new)
│   │   │   ├── system.py                 (new)
│   │   │   ├── compliance.py             (new)
│   │   │   ├── report.py                 (new)
│   │   │   └── audit.py                  (new)
│   │   ├── schemas/
│   │   │   ├── chat.py                   (new)
│   │   │   ├── system.py                 (new)
│   │   │   ├── compliance.py             (new)
│   │   │   ├── report.py                 (new)
│   │   │   └── approval.py               (new)
│   │   ├── agent/
│   │   │   ├── graph.py                  (new)
│   │   │   ├── state.py                  (new)
│   │   │   ├── nodes.py                  (new)
│   │   │   └── mcp_client.py             (new)
│   │   ├── services/
│   │   │   ├── report_service.py         (new)
│   │   │   ├── system_service.py         (new)
│   │   │   └── audit_service.py          (new)
│   │   └── main.py                       (new)
│   ├── tests/
│   │   ├── conftest.py                   (new)
│   │   ├── unit/                         (new)
│   │   ├── integration/                  (new)
│   │   └── api/                          (new)
│   └── requirements.txt                  (new)
├── mcp_server/                           (new)
│   ├── server.py                         (new)
│   ├── mlm_client.py                     (new)
│   ├── tools/
│   │   ├── auth_tools.py                 (new)
│   │   ├── system_tools.py               (new)
│   │   ├── audit_tools.py                (new)
│   │   ├── errata_tools.py               (new)
│   │   └── schedule_tools.py             (new)
│   ├── tests/                            (new)
│   └── requirements.txt                  (new)
├── frontend/                             (new)
│   ├── src/
│   │   ├── components/
│   │   │   ├── chat/                     (new)
│   │   │   │   ├── ChatContainer.jsx     (new)
│   │   │   │   ├── MessageList.jsx       (new)
│   │   │   │   ├── MessageItem.jsx       (new)
│   │   │   │   ├── ApprovalCard.jsx      (new)
│   │   │   │   └── ThoughtTrace.jsx      (new)
│   │   │   ├── dashboard/                (new)
│   │   │   │   ├── ComplianceOverview.jsx(new)
│   │   │   │   ├── SystemList.jsx        (new)
│   │   │   │   └── ErrataSummary.jsx     (new)
│   │   │   ├── reports/                  (new)
│   │   │   │   ├── ReportViewer.jsx      (new)
│   │   │   │   └── ExportModal.jsx       (new)
│   │   │   └── common/
│   │   │       ├── Header.jsx            (new)
│   │   │       ├── Sidebar.jsx           (new)
│   │   │       └── ErrorBanner.jsx       (new)
│   │   ├── services/
│   │   │   ├── api.js                    (new)
│   │   │   └── chatStream.js             (new)
│   │   ├── App.jsx                       (new)
│   │   ├── main.jsx                      (new)
│   │   └── index.css                     (new)
│   ├── tests/
│   │   └── e2e/
│   │       ├── chat_flows.spec.js        (new)
│   │       ├── compliance_audit.spec.js  (new)
│   │       └── report_export.spec.js     (new)
│   ├── package.json                      (new)
│   ├── vite.config.js                    (new)
│   └── playwright.config.js              (new)
├── docs/                                 (new)
│   ├── APPLICATION_DOCUMENTATION.md      (new)
│   ├── PHASE_1_MCP_SERVER.md             (new)
│   ├── PHASE_2_LANGGRAPH_BACKEND.md      (new)
│   ├── PHASE_3_REACT_FRONTEND.md         (new)
│   └── PHASE_4_REPORTING_VERIFICATION.md (new)
├── prd.md
├── HERMES-MANUAL.md
├── plan.md                               (new)
├── task.md                               (new)
├── docker-compose.yml                    (new)
└── README.md                             (new)
```

### Frontend Plan
- **Pages / Screens / Routes:**
  - `/` -> Main Dashboard & Conversational Compliance Chat interface.
  - `/systems` -> Server Fleet Inventory & OpenSCAP/Errata detail inspection.
  - `/reports` -> Compliance Report Generator, Viewer, and Export Center.
  - `/audit-logs` -> Operator Remediation Approvals & System Audit Trails.
- **Component Hierarchy:**
  - `App` -> `Layout` (`Header`, `Sidebar`, `MainContent`)
  - `MainContent` -> `ChatContainer` (`MessageList` -> `MessageItem` -> `ThoughtTrace`, `ApprovalCard`, `PromptInput`), `ComplianceDashboard`, `ReportViewer`.
- **State Management:** React Context + Hooks (`ChatContext`, `SystemContext`, `AuthContext`) for lightweight predictable state.
- **Client-Server Data Flow:** SSE (Server-Sent Events) / Streaming HTTP for real-time chat tokens, thoughts, and tool traces; REST endpoints for tabular fleet data, approval actions, and report downloads.
- **Styling:** Tailwind CSS with high-contrast, accessible enterprise dark/light themes.
- **Client-Side Routing:** React Router v6 with route navigation guards.
- **Accessibility:** WCAG 2.1 AA compliant, full keyboard operability, ARIA labels on dynamic chat stream and modal elements.
- **Tooling:** Vite, React 18, Playwright for E2E testing.

---

## 6. Technology Decisions
- **Language:** Python 3.11+ (Backend, MCP, Agent) for native async support, typing, and ecosystem compatibility; JavaScript/JSX (ES2022) for React frontend.
- **Agent Framework:** LangGraph for explicit state graphs, deterministic tool cycles, and first-class `interrupt()` human-in-the-loop support.
- **MCP Framework:** FastMCP for clean, typed, high-performance tool exposure adhering to Model Context Protocol standards.
- **Backend Web Framework:** FastAPI for asynchronous endpoints, Pydantic v2 data validation, OpenAPI autodoc, and SSE streaming.
- **Frontend Framework:** React 18 + Vite for fast HMR, component composition, and responsive client-side rendering.
- **Database / ORM:** PostgreSQL with SQLAlchemy 2.0 (asyncio) for normalized ACID persistence.
- **Reporting:** ReportLab / WeasyPrint (PDF generation), Python standard `csv` and `json` modules.
- **Testing:** Pytest, pytest-asyncio, pytest-mock, Playwright test suite for automated E2E browser verification.

---

## 7. API / Interface Contract

### FastMCP Tools Exposed:
1. `auth_login(username, password) -> session_token`
2. `auth_logout(session_token) -> status`
3. `system_list_systems(session_token) -> list[SystemSummary]`
4. `system_get_details(session_token, server_id) -> SystemDetails`
5. `system_list_installed_packages(session_token, server_id) -> list[PackageInfo]`
6. `audit_list_scap_profiles(session_token) -> list[ScapProfile]`
7. `audit_schedule_xccdf_scan(session_token, server_id, profile_name, path) -> action_id`
8. `audit_get_xccdf_scan_details(session_token, xccdf_test_result_id) -> ScanDetails`
9. `errata_find_by_cve(session_token, cve_id) -> list[ErrataAdvisory]`
10. `system_get_relevant_errata(session_token, server_id) -> list[ErrataAdvisory]`
11. `system_schedule_apply_errata(session_token, server_id, errata_ids) -> action_id`
12. `schedule_get_action_status(session_token, action_id) -> ActionStatus`

### Backend REST & Streaming Endpoints:
- `POST /api/v1/chat/message` -> Request: `{"session_id": str, "message": str}` -> Response: SSE stream with events `token`, `thought`, `tool_call`, `approval_required`, `final_message`.
- `GET /api/v1/chat/sessions` -> List chat sessions.
- `GET /api/v1/chat/sessions/{session_id}/messages` -> Fetch message history.
- `POST /api/v1/approvals/{token}/action` -> Request: `{"approved": bool, "operator": str, "comment": str}` -> Resumes LangGraph execution.
- `GET /api/v1/systems` -> Filterable server inventory list.
- `GET /api/v1/systems/{server_id}/compliance` -> Detailed OpenSCAP results & relevant errata.
- `POST /api/v1/reports/generate` -> Request: `{"scope": "all"|"system"|"group", "target_id": str, "formats": ["pdf", "csv", "json"]}` -> Returns `report_id`.
- `GET /api/v1/reports/{report_id}/download/{format}` -> Serves binary file download.
- `GET /api/v1/audit/logs` -> Paginated operator approval & action audit trail.

---

## 8. Data Model

**Strict JSON/JSONB Constraint:** All entities use normalized, strictly typed relational columns. No unstructured JSON/JSONB fields are used.

### Relational Entities
1. **`chat_sessions`:**
   - `id`: UUID (PK)
   - `title`: VARCHAR(255)
   - `created_at`: TIMESTAMP WITH TIME ZONE
   - `updated_at`: TIMESTAMP WITH TIME ZONE
2. **`chat_messages`:**
   - `id`: UUID (PK)
   - `session_id`: UUID (FK -> chat_sessions.id)
   - `sender`: VARCHAR(50) (user | agent | system)
   - `content`: TEXT
   - `thought_log`: TEXT
   - `created_at`: TIMESTAMP WITH TIME ZONE
3. **`managed_servers`:**
   - `id`: BIGINT (PK, MLM server ID)
   - `hostname`: VARCHAR(255)
   - `ip_address`: VARCHAR(45)
   - `os_release`: VARCHAR(100)
   - `kernel_version`: VARCHAR(100)
   - `last_checkin`: TIMESTAMP WITH TIME ZONE
   - `compliance_score`: DECIMAL(5, 2)
   - `security_errata_count`: INTEGER
   - `bugfix_errata_count`: INTEGER
   - `updated_at`: TIMESTAMP WITH TIME ZONE
4. **`openscap_scans`:**
   - `id`: UUID (PK)
   - `mlm_test_result_id`: BIGINT (Unique)
   - `server_id`: BIGINT (FK -> managed_servers.id)
   - `profile_name`: VARCHAR(255)
   - `scan_timestamp`: TIMESTAMP WITH TIME ZONE
   - `pass_count`: INTEGER
   - `fail_count`: INTEGER
   - `error_count`: INTEGER
   - `other_count`: INTEGER
   - `score`: DECIMAL(5, 2)
5. **`openscap_rule_results`:**
   - `id`: UUID (PK)
   - `scan_id`: UUID (FK -> openscap_scans.id)
   - `rule_identifier`: VARCHAR(255)
   - `rule_title`: VARCHAR(500)
   - `result`: VARCHAR(50) (pass | fail | error | notapplicable)
   - `severity`: VARCHAR(50) (low | medium | high | critical)
6. **`system_errata_advisories`:**
   - `id`: UUID (PK)
   - `server_id`: BIGINT (FK -> managed_servers.id)
   - `advisory_name`: VARCHAR(100)
   - `advisory_type`: VARCHAR(50) (Security Advisory | Bug Fix Advisory | Enhancement)
   - `cve_id`: VARCHAR(100)
   - `synopsis`: TEXT
   - `issue_date`: TIMESTAMP WITH TIME ZONE
   - `remediation_status`: VARCHAR(50) (pending | scheduled | applied | ignored)
7. **`remediation_approvals`:**
   - `id`: UUID (PK)
   - `approval_token`: VARCHAR(128) (Unique, indexed)
   - `session_id`: UUID (FK -> chat_sessions.id)
   - `server_id`: BIGINT (FK -> managed_servers.id)
   - `action_type`: VARCHAR(100)
   - `proposed_errata_ids`: TEXT (Comma-delimited string)
   - `status`: VARCHAR(50) (pending | approved | rejected | expired)
   - `operator`: VARCHAR(100)
   - `operator_comment`: TEXT
   - `mlm_action_id`: BIGINT (Nullable)
   - `created_at`: TIMESTAMP WITH TIME ZONE
   - `resolved_at`: TIMESTAMP WITH TIME ZONE (Nullable)
8. **`compliance_reports`:**
   - `id`: UUID (PK)
   - `title`: VARCHAR(255)
   - `report_scope`: VARCHAR(50)
   - `target_id`: VARCHAR(100)
   - `pdf_path`: VARCHAR(500)
   - `csv_path`: VARCHAR(500)
   - `json_path`: VARCHAR(500)
   - `generated_by`: VARCHAR(100)
   - `created_at`: TIMESTAMP WITH TIME ZONE
9. **`audit_logs`:**
   - `id`: UUID (PK)
   - `event_type`: VARCHAR(100)
   - `operator`: VARCHAR(100)
   - `resource_type`: VARCHAR(100)
   - `resource_id`: VARCHAR(100)
   - `action_details`: TEXT
   - `ip_address`: VARCHAR(45)
   - `timestamp`: TIMESTAMP WITH TIME ZONE

---

## 9. Security
- **Authentication & Secrets:** SUSE MLM credentials and session tokens managed via environment variables and secure in-memory FastMCP session manager.
- **Fail-Closed Approvals:** State-altering operations (errata deployment, scan scheduling) fail-closed; requiring signed, unexpired cryptographic approval tokens.
- **Input Validation:** Strict Pydantic v2 schemas and validation for all API routes and MCP tool inputs.
- **SQL Injection Prevention:** 100% parameterized queries via SQLAlchemy ORM.
- **Audit Logging:** Every user action, agent tool invocation, approval decision, and remediation execution permanently saved to PostgreSQL `audit_logs`.

---

## 10. Scalability
- Asynchronous FastAPI ASGI architecture with multi-worker support (Uvicorn).
- Dedicated FastMCP process decoupling SUSE MLM XML-RPC serialization overhead from web server request loop.
- PostgreSQL connection pooling via `asyncpg`.
- Lightweight streaming via SSE reducing WebSocket handshake memory overhead.

---

## 11. Performance
- **Streaming First-Token Latency:** < 800ms.
- **MCP Tool Invocation Roundtrip:** < 500ms (mock/cached), < 1500ms (live XML-RPC).
- **Report Generation Time:** < 2s (JSON/CSV), < 4s (PDF).
- **Database Query Latency:** Indexed lookup < 10ms for inventory and compliance tables.

---

## 12. Error Handling & Resilience
- Graceful XML-RPC fault handling with domain-mapped error codes.
- FastMCP automatic retry with exponential backoff on transient network faults.
- Agent circuit breaker when external tools fail repeatedly, providing concise explanations to users.
- Database transactions rolled back cleanly on unexpected server errors.

---

## 13. Observability
- Structured JSON logs with correlation IDs linking Chat Message -> Agent Node -> MCP Tool -> Audit Log.
- Prometheus health metrics (`/metrics`) tracking tool latencies, agent token consumption, and error rates.
- Health probe endpoints (`/health/live` and `/health/ready`).

---

## 14. Testing Strategy (Backend, Frontend, Contract, User Stories)

### Backend
- **Unit Tests:** FastMCP tool handlers, XML-RPC client response parsers, LangGraph node transition logic, report generator formatters, token approval verifiers.
- **Integration Tests:** PostgreSQL model migrations, CRUD lifecycles, LangGraph checkpoint state recovery.
- **API Tests:** FastAPI REST endpoints, SSE stream event integrity, approval submission routes, report download streaming.
- **Security Tests:** Token forgery rejection, SQL injection attempts, unauthorized remediation triggers.

### Frontend
- **Unit & Component Tests:** Chat message rendering, thought trace accordion toggling, interactive approval card actions, compliance data tables.
- **Playwright End-to-End Tests:**
  - Automated natural language query flow and streaming response assertion.
  - Interactive approval card interaction (Approve and Reject paths).
  - Server compliance inspection and report generation & file download verification.
  - Absence of console errors and clean network requests.

---

## 15. Test Cases & User Story Verification Matrix

| ID | Scenario | Expected Result | Type | Layer |
|----|----------|-----------------|------|-------|
| TC-001 | FastMCP `auth.login` with valid credentials | Returns valid session token string | Unit | FastMCP |
| TC-002 | FastMCP `system.listSystems` invocation | Returns list of registered server summaries | Unit/API | FastMCP |
| TC-003 | FastMCP `audit.listScapProfiles` invocation | Returns standard OpenSCAP profiles (CIS, DISA) | Unit | FastMCP |
| TC-004 | FastMCP `errata.findByCve` lookup | Returns matching errata advisory objects | Unit | FastMCP |
| TC-005 | FastMCP XML-RPC error response | FastMCP catches fault and returns formatted error object | Unit | FastMCP |
| TC-006 | LangGraph Agent processes natural language inquiry | Invokes appropriate FastMCP read tool and answers query | Integration | Backend |
| TC-007 | LangGraph Agent detects remediation intent | Halts at `interrupt` state and emits approval token | Integration | Backend |
| TC-008 | FastAPI Chat endpoint streams SSE events | Stream outputs `token`, `thought`, and `final_message` | API | Backend |
| TC-009 | POST `/api/v1/approvals/{token}/action` with valid approval | Resumes LangGraph and executes remediation tool | API/Security | Backend |
| TC-010 | POST `/api/v1/approvals/{token}/action` with invalid/expired token | Returns 400/403 and executes zero MCP write actions | Security | Backend |
| TC-011 | Generate PDF, CSV, and JSON compliance report | Valid artifacts created on disk and metadata saved in DB | Integration | Backend |
| TC-012 | Download generated report via API | HTTP 200 with correct Content-Type and valid payload | API | Backend |
| TC-013 | Frontend renders initial Chat & Dashboard UI | Header, Sidebar, Chat Box, and System widgets visible | E2E | Frontend |
| TC-014 | User sends query "Check compliance for server 101" | Streaming tokens display, thought trace expands, data table renders | E2E | Frontend |
| TC-015 | Operator approves remediation in UI | Approval card updates state to Approved, action ID shown | E2E | Frontend |
| TC-016 | Operator exports compliance report from UI | Export modal completes and download link triggers download | E2E | Frontend |

---

## 16. Edge Cases
- **SUSE MLM XML-RPC Endpoint Downtime:** FastMCP returns informative downtime payload; Agent explains to user without throwing uncaught 500.
- **Expired Approval Token:** Attempted execution after timeout fails safely with clear expiration message.
- **Server with 0 OpenSCAP Scans:** Dashboard and report show "No Scans Recorded" empty-state UI rather than crashing.
- **High Concurrency Streaming Requests:** SSE connections handled without memory leaks or worker starvation.
- **Large Errata Lists:** Errata tables paginated in UI and truncated with summary totals in chat response.

---

## 17. Deployment
- **Containerization:** Multi-service `docker-compose.yml` defining `postgres`, `mcp-server`, `backend`, and `frontend`.
- **Configuration:** Environment variables in `.env` (`DATABASE_URL`, `MLM_URL`, `MLM_USER`, `MLM_PASSWORD`, `FASTAPI_PORT`, `MCP_PORT`).
- **Health Checks:** Automated container health checks pinging `/health/ready` endpoints.

---

## 18. CI/CD
- **Lint & Format:** `flake8`, `black`, `eslint` checks.
- **Type Checking:** `mypy --strict` for backend/MCP, `tsc` / ESLint for frontend.
- **Automated Test Suite:** Pytest backend tests and Playwright frontend tests executed sequentially.

---

## 19. Compatibility
- **OS:** Linux (SUSE Enterprise Linux 15, openSUSE Leap, Ubuntu, Debian, RHEL/Rocky).
- **SUSE MLM / Uyuni Versions:** Uyuni 2024.x, SUSE Multi-Linux Manager 4.3+.
- **Browsers:** Chrome 110+, Firefox 110+, Safari 16+, Edge 110+.
- **PostgreSQL:** PostgreSQL 14, 15, 16.

---

## 20. Migration / Upgrade Plan
- Initial schema setup managed via SQLAlchemy models & Alembic migration scripts.
- Backward compatibility guaranteed across XML-RPC API minor versions.

---

## 21. Risks & Trade-offs
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| MLM XML-RPC latency on large queries | High | Medium | Cache inventory snapshots in PostgreSQL with TTL; use targeted API filters. |
| Operator executes incorrect patch | High | Low | Enforce explicit Human-in-the-Loop review cards with exact package list before execution. |
| FastMCP process disconnect | Medium | Low | Auto-restarting daemon and client retry wrappers with exponential backoff. |

---

## 22. Open Questions
- None. Requirements and architecture fully mapped from `prd.md`.

---

## 23. Implementation Plan

### Phase 1: FastMCP Server Core & SUSE MLM Integration
- Initialize FastMCP server and XML-RPC client wrapper.
- Implement tools for authentication, systems inventory, OpenSCAP audits, errata management, and remediation scheduling.
- Unit and integration tests for FastMCP tools with mock MLM XML-RPC server.

### Phase 2: LangGraph Agent Engine & FastAPI Core
- Setup PostgreSQL models, schemas, and async database engine (normalized schema with 0 JSON columns).
- Build LangGraph multi-agent workflow with FastMCP tool integration, checkpointer, and interrupt approval state.
- Implement FastAPI REST and SSE streaming endpoints for chat, systems, compliance, and token approvals.
- Unit and API integration tests for agent routing and human-in-the-loop approvals.

### Phase 3: React Conversational UI & Dashboard
- Scaffold React frontend with Vite and Tailwind CSS.
- Implement Chat Container, SSE token streaming parser, Thought Trace accordion, and interactive Approval Cards.
- Implement Compliance Dashboard, Server Inventory table, and Errata Summary views.
- E2E browser test foundation using Playwright.

### Phase 4: Server Reporting Engine, E2E Verification & Production Docs
- Implement multi-format report generator (PDF, CSV, JSON, Web view).
- Complete comprehensive Playwright end-to-end user story walkthroughs.
- Generate root `README.md`, `docs/APPLICATION_DOCUMENTATION.md`, and all phase documentation (`docs/PHASE_*.md`).

---

## 24. Definition of Done
- [ ] Requirements FR-001 through FR-007 fully implemented.
- [ ] All Unit, Integration, API, and E2E tests passing.
- [ ] 0 JSON/JSONB columns in database schema.
- [ ] Human-in-the-loop approval workflow verified fail-closed.
- [ ] Automated Playwright browser tests passing with zero console errors.
- [ ] Root `README.md` and `docs/APPLICATION_DOCUMENTATION.md` completed.
- [ ] Phase documentation created in `docs/PHASE_*.md`.

---

## 25. Post-Implementation Verification
- Smoke test all API endpoints and health check probes (`/health/live`, `/health/ready`).
- Verify SSE chat streaming and thought traces in live browser.
- Verify remediation approval card interruption and resumption.
- Verify PDF, CSV, and JSON report downloads.
- Confirm PostgreSQL audit log persistence.

---

## 26. Existing Codebase Analysis
- **Relevant Files:** `HERMES-MANUAL.md`, `prd.md`.
- **Existing Patterns:** Greenfield project setup with Python `.venv` and Git repository initialized.
- **DO NOT Change:** Root configuration principles and strict FastMCP boundary.
- **Reuse:** Standard Python and React libraries.

---

## 27. Implementation Constraints
- Follow clean decoupled architecture (FastAPI -> FastMCP -> MLM XML-RPC).
- No JSON/JSONB columns anywhere in the database schema.
- Do not bypass FastMCP for MLM communications.
- State-altering operations must pass through human-in-the-loop approval gate.

---

## 28. Acceptance Criteria
- **AC-001 (FastMCP Inventory & Compliance):** Given the FastMCP server, when `system_list_systems` or `audit_list_scap_profiles` is called, then valid parsed SUSE MLM data is returned.
- **AC-002 (Streaming Conversational Chat):** Given a user query in chat, when submitted, then the agent streams real-time tokens along with collapsible thought/tool execution traces.
- **AC-003 (Human-in-the-Loop Remediation):** Given a request to patch a server, when the agent detects the action, then it halts at an interrupt state, produces an approval card in UI, and executes only when approved.
- **AC-004 (Compliance Report Export):** Given a request to export compliance data, when triggered, then PDF, CSV, and JSON reports are generated and downloadable from the web UI.
