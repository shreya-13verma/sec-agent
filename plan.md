# PLAN.md

## 1. Overview
- **Project / Feature Name:** SUSE MLM Security & Compliance Agent (Compliance Agent)
- **Problem Statement:** Infrastructure operations and security teams managing Linux server fleets across enterprise environments face significant complexity in maintaining continuous regulatory compliance (CIS Benchmarks, HIPAA, PCI-DSS, STIG), detecting security configuration drift, identifying critical errata/CVEs, and safely orchestrating remediations across hosts registered to SUSE Multi-Linux Manager (MLM). Manual compliance audits are time-consuming, point-in-time, error-prone, and lack autonomous multi-step reasoning for remediation planning and audit trail preservation.
- **Goal:** Deliver an autonomous, agentic security and compliance platform integrating with SUSE Multi-Linux Manager (MLM) to continuously audit registered hosts, detect drift, perform multi-step agent reasoning for remediation planning, generate executive and technical audit reports (PDF, CSV, web dashboards), and execute safety-bounded, human-approved remediation tasks with complete cryptographic and relational audit trails.
- **Non-Goals:**
  - Replacing SUSE Multi-Linux Manager itself as the primary package mirror or host provisioning daemon.
  - Deploying hypervisor-level firmware updates or out-of-band hardware management outside MLM API capabilities.
  - Unsupervised, fully autonomous execution of destructive kernel re-installations without explicit user approval boundaries.
- **Success Criteria:**
  - Full discovery and synchronization of registered systems, software channels, CVE errata, and installed packages via SUSE MLM API adapter.
  - Automated compliance evaluation against CIS, HIPAA, PCI-DSS, and hardening standards with score computation across systems.
  - Multi-step autonomous agent engine for root-cause diagnosis, posture analysis, drift detection, and step-by-step remediation plan synthesis.
  - Role-gated remediation lifecycle with explicit staging, risk assessment, human approval gate, and execution tracking via MLM actions.
  - Exportable audit-ready reports (PDF and CSV) and interactive real-time React dashboard with sub-second response times.
  - 100% normalized PostgreSQL schema with zero JSON/JSONB fields and exhaustive test coverage (Unit, Integration, API, Security, Performance, and Playwright E2E browser tests).

---

## 2. Requirements

### Functional Requirements
- **FR-001 (SUSE MLM Synchronization & Inventory):** The system shall connect to SUSE Multi-Linux Manager API (`https://10.0.33.56/rhn/apidoc/index.jsp` / XML-RPC / REST) to authenticate, discover, and synchronize registered systems, OS versions, hardware details, subscribed channels, and installed package inventories.
- **FR-002 (Vulnerability & Errata Tracking):** The system shall ingest, index, and track all available security advisories, bug fixes, enhancement errata, CVE identifiers, and missing package updates per registered host.
- **FR-003 (Compliance Framework & Benchmark Engine):** The system shall execute automated compliance scans against standardized frameworks (CIS Benchmarks Level 1/2, HIPAA Security Rule, PCI-DSS v4.0, Linux Hardening Baselines) evaluating configuration rules, required packages, prohibited services, and patch levels.
- **FR-004 (Autonomous Agent Engine & Reasoning Loop):** The system shall provide an autonomous agent engine that utilizes tool execution, posture analysis, drift detection, and multi-step reasoning to analyze system vulnerabilities, correlate misconfigurations, determine remediation priorities, and generate structured remediation plans.
- **FR-005 (Controlled Remediation & Approval Gate):** The system shall enforce a strict approval workflow for all remediation plans. No remediation job shall be executed on MLM hosts until an authorized user explicitly approves the staged plan.
- **FR-006 (Remediation Execution & Verification):** The system shall dispatch approved remediation actions (package upgrade, errata application, config enforcement, script execution) via SUSE MLM API, monitor job progress, and trigger automatic post-remediation verification scans.
- **FR-007 (Audit Trail & Historical Snapshots):** The system shall maintain an immutable, relational audit log of every agent reasoning step, scan result, user approval, parameter override, and remediation execution.
- **FR-008 (Reporting & Export):** The system shall generate comprehensive executive summaries, technical compliance reports, drift logs, and remediation audit records with export capabilities in PDF, CSV, and interactive dashboard views.
- **FR-009 (Authentication & Role-Based Access Control):** The system shall provide secure user authentication (JWT) with distinct roles: `Admin`, `Security_Officer`, `Operator`, and `Auditor`.

---

### User Stories & Complete Lifecycle Scenarios

#### US-001 (Security Officer): Discover Infrastructure and Run Baseline Compliance Scans
- **User Story:** As a Security Officer, I want to synchronize the host inventory from SUSE MLM and trigger a compliance scan against CIS Level 1 benchmarks so that I can evaluate our overall fleet posture.
- **Scenario A (Happy Path - Full Lifecycle Discovery & Scan):**
  - *Given* a configured connection to SUSE Multi-Linux Manager with 10 registered SLES/RHEL hosts.
  - *When* the Security Officer clicks "Sync Inventory" and initiates a "CIS Benchmark Level 1" audit on the host fleet.
  - *Then* the backend synchronizes all host metadata, evaluates all 45 benchmark rules, records individual rule results in `audit_findings`, computes a fleet compliance score (e.g. 84%), and updates the UI dashboard in real time.
- **Scenario B (Negative / Connection Failure):**
  - *Given* the SUSE MLM API endpoint is unreachable or credentials have expired.
  - *When* an inventory sync or scan is triggered.
  - *Then* the system transitions the scan status to `FAILED`, logs the connection error in the audit log, displays a clear error toast to the user, and leaves existing historical snapshot data intact.

#### US-002 (Security Officer / Operator): Autonomous Agent Reasoning & Remediation Plan Generation
- **User Story:** As an Operator, I want the autonomous agent to analyze compliance drift on a non-compliant host and synthesize an actionable, multi-step remediation plan so that I understand what patches and configuration changes are required.
- **Scenario A (Happy Path - Agent Reasoning to Staged Plan):**
  - *Given* Host `srv-db-01` has 3 critical errata and 2 failing CIS configuration rules.
  - *When* the user requests "Autonomous Remediation Analysis" for `srv-db-01`.
  - *Then* the Autonomous Agent executes its multi-step reasoning loop (analyzing dependencies, checking channel availability, calculating risk), creates a `remediation_plan` in `STAGED` status with ordered `remediation_steps`, and notifies the user that approval is pending.
