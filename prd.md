# PRD: SUSE MLM Security & Compliance Agent

## 1. Product Summary
An autonomous, agentic security and compliance application that connects to SUSE Multi-Linux Manager (MLM) / Uyuni (`https://10.0.33.56/rhn/apidoc/index.jsp`) via a dedicated Model Context Protocol (MCP) server. Built with LangGraph, FastAPI, React, and PostgreSQL, the platform audits registered servers using native SUSE MLM OpenSCAP profiles and errata channels, provides an interactive chat interface, generates exportable server compliance reports, and orchestrates approved remediations.

---

## 2. Tech Stack & Integration Model
* **Frontend:** React (Chat interface, compliance dashboards, report viewer/downloader)
* **Agent Framework:** LangGraph (Stateful multi-agent workflows, tool routing, memory, and human-in-the-loop approvals)
* **Backend:** FastAPI (Application core, streaming chat endpoints, report generation, and session handling)
* **Tooling / Integration:** FastMCP (Dedicated MCP server wrapping SUSE MLM XML-RPC APIs; the core application interacts with MLM exclusively through this MCP layer)
* **Database:** PostgreSQL (Agent state, scan results, system snapshots, generated reports, and audit logs)
* **Target Infrastructure:** SUSE MLM / Uyuni XML-RPC API (`/rpc/api`)

---

## 3. Product Features & Scope

### 3.1 FastMCP Server (SUSE MLM Capabilities)
* Standalone MCP server built with FastMCP exposing native SUSE MLM XML-RPC endpoints as tools.
* **Authentication Tools:** Session creation and lifecycle handling via `auth.login` and `auth.logout`.
* **System & Inventory Tools:** Tools mapped to `system.*` (e.g., list managed servers, fetch system details, inspect installed packages).
* **OpenSCAP & Compliance Tools:** Tools mapped to `audit.*` (e.g., list available SCAP profiles, schedule XCCDF scans, fetch scan status, retrieve detailed rule pass/fail results).
* **Errata & Patch Tools:** Tools mapped to `errata.*` and `system.*` (e.g., get relevant errata per system, lookup errata by CVE ID, fetch patch advisories).
* **Remediation & Action Tools:** Tools mapped to `system.scheduleApplyErrata` and `schedule.*` for tracking action execution.

### 3.2 Autonomous Agent Engine (LangGraph)
* **Multi-Step Agent Graphs:** Coordinates tool discovery, compliance rule evaluation, and remediation planning without manual command-by-command instructions.
* **Strict Rule Compliance:** Evaluates compliance exclusively using native SUSE MLM data: SCAP Security Guide profiles (e.g., CIS benchmarks, DISA-STIG, HIPAA-aligned standard profiles available in MLM) and vendor errata/CVE channels. No synthetic or external compliance rules are invented.
* **Human-in-the-Loop Safeguards:** Mandatory interrupt states requiring explicit operator confirmation before executing any state-altering MCP tool (such as dispatching patch updates or scheduling audit scans).

### 3.3 Conversational Chat Interface (React)
* Real-time natural language interface to query server posture (e.g., *"Which servers failed CIS benchmark rule audits?"* or *"Summarize pending security errata on production hosts"*).
* Streaming responses showing agent reasoning steps and MCP tool invocations.
* In-chat interactive approval cards for reviewing and executing remediation proposals.

### 3.4 Server Reporting Engine
* Generation and download of comprehensive server compliance and vulnerability reports (PDF, CSV, JSON, and Web view).
* **Report Contents:**
  * OpenSCAP scan rule results (Pass/Fail/Error counts and rule descriptions per server).
  * Applicable errata breakdowns (Security, Bugfix, Enhancement) and mapped CVE identifiers.
  * Server compliance trends and configuration drift over time.
  * Complete audit trail of operator approvals and executed remediation actions stored in PostgreSQL.

---

## 4. Key Non-Functional Requirements
* **Decoupled Architecture:** FastAPI core communicates strictly through the FastMCP server, eliminating direct XML-RPC calls from the application layer.
* **Audit Persistence:** Every scan result, agent decision path, user approval, and executed patch job is permanently recorded in PostgreSQL.
* **Asynchronous Execution:** Non-blocking handling of long-running OpenSCAP scans, patch schedules, and report exports.
* **Safe Operations:** Automated remediations fail-closed; actions cannot execute without verified user approval tokens.
