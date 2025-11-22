
---

# TERMS_SPEC_V1

## 0. Purpose

This document defines **canonical terminology** for the development pipeline so that all AIs and tools:

* Use the same words with the same meanings.
* Model work in a consistent, machine-readable way.
* Avoid confusion between “phase plan”, “phase”, “workstream”, “task”, and “CLI tool instance”.

This spec is **project-agnostic** and should be reused across modules.

---

## 1. TERM: PHASE_PLAN

**ID:** `TERM.PHASE_PLAN`
**Type:** Top-level planning artifact

### 1.1 Definition

A **Phase Plan** is the **development plan** for a project or section, defined *before coding starts*, and broken down into a sequence of **phases**.

It is:

* The **big map** of the work.
* The primary reference for:

  * where we are in the development journey,
  * which phases exist,
  * which **workstreams** and tasks are allowed.

### 1.2 Role in the System

* Owns:

  * the list of phases,
  * the list of workstreams associated with this scope,
  * the constraints and policies for execution (parallelism, gates, etc.).
* Does **not** directly edit files itself; it **describes** the work.

### 1.3 Key Properties (Conceptual)

* `id` – stable identifier for the phase plan.
* `scope` – project or section it applies to.
* `phases[]` – ordered list of phase definitions.
* `workstreams[]` – associated workstreams (see `TERM.WORKSTREAM`).
* `policies` – global rules (parallelism, error handling, OS modes, etc.).

---

## 2. TERM: PHASE

**ID:** `TERM.PHASE`
**Type:** Stage marker inside a Phase Plan

### 2.1 Definition

A **Phase** is a named **stage** inside a Phase Plan (e.g., “Spec”, “Implementation”, “Tests”, “Docs”, “Integration”).

It describes ***when*** certain kinds of work happen, not the fine-grained steps themselves.

### 2.2 Role in the System

* Provides clear **progress markers**:

  * “We are currently in PH-02: Implementation.”
* Defines **allowed or expected work**:

  * which kinds of tasks/workstreams belong in this stage.
* Can host:

  * multiple workstreams,
  * and tasks from workstreams that span multiple phases.

### 2.3 Key Properties (Conceptual)

* `id` – phase identifier (e.g., `PH-01-SPEC`).
* `name` – human-meaningful label.
* `order` – position in the Phase Plan’s timeline.
* `allowed_kinds` – which `kind` of tasks are expected (design/impl/tests/docs/etc.).
* `gates` – conditions that must be satisfied to move past this phase (e.g., test gates).

---

## 3. TERM: WORKSTREAM

**ID:** `TERM.WORKSTREAM`
**Type:** Independent execution lane of edits

### 3.1 Definition

A **Workstream** is an **independent path of executable work** within a Phase Plan.

Each workstream:

* Represents a coherent “lane of work” (e.g., “implement feature X”, “refactor module Y”, “write docs for Z”).
* Is defined so that its edits can be reasoned about separately from other workstreams.
* Has a `files_scope` that allows safe parallel execution when combined with other workstreams.

### 3.2 Role in the System

* Connects the **high-level plan** (Phase Plan) to **executable work**:

  * a Phase Plan may define one or many workstreams.
* Supports **parallelism**:

  * multiple workstreams from the same Phase Plan may run simultaneously **if** their file scopes and dependencies allow it.
* Can:

  * live entirely in one phase, **or**
  * have tasks in multiple phases of the same Phase Plan.

### 3.3 Independence / Parallel-Safety

A Workstream is considered **parallel-safe** with another if:

* Their `files_scope.writes` do not overlap *in the same sandbox*, **or**
* They operate in different sandboxes/branches/worktrees.

This is the primary unit for “independent path” in the user’s mental model.

### 3.4 Key Properties (Conceptual)

* `id` – workstream identifier.
* `phase_plan_id` – owning phase plan.
* `phases[]` – list of phases where this workstream has tasks.
* `files_scope` – read/write sets that define what the workstream may touch.
* `responsibility` – description of what the workstream is meant to achieve.
* `tasks[]` – list of tasks (see `TERM.TASK`).

---

## 4. TERM: TASK

**ID:** `TERM.TASK`
**Type:** Smallest schedulable unit

### 4.1 Definition

A **Task** is the smallest **executable unit** of work inside a workstream – what a CLI tool instance actually does in one shot.

Examples:

* “Generate handler skeleton for API X”
* “Write initial unit tests for module Y”
* “Run lint and tests on files changed in this workstream”
* “Refactor function Z for readability”

### 4.2 Role in the System

* Tasks are the **nodes** in the DAG that the execution kernel schedules.
* Tasks belong to:

  * a single workstream,
  * a specific phase (logical association),
  * and have precise dependencies (`depends_on`) and file scopes.

### 4.3 Key Properties (Conceptual)

* `id` – task identifier.
* `workstream_id` – owning workstream.
* `phase_id` – phase this task belongs to logically.
* `kind` – design / implementation / test / docs / infra / refactor / background / spike / etc.
* `depends_on[]` – list of prerequisite tasks.
* `files_scope` – fine-grained read/write scope for this task.
* `parallel_ok` – whether this task is logically safe to run in parallel if other constraints are met.
* `conflict_group` – label to prevent parallel running with certain other tasks.
* `tool_preference` – hint which CLI tool is best suited.
* `priority` – foreground vs background.
* `state` – `PENDING`, `READY`, `RUNNING`, `SUCCEEDED`, `FAILED`, `CANCELLED`.

---

## 5. TERM: CLI_TOOL_INSTANCE (WORKER)

**ID:** `TERM.CLI_TOOL_INSTANCE`
**Alias:** `TERM.WORKER`
**Type:** Execution agent

### 5.1 Definition

A **CLI Tool Instance** (or **Worker**) is a running CLI process (e.g., Claude Code CLI, Codex CLI, Aider, etc.) that executes tasks on behalf of the system.

Each worker:

* Is typically bound to **one active foreground workstream** at a time.
* May execute **background tasks** that either:

  * speed up that same workstream (lint/tests/docs),
  * or work on other workstreams in a safe sandbox or non-conflicting file scope.

### 5.2 Role in the System

* Acts as the **physical executor** of tasks.
* Pulls tasks from the scheduler (or is assigned by the kernel).
* Operates within:

  * a specific sandbox or branch/worktree,
  * a defined `role` (impl / tests / docs / background / refactor / integration / spike),
  * resource and policy constraints (parallelism limits, OS mode, etc.).

### 5.3 Safety & Scope

To preserve determinism and avoid conflicts:

* A worker’s **foreground tasks** must obey:

  * non-overlapping `files_scope.writes` with other workers sharing the same sandbox,
  * or use an isolated sandbox/branch.
* **Background tasks** executed by a worker must either:

  * not modify mainline source files, **or**
  * do so only through controlled, conflict-safe mechanisms (e.g., patches applied via integration worker).

### 5.4 Key Properties (Conceptual)

