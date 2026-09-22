# HERMES-MANUAL.md

> **This is the project orchestration manual for Hermes.**
> Pair this file with `prd.md` to start any project. Hermes reads both and runs the full pipeline autonomously.

---

## For You (the Human) — How to Use This

**Prerequisites (one-time setup):**
- Run `HERMES-SKILL-BUILDER.md` once: give it to Hermes with `"refer the manual"`. This installs all 14 skills into `skills/`. You do not repeat this per project.
- Mandatory (install once): Ponytail, RTK, Agent-Reach — see `HERMES-SKILL-BUILDER.md` § Mandatory Productivity Tools.

**Per project:**
1. Write your idea/spec into `prd.md` (rough description is fine — Hermes asks if something critical is missing).
2. Put `prd.md` and this file (`HERMES-MANUAL.md`) in your project folder.
3. Open Hermes and send **one message**:

```
Read prd.md and HERMES-MANUAL.md in this folder.
Follow HERMES-MANUAL.md exactly, start to finish, on your own, using the
mandatory skills it names at each step. Stop only at the human touchpoints
it defines.
```

4. That is the only message you send. Hermes handles everything else, stopping only at the touchpoints below.

---

## Human Touchpoints — The Only Times Hermes Stops and Waits

| # | When | What you do |
|---|---|---|
| 1 | **Step 3** | Approve `plan.md` + `task.md` (or list changes). Reply *"approved"* to proceed. |
| 2 | **Step 3.1** | Provide target repo name (`<owner>/<repo>`) and confirm `GITHUB_TOKEN` is exported. |
| 3 | **Step 3.2** | Answer Hermes's domain/operational-parameter questions. |
| 4 | **Step 5 — semantic conflict** | Hermes shows both conflicting versions; you decide which wins. |
| 5 | **Step 4 — Loop Engineering blocker (5 iterations hit)** | Hermes reports the specific blocker; you decide how to proceed. |
| 6 | **Step 9 — plan.md Sections 5–8 change** | Hermes presents only the diff; you re-approve just that section. |

Everything else Hermes does autonomously once it has cleared the touchpoint that gates it.

---

## Autonomous Operation Principle

Once given the single kickoff message, Hermes runs Steps 1–10 end-to-end without waiting for further instruction, except at the touchpoints above.

- Hermes decides for itself, from `prd.md` and the repo's current state, which step applies next.
- A plain-language mid-project request ("add a feature that lets users export their data," "switch to Postgres," "check the frontend," "this is actually three services") is matched to the right step/skill below and run in full — no special template needed from the human.
- The only things Hermes cannot supply itself are secrets (the GitHub token) and the decisions this manual reserves for a human.

---

## Mandatory Skill Map

Each step requires Hermes to open and follow the named skill file in full. Never carry out a step's substance from memory or paraphrase — open and follow the named skill.

| Step | Mandatory skill(s) | Skill file(s) |
|---|---|---|
| Step 1 — Read the input | *(no skill — instructions below)* | — |
| Step 1.1 — Project analysis & skill selection | *(no skill — instructions below)* | — |
| Step 2 — Generate `plan.md` | `plan-generation` | `skills/plan-generation/SKILL.md` |
| Step 2.1 — Generate `task.md` | `task-generation` | `skills/task-generation/SKILL.md` |
| Step 3 — Human review gate | `human-review-gate` + `quality-checklist` (full checklist, pre-code items) | `skills/human-review-gate/SKILL.md` + `skills/quality-checklist/SKILL.md` |
| Step 3.1 — GitHub setup & auth | `github-setup` | `skills/github-setup/SKILL.md` |
| Step 3.2 — Domain & operational parameters | `domain-clarification` | `skills/domain-clarification/SKILL.md` |
| Step 4 — Implementation, phase by phase | `phase-implementation` + `loop-engineering` | `skills/phase-implementation/SKILL.md` + `skills/loop-engineering/SKILL.md` |
| Step 5 — Multi-developer merge handling | `multi-dev-merge` | `skills/multi-dev-merge/SKILL.md` |
| Step 6 — Production documentation | `production-documentation` | `skills/production-documentation/SKILL.md` |
| Step 7 — Git/GitHub automation | `git-github-automation` | `skills/git-github-automation/SKILL.md` |
| Step 8 — Deployment & verification | `deployment-verification` + `quality-checklist` (full checklist, post-deploy items) | `skills/deployment-verification/SKILL.md` + `skills/quality-checklist/SKILL.md` |
| Step 9 — New feature / tech-stack change | `feature-tech-stack-change` | `skills/feature-tech-stack-change/SKILL.md` |
| Step 10 — Microservices adaptation | `microservices-adaptation` | `skills/microservices-adaptation/SKILL.md` |
| Throughout — any build/test/fix cycle | `loop-engineering` | `skills/loop-engineering/SKILL.md` |
| After each phase / on demand — context compression | `context-compression` | `skills/context-compression/SKILL.md` |

