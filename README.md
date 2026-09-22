# SUSE MLM Security & Compliance Agent

[![FastMCP](https://img.shields.io/badge/FastMCP-v1.0-emerald)](https://github.com/jlowin/fastmcp)
[![LangGraph](https://img.shields.io/badge/LangGraph-Stateful%20Agent-blue)](https://github.com/langchain-ai/langgraph)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-teal)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.2-cyan)](https://reactjs.org)
[![Playwright](https://img.shields.io/badge/Playwright-E2E%20Verified-green)](https://playwright.dev)

An autonomous, agentic security and compliance application that connects to **SUSE Multi-Linux Manager (MLM) / Uyuni** via a dedicated **Model Context Protocol (MCP)** server. Built with LangGraph, FastAPI, React, and PostgreSQL, the platform audits registered servers using native OpenSCAP benchmark profiles and errata channels, provides an interactive streaming chat interface with collapsible reasoning traces, generates certified compliance reports (PDF, CSV, JSON), and orchestrates approved remediations with fail-closed Human-in-the-Loop safeguards.

---

## 1. System Architecture

```
+------------------------------------------------------------------------------------+
|                                React Frontend (Vite)                              |
|  [Chat Stream & Traces]  [Approval Cards]  [Compliance Dashboard]  [Report Center] |
+------------------------------------------+-----------------------------------------+
                                           | HTTP / SSE / WebSocket (:3000 / :3030)
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

---

## 2. Component & Port Inventory

| Service | Component | Port | Description |
|---|---|---|---|
| **Frontend** | React + Vite + Tailwind CSS | `3000` / `3030` | Conversational compliance chat, fleet posture, report viewer |
| **Backend API** | FastAPI + Uvicorn | `8000` / `8030` | Core REST APIs, SSE chat stream, LangGraph runtime |
| **FastMCP Server** | Python FastMCP (`suse-mlm-security`) | Internal / `8001` | 12 typed MCP tools wrapping SUSE MLM XML-RPC endpoints |
| **Database** | PostgreSQL 15 / aiosqlite | `5432` | Normalized relational models with **0 JSON/JSONB columns** |

---

## 3. User Roles & Access Control Matrix

| Role | Permissions & Operational Scope |
|---|---|
| **SecOps Lead / Administrator** | Full access: View fleet posture, execute compliance queries, approve/reject remediation proposals, export reports. |
| **Security Auditor** | Read-only access: Query OpenSCAP scan results, inspect CVE errata, download certified compliance reports. |
| **Autonomous Agent (LangGraph)** | Execution scope: Query inventory/scans via FastMCP; state-modifying patch actions halted at `interrupt` gate. |

---

## 4. Quickstart Guide (Docker Compose)

Launch the entire stack (PostgreSQL, FastMCP Server, FastAPI Core, React Frontend) with one command:

```bash
docker compose up -d --build
```

Access services:
- **Web UI & Chat Console:** `http://localhost:3000`
- **FastAPI OpenAPI Documentation:** `http://localhost:8000/api/v1/docs`
- **Health Checks:** `http://localhost:8000/health/ready`

---

## 5. Local Development Setup

### Backend & FastMCP Setup
```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Install dependencies
pip install -r backend/requirements.txt
pip install -r mcp_server/requirements.txt

# 3. Launch FastMCP & FastAPI backend
PYTHONPATH=. uvicorn backend.app.main:app --port 8030 --reload
```

### Frontend Setup
```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies & launch dev server
npm install
npm run dev -- --port 3030
```

---

## 6. Comprehensive Test Suite Execution

### Backend & FastMCP Unit/Integration Tests
```bash
PYTHONPATH=. pytest backend/tests/ mcp_server/tests/ -v -o asyncio_mode=auto
```

### Frontend Automated Playwright E2E Tests
```bash
cd frontend
npx playwright test
```

---

## 7. Implementation Phase Documentation
- [Phase 1 — FastMCP Server Core & SUSE MLM Integration](docs/PHASE_1_MCP_SERVER.md)
- [Phase 2 — LangGraph Agent Engine & FastAPI Core](docs/PHASE_2_LANGGRAPH_BACKEND.md)
- [Phase 3 — React Conversational UI & Dashboard](docs/PHASE_3_REACT_FRONTEND.md)
- [Phase 4 — Server Reporting Engine & E2E Verification](docs/PHASE_4_REPORTING_VERIFICATION.md)
- [Comprehensive Application Specification](docs/APPLICATION_DOCUMENTATION.md)