* `id` – worker identifier.
* `tool` – which CLI tool (Claude Code, Codex, etc.).
* `role` – main responsibility (impl / tests / docs / background / sweeper / integration / spike).
* `sandbox` – branch/worktree or environment it operates in.
* `allowed_workstreams[]` – which workstreams it may serve.
* `state` – `SPAWNING`, `IDLE`, `BUSY`, `DRAINING`, `TERMINATED`.
* `current_task_id` – task it is currently executing, if any.
* `health` – heartbeat data, recent failures, etc.

---

## 6. RELATIONSHIPS (SUMMARY)

* A **Phase Plan** (`PHASE_PLAN`)

  * owns **Phases** (`PHASE`) and **Workstreams** (`WORKSTREAM`).
* A **Phase**

  * is a stage in the plan; tasks from many workstreams can map into it.
* A **Workstream**

  * is an independent execution lane tied to a `PHASE_PLAN`,
  * may span one or multiple `PHASE`s,
  * contains multiple **Tasks**.
* A **Task**

  * belongs to one **Workstream** and one logical **Phase**,
  * is the atomic schedulable unit.
* A **CLI Tool Instance / Worker**

  * executes **Tasks**,
  * typically focuses on one foreground **Workstream** at a time,
  * can run background tasks when parallelism and policies allow.


---

## 1. Core Execution / Topology Terms

### 1.1 TERM: DAG

**Definition:**
The **Directed Acyclic Graph** that represents all **Tasks** and their `depends_on` relationships for a given Phase Plan (or subset). It’s the canonical structure the kernel uses to:

* determine valid execution order,
* compute parallelism opportunities,
* detect cycles and impossible constraints.

---

### 1.2 TERM: NODE_STATE

**Definition:**
The lifecycle state of a **Task** in the DAG. Canonical values:

* `PENDING` – defined but not yet eligible to run.
* `READY` – all dependencies satisfied; can be scheduled.
* `RUNNING` – currently being executed by a worker.
* `SUCCEEDED` – finished successfully.
* `FAILED` – finished with error, routed to error handling.
* `CANCELLED` – intentionally stopped; will not be retried.

(You already use these implicitly; worth defining as a formal term.)

---

## 2. Scope & Isolation Terms

### 2.1 TERM: FILE_SCOPE

**Definition:**
The declared **read/write footprint** of a Task or Workstream:

* `reads` – files or patterns the unit may read.
* `writes` – files or patterns the unit may modify.

It is the primary mechanism for:

* deciding which Workstreams are safe to run in parallel,
* detecting conflicts,
* building integration/merge logic.

---

### 2.2 TERM: SANDBOX

**Definition:**
An isolated working environment for a Worker. Typically:

* a git branch,
* a git worktree,
* or a separate clone / directory.

Sandbox boundaries guarantee:

* changes made inside do not directly affect mainline,
* multiple Workers can run in parallel across different sandboxes without collisions.

---

### 2.3 TERM: BACKGROUND_TASK

**Definition:**
A Task with `priority = background` whose execution:

* does **not** block the main foreground Workstream’s progress,
* often runs lower priority,
* usually writes only to logs, build artifacts, ledgers, or non-critical branches.

Examples: lint runs, quick tests, metrics collection, doc indexing.

---

## 3. Parallelism & Control Terms

### 3.1 TERM: PARALLELISM_CHART

**Definition:**
A time/step-oriented profile derived from the DAG that describes, for each logical stage:

* how many Tasks are **READY** and **parallel-safe**,
* how many are actually being run.

The chart is used as a **control signal** to decide:

* how many Workers to spin up,
* how many background jobs to allow,
* when to scale in/out MCP services or workers.

---

### 3.2 TERM: OS_MODE

**Definition:**
A high-level configuration of the host operating system’s behavior during execution. Canonical examples:

* `OS_MODE_NORMAL` – no special restrictions.
* `OS_MODE_FOCUS_DEV` – some non-essential apps/services suppressed.
* `OS_MODE_CRITICAL_PIPELINE` – strongest “development blackout”; only essential services + pipeline.

OS_MODE is declared per Phase/Workstream and enforced by scripts/automations.

---

### 3.3 TERM: CIRCUIT_BREAKER

**Definition:**
A policy component that monitors system resources (CPU, RAM, IO, etc.) and enforces:

* **soft limits** – stop scaling out, throttle background work.
* **hard limits** – stop scheduling new tasks, possibly drain/kill low-priority workers.

Goal: protect the machine from overload and keep the pipeline from crashing the system.

---

## 4. MCP & Service Terms

### 4.1 TERM: MCP_SERVICE

**Definition:**
Any Model Context Protocol (MCP) server or similar external “service agent” that provides capabilities to Workers, such as:

* filesystem access,
* GitHub access,
* Jira/issue tracking,
* other context sources.

The kernel manages MCP_SERVICE lifecycle:

* start/stop,
* health checks,
* mapping which Workers/tasks may use which services.

---

## 5. Error & Recovery Terms

### 5.1 TERM: ERROR_EVENT

**Definition:**
A structured record created whenever a Task, Worker, MCP_SERVICE, or system-level component fails or behaves unexpectedly.

Contains:

* error type (e.g., `E_TOOL_FAILURE`, `E_MCP_FAILURE`, `E_RESOURCE_LIMIT`, `E_PLAN_CONSISTENCY`, etc.),
* phase_id, workstream_id, task_id, worker_id, sandbox,
* description and context (logs, exit codes, resource snapshot),
* timestamp and sequence.

---

### 5.2 TERM: ERROR_PIPELINE (ERR_EXEC)

**Definition:**
A deterministic **state machine** applied to ERROR_EVENTs to decide:

* retry strategies,
* context repair steps,
* when to switch tools,
* when to split tasks,
* when to escalate to stronger agents,
* when to escalate to human,
* when to quarantine.

This is the execution-level analogue of your file error module.

---

### 5.3 TERM: SELF_HEAL_POLICY

**Definition:**
A per-task or per-phase configuration that defines:

* maximum self-healing attempts,
* allowed strategies (retry same tool, switch tool, split task, repair context),
* escalation path (agent review → human review).

The ERROR_PIPELINE uses SELF_HEAL_POLICY to make decisions automatically.

---

### 5.4 TERM: CHECKPOINT

**Definition:**
A persisted snapshot of:

* DAG + NODE_STATE set,
* worker states,
* OS_MODE,
* active sandboxes/branches.

Used for:

* crash recovery,
* rollback to safe states,
* controlled replay / what-if analysis.

---

### 5.5 TERM: COMPENSATION_ACTION

**Definition:**
A defined **undo** or mitigation step associated with a Phase or Task, used when:

* later work reveals that earlier changes were wrong/harmful,
* a rollback is required beyond simple git revert.

It’s the development-side application of the **Saga pattern**.

---

## 6. Test & Quality Terms

### 6.1 TERM: GATE / TEST_GATE

