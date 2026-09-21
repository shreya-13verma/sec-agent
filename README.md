# SUSE MLM Security & Compliance Agent

An autonomous, agentic security and compliance platform integrating with **SUSE Multi-Linux Manager (MLM)** (`https://10.0.33.56/rhn/apidoc/index.jsp`) to audit registered Linux infrastructure against regulatory and hardening standards (CIS Benchmarks, HIPAA Security Rule, PCI-DSS v4.0), autonomously detect configuration and errata drift, synthesize multi-step remediation plans, generate executive compliance dossiers (PDF & CSV), and safely dispatch controlled remediations with human approval boundaries.

---

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    React 18 + Tailwind SPA Dashboard                    │
│  (Fleet Posture, Host Inventory, Audits, Agent Console, Remediations)   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ HTTPS / REST / JWT Auth
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          FastAPI Backend Core                           │
│  ┌──────────────────────┬──────────────────────┬─────────────────────┐  │
│  │ Auth & RBAC Router   │ Host & Sync Router   │ Compliance Router   │  │
│  ├──────────────────────┼──────────────────────┼─────────────────────┤  │
│  │ Agent Engine Router  │ Remediation Router   │ Reports & Audit Log │  │
│  └──────────────────────┴──────────────────────┴─────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                 Autonomous Agent Reasoning Engine                 │  │
│  │  [Observation] ➔ [Correlation] ➔ [Risk Assessment] ➔ [Decision]  │  │
│  └──────────────────────────────────┬────────────────────────────────┘  │
│  ┌──────────────────────────────────┴────────────────────────────────┐  │
│  │               SUSE Multi-Linux Manager API Adapter                │  │
│  │      (XML-RPC / REST Session Manager, Errata & Package RPC)       │  │
│  └──────────────────────────────────┬────────────────────────────────┘  │
└───────────────────┬─────────────────┼───────────────────────────────────┘
                    │                 │
                    ▼                 ▼
     ┌────────────────────────┐  ┌────────────────────────────────────────┐
     │ PostgreSQL 16 Database │  │   SUSE Multi-Linux Manager (MLM)       │
     │ (100% Normalized Zero- │  │       (Target: 10.0.33.56)             │
     │   JSON Relational DB)  │  │ (Registered SLES, RHEL, openSUSE hosts)│
     └────────────────────────┘  └────────────────────────────────────────┘
```

---

## 2. Component & Port Inventory

| Service | Technology | Port | Purpose |
|---|---|---|---|
| **Frontend UI** | React 18, Vite, Tailwind CSS | `3000` (Dev: `8081`) | Security management console, agent thought visualization & audit reports |
| **Backend API** | FastAPI (Python 3.11), SQLAlchemy | `8000` (Dev: `8080`) | Core REST API, autonomous reasoning engine, MLM adapter, PDF/CSV generator |
| **Database** | PostgreSQL 16 (or SQLite in-memory) | `5432` | 100% normalized relational storage for hosts, errata, rules, findings & audit logs |
| **SUSE MLM Integration** | XML-RPC / REST API | `443` (`10.0.33.56`) | Upstream SUSE Multi-Linux Manager endpoint for package & errata orchestration |

---

## 3. User Roles & RBAC Matrix

| Role | Default User | Permissions |
|---|---|---|
| **Admin** | `admin` / `admin123` | Full administrative control: user provisioning, system settings, host management, scan triggering, plan approval, and execution. |
| **Security_Officer** | `sec_officer` / `sec123` | Compliance scanning, autonomous agent analysis, remediation plan approval/rejection, reporting, and audit logs. |
| **Operator** | `operator` / `op123` | Inventory sync, scan triggering, requesting agent reasoning, and executing approved remediation plans. |
| **Auditor** | `auditor` / `audit123` | Read-only access to host posture, compliance findings, executive reports, and immutable audit trails. (Forbidden from approving/executing actions). |

---

## 4. Quickstart Guide (Docker Compose)

Launch the entire multi-service stack with a single command:

```bash
docker compose up -d --build
```

- **Frontend Console:** `http://localhost:3000`
- **Backend API & OpenAPI Docs:** `http://localhost:8000/docs`
- **Health Check Endpoint:** `http://localhost:8000/health`

