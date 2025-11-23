

Gotcha — you want **this second blob of concepts** wired into the same architecture we just mapped onto your repo, *and* you want it to cover the “no general-purpose restructuring tool” reality.

I’ll treat this as:

> “Make *codebase restructuring* and *AI-assisted refactors* first-class citizens inside the same stateful, observable orchestration model.”

I’ll keep it concrete and repo-shaped.

---

## 1. What “the second block” actually adds

The new text is really three extra layers on top of your existing orchestration principles:

1. **Admits reality**

   * There is no magical general-purpose restructuring tool.
   * Architectural refactors must be **planned**, **reviewed**, and **executed** with context.
2. **Introduces a “restructuring spec” pattern**

   * A declarative YAML/JSON plan that says: “move X → Y, update imports, run tests.”
3. **Positions AI as:**

   * Planner (generate & refine the restructuring spec)
   * Executor (Aider / codex / CLI agents apply it)
   * Auditor (checks state, failure modes, and rollback).

So the move is:

> Treat “codebase restructuring” as **just another orchestrated workstream** with:
>
> * Tasks, plans, states, events, checkpoints, recovery rules
> * Exactly like the rest of the pipeline.

---

## 2. Turn restructuring into a first-class Workstream Bundle

### 2.1. Add a Restructure Bundle type

Under your `registry/`:

**File:** `registry/workstream_bundles.json`

Extend (or create) with a *restructuring* bundle type:

```json
{
  "schema_version": "WorkstreamBundlesV1",
  "bundles": [
    {
      "bundle_id": "RESTRUCTURE-CODEBASE-V1",
      "kind": "restructure",
      "description": "Architectural refactor of core pipeline modules",
      "tasks": [
        "TSK-ANALYZE-STRUCTURE",
        "TSK-GENERATE-RESTRUCTURE-SPEC",
        "TSK-REVIEW-SPEC",
        "TSK-APPLY-MOVES",
        "TSK-UPDATE-IMPORTS",
        "TSK-RUN-VALIDATION-SUITE"
      ],
      "completion_criteria": {
        "all_tests_pass": true,
        "no_lint_errors": true,
        "restructure_spec_applied": true
      }
    }
  ]
}
```

### 2.2. Add the restructuring tasks to the Task Registry

In `registry/tasks_registry.json`:

```json
{
  "task_id": "TSK-GENERATE-RESTRUCTURE-SPEC",
  "name": "generate_restructure_spec",
  "phase_id": "PH-RESTRUCTURE-01",
  "workstream_id": "WS-RESTRUCTURE-PLAN",
  "inputs": {
    "codebase_root": "path",
    "constraints_file": "path",       // e.g. DEV_RULES_CORE.md
    "target_architecture_doc": "path" // your canonical structure doc
  },
  "outputs": {
    "restructure_spec_path": "path"
  },
  "preconditions": ["filesystem_accessible"],
  "postconditions": ["restructure_spec_generated"],
  "max_runtime_seconds": 300,
  "retry_policy": "exponential_backoff",
  "worker_requirements": ["filesystem", "python3", "ai_planner"],
  "idempotent": true,
  "side_effects": ["writes_to_disk"],
  "rollback_handler": "delete_generated_spec_if_marked_invalid"
}
```

Then similar entries for `TSK-APPLY-MOVES`, `TSK-UPDATE-IMPORTS`, `TSK-RUN-VALIDATION-SUITE`.

Now AI can “see” restructuring as a graph of tasks, not hand-wavy magic.

---

## 3. Define the Restructuring Spec as Data

This is where your “no general-purpose tool exists” part becomes structured.

### 3.1. Restructuring spec file

**Directory:** `plans/restructure/`
**Example file:** `plans/restructure/RESTRUCTURE_CODEBASE_V1.yaml`

```yaml
schema_version: RestructureSpecV1
plan_id: RESTRUCTURE_CODEBASE_V1
description: >
  Consolidate orchestration engine modules, separate dev-docs from system-docs,
  normalize paths for AI tools.

moves:
  - id: move_phase_docs
    from: "docs/phases/"
    to: "devdocs/phases/"
    kind: directory
    rationale: "Phase specs are development-time governance artifacts."
  - id: move_error_module
    from: "error/"
    to: "engine/error_pipeline/"
    kind: directory
    rationale: "Align error pipeline with orchestrator engine boundary."
  - id: move_support_scripts
    from: "scripts/*.ps1"
    to: "tools/powershell/"
    kind: glob
    rationale: "Centralize operator scripts."

post_move_actions:
  - update_imports: true
  - regenerate_indexes:
      - "registry/path_index.json"
  - run_validation_suite: true

safety:
  require_clean_git: true
  create_checkpoint: true
  rollback_strategy: "git_reset_to_checkpoint"
```

This file is:

* What AI helps you *generate/refine*
* What the orchestrator *executes*
* What the append-only logs *reference*.

### 3.2. Wire it to the Execution Plan

Create:

`registry/plans/PH-RESTRUCTURE-01_EXECUTION_PLAN.json`

