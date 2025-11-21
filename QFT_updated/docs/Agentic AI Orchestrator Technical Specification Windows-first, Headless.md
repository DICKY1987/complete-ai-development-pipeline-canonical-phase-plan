# Agentic AI Orchestrator — Technical Specification (Windows-first, Headless)

**Status:** Draft v1.0
**Target OS:** Windows 11 (PowerShell 7+)
**Primary Tools:** Git, Python 3.x, PowerShell, Aider (headless), Claude Code CLI (optional), CI (GitHub Actions)
**Audience:** Engineers building deterministic, audit-ready AI automation that edits codebases headlessly

---

## 1) Purpose & Scope

This specification defines a **deterministic, headless agentic AI system** that plans, edits, validates, and merges code through **non-interactive CLIs**. It prescribes architecture, components, interfaces (schemas & commands), control flows, quality gates, observability, and failure handling. The system is **Windows-first** but portable to POSIX.

**In scope**

* Local orchestration (headless) of AI CLIs (e.g., Aider; Claude Code via a shell tool).
* Task queue + JSONL contracts for requests and logs.
* Git worktree isolation for parallel workstreams.
* Quality gates (Ruff/pytest for Python; Pester for PowerShell).
* Deterministic rollback, circuit-breaker, and retry policies.

**Out of scope**

* Cloud deployment and secrets management platforms (covered only as interfaces).
* IDE/TUI experiences; this spec is **TUI-free** and **HTTP-free**.

---

## 2) Goals & Non-Goals

**Goals**

1. **Deterministic edits**: every agent action is reproducible from an append-only task log.
2. **Safety by design**: automatic rollback on failure; never merge “red” branches.
3. **Auditability**: JSONL ledger for every attempt, artifact, and decision.
4. **Parallelism with isolation**: Git worktrees to run many jobs concurrently, safely.
5. **Zero-touch operations**: background worker + supervisor with heartbeats and self-healing.

**Non-Goals**

* No interactive UI loops; all commands are batch-invoked.
* No persistent network services on localhost (no HTTP servers).

---

## 3) Architectural Overview

### 3.1 Logical Layers

* **Agent Layer (Planners/Editors)**:

  * *Planner*: Claude Code (optional) to generate session plans or .aider command files.
  * *Editor*: Aider headless to apply scoped changes and commit atomically.
* **Orchestration Layer**:

  * Queue Worker (PowerShell) consumes **JSONL tasks**, invokes tools headlessly, and enforces policies (timeouts, retries, circuit breakers, rollbacks).
  * Optional Headless Orchestrator loop (periodic jobs like `git fetch` status).
* **Deterministic-Git Layer**:

  * Worktrees for parallel units; checkpoints before/after edits; green-only merge policy.
* **Quality & Gates Layer**:

  * Local and CI gates (Ruff/pytest/Pester) before merge; pre-commit optional.
* **Observability Layer**:

  * JSONL ledger, per-task logs, heartbeats, log rotation, artifacts.

### 3.2 Component Diagram (Mermaid)

```mermaid
flowchart LR
  subgraph Agent_Layer
    CC[Claude Code (optional planner)]
    AD[Aider (headless editor)]
  end

  subgraph Orchestration
    QW[QueueWorker.ps1]
    SV[Supervisor.ps1]
    ORCH[Headless Orchestrator (optional loops)]
  end

  subgraph Storage
    TQ[(.tasks/inbox *.jsonl)]
    LOGS[(logs/*)]
    LEDGER[(logs/ledger.jsonl)]
    STATE[(.state/heartbeat.json)]
  end

  subgraph Git
    MAIN[(repo main)]
    WS_A[(worktree A)]
    WS_B[(worktree B)]
  end

  CC -- emits plan/.aider --> TQ
  TQ --> QW
  QW <-- monitors --> SV
  ORCH --> LOGS
  QW -- invoke --> AD
  QW -- commits --> WS_A
  WS_A --> MAIN
  QW --> LEDGER
  QW --> STATE
```

---

## 4) Execution Patterns (no TUI, no HTTP)

The orchestrator supports three complementary **CLI-only** patterns:

* **Pattern A (Claude-driven shell calls, optional)**
  Claude Code uses a shell tool to run PowerShell that in turn calls Aider. Real-time chat isn’t required; the call remains non-interactive.
* **Pattern B (Scripted Aider)**
  PowerShell/Python builds `aider --yes --auto-commits -m "..."`
  messages and executes them headlessly.
* **Pattern C (Pre-generated `.aider` command files)**
  Preplan steps in `session_*.aider`; run: `aider --yes --auto-commits /load session_*.aider`.

> **Recommendation:** Use **Pattern B** for automation/CI and **Pattern C** for large, auditable migrations. Pattern A is optional for “AI planning” but still runs headlessly.

---

## 5) Git Strategy

* **Worktrees**: each parallel job runs in its own worktree (`feature/<unit>`).
* **Checkpoints**: capture `HEAD` before tool execution; auto-rollback on failure.
* **Merge policy**: only green (validated) branches merge to `main`.
* **Commit convention** (AI): `Aider: <area>: <action>` (e.g., `Aider: ids: add ULID registry`).

---

## 6) Interfaces

### 6.1 Task JSONL (inbox → processing → done/failed/quarantine)

**Location**: `.tasks/inbox/*.jsonl` (each line = one task)

**Schema (conceptual)**

```json
{
  "id": "string (ULID/UUIDv7 recommended)",
  "tool": "git | aider | pwsh | python | claude",
  "repo": "path | '.'",
  "worktree": "optional path (if using git worktrees)",
  "args": ["array of strings"],             // for generic tools
  "prompt": "string or null",               // for AI tools
  "files": ["paths..."],                    // optional, file scope hints
  "flags": ["--yes","--auto-commits"],      // for aider, etc.
  "timeout_sec": 1800,
  "env": {"NAME": "VALUE"},                 // optional environment vars
  "tags": ["labels for routing/SLAs"]
}
```

**Examples**

```json
{ "id":"git-001","tool":"git","repo":".","args":["fetch","--all","--prune"] }
{ "id":"aider-101","tool":"aider","repo":".","prompt":"Refactor tools/migrate.py into modules","files":["tools/migrate.py"],"flags":["--yes","--auto-commits"],"timeout_sec":1200 }
{ "id":"quality-001","tool":"pwsh","args":["-NoProfile","-File","scripts/run_quality.ps1"],"timeout_sec":1800 }
```

### 6.2 Aider Invocation Contract (headless)

**Command (Pattern B)**

```
aider --yes --auto-commits [-m "<step1>"] [-m "<step2>"] ... ["/load session_<X>.aider"]
```

**Step examples**

```
/add README.md
/code Implement ULID registry at tools/spec_migrate/ulid_registry.py with tests
/diff
/lint
/test pytest -q
/commit Aider: ids: implement ULID registry
```

### 6.3 Planner Output (optional Claude → .aider)

Claude (or any planner) emits `.aider` command files:

```
/add tools/spec_migrate/migrate.py
/code Refactor into resolver.py and types.py (see acceptance criteria…)
/diff
/lint
/test pytest -q
/commit Aider: migrate: refactor config resolver
```

---

## 7) Orchestration Policies

### 7.1 Timeouts & Retries

* **Per-task timeout**: `timeout_sec` (default 1800).
* **Retries**: exponential backoff with jitter (configurable window).
* **Max attempts**: configurable per `tool` and per `tags`.

### 7.2 Circuit Breaker (per tool)

* Open the breaker after **N** consecutive failures; move new tasks for that tool to **quarantine**.
* Reclose after cool-down or manual operator action.

### 7.3 Rollback

* Before invoking an editor tool (e.g., Aider), record `BEFORE_SHA = git rev-parse HEAD`.
* On non-zero exit, run `git reset --hard BEFORE_SHA` in that worktree.

### 7.4 Self-Healing

* **Recover processing**: at startup, move stale `.tasks/processing/*.jsonl` back to inbox.
* **Git lock repair**: if `.git/index.lock` is old and no `git` process, safely remove it.
* **Heartbeat**: write `.state/heartbeat.json` every few seconds; supervisor restarts on staleness.