- **Scenario B (Edge Case - Circular Dependency / Unavailable Package):**
  - *Given* an erratum requires a package version not present in the host's subscribed software channels.
  - *When* the agent analyzes the remediation feasibility.
  - *Then* the agent flags the blocker in its reasoning log, marks the specific step as `BLOCKED_CHANNEL_MISSING`, creates a partial remediation plan for resolvable items, and alerts the operator.

#### US-003 (Admin / Security Officer): Review, Approve, and Execute Controlled Remediation
- **User Story:** As an Admin, I want to review the staged remediation plan, inspect individual actions, and approve execution so that remediation only occurs under strict authorization.
- **Scenario A (Happy Path - Approval, Dispatch, and Verification):**
  - *Given* a staged remediation plan with 3 package upgrades and 1 configuration lock.
  - *When* the Admin approves the plan and clicks "Execute Remediation".
  - *Then* the status changes to `IN_PROGRESS`, the system dispatches actions to SUSE MLM, polls execution status until completion (`SUCCESS`), and automatically triggers a post-remediation audit scan confirming the host is now compliant.
- **Scenario B (Rejection / Cancellation):**
  - *Given* a staged remediation plan during a maintenance freeze window.
  - *When* the Admin rejects the plan with reason "Maintenance freeze in effect".
  - *Then* the plan status transitions to `REJECTED`, no MLM actions are scheduled, and the rejection reason is committed to the audit trail.

#### US-004 (Auditor): Generate and Export Audit-Ready Reports
- **User Story:** As an Auditor, I want to generate compliance reports filtered by framework, system group, or date range and export them as PDF or CSV so that I can provide evidence to external compliance assessors.
- **Scenario A (Happy Path - PDF/CSV Generation & Download):**
  - *Given* historical compliance audit snapshots and remediation records across the fleet.
  - *When* the Auditor selects "PCI-DSS v4.0", date range "Last 30 Days", and clicks "Export PDF Report".
  - *Then* the system renders a multi-page executive summary including compliance breakdown charts, system inventory tables, errata resolution logs, and serves the downloadable PDF file.
- **Scenario B (Edge Case - Empty Dataset / No Records in Filter):**
  - *Given* a filter query matching zero hosts or scans.
  - *When* the Auditor requests a report export.
  - *Then* the system returns an empty-state notification without crashing or producing a corrupted blank file.

---

### Non-Functional Requirements
- **Performance:**
  - API endpoint response latency < 200ms for p95 requests under standard load.
  - Compliance evaluation engine processing speed > 50 hosts/second.
  - PDF/CSV report generation < 2.5 seconds for 500-host fleets.
- **Scalability:**
  - Support up to 5,000 registered hosts and 500,000 historical audit findings.
  - Concurrent user support: up to 100 simultaneous active operators/auditors.
- **Availability & Reliability:**
  - Service uptime target: 99.9%.
  - Database transactions with atomic ACID rollback on failure during scan or remediation orchestration.
- **Security:**
  - Password hashing using native bcrypt (`bcrypt.hashpw` / `bcrypt.checkpw`).
  - JWT authentication with secure expiration and RBAC validation on all mutation endpoints.
  - Sanitized inputs protecting against SQL injection, XSS, and command injection.
  - Zero plain-text credentials stored; SUSE MLM credentials stored securely via environment variables and encrypted config.
- **Observability:**
  - Structured logging with correlation IDs on every HTTP request and agent reasoning step.
  - Health check endpoint `/health` verifying API and PostgreSQL database connectivity.
- **Maintainability:**
  - Modular architecture (API routes, services, models, schemas, agent engine, MLM adapters).
  - 100% normalized schema with foreign key cascades preventing orphan records.

---

## 3. Scope

### In Scope
- SUSE Multi-Linux Manager API adapter (XML-RPC & REST client with live connection and robust mock test harness).
- Fleet inventory synchronization (Hosts, Groups, Subscribed Channels, Packages, Errata).
- Compliance evaluation engine supporting CIS Benchmarks, HIPAA, PCI-DSS, and Custom Hardening Rules.
- Multi-step Autonomous Agent Engine with reasoning traces, drift detection, and remediation planning.
- Role-gated human-in-the-loop remediation approval workflow.
- Remediation dispatcher via MLM action scheduling and post-remediation verification.
- Executive and technical report generator with PDF and CSV export endpoints.
- Modern responsive React Single Page Application (Dashboard, Host Inventory, Compliance Audits, Agent Console, Remediation Manager, Reports, Audit Logs, Settings).
- Full automated test suite (Unit, Integration, API, Security, Performance, and Playwright E2E browser tests).
- Docker containerization with `docker-compose.yml` for single-command orchestration.

### Out of Scope
- Direct SSH/Ansible execution bypassing SUSE MLM (all node management is mediated via MLM).
- Hardware out-of-band power management (IPMI/iLO).
- Windows Server Active Directory policy management.

---

## 4. User / System Flows

### Main User Flow
1. **Login & Overview:** User logs into the React frontend with role-based credentials. Dashboard displays fleet compliance health, critical errata, open remediations, and agent activity.
2. **Inventory Sync:** Operator or scheduled worker triggers an inventory sync from SUSE MLM.
3. **Audit Execution:** User or automated cron job triggers a compliance audit for selected frameworks (e.g. CIS, HIPAA).
4. **Agent Reasoning:** The autonomous agent analyzes non-compliant hosts, evaluates missing errata and misconfigurations, calculates blast radius, and compiles a staged `remediation_plan`.
5. **Human Approval:** Admin reviews the proposed remediation steps, inspects errata details, and clicks `Approve`.
6. **Remediation Execution:** Backend dispatches actions to SUSE MLM, streams execution status updates, and marks steps completed.
7. **Verification Scan:** System triggers an automatic post-remediation scan, verifying that the target hosts have achieved compliance.
8. **Reporting & Audit:** Auditor reviews the updated compliance score and downloads executive PDF / CSV compliance reports.

### Error & Edge Flows
- **MLM Endpoint Offline:** Handled gracefully via exponential backoff retry; if offline, user receives a structured notification; existing cached inventory remains available in read-only audit mode.
- **Action Failure on Host:** If an MLM action fails (e.g. package lock), the step is marked `FAILED`, the remediation execution halts gracefully, rollback recommendations are generated, and an alert is recorded.
- **Token Expiry / Unauthorized Access:** 401 response triggers automatic frontend redirect to `/login` with stored return path.

