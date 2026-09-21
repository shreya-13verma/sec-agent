# Technical & Operational Specification

## 1. System Overview & Architecture Boundaries
The **SUSE MLM Security & Compliance Agent** is an enterprise-grade agentic system engineered to continuously monitor, audit, plan, and remediate security posture for Linux fleets managed by SUSE Multi-Linux Manager (MLM) (`https://10.0.33.56/rhn/apidoc/index.jsp`).

### Component Boundary Rules
1. **Host Isolation:** Node management actions (package install, package removal, errata application) are strictly mediated through SUSE Multi-Linux Manager XML-RPC APIs. The agent does not execute arbitrary direct shell code on remote hosts without MLM audit coordination.
2. **Normalized Data Isolation:** All entity state (hosts, channels, packages, errata, rules, findings, reasoning thoughts, remediation steps, audit events) is stored in a 100% normalized relational database schema without JSON/JSONB blobs.
3. **Controlled Human-in-the-Loop Gate:** All autonomous remediation plans remain in `STAGED` status until explicitly approved by a user with `Admin` or `Security_Officer` permissions. Unapproved execution attempts are rejected with HTTP 400.
4. **Automatic Post-Verification:** Execution of an approved remediation plan triggers an automated compliance scan against the target host to verify that the compliance score has improved and missing errata have been resolved.

---

## 2. API Endpoint Specification

### Authentication & User Management
- `POST /api/v1/auth/login`
  - **Description:** Authenticates credentials and returns JWT access token with embedded role claims.
  - **Request Body:** `{"username": "admin", "password": "..."}`
  - **Response 200:** `{"access_token": "...", "token_type": "bearer", "user": {"id": 1, "username": "admin", "role": "Admin", "email": "..."}}`
  - **Response 401:** `{"detail": "Invalid username or password"}`
- `GET /api/v1/auth/me`
  - **Description:** Returns the profile of the currently authenticated user.
  - **Headers:** `Authorization: Bearer <token>`
- `POST /api/v1/auth/register`
  - **Description:** Admin endpoint for provisioning new user accounts.
  - **Required Role:** `Admin`

### Host Inventory & SUSE MLM Sync
- `GET /api/v1/hosts`
  - **Query Parameters:** `search` (string), `compliance_status` (string), `os_family` (string), `limit` (int), `offset` (int).
  - **Response 200:** `{"total": int, "items": [HostSummary]}`
- `GET /api/v1/hosts/{id}`
  - **Description:** Returns full host detail including installed package list, missing errata advisories with CVE identifiers, and subscribed MLM software channels.
- `POST /api/v1/hosts/sync`
  - **Description:** Triggers inventory discovery from SUSE MLM API endpoint (`https://10.0.33.56/rpc/api`).
  - **Required Roles:** `Admin`, `Security_Officer`, `Operator`
  - **Response 202:** `{"status": "SUCCESS", "synced_hosts_count": int, "synced_errata_count": int}`
- `DELETE /api/v1/hosts/{id}`
  - **Description:** Deletes a host record, with relational cascade deletion removing all child packages, channels, and findings.
  - **Required Role:** `Admin`

### Compliance Scans & Rule Engine
- `GET /api/v1/compliance/frameworks`
  - **Response 200:** List of seeded compliance frameworks (`CIS_SLES_15`, `HIPAA`, `PCI_DSS_V4`).
- `GET /api/v1/compliance/frameworks/{id}`
  - **Response 200:** Framework definition with all active rules and check types.
- `POST /api/v1/compliance/scans`
  - **Description:** Executes compliance audit scan for a framework across selected or all registered hosts.
  - **Request Body:** `{"framework_id": int, "host_ids": [int] | null}`
  - **Response 202:** `{"id": int, "scan_status": "COMPLETED", "overall_score": float, "hosts_scanned_count": int}`
- `GET /api/v1/compliance/scans/{id}`
  - **Response 200:** Detailed scan results including host rule evaluation findings.
- `GET /api/v1/compliance/findings`
  - **Query Parameters:** `scan_id` (int), `host_id` (int), `status` (PASS | FAIL).

### Autonomous Agent Engine
- `POST /api/v1/agent/analyze`
  - **Description:** Initiates multi-step agent reasoning session on a host.
  - **Request Body:** `{"host_id": int, "framework_id": int | null}`
  - **Response 200:**
    ```json
    {
      "id": 1,
      "host_id": 1,
      "analysis_status": "PLAN_GENERATED",
      "drift_detected": true,
      "root_cause_summary": "1 unpatched Critical Errata; Insecure legacy services detected: telnet",
      "thought_steps": [
        {"step_order": 1, "thought_type": "OBSERVATION", "thought_content": "..."},
        {"step_order": 2, "thought_type": "CORRELATION", "thought_content": "..."},
        {"step_order": 3, "thought_type": "RISK_EVALUATION", "thought_content": "..."},
        {"step_order": 4, "thought_type": "DECISION", "thought_content": "..."}
      ],
      "proposed_plan_id": 1
    }
    ```