---

## 8) Observability & Audit

### 8.1 Ledger JSONL (append-only)

* **File**: `logs/ledger.jsonl`
* **One line per attempt**

```json
{
  "ts": "2025-11-10T17:05:33.219Z",
  "task_id": "aider-101",
  "tool": "aider",
  "repo": "C:/repos/proj",
  "worktree": "C:/repos/proj/ws_A",
  "cmd": "aider --yes --auto-commits -m ...",
  "exit_code": 0,
  "duration_ms": 43210,
  "before_sha": "2f1b8a6c",
  "after_sha": "9c0e2d11",
  "files_touched": ["tools/spec_migrate/ulid_registry.py","tests/..."],
  "artifact": "logs/task_aider-101.log"
}
```

### 8.2 Per-Task Logs

* `logs/task_<id>.log` — raw stdout/stderr merged, timestamped.

### 8.3 Heartbeat

* `.state/heartbeat.json` — `{ "ts": "...", "pid": 1234, "queue_depth": 7 }`

### 8.4 Log Rotation

* Rotate when exceeding `LogRotateMaxMB`; archive to `logs/archive/` and prune older than `LogKeepDays`.

---

## 9) Data Models (reference)

### 9.1 Worktree Status (optional reporting)

If you maintain a **worktree status** document, use a JSON schema with fields like:

```json
{
  "worktree": "string",
  "branch": "string",
  "ahead": 0,
  "behind": 0,
  "dirty": true,
  "head": "sha1",
  "last_update": "iso8601",
  "queued_tasks": 3,
  "state": "idle | running | failing | quarantined"
}
```

### 9.2 Quality Report (batch-level)

```json
{
  "batch_id": "20251110_170530",
  "result": "PASS | FAIL",
  "linters": {"ruff": "ok"},
  "tests": {"pytest": {"passed": 45, "failed": 0}, "pester": {"passed": 12, "failed": 0}},
  "notes": "optional string",
  "artifacts": ["logs/pytest.txt","logs/pester.txt"]
}
```

---

## 10) Quality Gates

### 10.1 Local Gate (CLI)

* **Python**: `ruff format --check`, `ruff check`, `pytest -q`
* **PowerShell**: `Invoke-Pester -CI`
* Optional: `pre-commit` config for instant feedback.

### 10.2 CI Gate (GitHub Actions)

* Reuse the same script (`scripts/run_quality.ps1`).
* Upload logs as artifacts.
* Protect `main`: require the “Quality Gate” check to pass.

---

## 11) Security & Secrets

* Never log secrets.
* Provide model/API keys via **environment** at execution time (e.g., `ANTHROPIC_API_KEY`) or a secure store.
* `.aider` files and ledger must not embed secrets.
* Quarantine tasks that reference forbidden env keys.

---

## 12) Configuration

### 12.1 Paths & Policies

* `scripts/QueueWorker.ps1` — main loop, **Build-Command** table for tools.
* `Config/HeadlessPolicies.psd1` — retries, backoff, circuit thresholds, rotation.
* `scripts/Supervisor.ps1` — restart on dead heartbeat.

### 12.2 Tool Name Map (examples)

| Tool key | Executable | Required flags              |
| -------- | ---------- | --------------------------- |
| `aider`  | `aider`    | `--yes --auto-commits`      |
| `git`    | `git`      | (per args)                  |
| `pwsh`   | `pwsh`     | `-NoProfile -File <script>` |
| `python` | `python`   | `<module or script>`        |

---

## 13) Control Flows

### 13.1 Single Issue (Pattern C → B)

1. **Plan**: author `session_<ISSUE>.aider` with explicit acceptance criteria.
2. **Enqueue**: drop **aider** task pointing at that file (`/load`).
3. **Execute**: worker runs aider; atomic commits.
4. **Gate**: worker enqueues **quality** task (ruff/pytest/Pester).
5. **Validate**: if green → mark batch approved; else rollback.
6. **Merge**: fast-forward/squash per policy.
7. **Log**: ledger + artifacts.

### 13.2 Parallel Streams (Worktrees)

