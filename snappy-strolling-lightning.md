# Plan Evaluation: Reusable Orchestrator Design

## Executive Summary

**Verdict**: ✅ **Implement the proposed reusable orchestrator** - You're 70-80% there with existing infrastructure.

**Key Finding**: The proposed generic plan-based orchestrator is an **evolutionary upgrade**, not a rewrite. Your existing components (DAGBuilder, state machine, resilience patterns, SQLite persistence) already provide the foundation - you just need to add a step executor and unified plan schema.

**Effort**: ~25 hours of focused development to achieve a production-ready reusable orchestrator.

---

## Critical Files Referenced

- **Current Orchestrator**: `core/engine/orchestrator.py:1-348`
- **DAG Builder**: `core/engine/dag_builder.py:1-120`
- **Resilience Module**: `core/engine/resilience/resilient_executor.py:1-80`
- **State Layer**: `core/state/db.py:1-200`
- **SAFE_MERGE Reference**: `scripts/safe_merge_orchestrator.ps1:1-450`
- **Workstream Schema**: `phase0_bootstrap/modules/bootstrap_orchestrator/schemas/schema/workstream.schema.json:1-100`

---

## What You Already Have (Strengths)

### 1. Core Infrastructure ✅

**State Machine** (`core/engine/state_machine.py`)
- Run lifecycle: pending → running → succeeded/failed/quarantined/canceled
- Step attempt tracking with exit codes
- Event emission (JSONL-compatible)

**DAG Builder** (`core/engine/dag_builder.py`)
- Topological sort using Kahn's algorithm
- Wave-based parallel execution planning
- Cycle detection

**Scheduler** (`core/engine/scheduler.py`)
- Task dependency graph management
- Ready task detection (all dependencies satisfied)
- Reverse dependency tracking

**SQLite Persistence** (`core/state/db.py`)
- Tables: runs, step_attempts, run_events
- Complete run lifecycle tracking
- Event stream storage

**Resilience Patterns** (`core/engine/resilience/`)
- Circuit breaker pattern
- Retry logic with exponential backoff
- Per-tool failure tracking

### 2. Working Pattern Templates ✅

**SAFE_MERGE Pipeline** (`scripts/safe_merge_orchestrator.ps1`)
- 8-phase merge strategy
- Retry logic with exponential backoff
- Lock acquisition for concurrent access prevention
- Comprehensive JSONL logging
- **Key Insight**: This is essentially a reusable orchestrator template that's currently hardcoded to merge operations

---

## What's Missing (Gaps)

### 1. No Generic Plan Schema (HIGH PRIORITY)

**Current State**:
- Workstream schema has task descriptions (strings), not executable steps
- SAFE_MERGE phases are hardcoded PowerShell blocks
- No unified format across use cases

**Proposed Solution**:
```json
{
  "plan_id": "PLAN-SAFE-MERGE-001",
  "globals": {
    "max_concurrency": 2,
    "default_timeout_sec": 1800,
    "env": {"PYTHONUNBUFFERED": "1"}
  },
  "steps": [
    {
      "id": "snapshot_repo",
      "command": "powershell.exe",
      "args": ["-File", "scripts/Create-Snapshot.ps1"],
      "depends_on": [],
      "timeout_sec": 600,
      "retries": 0,
      "on_failure": "abort",
      "critical": true
    }
  ]
}
```

**Gap**: Extend workstream schema to include executable command/args, timeout, retries, failure policies.

---

### 2. No Step Executor (HIGH PRIORITY)

**Current State**:
- No unified way to execute a step with timeout/retry enforcement
- SAFE_MERGE has subprocess wrappers, but they're pipeline-specific

**Proposed Solution**:
A `StepExecutor` class that:
- Wraps `subprocess.Popen` with timeout tracking
- Integrates with `ResilientExecutor` for retry logic
- Captures stdout/stderr to logs
- Returns structured result (exit_code, status, error)

**Gap**: Create `core/engine/step_executor.py` (new file)

---

### 3. No Unified Failure Policies (HIGH PRIORITY)

**Current State**:
- SAFE_MERGE has hardcoded "abort on failure" logic
- No config-driven on_failure modes

**Proposed Solution**:
Per-step `on_failure` enum:
- `abort`: Stop entire plan (critical failures)
- `skip_dependents`: Mark dependent steps as SKIPPED
- `continue`: Let other steps proceed (non-critical)
- `fallback_step`: Execute alternate step on failure

**Gap**: Add on_failure handling to orchestrator

---

### 4. No Condition Expressions (MEDIUM PRIORITY)

**Current State**:
- Steps execute based on dependency satisfaction only
- No conditional execution (e.g., "only run if previous step succeeded")

**Proposed Solution**:
```json
{
  "condition": "prev.snapshot_repo.status == 'success'",
  "on_failure": "skip_dependents"
}
```

**Gap**: Add expression evaluator to orchestrator

