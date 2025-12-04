---
doc_id: DOC-GUIDE-CURRENT-ORCHESTRATION-VS-REUSABLE-456
---


---

## 1. Findings report: current orchestration vs reusable orchestrator

### 1.1 What you already effectively have (pattern-level)

From our previous work, there are several “mini-orchestrators” in your world:

1. **SAFE_MERGE / merge pipeline patterns**

   * Phases: env scan → snapshot → pull → merge → validate → push.
   * You’ve got explicit phase names, pattern IDs, and rules like “never push without validation,” “snapshot before mutating,” etc.
   * Implementation: multiple PowerShell scripts + human instructions, not yet a unified engine.

2. **Git Auto-Sync watcher**

   * Long-running watcher that auto-adds/commits/pushes changes.
   * Has its own logging, its own error handling, its own policy knobs.
   * Lives in its own world, not driven by a shared “plan” schema.

3. **Headless CLI supervisor spec (recent)**

   * You already designed `run_cli_tool(tool_name, args, execution_id, timeout, heartbeat_timeout)` as a **standard process wrapper**:

     * Captures stdout/stderr
     * Records status → SQLite + JSONL
     * Detects timeout/heartbeat loss
   * This is basically the **core “step runner”** your orchestrator should use.

4. **Phase-based / workstream plans**

   * You have Phase 0–7, per-phase tasks, and workstreams (sometimes DAG-like).
   * Right now they’re mostly in Markdown/English, sometimes in JSON, but **not** in a single, consistent machine-readable schema that an engine can just “run”.

5. **Doc-ID / pattern / registry tools**

   * You already have JSON/JSONL-based scanners, registry updaters, etc., which **are perfect examples of “steps”** in a plan:

     * `scan_docs`
     * `sync_doc_ids`
     * `generate_report`
   * Today they are invoked ad hoc or via one-off scripts.

---

### 1.2 Gap analysis vs the “generic orchestrator” you described

Criteria for a good reusable orchestrator:

* **Config-driven**: behaviors live in JSON/YAML plans, not hard-coded.
* **DAG aware**: steps express dependencies (`depends_on`) and the engine respects them.
* **Centralized** process handling: timeouts, retries, logging, error policies in one place.
* **Reusable** across use cases: same engine for SAFE_MERGE, doc_id restore, test gates, AI pipelines, etc.
* **Observable**: every step/status is written to JSONL/SQLite and visible to GUI/TUI.

#### Where you’re strong

1. **Patterns and phases are already very explicit.**

   * Perfect for turning into plan files.
   * SAFE_MERGE phases, Doc-ID restore phases, headless CLI supervision patterns—all map cleanly to “steps”.

2. **You have a good process wrapper design.**

   * The `run_cli_tool(...)` concept is basically `run_step()` for the orchestrator.
   * You already thought about:

     * exit codes
     * heartbeats
     * stalls
     * logging

3. **You already think in “plans” and “workstreams”.**

   * Phase plans, workstreams, SAFE_MERGE, doc_id restoration—all of them are “plan_X.json” waiting to exist.

#### Where the current approach falls short

1. **No single “Plan Schema” that everything uses.**

   * SAFE_MERGE has one structure, Auto-Sync another, doc_id tools another.
   * Result: lots of duplicated logic (how you sequence steps, how you handle errors, etc.).

2. **No central orchestration engine.**

   * Each script partially re-implements:

     * logging
     * retries
     * timeouts
     * dependency management (usually via manual ordering)
   * You’re paying for this every time you add a new pipeline.

3. **Dependency management is mostly implicit / linear.**

   * Phases/steps are in order, but not formally a DAG.
   * That blocks true parallelism and makes partial re-runs harder.

4. **Error policies are scattered.**

   * Some flows say “abort on failure”, others “continue”, some rely on human judgment.
   * There’s no single `on_failure` policy per step that the engine understands.

5. **Observability is not normalized.**

   * You’ve got JSONL logs and SQLite ideas, but they’re not enforced by a central engine.
   * TUI/GUI can’t rely on one consistent schema for “what’s running, what failed, what’s next”.

---

### 1.3 Summary of opportunities