---

## Tool Layer Map

These mandatory tools activate automatically at the steps indicated. They do not change what any skill requires — only how efficiently and robustly it is satisfied.

| Tool | Activation | What Hermes does |
|---|---|---|
| **RTK** | Step 3.1 (init), Steps 4–8 (always-on) | After `github-setup`, run `rtk init --agent hermes`. All CLI tool calls (git, gh, test runners, mypy) go through RTK transparently from Step 4 onward. |
| **Ponytail** | Steps 4–9 (always-on) | Before every code-write decision in implementation, apply Ponytail's 7-step Decision Ladder: Eliminate → Reuse → Stdlib → Native → Dependencies → One-liner → Surgical write. Never skip this for security, validation, or accessibility work. |
| **Agent-Reach** | Step 1–2 (if prd.md references external APIs/integrations), Step 4 (on-demand debugging) | If `prd.md` mentions third-party APIs, integrations, or live data sources, activate Agent-Reach to fetch live documentation and verify endpoint schemas before designing the API Contract (Section 7). In Step 4 debugging, use Agent-Reach to look up real error patterns before guessing. |

---

## Flow Diagram

```
PRD (Step 1) → Step 1.1 (Project Analysis & Skill Selection)
                        │
          ┌─────────────┴──────────────────┐
          │ single-service                 │ multi-service
          ▼                               ▼
    Step 2 plan-generation          Step 10 microservices-adaptation
    Step 2.1 task-generation          └─ 10.A: SYSTEM-PLAN.md [HUMAN APPROVES]
          │                               └─ 10.B per service:
    Step 3 human-review-gate [HUMAN APPROVES]   plan.md + task.md + Steps 3→8
          │                               └─ 10.C: cross-service contract change [HUMAN]
    Step 3.1 github-setup [HUMAN: repo + token]
    [RTK init here]
          │
    Step 3.2 domain-clarification [HUMAN: answers]
          │
      ┌──► Step 4 phase-implementation + loop-engineering [Ponytail always-on]
      │          │ fail (max 5 iterations) → [HUMAN: blocker report]
      │          │ pass
      │          ▼
      │    Step 5 multi-dev-merge (only when a branch needs merging)
      │          │ semantic conflict → [HUMAN: decide]
      │          ▼
      │    Step 6 production-documentation
      │          ▼
      │    Step 7 git-github-automation
      │          ▼
      │    Step 8 deployment-verification + quality-checklist [full]
      │          │
      │    more phases? ── yes ──┘
      │          │ no
      │          ▼
      │        DONE
      │          │
      │    later: plain-language feature / tech-stack request
      │          ▼
      └── Step 9 feature-tech-stack-change → back into Step 4

Agent-Reach: activates at Steps 1–2 if prd.md references external integrations,
             and on-demand during Step 4 debugging.
```

---

# INSTRUCTIONS FOR HERMES

> You are reading this because the human sent you `HERMES-MANUAL.md` alongside `prd.md`. Execute the following steps now, autonomously, in order. Stop only at the designated touchpoints. Do not ask the human for anything not listed as a touchpoint.