```json
{
  "schema_version": "ExecutionPlanV1",
  "plan_id": "PH-RESTRUCTURE-01",
  "description": "Execute restructuring spec against the codebase",
  "stages": [
    {
      "stage_id": 1,
      "parallel_tasks": ["TSK-ANALYZE-STRUCTURE"],
      "max_parallelism": 1
    },
    {
      "stage_id": 2,
      "parallel_tasks": [
        "TSK-GENERATE-RESTRUCTURE-SPEC",
        "TSK-REVIEW-SPEC"
      ],
      "max_parallelism": 2,
      "depends_on_stages": [1]
    },
    {
      "stage_id": 3,
      "parallel_tasks": [
        "TSK-APPLY-MOVES",
        "TSK-UPDATE-IMPORTS"
      ],
      "max_parallelism": 2,
      "depends_on_stages": [2]
    },
    {
      "stage_id": 4,
      "parallel_tasks": ["TSK-RUN-VALIDATION-SUITE"],
      "max_parallelism": 1,
      "depends_on_stages": [3]
    }
  ]
}
```

Parallelism + dependencies are now **explicit data**, not implicit logic.

---

## 4. Make Restructuring Fully Observable

Use the same state/observability patterns, just add restructuring-specific views.

### 4.1. State snapshots

Extend your `.state/` files with a “restructuring” section:

**`.state/orchestrator_state.json` (excerpt):**

```json
{
  "schema_version": "OrchestratorStateV1",
  "active_bundles": [
    {
      "bundle_id": "RESTRUCTURE-CODEBASE-V1",
      "phase_id": "PH-RESTRUCTURE-01",
      "status": "RUNNING",
      "current_stage": 3,
      "current_tasks": ["TSK-APPLY-MOVES", "TSK-UPDATE-IMPORTS"]
    }
  ]
}
```

**Optional:** dedicated:

* `.state/restructure_state.json` showing:

  * spec path
  * moves completed / remaining
  * last checkpoint
  * validation status.

### 4.2. Event stream

In `.ledger/events/orchestrator_events.jsonl`, emit events like:

```json
{
  "event_id": "EVT-ULID-123",
  "timestamp": "2025-11-22T05:12:33.123456Z",
  "event_type": "restructure_spec_generated",
  "actor": "planner_ai",
  "bundle_id": "RESTRUCTURE-CODEBASE-V1",
  "task_id": "TSK-GENERATE-RESTRUCTURE-SPEC",
  "context": {
    "restructure_spec_path": "plans/restructure/RESTRUCTURE_CODEBASE_V1.yaml",
    "summary": "14 moves planned, 3 high-risk"
  },
  "caused_by": "EVT-ULID-122"
}
```

So an AI can later read:

* What was proposed
* What was applied
* What failed
* What got rolled back.

### 4.3. Failure modes for restructuring

In `docs/FAILURE_MODES.md` (or a restructures subsection):

* “Move failed because path missing”
* “AST import update produced syntax error”
* “Tests failed after restructuring”

Map each to an error policy in `registry/error_policies.yaml`, e.g.:

```yaml
- id: restructure_tests_failed
  when:
    bundle_kind: restructure
    event_type: validation_failed
  then:
    action: rollback_to_checkpoint
    notify: ["operator"]
```

---

## 5. Connect to AI Tools (Aider / Codex / Copilot)

This is where the “no general-purpose tool” part turns into **tool roles**:

* **Planner AI (Claude/OpenSpec/CCPM)**

  * Reads codebase + your canonical architecture docs
  * Generates `RESTRUCTURE_CODEBASE_V1.yaml`
* **Executor AI (Aider, Codex)**

  * Takes each `moves[]` entry and performs:

    * file moves
    * function moves (via AST)
    * import updates
* **Verifier AI**

  * Reads `.state/` and `.ledger/events`
  * Confirms:

    * all moves applied
    * tests/lint passed
    * no unexpected diffs outside spec

To make this smooth, add a small **tool contract** per AI in your repo, e.g.:

* `tools/aider/TOOL_CONTRACT.md`
* `tools/codex/TOOL_CONTRACT.md`

Each says:

* “You **MUST** only make changes described in the current `restructure_spec`.”
* “You **MUST** log each applied move to `.ledger/events`.”
* “You **MUST NOT** touch files under X/Y/Z.”

(You already have DEV_RULES-style docs; this just scopes them to restructuring.)

---

## 6. Minimal next steps (concrete to-do list)

If you want to actually apply all this to your repo **right now**, I’d do it in this order:

1. **Create the Restructure Spec schema + example**

   * `schema/RestructureSpecV1.json`
   * `plans/restructure/RESTRUCTURE_CODEBASE_V1.yaml` (even if mostly stubbed).
2. **Add restructuring tasks to `registry/tasks_registry.json`**

   * At least: `TSK-GENERATE-RESTRUCTURE-SPEC`, `TSK-APPLY-MOVES`, `TSK-RUN-VALIDATION-SUITE`.
3. **Add a restructure execution plan**

   * `registry/plans/PH-RESTRUCTURE-01_EXECUTION_PLAN.json`.
4. **Update `.state/orchestrator_state.json` format**

   * So it can show restructure bundles & their stages.
5. **Wire your AI tools to this pattern**

   * One short `TOOL_CONTRACT.md` per CLI tool that explains:

     * “When running in restructure mode, read this spec, perform these tasks, and respect these constraints.”

If you want, next message I can draft **one complete RestructureSpecV1 schema + example** specifically tuned to your `complete-ai-development-pipeline-canonical-phase-plan` repo, so you can drop it into `schema/` and `plans/` and start using it as the canonical pattern.


````markdown
---
spec_id: AI-ORCH-REPO-V1
title: AI-Oriented Orchestration Repository Spec
version: 1.0.0
status: draft
owner: orchestration-architecture
applies_to:
  - autonomous_orchestration_systems
  - ai-assisted_dev_pipelines
---

# AI-Oriented Orchestration Repository Spec (AI-ORCH-REPO-V1)