**High-impact upgrades:**

1. **Define ONE JSON plan schema** and migrate:

   * SAFE_MERGE pipeline
   * Doc-ID restore pipeline
   * Phase 0–7 pipeline
   * Headless CLI “AI codegen + tests + commit” pipelines
     into that schema.

2. **Implement ONE orchestrator runner (PS/Python or both)** that:

   * Reads the plan JSON
   * Constructs a DAG of steps
   * Executes steps via your `run_cli_tool`/`run_step` wrapper
   * Emits JSONL + SQLite status.

3. **Retrofit existing scripts as “step commands”**, not orchestrators themselves.

   * i.e. `safe_merge_phase1.ps1` becomes a step invoked by the orchestrator.
   * Or better, you consolidate into parametric scripts called with specific args from steps.

4. **Wire GUI/TUI to the orchestrator’s state.**

   * Since everything shares the same JSONL/SQLite schema, your “Mission Control” UI becomes much easier.

Net: the **design we talked about *is* a better solution** because it turns your multiple bespoke orchestrations into a **single, reusable engine** plus many plan files.

---

## 2. Concrete JSON plan design

Let’s define a **generic plan schema** that can work across all your pipelines.

### 2.1 JSON schema (conceptual)

Top level:

```json
{
  "plan_id": "PLAN-SAFE-MERGE-001",
  "version": "1.0",
  "description": "Safe merge pipeline for main -> experiment branches",
  "metadata": {
    "project": "complete-ai-dev-pipeline",
    "created_by": "DICK",
    "created_at": "2025-12-04T01:00:00Z",
    "tags": ["safe-merge", "git", "ci"]
  },
  "globals": {
    "max_concurrency": 2,
    "default_timeout_sec": 1800,
    "default_retries": 0,
    "env": {
      "PYTHONUNBUFFERED": "1"
    }
  },
  "steps": [
    {
      "id": "snapshot_repo",
      "name": "Snapshot repository state",
      "description": "Create a pre-merge snapshot branch and backup",
      "command": "powershell.exe",
      "args": [
        "-File",
        "scripts/safe_merge/Create-Snapshot.ps1",
        "-TargetBranch", "main"
      ],
      "cwd": "C:/Users/richg/ALL_AI/Complete AI Development Pipeline – Canonical Phase Plan",
      "shell": false,
      "env": {},
      "depends_on": [],
      "timeout_sec": 600,
      "retries": 0,
      "retry_delay_sec": 0,
      "critical": true,
      "condition": null,
      "on_failure": "abort",
      "provides": ["snapshot_ref"],
      "consumes": [],
      "tags": ["phase:1", "workstream:merge"],
      "ui_hints": {
        "group": "Pre-merge safety",
        "weight": 10
      }
    }
  ]
}
```

**Core fields per step:**

* `id` *(string, required)* – unique within plan.
* `name`, `description` – human context.
* `command` *(string)* – executable (e.g. `python`, `powershell.exe`, `git`).
* `args` *(array of strings)* – arguments.
* `cwd` *(string)* – working directory.
* `shell` *(bool)* – whether to use shell invocation.
* `env` *(object)* – per-step environment overrides.
* `depends_on` *(array of step IDs)* – DAG edges.
* `timeout_sec` *(int, optional)* – overrides global default.
* `retries`, `retry_delay_sec` – per-step policy.
* `critical` *(bool)* – if true and `on_failure = abort`, pipeline stops.
* `condition` *(string or null)* – expression like `prev.snapshot_repo.status == "success"`.
* `on_failure` *(enum)* – `"abort" | "skip_dependents" | "continue" | "fallback_step"`.
* `provides` / `consumes` *(arrays of logical resource names)* – optional resource graph.
* `tags` – arbitrary classification (`phase:X`, `workstream:Y`, etc.).
* `ui_hints` – grouping/ordering hints for the UI.

### 2.2 Tiny end-to-end example: “Run tests + lint + safe commit”