---

## Step 1 — Read the Input

1. Read `prd.md` fully before doing anything else.
2. If `prd.md` is missing information critical to Step 2, list the specific open questions and ask the human — do not invent requirements, architecture, or technology choices that were never stated.
3. **Auto-detect project shape.** Determine from `prd.md` whether this is a single-service or multi-service (microservices) build. If multi-service, activate Step 10's skill (`skills/microservices-adaptation/SKILL.md`) instead of the single-`plan.md` flow — do not wait for a special kickoff message; if genuinely ambiguous, ask as one of this step's open questions.
4. **Agent-Reach activation check:** If `prd.md` mentions external APIs, third-party integrations, live data sources, or social platforms, activate Agent-Reach now for use in Steps 1–2. Note this in your internal manifest.

**Transition to Step 1.1:** Immediately after reading `prd.md`, proceed automatically.

---

## Step 1.1 — Project Analysis & Skill Selection

Runs immediately after Step 1, before Step 2. **This step never changes what any skill produces.** It only resolves, once, which of the already-existing conditional rules inside the skills apply here — so later steps don't re-derive the same condition repeatedly.

1. **Detect application type** from `prd.md` (and a repo scan if one exists):
   - Has a UI (web/mobile/desktop/extension)?
   - Single- or multi-service?
   - Existing codebase or greenfield?
   - External SaaS/integration surfaces involved?
   - A data/ETL pipeline as a first-class component?

2. **Resolve conditional rules once** into a short internal manifest:
   - Does `plan-generation`'s Frontend Plan / Frontend test coverage apply?
   - Does `deployment-verification`'s Playwright requirement apply?
   - Does `microservices-adaptation` (Step 10) apply?
   - Is `plan-generation`'s Existing Codebase Analysis section populated from a real scan or marked greenfield?
   - Is Agent-Reach active for this project?
   Refer back to this manifest at later steps instead of re-checking each condition from scratch.

3. **Confirm mandatory skills are available.** Check that all 14 skills in `skills/` are loadable:
   - `plan-generation`, `task-generation`, `human-review-gate`, `github-setup`, `domain-clarification`, `phase-implementation`, `loop-engineering`, `multi-dev-merge`, `production-documentation`, `git-github-automation`, `deployment-verification`, `feature-tech-stack-change`, `microservices-adaptation`, `quality-checklist`.
   - If any named skill is missing, stop and tell the human which one and that `HERMES-SKILL-BUILDER.md` needs to be (re)run — do not attempt to reconstruct a missing skill's content from memory.

4. **Verify mandatory efficiency tools** in this session (RTK, Ponytail, Agent-Reach). Using them ensures high-discipline, token-efficient, and reality-grounded pipeline execution. Note their active status in the internal manifest.

**Transition — FORK based on manifest result:**
- **Multi-service detected** → skip Steps 2, 2.1, and 3 entirely. Go directly to **Step 10** now. Step 10 handles `SYSTEM-PLAN.md` generation and approval before any service's `plan.md` is written.
- **Single-service detected** → proceed to **Step 2** now.

---

## Step 2 — Generate `plan.md`

> ⚠️ **Single-service projects only.** If Step 1.1 detected a multi-service (microservices) project, you must not be here — go to Step 10. `SYSTEM-PLAN.md` must be written and approved before any service's `plan.md` is started.

**Open `skills/plan-generation/SKILL.md` and follow it in full.**

- Use the Appendix A template from that skill file exactly.
- Apply Loop Engineering (`skills/loop-engineering/SKILL.md`) while drafting: draft → self-check → fix gaps → repeat until consistent.
- If Agent-Reach is active and `prd.md` references external APIs: use it now to verify endpoint schemas and authentication requirements before filling Section 7 (API Contract).

**Transition to Step 2.1:** Immediately after `plan.md` is complete, proceed.

---

## Step 2.1 — Generate `task.md`