### State Transitions
- **Audit Scan State:** `PENDING` → `RUNNING` → `COMPLETED` | `FAILED` | `CANCELLED`
- **Remediation Plan State:** `DRAFT` → `STAGED` → `APPROVED` | `REJECTED` → `IN_PROGRESS` → `COMPLETED` | `PARTIAL_FAILURE` | `FAILED`
- **Remediation Step State:** `QUEUED` → `DISPATCHED` → `RUNNING` → `SUCCESS` | `FAILED` | `SKIPPED`

---

## 5. Architecture

### Components & Services
- **Frontend (React SPA):** React 18, Vite, Tailwind CSS, Lucide Icons, Axios, React Router.
- **Backend (FastAPI):** Python 3.11, FastAPI, Pydantic v2, SQLAlchemy (Async/Sync ORM), ReportLab (PDF generation).
- **Database (PostgreSQL 16):** Normalized relational database with indexed queries and foreign key constraints.
- **SUSE MLM Client Adapter:** Handles authentication, XML-RPC/REST session management, host discovery, errata querying, and action dispatching.
- **Autonomous Agent Engine:** Rule evaluator, drift detector, reasoning loop, dependency analyzer, and remediation planner.
- **Reporting Engine:** Formats compliance data into structured tables, CSV streams, and styled multi-page PDF documents.

### Architecture Diagram
```
┌─────────────────────────────────────────────────────────────────────────┐
│                           React 18 Frontend                             │
│  (Dashboard, Hosts, Audits, Agent Console, Remediations, Reports, Logs) │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ HTTPS / REST API / JWT
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        FastAPI Backend Engine                           │
│  ┌──────────────────────┬──────────────────────┬─────────────────────┐  │
│  │ Auth & RBAC Router   │ Host & Sync Router   │ Compliance Router   │  │
│  ├──────────────────────┼──────────────────────┼─────────────────────┤  │
│  │ Agent Engine Router  │ Remediation Router   │ Reporting & Export  │  │
│  └──────────────────────┴──────────────────────┴─────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                 Autonomous Compliance Agent Core                  │  │
│  │  [Posture Analyzer] -> [Drift Detector] -> [Plan Synthesizer]     │  │
│  └──────────────────────────────────┬────────────────────────────────┘  │
│  ┌──────────────────────────────────┴────────────────────────────────┐  │
│  │               SUSE Multi-Linux Manager API Adapter                │  │
│  │   (XML-RPC / REST Session Manager, Errata & Package Dispatcher)   │  │
│  └──────────────────────────────────┬────────────────────────────────┘  │
└───────────────────┬─────────────────┼───────────────────────────────────┘
                    │                 │
                    ▼                 ▼
     ┌────────────────────────┐  ┌────────────────────────────────────────┐
     │ PostgreSQL 16 Database │  │   SUSE Multi-Linux Manager (MLM)       │
     │  (Normalized Relational│  │      https://10.0.33.56/rhn/...        │
     │   Zero-JSON Schema)    │  │ (Registered Linux Hosts, Errata, Repos)│
     └────────────────────────┘  └────────────────────────────────────────┘
```

### Project Directory Structure (Required)
```
/home/shreya/compliance-agent/
├── backend/                                   (new)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                            (new - FastAPI application entry point)
│   │   ├── config.py                          (new - App settings & environment config)
│   │   ├── database.py                        (new - SQLAlchemy DB engine & session)
│   │   ├── models/                            (new - Normalized SQLAlchemy ORM models)
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── host.py
│   │   │   ├── compliance.py
│   │   │   ├── remediation.py
│   │   │   ├── agent.py
│   │   │   └── audit_log.py
│   │   ├── schemas/                           (new - Pydantic validation models)
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── host.py
│   │   │   ├── compliance.py
│   │   │   ├── remediation.py
│   │   │   ├── agent.py
│   │   │   └── report.py
│   │   ├── routers/                           (new - API endpoint handlers)
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── hosts.py
│   │   │   ├── compliance.py
│   │   │   ├── agent.py
│   │   │   ├── remediation.py
│   │   │   ├── reports.py
│   │   │   └── audit_logs.py
│   │   ├── services/                          (new - Core business logic)
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── suse_mlm_client.py             (new - SUSE MLM API adapter)
│   │   │   ├── compliance_engine.py           (new - Framework rule evaluation)
│   │   │   ├── agent_engine.py                (new - Multi-step autonomous agent)
│   │   │   ├── remediation_service.py         (new - Action orchestration & approval)
│   │   │   └── report_service.py              (new - PDF/CSV generation engine)
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── security.py                    (new - Password hashing & JWT)
│   │       └── seed_data.py                   (new - Standard frameworks & initial seed)
│   ├── tests/                                 (new - Backend test suite)
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_hosts_and_sync.py
│   │   ├── test_compliance_engine.py
│   │   ├── test_agent_reasoning.py
│   │   ├── test_remediation_workflow.py
│   │   ├── test_reports_export.py
│   │   ├── test_security_and_rbac.py
│   │   └── test_performance_and_edge_cases.py
│   ├── requirements.txt                       (new - Python dependencies)
│   └── Dockerfile                             (new - Backend container image)
├── frontend/                                  (new)
│   ├── src/
│   │   ├── main.jsx                           (new - React application entry)
│   │   ├── App.jsx                            (new - Root routing & layout)
│   │   ├── index.css                          (new - Tailwind styling)
│   │   ├── api/                               (new - Axios client & API helpers)
│   │   │   ├── client.js
│   │   │   ├── auth.js
│   │   │   ├── hosts.js
│   │   │   ├── compliance.js
│   │   │   ├── agent.js
│   │   │   ├── remediation.js
│   │   │   └── reports.js
│   │   ├── context/                           (new - Global state & Auth context)
│   │   │   └── AuthContext.jsx
│   │   ├── components/                        (new - Reusable UI widgets)
│   │   │   ├── Layout.jsx
│   │   │   ├── Navbar.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   ├── StatCard.jsx
│   │   │   ├── ComplianceGauge.jsx
│   │   │   ├── StatusBadge.jsx
│   │   │   ├── Modal.jsx
│   │   │   └── Toast.jsx
│   │   └── pages/                             (new - Application screens)
│   │       ├── Login.jsx
│   │       ├── Dashboard.jsx
│   │       ├── Hosts.jsx
│   │       ├── HostDetail.jsx
│   │       ├── ComplianceScans.jsx
│   │       ├── AgentConsole.jsx
│   │       ├── RemediationManager.jsx
│   │       ├── Reports.jsx
│   │       ├── AuditLogs.jsx
│   │       └── Settings.jsx
│   ├── package.json                           (new - Node dependencies)
│   ├── vite.config.js                         (new - Vite configuration & proxy)
│   ├── tailwind.config.js                     (new - Tailwind CSS setup)
│   ├── postcss.config.js                      (new)
│   └── Dockerfile                             (new - Frontend container image)
├── e2e/                                       (new - Playwright browser E2E test suite)
│   ├── playwright.config.js
│   ├── package.json
│   └── tests/
│       ├── auth_and_navigation.spec.js
│       ├── host_discovery_and_audit.spec.js
│       ├── agent_reasoning_and_remediation.spec.js
│       └── report_export_and_audit_trail.spec.js
├── docs/                                      (new - Phased implementation & technical documentation)
│   ├── APPLICATION_DOCUMENTATION.md
│   ├── PHASE_1_FOUNDATION_AND_MLM_SYNC.md
│   ├── PHASE_2_COMPLIANCE_AND_AGENT_ENGINE.md
│   ├── PHASE_3_REMEDIATION_AND_REPORTING.md
│   └── PHASE_4_FRONTEND_AND_E2E_VERIFICATION.md
├── docker-compose.yml                         (new - Full multi-service orchestration)
├── README.md                                  (new - Industry-grade project documentation)
├── prd.md                                     (existing - Product requirements document)
├── Hermes-Manual.md                           (existing - Hermes process manual)
├── plan.md                                    (new - System implementation plan)
└── task.md                                    (new - Step-by-step checkable task tracker)
```

