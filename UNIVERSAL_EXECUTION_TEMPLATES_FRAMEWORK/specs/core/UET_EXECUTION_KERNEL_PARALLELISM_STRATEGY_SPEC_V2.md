---
doc_id: DOC-CORE-UET-EXECUTION-KERNEL-PARALLELISM-194
---



---

# EXECUTION_KERNEL_PARALLELISM_STRATEGY_SPEC_V2

## 0. Purpose and Context

This document defines a **parallelism-aware, deterministic execution kernel** for a multi-CLI, multi-agent software development pipeline.

It:

1. Preserves the core model from `EXECUTION_KERNEL_PARALLELISM_STRATEGY_SPEC_V1`.
2. Incorporates an external AI assessment that identified key gaps:

   * merge strategy,
   * state persistence,
   * inter-worker coordination,
   * context management,
   * plan validation,
   * cost tracking,
   * test feedback loops,
   * human review workflow,
   * rollback/undo,
   * security and isolation.
3. Provides **complete, machine-readable concepts** so agentic AIs can:

   * assess, critique, extend, or implement this system,
   * map it onto existing orchestration tools (e.g., Prefect, Temporal, Dagster),
   * or build a custom kernel with equivalent capabilities.

The user will not read this document; **AI is the sole consumer**.

---

## 1. Core Model (Summary of V1)

### 1.1 Hierarchy

* Project
* Section
* Phase Plan (for project or section, defined before any coding)
* Workstream
* Task / Node (atomic unit in DAG)

### 1.2 DAG and Dependencies

* All tasks form a **Directed Acyclic Graph (DAG)**.
* Each node has:

  * `id`
  * `kind` (design, impl, test, docs, infra, refactor, background, spike, etc.)
  * `depends_on`
  * `files_scope.reads` / `files_scope.writes`
  * `parallel_ok`
  * `conflict_group`
  * `tool_preference`
  * `priority` (foreground vs background)
* Node states: `PENDING`, `READY`, `RUNNING`, `SUCCEEDED`, `FAILED`, `CANCELLED`.

### 1.3 Parallelism and Workers

* **Parallelism** derived from DAG + file scopes + policies.
* CLI instances are **workers**:

  * bound to roles, sandboxes, and file scopes.
  * consume tasks from the DAG.
* Background tasks:

  * run off to the side,
  * do not modify mainline source files,
  * write to logs, build directories, or ledgers.

### 1.4 OS Modes, Circuit Breakers, and Error Handling

* OS modes: `OS_MODE_NORMAL`, `OS_MODE_FOCUS_DEV`, `OS_MODE_CRITICAL_PIPELINE`.
* Circuit breakers:

  * monitor CPU, RAM, I/O,
  * enforce soft and hard thresholds.
* Error types:

  * `E_TOOL_FAILURE`, `E_MCP_FAILURE`, `E_RESOURCE_LIMIT`, `E_OS_MODE_FAILURE`, `E_PLAN_CONSISTENCY`, `E_UNKNOWN`.
* Error pipeline (ERR-EXEC):

  * auto retry → context repair → agent review → human escalation → resolved/ quarantined.

The rest of this document **extends** that base model with additional requirements.

---

## 2. Merge Strategy & Conflict Resolution (GAP-01)

### 2.1 Branch and Sandbox Model

* Each worker operates in:

  * its own branch or worktree, or
  * shared branch with strictly non-overlapping `files_scope.writes`.
* Parallel work is merged into one or more **integration branches**.

### 2.2 Integration Worker Role

Define a dedicated **Integration Worker**:

* Responsibilities:

  * Collect patches or branch updates from workers.
  * Perform merges into the integration branch.
  * Resolve conflicts or route to error pipeline.
  * Manage commit granularity and tagging.
* Integration worker is itself driven by a **Phase / Workstream** (e.g., `PH-INTEGRATION`).

### 2.3 Merge Orchestration Rules

Define a **merge decision tree**:

1. Identify candidate branches or patch sets ready for integration:

   * all required tests passed,
   * associated tasks `SUCCEEDED`.
2. If multiple candidates are ready:

   * sort by:

     * critical path importance,
     * dependency count,
     * age (oldest first),
     * policy-defined priority.
3. Merge in deterministic order:

   * apply candidate 1,
   * run validation (tests, static checks),
   * if success → move to candidate 2,
   * if failure → route to error pipeline and possibly revert.

### 2.4 Conflict Handling