**Open `skills/task-generation/SKILL.md` and follow it in full.**

- Generate `task.md` from `plan.md` Section 23 immediately after `plan.md` is drafted.
- Do not proceed to Step 3 until both `plan.md` and `task.md` are complete.

**Transition to Step 3:** Present both files to the human per the human-review-gate skill.

---

## Step 3 — Human Review Gate (BLOCKING TOUCHPOINT)

**Open `skills/human-review-gate/SKILL.md` and follow it in full.**

Before presenting, self-audit using `skills/quality-checklist/SKILL.md` — read the full checklist and verify every pre-code item (those relating to prd.md, plan.md, task.md, directory structure, JSON constraint, User Stories, FRs, test cases, DoD). Fix any failures before showing the human.

- Present `plan.md` and `task.md` together.
- Ask explicitly: *"Please review plan.md and task.md. Reply 'approved' to proceed, or list changes needed."*
- If changes are requested: revise, re-present, ask again.
- **Do not proceed until the human replies "approved".**

**Transition to Step 3.1:** Proceed immediately after approval.

---

## Step 3.1 — GitHub Setup & Authentication (BLOCKING TOUCHPOINT)

**Open `skills/github-setup/SKILL.md` and follow it in full.**

This is a blocking touchpoint: you need the human to supply the target repo name and confirm `GITHUB_TOKEN` is exported.

After successful authentication:
- Run `rtk init --agent hermes` and confirm the savings dashboard is accessible via `rtk gain`. From this point forward, route all CLI tool calls through RTK transparently.
- Confirm authentication with a test push to a throwaway branch before starting implementation.

**Transition to Step 3.2:** Proceed immediately after GitHub is confirmed.

---

## Step 3.2 — Domain & Operational Parameters (BLOCKING TOUCHPOINT)

**Open `skills/domain-clarification/SKILL.md` and follow it in full.**

This is a blocking touchpoint: you need the human's answers before writing core feature code. Present all domain questions in one structured list — do not ask in multiple rounds.

After receiving answers: apply the operational parameters across config files, environment variables, validation schemas, and database default constraints before Step 4 begins.

**Transition to Step 4:** Begin the first phase immediately after answers are incorporated.

---

## Step 4 — Implementation, Phase by Phase

**Open `skills/phase-implementation/SKILL.md` and follow it in full.**
**Keep `skills/loop-engineering/SKILL.md` open throughout — apply the Loop Engineering cycle for every build/test/fix within each phase.**

**Ponytail layer (mandatory, always-on):** Before every code-write decision, apply the Decision Ladder:
1. Eliminate — does this code need to exist at all?
2. Reuse — does the codebase already solve this?
3. Stdlib — does the standard library handle it?
4. Native — does the platform have a native feature (e.g., `<input type="date">`)?
5. Dependencies — does an already-installed dep solve it?
6. One-liner — can it be one line?
7. Surgical write — only then, write the absolute minimum correct implementation.
Never skip steps 1–6 for code that touches security, data-loss paths, or accessibility.

**Agent-Reach layer (on-demand):** If a test or debug cycle hits a blocker that involves a third-party API behavior, error code, or library version issue, use Agent-Reach to look up real documentation or community reports before guessing.

For each phase:
1. Build the phase's scope.
2. Validate — run every relevant test type (unit, integration, API, security, performance, edge cases, end-to-end user story walkthroughs from Section 15/16).
3. If anything fails: read the exact failure, fix specifically that, re-run the same check.
4. Repeat up to 5 iterations. If still failing at iteration 5: **STOP — this is a Loop Engineering Blocker touchpoint.** Report the specific blocker to the human and wait for direction.
5. When a task passes validation, mark it `- [x]` in `task.md` immediately.
6. When all tasks in a phase are checked off and Definition of Done (Section 24) items for that phase are met: proceed to Step 5 or Step 6.

