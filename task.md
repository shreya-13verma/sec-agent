# TASK.md

Progress tracker for SUSE MLM Security & Compliance Agent, derived from plan.md Section 23.
Legend: [ ] not started · [x] done

## Phase 1 — Workspace Setup, Database Models, and SUSE MLM Integration Adapter
- [ ] Initialize project structure under `/home/shreya/compliance-agent/` (backend, frontend, e2e, docs) (covers Section 5)
- [ ] Configure environment variables, settings, and database connection pool in `backend/app/config.py` and `database.py` (covers FR-001, TC-015)
- [ ] Define normalized SQLAlchemy models (100% zero-JSON schema) in `backend/app/models/` (covers Section 8, TC-013)
- [ ] Define Pydantic v2 validation schemas in `backend/app/schemas/` (covers Section 7)
- [ ] Implement password hashing and JWT authentication utilities in `backend/app/utils/security.py` (covers FR-009, TC-001, TC-002, AC-001)
- [ ] Implement SUSE Multi-Linux Manager (MLM) API Client Adapter in `backend/app/services/suse_mlm_client.py` (covers FR-001, FR-002, TC-005, AC-002)
- [ ] Create database seed script with default compliance frameworks (CIS, HIPAA, PCI-DSS), rules, demo hosts, and admin users in `backend/app/utils/seed_data.py` (covers FR-003)
- [ ] Implement Auth and Hosts API routers in `backend/app/routers/auth.py` and `hosts.py` (covers FR-001, FR-009, TC-001, TC-005)
- [ ] Write and run Phase 1 Unit and Integration tests for models, auth, and MLM adapter (covers TC-001, TC-002, TC-003, TC-005, TC-013, TC-015)

## Phase 2 — Compliance Evaluation Engine & Autonomous Agent Engine
- [ ] Implement Compliance Evaluation Engine in `backend/app/services/compliance_engine.py` (covers FR-003, TC-006, AC-003)
- [ ] Implement Autonomous Agent Core in `backend/app/services/agent_engine.py` with multi-step reasoning traces and drift detection (covers FR-004, TC-007, AC-004)
- [ ] Implement Compliance and Agent API routers in `backend/app/routers/compliance.py` and `agent.py` (covers FR-003, FR-004, TC-006, TC-007)
- [ ] Implement query filtering, search, and pagination for findings and compliance scans (covers Section 7, TC-006, TC-014)
- [ ] Write and run Phase 2 Unit and Integration tests for compliance evaluation, score calculation, and agent reasoning traces (covers TC-006, TC-007, TC-014)

## Phase 3 — Controlled Remediation Engine, Report Generation, and Security/Audit Logging
- [ ] Implement Controlled Remediation Service in `backend/app/services/remediation_service.py` with human approval/rejection gates (covers FR-005, FR-006, TC-008, TC-009, TC-010, AC-005, AC-006)
- [ ] Implement Report Generator in `backend/app/services/report_service.py` supporting PDF (ReportLab) and CSV exports (covers FR-008, TC-011, TC-012, AC-007)
- [ ] Implement Audit Logging Service and Router in `backend/app/services/audit_service.py` and `routers/audit_logs.py` (covers FR-007, AC-008)
- [ ] Implement Remediation and Reports API routers in `backend/app/routers/remediation.py` and `reports.py` (covers FR-005, FR-006, FR-008, TC-008, TC-009, TC-010, TC-011, TC-012)
- [ ] Implement RBAC authorization middleware and permission checks (covers FR-009, TC-003, TC-004)
- [ ] Write and run Phase 3 backend test suite covering remediation, reporting, RBAC, and error handling (covers TC-003, TC-004, TC-008, TC-009, TC-010, TC-011, TC-012, TC-014)

## Phase 4 — React Enterprise Frontend & Automated Playwright E2E Browser Verification
- [ ] Scaffold React 18 + Vite frontend with Tailwind CSS and Lucide icons in `frontend/` (covers Section 5)
- [ ] Implement API client, Auth Context, and route guards in `frontend/src/api/` and `context/` (covers Section 5, TC-016)
- [ ] Implement reusable UI components (Layout, Navbar, Sidebar, StatCard, ComplianceGauge, StatusBadge, Modal, Toast) in `frontend/src/components/` (covers Section 5)
- [ ] Implement Login, Dashboard, Hosts, and Host Detail pages in `frontend/src/pages/` (covers US-001, TC-016, TC-017)
- [ ] Implement Compliance Scans, Agent Console, Remediation Manager, Reports, Audit Logs, and Settings pages (covers US-001, US-002, US-003, US-004, TC-018, TC-019, TC-020, TC-021, TC-022)
- [ ] Set up Playwright E2E browser test configuration and test suites in `e2e/` (covers Section 14, TC-016 through TC-022)
- [ ] Execute automated Playwright E2E browser tests against live frontend/backend services (covers Step 8.1, TC-016 through TC-022)
- [ ] Author industry-grade root `README.md` and `docs/APPLICATION_DOCUMENTATION.md` along with phase logs `docs/PHASE_*.md` (covers Step 6)
- [ ] Create and verify `docker-compose.yml` multi-container build and orchestration (covers Section 17)
