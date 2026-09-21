# PLAN.md

## 1. Overview
- **Project / Feature Name:** SUSE MLM Security & Compliance Agent (with FastMCP Integration)
- **Problem Statement:** Infrastructure operations and security teams managing Linux server fleets across enterprise environments face significant complexity in maintaining continuous regulatory compliance (CIS Benchmarks, HIPAA, PCI-DSS, STIG), detecting security configuration drift, identifying critical errata/CVEs, and safely orchestrating remediations across hosts registered to SUSE Multi-Linux Manager (MLM). Manual compliance audits are time-consuming, point-in-time, error-prone, and lack autonomous multi-step reasoning for remediation planning and audit trail preservation.
- **Goal:** Deliver an autonomous, agentic security and compliance platform integrating with SUSE Multi-Linux Manager (MLM) via standard Model Context Protocol (FastMCP) tools to continuously audit registered hosts (`hana-node1`, `hana-node2`, `klp-server`, `monitoring-srv`, `rhel10`, `trento-server`, `ubuntu240`), detect drift, perform multi-step agent reasoning for remediation planning, generate executive and technical audit reports (PDF, CSV, web dashboards), and execute safety-bounded, human-approved remediation tasks with complete cryptographic and relational audit trails.
- **Non-Goals:**
  - Replacing SUSE Multi-Linux Manager itself as the primary package mirror or host provisioning daemon.
  - Deploying hypervisor-level firmware updates or out-of-band hardware management outside MLM API capabilities.
  - Unsupervised, fully autonomous execution of destructive kernel re-installations without explicit user approval boundaries.
- **Success Criteria:**
  - FastMCP tool server (`suse_mlm_mcp`) exposing standardized MCP tools for system discovery, package listing, errata queries, and action dispatching.
  - Full discovery and synchronization of real registered systems (`hana-node1`, `hana-node2`, `klp-server`, `monitoring-srv`, `rhel10`, `trento-server`, `ubuntu240`) from SUSE MLM API (`https://10.0.33.56/rpc/api`).
  - Automated compliance evaluation against CIS, HIPAA, PCI-DSS, and hardening standards with score computation across systems.
  - Multi-step autonomous agent engine for root-cause diagnosis, posture analysis, drift detection, and step-by-step remediation plan synthesis using FastMCP tools.
  - Role-gated remediation lifecycle with explicit staging, risk assessment, human approval gate, and execution tracking via MLM actions.
  - Exportable audit-ready reports (PDF and CSV) and interactive real-time React dashboard with sub-second response times.
  - 100% normalized PostgreSQL schema with zero JSON/JSONB fields and exhaustive test coverage (Unit, Integration, API, Security, Performance, and Playwright E2E browser tests).

---

## 2. Requirements

### Functional Requirements
- **FR-001 (SUSE MLM Synchronization & Inventory via FastMCP):** The system shall connect to SUSE Multi-Linux Manager API (`https://10.0.33.56/rpc/api`) via FastMCP tools to authenticate (`admin:linux`), discover, and synchronize real registered systems, OS versions, hardware details, subscribed channels, and installed package inventories.
- **FR-002 (Vulnerability & Errata Tracking):** The system shall ingest, index, and track all live security advisories, bug fixes, enhancement errata, CVE identifiers, and missing package updates per registered host via `suse_mlm_list_applicable_errata` MCP tool.
- **FR-003 (Compliance Framework & Benchmark Engine):** The system shall execute automated compliance scans against standardized frameworks (CIS Benchmarks Level 1/2, HIPAA Security Rule, PCI-DSS v4.0, Linux Hardening Baselines) evaluating configuration rules, required packages, prohibited services, and patch levels against real host inventories.
- **FR-004 (Autonomous Agent Engine & Reasoning Loop):** The system shall provide an autonomous agent engine that utilizes FastMCP tool execution, posture analysis, drift detection, and multi-step reasoning to analyze system vulnerabilities, correlate misconfigurations, determine remediation priorities, and generate structured remediation plans.
- **FR-005 (Controlled Remediation & Approval Gate):** The system shall enforce a strict approval workflow for all remediation plans. No remediation job shall be executed on MLM hosts until an authorized user explicitly approves the staged plan.
- **FR-006 (Remediation Execution & Verification):** The system shall dispatch approved remediation actions (package upgrade, errata application, config enforcement, script execution) via FastMCP action tools, monitor job progress, and trigger automatic post-remediation verification scans.
- **FR-007 (Audit Trail & Historical Snapshots):** The system shall maintain an immutable, relational audit log of every agent reasoning step, scan result, user approval, parameter override, and remediation execution.
- **FR-008 (Reporting & Export):** The system shall generate comprehensive executive summaries, technical compliance reports, drift logs, and remediation audit records with export capabilities in PDF, CSV, and interactive dashboard views.
- **FR-009 (Authentication & Role-Based Access Control):** The system shall provide secure user authentication (JWT) with distinct roles: `Admin`, `Security_Officer`, `Operator`, and `Auditor`.