---

### 5. No Resource Graph (MEDIUM PRIORITY)

**Current State**:
- No provides/consumes model for inter-step communication
- Steps can't declare what they produce/need

**Proposed Solution**:
```json
{
  "provides": ["snapshot_ref", "backup_path"],
  "consumes": ["repo_status"]
}
```

**Gap**: Add resource tracking to state management

---

## Implementation Plan

### Phase 1: Schema Design (5 hours)

**Task 1.1**: Create generic plan schema
- **File**: `schema/plan.schema.json` (new)
- **Action**: Define schema with:
  - `plan_id`, `version`, `description`, `metadata`
  - `globals`: max_concurrency, default_timeout_sec, env
  - `steps[]`: id, command, args, cwd, depends_on, timeout_sec, retries, on_failure, critical
- **Output**: JSON schema validated with ajv

**Task 1.2**: Extend workstream schema (optional compatibility layer)
- **File**: `phase0_bootstrap/modules/bootstrap_orchestrator/schemas/schema/workstream.schema.json`
- **Action**: Add `steps[]` field as superset of existing structure
- **Benefit**: Backward compatibility with Phase 0 bootstrap workstreams

---

### Phase 2: Step Executor (8 hours)

**Task 2.1**: Create base step executor
- **File**: `core/engine/step_executor.py` (new)
- **API**:
  ```python
  class StepExecutor:
      def execute(self, step_def: StepDef, run_id: str) -> StepResult:
          # Launches command with timeout, retry, logging
          # Returns: {status, exit_code, stdout, stderr, started_at, finished_at}
  ```

**Task 2.2**: Integrate with ResilientExecutor
- **File**: `core/engine/step_executor.py`
- **Action**: Wire retry logic from `core/engine/resilience/resilient_executor.py`
- **Benefit**: Reuse existing circuit breaker, exponential backoff

**Task 2.3**: Add timeout enforcement
- **File**: `core/engine/step_executor.py`
- **Action**: Use `subprocess.Popen` with `timeout` parameter
- **Behavior**: Kill process if timeout exceeded, mark as FAILED

**Task 2.4**: Add PowerShell integration
- **File**: `core/engine/powershell_executor.py` (new)
- **Action**: Wrapper for PowerShell scripts with:
  - Stdout/stderr capture
  - Exit code detection ($LASTEXITCODE)
  - Error stream handling

---

### Phase 3: Orchestrator Enhancement (6 hours)

**Task 3.1**: Add plan loading and validation
- **File**: `core/engine/orchestrator.py:1-348`
- **Action**: Add method `load_plan(plan_path)` that:
  - Reads JSON from file
  - Validates against schema
  - Constructs Step objects

**Task 3.2**: Integrate DAGBuilder for step dependencies
- **File**: `core/engine/orchestrator.py`
- **Action**: Call `DAGBuilder.build_from_workstreams()` with steps
- **Output**: Execution waves for parallel execution

**Task 3.3**: Implement on_failure handlers
- **File**: `core/engine/orchestrator.py`
- **Action**: Add logic for:
  - `abort`: Cancel remaining steps, mark run as FAILED
  - `skip_dependents`: Mark dependent steps as SKIPPED
  - `continue`: Log error but proceed
  - `fallback_step`: Execute alternate step

**Task 3.4**: Add condition expression evaluator
- **File**: `core/engine/condition_evaluator.py` (new)
- **API**:
  ```python
  def evaluate_condition(condition: str, context: Dict) -> bool:
      # Evaluates expressions like "prev.step1.status == 'success'"
  ```
- **Safety**: Use ast.literal_eval or safe expression parser (no eval())

---

### Phase 4: Database Schema Extension (1 hour)

**Task 4.1**: Add plans table
- **File**: `core/state/db.py`
- **Schema**:
  ```sql
  CREATE TABLE plans (
      plan_id TEXT PRIMARY KEY,
      version TEXT NOT NULL,
      description TEXT,
      plan_json TEXT NOT NULL,
      created_at TEXT NOT NULL
  );
  ```

**Task 4.2**: Extend step_attempts table
- **File**: `core/state/db.py`
- **Action**: Add columns:
  - `timeout_sec` INTEGER
  - `retries_attempted` INTEGER
  - `on_failure` TEXT
  - `provides` TEXT (JSON array)
  - `consumes` TEXT (JSON array)

---

### Phase 5: Migration to Plan Format (2 hours)

**Task 5.1**: Convert SAFE_MERGE to plan
- **File**: `specs/plans/safe_merge_plan.json` (new)
- **Action**: Extract 8 phases from `scripts/safe_merge_orchestrator.ps1` into step definitions
- **Output**: Executable plan file

**Task 5.2**: Create plan templates
- **Files**:
  - `specs/plans/test_gate_plan.json`
  - `specs/plans/doc_id_restore_plan.json`