* Scheduler assigns tasks to distinct worktrees.
* Each worktree maintains its own BEFORE/AFTER SHA and logs.
* Merge only after **per-worktree** validation is green.

---

## 14) Error Classes & Handling

| Error class      | Detection                    | Action                                  |
| ---------------- | ---------------------------- | --------------------------------------- |
| Tool timeout     | exec elapsed > `timeout_sec` | mark attempt failed; retry with backoff |
| Non-zero exit    | exit code != 0               | rollback (if editor); retry (bounded)   |
| Circuit open     | failure window exceeded      | quarantine next tasks for tool          |
| Stale processing | `.tasks/processing` aged     | move back to inbox at startup           |
| Git lock stuck   | old `.git/index.lock`        | safe remove & continue                  |
| Lint/test fail   | gate script exit != 0        | reject batch; report                    |

---

## 15) Acceptance Criteria (System)

* **AC-1 Determinism**: given the same task JSONL inputs, the system reproduces the same commits and logs (modulo timestamps).
* **AC-2 Safety**: no editor task leaves the repo in a dirty or partially applied state (rollback on failure).
* **AC-3 Audit**: every attempt present in `logs/ledger.jsonl` with exit code and before/after SHAs.
* **AC-4 Isolation**: tasks in different worktrees never write to the same path concurrently.
* **AC-5 Gates**: CI and local gates share the same script and must fail identically on the same code.
* **AC-6 No TUI/HTTP**: all operations proceed without interactive prompts or local servers.
* **AC-7 Recovery**: after an unclean shutdown, pending tasks are returned to inbox and can re-run.

---

## 16) Reference CLI Snippets

**Aider (Pattern B) – PowerShell**

```powershell
$steps = @('/add README.md','/code Implement X','/diff','/commit Aider: feature X')
$cmd = 'aider --yes --auto-commits'
foreach ($s in $steps) { $cmd += " -m `"$($s -replace '"','\"')`"" }
Invoke-Expression $cmd; if ($LASTEXITCODE) { exit $LASTEXITCODE }
```

**Aider (Pattern C) – PowerShell**

```powershell
aider --yes --auto-commits "/load session_feature_x.aider"
```

**Gate – PowerShell**

```powershell
pwsh -NoProfile -File scripts/run_quality.ps1
```

---

## 17) Deployment & Operations

* **Start worker (manual):** `pwsh -NoProfile -File .\scripts\QueueWorker.ps1`
* **Start supervisor (auto-restart):** `pwsh -NoProfile -File .\scripts\Supervisor.ps1`
* **Stop cleanly:** create `STOP.HEADLESS` at repo root
* **Schedule at logon:** Windows Task Scheduler → Supervisor.ps1
* **Logs:** `logs/*.log`, `logs/ledger.jsonl`, `logs/archive/`
* **Health:** heartbeat freshness; queue depth trending

---

## 18) Future Extensions (non-breaking)

* Pluggable **pre/post** hooks per tool (e.g., secret scanning before commit).
* **Batch** semantics (group tasks into an atomic unit with staged gate).
* **Model fallback** policy for Aider (switch models on failure).
* **Coverage gates** and **policy-as-code** (markdownlint, license scanners).

---

### Appendix A — Minimal File Tree (drop-in)

```
.
├─ .tasks/
│  ├─ inbox/
│  ├─ processing/
│  ├─ done/
│  ├─ failed/
│  └─ quarantine/
├─ .state/
│  └─ heartbeat.json           # worker heartbeat
├─ logs/
│  ├─ ledger.jsonl             # append-only audit
│  ├─ task_<id>.log            # per-task logs
│  └─ archive/
├─ scripts/
│  ├─ QueueWorker.ps1          # main loop
│  ├─ Supervisor.ps1           # restarts worker on stale heartbeat
│  ├─ RecoverProcessing.ps1    # returns stale to inbox
│  └─ run_quality.ps1          # Ruff/pytest/Pester
├─ Config/
│  └─ HeadlessPolicies.psd1    # retries, backoff, breaker, rotation
└─ sessions/
   └─ session_<issue>.aider    # optional Pattern C plans
```

---