**Definition:**
A synchronization point in the Phase Plan where progression or merging is **blocked** until certain validation tasks succeed.

Examples:

* `GATE_LINT`, `GATE_UNIT`, `GATE_INTEGRATION`, `GATE_SECURITY`.

Gates:

* consume test results,
* can create new tasks (fixes),
* control when integration/merge phases are allowed to proceed.

---

## 7. Cost & Human Interaction Terms

### 7.1 TERM: COST_POLICY / BUDGET

**Definition:**
Configuration describing:

* maximum allowed cost for a project/phase,
* per-task or per-worker cost caps,
* desired tradeoff between speed and spend.

Used by the kernel to:

* throttle parallelism,
* deprioritize low-value tasks,
* require human approval when approaching limits.

---

### 7.2 TERM: HUMAN_REVIEW_TASK

**Definition:**
A special Task created when:

* SELF_HEAL_POLICY is exhausted, **or**
* policies require human decision (e.g., budget override, risky merge).

It includes:

* condensed context from ERROR_EVENTs and execution history,
* recommended actions from agents,
* a place for the human to submit structured decisions that flow back into the system.

---

## 8. Core Data Structures

### 8.1 TERM: BUNDLE

**ID:** `TERM.BUNDLE`
**Type:** Data artifact

**Definition:**
A **Bundle** is a JSON file (conforming to `workstream.schema.json`) that contains the complete definition of a **WORKSTREAM**.

The bundle file:

* is the **single source of truth** for a workstream's metadata,
* contains: `id`, `files_scope`, `files_create`, `tasks`, `depends_on`, `acceptance_tests`, gate requirements, tool preferences, and optional advanced properties (parallelism hints, cost limits, compensation actions, test gates),
* is loaded by `core/state/bundles.py` and validated against the JSON schema,
* may be generated manually, from an OpenSpec change proposal, or by the planner.

**Location:** Typically stored in `workstreams/*.json`

**Key Properties:**
* `id` – unique workstream identifier (e.g., `ws-feature-x`)
* `openspec_change` – links to OpenSpec change proposal
* `ccpm_issue` – links to GitHub/CCPM issue
* `gate` – minimum approval level required
* `files_scope` – files this workstream may modify
* `files_create` – files this workstream may create
* `tasks` – high-level task descriptions
* `acceptance_tests` – validation criteria
* `depends_on` – upstream workstream dependencies
* `tool` – primary tool identifier (DEPRECATED; use `capability`)
* `capability` – AIM capability for routing (e.g., `code_generation`, `linting`)
* `circuit_breaker`, `metadata`, `parallel_ok`, `conflict_group`, `kind`, `priority`, `estimated_context_tokens`, `max_cost_usd`, `compensation_actions`, `test_gates` – advanced orchestration properties

**Related Terms:** WORKSTREAM, OPENSPEC, SIDECAR, LEDGER

---

### 8.2 TERM: RUN

**ID:** `TERM.RUN`
**Type:** Execution instance

**Definition:**
A **Run** is a single execution instance of one or more **WORKSTREAM**s.

Each run:

* has a unique `run_id`,
* tracks lifecycle state: `pending`, `running`, `succeeded`, `failed`, `cancelled`,
* persists to the SQLite database (`runs` table),
* coordinates one or more workstreams,
* maintains execution metadata (timestamps, status, metadata JSON),
* is the top-level correlation identifier for all steps, events, and errors during execution.

**Database Table:** `runs`

**Key Properties:**
* `run_id` – unique identifier (e.g., `run-20251122-abc123`)
* `status` – current lifecycle state
* `created_at` – ISO 8601 UTC timestamp
* `updated_at` – ISO 8601 UTC timestamp
* `metadata_json` – arbitrary metadata dictionary

**Related Terms:** WORKSTREAM, STEP, EVENT, LEDGER

**Implementation:** `core/state/crud.py` (CRUD operations)

---

### 8.3 TERM: STEP

**ID:** `TERM.STEP`
**Type:** Execution unit (granular)

**Definition:**
A **Step** (or **Step Attempt**) is a finer-grained execution record within a **TASK**.

Each step:

* represents one attempt to execute a portion of a task (e.g., single tool invocation),
* is recorded in the `step_attempts` database table,
* tracks: command, exit code, stdout, stderr, duration, retry count,
* enables **retry logic** – a task may have multiple step attempts if failures occur,
* is the level at which **CIRCUIT_BREAKER** and **RECOVERY_MANAGER** operate.

**Database Table:** `step_attempts`

**Key Properties:**
* `id` – auto-incremented step attempt ID
* `run_id` – owning run
* `ws_id` – owning workstream
* `step_idx` – logical step index in workstream
* `attempt` – retry attempt number (1-indexed)
* `status` – `running`, `success`, `failed`, etc.
* `started_at`, `completed_at` – timestamps
* `exit_code`, `stdout`, `stderr` – tool invocation results
* `retry_eligible` – whether this step can be retried

**Related Terms:** TASK, RUN, WORKSTREAM, CIRCUIT_BREAKER

**Implementation:** `core/state/crud.py`, `core/engine/executor.py`

---

### 8.4 TERM: SIDECAR

**ID:** `TERM.SIDECAR`
**Type:** Metadata file

**Definition:**
A **Sidecar** is a YAML metadata file (`.sidecar.yaml`) that accompanies a specification document and provides:

* document-level metadata (ID, title, version, category, authors, tags, dependencies, status, checksum),
* paragraph-level addressing (anchor, start/end lines, mfid, id),
* stable cross-referencing and change tracking for specifications.

Sidecars enable:

* precise paragraph-level references in workstream tasks,
* change detection via checksums (mfid – multi-file identifier),
* dependency tracking between specs,
* versioning and approval workflows.

**Schema:** `schema/sidecar_metadata.schema.yaml`

**Key Properties (Document Level):**
* `document_id`, `title`, `version`, `category`, `last_updated`, `authors`, `tags`, `depends_on`, `status`, `checksum`, `file`, `mfid`

**Key Properties (Paragraph Level):**
* `paragraphs[]` – array of paragraph metadata
  * `anchor` – paragraph identifier (e.g., `p-42`)
  * `start_line`, `end_line` – line range
  * `mfid` – paragraph-level checksum
  * `id` – stable paragraph ID

**Related Terms:** OPENSPEC, BUNDLE, MANIFEST

**Implementation:** `specifications/tools/`, `docs/spec/`

---

### 8.5 TERM: LEDGER

**ID:** `TERM.LEDGER`
**Type:** Audit log

**Definition:**
The **Ledger** is an append-only audit trail (stored in `.ledger/`) that records:

* all execution events,
* tool invocations,
* state transitions,
* error occurrences,
* file lifecycle changes.

The ledger provides:

* **immutable history** for debugging and compliance,
* **replay capability** for what-if analysis,
* **audit trail** for security and traceability,
* typically stored as JSONL (JSON Lines) files, one line per event.