```json
{
  "plan_id": "PLAN-CHECKIN-001",
  "version": "1.0",
  "description": "Pre-commit checks: lint + tests + safe commit",
  "globals": {
    "max_concurrency": 2,
    "default_timeout_sec": 1800,
    "default_retries": 0,
    "env": {
      "PYTHONUNBUFFERED": "1"
    }
  },
  "steps": [
    {
      "id": "lint_python",
      "name": "Run Python linters",
      "command": "python",
      "args": ["-m", "ruff", "."],
      "cwd": ".",
      "shell": false,
      "env": {},
      "depends_on": [],
      "timeout_sec": 600,
      "retries": 0,
      "retry_delay_sec": 0,
      "critical": true,
      "condition": null,
      "on_failure": "abort",
      "provides": ["lint_report"],
      "consumes": [],
      "tags": ["phase:lint", "lang:python"],
      "ui_hints": { "group": "Checks", "weight": 10 }
    },
    {
      "id": "run_tests",
      "name": "Run Python tests",
      "command": "pytest",
      "args": ["-q"],
      "cwd": ".",
      "shell": false,
      "env": {},
      "depends_on": ["lint_python"],
      "timeout_sec": 1200,
      "retries": 0,
      "retry_delay_sec": 0,
      "critical": true,
      "condition": null,
      "on_failure": "abort",
      "provides": ["test_report"],
      "consumes": [],
      "tags": ["phase:test"],
      "ui_hints": { "group": "Checks", "weight": 20 }
    },
    {
      "id": "safe_commit",
      "name": "Create safe commit",
      "command": "powershell.exe",
      "args": [
        "-File",
        "scripts/git/Create-SafeCommit.ps1",
        "-Message",
        "Auto: lint+tests passed"
      ],
      "cwd": ".",
      "shell": false,
      "env": {},
      "depends_on": ["run_tests"],
      "timeout_sec": 300,
      "retries": 0,
      "retry_delay_sec": 0,
      "critical": false,
      "condition": "prev.run_tests.status == 'success'",
      "on_failure": "continue",
      "provides": ["commit_sha"],
      "consumes": [],
      "tags": ["phase:commit"],
      "ui_hints": { "group": "Git", "weight": 30 }
    }
  ]
}
```

---

## 3. Orchestrator pseudocode (engine design)

Language-agnostic flow:

```text
function run_plan(plan_path):
    plan = load_and_validate_json(plan_path)
    state = init_state(plan)  # status per step, outputs, logs
    while exists steps in {PENDING, RUNNING}:
        runnable = find_runnable_steps(plan, state)
        if runnable is empty and no RUNNING steps:
            break  # deadlock or all done

        for step in runnable:
            if can_start_more_work(state, plan.globals.max_concurrency):
                start_step_async(step, state)

        # poll running steps, update statuses, handle retries/heartbeats
        update_running_steps(state)

    summary = compute_summary(state)
    write_summary(summary)
    return summary.exit_code
```

Key components:

* `load_and_validate_json`

  * Validates required fields, `depends_on` references, etc.

* `init_state(plan)`

  * Sets each step status to `PENDING`.
  * Prepares global execution ID, log files, SQLite row(s).

* `find_runnable_steps(plan, state)`

  * Steps whose:

    * status is `PENDING`
    * all `depends_on` are `SUCCESS` or `SKIPPED` (depending on policy)
    * `condition` evaluates true (if present).

* `start_step_async(step, state)`

  * Launches a process (PS or Python) with given `command`, `args`, `cwd`, `env`.
  * Writes `RUNNING` status + `started_at`.
  * Starts stdout/stderr capture into logs (one combined log per plan, plus optional per-step file).
  * Optionally writes a row to SQLite with step metadata and `status = running`.

* `update_running_steps(state)`

  * For each running process:

    * Check `timeout_sec` vs `started_at`.
    * Check if process exited.

      * If exit code = 0 → mark `SUCCESS`.
      * If non-zero → handle according to `retries` / `on_failure`.
    * If heartbeat mechanism is implemented, detect stalls and treat as failure/timeout.

* `handle_step_failure(step, error)`

  * If retries remaining → increment `retry_count`, reschedule as `PENDING`.
  * Else:

    * Set status to `FAILED`.
    * If `on_failure == "abort"` and `step.critical`:

      * Mark plan as `FAILED`, cancel remaining `PENDING` steps.
    * If `on_failure == "skip_dependents"`:

      * Mark dependents as `SKIPPED`.
    * If `on_failure == "continue"`:

      * Leave dependents runnable, they may still execute.

