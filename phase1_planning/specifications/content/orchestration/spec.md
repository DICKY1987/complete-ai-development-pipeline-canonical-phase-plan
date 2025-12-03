---
doc_id: DOC-GUIDE-SPEC-1554
---

# Orchestration Specification

## Purpose
Coordinate EDIT → STATIC → RUNTIME → PIPELINE flow across multiple workstreams with deterministic, auditable, AI-transparent orchestration.

This specification defines requirements for production-grade orchestration that enables "transparency without execution" - allowing AI agents and humans to understand system state, dependencies, and execution progress without executing code.

## Key Principles
- **Stable Requirement IDs**: All requirements use stable IDs (STATE-OBS-001, TASK-DEF-002, etc.) for traceability
- **RFC 2119 Compliance**: MUST/SHOULD/MAY keywords have precise meanings per RFC 2119
- **AI-First Design**: Every component serves transparency and auditability
- **Separation of Concerns**: Modular structure enables independent validation

---

## 1. Overview

### 1.1 Execution Phases
1. **EDIT:** Implement changes per spec/task
2. **STATIC:** Run linters, formatters, type checkers
3. **RUNTIME:** Execute tests
4. **PIPELINE:** Error pipeline with AI-assisted fixes

### 1.2 Workstream Isolation
- Each workstream runs in separate git worktree
- Independent state tracking per workstream
- Parallel execution across workstreams
- Merge on success, preserve on failure

---

## 2. State Observability

### STATE-OBS-001: State Snapshot Requirements
The orchestration system MUST maintain a `.state/current.json` file that:
- Contains complete current state of all active workstreams and tasks
- Is updated atomically on every state transition
- Is queryable without executing any code
- Follows the schema defined in STATE-OBS-004

**Rationale**: Enables AI agents to understand system state instantly without code execution.

### STATE-OBS-002: Transition Log Requirements
The orchestration system MUST maintain a `.state/transitions.jsonl` file that:
- Appends one JSON object per line for each state transition
- Is append-only (never modified or deleted)
- Contains sufficient information to reconstruct state at any timestamp
- Follows the event schema defined in STATE-OBS-004

**Rationale**: Provides complete audit trail for debugging and compliance.

### STATE-OBS-003: Atomicity Guarantees
State updates MUST be atomic via the following mechanism:
1. Write new state to `.state/current.json.tmp`
2. Perform atomic rename/move to `.state/current.json`
3. Only then append transition event to `.state/transitions.jsonl`

This prevents AI agents from seeing partial state during updates.

### STATE-OBS-004: Event Schema
State transition events MUST follow this schema:

```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "event": "task_started|task_completed|task_failed|task_timeout|...",
  "severity": "info|warning|error|critical",
  "workstream_id": "ws-ulid-001",
  "task_id": "task-ulid-002",
  "from_state": "pending",
  "to_state": "running",
  "caused_by": "parent-event-id",
  "metadata": {
    "worker_id": "worker-001",
    "retry_count": 0
  }
}
```

**Severity Levels**:
- `info`: Normal operations (task_started, task_completed)
- `warning`: Recoverable issues (task_retry, validation_warning)
- `error`: Failed operations requiring intervention (task_failed after retries)
- `critical`: System-level failures (worker_unresponsive, resource_exhaustion)

### STATE-OBS-005: Index Files
The orchestration system SHOULD maintain derived index files:
- `.state/by_workstream.json`: Tasks grouped by workstream
- `.state/by_status.json`: Tasks grouped by status (pending/running/completed/failed)
- `.state/by_worker.json`: Tasks grouped by assigned worker

These indices MUST be derivable from `current.json` and MAY be regenerated at any time.

### STATE-OBS-006: Index Generation
Index generation MUST satisfy:
- Indices are regenerated whenever `current.json` changes
- Index generation is idempotent
- If indices are stale, queries MUST fall back to `current.json`
- Index staleness is detected via timestamp comparison

---

## 3. Execution Model Documentation

### EXEC-DOC-001: Execution Model Directory
Documentation MUST be organized in `docs/execution_model/`:
- `OVERVIEW.md`: High-level execution flow
- `STATE_MACHINE.md`: Task and workstream state machines
- `SCHEDULING.md`: DAG-based scheduling algorithm
- `WORKERS.md`: Worker lifecycle and capabilities
- `RECOVERY.md`: Recovery procedures

### EXEC-DOC-002: Overview Documentation
`docs/execution_model/OVERVIEW.md` MUST describe:
- Overall architecture and components
- Data flow between components
- External dependencies
- Performance characteristics

