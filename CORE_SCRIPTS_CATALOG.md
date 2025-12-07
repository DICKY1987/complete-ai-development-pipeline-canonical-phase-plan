# Core Scripts Catalog

**Generated**: 2025-12-06
**Scope**: `core/engine`, `core/cli`, `core/automation`, `core/autonomous`

This document provides a comprehensive listing of all scripts in the core directories with descriptions of their functionality.

---

## Table of Contents

- [core/engine](#coreengine)
  - [Main Engine Components](#main-engine-components)
  - [State Management](#state-management)
  - [Validation Components](#validation-components)
  - [Patch Management](#patch-management)
  - [Resilience Components](#resilience-components)
  - [Monitoring Components](#monitoring-components)
  - [Trigger Components](#trigger-components)
  - [Utilities](#utilities)
- [core/cli](#corecli)
- [core/automation](#coreautomation)
- [core/autonomous](#coreautonomous)

---

## core/engine

### Main Engine Components

#### `orchestrator.py`
**DOC_ID**: `DOC-CORE-ENGINE-ORCHESTRATOR-151`
**Workstream**: WS-03-01A

Main orchestration logic for executing workstreams. Manages run lifecycle, state transitions, and event emission. The orchestrator is the central component that coordinates workstream execution.

**Key Features**:
- Run lifecycle management
- State machine transitions
- Event emission and handling
- ULID generation (deterministic mode support)

---

#### `executor.py`
**DOC_ID**: `DOC-CORE-ENGINE-EXECUTOR-149`

Parallel execution workers that run scheduled workstream tasks with isolation and telemetry capture. Handles actual task execution with adapter integration.

**Key Features**:
- Parallel task execution
- Tool adapter integration
- Result capture and telemetry
- Subprocess adapter support

---

#### `scheduler.py`
**DOC_ID**: `DOC-CORE-ENGINE-SCHEDULER-158`
**Workstream**: WS-03-01C

Schedules and executes tasks with dependency resolution. Handles parallel and sequential execution based on task dependencies.

**Key Features**:
- Task dependency resolution
- Parallel execution coordination
- Sequential execution handling
- Task status tracking (pending, ready, running, completed, failed)

---

#### `router.py`
**DOC_ID**: `DOC-CORE-ENGINE-ROUTER-157`
**Workstream**: WS-03-01B

Routes tasks to appropriate tools based on `router_config.json`. Supports multiple routing strategies and capability matching.

**Key Features**:
- Task-to-tool routing
- Multiple routing strategies
- Capability matching
- Round-robin and weighted routing
- File-backed state persistence

---

#### `dag_builder.py`
**DOC_ID**: `DOC-CORE-ENGINE-DAG-BUILDER-147`

Constructs execution DAG (Directed Acyclic Graph) from workstreams. Performs topological sort for wave-based parallel execution.

**Key Features**:
- DAG construction from workstreams
- Topological sorting
- Dependency graph building
- Wave-based execution planning

---

#### `execution_request_builder.py`
**DOC_ID**: `DOC-CORE-ENGINE-EXECUTION-REQUEST-BUILDER-148`
**Workstream**: WS-03-01B

Builds ExecutionRequest objects for tool invocation. Creates standardized request structures for tool adapters.

**Key Features**:
- ULID generation
- Task information setting
- Context attachment
- Request metadata building

---

#### `phase_coordinator.py`
**DOC_ID**: `DOC-CORE-ENGINE-PHASE-COORDINATOR-500`

Central automation orchestrator for Phase 4→5→6 flow. Coordinates routing, execution, and error recovery in a fully automated loop.

**Key Features**:
- Cross-phase coordination
- Automated routing → execution → recovery
- Event-driven workflow
- Configuration-based behavior

---

#### `integration_worker.py`
**DOC_ID**: `DOC-CORE-ENGINE-INTEGRATION-WORKER-150`
**Workstream**: Phase I WS-I4

Handles merge conflict detection and resolution for parallel workstream results. Integrates outputs from multiple parallel executions.

**Key Features**:
- Merge conflict detection
- Conflict resolution
- Branch merging
- Result integration

---

#### `worker_lifecycle.py`
**DOC_ID**: `DOC-CORE-ENGINE-WORKER-LIFECYCLE-162`
**Workstream**: WS-NEXT-002-001

Manages worker process lifecycle with state machine transitions. Tracks worker status, heartbeats, and execution statistics.

**State Machine**:
- `idle → busy → idle` (normal cycle)
- `idle → paused → idle` (pause/resume)
- `any → stopped` (shutdown)
- `any → crashed` (error)

---

#### `process_spawner.py`
**DOC_ID**: `DOC-CORE-ENGINE-PROCESS-SPAWNER-154`
**Workstream**: Phase I-1 WS-I2

Worker process spawning for parallel execution. Manages subprocess creation, sandboxing, and lifecycle for tool adapters.

**Key Features**:
- Worker process spawning
- Sandbox environment creation
- Process lifecycle management
- Environment variable handling

---

#### `executor_cli.py`
**DOC_ID**: `DOC-CORE-ENGINE-EXECUTOR-CLI-001`
**Workstream**: WS1-002

Bootstrap task execution from `task_queue.json`. Command-line interface for executing queued tasks.

**Key Features**:
- Task queue loading
- CLI argument parsing
- Task execution bootstrapping
- Integration with orchestrator

---

#### `__main__.py`
**DOC_ID**: `DOC-CORE-ENGINE-MAIN-202`

CLI entry point for orchestrator plan execution. Allows running orchestrator from command line with plan files.

**Usage Examples**:
```bash
python -m core.engine plans/safe_merge.json --var BRANCH=main
python -m core.engine plans/test_gate.json --var COMMIT_MSG="fix: bug"
```

---

### State Management

#### `state_machine.py`
**DOC_ID**: `DOC-CORE-ENGINE-STATE-MACHINE-159`
**Workstream**: WS-03-01A

Implements the state machine for run lifecycle following `COOPERATION_SPEC`. Defines valid state transitions and transition logic.

**Run States**:
- `PENDING` → `RUNNING` → `SUCCEEDED`
- `PENDING` → `RUNNING` → `FAILED`
- `any` → `QUARANTINED`
- `any` → `CANCELED`

**Step States**:
- `RUNNING` → `SUCCEEDED`
- `RUNNING` → `FAILED`
- `RUNNING` → `CANCELED`

---

#### `state_file_manager.py`
**DOC_ID**: (Not specified)

State file export utilities for cross-phase automation. Writes phase handoff state files in a consistent, atomic manner.

**Key Features**:
- Atomic file writes
- Routing decision export
- Task state export
- Cross-phase handoff support

---

#### `plan_schema.py`
**DOC_ID**: `DOC-CORE-ENGINE-PLAN-SCHEMA-201`

JSON plan definitions for orchestrator. Defines the structure for JSON plan files that drive the orchestrator.

**Key Features**:
- Step definition schema
- Plan structure validation
- Template variable support
- Dependency specification

---

### Validation Components

#### `request_validator.py`
**DOC_ID**: (Not specified)

Phase 2 (Request Building) contract validator. Validates entry/exit contracts for Phase 2.

**Entry Requirements**:
- `workstreams/*.json` exist (from phase1)
- `schema/execution_request.v1.json` exists
- `workstreams` table exists

---

#### `routing_validator.py`
**DOC_ID**: (Not specified)

Phase 4 (Routing) contract validator. Validates entry/exit contracts for Phase 4.

**Entry Requirements**:
- `.state/task_queue.json` exists
- `config/tool_profiles/*.yaml` exist
- `tasks` table populated

---

#### `scheduling_validator.py`
**DOC_ID**: (Not specified)

Phase 3 (Scheduling) contract validator. Validates entry/exit contracts for Phase 3.

**Entry Requirements**:
- `.state/orchestration.db` with run record
- `workstreams/*.json` exist

---

#### `execution_validator.py`
**DOC_ID**: (Not specified)

Phase 5 (Execution) contract validator. Validates entry/exit contracts for Phase 5.

**Entry Requirements**:
- `.state/routing_decisions.json` exists
- `tasks` table with `adapter_id`
- `ROUTING_COMPLETE` flag set

---

### Patch Management

#### `patch_converter.py`
**DOC_ID**: `DOC-CORE-ENGINE-PATCH-CONVERTER-152`

Converts tool outputs to unified diff format. Standardizes patches from different tools (aider, custom tools).

**Key Features**:
- Tool-specific to unified patch conversion
- Patch format standardization
- Metadata tracking

---

#### `patch_ledger.py`
**DOC_ID**: `DOC-CORE-ENGINE-PATCH-LEDGER-153`
**Workstream**: WS-NEXT-002-002

Manages patch lifecycle with state machine transitions. Tracks patch validation, application, verification, and quarantine.

**State Machine**:
- `created → validated → queued → applied → verified → committed`
- `any → apply_failed` (retry or quarantine)
- `any → quarantined` (safety)
- `any → dropped` (reject)

---

### Resilience Components

#### `resilience/circuit_breaker.py`
**DOC_ID**: `DOC-CORE-RESILIENCE-CIRCUIT-BREAKER-186`
**Workstream**: WS-03-03A

Circuit breaker pattern implementation. Prevents cascading failures by stopping requests to failing services.

**States**:
- `CLOSED`: Normal operation, requests pass through
- `OPEN`: Too many failures, requests blocked
- `HALF_OPEN`: Testing if service recovered

---

#### `resilience/retry.py`
**DOC_ID**: `DOC-CORE-RESILIENCE-RETRY-189`
**Workstream**: WS-03-03A

Retry logic with exponential backoff and jitter. Provides retry strategies for failed operations.

**Key Features**:
- Exponential backoff
- Jitter for collision avoidance
- Configurable max attempts
- Strategy pattern implementation

---

#### `resilience/resilient_executor.py`
**DOC_ID**: `DOC-CORE-RESILIENCE-RESILIENT-EXECUTOR-188`
**Workstream**: WS-03-03A

Combines circuit breakers and retry logic for robust task execution.

**Key Features**:
- Circuit breaker integration
- Retry strategy management
- Per-tool failure tracking
- Auto-recovery

---

#### `circuit_breakers.py`
**DOC_ID**: `DOC-CORE-ENGINE-CIRCUIT-BREAKERS-144`
**Workstream**: Phase 6 (PH-06)

Circuit breakers, retries, and oscillation detection. Lightweight utilities to load breaker config, compute error/diff signatures, and decide whether to continue FIX attempts.

**Key Features**:
- Pure Python stdlib implementation
- Deterministic defaults when config missing
- Error signature computation
- Diff hash calculation
- Oscillation detection

---

#### `recovery.py`
**DOC_ID**: (Not specified)
**Workstream**: Phase 6 bridge

Failure handling and retry orchestration. Coordinates retries after error recovery.

**Key Features**:
- Recovery policy configuration
- Task retry coordination
- Event-driven recovery
- Backoff strategy support

---

### Monitoring Components

#### `monitoring/progress_tracker.py`
**DOC_ID**: `DOC-CORE-MONITORING-PROGRESS-TRACKER-178`
**Workstream**: WS-03-03B

Tracks execution progress and calculates completion percentages.

**Key Features**:
- Progress snapshot creation
- Completion percentage calculation
- Task status aggregation
- Timing metrics

---

#### `monitoring/run_monitor.py`
**DOC_ID**: `DOC-CORE-MONITORING-RUN-MONITOR-179`
**Workstream**: WS-03-03B

Monitors run execution and aggregates metrics.

**Run Statuses**:
- `PENDING`
- `RUNNING`
- `SUCCEEDED`
- `FAILED`
- `QUARANTINED`
- `CANCELED`

---

### Trigger Components

#### `triggers/trigger_engine.py`
**DOC_ID**: (Not specified)

Event-driven trigger engine for automated workflow execution.

**Key Features**:
- Event pattern matching
- Trigger rule management
- Workstream auto-triggering
- Condition evaluation

---

### Utilities

#### `cost_tracker.py`
**DOC_ID**: `DOC-CORE-ENGINE-COST-TRACKER-146`
**Workstream**: WS-NEXT-002-004

Tracks costs for execution requests including API calls, compute time, and resource usage.

**Key Features**:
- API call cost tracking
- Compute time tracking
- Resource usage monitoring
- Cost aggregation

---

#### `context_estimator.py`
**DOC_ID**: `DOC-CORE-ENGINE-CONTEXT-ESTIMATOR-145`
**Workstream**: Phase I WS-I8

Context window management and estimation. Enhanced context optimization for parallel execution.

**Key Features**:
- Token estimation
- File count tracking
- Context optimization
- File pruning recommendations

---

#### `prompt_engine.py`
**DOC_ID**: `DOC-CORE-ENGINE-PROMPT-ENGINE-155`

Prompt Engine V1.1 for Pipeline Plus. WORKSTREAM_V1.1 template rendering with classification inference.

**Key Features**:
- Jinja2 template rendering
- Workstream classification
- Multi-target support (aider, codex, claude, universal)
- Context building

---

#### `test_gate.py`
**DOC_ID**: `DOC-CORE-ENGINE-TEST-GATE-160`
**Workstream**: WS-NEXT-002-003

Quality gate management. Manages quality gate execution and pass/fail decisions.

**State Machine**:
- `pending → running → passed/failed/error`
- `any → skipped`

**Key Features**:
- Test execution tracking
- Coverage criteria evaluation
- Gate criteria management

---

#### `tools.py`
**DOC_ID**: `DOC-CORE-ENGINE-TOOLS-161`

Tool adapter layer for AI Development Pipeline. Provides config-driven external tool execution with subprocess handling, timeouts, error capture, and result tracking.

**Key Features**:
- Template-based command rendering
- Subprocess handling
- Timeout management
- Standardized result reporting

---

## core/cli

### `orchestrator_cli.py`
**DOC_ID**: `DOC-CORE-CLI-ORCHESTRATOR-001`

Orchestrator CLI for workstream execution. Click-based command-line interface for running workstreams.

**Key Features**:
- Plan execution
- Phase specification
- Workstream filtering
- Timeout configuration

**Usage**:
```bash
orchestrator-cli --plan plans/example.json --phase phase1 --workstream WS-001
```

---

### `wrapper.py`
**DOC_ID**: (Not specified)

CLI wrapper for automated, non-interactive script execution with orchestrator integration.

**Key Features**:
- Script execution automation
- Event bus integration
- Result capture
- Timeout handling
- Non-interactive execution

---

## core/automation

### `monitoring_trigger.py`
**DOC_ID**: `DOC-CORE-AUTOMATION-MONITORING-TRIGGER-001`
**Workstream**: WS1-005

Auto-start monitoring on `RUN_CREATED` event. Watches `orchestration.db` for new runs and auto-launches monitoring UI.

**Key Features**:
- Database polling
- Run detection
- Monitoring UI auto-launch
- Event-driven activation

---

### `request_builder_trigger.py`
**DOC_ID**: `DOC-CORE-AUTOMATION-REQUEST-BUILDER-TRIGGER-001`
**Workstream**: WS1-003

Auto-trigger request builder on `PLANNING_COMPLETE` event. Watches for `PLANNING_COMPLETE` flag and automatically invokes request builder.

**Key Features**:
- Flag file watching
- Metadata extraction
- Request builder invocation
- Automated phase transition

---

### `router_trigger.py`
**DOC_ID**: `DOC-CORE-AUTOMATION-ROUTER-TRIGGER-001`
**Workstream**: WS1-004

Auto-trigger router on `task_queue.json` changes. Watches for task queue updates and automatically invokes router.

**Key Features**:
- File modification monitoring
- Queue change detection
- Router auto-invocation
- Continuous watching

---

## core/autonomous

### `error_analyzer.py`
**DOC_ID**: `DOC-CORE-AUTONOMOUS-ERROR-ANALYZER-609`
**Workstream**: WS-04-03A

Minimal error analyzer for reflexion loop. Parses stderr/test output into structured errors.

**Key Features**:
- Regex-based error parsing
- File and line extraction
- Structured error output
- Multi-line error handling

---

### `feature_flags.py`
**DOC_ID**: `DOC-CORE-AUTONOMOUS-FEATURE-FLAGS-610`

Feature flags for Phase 4 AI components.

**Available Flags**:
- `enable_reflexion`: Enable reflexion loop (default: `True`)
- `enable_hyde_search`: Enable HyDE search (default: `True`)
- `enable_terminal_capture`: Enable terminal capture (default: `True`)
- `enable_episodic_memory`: Enable episodic memory (default: `True`)

---

### `fix_generator.py`
**DOC_ID**: `DOC-CORE-AUTONOMOUS-FIX-GENERATOR-611`

Lightweight fix generator interface for reflexion loop. Delegates fix generation to a provided callable or a trivial fallback.

**Key Features**:
- Callable-based fix generation
- Default fallback implementation
- Attempt tracking
- Patch generation

---

### `reflexion.py`
**DOC_ID**: (Not specified)
**Workstream**: WS-04-03A

Reflexion loop orchestrator. Coordinates error detection, analysis, and fix generation in an iterative loop.

**Key Features**:
- Iterative error fixing
- Attempt tracking
- Success/failure detection
- Escalation support
- Episodic memory integration

**Workflow**:
1. Run task
2. Validate result
3. If failed, analyze errors
4. Generate fix
5. Apply fix
6. Repeat until success or max attempts

---

## Summary Statistics

| Directory | Script Count | Key Focus |
|-----------|--------------|-----------|
| `core/engine` | 33 | Orchestration, execution, scheduling, routing |
| `core/engine/resilience` | 3 | Circuit breakers, retry logic, resilient execution |
| `core/engine/monitoring` | 2 | Progress tracking, run monitoring |
| `core/engine/triggers` | 1 | Event-driven triggers |
| `core/cli` | 2 | Command-line interfaces |
| `core/automation` | 3 | Automated phase transitions |
| `core/autonomous` | 4 | AI-driven error recovery |
| **Total** | **48** | **Complete pipeline automation** |

---

## Key Integration Points

### Phase Flow
1. **Planning** → `request_builder_trigger.py` → **Request Building**
2. **Request Building** → **Scheduling** (`scheduler.py`)
3. **Scheduling** → `router_trigger.py` → **Routing** (`router.py`)
4. **Routing** → **Execution** (`executor.py`)
5. **Execution** → **Error Recovery** (`reflexion.py`, `recovery.py`)
6. **Monitoring** → `monitoring_trigger.py` → **UI Display**

### Cross-Cutting Concerns
- **State Management**: `state_machine.py`, `state_file_manager.py`
- **Resilience**: `circuit_breaker.py`, `retry.py`, `resilient_executor.py`
- **Validation**: `*_validator.py` files
- **Observability**: `progress_tracker.py`, `run_monitor.py`, `cost_tracker.py`

---

## Document Version

- **Version**: 1.0
- **Last Updated**: 2025-12-06
- **Maintenance**: Auto-regenerate when new scripts are added to core directories