- **Action**: Convert existing pipelines to plan format

---

### Phase 6: Testing & Validation (3 hours)

**Task 6.1**: Create orchestrator tests
- **File**: `tests/engine/test_plan_orchestrator.py` (new)
- **Coverage**:
  - Plan loading and validation
  - DAG execution with dependencies
  - Timeout enforcement
  - Retry logic
  - on_failure handlers

**Task 6.2**: Integration test with SAFE_MERGE plan
- **File**: `tests/integration/test_safe_merge_plan.py` (new)
- **Action**: Execute converted SAFE_MERGE plan in test repo

**Task 6.3**: Add validation gate
- **File**: `scripts/validate_plans.py` (new)
- **Action**: Validate all plan files against schema

---

## Risk Assessment

### Low-Risk Components (Reuse Existing)
✅ State machine → Already production-ready
✅ DAG builder → Tested with workstreams
✅ SQLite persistence → Stable schema
✅ Resilience patterns → Circuit breaker + retry work

### Medium-Risk Components (Extension)
⚠️ Plan schema → New format, needs validation
⚠️ Step executor → Core abstraction, needs thorough testing
⚠️ on_failure handlers → Complex state transitions

### High-Risk Components (New Logic)
🔴 Condition expressions → Security risk if not sandboxed properly
🔴 PowerShell integration → Stdout/stderr capture can be tricky on Windows

---

## Recommendations

### 1. ✅ **PROCEED WITH IMPLEMENTATION** (Confidence: 90%)

**Rationale**:
- Existing infrastructure provides 70-80% of required functionality
- Proposal aligns with codebase architecture (spec-driven, layered design)
- SAFE_MERGE proves the pattern works (you've already built a mini-orchestrator)
- ~25 hours investment yields massive ROI (eliminates code duplication across all future pipelines)

### 2. **Prioritize These Features** (Phase 1-3)

**Critical Path**:
1. Plan schema (enables config-driven execution)
2. Step executor (core abstraction)
3. on_failure handlers (resilience)
4. Orchestrator integration (wires everything together)

**Defer These** (Phase 2 or later):
- Condition expressions (nice-to-have, not critical)
- Resource graph (provides/consumes) (can add later)
- Fallback steps (advanced recovery)

### 3. **Incremental Migration Strategy**

**Month 1**: Build core orchestrator + plan schema
**Month 2**: Migrate SAFE_MERGE to plan format
**Month 3**: Migrate Doc-ID restore, test gates
**Month 4**: GUI integration (read plan status from SQLite)

### 4. **Design Refinements** (vs proposal document)

**Change 1**: Use `step_def` field instead of separate command/args
```json
{
  "step_def": {
    "type": "powershell",
    "script": "scripts/Create-Snapshot.ps1",
    "args": {"-TargetBranch": "main"}
  }
}
```
**Benefit**: Extensible to non-CLI steps (API calls, file operations)

**Change 2**: Add `max_step_duration` global
```json
{
  "globals": {
    "max_step_duration_sec": 3600,  // Hard limit for any step
    "default_timeout_sec": 1800
  }
}
```
**Benefit**: Prevents runaway steps

**Change 3**: Add `skip_if` field (simpler than condition expressions)
```json
{
  "skip_if": ["env.DRY_RUN == '1'", "prev.preflight.status == 'failed'"]
}
```
**Benefit**: Safer than general expressions

---

## Success Criteria

### Before Deployment
✅ All 196 existing tests still pass
✅ New orchestrator tests cover 80%+ of step_executor.py
✅ SAFE_MERGE plan executes successfully in test repo
✅ Plan validation script added to CI pipeline

### After Deployment
✅ 3+ pipelines migrated to plan format (SAFE_MERGE, Doc-ID restore, test gates)
✅ GUI can display plan execution status
✅ Zero code duplication for new pipelines (just create plan JSON)

---

## Next Steps (If Approved)

1. **Review this plan** - Clarify any questions
2. **Create implementation tasks** - Break Phase 1-6 into tickets
3. **Start with Phase 1** (schema design) - Quick win, enables everything else
4. **Iterate on step executor** - Most critical component
5. **Migrate SAFE_MERGE** - Prove the pattern works

---

## Key References

**Proposal Document**: `current orchestration vs reusable orchestrator.md:1-872`

**Example JSON Schemas** (from proposal):
- Plan schema: Line 152-202
- SAFE_MERGE example: Line 225-306

**Implementation Skeletons** (from proposal):
- PowerShell orchestrator: Line 399-615
- Python orchestrator: Line 636-857

**Core Existing Files**:
- Orchestrator: `core/engine/orchestrator.py:1-348`
- DAG Builder: `core/engine/dag_builder.py:1-120`
- Resilience: `core/engine/resilience/resilient_executor.py:1-80`
- SAFE_MERGE: `scripts/safe_merge_orchestrator.ps1:1-450`