---

### User Stories & Complete Lifecycle Scenarios

#### US-001 (Security Officer): Discover Infrastructure and Run Baseline Compliance Scans
- **Scenario A (Happy Path - Real Host Discovery & Scan):**
  - *Given* a configured FastMCP connection to SUSE Multi-Linux Manager with real registered hosts (`hana-node1`, `hana-node2`, `klp-server`, `monitoring-srv`, `rhel10`, `trento-server`, `ubuntu240`).
  - *When* the Security Officer clicks "Sync Inventory" and initiates a "CIS Benchmark Level 1" audit on the host fleet.
  - *Then* the backend synchronizes all real host metadata via `suse_mlm_list_systems` and `suse_mlm_list_installed_packages`, evaluates benchmark rules, records individual rule results in `audit_findings`, computes fleet compliance scores, and updates the UI dashboard in real time.

#### US-002 (Operator): Autonomous Agent Reasoning & Remediation Plan Generation
- **Scenario A (Happy Path - Agent Reasoning to Staged Plan via MCP):**
  - *Given* Host `hana-node1` has missing errata (e.g. `SUSE-15-SP7-2026-4264` MozillaFirefox).
  - *When* the user requests "Autonomous Remediation Analysis" for `hana-node1`.
  - *Then* the Autonomous Agent executes its multi-step reasoning loop using FastMCP tools, creates a `remediation_plan` in `STAGED` status with ordered `remediation_steps`, and notifies the user that approval is pending.

#### US-003 (Admin / Security Officer): Review, Approve, and Execute Controlled Remediation
- **Scenario A (Happy Path - Approval and Dispatch via FastMCP):**
  - *Given* a staged remediation plan for `hana-node1`.
  - *When* the Admin approves the plan and clicks "Execute Remediation".
  - *Then* the status changes to `IN_PROGRESS`, the system dispatches actions via `suse_mlm_schedule_apply_errata` MCP tool, polls execution status until completion, and automatically triggers a post-remediation audit scan.

---

### Non-Functional Requirements
- **Performance:** Latency < 200ms for p95 API requests; FastMCP tool call execution < 1.5s for live MLM queries.
- **Scalability:** Support 5,000+ registered hosts and 500,000 historical audit findings.
- **Security:** Native bcrypt password hashing, JWT authorization, FastMCP tool permission boundaries, zero plain-text credentials stored.

---

## 5. Architecture