## 0. Conventions

- The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are to be interpreted as described in RFC 2119.
- Each requirement is given a stable ID (e.g. `STATE-OBS-001`), which **MUST** be used by Phase Specs, Workstreams, and tools when referring to that requirement.
- Examples are **non-normative** unless explicitly marked otherwise.

---

## 1. Scope and Purpose

### REPO-SCOPE-001

This specification defines how an autonomous orchestration repository **MUST** be structured to maximize:

- AI understanding of execution model and state
- Observability and auditability of all actions
- Safe, deterministic automation

It is intended for:

- Phase and Workstream specifications
- Agentic AI tools (Claude Code, Codex, Aider, Copilot CLI, etc.)
- Human operators implementing or extending the orchestration engine

### REPO-SCOPE-002

All orchestration-related repositories in this system **MUST** conform to this spec for:

- State representation (`.state/`)
- Execution model documentation (`docs/execution_model/`)
- Task definitions (`schema/tasks/`)
- DAG representation (`workstreams/.../dag.json` etc.)
- Capability catalogs (`capabilities/`)
- Failure modes and error handling (`docs/failure_modes/`)
- Tool integration contracts (e.g. Aider)

---

## 2. State Observability

### STATE-OBS-001: State Directory Layout

The repository **MUST** contain a top-level `.state/` directory with the following structure:

```text
.state/
  snapshots/               # Timestamped complete state captures
  current.json             # Latest queryable state snapshot
  transitions.jsonl        # Append-only state transition log
  health.json              # Real-time health metrics
  indices/                 # Precomputed queryable views
````

### STATE-OBS-002: Snapshots

* `.state/snapshots/` **MUST** contain timestamped state snapshots in JSON format.
* Filenames **MUST** be sortable by lexicographical order to represent chronological order (e.g. `YYYY-MM-DDTHH-mm-ss.json`).
* Each snapshot **MUST** be a complete state object sufficient to reconstruct all active workstreams, tasks, and workers at that moment.

> Non-normative example:
> `.state/snapshots/2024-11-22T14-30-00.json`

### STATE-OBS-003: Current State

* `.state/current.json` **MUST** contain the latest complete state snapshot.
* The orchestrator **MUST** update `.state/current.json` atomically on each state change.
* `.state/current.json` **MUST** be sufficient for AI agents to answer “what is happening now?” without executing any code.

### STATE-OBS-004: State Transitions Log

* `.state/transitions.jsonl` (or `.ledger/events/...jsonl` if already established) **MUST** be an append-only log of state transitions.
* Each line **MUST** be a single JSON object including at least:

  * `timestamp` (ISO8601 with microseconds)
  * `event` or `event_type`
  * `actor` (component or worker)
  * `context` (before/after or delta)
  * `caused_by` (optional parent event ID)

### STATE-OBS-005: Indices

* `.state/indices/` **MUST** contain precomputed query views **at minimum**:

  * `tasks_by_status.json`
  * `blocked_tasks.json`
  * `worker_capabilities.json`

* Indices **MUST** be derived from canonical state (snapshots or current) and **MUST NOT** be treated as authoritative state.

> Non-normative structure:

```text
.state/indices/
  tasks_by_status.json
  blocked_tasks.json
  worker_capabilities.json
```

---

## 3. Execution Model Documentation

### EXEC-DOC-001: Execution Model Directory

The repository **MUST** contain:

```text
docs/execution_model/
  ORCHESTRATION_OVERVIEW.md
  TASK_LIFECYCLE.md
  WORKSTREAM_EXECUTION.md
  AIDER_INTEGRATION.md
  PARALLEL_EXECUTION.md
  state_machine_diagrams/   # optional visualizations