* `write_summary(summary)`

  * Write JSON summary: statuses, timings, logs paths, etc.
  * This is what your GUI/TUI reads.

---

## 4. PowerShell orchestrator skeleton

Here’s a skeleton `Invoke-Orchestrator.ps1` you can evolve.

```powershell
param(
    [Parameter(Mandatory)]
    [string]$PlanPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Read-JsonFile {
    param([string]$Path)
    Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
}

function New-OrchestratorState {
    param($Plan)

    $steps = @{}
    foreach ($step in $Plan.steps) {
        $steps[$step.id] = [ordered]@{
            id          = $step.id
            status      = 'PENDING'
            started_at  = $null
            finished_at = $null
            attempt     = 0
            exit_code   = $null
            error       = $null
            pid         = $null
        }
    }

    return [ordered]@{
        plan          = $Plan
        steps         = $steps
        running       = @{}   # stepId -> process object
        execution_id  = [guid]::NewGuid().ToString()
        started_at    = (Get-Date).ToString('o')
        log_file      = Join-Path -Path (Get-Location) -ChildPath "logs\orchestrator_$((Get-Date).ToString('yyyyMMddHHmmss')).jsonl"
    }
}

function Write-OrchestratorEvent {
    param(
        $State,
        [string]$EventType,
        [hashtable]$Payload
    )

    $record = @{
        ts         = (Get-Date).ToString('o')
        event_type = $EventType
        execution  = $State.execution_id
        payload    = $Payload
    }

    $json = ($record | ConvertTo-Json -Depth 6 -Compress)
    $logFile = $State.log_file
    $logDir = Split-Path $logFile
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir | Out-Null
    }
    Add-Content -LiteralPath $logFile -Value $json
}

function Get-RunnableSteps {
    param($State)

    $plan = $State.plan
    $steps = @()

    foreach ($step in $plan.steps) {
        $id = $step.id
        $s = $State.steps[$id]

        if ($s.status -ne 'PENDING') { continue }

        # Check dependencies
        $deps = @($step.depends_on)
        $depsOk = $true
        foreach ($dep in $deps) {
            if (-not $dep) { continue }
            $depState = $State.steps[$dep]
            if ($depState.status -ne 'SUCCESS') {
                $depsOk = $false
                break
            }
        }

        if (-not $depsOk) { continue }

        # TODO: evaluate condition expression if present
        $steps += $step
    }

    return $steps
}

function Start-Step {
    param(
        $State,
        $Step
    )

    $stepId = $Step.id
    $stepState = $State.steps[$stepId]

    $stepState.status     = 'RUNNING'
    $stepState.started_at = (Get-Date).ToString('o')
    $stepState.attempt   += 1

    $startInfo = @{
        FilePath     = $Step.command
        ArgumentList = $Step.args
        WorkingDirectory = $Step.cwd
        NoNewWindow  = $true
        PassThru     = $true
        RedirectStandardOutput = $true
        RedirectStandardError  = $true
    }

    $proc = Start-Process @startInfo

    $stepState.pid = $proc.Id
    $State.running[$stepId] = $proc

    Write-OrchestratorEvent -State $State -EventType 'step_started' -Payload @{
        step_id = $stepId
        pid     = $proc.Id
        attempt = $stepState.attempt
    }
}

function Update-RunningSteps {
    param($State)

    $now = Get-Date

    foreach ($entry in @($State.running.GetEnumerator())) {
        $stepId = $entry.Key
        $proc   = $entry.Value
        $stepState = $State.steps[$stepId]
        $stepDef = ($State.plan.steps | Where-Object { $_.id -eq $stepId })

        if ($proc.HasExited) {
            $exitCode = $proc.ExitCode
            $stepState.exit_code   = $exitCode
            $stepState.finished_at = $now.ToString('o')

            if ($exitCode -eq 0) {
                $stepState.status = 'SUCCESS'
                Write-OrchestratorEvent -State $State -EventType 'step_succeeded' -Payload @{
                    step_id   = $stepId
                    exit_code = $exitCode
                }
            } else {
                $stepState.status = 'FAILED'
                $stepState.error  = "Non-zero exit code: $exitCode"
                Write-OrchestratorEvent -State $State -EventType 'step_failed' -Payload @{
                    step_id   = $stepId
                    exit_code = $exitCode
                }
                # TODO: respect retries, on_failure, critical flags
            }

            $State.running.Remove($stepId) | Out-Null
        } else {
            # TODO: enforce timeout_sec based on stepDef and started_at
        }
    }
}

function Invoke-Orchestrator {
    param([string]$PlanPath)

    $plan = Read-JsonFile -Path $PlanPath
    $state = New-OrchestratorState -Plan $plan

    Write-OrchestratorEvent -State $state -EventType 'plan_started' -Payload @{
        plan_id = $plan.plan_id
        version = $plan.version
    }

    while ($true) {
        Update-RunningSteps -State $state

        $pendingOrRunning = $false
        foreach ($s in $state.steps.Values) {
            if ($s.status -eq 'PENDING' -or $s.status -eq 'RUNNING') {
                $pendingOrRunning = $true
                break
            }
        }

        if (-not $pendingOrRunning) { break }

        # Launch runnable steps if capacity allows
        $runnable = Get-RunnableSteps -State $state
        $maxConc = $state.plan.globals.max_concurrency
        $currentRunning = $state.running.Count

        foreach ($step in $runnable) {
            if ($currentRunning -ge $maxConc) { break }
            Start-Step -State $state -Step $step
            $currentRunning++
        }

        Start-Sleep -Seconds 1
    }

    Write-OrchestratorEvent -State $state -EventType 'plan_finished' -Payload @{
        plan_id = $plan.plan_id
        statuses = @($state.steps.Values)
    }
}

Invoke-Orchestrator -PlanPath $PlanPath
```