### Components & Services
- **FastMCP Server (`suse_mlm_mcp`):** FastMCP tool server providing standardized MCP tool interfaces to SUSE Multi-Linux Manager XML-RPC API (`https://10.0.33.56/rpc/api`).
- **Frontend (React SPA):** React 18, Vite, Tailwind CSS, Lucide Icons, Axios, React Router.
- **Backend (FastAPI):** Python 3.11, FastAPI, Pydantic v2, SQLAlchemy 2.0, ReportLab.
- **Database (PostgreSQL 16):** Normalized relational database with indexed queries and zero JSON columns.

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
│  │             FastMCP SUSE Multi-Linux Manager Client               │  │
│  │ (suse_mlm_list_systems, suse_mlm_list_installed_packages, etc.)   │  │
│  └──────────────────────────────────┬────────────────────────────────┘  │
└───────────────────┬─────────────────┼───────────────────────────────────┘
                    │                 │
                    ▼                 ▼
     ┌────────────────────────┐  ┌────────────────────────────────────────┐
     │ PostgreSQL 16 Database │  │   FastMCP Server / SUSE MLM Adapter    │
     │  (Normalized Relational│  │      https://10.0.33.56/rpc/api        │
     │   Zero-JSON Schema)    │  │ (Real Hosts: hana-node1, klp-server,..)│
     └────────────────────────┘  └────────────────────────────────────────┘
```

---

## 6. Technology Decisions
- **FastMCP (`fastmcp` / `mcp`):** Model Context Protocol server exposing standard tool definitions for SUSE MLM operations.
- **Backend Framework:** FastAPI (Python 3.11).
- **Database:** PostgreSQL 16 (100% normalized schema).
- **Frontend Framework:** React 18 + Vite + Tailwind CSS.
- **Testing:** Pytest (Unit & Integration) + Playwright (E2E Browser journeys).

---

## 7. API / Interface Contract (Unchanged, enhanced with FastMCP backend adapter)
- Endpoints remain consistent (`/api/v1/auth`, `/api/v1/hosts`, `/api/v1/compliance`, `/api/v1/agent`, `/api/v1/remediations`, `/api/v1/reports`, `/api/v1/audit-logs`).

---

## 8. Data Model (100% Normalized Zero-JSON Schema Unchanged)
- Entities: `users`, `hosts`, `host_channels`, `host_packages`, `errata_advisories`, `host_missing_errata`, `compliance_frameworks`, `compliance_rules`, `compliance_scans`, `compliance_findings`, `agent_analyses`, `agent_thought_steps`, `remediation_plans`, `remediation_steps`, `audit_logs`.

---

## 23. Implementation Plan

### Phase 1: Foundation, Data Models & MLM Sync (COMPLETED)
### Phase 2: Compliance Engine & Agent Reasoning (COMPLETED)
### Phase 3: Controlled Remediation & Reporting (COMPLETED)
### Phase 4: React UI & Playwright E2E Verification (COMPLETED)
### Phase 5: FastMCP SUSE MLM Server & Real Server Integration (NEW)
- Implement FastMCP server in `backend/app/mcp_server.py` with MCP tools:
  - `suse_mlm_list_systems`
  - `suse_mlm_get_system_details`
  - `suse_mlm_list_installed_packages`
  - `suse_mlm_list_subscribed_channels`
  - `suse_mlm_list_applicable_errata`
  - `suse_mlm_schedule_apply_errata`
  - `suse_mlm_schedule_package_install`
  - `suse_mlm_schedule_package_remove`
- Connect SUSE MLM adapter (`suse_mlm_client.py`) to the real SUSE Multi-Linux Manager endpoint (`https://10.0.33.56/rpc/api` with `admin:linux`).
- Synchronize real registered systems (`hana-node1`, `hana-node2`, `klp-server`, `monitoring-srv`, `rhel10`, `trento-server`, `ubuntu240`).
- Update agent engine and test suites to validate FastMCP tools and real host data.
- Run full regression testing (Backend Pytest + Playwright E2E browser tests).
- Update documentation in `APPLICATION_DOCUMENTATION.md`, `README.md`, and create `docs/PHASE_5_FASTMCP_MLM_INTEGRATION.md`.
- Push to GitHub.

---

## 24. Definition of Done
- [x] Phase 1-4 completed.
- [ ] FastMCP tools implemented and verified against real SUSE MLM endpoint (`10.0.33.56`).
- [ ] Real server fleet synchronized in database.
- [ ] Full backend and Playwright E2E regression suites passing.
- [ ] Documentation updated and committed to GitHub.