### Frontend Plan (Required for UI)
- **Pages / Routes:**
  - `/login`: User authentication with credentials, error handling, session persistence.
  - `/`: Main dashboard (Fleet compliance posture, critical CVEs, active scans, agent recommendations).
  - `/hosts`: System inventory table with channel, OS, compliance badge, search, and filter.
  - `/hosts/:id`: Detailed system view (installed packages, missing errata, compliance rules breakdown).
  - `/compliance`: Framework audit center (CIS, HIPAA, PCI-DSS scan triggers, score history).
  - `/agent`: Autonomous Agent Console (Real-time agent reasoning trace, drift detection, interactive investigation).
  - `/remediation`: Controlled Remediation Manager (Staged plans, risk impact, human approval modal, execution logs).
  - `/reports`: Report Generator (Filter by framework/host, live preview, PDF/CSV downloads).
  - `/audit-logs`: Immutable security audit trail with user actions and timestamps.
  - `/settings`: SUSE MLM connection config, scan schedule intervals, threshold parameters.
- **Component Hierarchy:**
  - `Layout` (Sidebar, Header, Breadcrumbs, System Status indicator).
  - `StatCard`, `ComplianceGauge`, `StatusBadge`, `DataTable`, `FilterDropdown`, `ConfirmationModal`, `AgentThoughtStream`, `ToastContainer`.
- **State Management:** React Context (`AuthContext` for user session & permissions) + local component state with optimistic updates and polling for live agent/job runs.
- **Styling:** Tailwind CSS with dark/light enterprise security dashboard theme, responsive flex/grid layouts.
- **Routing & Navigation Guards:** `ProtectedRoute` component enforcing authenticated sessions and RBAC role permissions.
- **Build Tooling:** Vite 6 / React 18 / Node 20.

---

## 6. Technology Decisions
- **Backend Framework:** FastAPI (Python 3.11) — high-performance asynchronous REST API, native Pydantic v2 validation, automated OpenAPI docs.
- **Database:** PostgreSQL 16 (with SQLite support for isolated unit tests) — relational integrity, strong ACID guarantees, indexed query performance.
- **ORM:** SQLAlchemy 2.0 — declarative models with explicit relational foreign keys and cascade options.
- **Password Security:** Native `bcrypt` — secure salted password hashing resisting brute-force attacks.
- **JWT Authentication:** `python-jose` / `pyjwt` with SHA256 signatures for stateless, secure session authorization.
- **PDF Generation:** `reportlab` — industry-standard programmatic PDF builder generating formatted compliance dossiers with headers, tables, and audit signatures.
- **Frontend Framework:** React 18 + Vite — component-driven UI with instant Hot Module Replacement and production bundling.
- **CSS Framework:** Tailwind CSS — utility-first styling for consistent design system tokens.
- **Icons:** `lucide-react` — clean, modern SVG icons for system dashboards.
- **Browser E2E Automation:** Playwright (`@playwright/test`) — reliable cross-browser automated user journey validation.

---

## 7. API / Interface Contract

### Authentication & Users
- `POST /api/v1/auth/login` → `Request: {username, password}` → `Response 200: {access_token, token_type, user: {id, username, email, role}}` | `401: Unauthorized`
- `GET /api/v1/auth/me` → `Response 200: {id, username, email, role, full_name}`

### Host Inventory & SUSE MLM Sync
- `GET /api/v1/hosts` → `Query: [search, status, compliance_status, limit, offset]` → `Response 200: {total, items: [HostSummary]}`
- `GET /api/v1/hosts/{id}` → `Response 200: HostDetail (with packages, errata, channels)`
- `POST /api/v1/hosts/sync` → `Request: {force_full_sync: bool}` → `Response 202: {sync_job_id, status, synced_count}`

### Compliance & Audits
- `GET /api/v1/compliance/frameworks` → `Response 200: [FrameworkSummary (CIS, HIPAA, PCI-DSS, STIG)]`
- `POST /api/v1/compliance/scans` → `Request: {framework_id, host_ids: [int]}` → `Response 202: {scan_id, status: "PENDING"}`
- `GET /api/v1/compliance/scans/{id}` → `Response 200: ScanDetail (with rule findings and overall score)`
- `GET /api/v1/compliance/findings` → `Query: [host_id, framework_id, status, severity]` → `Response 200: [FindingSummary]`

### Autonomous Agent Engine
- `POST /api/v1/agent/analyze` → `Request: {host_id, target_framework_id}` → `Response 200: {analysis_id, status, reasoning_steps: [Step], proposed_plan_id}`
- `GET /api/v1/agent/analyses/{id}` → `Response 200: AgentAnalysisDetail`
- `GET /api/v1/agent/drift-detection` → `Response 200: {drift_summary: [HostDriftItem]}`