- `GET /api/v1/agent/drift-detection`
  - **Response 200:** Fleet drift summary with recommended actions per host.

### Controlled Remediation Engine
- `GET /api/v1/remediations/plans`
  - **Query Parameters:** `status` (STAGED | APPROVED | REJECTED | COMPLETED), `host_id` (int).
- `GET /api/v1/remediations/plans/{id}`
  - **Response 200:** Plan detail with ordered remediation steps, MLM action IDs, and execution logs.
- `POST /api/v1/remediations/plans/{id}/approve`
  - **Description:** Authorizes a staged remediation plan for execution.
  - **Required Roles:** `Admin`, `Security_Officer`
  - **Request Body:** `{"approval_notes": "..."}`
- `POST /api/v1/remediations/plans/{id}/reject`
  - **Description:** Rejects a staged remediation plan with justification.
  - **Required Roles:** `Admin`, `Security_Officer`
  - **Request Body:** `{"rejection_reason": "..."}`
- `POST /api/v1/remediations/plans/{id}/execute`
  - **Description:** Dispatches approved remediation actions to SUSE MLM.
  - **Required Roles:** `Admin`, `Security_Officer`, `Operator`
  - **Response 202:** `{"plan_id": int, "status": "COMPLETED", "dispatched_steps_count": int}`

### Reports & Audit Trail
- `GET /api/v1/reports/compliance`
  - **Response 200:** Structured JSON executive compliance dataset.
- `GET /api/v1/reports/export/csv`
  - **Response 200:** Streamed `text/csv` attachment.
- `GET /api/v1/reports/export/pdf`
  - **Response 200:** Streamed `application/pdf` binary compliance dossier.
- `GET /api/v1/audit-logs`
  - **Query Parameters:** `action` (string), `resource_type` (string), `limit` (int), `offset` (int).
  - **Response 200:** Immutable audit records.

---

## 3. Data Models & Schema Mappings

All models reside in `backend/app/models/` and comply with the zero-JSON constraint:
- `users`: User identity, password hash (bcrypt), role, active status.
- `hosts`: Registered MLM systems, hardware architecture, kernel, compliance score, and status.
- `host_channels`: Relational child table of subscribed software channels.
- `host_packages`: Relational child table of installed RPM packages per host.
- `errata_advisories`: Security advisories, bug fixes, CVE references, severity, and issued timestamps.
- `host_missing_errata`: Relational join table linking hosts to applicable unpatched errata.
- `compliance_frameworks`: Framework definitions (`CIS_SLES_15`, `HIPAA`, `PCI_DSS_V4`).
- `compliance_rules`: Individual check definitions with target package/property and expected value.
- `compliance_scans`: Audit execution records with summary statistics.
- `compliance_findings`: Relational rule evaluation outcomes per host.
- `agent_analyses`: Multi-step reasoning session records with root-cause summaries.
- `agent_thought_steps`: Ordered thought traces (`OBSERVATION`, `CORRELATION`, `RISK_EVALUATION`, `DECISION`).
- `remediation_plans`: Staged remediation proposals with approval notes and risk levels.
- `remediation_steps`: Ordered actionable steps (`APPLY_ERRATA`, `INSTALL_PACKAGE`, `REMOVE_PACKAGE`).
- `audit_logs`: Immutable security log with actor username, action, resource ID, and client IP.

---

## 4. State Transitions & Lifecycle Rules

### Audit Scan Lifecycle
```
[PENDING] ──► [RUNNING] ──► [COMPLETED]
                   │
                   └──► [FAILED]
```

### Remediation Plan Lifecycle
```
                 ┌──► [REJECTED]
                 │
[STAGED] ──► [APPROVED] ──► [IN_PROGRESS] ──► [COMPLETED]
                                   │
                                   └──► [FAILED]
```
- **Rule 1:** A plan cannot transition to `APPROVED` or `REJECTED` unless its current state is `STAGED` or `DRAFT`.
- **Rule 2:** `POST .../execute` is strictly rejected if the plan is in `STAGED`, `REJECTED`, or `DRAFT` state.
- **Rule 3:** Once execution finishes, the plan moves to `COMPLETED` and automatically launches a verification scan.

---

## 5. Error Handling & Resilience Policy
- **SUSE MLM Offline Graceful Degradation:** When the upstream endpoint (`10.0.33.56`) is unreachable, the adapter transparently utilizes cached/mock infrastructure, allowing security teams to continue reviewing baselines without system crashes.
- **Transactional Rollback:** Database sessions utilize scoped transactions; any unhandled database exception results in an immediate rollback preventing partial/corrupt states.
- **Uniform Error Envelope:** All client errors return standard FastAPI schema `{"detail": "<Human-readable message>"}`.
