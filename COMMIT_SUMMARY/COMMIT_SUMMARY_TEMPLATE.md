---
doc_id: DOC-GUIDE-COMMIT-SUMMARY-TEMPLATE-155
doc_type: commit_summary
schema_version: 1.0.0
doc_id: COMMIT-SUMMARY-PLACEHOLDER    # filled by doc_id system
generated_by:
  tool: commit_summary_agent
  mode: auto_6h                       # [auto_6h | on_demand]
  run_id: RUN-PLACEHOLDER
time_window:
  start: 2025-01-01T00:00:00-06:00    # inclusive
  end:   2025-01-01T06:00:00-06:00    # exclusive
repo:
  name: complete-ai-development-pipeline-canonical-phase-plan
  default_branch: main
branches_analyzed:
  - main
  - feature/example
stats:
  commit_count: 0
  authors_count: 0
  files_changed: 0
  tests_changed: 0
  pipelines_touched: 0               # CI/workflow files changed
risk_overall: TBD                     # [LOW | MEDIUM | HIGH]
focus_signal: TBD                     # Short human-readable label, e.g. "Phase 5 executor wiring"
---

# 0. Mission & Focus Anchor (for this window)

> **Goal of this 6-hour slice:**
> _One sentence that anchors what this chunk of work is trying to achieve._

- **Current high-level mission:**
  - e.g. "Implement Phase 5 executor + acceptance tests."

- **Active phases touched in this window:**
  - Phase 0 – Initialization
  - Phase 1 – Planning
  - Phase 2 – Scheduling
  - Phase 3 – Routing
  - Phase 4 – ???
  - Phase 5 – Execution & Validation
  - Phase 6 – Error Recovery
  - Phase 7 – Monitoring & UX

- **Core subsystems impacted (check all that apply):**
  - [ ] Core engine (orchestrator / scheduler / executor / state)
  - [ ] Error engine & plugins
  - [ ] Spec / OpenSpec / workstreams bridge
  - [ ] Tool adapters & profiles
  - [ ] State & persistence (DB, ledgers, .state/)
  - [ ] GUI / PM integration / CCPM
  - [ ] Docs / diagrams / schemas

---

# 1. Executive Summary (Last 6 Hours)

- **Net effect on system:**
  - e.g. "Executor stub partially implemented; new tests added; no production-grade error handling yet."

- **Change volume:**
  - Commits: `{{commit_count}}`
  - Files changed: `{{files_changed}}`
  - Tests changed/added: `{{tests_changed}}`
  - Workflows/CI changed: `{{pipelines_touched}}`

- **Risk assessment for this window:**
  - **Overall:** `[LOW | MEDIUM | HIGH]`
  - **Key reasons:**
    - `• Reason 1`
    - `• Reason 2`

- **Automation posture:**
  - [ ] Automation strengthened
  - [ ] Automation weakened / bypassed
  - [ ] Neutral
  - **Evidence:** short bullets referencing commits / files.

- **High-priority notes for next AI run (TL;DR):**
  - `• One-sentence instruction 1`
  - `• One-sentence instruction 2`

---

# 2. Branch & Workstream Overview

## 2.1 Branches in this window

| Branch           | Commits | Status vs default | Merge risk | Comment |
|------------------|---------|-------------------|-----------:|---------|
| `main`           | 0       | base              | LOW        |         |
| `feature/foo`    | 0       | ahead by N        | MEDIUM     |         |
| `agent-1-phase5` | 0       | diverged          | HIGH       |         |

> **Agent rule:** Never merge based solely on this table. It's a planning signal, not a merge gate.

## 2.2 Workstreams / specs touched

List any **workstreams** or **OpenSpec URIs** that had commits:

- Workstreams:
  - `workstreams/ws-XX-PLACEHOLDER.json` – brief description of what changed.
- Specs / OpenSpec:
  - `spec://domain/path` – file path (e.g. `specifications/content/...`), nature of change.

---

# 3. Changes by Phase & Subsystem

> Group commits by **pipeline phase** + **subsystem**, not by file path alone.
> This keeps AI aligned with the architecture (phases 0–7, core engine, error engine, spec bridge, adapters, GUI, etc.).

## 3.1 Phase-aligned summary

For each phase touched in the window, list the main changes and impact.

### Phase 0 – Initialization
- **Key changes:**
  - `• …`
- **Impact on config / schemas / startup:**
  - `• …`
- **Follow-ups required (yes/no + bullets):**
  - `• …`

### Phase 1 – Planning
### Phase 2 – Scheduling
### Phase 3 – Routing
### Phase 4 – ??? (fill in actual phase name)
### Phase 5 – Execution & Validation
- **Key changes:**
  - `• executor logic updated in core/engine/executor.py`
  - `• new acceptance tests / test_gate wiring`
- **Impact on task lifecycle (IN_PROGRESS → VALIDATING → COMPLETED/FAILED):**
  - `• …`
- **Risk to execution stability:** `[LOW | MEDIUM | HIGH]` + explanation.

### Phase 6 – Error Recovery
### Phase 7 – Monitoring & UX