**Location:** `.ledger/` directory (gitignored)

**Related Terms:** EVENT, RUN, AUDIT_LOG, CHECKPOINT

---

### 8.6 TERM: EVENT

**ID:** `TERM.EVENT`
**Type:** System event record

**Definition:**
An **Event** is a structured record emitted by the system when significant actions occur.

Events are:

* published to the **EVENT_BUS**,
* persisted to the **LEDGER**,
* optionally stored in the `events` database table for querying,
* used for monitoring, debugging, and coordination.

**Event Types (examples):**
* Worker events: `WORKER_SPAWNED`, `WORKER_TERMINATED`
* Task events: `TASK_ASSIGNED`, `TASK_STARTED`, `TASK_COMPLETED`, `TASK_FAILED`
* Job/Workstream events: `JOB_CREATED`, `JOB_STARTED`, `JOB_COMPLETED`, `JOB_FAILED`
* Tool events: `TOOL_INVOKED`, `TOOL_SUCCEEDED`, `TOOL_FAILED`, `TOOL_TIMEOUT`
* File lifecycle events: `FILE_DISCOVERED`, `FILE_CLASSIFIED`, `FILE_STATE_CHANGED`, `FILE_COMMITTED`, `FILE_QUARANTINED`
* Error events: `ERROR_RAISED`, `ERROR_RESOLVED`
* Circuit breaker events: `CIRCUIT_OPENED`, `CIRCUIT_CLOSED`, `CIRCUIT_HALF_OPEN`
* System events: `HEARTBEAT`, `MERGE_CONFLICT`, `RESOURCE_LIMIT`

**Key Properties:**
* `event_type` – type from EventType enum
* `severity` – DEBUG, INFO, WARNING, ERROR, CRITICAL
* `timestamp` – ISO 8601 UTC
* `run_id`, `workstream_id`, `job_id`, `file_id` – correlation IDs
* `payload` – event-specific data
* `source` – component that emitted the event

**Related Terms:** EVENT_BUS, LEDGER, ERROR_EVENT

**Implementation:** `core/engine/event_bus.py`

---

### 8.7 TERM: MANIFEST

**ID:** `TERM.MANIFEST`
**Type:** Plugin metadata file

**Definition:**
A **Manifest** is a JSON file (`manifest.json`) that describes a detection **PLUGIN**.

Each manifest contains:

* `plugin_id` – unique plugin identifier (e.g., `python_ruff`)
* `name` – human-readable name
* `file_extensions` – file types the plugin handles (e.g., `["py"]`)
* `requires` – prerequisite plugins (dependencies)
* `tool` – external tool metadata (e.g., success codes)
* optional: version, author, capabilities, configuration schema

**Purpose:**
* enables **plugin discovery** by the `error/engine/plugin_manager.py`,
* defines plugin contract and capabilities,
* supports dependency ordering (e.g., `black` runs before `ruff`).

**Location:** `error/plugins/<plugin_name>/manifest.json`

**Example:**
```json
{
  "plugin_id": "python_ruff",
  "name": "Ruff Linter",
  "file_extensions": ["py"],
  "requires": ["python_black_fix"],
  "tool": {
    "success_codes": [0, 1]
  }
}
```

**Related Terms:** PLUGIN, ERROR_PIPELINE

**Implementation:** `error/engine/plugin_manager.py`

---

## 9. Tool & Integration Layer

### 9.1 TERM: ADAPTER

**ID:** `TERM.ADAPTER`
**Type:** Tool interface

**Definition:**
An **Adapter** is a tool-specific interface implementation that standardizes how the pipeline invokes external CLI tools (Aider, Codex, Claude Code, etc.).

Each adapter:

* inherits from `ToolAdapter` base class,
* implements `build_command()` to construct tool-specific command lines,
* implements `execute()` to run the command and capture results,
* returns standardized `ExecutionResult` with success flag, exit code, stdout, stderr, duration, timeout info,
* handles tool-specific quirks (environment variables, model selection, context passing).

**Available Adapters:**
* `aider_adapter.py` – Aider integration
* `codex_adapter.py` – Codex CLI integration
* `claude_adapter.py` – Claude Code integration
* `git_adapter.py` – Git operations
* `test_adapter.py` – Test execution

**Location:** `core/engine/adapters/`

**Key Interface:**
```python
class ToolAdapter(ABC):
    def build_command(self, task: Dict[str, Any], prompt_file: Optional[Path]) -> List[str]
    def execute(self, command: List[str], cwd: str, timeout: int) -> ExecutionResult
    def execute_task(self, task: Dict[str, Any], worktree_path: str, ...) -> ExecutionResult
```

**Related Terms:** TOOL_PROFILE, CLI_TOOL_INSTANCE, CAPABILITY

**Implementation:** `core/engine/adapters/base.py`

---

### 9.2 TERM: TOOL_PROFILE

**ID:** `TERM.TOOL_PROFILE`
**Type:** Configuration template

**Definition:**
A **Tool Profile** is a configuration template (defined in `invoke.yaml`) that specifies how to invoke a specific CLI tool.

Each profile contains:

* `tool_id` – unique identifier (e.g., `aider`, `codex`)
* `command_template` – command pattern with placeholders (e.g., `{files}`, `{prompt_file}`)
* `timeout_sec` – default timeout
* `env_vars` – environment variable overrides
* `model` – AI model to use (if applicable)
* `success_exit_codes` – which exit codes indicate success (default: `[0]`)

**Purpose:**
* separates tool configuration from orchestration logic,
* allows per-environment customization,
* supports templating for dynamic argument substitution,
* loaded by `core/engine/tools.py`.

**Location:** `invoke.yaml` (root level or config/)

**Related Terms:** ADAPTER, CLI_TOOL_INSTANCE, TOOLS

**Implementation:** `core/engine/tools.py` (`load_tool_profiles()`)

---

### 9.3 TERM: CAPABILITY

**ID:** `TERM.CAPABILITY`
**Type:** AIM routing key

**Definition:**
A **Capability** is a functional capability identifier used by **AIM** to route workstream tasks to appropriate tools.

Instead of hardcoding tool names (`tool: aider`), workstreams declare capabilities:

* `code_generation` – write new code
* `linting` – static analysis and formatting
* `refactoring` – code restructuring
* `testing` – test generation and execution
* `version_checking` – dependency analysis

AIM resolves capabilities to tools via:

* registry lookup (`AIM_registry.json`),
* fallback chains (primary → secondary → tertiary),
* version constraints,
* environment availability checks.

**Schema Location:** `schema/workstream.schema.json` (`capability` field)

**Example Usage:**
```json
{
  "id": "ws-feature-x",
  "capability": "code_generation",
  "capability_payload": {
    "files": ["src/handler.py"],
    "prompt": "Implement API handler",
    "timeout_ms": 300000
  }
}
```

**Related Terms:** AIM, ADAPTER, TOOL_PROFILE, BRIDGE

