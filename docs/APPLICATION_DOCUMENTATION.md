# Comprehensive Application Documentation: SUSE MLM Security & Compliance Agent

## 1. Architectural Boundary Rules & Protocols

### 1.1 Decoupled Integration Pattern
The application strictly enforces that the FastAPI core and LangGraph agent communicate with SUSE Multi-Linux Manager (MLM) / Uyuni exclusively through the dedicated **FastMCP Server** (`mcp_server/server.py`). No direct XML-RPC calls bypass this boundary.

```
[React Frontend] <-- HTTP/SSE --> [FastAPI Backend / LangGraph] <-- MCP Protocol --> [FastMCP Server] <-- XML-RPC --> [SUSE MLM]
```

### 1.2 Human-in-the-Loop Approval Boundary
All state-altering actions (e.g. `system.scheduleApplyErrata`, `audit.scheduleXccdfScan`) cannot be executed autonomously by the agent. When intent is classified as `remediation_request`:
1. The LangGraph state machine halts at an `interrupt()` / proposal node.
2. A cryptographically random, single-use token (`appr_tok_<32_hex_chars>`) is generated with a 900-second TTL.
3. The React UI renders an interactive `ApprovalCard`.
4. The FastMCP write tool is dispatched **only** after the operator clicks "Approve" and the token is validated against PostgreSQL.

---

## 2. API Endpoint Reference

### 2.1 Chat & Streaming
- `POST /api/v1/chat/message`
  - **Request Body:** `{"session_id": string (optional), "message": string}`
  - **Response:** Server-Sent Events (SSE) stream yielding:
    - `event: session_id` -> `{"session_id": "uuid"}`
    - `event: thought` -> `{"thought": "string"}`
    - `event: tool_call` -> `{"tool": "string", "status": "executed"}`
    - `event: approval_required` -> `{"approval_token": "string", "plan": {...}}`
    - `event: token` -> `{"token": "chunk "}`
    - `event: done` -> `{"status": "completed"}`
- `GET /api/v1/chat/sessions`
  - Returns array of `ChatSessionResponse` sorted by `updated_at DESC`.
- `GET /api/v1/chat/sessions/{session_id}/messages`
  - Returns complete chronological message history for a session.

### 2.2 Managed Servers & Fleet Inventory
- `GET /api/v1/systems`
  - Returns list of registered server summaries (`id`, `hostname`, `ip_address`, `os_release`, `kernel_version`, `compliance_score`, `security_errata_count`).
- `GET /api/v1/systems/{server_id}`
  - Returns granular metadata for a given server.
- `GET /api/v1/systems/{server_id}/packages`
  - Returns installed RPM package catalog.

### 2.3 Compliance & OpenSCAP
- `GET /api/v1/compliance/scap-profiles`
  - Lists native OpenSCAP profiles (`CIS`, `DISA STIG`, `HIPAA`, `PCI-DSS`).
- `GET /api/v1/compliance/scans/{server_id}`
  - Returns latest OpenSCAP scan scores, pass/fail counts, and detailed rule failure objects.
- `GET /api/v1/compliance/errata/{server_id}`
  - Returns pending Security, Bugfix, and Enhancement advisories with mapped CVEs.

### 2.4 Human-in-the-Loop Approvals
- `GET /api/v1/approvals/pending`
  - Lists all active, unresolved remediation approval requests.
- `POST /api/v1/approvals/{token}/action`
  - **Request Body:** `{"approved": boolean, "operator": string, "comment": string}`
  - **Behavior:** Validates TTL and single-use status; on approval, invokes FastMCP `system_schedule_apply_errata` and returns `mlm_action_id`.

### 2.5 Compliance Reporting
- `POST /api/v1/reports/generate`
  - **Request Body:** `{"title": string, "scope": "all"|"system", "target_id": string, "formats": ["pdf", "csv", "json"]}`
  - **Response:** `ReportResponse` with generated file paths.
- `GET /api/v1/reports/{report_id}/download/{format_type}`
  - Streams binary download (`application/pdf`, `text/csv`, `application/json`).

---

## 3. Relational Data Models (Strict 0 JSON Columns)

All database entities are fully normalized without any schemaless JSON or JSONB columns:

```sql
-- Chat Sessions
CREATE TABLE chat_sessions (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Chat Messages
CREATE TABLE chat_messages (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) REFERENCES chat_sessions(id) ON DELETE CASCADE,
    sender VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    thought_log TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Managed Servers
CREATE TABLE managed_servers (
    id BIGINT PRIMARY KEY,
    hostname VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    os_release VARCHAR(100) NOT NULL,
    kernel_version VARCHAR(100) NOT NULL,
    last_checkin TIMESTAMP WITH TIME ZONE,
    compliance_score FLOAT NOT NULL DEFAULT 0.0,
    security_errata_count INTEGER NOT NULL DEFAULT 0,
    bugfix_errata_count INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- OpenSCAP Scans
CREATE TABLE openscap_scans (
    id VARCHAR(36) PRIMARY KEY,
    mlm_test_result_id BIGINT UNIQUE NOT NULL,
    server_id BIGINT REFERENCES managed_servers(id) ON DELETE CASCADE,
    profile_name VARCHAR(255) NOT NULL,
    scan_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    pass_count INTEGER NOT NULL DEFAULT 0,
    fail_count INTEGER NOT NULL DEFAULT 0,
    error_count INTEGER NOT NULL DEFAULT 0,
    other_count INTEGER NOT NULL DEFAULT 0,
    score FLOAT NOT NULL DEFAULT 0.0
);

-- OpenSCAP Rule Results
CREATE TABLE openscap_rule_results (
    id VARCHAR(36) PRIMARY KEY,
    scan_id VARCHAR(36) REFERENCES openscap_scans(id) ON DELETE CASCADE,
    rule_identifier VARCHAR(255) NOT NULL,
    rule_title VARCHAR(500) NOT NULL,
    result VARCHAR(50) NOT NULL,
    severity VARCHAR(50) NOT NULL
);

-- System Errata Advisories
CREATE TABLE system_errata_advisories (
    id VARCHAR(36) PRIMARY KEY,
    server_id BIGINT REFERENCES managed_servers(id) ON DELETE CASCADE,
    advisory_name VARCHAR(100) NOT NULL,
    advisory_type VARCHAR(50) NOT NULL,
    cve_id VARCHAR(100) NOT NULL DEFAULT 'N/A',
    synopsis TEXT NOT NULL,
    issue_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    remediation_status VARCHAR(50) NOT NULL DEFAULT 'pending'
);

-- Remediation Approvals
CREATE TABLE remediation_approvals (
    id VARCHAR(36) PRIMARY KEY,
    approval_token VARCHAR(128) UNIQUE NOT NULL,
    session_id VARCHAR(36) REFERENCES chat_sessions(id) ON DELETE CASCADE,
    server_id BIGINT REFERENCES managed_servers(id) ON DELETE CASCADE,
    action_type VARCHAR(100) NOT NULL DEFAULT 'Apply Errata Remediation',
    proposed_errata_ids TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    operator VARCHAR(100),
    operator_comment TEXT,
    mlm_action_id BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Compliance Reports
CREATE TABLE compliance_reports (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    report_scope VARCHAR(50) NOT NULL,
    target_id VARCHAR(100) NOT NULL DEFAULT 'all',
    pdf_path VARCHAR(500) NOT NULL,
    csv_path VARCHAR(500) NOT NULL,
    json_path VARCHAR(500) NOT NULL,
    generated_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Audit Logs
CREATE TABLE audit_logs (
    id VARCHAR(36) PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    operator VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id VARCHAR(100) NOT NULL,
    action_details TEXT NOT NULL,
    ip_address VARCHAR(45) NOT NULL DEFAULT '127.0.0.1',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. State Transitions & Lifecycle Rules

### 4.1 Remediation Proposal Lifecycle
```
[User Query] 
     │
     ▼
[Intent Analysis: remediation_request]
     │
     ▼
[Generate Plan & Token (status: pending)] ─── (Timeout > 900s) ───► [status: expired]
     │
     ├─────────── Operator Action: Approve ──────────► [Dispatch FastMCP: status: approved]
     │
     └─────────── Operator Action: Reject ──────────► [status: rejected (No MLM modification)]
```

---

## 5. Resilience & Error Handling Policies
- **XML-RPC Network Partition:** FastMCP wraps raw faults and returns structured JSON `{status: "error", code: N, message: "..."}` preventing uncaught exceptions.
- **Fail-Closed Security:** Approval tokens are strictly single-use and expire after 15 minutes (900 seconds). Subsequent execution attempts return 400 Bad Request.
- **Streaming Integrity:** SSE connections flush thought events and tokens asynchronously; if a client disconnects mid-stream, database commits for completed messages remain consistent.