### Remediation Management & Approval Gate
- `GET /api/v1/remediations/plans` → `Query: [status, host_id]` → `Response 200: [RemediationPlanSummary]`
- `GET /api/v1/remediations/plans/{id}` → `Response 200: RemediationPlanDetail (steps, risks, status)`
- `POST /api/v1/remediations/plans/{id}/approve` → `Request: {approval_notes}` → `Response 200: {plan_id, status: "APPROVED", approved_by}`
- `POST /api/v1/remediations/plans/{id}/reject` → `Request: {rejection_reason}` → `Response 200: {plan_id, status: "REJECTED"}`
- `POST /api/v1/remediations/plans/{id}/execute` → `Response 202: {execution_job_id, status: "IN_PROGRESS"}`

### Reporting & Audit Logs
- `GET /api/v1/reports/compliance` → `Query: [framework_id, host_id, format: "json"|"csv"|"pdf"]` → `Response 200: Report Data or File Download Stream`
- `GET /api/v1/audit-logs` → `Query: [limit, offset, action, user_id]` → `Response 200: {total, items: [AuditLogItem]}`
- `GET /api/v1/health` → `Response 200: {status: "healthy", database: "connected", mlm_adapter: "ready"}`

---

## 8. Data Model

**JSON/JSONB Constraint Compliance:** No JSON, JSONB, or schemaless blob fields are present in this data model. All entities use explicitly typed, normalized relational tables and columns.

### Normalized Relational Entities

1. **`users`**
   - `id`: Integer, Primary Key, Auto-increment.
   - `username`: String(64), Unique, Not Null, Indexed.
   - `email`: String(128), Unique, Not Null.
   - `hashed_password`: String(255), Not Null.
   - `full_name`: String(128), Not Null.
   - `role`: String(32), Not Null (e.g. `Admin`, `Security_Officer`, `Operator`, `Auditor`).
   - `is_active`: Boolean, Default True.
   - `created_at`: DateTime, Not Null.
   - `updated_at`: DateTime, Not Null.

2. **`hosts`**
   - `id`: Integer, Primary Key, Auto-increment.
   - `mlm_system_id`: Integer, Unique, Not Null, Indexed (ID in SUSE MLM).
   - `hostname`: String(255), Not Null, Indexed.
   - `ip_address`: String(64), Not Null.
   - `os_family`: String(64), Not Null (e.g. `SLES`, `RHEL`, `openSUSE`).
   - `os_version`: String(64), Not Null.
   - `kernel_release`: String(128), Not Null.
   - `architecture`: String(32), Not Null (e.g. `x86_64`, `aarch64`).
   - `last_checkin_time`: DateTime, Nullable.
   - `compliance_status`: String(32), Not Null, Default `UNKNOWN` (`COMPLIANT`, `NON_COMPLIANT`, `CRITICAL`, `UNKNOWN`).
   - `compliance_score`: Float, Not Null, Default 0.0.
   - `critical_errata_count`: Integer, Not Null, Default 0.
   - `created_at`: DateTime, Not Null.
   - `updated_at`: DateTime, Not Null.

3. **`host_channels`** (Relational table for subscribed software channels)
   - `id`: Integer, Primary Key, Auto-increment.
   - `host_id`: Integer, Foreign Key (`hosts.id`, ondelete `CASCADE`), Indexed.
   - `channel_label`: String(128), Not Null.
   - `channel_name`: String(255), Not Null.

4. **`host_packages`** (Relational table for installed packages per host)
   - `id`: Integer, Primary Key, Auto-increment.
   - `host_id`: Integer, Foreign Key (`hosts.id`, ondelete `CASCADE`), Indexed.
   - `package_name`: String(128), Not Null, Indexed.
   - `package_version`: String(64), Not Null.
   - `package_release`: String(64), Not Null.
   - `package_arch`: String(32), Not Null.

5. **`errata_advisories`** (Security advisories and CVEs from SUSE MLM)
   - `id`: Integer, Primary Key, Auto-increment.
   - `advisory_name`: String(128), Unique, Not Null, Indexed (e.g. `SUSE-SU-2026:1042-1`).
   - `advisory_type`: String(32), Not Null (e.g. `Security Advisory`, `Bug Fix`, `Enhancement`).
   - `severity`: String(32), Not Null (`Critical`, `Important`, `Moderate`, `Low`).
   - `synopsis`: String(512), Not Null.
   - `cve_identifier`: String(128), Nullable, Indexed (e.g. `CVE-2026-2144`).
   - `issued_date`: DateTime, Not Null.

6. **`host_missing_errata`** (Join table linking hosts to missing errata)
   - `id`: Integer, Primary Key, Auto-increment.
   - `host_id`: Integer, Foreign Key (`hosts.id`, ondelete `CASCADE`), Indexed.
   - `errata_id`: Integer, Foreign Key (`errata_advisories.id`, ondelete `CASCADE`), Indexed.
   - `detected_at`: DateTime, Not Null.

7. **`compliance_frameworks`**
   - `id`: Integer, Primary Key, Auto-increment.
   - `name`: String(64), Unique, Not Null (e.g. `CIS SLES 15 Benchmark`, `HIPAA Security Baseline`, `PCI-DSS v4.0`).
   - `code`: String(32), Unique, Not Null (e.g. `CIS_SLES_15`, `HIPAA`, `PCI_DSS_V4`).
   - `version`: String(32), Not Null.
   - `description`: String(512), Not Null.
   - `rule_count`: Integer, Not Null, Default 0.