### EXEC-DOC-003: State Machine Documentation
`docs/execution_model/STATE_MACHINE.md` MUST describe:
- All valid states for tasks and workstreams
- Valid transitions between states
- Conditions triggering each transition
- Invariants maintained by state machine

### EXEC-DOC-004: Scheduling Documentation
`docs/execution_model/SCHEDULING.md` MUST describe:
- How DAG is constructed from task dependencies
- Scheduling algorithm (priority, fairness, resource allocation)
- Handling of parallel execution
- Critical path calculation

### EXEC-DOC-005: Worker Documentation
`docs/execution_model/WORKERS.md` MUST describe:
- Worker initialization and registration
- Capability advertisement
- Task assignment algorithm
- Worker health monitoring

### EXEC-DOC-006: Recovery Documentation
`docs/execution_model/RECOVERY.md` MUST describe:
- Checkpoint/rollback mechanisms
- Recovery from partial workstream failures
- Manual intervention procedures
- Recovery decision trees

---

## 4. Task Definitions

### TASK-DEF-001: Task File Requirements
Each task MUST be defined in a standalone JSON file:
- Location: `tasks/{workstream_id}/{task_id}.json`
- Filename matches task_id
- Valid against task schema (TASK-DEF-002)

### TASK-DEF-002: Task Schema
Task definition files MUST follow this schema:

```json
{
  "task_id": "task-ulid-002",
  "workstream_id": "ws-ulid-001",
  "name": "Implement user authentication",
  "description": "Add JWT-based authentication to API",
  "type": "aider|pytest|lint|custom",
  "status": "pending|running|completed|failed",
  
  "dependencies": ["task-ulid-001"],
  "blocks": ["task-ulid-003"],
  
  "worker_requirements": {
    "capabilities": ["python_editing", "git_operations"],
    "min_version": "1.0.0"
  },
  
  "execution": {
    "command": "aider --yes --message '{prompt}'",
    "working_directory": "src/auth",
    "timeout_seconds": 600,
    "max_retries": 3,
    "retry_delay_seconds": 10
  },
  
  "context_requirements": {
    "max_context_tokens": 8000,
    "required_files": ["src/auth/handler.py", "src/auth/models.py"],
    "optional_files": ["src/auth/utils.py"],
    "exclude_patterns": ["tests/**", "docs/**", "*.pyc"]
  },
  
  "validation_rules": {
    "pre_execution": ["git_clean", "tests_passing"],
    "post_execution": ["no_lint_errors", "tests_still_passing", "no_security_issues"]
  },
  
  "state": {
    "created_at": "2024-01-15T10:00:00.000Z",
    "started_at": null,
    "completed_at": null,
    "assigned_worker": null,
    "retry_count": 0,
    "last_error": null
  }
}
```

**Context Requirements** (NEW):
- `max_context_tokens`: Maximum tokens for AI context window
- `required_files`: Files that MUST be in context
- `optional_files`: Files that SHOULD be in context if space allows
- `exclude_patterns`: Patterns to exclude from context

**Validation Rules** (NEW):
- `pre_execution`: Checks that MUST pass before task starts
- `post_execution`: Checks that MUST pass before task is marked complete

---

## 5. DAG and Execution Plans

### DAG-VIEW-001: DAG Structure Requirements
The orchestration system MUST generate DAG files:
- Location: `.state/dag_{workstream_id}.json`
- Updated when task dependencies change
- Contains complete dependency graph
- Includes topological sort of tasks

### DAG-VIEW-002: DAG File Schema
DAG files MUST follow this schema:

```json
{
  "workstream_id": "ws-ulid-001",
  "generated_at": "2024-01-15T10:00:00.000Z",
  "nodes": [
    {
      "task_id": "task-ulid-001",
      "name": "Task name",
      "type": "aider",
      "status": "completed"
    }
  ],
  "edges": [
    {
      "from": "task-ulid-001",
      "to": "task-ulid-002",
      "type": "depends_on"
    }
  ],
  "topological_order": ["task-ulid-001", "task-ulid-002", "task-ulid-003"]
}
```

### DAG-VIEW-003: Execution Plan Schema
Execution plan files (`.state/execution_plan_{workstream_id}.json`) MUST include:

```json
{
  "workstream_id": "ws-ulid-001",
  "generated_at": "2024-01-15T10:00:00.000Z",
  "stages": [
    {
      "stage": 1,
      "parallel_tasks": ["task-ulid-001"],
      "max_parallelism": 3,
      "estimated_duration_seconds": 120,
      "critical_path": true,
      "resource_requirements": {
        "git_repo_write": 1,
        "cpu_cores": 2
      }
    }
  ],
  "total_estimated_duration": 450,
  "critical_path_duration": 300,
  "critical_path_tasks": ["task-ulid-001", "task-ulid-003"]
}
```