**Implementation:** `aim/bridge.py`

---

### 9.4 TERM: AIM

**ID:** `TERM.AIM`
**Type:** Integration system

**Definition:**
**AIM** (AI-tools Inventory Manager) is the integration bridge that manages:

* **tool discovery** – detecting installed AI tools and their versions,
* **capability routing** – mapping capabilities to available tools,
* **fallback chains** – automatic fallback when primary tool unavailable,
* **secrets injection** – managing API keys and credentials,
* **audit logging** – tracking tool invocations and costs,
* **environment validation** – verifying tool availability and health.

AIM provides:

* PowerShell-based registry management,
* Python bridge (`aim/bridge.py`) for pipeline integration,
* coordination rules for tool selection,
* version checking and compatibility validation.

**Key Components:**
* `aim/.AIM_ai-tools-registry/` – registry storage
* `aim/bridge.py` – Python-to-PowerShell bridge
* `aim/environment/` – environment and secrets management
* `AIM_registry.json` – tool inventory
* `AIM_coordination_rules.json` – routing logic

**Related Terms:** CAPABILITY, ADAPTER, BRIDGE, MCP_SERVICE

**Implementation:** `aim/` section

**Contract Version:** AIM_PLUS_V1 (see `docs/AIM_docs/AIM_INTEGRATION_CONTRACT.md`)

---

### 9.5 TERM: OPENSPEC

**ID:** `TERM.OPENSPEC`
**Type:** Specification system

**Definition:**
**OpenSpec** is a specification format and change proposal workflow that enables:

* **structured specifications** – machine-readable spec documents,
* **change proposals** – proposals for new features or modifications,
* **gate-based approval** – multi-level review process,
* **workstream generation** – automatic conversion from specs to executable workstreams,
* **cross-referencing** – stable paragraph-level references via sidecars.

OpenSpec workflow:

1. Create change proposal: `/openspec:proposal "feature description"`
2. Proposal stored in `openspec/changes/`
3. Gate approval process (gates 1-5)
4. Conversion to workstream: `spec_to_workstream.py`
5. Execution via orchestrator
6. Archive on completion: `/openspec:archive <change-id>`

**Key Components:**
* `openspec/` – legacy location for raw proposals
* `specifications/` – unified spec management
* `specifications/changes/` – active change proposals
* `specifications/bridge/` – OpenSpec-to-workstream integration
* `core/openspec_parser.py` – parsing and validation
* `core/openspec_convert.py` – conversion to workstream bundles

**Related Terms:** BUNDLE, SIDECAR, GATE, BRIDGE

**Implementation:** `specifications/`, `core/openspec_*.py`

**Quick Start:** `docs/QUICKSTART_OPENSPEC.md`

---

### 9.6 TERM: BRIDGE

**ID:** `TERM.BRIDGE`
**Type:** Integration component

**Definition:**
A **Bridge** is an integration layer that connects the core pipeline with external systems or formats.

**Types:**

**AIM Bridge** (`aim/bridge.py`):
* Python-to-PowerShell interface
* Tool registry access
* Capability resolution
* Secret injection

**OpenSpec Bridge** (`specifications/bridge/`):
* OpenSpec-to-workstream conversion
* Gate validation
* Change proposal tracking
* Spec indexing and resolution

Bridges provide:

* **abstraction** – hide external system complexity,
* **translation** – convert between formats,
* **coordination** – manage cross-system workflows,
* **isolation** – keep core pipeline independent.

**Related Terms:** AIM, OPENSPEC, ADAPTER, MCP_SERVICE

---

## 10. Isolation & Execution Context

### 10.1 TERM: WORKTREE

**ID:** `TERM.WORKTREE`
**Type:** Isolated workspace

**Definition:**
A **Worktree** is an isolated git working directory (managed via `git worktree` or stub directory) where a **WORKSTREAM** executes.

Each worktree:

* is located under `.worktrees/<ws-id>/`,
* provides **file isolation** – changes don't affect main working tree,
* enables **parallel execution** – multiple workstreams can run simultaneously,
* is **sandboxed** – validates file scope before committing,
* is managed by `core/state/worktree.py`.

**Current Implementation:**
* Phase-05 stub: creates directory under `.worktrees/`
* Future phases: full `git worktree` integration with branch management

**Key Operations:**
* `create_worktree_for_ws(run_id, ws_id)` – create/reuse worktree
* `validate_scope(worktree_path, allowed_paths)` – check file scope violations

**Related Terms:** SANDBOX, WORKSTREAM, FILE_SCOPE

**Implementation:** `core/state/worktree.py`

---

### 10.2 TERM: INTEGRATION_WORKER

**ID:** `TERM.INTEGRATION_WORKER`
**Type:** Specialized worker

**Definition:**
An **Integration Worker** is a specialized **CLI_TOOL_INSTANCE** responsible for:

* **merging results** from parallel workstreams,
* **detecting merge conflicts**,
* **coordinating integration branches**,
* **validating cross-workstream consistency**.

Responsibilities:

* Create integration branch (`uet-integration-<run-id>`)
* Merge feature branches from parallel workstreams
* Detect conflicts: content, delete, rename
* Invoke conflict resolution strategies
* Run integration tests before final merge

**Conflict Types:**
* `content` – overlapping changes to same lines
* `delete` – one branch deletes what another modifies
* `rename` – conflicting file renames

**Key Operations:**
* `merge_workstream_results(base_branch, feature_branches, run_id)` → `MergeResult`
* `detect_conflicts()` → `List[MergeConflict]`
* `resolve_conflict()` – apply resolution strategy

**Related Terms:** CLI_TOOL_INSTANCE, WORKER, WORKTREE, COMPENSATION_ACTION

**Implementation:** `core/engine/integration_worker.py`

---

### 10.3 TERM: PROCESS_SPAWNER

**ID:** `TERM.PROCESS_SPAWNER`
**Type:** Process manager

**Definition:**
The **Process Spawner** manages the lifecycle of external CLI tool processes:

* **spawning** – launch tool processes with correct environment,
* **monitoring** – track process health and resource usage,
* **timeout enforcement** – kill processes exceeding time limits,
* **output capture** – collect stdout/stderr,
* **cleanup** – ensure processes terminate cleanly.

Features:

* subprocess management with timeout handling,
* environment variable injection,
* encoding handling (UTF-8),
* exit code interpretation,
* graceful shutdown with SIGTERM → SIGKILL escalation.

**Related Terms:** CLI_TOOL_INSTANCE, ADAPTER, TOOLS

**Implementation:** `core/engine/process_spawner.py`, `core/engine/adapters/base.py`

---

### 10.4 TERM: PROMPT_ENGINE

**ID:** `TERM.PROMPT_ENGINE`
**Type:** Template processor

**Definition:**
The **Prompt Engine** generates tool-specific prompts from templates and workstream metadata.

Capabilities:

* **template rendering** – fill placeholders with task data,
* **context injection** – include file contents, specs, previous results,
* **prompt file generation** – create temporary prompt files for tools,
* **token estimation** – predict context window usage,
* **prompt caching** – reuse rendered prompts when applicable.

**Template Variables (examples):**
* `{task_description}` – task summary
* `{files}` – file list
* `{context}` – additional context
* `{acceptance_tests}` – test criteria
* `{previous_output}` – output from previous steps

**Related Terms:** ADAPTER, TOOL_PROFILE, CONTEXT_ESTIMATOR

**Implementation:** `core/engine/prompt_engine.py`, `core/prompts.py`

---

## 11. Quality & Control

### 11.1 TERM: PLUGIN

**ID:** `TERM.PLUGIN`
**Type:** Error detection module

**Definition:**
A **Plugin** is a modular error detection component that analyzes code for specific issues.

Each plugin:

* has a `manifest.json` describing capabilities and dependencies,
* implements `parse(file_path)` to detect errors,
* optionally implements `fix(file_path, error)` to auto-fix issues,
* returns structured error records,
* is discovered and loaded by `error/engine/plugin_manager.py`.

**Plugin Categories:**
* **Python**: ruff, black, isort, pylint, mypy, pyright, bandit, safety
* **PowerShell**: PSScriptAnalyzer (pssa)
* **JavaScript**: prettier, eslint
* **Markup/Data**: yamllint, mdformat, markdownlint, jq
* **Cross-cutting**: codespell, semgrep, gitleaks
* **Utilities**: path_standardizer, test_runner

**Plugin Structure:**
```
error/plugins/<plugin-name>/
  manifest.json       # Metadata
  plugin.py          # parse() and fix() implementations
  __init__.py        # Package marker
```

**Related Terms:** MANIFEST, ERROR_PIPELINE, PLUGIN_MANAGER

**Implementation:** `error/plugins/`

---

### 11.2 TERM: TEST_RUNNER

**ID:** `TERM.TEST_RUNNER`
**Type:** Specialized plugin/adapter

**Definition:**
The **Test Runner** is a specialized component that:

* executes test suites (unit, integration, acceptance),
* captures test results and coverage,
* reports failures to the error pipeline,
* integrates with **TEST_GATE**s,
* supports multiple test frameworks (pytest, npm test, etc.).

**Modes:**
* **Foreground**: blocking test execution before proceeding
* **Background**: async test execution for fast feedback
* **Gate**: mandatory test execution before merge/phase transition

**Related Terms:** GATE, TEST_GATE, ACCEPTANCE_TEST, PLUGIN

**Implementation:** `error/plugins/test_runner/`, `core/engine/test_gates.py`

---

### 11.3 TERM: PLAN_VALIDATOR

**ID:** `TERM.PLAN_VALIDATOR`
**Type:** Validation component

**Definition:**
The **Plan Validator** ensures **PHASE_PLAN** and **WORKSTREAM** consistency:

* **dependency graph validation** – no cycles, valid workstream IDs in `depends_on`,
* **file scope validation** – no overlapping `files_scope.writes` without isolation,
* **gate consistency** – gate values within valid range,
* **task coherence** – tasks align with phase expectations,
* **schema compliance** – bundles conform to `workstream.schema.json`.

**Validation Levels:**
* **Syntactic**: JSON schema validation
* **Semantic**: dependency cycles, file conflicts
* **Policy**: gate requirements, cost limits, parallelism constraints

**Related Terms:** BUNDLE, WORKSTREAM, FILE_SCOPE, GATE

**Implementation:** `core/engine/plan_validator.py`, `scripts/validate_workstreams.py`

---

### 11.4 TERM: ACCEPTANCE_TEST

**ID:** `TERM.ACCEPTANCE_TEST`
**Type:** Validation criterion

**Definition:**
An **Acceptance Test** is a workstream-level validation criterion defined in the **BUNDLE**.

Acceptance tests:

* are declared in the `acceptance_tests[]` array,
* describe **what success looks like** for the workstream,
* can be:
  * executable test commands (e.g., `pytest tests/test_feature.py`),
  * manual validation checklists,
  * behavioral assertions (e.g., "API returns 200 for valid input"),
* are checked before marking workstream as complete,
* gate final integration/merge when used with **TEST_GATE**s.

**Example:**
```json
{
  "id": "ws-feature-x",
  "acceptance_tests": [
    "pytest tests/test_feature_x.py --cov=src/feature_x",
    "Manual: Verify API returns correct JSON structure",
    "Performance: Response time < 100ms"
  ]
}
```

**Related Terms:** TEST_GATE, GATE, TEST_RUNNER, BUNDLE

---

### 11.5 TERM: HARDENING

**ID:** `TERM.HARDENING`
**Type:** Robustness strategy

**Definition:**
**Hardening** refers to robustness improvement strategies applied to the pipeline:

* **input validation** – strict schema checking, sanitization,
* **error boundaries** – isolate failures to prevent cascade,
* **defensive programming** – null checks, type guards, bounds checking,
* **graceful degradation** – fallback modes when resources constrained,
* **idempotency** – safe to retry operations,
* **audit trails** – comprehensive logging for debugging.

**Hardening Techniques:**
* Circuit breakers to prevent runaway retries
* Timeout enforcement on all external calls
* File scope validation before commits
* Worktree isolation for parallel execution
* Checkpoint/restore for crash recovery
* Schema validation at every boundary

**Related Terms:** CIRCUIT_BREAKER, RECOVERY_MANAGER, ERROR_PIPELINE

**Implementation:** `core/engine/hardening.py`

---

## 12. Monitoring & Observability

### 12.1 TERM: METRICS

**ID:** `TERM.METRICS`
**Type:** Measurement system

**Definition:**
**Metrics** track runtime performance and resource usage:

* **execution metrics**: task duration, success rates, retry counts,
* **resource metrics**: CPU, memory, disk I/O, network,
* **cost metrics**: API token usage, estimated USD cost per run,
* **parallelism metrics**: concurrent workers, queue depth, utilization,
* **quality metrics**: test coverage, error density, fix rates.

**Metric Categories:**

**Performance:**
* `task_duration_sec` – time per task
* `workstream_duration_sec` – total workstream time
* `queue_wait_time_sec` – time task spent waiting

**Cost:**
* `tokens_consumed` – AI model token usage
* `estimated_cost_usd` – running cost estimate
* `cost_per_task` – granular cost tracking

**Quality:**
* `error_count` – errors detected
* `fix_rate` – auto-fix success percentage
* `test_pass_rate` – test success percentage

**Related Terms:** COST_POLICY, CONTEXT_ESTIMATOR, AUDIT_LOG

**Implementation:** `core/engine/metrics.py`, `core/engine/cost_tracker.py`

---

### 12.2 TERM: AUDIT_LOG

**ID:** `TERM.AUDIT_LOG`
**Type:** Compliance record