---

## 5. Local Development Setup

### Backend Setup
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start backend server
uvicorn backend.app.main:app --host 127.0.0.1 --port 8080 --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
# Accessible at http://localhost:8081
```

---

## 6. Test Suites & Verification Coverage

### Running Backend Tests (28 Test Cases)
```bash
source .venv/bin/activate
pytest -v backend/tests
```

### Running Automated Playwright Browser E2E Tests (10 Test Cases)
```bash
cd e2e
npx playwright test
```

### Test Suite Coverage Summary

| Test ID | Description | Layer | Result |
|---|---|---|---|
| **TC-001** | Valid user authentication (JWT generation) | Backend API | **PASS** |
| **TC-002** | Invalid password / non-existent user handling | Backend Security | **PASS** |
| **TC-003** | Route protection & unauthenticated rejection | Backend Security | **PASS** |
| **TC-004** | Auditor role forbidden from approval/execution | Backend RBAC | **PASS** |
| **TC-005** | SUSE MLM host inventory & errata synchronization | Backend Integration | **PASS** |
| **TC-006** | Compliance scan execution against CIS / HIPAA | Backend Engine | **PASS** |
| **TC-007** | Autonomous agent multi-step reasoning & plan staging | Backend Engine | **PASS** |
| **TC-008** | Staged remediation plan approval lifecycle | Backend API | **PASS** |
| **TC-009** | Remediation plan rejection with stated reason | Backend API | **PASS** |
| **TC-010** | Approved remediation execution & verification scan | Backend Integration | **PASS** |
| **TC-011** | PDF executive compliance dossier generation | Backend Reporting | **PASS** |
| **TC-012** | CSV fleet posture and errata report export | Backend Reporting | **PASS** |
| **TC-013** | Database foreign key cascade deletion | Database / ORM | **PASS** |
| **TC-014** | SQL injection protection on query parameters | Backend Security | **PASS** |
| **TC-015** | Application and database health verification | Backend API | **PASS** |
| **TC-016** | Playwright E2E: Login, session persistence & route guards | Frontend Browser | **PASS** |
| **TC-017** | Playwright E2E: Host search, filter, and tab navigation | Frontend Browser | **PASS** |
| **TC-018** | Playwright E2E: Triggering fleet scan & findings breakdown | Frontend Browser | **PASS** |
| **TC-019** | Playwright E2E: Agent reasoning stream inspection | Frontend Browser | **PASS** |
| **TC-020** | Playwright E2E: Controlled remediation approval modal & run | Frontend Browser | **PASS** |
| **TC-021** | Playwright E2E: Reports preview & export buttons | Frontend Browser | **PASS** |
| **TC-022** | Playwright E2E: Audit log inspection & filter controls | Frontend Browser | **PASS** |

---

## 7. Phase Implementation Logs
- [Phase 1 Documentation](docs/PHASE_1_FOUNDATION_AND_MLM_SYNC.md) — Foundation, Normalized Models & MLM Adapter.
- [Phase 2 Documentation](docs/PHASE_2_COMPLIANCE_AND_AGENT_ENGINE.md) — Compliance Evaluation & Autonomous Agent Reasoning.
- [Phase 3 Documentation](docs/PHASE_3_REMEDIATION_AND_REPORTING.md) — Controlled Remediation, ReportLab PDF & Audit Logging.
- [Phase 4 Documentation](docs/PHASE_4_FRONTEND_AND_E2E_VERIFICATION.md) — React Frontend, Playwright E2E Tests & Docker Deployment.
- [Comprehensive Technical Documentation](docs/APPLICATION_DOCUMENTATION.md) — Complete API reference, data models, and lifecycle specifications.