**Enhancements** (NEW):
- `max_parallelism`: Explicit concurrency limit per stage
- `estimated_duration_seconds`: Estimated time for stage
- `critical_path`: Whether stage is on critical path
- `total_estimated_duration`: Overall workstream estimate
- `critical_path_duration`: Longest dependency chain

---

## 6. Capability Catalog

### CAP-REG-001: PowerShell Capability Registry
Worker capabilities MUST be registered in `capabilities/registry.psd1`:

```powershell
@(
    @{
        CapabilityId = 'cap-ulid-001'
        Version      = '1.0.0'
        Name         = 'WorkstreamOrchestration'
        Description  = 'Coordinate multi-phase workstream execution'
        Provider     = 'core.engine.orchestrator'
        DeprecatedBy = $null
        Stability    = 'stable'
        SinceVersion = '1.0.0'
        
        Requirements = @{
            MinPythonVersion = '3.10'
            Dependencies     = @('git', 'pytest')
        }
        
        Operations = @(
            @{
                Name   = 'StartWorkstream'
                Inputs = @('workstream_id', 'config')
                Output = 'workstream_handle'
            }
        )
    }
)
```

### CAP-REG-002: Capability Versioning
Capabilities MUST include versioning information:
- `Version`: Semantic version of capability
- `DeprecatedBy`: ID of capability that replaces this one (if deprecated)
- `Stability`: `experimental|stable|deprecated`
- `SinceVersion`: Version when capability was introduced

This allows capability evolution while maintaining backward compatibility.

---

## 7. Failure Modes

### ERR-FM-001: Failure Mode Documentation
Each failure mode MUST be documented in `docs/failure_modes/{failure_mode}.md` with:

```markdown
## Task Timeout

**Detection**: Task exceeds `max_runtime_seconds` without completion
**Probability**: Medium (5-10% of tasks under load)
**Impact**: Low (automatic retry available)
**Manifestation**: `{"event":"task_timeout","severity":"warning",...}`

**Automatic Recovery**:
1. Kill task process
2. Retry with exponential backoff (retry_count + 1)
3. If retry_count == max_retries, mark as failed

**Manual Intervention**:
- Investigate task logs in `.state/logs/{task_id}.log`
- Check worker health: `./scripts/check_worker.ps1 -WorkerId {worker_id}`
- Increase timeout if legitimate: Edit task definition `timeout_seconds`

**Related Failures**:
- Worker-Unresponsive (may cause timeouts)
- Resource-Exhaustion (may slow task execution)
```

### ERR-FM-002: Failure Mode Catalog
`docs/failure_modes/CATALOG.md` MUST list all documented failure modes:
- Task-Timeout
- Task-Failed
- Worker-Unresponsive
- Resource-Exhaustion
- Validation-Failed
- Dependency-Cycle
- Context-Overflow

### ERR-FM-003: Recovery Decision Trees
For each failure mode, `docs/failure_modes/` SHOULD contain a decision tree showing:
- Detection conditions (how to identify this failure)
- Automatic recovery attempts (what system tries automatically)
- Escalation paths (when to involve humans)
- Human intervention triggers (conditions requiring manual action)

---

## 8. Aider Integration

### AIDER-INT-001: Aider as Worker
Aider is explicitly a **worker implementation**, not a framework component:
- Aider receives task definitions via standard worker interface
- Aider executes within task timeout and retry constraints
- Aider output conforms to worker output contract

### AIDER-INT-002: Aider Context Boundaries
When executing Aider tasks:
- Aider MUST receive only files listed in `task.context_requirements.required_files`
- Aider MUST NOT request additional files during execution
- If Aider indicates insufficient context, task MUST fail with `error_type: "insufficient_context"` for human review
- Context boundaries are enforced by worker adapter

### AIDER-INT-003: Aider Output Contract
Aider MUST return structured output including:

```json
{
  "status": "success|failure",
  "files_modified": ["src/auth/handler.py", "src/auth/models.py"],
  "diff_summary": "Added JWT authentication with token validation",
  "validation_status": "pending|passed|failed",
  "commit_message": "feat: implement JWT authentication",
  "error": null,
  "metadata": {
    "tokens_used": 1500,
    "duration_seconds": 45
  }
}
```

This makes Aider a true black-box worker with clear boundaries.

---

## 9. State Machine Definitions