**Transition after each phase:** After a phase passes: run Step 5 only if a feature branch is ready to merge (otherwise skip it), then run Steps 6 → 7 → 8. Then **auto-compress context** — open `skills/context-compression/SKILL.md` and write `SESSION-STATE.md` to the project root before starting the next phase. Then check if more phases remain in `plan.md` Section 23 — if yes, return to Step 4. If no phases remain and the quality checklist passes, declare completion.

---

## Step 5 — Multi-Developer Merge Handling

**Open `skills/multi-dev-merge/SKILL.md` and follow it in full.**

Apply this step whenever a feature branch is ready to merge:
- Pull latest `main` into the feature branch.
- Re-run the full test suite against the merged result.
- Classify conflicts: textual (auto-resolve + re-test) vs. semantic (present both versions to human — **BLOCKING TOUCHPOINT**).
- Merge only via Pull Request, never direct push to `main`.
- Create `docs/MERGE_<date>_<branches>.md` after every merge.

**Transition to Step 6:** Proceed immediately after a successful merge.

---

## Step 6 — Production Documentation

**Open `skills/production-documentation/SKILL.md` and follow it in full.**

Mandatory after every phase and every merge:
1. Create/update root `README.md` with architecture diagram, port inventory, role matrix, quickstart, dev setup, test commands, and phase doc links.
2. Create/update `docs/APPLICATION_DOCUMENTATION.md` with full technical, API, domain, state-transition, and error-handling specs.
3. Create `docs/PHASE_<number>_<short-name>.md` (or `docs/MERGE_<date>_<branches>.md`) with what was implemented, the Loop Engineering log, and test results by type (referencing TC-xxx IDs from Section 15).

**Transition to Step 7:** Proceed immediately after documentation is written.

---

## Step 7 — Version Control & GitHub Automation

**Open `skills/git-github-automation/SKILL.md` and follow it in full.**

- Push all completed code, tests, and documentation to the remote repository.
- Use feature branches and Pull Requests — never direct push to `main`.
- Every commit message references the phase or feature (e.g., `feat(phase-2): add user auth endpoints`).
- Autonomous merge is only allowed if the human has explicitly set `autonomous-merge: true` for this project, CI is fully green, and the change does not touch auth, payments, secrets, or data-deletion logic.

**Transition to Step 8:** Proceed immediately after the push/PR is done.

---

## Step 8 — Deployment & Verification

**Open `skills/deployment-verification/SKILL.md` and follow it in full.**

1. Deploy per `plan.md` Section 17 (Deployment).
2. Run all Section 25 Post-Implementation Verification checks: smoke tests, health checks, metrics/log verification, regression tests.
3. If the project has a UI: run automated Playwright end-to-end browser verification covering all user journeys and scenarios listed in Section 14 (Frontend) and Section 15 (Test Cases).
4. Give the human the live URL and a summary of what was deployed and which phase docs cover it.
5. If any post-deployment check fails: do not declare the phase done — re-enter the Loop Engineering cycle (Step 4).

Before declaring the project complete, self-audit using `skills/quality-checklist/SKILL.md` in full. Fix any unchecked items.

**Transition after Step 8:**
- If more phases remain in `plan.md` Section 23: return to Step 4.
- If all phases are done and the quality checklist is fully passed: declare completion and present the live URL to the human.

---

## Step 9 — New Feature or Tech-Stack Change (Triggered by Human Request)

**Open `skills/feature-tech-stack-change/SKILL.md` and follow it in full.**

Activated when the human sends a plain-language request like:
- "Add a feature that lets users export their data"
- "Switch to Postgres"
- "Add Redis for caching"
- "Replace REST with GraphQL"

Hermes matches the request to this step automatically — the human does not need to specify "Step 9".

After completing Step 9: re-enter Step 4 for the new phase, then continue through Steps 5–8 as normal.

---

## Step 10 — Microservices Adaptation (Auto-Detected at Step 1.1)

**Open `skills/microservices-adaptation/SKILL.md` and follow it in full.**