```

### EXEC-DOC-002: Orchestration Overview

* `docs/execution_model/ORCHESTRATION_OVERVIEW.md` **MUST** describe:

  * The boss program’s responsibilities
  * High-level execution flow (from user request → workstream bundle → tasks → validation)
  * How state is persisted (`.state/` + logs)

This doc **MUST** be written so an AI can understand the high-level architecture without code execution.

### EXEC-DOC-003: Task Lifecycle

* `docs/execution_model/TASK_LIFECYCLE.md` **MUST** describe all task states and transitions, consistent with `SM-DEF-001` (state machine spec).
* Phase and Workstream specs **MUST** refer to these states by name (e.g. `PENDING`, `READY`, `RUNNING`, `COMPLETED`, `FAILED`, `RETRY_PENDING`).

### EXEC-DOC-004: Workstream Execution

* `docs/execution_model/WORKSTREAM_EXECUTION.md` **MUST** describe:

  * How workstream bundles are constructed
  * How dependencies are resolved into a DAG
  * How parallel execution is managed
  * How completion and failure are determined

### EXEC-DOC-005: Aider Integration Docs

* `docs/execution_model/AIDER_INTEGRATION.md` **MUST** describe:

  * Aider’s role as a worker (not a standalone tool)
  * Inputs Aider receives (files, prompts, post-conditions)
  * Outputs it returns (diffs, logs, status)
  * Validation rules applied after Aider runs (tests, lint, etc.)

This document **MUST** align with `AIDER-INT-001`.

### EXEC-DOC-006: Parallelism Documentation

* `docs/execution_model/PARALLEL_EXECUTION.md` **SHOULD** describe:

  * How stages and parallel tasks are derived from the DAG
  * Any resource or concurrency constraints (see `CONC-REG-001` if defined)
  * Examples of parallel vs sequential stages

---

## 4. Task Definitions

### TASK-DEF-001: Task Definition Location

* All canonical task definitions **MUST** reside under `schema/tasks/definitions/`.
* Each task definition file **SHOULD** be a single JSON file representing one task, or a JSON object containing an array of tasks.

### TASK-DEF-002: Task Definition Schema

Task definitions **MUST** conform to `schema/tasks/task_definition_v1.json`, which **MUST** include at least:

```json
{
  "task_id": "ulid-here",
  "name": "validate_file_structure",
  "executor": "aider|codex|tests|git",
  "inputs": {
    "path": { "type": "string", "required": true }
  },
  "outputs": {
    "is_valid": { "type": "bool" },
    "errors": { "type": "array", "items": "string" }
  },
  "preconditions": [
    "filesystem_accessible",
    "git_repo_clean"
  ],
  "postconditions": [
    "validation_complete",
    "results_logged"
  ],
  "dependencies": [],          // task_ids this task depends on
  "dependents": [],            // task_ids that depend on this task
  "max_runtime_seconds": 30,
  "retry_policy": {
    "strategy": "exponential_backoff",
    "max_attempts": 3,
    "initial_delay_seconds": 1
  },
  "worker_requirements": {
    "capabilities": ["filesystem", "python3"],
    "min_memory_mb": 512
  },
  "idempotent": true,
  "side_effects": ["writes_to_disk"],
  "rollback_handler": "cleanup_validation_artifacts"
}
```

### TASK-DEF-003: Phase/Workstream Binding

* Phase Specs and Workstream Bundles **MUST** reference tasks by `task_id` defined in `schema/tasks/definitions/`.
* Phase/Workstream documents **MAY** override `max_runtime_seconds` and `retry_policy` per task, but **MUST NOT** change `inputs`/`outputs` types.

---

## 5. DAG and Execution Plans

### DAG-VIEW-001: Workstream DAG Files

For each workstream instance, the repository **SHOULD** generate:

```text
workstreams/
  ws-<id>/
    bundle.json              # Existing bundle format
    dag.json                 # Graph structure (required for DAG)
    execution_plan.json      # Resolved execution order
    parallel_stages.json     # Explicit parallelism declaration (optional if in execution_plan)
```

### DAG-VIEW-002: DAG JSON Structure

`dag.json` **MUST** be structured so AI can understand task dependencies without code execution.

> Non-normative example:

```json
{
  "nodes": [
    {"task_id": "task_a", "type": "aider"},
    {"task_id": "task_b", "type": "tests"},
    {"task_id": "task_c", "type": "git"}
  ],
  "edges": [
    {"from": "task_a", "to": "task_b", "type": "completion"},
    {"from": "task_b", "to": "task_c", "type": "validation"}
  ]
}
```

### DAG-VIEW-003: Execution Plan Structure

`execution_plan.json` **MUST** make execution stages and parallelism explicit:

```json
{
  "stages": [
    {
      "stage": 1,
      "parallel_tasks": ["task_a"],
      "estimated_duration_seconds": 120
    },
    {
      "stage": 2,
      "parallel_tasks": ["task_b"],
      "depends_on_stages": [1]
    }
  ]
}
```

* Orchestrator scheduling logic **SHOULD** be derivable from this file without executing code.

---

## 6. Capability Catalog (PowerShell Orchestration)

### CAP-REG-001: Capability Catalog Location

* A PowerShell-based capability catalog **MUST** exist at:
  `capabilities/catalog.psd1`

### CAP-REG-002: Capability Entry Schema

Each capability entry in `catalog.psd1` **MUST** declare:

* Stable `CapabilityId`
* `Name`
* `Type` (e.g. `Autonomous`, `Interactive`)
* `Executor` path
* `Input` schema
* `Output` schema
* `Preconditions`
* `Postconditions`

> Non-normative example:

```powershell
@{
    Capabilities = @(
        @{
            CapabilityId = 'cap-ulid-001'
            Name         = 'WorkstreamOrchestration'
            Type         = 'Autonomous'
            Executor     = 'scripts/orchestrate_workstream.ps1'
            
            Input = @{
                WorkstreamId    = 'string'
                MaxParallelism  = 'int'
                ValidationLevel = 'enum[Basic,Full,Paranoid]'
            }
            
            Output = @{
                CompletedTasks = 'array[string]'
                FailedTasks    = 'array[string]'
                ExecutionLog   = 'path'
            }
            
            Preconditions = @(
                'Repository-CleanWorkingDirectory'
                'All-WorkerCapabilities-Available'
            )
            
            Postconditions = @(
                'All-Tasks-Completed-Or-Failed'
                'State-Persisted-To-Disk'
            )
        }
    )
}
```

---

## 7. Failure Modes and Error Handling

### ERR-FM-001: Failure Modes Catalog

* The repository **MUST** define a failure modes catalog at:
  `docs/failure_modes/CATALOG.md`

* Each failure mode entry **SHOULD** include:

  * Name
  * Detection mechanism
  * How it manifests in logs/events
  * Automatic recovery behavior
  * Required manual intervention (if any)

> Non-normative example:

```markdown
## Task Timeout
**Detection:** Task exceeds max_runtime_seconds  
**Manifestation:** `{"event":"task_timeout","task_id":"..."}` in execution log  
**Automatic Recovery:** Retry with exponential backoff (if retry_count < max_retries)  
**Manual Intervention:** Investigate worker logs, check for deadlock
```

### ERR-FM-002: Error Events

* Error-related events **MUST** be logged in the same JSONL event streams covered by `STATE-OBS-004`.
* Error policies and recovery behaviors **SHOULD** be additionally defined in a machine-readable policy file (e.g. `registry/error_policies.yaml`), but that file is out of scope for this spec.

---

## 8. Aider Integration Contract

### AIDER-INT-001: Aider as Worker

Aider **MUST** be treated as a *worker* under orchestration, not as a standalone tool.

The Aider integration spec **MUST** define:

1. **Execution Flow**

   * Workstream bundle creation
   * Task assignment to Aider
   * Aider receiving:

     * File context (`required_files`)
     * Prompt
     * Post-conditions / success criteria
   * Validation and rollback after Aider completes

2. **Context Management**

   * Max token context per task (`context_limit_tokens`)
   * Exact list of files to include (`required_files`)
   * Explicit statement that Aider **MUST NOT** see the entire codebase by default.

These details **MUST** be documented in `docs/execution_model/AIDER_INTEGRATION.md` (see `EXEC-DOC-005`).

---

## 9. State Machine Definitions

### SM-DEF-001: Task Lifecycle State Machine

* A machine-readable state machine definition **MUST** exist at:
  `docs/state_machines/task_lifecycle.yaml`

* It **MUST** define:

  * `initial_state`
  * All valid states
  * All transitions (`from`, `to`, `trigger`, optional `guard`)

> Non-normative example:

```yaml
name: Task Lifecycle State Machine
initial_state: PENDING