### SM-DEF-001: Task Lifecycle State Machine
`docs/state_machines/task_lifecycle.yaml` MUST define:

```yaml
states:
  - pending      # Task created, not yet scheduled
  - queued       # Task scheduled, waiting for worker
  - running      # Task executing on worker
  - validating   # Task completed, validation in progress
  - completed    # Task and validation successful
  - failed       # Task or validation failed
  - retrying     # Task failed, retry scheduled

transitions:
  - from: pending
    to: queued
    trigger: scheduler_assigned
    
  - from: queued
    to: running
    trigger: worker_started
    guard: worker_available
    
  - from: running
    to: validating
    trigger: execution_completed
    guard: exit_code_zero
    
  - from: running
    to: retrying
    trigger: execution_failed
    guard: retry_count < max_retries
    
  - from: running
    to: failed
    trigger: execution_failed
    guard: retry_count >= max_retries

invariants:
  - Only one task can be in 'running' state per worker
  - completed and failed are terminal states
  - retry_count never decreases
```

### SM-DEF-002: Workstream Lifecycle State Machine
`docs/state_machines/workstream_lifecycle.yaml` MUST define:

```yaml
states:
  - planned      # Workstream defined, tasks not created
  - ready        # All tasks created, ready to execute
  - executing    # At least one task running
  - validating   # All tasks completed, final validation
  - completed    # Workstream successful, merged
  - failed       # Workstream failed, preserved for analysis
  - cancelled    # Workstream cancelled by user

transitions:
  - from: planned
    to: ready
    trigger: all_tasks_created
    
  - from: ready
    to: executing
    trigger: first_task_started
    
  - from: executing
    to: validating
    trigger: all_tasks_completed
    guard: no_failed_tasks
    
  - from: validating
    to: completed
    trigger: validation_passed

workstream_state_derivation:
  - If any task is 'running': workstream is 'executing'
  - If all tasks 'completed' and no failures: workstream is 'validating'
  - If any task 'failed' and retries exhausted: workstream is 'failed'
```

### SM-DEF-003: Worker State Machine
`docs/state_machines/worker_lifecycle.yaml` SHOULD define:

```yaml
states:
  - initializing  # Worker starting up
  - idle          # Worker ready, no assigned tasks
  - busy          # Worker executing task
  - unresponsive  # Worker not responding to health checks
  - shutdown      # Worker gracefully shutting down

transitions:
  - from: initializing
    to: idle
    trigger: registration_complete
    
  - from: idle
    to: busy
    trigger: task_assigned
    
  - from: busy
    to: idle
    trigger: task_completed
    
  - from: busy
    to: unresponsive
    trigger: health_check_timeout
```

---

## 10. Module Indexing

### MOD-IDX-001: Module Documentation Requirements
Each module MUST include docstring with:

```python
"""
Core orchestration engine.

Public API:
- Orchestrator: Main orchestration coordinator
- Scheduler: DAG-based task scheduler
- Worker: Task execution worker

Stability Guarantees:
- Orchestrator: Stable since v1.0
- Scheduler: Experimental, may change
- Worker: Stable since v1.0

Integration Points:
- Aider: core.engine.tools.AiderAdapter
- State: core.state.crud operations
- Metrics: core.engine.metrics.MetricsCollector

Dependencies:
- core.state: State management
- core.engine.event_bus: Event publishing
"""
```

This helps AI understand API stability and integration patterns.

---

## 11. Concurrency and Resource Management

### CONC-REG-001: Resource Registry
`capabilities/resources.psd1` MUST declare:

```powershell
@(
    @{
        ResourceId   = 'git_repo_write'
        Type         = 'exclusive'
        Description  = 'Exclusive write access to git repository'
        MaxHolders   = 1
    },
    @{
        ResourceId   = 'filesystem_read'
        Type         = 'shared'
        Description  = 'Shared read access to filesystem'
        MaxHolders   = -1  # Unlimited
    },
    @{
        ResourceId   = 'api_quota'
        Type         = 'rate_limited'
        Description  = 'API rate limit'
        MaxHolders   = 100
        RefillRate   = '100/minute'
    }
)
```

**Resource Types**:
- `exclusive`: Only 1 holder at a time (e.g., git repo write)
- `shared`: Multiple readers allowed (e.g., filesystem read)
- `rate_limited`: Limited by rate (e.g., API quota)

### CONC-REG-002: Resource Requirements in Tasks
Task definitions MUST include resource requirements:

```json
{
  "task_id": "task-ulid-002",
  "resource_requirements": {
    "git_repo_write": "exclusive",
    "filesystem_read": "shared",
    "api_quota": 10
  }
}
```