* If merge conflict occurs:

  * raise `E_MERGE_CONFLICT` (subtype of `E_TOOL_FAILURE` or `E_PLAN_CONSISTENCY`).
  * generate a **merge conflict task**:

    * inputs:

      * conflicted files,
      * original branches,
      * context about the tasks that generated each side.
    * outputs:

      * a resolved patch or decision to roll back one side.
* Resolution path:

  * automatic AI-assisted merge where safe,
  * if not resolvable automatically → agent review,
  * if still unresolved → human review.

### 2.5 Stale Branch Cleanup

Define **stale branch policy**:

* Conditions for stale:

  * branch inactive for N days,
  * or superseded by later integrations,
  * or associated tasks cancelled or quarantined.
* Actions:

  * archive branch references in ledger,
  * delete local worktrees,
  * optionally keep remote branch with `archived/` prefix.

---

## 3. State Persistence & Crash Recovery (GAP-02)

### 3.1 State Storage

All orchestration state must be **persisted** in a durable store:

* Task states,
* Phase/Workstream states,
* Worker states,
* OS mode transitions,
* MCP service states,
* Error events,
* Resource limit events.

This can be stored in:

* relational database (e.g., SQLite, PostgreSQL), or
* workflow engine with built-in persistence (e.g., Prefect/Temporal), or
* equivalent structured persistence layer.

### 3.2 Checkpointing

Define **checkpoint granularity**:

* On every state transition of a task:

  * `PENDING` → `READY` → `RUNNING` → `SUCCEEDED` / `FAILED` / `CANCELLED`.
* On worker lifecycle events:

  * `SPAWNING`, `IDLE`, `BUSY`, `DRAINING`, `TERMINATED`.
* On OS mode changes and resource limit events.

Checkpoints are **idempotent**:

* Re-applying a checkpoint should not corrupt state.
* Task resumption must ensure:

  * partial writes are reconciled (e.g., via patching or sandboxing),
  * duplicate executions are either prevented or made safe.

### 3.3 Crash Recovery Protocol

On orchestrator restart:

1. Load last known states from persistence.
2. Identify tasks in `RUNNING` state with no alive worker:

   * mark as `FAILED` with `E_ORCHESTRATOR_CRASH` subtype.
3. Apply self-heal policy:

   * decide whether to rerun tasks,
   * or escalate to agent/human review.
4. Restore OS mode and MCP services to match current active tasks, if needed.
5. Resume scheduling from the reconstructed state.

---

## 4. Inter-Worker Communication & Coordination (GAP-03)

### 4.1 Event Bus / Message Channel

Define a **logical message bus** for coordination:

* Channels for:

  * `worker_status`,
  * `task_events`,
  * `resource_events`,
  * `error_events`,
  * `integration_events`.
* Messages include:

  * worker ID,
  * task ID,
  * event type,
  * timestamps,
  * minimal context for routing.

Implementation options (conceptual, choice left to implementer):

* centralized event store,
* message queue,
* streaming log.

### 4.2 Worker Signaling

Workers send events to the kernel:

* `TASK_STARTED`,
* `TASK_PROGRESS` (optional),
* `TASK_COMPLETED`,
* `TASK_FAILED`,
* `HEARTBEAT` (health check).

Kernel uses these signals to:

* update state,
* trigger downstream tasks,
* detect stuck or unhealthy workers.

### 4.3 Dynamic Dependencies

If a task discovers **new dependencies** at runtime:

* It can emit a `DYNAMIC_DEPENDENCY_DISCOVERED` event:

  * specifying new node(s) and dependencies.
* Kernel verifies:

  * no cycles introduced,
  * compatibility with plan constraints.
* If valid, kernel updates the DAG and reschedules as needed.
* If invalid, event is treated as `E_PLAN_CONSISTENCY` and routed to error pipeline.

### 4.4 Shared State Beyond Filesystem

Shared mutable state (beyond file system) is:

* strongly discouraged except via:

  * the orchestrator’s persistent state,
  * the message bus,
  * explicit ledger entries.

This keeps coordination deterministic and traceable.

---

## 5. Context Window Management (GAP-04)

### 5.1 Context Size Estimation

Each task requires **context** for AI tools:

* Source files,
* specs,
* prior outputs,
* error logs.

The kernel must estimate:

* total token size (or equivalent measure) before assigning task to a tool.

Per-node metadata:

* `estimated_context_tokens` (or similar),
* `max_context_tokens` per tool.

### 5.2 Context Strategies

When estimated context exceeds tool limits:

* **Pruning**:

  * truncate less relevant sections (e.g., older logs, comments).
* **Summarization**:

  * generate summarized versions of large files or conversation histories.
* **Chunking**:

  * split large tasks into smaller subtasks with reduced context.