states:
  - name: PENDING
    description: Task created, waiting for dependencies
    
  - name: READY
    description: Dependencies satisfied, ready for worker assignment
    
  - name: RUNNING
    description: Assigned to worker, execution in progress
    
  - name: COMPLETED
    description: Successfully completed
    terminal: true
    
  - name: FAILED
    description: Execution failed
    terminal: false
    
  - name: RETRY_PENDING
    description: Waiting for retry backoff period

transitions:
  - from: PENDING
    to: READY
    trigger: all_dependencies_complete
    
  - from: READY
    to: RUNNING
    trigger: worker_assigned
    
  - from: RUNNING
    to: COMPLETED
    trigger: execution_success
    
  - from: RUNNING
    to: FAILED
    trigger: execution_failure
    guard: retry_count >= max_retries
    
  - from: RUNNING
    to: RETRY_PENDING
    trigger: execution_failure
    guard: retry_count < max_retries
    
  - from: RETRY_PENDING
    to: READY
    trigger: backoff_period_elapsed
```

* The task lifecycle states used in code and docs **MUST** be consistent with this definition.

---

## 10. Module and API Indexing

### MOD-IDX-001: Public API Index Files

* Each major Python module directory (e.g. `core/engine/`) **SHOULD** provide an `__init__.py` that:

  * Lists the public API (classes/functions intended for use)
  * Distinguishes public vs internal modules in docstring

> Non-normative example:

```python
"""
Core orchestration engine.

Public API:
- Orchestrator: Main orchestration coordinator
- Scheduler: DAG-based task scheduler
- Executor: Task execution manager
- CircuitBreaker: Failure isolation

Internal modules:
- tools: Tool adapter implementation
- recovery: Automatic recovery mechanisms
"""

from .orchestrator import Orchestrator
from .scheduler import Scheduler
from .executor import Executor
from .circuit_breaker import CircuitBreaker

__all__ = ['Orchestrator', 'Scheduler', 'Executor', 'CircuitBreaker']
```

This pattern **SHOULD** be followed so AI can clearly identify public surface area.

---

## 11. Reference Implementation (Non-Normative)

### IMPL-REF-001: PowerShell Reference Script

A reference implementation script **SHOULD** exist at:
`scripts/optimize_for_ai.ps1`

This script MAY:

* Create `.state/` subdirectories per `STATE-OBS-001`
* Generate stub execution model docs per `EXEC-DOC-001..006`
* Create an initial capability catalog per `CAP-REG-001`
* Create an initial state snapshot

> This script is **non-normative**.
> The authoritative behavior is defined by the requirement IDs in this spec.

---

## 12. Compliance

### COMPLIANCE-001

* A repository is **AI-Orch-Compliant** if it:

  * Satisfies all **MUST** requirements in this spec.
  * Documents all deviations from **SHOULD** requirements in a `docs/compliance/AI-ORCH-REPO-V1_DEVIATIONS.md` file.

### COMPLIANCE-002

* Automated validators and orchestrator sanity checks **SHOULD** verify:

  * Presence and basic shape of `.state/` files (`STATE-OBS-*`)
  * Existence and schema-conformance of task definitions (`TASK-DEF-*`)
  * Presence of DAG and execution plan files for active workstreams (`DAG-VIEW-*`)
  * Presence of failure modes catalog (`ERR-FM-*`)
  * Presence of Aider integration docs if Aider is enabled (`AIDER-INT-*`)

---

```
::contentReference[oaicite:0]{index=0}
```

---


```powershell
<#
.SYNOPSIS
  Validate repository compliance with AI-ORCH-REPO-V1.1 state & audit requirements.

.DESCRIPTION
  Checks the following requirement IDs:

    STATE-OBS-001  .state/ layout exists
    STATE-OBS-002  snapshots/ exists and contains JSON snapshots
    STATE-OBS-003  current.json exists, is valid JSON, atomic pattern ready
    STATE-OBS-004  transitions.jsonl exists and each line is valid JSON with required fields
    STATE-OBS-005  indices/ exists with required index files, valid JSON
    STATE-OBS-006  indices are derivable from current.json (basic sanity)
    AUDIT-001      Audit trail completeness (presence of snapshots + transitions)
    AUDIT-002      Audit retention doc exists

  Output:
    - Per-requirement PASS/FAIL
    - Detailed message per requirement
    - Overall summary
    - Exit code:
        0 if ALL checks PASS
        1 if ANY check FAILs