**Definition:**
An **Audit Log** is a structured, immutable record of security-relevant events:

* tool invocations (which tool, which model, who authorized),
* file modifications (what changed, when, by which workstream),
* access control decisions (permission grants/denials),
* secret usage (which API keys accessed, redacted values),
* cost accrual (incremental cost tracking),
* policy violations (constraint breaches, escalations).

**Storage:**
* AIM audit logs: `aim/.AIM_ai-tools-registry/AIM_audit/`
* Pipeline audit logs: `.ledger/audit/`
* Database: `events` table with `severity = AUDIT`

**Format:** JSONL (one event per line)

**Related Terms:** LEDGER, EVENT, METRICS

**Implementation:** `core/state/audit_logger.py`, `aim/bridge.py`

---

### 12.3 TERM: HEALTH_CHECK

**ID:** `TERM.HEALTH_CHECK`
**Type:** Monitoring probe

**Definition:**
A **Health Check** monitors the health of **WORKER**s and **MCP_SERVICE**s:

* **liveness**: is the component running?
* **readiness**: can it accept new work?
* **resource health**: within CPU/memory limits?
* **connectivity**: can it reach dependencies?

**Health States:**
* `HEALTHY` – operating normally
* `DEGRADED` – functioning but performance impaired
* `UNHEALTHY` – not functioning, needs intervention
* `UNKNOWN` – cannot determine health

**Actions on Unhealthy:**
* Drain workload to healthy workers
* Attempt restart/recovery
* Alert human operator
* Update circuit breaker state

**Related Terms:** WORKER, MCP_SERVICE, CIRCUIT_BREAKER, EVENT_BUS

**Implementation:** Worker heartbeat in `core/engine/worker.py`, service probes in MCP integration

---

### 12.4 TERM: CONTEXT_ESTIMATOR

**ID:** `TERM.CONTEXT_ESTIMATOR`
**Type:** Prediction component

**Definition:**
The **Context Estimator** predicts token/context usage before executing tasks:

* **token counting**: estimate tokens in prompts, file contents, context,
* **window checking**: validate against model context limits,
* **cost prediction**: estimate API cost before execution,
* **chunking hints**: suggest file splits when context too large,
* **optimization**: recommend context reduction strategies.

**Estimation Inputs:**
* Task description length
* File sizes in `files_scope`
* Template complexity
* Model-specific tokenizer (if available)

**Estimation Outputs:**
* `estimated_tokens` – predicted token count
* `fits_in_context` – boolean, fits in model window
* `estimated_cost_usd` – predicted API cost
* `chunking_needed` – whether files must be split

**Related Terms:** PROMPT_ENGINE, COST_POLICY, METRICS, TOOL_PROFILE

**Implementation:** `core/engine/context_estimator.py`

---

## 13. Advanced Coordination

### 13.1 TERM: EVENT_BUS

**ID:** `TERM.EVENT_BUS`
**Type:** Pub/sub system

**Definition:**
The **Event Bus** is a publish-subscribe event distribution system that:

* **decouples components** – publishers don't know about subscribers,
* **broadcasts events** – all subscribers receive published events,
* **enables monitoring** – centralized event stream for observability,
* **supports filtering** – subscribers filter by event type/severity,
* **persists to ledger** – events written to append-only log.

**Event Flow:**
1. Component publishes event → `EventBus.publish(event)`
2. Event Bus broadcasts to all subscribers
3. Subscribers process event asynchronously
4. Event persisted to LEDGER

**Subscribers (examples):**
* Metrics collector
* Audit logger
* UI update notifier
* Circuit breaker monitor
* Error pipeline trigger

**Related Terms:** EVENT, LEDGER, METRICS, AUDIT_LOG

**Implementation:** `core/engine/event_bus.py`

---

### 13.2 TERM: PATCH_MANAGER

**ID:** `TERM.PATCH_MANAGER`
**Type:** Merge coordinator

**Definition:**
The **Patch Manager** coordinates code patches from multiple sources:

* **patch collection** – gather patches from parallel workers,
* **conflict detection** – identify overlapping changes,
* **merge strategies** – apply patches in safe order,
* **verification** – validate merged result,
* **rollback** – undo problematic patches.

**Patch Sources:**
* Foreground workers (feature implementations)
* Background workers (formatting, linting fixes)
* Auto-fix plugins (error corrections)
* Integration workers (cross-workstream merges)

**Strategies:**
* **Sequential application** – apply patches one-by-one with validation
* **Three-way merge** – use base/ours/theirs merge
* **Human escalation** – punt to HUMAN_REVIEW_TASK on conflicts

**Related Terms:** INTEGRATION_WORKER, WORKTREE, FILE_SCOPE, COMPENSATION_ACTION

**Implementation:** `core/engine/patch_manager.py`

---

### 13.3 TERM: RECOVERY_MANAGER

**ID:** `TERM.RECOVERY_MANAGER`
**Type:** Failure orchestrator

**Definition:**
The **Recovery Manager** orchestrates recovery strategies when tasks/workers fail:

* **retry with backoff** – exponential backoff between retries,
* **tool switching** – try alternate tool if primary fails,
* **task splitting** – break large task into smaller subtasks,
* **context repair** – fix corrupted context or state,
* **escalation** – route to stronger agent or human,
* **compensation** – execute undo actions if rollback needed.

**Recovery Decision Tree:**
1. Transient error? → Retry with backoff
2. Tool-specific issue? → Switch to fallback tool
3. Context too large? → Split task
4. Persistent failure? → Escalate to human review
5. Corruption detected? → Execute compensation actions

**Recovery Policies:**
* `max_retries` – retry limit per task
* `retry_backoff_sec` – backoff schedule
* `fallback_tools[]` – alternate tool chain
* `escalation_threshold` – when to escalate
* `compensation_on_fail` – whether to execute compensations

**Related Terms:** CIRCUIT_BREAKER, SELF_HEAL_POLICY, ERROR_PIPELINE, COMPENSATION_ACTION

**Implementation:** `core/engine/recovery_manager.py`

---

### 13.4 TERM: CCPM

**ID:** `TERM.CCPM`
**Type:** Project management integration

**Definition:**
**CCPM** (Critical Chain Project Management) integration provides:

* **dependency-aware scheduling** – schedule tasks respecting dependencies,
* **buffer management** – project/feeding buffers to absorb uncertainty,
* **critical chain identification** – find longest dependency path,
* **resource leveling** – avoid over-allocation,
* **progress tracking** – buffer consumption metrics,
* **GitHub issue sync** – bidirectional sync with GitHub Issues.

**CCPM Concepts:**
* **Critical Chain**: longest dependency path through task network
* **Project Buffer**: time buffer at end of critical chain
* **Feeding Buffer**: buffers where non-critical chains feed into critical chain
* **Buffer Penetration**: how much buffer consumed (red/yellow/green zones)