Activated automatically when Step 1.1 detects that `prd.md` describes multiple independently-owned services. This step replaces the single-`plan.md` flow — do not run Steps 2–8 in the single-service order. Instead follow this exact sequence:

### 10.A — Generate `SYSTEM-PLAN.md` (BLOCKING TOUCHPOINT)

1. Open `skills/microservices-adaptation/SKILL.md`.
2. Scroll to the section labelled **`# APPENDIX D — SYSTEM-PLAN.md Template (Microservices)`** inside that file. That section contains the exact template with 11 numbered headings (System Overview, Service Inventory, Service Boundaries, Communication Patterns, Inter-Service API Contracts, Authentication Between Services, Shared Standards, Deployment Topology, Failure & Degradation, Contract Change Process, Open Questions).
3. Use that template to generate `SYSTEM-PLAN.md` in the project root, filled in from `prd.md`.
4. **STOP. Present `SYSTEM-PLAN.md` to the human and ask for explicit approval.** Do not begin any individual service's `plan.md` or `task.md` until the human approves.

```
project-root/
  SYSTEM-PLAN.md   ← generated here from Appendix D template
  service-<name-a>/
  service-<name-b>/
```

### 10.B — Per-Service: `plan.md` + `task.md` (one pair per service)

Once `SYSTEM-PLAN.md` is approved, for **each service**:

1. **Generate `plan.md`** — open `skills/plan-generation/SKILL.md`, use the Appendix A template (28 sections), scoped to that service's `prd.md`. Section 7 (API Contract) must match what `SYSTEM-PLAN.md` allows for this service.
2. **Generate `task.md`** — open `skills/task-generation/SKILL.md`, use the Appendix E template, derived from this service's `plan.md` Section 23.
3. **Add Consumer-Driven Contract Tests** — per the microservices-adaptation skill Section 10.3: add a Contract Tests category to `plan.md` Section 14 and corresponding TC-xxx rows to Section 15 for each service dependency.
4. **Human review gate (Step 3)** — present this service's `plan.md` + `task.md` together for approval before implementing it.
5. **Run Steps 3.1 → 3.2 → 4 → 5 → 6 → 7 → 8** for this service exactly as in the single-service flow.

### 10.C — Cross-Service Contract Change (BLOCKING TOUCHPOINT)

If implementing one service reveals a need to change an interface that another service depends on:
- **STOP** — do not change the service's `plan.md` unilaterally.
- Update `SYSTEM-PLAN.md` first, present the diff to the human, get explicit approval.
- Then update the affected services' `plan.md` Section 7 to match.
- Only then resume implementation.

---

## Hermes Self-Reminder (Read Before Every Step)

- You are autonomous. Do not ask the human for anything unless it is an explicitly listed blocking touchpoint.
- You must open the named skill file and follow it in full — never paraphrase or reconstruct from memory.
- **Ponytail Decision Ladder** is mandatory and applies before every code-write from Step 4 onward: Eliminate → Reuse → Stdlib → Native → Deps → One-liner → Surgical write. Never skip for security, validation, or a11y.
- **RTK** is mandatory and must be initialized at Step 3.1 (`rtk init --agent hermes`). From Step 4 onward, all CLI calls (git, gh, mypy, test runners) go through RTK transparently.
- **Agent-Reach** is mandatory and activates at Steps 1–2 if `prd.md` references external APIs/integrations, and on-demand during Step 4 debugging when a third-party API or library issue blocks progress.
- The Loop Engineering cycle (propose → validate → diagnose → refine → converge) applies during drafting, implementing, and debugging — everywhere.
- `task.md` is updated task-by-task as each passes validation, not batched.
- **Context compression** runs automatically after each phase completes (open `skills/context-compression/SKILL.md` and write `SESSION-STATE.md`). Also runs on-demand when the human says "compress context" or "/compress". This lets a fresh session resume with no conversation history.
- If a skill file is missing: stop and tell the human which skill is missing and that `HERMES-SKILL-BUILDER.md` must be re-run. Do not proceed.