.NOTES
  Run from the repository root:

      pwsh scripts/validate/validate_state_obs.ps1

#>

[CmdletBinding()]
param(
    [switch]$VerboseOutput
)

$ErrorActionPreference = 'Stop'

#---------------------------#
# Utility: Result structure #
#---------------------------#

class ValidationResult {
    [string]$RequirementId
    [string]$Status    # 'PASS' or 'FAIL'
    [string]$Message

    ValidationResult([string]$RequirementId, [string]$Status, [string]$Message) {
        $this.RequirementId = $RequirementId
        $this.Status        = $Status
        $this.Message       = $Message
    }
}

$results = New-Object System.Collections.Generic.List[ValidationResult]

function Add-Result {
    param(
        [string]$RequirementId,
        [string]$Status,   # PASS / FAIL
        [string]$Message
    )
    $results.Add([ValidationResult]::new($RequirementId, $Status, $Message))
}

function Test-JsonFile {
    param(
        [string]$Path,
        [switch]$RequireSchemaVersion,
        [string]$Description = $null
    )

    if (-not (Test-Path $Path -PathType Leaf)) {
        throw "Missing JSON file: $Path$([string]::IsNullOrEmpty($Description) ? '' : " ($Description)")"
    }

    try {
        $content = Get-Content -Raw -Path $Path -ErrorAction Stop
        if ([string]::IsNullOrWhiteSpace($content)) {
            throw "File is empty: $Path"
        }

        $json = $content | ConvertFrom-Json -ErrorAction Stop

        if ($RequireSchemaVersion -and -not $json.PSObject.Properties.Name.Contains('schema_version')) {
            throw "Missing 'schema_version' field in JSON file: $Path"
        }

        return $true
    }
    catch {
        throw "Invalid JSON in $Path : $($_.Exception.Message)"
    }
}

#----------------------#
# Check: STATE-OBS-001 #
#----------------------#

try {
    $stateRoot = ".state"

    if (-not (Test-Path $stateRoot -PathType Container)) {
        Add-Result -RequirementId 'STATE-OBS-001' -Status 'FAIL' -Message "Missing .state/ directory."
    }
    else {
        $expectedSubdirs = @('snapshots', 'indices')
        $expectedFiles   = @('current.json', 'transitions.jsonl', 'health.json')

        $missingSubdirs = @()
        foreach ($d in $expectedSubdirs) {
            if (-not (Test-Path (Join-Path $stateRoot $d) -PathType Container)) {
                $missingSubdirs += $d
            }
        }

        $missingFiles = @()
        foreach ($f in $expectedFiles) {
            if (-not (Test-Path (Join-Path $stateRoot $f) -PathType Leaf)) {
                $missingFiles += $f
            }
        }

        if ($missingSubdirs.Count -eq 0 -and $missingFiles.Count -eq 0) {
            Add-Result -RequirementId 'STATE-OBS-001' -Status 'PASS' -Message ".state/ layout present (snapshots/, indices/, current.json, transitions.jsonl, health.json)."
        }
        else {
            $msg = @()
            if ($missingSubdirs.Count -gt 0) {
                $msg += "Missing subdirectories: $($missingSubdirs -join ', ')"
            }
            if ($missingFiles.Count -gt 0) {
                $msg += "Missing files: $($missingFiles -join ', ')"
            }
            Add-Result -RequirementId 'STATE-OBS-001' -Status 'FAIL' -Message ($msg -join '; ')
        }
    }
}
catch {
    Add-Result -RequirementId 'STATE-OBS-001' -Status 'FAIL' -Message $_.Exception.Message
}

#----------------------#
# Check: STATE-OBS-002 #
#----------------------#

try {
    $snapshotsDir = ".state/snapshots"

    if (-not (Test-Path $snapshotsDir -PathType Container)) {
        Add-Result -RequirementId 'STATE-OBS-002' -Status 'FAIL' -Message "Missing .state/snapshots/ directory."
    }
    else {
        $snapshotFiles = Get-ChildItem -Path $snapshotsDir -Filter '*.json' -File -ErrorAction Stop

        if ($snapshotFiles.Count -eq 0) {
            Add-Result -RequirementId 'STATE-OBS-002' -Status 'FAIL' -Message "No snapshot JSON files found in .state/snapshots/."
        }
        else {
            $invalidSnapshots = @()
            foreach ($sf in $snapshotFiles) {
                try {
                    Test-JsonFile -Path $sf.FullName -RequireSchemaVersion
                }
                catch {
                    $invalidSnapshots += "$($sf.Name): $($_.Exception.Message)"
                }
            }

            if ($invalidSnapshots.Count -eq 0) {
                Add-Result -RequirementId 'STATE-OBS-002' -Status 'PASS' -Message "Snapshots present and JSON-valid with schema_version."
            }
            else {
                Add-Result -RequirementId 'STATE-OBS-002' -Status 'FAIL' -Message "Invalid snapshots: $($invalidSnapshots -join ' | ')"
            }
        }
    }
}
catch {
    Add-Result -RequirementId 'STATE-OBS-002' -Status 'FAIL' -Message $_.Exception.Message
}

#----------------------#
# Check: STATE-OBS-003 #
#----------------------#