**Integration Points:**
* Workstream `depends_on` → CCPM dependencies
* Task duration estimates → CCPM task sizing
* `ccpm_issue` field → GitHub issue linking
* Buffer consumption → triggers replanning

**Related Terms:** WORKSTREAM, TASK, GATE, PHASE

**Implementation:** `pm/`, `core/planning/ccpm_integration.py`

**Guides:** `docs/Project_Management_docs/ccpm-*.md`

---

### 13.5 TERM: SAGA

**ID:** `TERM.SAGA`
**Type:** Transaction pattern

**Definition:**
The **Saga Pattern** manages distributed transactions with **COMPENSATION_ACTION**s:

* **forward execution** – execute sequence of steps,
* **compensation on failure** – undo completed steps if later steps fail,
* **eventual consistency** – system reaches consistent state eventually,
* **isolation** – each step isolated, can be undone independently.

**Saga Types:**

**Choreography** (event-driven):
* Each step publishes events
* Next step triggered by event
* Compensation triggered by failure events

**Orchestration** (centralized):
* Orchestrator directs step sequence
* Orchestrator triggers compensations
* More control, easier debugging

**Pipeline Usage:**
* Multi-workstream execution with potential rollback
* Spec changes with revert capability
* Database migrations with undo scripts
* File transformations with backup/restore

**Related Terms:** COMPENSATION_ACTION, RECOVERY_MANAGER, CHECKPOINT, ERROR_PIPELINE

---

### 13.6 TERM: CONFLICT_GROUP

**ID:** `TERM.CONFLICT_GROUP`
**Type:** Mutual exclusion label

**Definition:**
A **Conflict Group** is a label applied to tasks that must **not run in parallel** with each other.

Tasks in the same conflict group:

* **serialize execution** – run one at a time,
* **share resources** – access same files/databases,
* **order-dependent** – execution order matters,
* **mutually exclusive** – logic incompatible with parallel execution.

**Example Conflict Groups:**
* `db-migration` – all database schema changes
* `config-edit` – all config file modifications
* `package-install` – dependency installation tasks
* `integration-test` – tests requiring exclusive environment

**Scheduler Handling:**
* Detect tasks with same `conflict_group`
* Enforce serial execution within group
* Allow parallelism across different groups
* Respect `depends_on` ordering within group

**Schema:** `conflict_group` field in workstream bundle (optional string)

**Related Terms:** TASK, PARALLELISM_CHART, SCHEDULER, FILE_SCOPE

**Implementation:** `core/engine/scheduler.py`

---

## 14. Cross-Reference Index

### By Category

**Core Execution Topology:**
PHASE_PLAN, PHASE, WORKSTREAM, TASK, CLI_TOOL_INSTANCE (WORKER), DAG, NODE_STATE

**Data Structures:**
BUNDLE, RUN, STEP, SIDECAR, LEDGER, EVENT, MANIFEST

**Tool Integration:**
ADAPTER, TOOL_PROFILE, CAPABILITY, AIM, OPENSPEC, BRIDGE

**Isolation & Context:**
FILE_SCOPE, SANDBOX, WORKTREE, BACKGROUND_TASK, INTEGRATION_WORKER, PROCESS_SPAWNER, PROMPT_ENGINE

**Parallelism & Control:**
PARALLELISM_CHART, OS_MODE, CIRCUIT_BREAKER, CONFLICT_GROUP

**Error & Recovery:**
ERROR_EVENT, ERROR_PIPELINE (ERR_EXEC), SELF_HEAL_POLICY, CHECKPOINT, COMPENSATION_ACTION, RECOVERY_MANAGER, PLUGIN

**Quality & Validation:**
GATE / TEST_GATE, ACCEPTANCE_TEST, PLAN_VALIDATOR, TEST_RUNNER, HARDENING

**Monitoring & Observability:**
METRICS, AUDIT_LOG, HEALTH_CHECK, CONTEXT_ESTIMATOR, EVENT_BUS

**Advanced Coordination:**
MCP_SERVICE, PATCH_MANAGER, CCPM, SAGA

**Cost & Human Interaction:**
COST_POLICY / BUDGET, HUMAN_REVIEW_TASK

### Alphabetical Quick Reference

- ACCEPTANCE_TEST → 11.4
- ADAPTER → 9.1
- AIM → 9.4
- AUDIT_LOG → 12.2
- BACKGROUND_TASK → 2.3
- BRIDGE → 9.6
- BUNDLE → 8.1
- CAPABILITY → 9.3
- CCPM → 13.4
- CHECKPOINT → 5.4
- CIRCUIT_BREAKER → 3.3
- CLI_TOOL_INSTANCE (WORKER) → 5
- COMPENSATION_ACTION → 5.5
- CONFLICT_GROUP → 13.6
- CONTEXT_ESTIMATOR → 12.4
- COST_POLICY / BUDGET → 7.1
- DAG → 1.1
- ERROR_EVENT → 5.1
- ERROR_PIPELINE (ERR_EXEC) → 5.2
- EVENT → 8.6
- EVENT_BUS → 13.1
- FILE_SCOPE → 2.1
- GATE / TEST_GATE → 6.1
- HARDENING → 11.5
- HEALTH_CHECK → 12.3
- HUMAN_REVIEW_TASK → 7.2
- INTEGRATION_WORKER → 10.2
- LEDGER → 8.5
- MANIFEST → 8.7
- MCP_SERVICE → 4.1
- METRICS → 12.1
- NODE_STATE → 1.2
- OPENSPEC → 9.5
- OS_MODE → 3.2
- PARALLELISM_CHART → 3.1
- PATCH_MANAGER → 13.2
- PHASE → 2
- PHASE_PLAN → 1
- PLAN_VALIDATOR → 11.3
- PLUGIN → 11.1
- PROCESS_SPAWNER → 10.3
- PROMPT_ENGINE → 10.4
- RECOVERY_MANAGER → 13.3
- RUN → 8.2
- SAGA → 13.5
- SANDBOX → 2.2
- SELF_HEAL_POLICY → 5.3
- SIDECAR → 8.4
- STEP → 8.3
- TASK → 4
- TEST_GATE → 6.1
- TEST_RUNNER → 11.2
- TOOL_PROFILE → 9.2
- WORKTREE → 10.1
- WORKSTREAM → 3

---

## 15. Version History

**V1.0** (2025-11-22):
- Initial release with 15 core terms
- Categories: Execution topology, Scope/Isolation, Parallelism, MCP, Error/Recovery, Testing, Cost/Human

**V1.1** (2025-11-22):
- **MAJOR EXPANSION**: Added 32 new terms (47 total)
- New categories: Core Data Structures (7), Tool & Integration Layer (6), Isolation & Execution Context (4), Quality & Control (5), Monitoring & Observability (4), Advanced Coordination (6)
- Verified all definitions against repository implementation
- Added cross-reference index and alphabetical quick reference
- Linked to schema files and implementation locations
- Added concrete examples for key terms

---

**END OF TERMS_SPEC_V1**