This is deliberately **barebones** but already:

* Reads a JSON plan.
* Tracks step state.
* Handles dependency order.
* Runs steps with some parallelism.
* Logs JSONL events you can feed into a GUI/TUI.

You’d then:

* Plug in timeout, retries, `on_failure`, conditions, SQLite integration.
* Replace `Start-Process` stdout/stderr handling with file logging or streams.

---

## 5. Python orchestrator skeleton

Here’s a simple `orchestrator.py` that mirrors the same behavior.

```python
import json
import subprocess
import time
import uuid
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any


@dataclass
class StepDef:
    id: str
    name: str
    command: str
    args: List[str]
    cwd: str = "."
    shell: bool = False
    env: Dict[str, str] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    timeout_sec: Optional[int] = None
    retries: int = 0
    retry_delay_sec: int = 0
    critical: bool = True
    condition: Optional[str] = None
    on_failure: str = "abort"  # abort | skip_dependents | continue
    provides: List[str] = field(default_factory=list)
    consumes: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    ui_hints: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StepState:
    id: str
    status: str = "PENDING"  # PENDING, RUNNING, SUCCESS, FAILED, SKIPPED
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    attempt: int = 0
    exit_code: Optional[int] = None
    error: Optional[str] = None
    pid: Optional[int] = None
    process: Optional[subprocess.Popen] = None


@dataclass
class Plan:
    plan_id: str
    version: str
    description: str
    globals: Dict[str, Any]
    steps: List[StepDef]


class Orchestrator:
    def __init__(self, plan: Plan, log_path: Path):
        self.plan = plan
        self.log_path = log_path
        self.execution_id = str(uuid.uuid4())
        self.steps: Dict[str, StepState] = {
            s.id: StepState(id=s.id) for s in plan.steps
        }

    def log_event(self, event_type: str, payload: Dict[str, Any]):
        record = {
            "ts": time.time(),
            "event_type": event_type,
            "execution": self.execution_id,
            "payload": payload,
        }
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, separators=(",", ":")) + "\n")

    def get_step_def(self, step_id: str) -> StepDef:
        for s in self.plan.steps:
            if s.id == step_id:
                return s
        raise KeyError(step_id)

    def find_runnable_steps(self) -> List[StepDef]:
        runnable = []
        for sdef in self.plan.steps:
            sstate = self.steps[sdef.id]
            if sstate.status != "PENDING":
                continue

            # deps
            deps_ok = all(
                self.steps[dep].status == "SUCCESS" for dep in sdef.depends_on
            )
            if not deps_ok:
                continue

            # TODO: evaluate condition expression if needed
            runnable.append(sdef)
        return runnable

    def start_step(self, step: StepDef):
        sstate = self.steps[step.id]
        sstate.status = "RUNNING"
        sstate.started_at = time.time()
        sstate.attempt += 1

        cmd = [step.command] + step.args
        env = dict(**step.env)
        # TODO: merge plan.globals.env, os.environ, etc.

        proc = subprocess.Popen(
            cmd,
            cwd=step.cwd,
            shell=step.shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        sstate.process = proc
        sstate.pid = proc.pid

        self.log_event("step_started", {"step_id": step.id, "pid": proc.pid, "attempt": sstate.attempt})

    def update_running_steps(self):
        now = time.time()
        max_timeout = self.plan.globals.get("default_timeout_sec")

        for step_id, sstate in list(self.steps.items()):
            if sstate.status != "RUNNING" or sstate.process is None:
                continue

            proc = sstate.process
            ret = proc.poll()

            # TODO: enforce timeout based on stepDef + started_at

            if ret is None:
                # still running
                continue

            stdout, stderr = proc.communicate()
            # you can write per-step logs here if desired

            sstate.exit_code = ret
            sstate.finished_at = now
            sdef = self.get_step_def(step_id)

            if ret == 0:
                sstate.status = "SUCCESS"
                self.log_event("step_succeeded", {"step_id": step_id, "exit_code": ret})
            else:
                sstate.status = "FAILED"
                sstate.error = stderr.strip() or f"Exit code {ret}"
                self.log_event("step_failed", {"step_id": step_id, "exit_code": ret, "stderr": sstate.error})
                # TODO: handle retries, on_failure, critical

            sstate.process = None  # cleaned up

    def run(self) -> int:
        self.log_event("plan_started", {"plan_id": self.plan.plan_id, "version": self.plan.version})
        max_conc = self.plan.globals.get("max_concurrency", 1)

        while True:
            self.update_running_steps()

            pending_or_running = any(
                s.status in ("PENDING", "RUNNING") for s in self.steps.values()
            )
            if not pending_or_running:
                break

            running_count = sum(1 for s in self.steps.values() if s.status == "RUNNING")
            capacity = max(0, max_conc - running_count)
            if capacity > 0:
                runnable = self.find_runnable_steps()
                for step in runnable[:capacity]:
                    self.start_step(step)

            time.sleep(0.5)

        self.log_event("plan_finished", {
            "plan_id": self.plan.plan_id,
            "statuses": {k: vars(v) for k, v in self.steps.items()}
        })

        # Determine exit code: 0 if all success/ skipped, 1 otherwise
        failed = [s for s in self.steps.values() if s.status == "FAILED"]
        return 0 if not failed else 1


def load_plan(path: Path) -> Plan:
    data = json.loads(path.read_text(encoding="utf-8"))
    steps = [StepDef(**s) for s in data["steps"]]
    return Plan(
        plan_id=data["plan_id"],
        version=data["version"],
        description=data.get("description", ""),
        globals=data.get("globals", {}),
        steps=steps,
    )


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("plan_path", help="Path to JSON plan file")
    parser.add_argument("--log-dir", default="logs", help="Log directory")
    args = parser.parse_args()

    plan_path = Path(args.plan_path)
    plan = load_plan(plan_path)

    ts = time.strftime("%Y%m%d%H%M%S")
    log_path = Path(args.log_dir) / f"orchestrator_{ts}.jsonl"

    orch = Orchestrator(plan=plan, log_path=log_path)
    exit_code = orch.run()
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
```

This is:

* Minimal but working.
* Already captures an execution ID and JSONL events.
* Ready to get:

  * timeout enforcement
  * retries
  * richer env merging
  * conditions and `on_failure` semantics
  * SQLite integration.

---