try {
    $currentPath = ".state/current.json"

    if (-not (Test-Path $currentPath -PathType Leaf)) {
        Add-Result -RequirementId 'STATE-OBS-003' -Status 'FAIL' -Message "Missing .state/current.json."
    }
    else {
        try {
            Test-JsonFile -Path $currentPath -RequireSchemaVersion
            # We can't fully verify atomic rename behavior here, but we can at least
            # ensure there is no lingering .tmp file suggesting incomplete writes.
            $tmpPath = ".state/current.json.tmp"
            if (Test-Path $tmpPath -PathType Leaf) {
                Add-Result -RequirementId 'STATE-OBS-003' -Status 'FAIL' -Message ".state/current.json.tmp exists; indicates non-atomic or incomplete update."
            }
            else {
                Add-Result -RequirementId 'STATE-OBS-003' -Status 'PASS' -Message "current.json present, JSON-valid with schema_version; no stale .tmp file detected."
            }
        }
        catch {
            Add-Result -RequirementId 'STATE-OBS-003' -Status 'FAIL' -Message $_.Exception.Message
        }
    }
}
catch {
    Add-Result -RequirementId 'STATE-OBS-003' -Status 'FAIL' -Message $_.Exception.Message
}

#----------------------#
# Check: STATE-OBS-004 #
#----------------------#

try {
    $transitionsPath = ".state/transitions.jsonl"

    if (-not (Test-Path $transitionsPath -PathType Leaf)) {
        Add-Result -RequirementId 'STATE-OBS-004' -Status 'FAIL' -Message "Missing .state/transitions.jsonl."
    }
    else {
        $lines = Get-Content -Path $transitionsPath -ErrorAction Stop
        if ($lines.Count -eq 0) {
            Add-Result -RequirementId 'STATE-OBS-004' -Status 'FAIL' -Message "transitions.jsonl exists but is empty."
        }
        else {
            $lineErrors = @()
            $lineNumber = 0

            foreach ($line in $lines) {
                $lineNumber++
                if ([string]::IsNullOrWhiteSpace($line)) {
                    continue
                }
                try {
                    $obj = $line | ConvertFrom-Json -ErrorAction Stop

                    $requiredFields = @('timestamp', 'actor', 'context', 'severity')
                    $hasEvent        = $obj.PSObject.Properties.Name.Contains('event') -or
                                       $obj.PSObject.Properties.Name.Contains('event_type')

                    foreach ($f in $requiredFields) {
                        if (-not $obj.PSObject.Properties.Name.Contains($f)) {
                            throw "Missing required field '$f'"
                        }
                    }

                    if (-not $hasEvent) {
                        throw "Missing 'event' or 'event_type' field"
                    }

                }
                catch {
                    $lineErrors += "Line $lineNumber: $($_.Exception.Message)"
                }
            }

            if ($lineErrors.Count -eq 0) {
                Add-Result -RequirementId 'STATE-OBS-004' -Status 'PASS' -Message "transitions.jsonl present; all lines valid JSON with required fields."
            }
            else {
                Add-Result -RequirementId 'STATE-OBS-004' -Status 'FAIL' -Message "Invalid transition entries: $($lineErrors -join ' | ')"
            }
        }
    }
}
catch {
    Add-Result -RequirementId 'STATE-OBS-004' -Status 'FAIL' -Message $_.Exception.Message
}

#----------------------#
# Check: STATE-OBS-005 #
#----------------------#

try {
    $indicesDir = ".state/indices"
    if (-not (Test-Path $indicesDir -PathType Container)) {
        Add-Result -RequirementId 'STATE-OBS-005' -Status 'FAIL' -Message "Missing .state/indices/ directory."
    }
    else {
        $requiredIndexFiles = @(
            "tasks_by_status.json",
            "blocked_tasks.json",
            "worker_capabilities.json"
        )

        $missing = @()
        $invalid = @()

        foreach ($fileName in $requiredIndexFiles) {
            $fullPath = Join-Path $indicesDir $fileName
            if (-not (Test-Path $fullPath -PathType Leaf)) {
                $missing += $fileName
                continue
            }
            try {
                Test-JsonFile -Path $fullPath
            }
            catch {
                $invalid += "$fileName: $($_.Exception.Message)"
            }
        }

        if ($missing.Count -eq 0 -and $invalid.Count -eq 0) {
            Add-Result -RequirementId 'STATE-OBS-005' -Status 'PASS' -Message "Required indices present and JSON-valid."
        }
        else {
            $parts = @()
            if ($missing.Count -gt 0) {
                $parts += "Missing index files: $($missing -join ', ')"
            }
            if ($invalid.Count -gt 0) {
                $parts += "Invalid index files: $($invalid -join ' | ')"
            }
            Add-Result -RequirementId 'STATE-OBS-005' -Status 'FAIL' -Message ($parts -join '; ')
        }
    }
}
catch {
    Add-Result -RequirementId 'STATE-OBS-005' -Status 'FAIL' -Message $_.Exception.Message
}

#----------------------#
# Check: STATE-OBS-006 #
# (basic sanity only)  #
#----------------------#