* **Streaming / Paging**:

  * feed only the required portions of the context in multiple calls, when possible.

### 5.3 Context Handoff Between Phases

For multi-phase tasks:

* Each phase:

  * records essential outputs in a compact form (e.g., structured summaries, key decisions, interface definitions).
* Subsequent phases:

  * read these compact forms rather than raw, full logs.

Goal:

* ensure context for later phases remains within tool limits,
* maintain a **chain of reasoning** without blowing the context window.

---

## 6. Plan Validation & Simulation (GAP-05)

### 6.1 Schema Validation

Phase plans must pass **schema validation** before execution:

* All required fields present (ids, kinds, dependencies, files_scopes).
* Types and formats correct.
* Known enumerations used for modes, error policies, etc.

### 6.2 DAG Validation

For each plan:

* Check for **cycles** in dependency graph.
* Check for **orphan nodes** (nodes not reachable from any root).
* Check for **impossible constraints**, e.g.:

  * tasks that require resources that cannot exist together,
  * conflicting file scopes with no allowed serialization.

### 6.3 File Scope Validation

Validate `files_scope` against actual repository:

* Patterns resolve to real or logically planned files.
* Overlaps between `writes` scopes are:

  * either forbidden, or
  * explicitly handled by conflict groups and serialization.

### 6.4 Dry-run / Validation Mode

System provides a `VALIDATE_ONLY` mode:

* Parses phase plan,
* Runs schema and DAG validation,
* Simulates scheduling:

  * identifies potential parallelism profile,
  * identifies bottlenecks,
  * estimates runtime and resource usage,
* Does **not** run any CLI tools or modify files.

Result: a report for AIs telling whether the plan is executable and efficient.

---

## 7. Cost & API Usage Tracking (GAP-06)

### 7.1 Token and Cost Metrics

For each task and worker, track:

* estimated and actual tokens:

  * input tokens,
  * output tokens.
* associated monetary cost, based on model pricing.

Store per:

* task,
* worker,
* phase,
* project.

### 7.2 Budget Policies

Per project/phase settings:

* `max_cost_total`,
* `max_cost_per_phase`,
* `max_cost_per_task`,
* `max_parallel_workers_for_budget`.

When budget thresholds are approached:

* The kernel may:

  * reduce parallelism,
  * prioritize high-value tasks,
  * suspend non-critical tasks,
  * require explicit human approval to continue (policy-dependent).

### 7.3 Rate Limiting

Rate limits on API calls:

* Per provider,
* Per model,
* Per project.

Kernel enforces:

* concurrency caps,
* back-off strategies (exponential, fixed windows),
* queueing of tasks that would exceed rate limits.

---

## 8. Test Feedback Loop & Gates (GAP-07)

### 8.1 Test Gates

Define **test gates** as synchronization points:

* A gate requires certain tests or validation tasks to pass before:

  * merging branches,
  * progressing to dependent phases,
  * or marking workstreams as complete.

Example gate types:

* `GATE_LINT`: all linting tasks must pass.
* `GATE_UNIT`: all unit tests must pass.
* `GATE_INTEGRATION`: all integration tests must pass.
* `GATE_SECURITY`: security scans must pass.

### 8.2 Gate Effects on Scheduling

When a gate is active:

* Dependent tasks are **blocked** until gate conditions are satisfied.
* Failures at gates produce:

  * error events,
  * new tasks for fixing issues,
  * potential rollback of certain changes.

### 8.3 Test-Driven Execution

System may enforce:

* certain phases or tasks can only start after a test gate is cleared.
* e.g., deployment or final integration cannot occur while:

  * any test gate has failing tasks.

Test results feed back into:

* prioritization of refactor and bug-fix tasks,
* decisions about parallelism (e.g., slow tests may be run in isolation).

---

## 9. Human Review Workflow (GAP-08)

### 9.1 Human Escalation Tasks

When escalation to a human is required:

* Kernel creates a **HUMAN_REVIEW** task with:

  * compact summary of the issue,
  * all relevant error events,
  * prior self-heal attempts,
  * proposed options or recommendations from agentic AI.

### 9.2 Interaction Channel (Abstract)

Human interaction may happen via:

* ticket system,
* messaging platform,
* custom UI.

Regardless of implementation, the AI sees it as:

* `HUMAN_REVIEW` task with input,
* `HUMAN_DECISION` update with output.

### 9.3 Structured Feedback Re-Entry

Human feedback must be structured:

* decision (approve / reject / adjust),
* actions to take,
* optional annotations.

Kernel converts this into:

* state transitions,
* new or updated tasks,
* updated phase plan or constraints where necessary.

Human review is:

* asynchronous where possible,
* blocking only when absolutely necessary (e.g., high-risk merges, budget overrides).

---

## 10. Rollback & Undo (GAP-09)

### 10.1 Logical Rollback vs Git Revert

Beyond simple Git revert, system supports **logical rollback**:

* Phases have **compensation steps**:

  * e.g., revert schema changes,
  * restore previous configurations,
  * undo migrations or generated artifacts.

This is the **Saga pattern** applied to development phases.

### 10.2 Compensation Metadata

For each phase:

* Define:

  * `forward_actions`: what the phase does,
  * `compensation_actions`: how to undo or mitigate if needed.

If later phases reveal a fundamental error in earlier phases:

* Kernel can trigger compensation actions to revert to a known safe state.

### 10.3 Partial Rollbacks

Rollbacks can be scoped:

* single task,
* single phase,
* sequence of phases.

Policy decides:

* when to roll back,
* how far to roll back,
* whether to re-execute from a checkpoint or redesign the plan.

---

## 11. Security & Isolation (GAP-10)

### 11.1 Process Isolation

Workers must be isolated to prevent:

* unbounded resource usage,
* cross-contamination of environments,
* unintentional persistence of harmful code.

Approaches include:

* OS-level sandboxing,
* containers,
* separate user accounts,
* restricted directories.

### 11.2 Resource Quotas per Worker

Per worker quotas:

* maximum CPU share,
* maximum RAM,
* maximum disk usage,
* optional network rules.

These quotas complement the **system-wide circuit breakers**.

### 11.3 Credential and Secrets Management

Access to:

* APIs,
* MCP services,
* repositories,
* other services

must be:

* centrally managed,
* least-privilege,
* never hard-coded in tasks.

Kernel ensures:

* workers receive only the credentials they need,
* credentials can be rotated and revoked.

### 11.4 Malicious Code Detection

At minimum:

* static analysis or heuristic checks for suspicious patterns,
* restrictions on running arbitrary downloaded binaries,
* logs and alerts for unusual behavior (e.g., network access where none is expected).

---

## 12. Worker Lifecycle & Health

### 12.1 Worker Lifecycle States

Workers have explicit states:

* `SPAWNING`
* `IDLE`
* `BUSY`
* `DRAINING` (finishing current tasks, accepting no new ones)
* `TERMINATED`

These states are part of the persisted orchestrator state.

### 12.2 Health Checks and Timeouts

Health mechanisms:

* periodic `HEARTBEAT`,
* maximum time allowed per task,
* maximum time allowed in each worker state.

If a worker stops heartbeating or exceeds timeouts:

* kernel marks associated tasks as failed,
* triggers ERR-EXEC pipeline,
* may quarantine the worker or its sandbox.

### 12.3 Affinity and Context Reuse

Where beneficial:

* tasks related to the same module or phase can be assigned to the **same worker** to exploit context reuse,
* while still respecting file-scope and parallelism rules.

---

## 13. Metrics, Observability, and Replay

### 13.1 Metrics

Track metrics per:

* task,
* worker,
* phase,
* project.

Example metrics:

* task durations,
* success/failure rates,
* parallelism efficiency (actual vs potential),
* resource usage,
* cost and token usage,
* error frequency by type.

### 13.2 Traces and Logs

Execution is fully logged:

* Task state transitions,
* worker events,
* OS mode changes,
* resource limit events,
* error pipeline steps.

Logs must be:

* timestamped,
* correlated by IDs (task, phase, worker),
* compact but sufficient for replay.

### 13.3 Replay and What-If Analysis

System supports:

* replay of execution from a checkpoint for auditing,
* “what-if” simulations:

  * e.g., “what if we had N more workers?” or “what if we capped at lower parallelism?”
* used by AIs to propose improvements to phase plans and policies.

---

## 14. Summary

This V2 specification:

* Keeps the core ideas of:

  * **phase plans defined before any code**,
  * **DAG-based parallelism**,
  * **multi-CLI worker model**,
  * **OS modes & circuit breakers**,
  * **deterministic error pipeline**.
* Adds explicit coverage of:

  * merge strategy and conflict resolution,
  * state persistence and crash recovery,
  * inter-worker communication and dynamic dependencies,
  * context window management,
  * plan validation and dry-run simulation,
  * cost and token tracking,
  * test gates and feedback loops,
  * structured human review workflow,
  * rollback and compensation,
  * security and isolation,
  * worker lifecycle and health,
  * metrics, observability, and replay.

This document is intended to be a **complete, machine-readable description** of the current strategy, suitable for assessment, critique, or implementation by other AIs.