Execution plan MUST track current resource holders to prevent contention.

---

## 12. Audit Trail

### AUDIT-001: Audit Trail Completeness
`.state/transitions.jsonl` MUST capture sufficient information to:
- Reconstruct complete system state at any timestamp
- Answer "why did task X fail?" without code execution
- Generate compliance reports (who did what when)
- Track resource usage and costs

### AUDIT-002: Audit Trail Retention
- Audit logs MUST be retained for minimum 90 days
- Rotation policy MUST be documented in `docs/operations/AUDIT_RETENTION.md`
- Archived logs MUST remain queryable
- Log format MUST NOT change without migration path

---

## 13. Schema Versioning

### SCHEMA-VER-001: Schema Versioning
All schemas (task definitions, state snapshots, DAG files) MUST include:

```json
{
  "schema_version": "1.0.0",
  "schema_url": "https://specs.example.com/task-schema/v1.0.0"
}
```

**Backward Compatibility**:
- Patch versions (1.0.x): Fully backward compatible
- Minor versions (1.x.0): Backward compatible, new optional fields
- Major versions (x.0.0): Breaking changes allowed

### SCHEMA-VER-002: Migration Path
`docs/schema_migrations/` MUST document:
- How to migrate from version N to N+1
- Which fields are deprecated
- Compatibility windows (how long old versions supported)
- Automated migration tools

Example: `docs/schema_migrations/task_v1_to_v2.md`

---

## 14. Observability

### OBS-001: Metrics Export
`.state/metrics.json` MUST be updated every 60 seconds with:

```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "workstreams": {
    "active": 3,
    "completed_today": 12,
    "failed_today": 1
  },
  "tasks": {
    "pending": 5,
    "running": 3,
    "completed": 45,
    "failed": 2,
    "avg_duration_seconds": 120,
    "completion_rate_per_hour": 15
  },
  "workers": {
    "total": 5,
    "idle": 2,
    "busy": 3,
    "unresponsive": 0,
    "avg_utilization": 0.75
  },
  "errors": {
    "task_timeout": 2,
    "task_failed": 1,
    "validation_failed": 1
  }
}
```

### OBS-002: Metrics Format
Metrics MUST be:
- Exportable to Prometheus/OpenMetrics format via `scripts/export_metrics.ps1`
- Queryable via time-series database
- Retained for minimum 30 days

---

## 15. Compliance Validation

### COMPLIANCE-001: Validation Scripts
Validation scripts in `scripts/validate/` MUST check requirements:

```
scripts/validate/
├── validate_state_obs.ps1      # Check STATE-OBS-*
├── validate_task_defs.ps1      # Check TASK-DEF-*
├── validate_dag_structure.ps1  # Check DAG-VIEW-*
├── validate_failure_modes.ps1  # Check ERR-FM-*
└── validate_compliance.ps1     # Run all validators
```

Each validator MUST output:
- PASS/FAIL per requirement ID
- Specific violations with file:line references
- Suggested fixes
- Exit code 0 for pass, non-zero for fail

---

## 16. Implementation Priority

### Phase 1 (Critical Path)
- STATE-OBS-001 through 006: State observability foundation
- TASK-DEF-001, 002: Task definition schema
- DAG-VIEW-001, 002, 003: DAG visualization
- SM-DEF-001: Task lifecycle state machine

### Phase 2 (Core Functionality)
- EXEC-DOC-001 through 006: Execution model docs
- AIDER-INT-001, 002, 003: Aider integration
- ERR-FM-001, 002, 003: Failure modes catalog
- CAP-REG-001, 002: Capability catalog

### Phase 3 (Production Hardening)
- CONC-REG-001, 002: Resource management
- AUDIT-001, 002: Audit trail requirements
- OBS-001, 002: Observability
- SCHEMA-VER-001, 002: Schema versioning

### Phase 4 (Polish)
- MOD-IDX-001: API indexing
- SM-DEF-002, 003: Additional state machines
- COMPLIANCE-001: Validation tooling

---

## Legacy Scenarios (Preserved for Compatibility)

### WHEN orchestrator starts workstream
- THEN create isolated worktree for changes
- AND initialize error pipeline context
- AND track workstream_id in database
- AND create `.state/current.json` with initial state

### WHEN static validation completes
- THEN proceed to runtime tests
- OR fix errors via pipeline if failures detected
- AND update state to 'validating' or 'failed'

### WHEN all phases complete successfully
- THEN merge workstream to main branch
- AND archive workstream context to `.state/archive/`
- AND update status tracking
- AND append completion event to transitions.jsonl