8. **`compliance_rules`**
   - `id`: Integer, Primary Key, Auto-increment.
   - `framework_id`: Integer, Foreign Key (`compliance_frameworks.id`, ondelete `CASCADE`), Indexed.
   - `rule_identifier`: String(64), Not Null, Indexed (e.g. `CIS-1.1.1.1`, `PCI-8.2.3`).
   - `title`: String(255), Not Null.
   - `description`: String(1024), Not Null.
   - `severity`: String(32), Not Null (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
   - `remediation_instructions`: String(1024), Not Null.
   - `check_type`: String(64), Not Null (`PACKAGE_REQUIRED`, `PACKAGE_PROHIBITED`, `CONFIG_PROPERTY`, `ERRATA_ABSENT`, `SERVICE_STATE`).
   - `check_target`: String(255), Not Null.
   - `expected_value`: String(255), Not Null.

9. **`compliance_scans`**
   - `id`: Integer, Primary Key, Auto-increment.
   - `framework_id`: Integer, Foreign Key (`compliance_frameworks.id`, ondelete `CASCADE`), Indexed.
   - `initiated_by_user_id`: Integer, Foreign Key (`users.id`, ondelete `SET NULL`), Nullable.
   - `scan_status`: String(32), Not Null (`PENDING`, `RUNNING`, `COMPLETED`, `FAILED`).
   - `hosts_scanned_count`: Integer, Not Null, Default 0.
   - `passed_rules_count`: Integer, Not Null, Default 0.
   - `failed_rules_count`: Integer, Not Null, Default 0.
   - `overall_score`: Float, Not Null, Default 0.0.
   - `started_at`: DateTime, Not Null.
   - `completed_at`: DateTime, Nullable.

10. **`compliance_findings`**
    - `id`: Integer, Primary Key, Auto-increment.
    - `scan_id`: Integer, Foreign Key (`compliance_scans.id`, ondelete `CASCADE`), Indexed.
    - `host_id`: Integer, Foreign Key (`hosts.id`, ondelete `CASCADE`), Indexed.
    - `rule_id`: Integer, Foreign Key (`compliance_rules.id`, ondelete `CASCADE`), Indexed.
    - `status`: String(32), Not Null (`PASS`, `FAIL`, `ERROR`, `SKIPPED`).
    - `observed_value`: String(255), Not Null.
    - `finding_details`: String(1024), Not Null.
    - `detected_at`: DateTime, Not Null.

11. **`agent_analyses`** (Autonomous agent reasoning sessions)
    - `id`: Integer, Primary Key, Auto-increment.
    - `host_id`: Integer, Foreign Key (`hosts.id`, ondelete `CASCADE`), Indexed.
    - `framework_id`: Integer, Foreign Key (`compliance_frameworks.id`, ondelete `CASCADE`), Indexed.
    - `analysis_status`: String(32), Not Null (`ANALYZING`, `PLAN_GENERATED`, `COMPLETED`, `FAILED`).
    - `drift_detected`: Boolean, Not Null, Default False.
    - `root_cause_summary`: String(1024), Not Null.
    - `created_at`: DateTime, Not Null.

12. **`agent_thought_steps`** (Step-by-step reasoning traces for transparency)
    - `id`: Integer, Primary Key, Auto-increment.
    - `analysis_id`: Integer, Foreign Key (`agent_analyses.id`, ondelete `CASCADE`), Indexed.
    - `step_order`: Integer, Not Null.
    - `thought_type`: String(64), Not Null (`OBSERVATION`, `CORRELATION`, `RISK_EVALUATION`, `DECISION`).
    - `thought_content`: String(1024), Not Null.
    - `created_at`: DateTime, Not Null.

13. **`remediation_plans`** (Staged remediation proposals with human approval gates)
    - `id`: Integer, Primary Key, Auto-increment.
    - `analysis_id`: Integer, Foreign Key (`agent_analyses.id`, ondelete `SET NULL`), Nullable.
    - `host_id`: Integer, Foreign Key (`hosts.id`, ondelete `CASCADE`), Indexed.
    - `title`: String(255), Not Null.
    - `status`: String(32), Not Null (`DRAFT`, `STAGED`, `APPROVED`, `REJECTED`, `IN_PROGRESS`, `COMPLETED`, `FAILED`).
    - `risk_level`: String(32), Not Null (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
    - `total_steps_count`: Integer, Not Null, Default 0.
    - `approved_by_user_id`: Integer, Foreign Key (`users.id`, ondelete `SET NULL`), Nullable.
    - `approval_notes`: String(512), Nullable.
    - `created_at`: DateTime, Not Null.
    - `executed_at`: DateTime, Nullable.

14. **`remediation_steps`** (Concrete actions to be dispatched via SUSE MLM)
    - `id`: Integer, Primary Key, Auto-increment.
    - `plan_id`: Integer, Foreign Key (`remediation_plans.id`, ondelete `CASCADE`), Indexed.
    - `step_number`: Integer, Not Null.
    - `action_type`: String(64), Not Null (`APPLY_ERRATA`, `INSTALL_PACKAGE`, `REMOVE_PACKAGE`, `SET_CONFIG_PARAMETER`, `RESTART_SERVICE`).
    - `target_package_or_errata`: String(255), Not Null.
    - `parameters`: String(512), Not Null.
    - `status`: String(32), Not Null (`QUEUED`, `DISPATCHED`, `RUNNING`, `SUCCESS`, `FAILED`, `SKIPPED`).
    - `mlm_action_id`: Integer, Nullable.
    - `execution_log`: String(1024), Nullable.

15. **`audit_logs`** (Immutable operational and security log)
    - `id`: Integer, Primary Key, Auto-increment.
    - `user_id`: Integer, Foreign Key (`users.id`, ondelete `SET NULL`), Nullable.
    - `user_username`: String(64), Not Null.
    - `action`: String(128), Not Null, Indexed.
    - `resource_type`: String(64), Not Null.
    - `resource_id`: String(64), Not Null.
    - `details`: String(1024), Not Null.
    - `ip_address`: String(64), Not Null.
    - `timestamp`: DateTime, Not Null, Indexed.

---

## 9. Security
- **Authentication:** JWT Bearer tokens signed with HS256 algorithm and configured expiration (`ACCESS_TOKEN_EXPIRE_MINUTES = 480`).
- **Authorization / RBAC:** Granular endpoint permissions based on roles:
  - `Admin`: Full access (system settings, user management, remediation approval/execution, scan trigger, report generation).
  - `Security_Officer`: Scan triggers, agent analysis, remediation plan approval/creation, reports, and audit logs.
  - `Operator`: View inventory, trigger scans, request agent analysis, execute approved plans.
  - `Auditor`: Read-only access to inventory, scans, findings, reports, and immutable audit logs.
- **Input Validation:** Strict Pydantic models with typed fields, regex validations for hostnames and identifiers.
- **Secrets Management:** Credentials read from environment variables; passwords hashed with bcrypt salt.
- **SQL Injection Prevention:** 100% parameterized queries via SQLAlchemy ORM.
- **Audit Logging:** Every user action (login, scan trigger, approval, rejection, execution) logged to `audit_logs` table.

---

## 10. Scalability & 11. Performance
- **Fleet Scale:** Supports scanning fleets of 5,000+ hosts using batched asynchronous evaluation.
- **Database Indexing:** Indexed foreign keys and search columns (`hostname`, `compliance_status`, `timestamp`, `advisory_name`).
- **Response Latency:** Sub-200ms p95 response time on API endpoints.
- **Streaming Exports:** Large CSV and PDF reports generated via memory-efficient streaming.

---

## 12. Error Handling & Resilience
- **SUSE MLM Client Resilience:** Exponential backoff retries on transient connection timeouts. Graceful fallback to offline/cached state with explicit status indicators.
- **Atomic Operations:** Compliance scans and remediation plan transitions execute within database transaction contexts.
- **Centralized Exception Handler:** FastAPI global exception handler mapping HTTP status codes (400, 401, 403, 404, 422, 500) with uniform error schemas: `{"detail": "Clear error message"}`.

---

## 13. Observability
- **Health Endpoint:** `GET /api/v1/health` verifying application, database connection, and MLM adapter status.
- **Structured Logging:** Timestamps, log levels, request methods, paths, and status codes.
- **Audit Events:** All security and remediation state transitions saved to the relational `audit_logs` table.

---

## 14. Testing Strategy (Backend, Frontend, User Stories)

### Backend Tests (Pytest)
- **Unit Tests:** Password hashing, JWT token creation/decoding, rule evaluation logic, agent drift scoring, report builders.
- **Integration Tests:** Database transactions, SQLAlchemy model relationships and cascade deletions, MLM client adapter live/mock calls.
- **API Tests:** All `/api/v1/*` endpoints testing valid requests (200/201/202), invalid inputs (400/422), unauthorized requests (401/403).
- **Security Tests:** Role-based access control matrix enforcement, SQL injection and XSS input sanitization.
- **Performance & Failure Tests:** Batch host processing under concurrency, MLM timeout handling, and partial failure rollback.

### Frontend Tests & Automated Playwright E2E Browser Tests
- **Automated Playwright Journey 1 (Auth & Navigation):** Login as Admin/Security Officer, verify token storage, navigate through all views, verify route protection and unauthenticated redirects.
- **Automated Playwright Journey 2 (Host Inventory & Sync):** View host fleet, filter by compliance status, trigger inventory sync, inspect host package/errata detail.
- **Automated Playwright Journey 3 (Compliance Audit & Agent Reasoning):** Trigger CIS Benchmark scan, inspect compliance gauge, open Agent Console, watch multi-step agent reasoning stream.
- **Automated Playwright Journey 4 (Controlled Remediation Approval & Execution):** Inspect staged remediation plan, click Approve in modal, trigger execution, observe progress and post-remediation verification scan.
- **Automated Playwright Journey 5 (Reporting & Audit Logs):** Filter compliance report, trigger PDF/CSV downloads, verify immutable audit log records.

---

## 15. Test Cases & User Story Verification Matrix

| ID | Scenario | Expected Result | Type | Layer |
|---|---|---|---|---|
| TC-001 | Valid user authentication (POST /api/v1/auth/login) | 200 OK with valid JWT access token and user role | Unit/API | Backend |
| TC-002 | Invalid credentials submitted to login | 401 Unauthorized with descriptive error detail | API/Security | Backend |
| TC-003 | Unauthorized request to protected endpoint without token | 401 Unauthorized | Security | Backend |
| TC-004 | Auditor attempts to execute remediation (RBAC check) | 403 Forbidden | Security | Backend |
| TC-005 | SUSE MLM Inventory Sync endpoint (POST /api/v1/hosts/sync) | 202 Accepted, hosts and packages synchronized | Integration/API | Backend |
| TC-006 | Trigger compliance scan against CIS Framework | 202 Accepted, scan completes, findings recorded | Integration/API | Backend |
| TC-007 | Autonomous agent reasoning analysis on non-compliant host | 200 OK, reasoning steps generated, staged plan created | Unit/Integration | Backend |
| TC-008 | Approve staged remediation plan (POST .../approve) | 200 OK, plan status transitions to APPROVED | API | Backend |
| TC-009 | Reject staged remediation plan with reason | 200 OK, plan status transitions to REJECTED | API | Backend |
| TC-010 | Execute approved remediation plan via MLM adapter | 202 Accepted, steps dispatched, verification scan run | Integration/API | Backend |
| TC-011 | Generate and export PDF compliance report | 200 OK with `application/pdf` binary stream | API | Backend |
| TC-012 | Generate and export CSV compliance report | 200 OK with `text/csv` stream | API | Backend |
| TC-013 | Database cascade delete on host deletion | Cascade deletes host packages, findings, remediation plans | Integration | Backend |
| TC-014 | SQL Injection payload in search query parameter | Input sanitized, 200 OK with empty result, no SQL error | Security | Backend |
| TC-015 | Health check endpoint verification (GET /api/v1/health) | 200 OK with status `healthy` and DB `connected` | API | Backend |
| TC-016 | E2E Browser: Login flow and route protection | Form submits, token saved, redirects to dashboard | E2E | Frontend |
| TC-017 | E2E Browser: Host list, search, and detail modal | Host renders, search filters list, detail shows packages | E2E | Frontend |
| TC-018 | E2E Browser: Compliance scan trigger and live gauge update | Scan runs, gauge updates with score, findings list shown | E2E | Frontend |
| TC-019 | E2E Browser: Agent Console reasoning stream inspection | Step-by-step reasoning steps visible with thought badges | E2E | Frontend |
| TC-020 | E2E Browser: Remediation approval modal & execution | Approval notes input, executes, progress bar completes | E2E | Frontend |
| TC-021 | E2E Browser: Report generation and download trigger | Download initiated without broken console errors | E2E | Frontend |
| TC-022 | Empty state rendering across tables and search queries | Clean empty state message rendered without UI crashes | Unit/Integration | Frontend |

---

## 16. Edge Cases
- **Unreachable MLM API Server:** Circuit breaker / timeout fallback ensures app remains operational and reports clear status.
- **Conflicting Errata Dependencies:** Agent detects missing dependency channels and flags steps as `BLOCKED` rather than failing blindly.
- **Concurrent Plan Approvals:** Database row locking prevents duplicate execution of the same remediation plan.
- **Large Inventory Datasets (5,000+ packages/host):** Bulk SQL inserts with batch chunking to avoid query parameter overflow.
- **Empty Host / Scan Filters:** Returns empty array `[]` with count `0` rather than 500 error.

---

## 17. Deployment
- **Containerization:** Multi-stage `Dockerfile` for Backend (Python 3.11-slim) and Frontend (Node 20-alpine build + Nginx/Vite preview).
- **Compose Orchestration:** `docker-compose.yml` defining `backend`, `frontend`, and `db` (PostgreSQL 16) on isolated bridge network.
- **Environment Configuration:** `.env` file for database credentials, JWT secret key, and MLM API endpoint.

---

## 18. CI/CD & 19. Compatibility
- **Testing Gates:** Pytest for backend tests, ESLint / build checks for React, and Playwright for E2E tests.
- **OS Support:** Linux (SLES 15, RHEL 8/9, openSUSE Leap, Ubuntu 22.04+).
- **Browser Support:** Chrome, Firefox, Safari, Edge (Evergreen modern browsers).

---

## 20. Migration / Upgrade Plan & 21. Risks & Trade-offs
| Risk | Impact | Probability | Mitigation |
|---|---|---|---|
| SUSE MLM API endpoint unavailable during audit | Medium | Medium | Implement robust offline mock/cache adapter and retry policy |
| Errata remediation causes unexpected host package conflicts | High | Low | Agent checks dependencies prior to staging; strict human approval gate |
| Schema performance with high volume of findings | Medium | Low | Composite indexes on `(scan_id, host_id)` and `(framework_id, status)` |

---

## 22. Open Questions
- None. Requirements and architecture are fully derived and normalized.

---

## 23. Implementation Plan

### Phase 1: Workspace Setup, Database Models, and SUSE MLM Integration Adapter
- Scaffolding project directory structure and environment files.
- Setting up PostgreSQL database engine, connection pooling, and normalized SQLAlchemy models (100% zero-JSON schema).
- Implementing SUSE Multi-Linux Manager API client (`suse_mlm_client.py`) with authentication, system discovery, package listing, and errata queries.
- Creating seed data for users, default compliance frameworks (CIS, HIPAA, PCI-DSS), and sample hosts.
- Implementing authentication, host inventory endpoints, and Unit/API test suites for Phase 1.

### Phase 2: Compliance Evaluation Engine & Autonomous Agent Engine
- Building compliance rule evaluator supporting package, configuration, errata, and service checks.
- Developing Autonomous Agent Engine (`agent_engine.py`) with drift detection, multi-step reasoning traces (`agent_thought_steps`), and posture analysis.
- Implementing API routes for triggering scans, viewing findings, and running agent analysis.
- Unit and integration tests for compliance engine, agent reasoning, and edge cases.

### Phase 3: Controlled Remediation Engine, Report Generation, and Security/Audit Logging
- Developing Remediation Service (`remediation_service.py`) supporting plan creation, risk calculation, human approval/rejection gates, and execution dispatch via MLM.
- Building Report Service (`report_service.py`) with PDF (ReportLab) and CSV generation endpoints.
- Implementing RBAC middleware and immutable `audit_logs` service.
- Comprehensive backend test validation (API, Security, Performance, and Failure tests).

### Phase 4: React Enterprise Frontend & Automated Playwright E2E Browser Verification
- Developing modern React SPA with Tailwind CSS (Dashboard, Hosts, Host Detail, Scans, Agent Console, Remediation Manager, Reports, Audit Logs).
- Integrating frontend with backend REST APIs, JWT auth context, and real-time polling.
- Authoring and executing automated Playwright E2E browser tests across all critical user journeys.
- Creating production-grade root `README.md` and `docs/APPLICATION_DOCUMENTATION.md` alongside phase logs.

---

## 24. Definition of Done
- [ ] Requirements FR-001 through FR-009 fully implemented.
- [ ] 100% normalized relational database schema with zero JSON/JSONB fields.
- [ ] Backend test suite passing (Unit, Integration, API, Security, Performance).
- [ ] React frontend built, styled, and connected to all endpoints.
- [ ] Automated Playwright E2E browser tests passing against live frontend/backend.
- [ ] Root `README.md` and `docs/APPLICATION_DOCUMENTATION.md` created.
- [ ] Phase documentation generated in `docs/PHASE_*.md`.
- [ ] Docker compose configuration verified for one-command startup.

---

## 25. Post-Implementation Verification
- Verification of `/api/v1/health` returning status `healthy`.
- Verification of inventory synchronization from SUSE MLM adapter.
- Full compliance scan execution and score calculation.
- Staged remediation approval and mock/live dispatch verification.
- PDF and CSV report download verification.
- Playwright E2E test execution with 100% pass rate.

---

## 26. Existing Codebase Analysis
- **Existing System:** Greenfield directory inside `/home/shreya/compliance-agent/` containing `prd.md` and `Hermes-Manual.md`.
- **DO NOT Change:** The root workflow contracts in `Hermes-Manual.md` and functional objectives in `prd.md`.
- **Reuse:** Standard Python 3.11, FastAPI, SQLAlchemy, React 18, and Playwright tooling.

---

## 27. Implementation Constraints
- Strict adherence to normalized schema without JSON/JSONB columns.
- Native bcrypt for password hashing (`bcrypt.hashpw` / `bcrypt.checkpw`).
- Node 20+ compatibility for frontend tooling.
- Mandatory automated Playwright E2E test suite.
- Absolute paths within `/home/shreya/compliance-agent/`.

---

## 28. Acceptance Criteria
- **AC-001 (Authentication & RBAC):** User can log in with valid credentials, receive a JWT token, and access role-permitted views; unauthorized requests receive HTTP 401/403.
- **AC-002 (MLM Inventory Sync):** System synchronizes host details, subscribed channels, installed packages, and missing errata from SUSE MLM API.
- **AC-003 (Compliance Audits):** System evaluates hosts against CIS, HIPAA, or PCI-DSS frameworks, records individual rule findings, and calculates compliance scores.
- **AC-004 (Autonomous Agent Reasoning):** Agent analyzes non-compliant hosts, outputs multi-step reasoning thoughts, detects drift, and stages a remediation plan.
- **AC-005 (Controlled Approval Gate):** Remediation plans cannot be executed until an Admin or Security Officer explicitly approves them.
- **AC-006 (Remediation Execution):** Executed plans dispatch actions to SUSE MLM, track step status, and trigger an automatic verification audit.
- **AC-007 (Audit-Ready Reporting):** System exports formatted multi-page PDF and CSV compliance dossiers on demand.
- **AC-008 (Audit Trail):** All user actions and agent decisions are immutably logged with timestamps and actor identities.