(Repeat structure for any phase actually touched; leave untouched phases omitted or "No changes".)

---

## 3.2 Subsystem summary (cross-cut)

Summarize changes by architecture subsystem:

- **Core Engine (orchestrator, scheduler, executor, state_manager):**
  - Files:
    - `core/engine/...`
  - Effects:
    - `• …`

- **Error Detection & Recovery (error engine, plugins, circuit breaker, retry):**
  - Files:
    - `error/engine/...`, `error/plugins/...`
  - Effects:
    - `• …`

- **Specification & Workstream Bridge (OpenSpec → workstreams):**
  - Files:
    - `specifications/content/...`, `specifications/bridge/...`, `schema/workstream.schema.json`
  - Effects:
    - `• …`

- **Tool Selection & Adapters (aim/, tool_profiles, adapters):**
  - Files:
    - `aim/...`, `config/tool_profiles.yaml`, `engine/adapters/...`
  - Effects:
    - `• …`

- **File & Task Lifecycle / State & Persistence:**
  - Files:
    - `.state/...`, `core/state/...`, DB migrations, patch ledgers, archive modules.
  - Effects:
    - `• …`

- **GUI / PM / CCPM integration:**
  - Files:
    - `gui/...`, `pm/...`, integration scripts.
  - Effects:
    - `• …`

---

# 4. Automation & Safety Signals

## 4.1 Automation tightened or loosened?

For each area below, mark:

- `status`: `[STRENGTHENED | WEAKENED | UNCHANGED | UNKNOWN]`
- `evidence`: shortlist of commits / files.

### a. Task lifecycle & retries
- status: …
- evidence:
  - `• …`

### b. Error detection & escalation
### c. Tool selection & adapter profiles
### d. Spec → workstream conversion
### e. File lifecycle (discover → committed → archived)
### f. Monitoring / metrics / logging

## 4.2 Tests & acceptance gates

- **New tests added:**
  - `• path:: description`
- **Existing tests modified:**
  - `• path:: description`
- **Overall acceptance gate status:**
  - `• Are there any areas where tasks now skip VALIDATING?`
  - `• Any new test suites still flaky or TODO only?`
- **CI / workflow changes that affect safety:**
  - `• …`

---

# 5. Focus Guidance For Next AI Runs (Critical Section)

> This is the part you want every agent to read **first** before working.

## 5.1 Do more of this (next 6 hours)

List **3–7 concrete "threads"** the AI should continue:

1. `Thread-1: short label`
   - Context: what changed this window.
   - Next step: one specific action.
2. `Thread-2: ...`
3. …

## 5.2 Do **not** touch (until explicitly gated)

List any files / modules / areas that are unstable, mid-refactor, or require human sign-off.

- **Guarded areas:**
  - `• path/to/module – reason`
- **Patterns to avoid:**
  - `• e.g. "Do not add new tools to aim/ without updating tool_profiles + schemas."`

## 5.3 Open loops / unresolved issues from this window

Each open loop should be a short, actionable item:

- `OL-001 – description – link to spec/workstream/issue if known`
- `OL-002 – …`

---

# 6. Commit Inventory (Machine-Readable Appendix)

> A compact, structured list for downstream tools.
> Keep it deterministic and consistent; use `UNKNOWN` rather than omitting fields.

```json
{
  "time_window": {
    "start": "2025-01-01T00:00:00-06:00",
    "end": "2025-01-01T06:00:00-06:00"
  },
  "commits": [
    {
      "hash": "abcdef123",
      "short_hash": "abcdef1",
      "author": "name <email>",
      "timestamp": "2025-01-01T02:13:45-06:00",
      "branch": "feature/example",
      "summary": "Short commit message",
      "phases_touched": ["Phase 5", "Phase 6"],
      "subsystems_touched": ["core_engine", "error_engine"],
      "files_changed": [
        "core/engine/executor.py",
        "error/engine/error_engine.py"
      ],
      "tests_changed": [
        "tests/test_executor.py"
      ],
      "risk": "MEDIUM",
      "automation_impact": "STRENGTHENED",
      "notes": "1-line note for humans/agents"
    }
  ]
}
```

---

# 7. Generator Notes (hidden from summary consumers)

> **For the commit_summary_agent / orchestrator only – may be stripped before publishing.**

1. Use `git log` + `git diff` constrained to `time_window` and `branches_analyzed` to populate `commits[]`.
2. Derive **phases** from:
   * file paths (`phaseX_*/`, `core/engine/` → Execution phase, etc.)
   * workstream / spec locations.
3. Derive **subsystems** from directory mapping (core engine, error engine, specs, adapters, GUI, etc).
4. When unsure, set fields to `UNKNOWN` instead of guessing.
5. Maintain stable ordering:
   * phases: 0→7
   * subsystems: fixed order listed above
   * commits: chronological ascending.
6. This file should be written to:
   * `docs/commit_summaries/COMMIT_SUMMARY_YYYYMMDD_HHMM.md`
7. Never auto-edit `.state/`, `.ledger/`, or schema files directly; only **report** on changes to them.