try {
    $currentPath = ".state/current.json"
    $indicesDir  = ".state/indices"

    if ((Test-Path $currentPath -PathType Leaf) -and (Test-Path $indicesDir -PathType Container)) {
        try {
            $current = (Get-Content -Raw -Path $currentPath | ConvertFrom-Json -ErrorAction Stop)

            # We don’t know exact schema, but we can at least ensure indices
            # reference known task IDs / shapes when both are present.
            $idxTasksByStatusPath = Join-Path $indicesDir "tasks_by_status.json"
            if (Test-Path $idxTasksByStatusPath -PathType Leaf) {
                $idxTasksByStatus = Get-Content -Raw -Path $idxTasksByStatusPath | ConvertFrom-Json -ErrorAction Stop

                # If current.json has a tasks collection, ensure IDs appear in index
                $currentTaskIds = @()
                if ($current.tasks) {
                    foreach ($t in $current.tasks) {
                        if ($t.task_id) { $currentTaskIds += $t.task_id }
                    }
                }

                if ($currentTaskIds.Count -gt 0 -and $idxTasksByStatus.PSObject.Properties.Count -gt 0) {
                    # Check that at least some task IDs show up somewhere in the index structure (best-effort)
                    $idxText = $idxTasksByStatus | ConvertTo-Json -Depth 10
                    $missingInIndex = @()
                    foreach ($tid in $currentTaskIds | Select-Object -Unique) {
                        if ($idxText -notlike "*$tid*") {
                            $missingInIndex += $tid
                        }
                    }

                    if ($missingInIndex.Count -eq $currentTaskIds.Count) {
                        Add-Result -RequirementId 'STATE-OBS-006' -Status 'FAIL' -Message "tasks_by_status.json appears unrelated to tasks in current.json (no task_ids found)."
                    }
                    else {
                        Add-Result -RequirementId 'STATE-OBS-006' -Status 'PASS' -Message "Indices appear derivable from current.json (task_ids overlap detected)."
                    }
                }
                else {
                    # Not enough structure to check overlap; treat as WARN-ish PASS
                    Add-Result -RequirementId 'STATE-OBS-006' -Status 'PASS' -Message "current.json and indices present, but insufficient shared structure for deep derivation check."
                }
            }
            else {
                Add-Result -RequirementId 'STATE-OBS-006' -Status 'FAIL' -Message "tasks_by_status.json missing; cannot verify derivation from current.json."
            }
        }
        catch {
            Add-Result -RequirementId 'STATE-OBS-006' -Status 'FAIL' -Message "Failed to compare indices vs current.json: $($_.Exception.Message)"
        }
    }
    else {
        Add-Result -RequirementId 'STATE-OBS-006' -Status 'FAIL' -Message "Either .state/current.json or .state/indices/ missing; cannot verify derivation."
    }
}
catch {
    Add-Result -RequirementId 'STATE-OBS-006' -Status 'FAIL' -Message $_.Exception.Message
}

#----------------------#
# Check: AUDIT-001     #
#----------------------#

try {
    $snapshotsDir = ".state/snapshots"
    $transitionsPath = ".state/transitions.jsonl"

    $snapshotsOk = Test-Path $snapshotsDir -PathType Container
    $transitionsOk = Test-Path $transitionsPath -PathType Leaf

    if ($snapshotsOk -and $transitionsOk) {
        Add-Result -RequirementId 'AUDIT-001' -Status 'PASS' -Message "Snapshots directory and transitions.jsonl present; basic audit trail structure exists."
    }
    else {
        $details = @()
        if (-not $snapshotsOk) { $details += "missing .state/snapshots/" }
        if (-not $transitionsOk) { $details += "missing .state/transitions.jsonl" }
        Add-Result -RequirementId 'AUDIT-001' -Status 'FAIL' -Message "Audit trail incomplete: $($details -join '; ')."
    }
}
catch {
    Add-Result -RequirementId 'AUDIT-001' -Status 'FAIL' -Message $_.Exception.Message
}

#----------------------#
# Check: AUDIT-002     #
#----------------------#

try {
    $auditDocPath = "docs/operations/AUDIT_RETENTION.md"

    if (Test-Path $auditDocPath -PathType Leaf) {
        Add-Result -RequirementId 'AUDIT-002' -Status 'PASS' -Message "Audit retention policy doc present at $auditDocPath."
    }
    else {
        Add-Result -RequirementId 'AUDIT-002' -Status 'FAIL' -Message "Missing docs/operations/AUDIT_RETENTION.md (required by AUDIT-002)."
    }
}
catch {
    Add-Result -RequirementId 'AUDIT-002' -Status 'FAIL' -Message $_.Exception.Message
}

#----------------------#
# Output + Exit Code   #
#----------------------#

Write-Host ""
Write-Host "=== AI-ORCH-REPO V1.1 State & Audit Validation ===" -ForegroundColor Cyan
Write-Host ""

# Sort by RequirementId for stable output
$resultsSorted = $results | Sort-Object RequirementId

foreach ($r in $resultsSorted) {
    $color = if ($r.Status -eq 'PASS') { 'Green' } else { 'Red' }
    Write-Host ("[{0}] {1} - {2}" -f $r.Status, $r.RequirementId, $r.Message) -ForegroundColor $color
}

$failed = $resultsSorted | Where-Object { $_.Status -eq 'FAIL' }

Write-Host ""
if ($failed.Count -eq 0) {
    Write-Host "All checks PASSED." -ForegroundColor Green
    $exitCode = 0
}
else {
    Write-Host "One or more checks FAILED:" -ForegroundColor Red
    foreach ($r in $failed) {
        Write-Host ("  - {0}: {1}" -f $r.RequirementId, $r.Message) -ForegroundColor Red
    }
    $exitCode = 1
}

if ($VerboseOutput) {
    Write-Host ""
    Write-Host "Raw results object (for tooling):" -ForegroundColor Yellow
    $resultsSorted | ConvertTo-Json -Depth 5
}

exit $exitCode
```
