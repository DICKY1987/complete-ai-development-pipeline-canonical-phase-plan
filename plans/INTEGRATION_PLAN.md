# Orchestrator Integration Plan
**Created**: 2025-12-04
**Status**: Ready for Implementation
**Estimated Effort**: 1-2 weeks

---

## Executive Summary

Migrate from fragmented, ad-hoc orchestration scripts to a **unified JSON-driven orchestration engine** that:

1. **Reuses** existing `core/engine/orchestrator.py` (run/step state management)
2. **Eliminates** duplicated retry/timeout/logging logic across scripts
3. **Enables** GUI observability via consistent JSONL/SQLite state
4. **Supports** parallel execution, DAG dependencies, and policy-driven error handling

---

## Current State Analysis

### Existing Assets ✅

1. **`core/engine/orchestrator.py`** (348 lines)
   - Run/step lifecycle management (`create_run`, `start_run`, `complete_run`)
   - State machines (`RunStateMachine`, `StepStateMachine`)
   - Event emission to JSONL + SQLite
   - **Gap**: No plan execution logic (DAG scheduler)

2. **`scripts/safe_merge_orchestrator.ps1`** (230 lines)
   - Hardcoded 7-phase safe merge pipeline
   - Ad-hoc retry logic, lock management, state files
   - **Problem**: Not reusable for other pipelines

3. **Scattered Orchestration**
   - `scripts/multi_agent_orchestrator.py`
   - `phase0_bootstrap/modules/bootstrap_orchestrator/src/orchestrator.py`
   - Git Auto-Sync watchers
   - **Problem**: Each reimplements process management

### Key Gaps ⚠️

| Gap | Impact | Priority |
|-----|--------|----------|
| No unified plan schema | Duplicated logic across pipelines | **P0** |
| No DAG scheduler | Linear execution only, no parallelism | **P0** |
| Scattered timeout/retry logic | Inconsistent error handling | **P0** |
| Fragmented observability | GUI can't track runs consistently | **P1** |

---

## Solution Architecture

### Phase 1: Core Orchestrator Extension (3 days)

**File**: `core/engine/orchestrator.py`

**Add**:
```python
def execute_plan(self, plan_path: str, variables: Dict[str, str] = None) -> str:
    """
    Execute a JSON plan and return run_id.

    Args:
        plan_path: Path to JSON plan file
        variables: Runtime variables (e.g., {"BRANCH": "main"})

    Returns:
        run_id from existing run tracking
    """
    plan = self._load_plan(plan_path, variables)
    run_id = self.create_run(
        project_id=plan.metadata["project"],
        phase_id=plan.metadata.get("phase_id", "ORCHESTRATED"),
        metadata={"plan_id": plan.plan_id, "plan_version": plan.version}
    )
    self.start_run(run_id)

    # DAG execution loop
    state = self._init_plan_state(plan)
    while self._has_pending_or_running_steps(state):
        self._update_running_steps(run_id, state)
        runnable = self._find_runnable_steps(state, plan)
        for step_def in runnable[:plan.globals["max_concurrency"]]:
            self._start_plan_step(run_id, step_def, state)
        time.sleep(0.5)

    # Finalize
    final_status = self._compute_final_status(state)
    self.complete_run(run_id, final_status, exit_code=0 if final_status == "succeeded" else 1)
    return run_id
```

**Key Methods**:
- `_load_plan(path, vars)` → Parse JSON, substitute `${VAR}` placeholders
- `_find_runnable_steps(state, plan)` → DAG scheduler (check `depends_on`)
- `_start_plan_step(run_id, step_def, state)` → Launch subprocess via `create_step_attempt()`
- `_update_running_steps(run_id, state)` → Poll processes, handle timeout/retry/on_failure
- `_handle_step_failure(step, state, plan)` → Implement abort/skip_dependents/continue

**Testing**:
```bash
pytest tests/engine/test_orchestrator_plan_execution.py -v
```

---

### Phase 2: Plan Schema Validation (1 day)

**File**: `core/engine/plan_schema.py` (new)

```python
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
import json

@dataclass
class StepDef:
    id: str
    name: str
    command: str
    args: List[str]
    depends_on: List[str] = field(default_factory=list)
    timeout_sec: Optional[int] = None
    retries: int = 0
    retry_delay_sec: int = 0
    critical: bool = True
    on_failure: str = "abort"  # abort | skip_dependents | continue
    # ... other fields ...

    def __post_init__(self):
        assert self.on_failure in ["abort", "skip_dependents", "continue"]

@dataclass
class Plan:
    plan_id: str
    version: str
    globals: Dict[str, Any]
    steps: List[StepDef]
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_file(cls, path: str) -> "Plan":
        with open(path) as f:
            data = json.load(f)
        steps = [StepDef(**s) for s in data["steps"]]
        return cls(
            plan_id=data["plan_id"],
            version=data["version"],
            globals=data.get("globals", {}),
            steps=steps,
            metadata=data.get("metadata", {})
        )
```

**Validation**:
- Check all `depends_on` references exist
- Detect circular dependencies (DAG cycles)
- Validate field types and enums

---

### Phase 3: Safe Merge Migration (2 days)

**Created**: `plans/safe_merge.json` ✅ (see above)

**Replace**: `scripts/safe_merge_orchestrator.ps1`

**New entrypoint**:
```bash
# Old way
pwsh scripts/safe_merge_orchestrator.ps1 -Branch main

# New way
python -m core.engine.orchestrator plans/safe_merge.json --var BRANCH=main
```

**Add CLI wrapper** (`core/engine/__main__.py`):
```python
import argparse
from core.engine.orchestrator import Orchestrator

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("plan_path", help="Path to JSON plan")
    parser.add_argument("--var", action="append", help="Variables (KEY=VALUE)")
    args = parser.parse_args()

    variables = {}
    for var in (args.var or []):
        k, v = var.split("=", 1)
        variables[k] = v

    orch = Orchestrator()
    run_id = orch.execute_plan(args.plan_path, variables)
    print(f"Run ID: {run_id}")

if __name__ == "__main__":
    main()
```

**Validation**:
1. Run safe merge on test branch
2. Compare state files (`.state/safe_merge/*.json`)
3. Verify lock acquisition/release
4. Check event log consistency

---

### Phase 4: Critical TODOs Implementation (2 days)

#### A. Timeout Enforcement
```python
def _update_running_steps(self, run_id: str, state: Dict):
    now = time.time()
    for step_id, step_state in list(state["running"].items()):
        step_def = state["step_defs"][step_id]
        timeout = step_def.timeout_sec or state["plan"].globals["default_timeout_sec"]

        if (now - step_state["started_at"]) > timeout:
            step_state["process"].kill()
            self.complete_step_attempt(
                step_id,
                status="failed",
                exit_code=-1,
                error_log=f"Timeout after {timeout}s"
            )
            self._handle_step_failure(run_id, step_def, state)
```

#### B. Retry Logic
```python
def _handle_step_failure(self, run_id: str, step_def: StepDef, state: Dict):
    step_state = state["steps"][step_def.id]
    max_retries = step_def.retries

    if step_state["attempt"] < (max_retries + 1):
        # Retry
        time.sleep(step_def.retry_delay_sec)
        step_state["status"] = "PENDING"
        self._emit_event(run_id, "step_retry", {
            "step_id": step_def.id,
            "attempt": step_state["attempt"] + 1
        })
    else:
        # Apply failure policy
        if step_def.on_failure == "abort" and step_def.critical:
            self._cancel_pending_steps(state)
        elif step_def.on_failure == "skip_dependents":
            self._skip_downstream_steps(step_def.id, state)
        # "continue" does nothing
```

#### C. `on_failure` Policies
```python
def _skip_downstream_steps(self, failed_step_id: str, state: Dict):
    """Mark all steps that depend on failed_step_id as SKIPPED"""
    for step_def in state["plan"].steps:
        if failed_step_id in step_def.depends_on:
            state["steps"][step_def.id]["status"] = "SKIPPED"
            self._skip_downstream_steps(step_def.id, state)  # Recursive
```

---

### Phase 5: GUI Integration (2 days)

**File**: `gui/orchestrator_monitor.py` (new)

```python
from core.engine.orchestrator import Orchestrator
from core.state.db import get_db

class OrchestrationMonitor:
    def __init__(self):
        self.orch = Orchestrator()

    def get_active_runs(self):
        """Get all running/pending orchestrated plans"""
        return self.orch.list_runs(state="running")

    def get_run_progress(self, run_id: str):
        """Get step-by-step progress"""
        run = self.orch.get_run_status(run_id)
        steps = self.orch.get_run_steps(run_id)
        events = self.orch.get_run_events(run_id)

        return {
            "run": run,
            "steps": steps,
            "timeline": events,
            "progress_pct": self._compute_progress(steps)
        }

    def _compute_progress(self, steps):
        total = len(steps)
        completed = sum(1 for s in steps if s["state"] in ["succeeded", "failed", "skipped"])
        return int((completed / total) * 100) if total > 0 else 0
```

**UI Component** (pseudo-code):
```python
# In your existing GUI dashboard
runs = monitor.get_active_runs()
for run in runs:
    progress = monitor.get_run_progress(run["run_id"])
    display_progress_bar(
        title=run["metadata"]["plan_id"],
        percent=progress["progress_pct"],
        steps=progress["steps"]
    )
```

---

## Testing Strategy

### Unit Tests
```python
# tests/engine/test_plan_execution.py
def test_execute_simple_plan(tmp_path):
    plan = {
        "plan_id": "TEST-001",
        "globals": {"max_concurrency": 1},
        "steps": [
            {"id": "echo", "command": "echo", "args": ["hello"], "depends_on": []}
        ]
    }
    plan_path = tmp_path / "test.json"
    plan_path.write_text(json.dumps(plan))

    orch = Orchestrator()
    run_id = orch.execute_plan(str(plan_path))

    run = orch.get_run_status(run_id)
    assert run["state"] == "succeeded"

def test_dependency_ordering():
    # Plan with A -> B -> C dependencies
    # Assert B doesn't start until A succeeds
    pass

def test_timeout_enforcement():
    # Step with 1s timeout running 10s sleep
    # Assert step fails with timeout error
    pass

def test_retry_on_failure():
    # Step with retries=2, fails first 2 times
    # Assert attempt counter increments
    pass
```

### Integration Tests
```bash
# Run actual safe_merge.json on test branch
git checkout -b test-orchestrator-merge
python -m core.engine.orchestrator plans/safe_merge.json --var BRANCH=test-orchestrator-merge

# Verify state files created
ls .state/safe_merge/

# Check run in database
sqlite3 .state/runs.db "SELECT * FROM runs WHERE metadata LIKE '%PLAN-SAFE-MERGE%';"
```

---

## Migration Checklist

### Week 1
- [ ] **Day 1-2**: Implement `execute_plan()` in `core/engine/orchestrator.py`
  - [ ] DAG scheduler (`_find_runnable_steps`)
  - [ ] Process launcher (`_start_plan_step`)
  - [ ] State tracking integration
- [ ] **Day 3**: Add `plan_schema.py` with validation
  - [ ] Dataclass models
  - [ ] Circular dependency detection
  - [ ] Variable substitution (`${VAR}`)
- [ ] **Day 4**: Implement timeout enforcement
  - [ ] Add timeout checks to `_update_running_steps`
  - [ ] Test with deliberate timeouts
- [ ] **Day 5**: Implement retry logic
  - [ ] Add `_handle_step_failure` with retry counter
  - [ ] Test with flaky network commands

### Week 2
- [ ] **Day 6**: Implement `on_failure` policies
  - [ ] abort (cancel all pending)
  - [ ] skip_dependents (recursive skip)
  - [ ] continue (no action)
- [ ] **Day 7-8**: Migrate safe_merge.json
  - [ ] Convert all 11 steps from PS script
  - [ ] Test on real branch merge
  - [ ] Compare output with old script
- [ ] **Day 9**: Add CLI wrapper (`__main__.py`)
  - [ ] Argument parsing
  - [ ] Variable injection
  - [ ] Error reporting
- [ ] **Day 10**: GUI integration
  - [ ] Add `OrchestrationMonitor` class
  - [ ] Wire to existing dashboard
  - [ ] Test live progress tracking

---

## Success Criteria

1. **Functional**:
   - [ ] Safe merge completes successfully via `execute_plan()`
   - [ ] Timeout kills long-running steps
   - [ ] Retry logic works on transient failures
   - [ ] DAG dependencies enforced (no premature execution)

2. **Observability**:
   - [ ] All runs/steps visible in `runs.db`
   - [ ] JSONL events match existing format
   - [ ] GUI shows live progress

3. **Reusability**:
   - [ ] Create 2nd plan (e.g., doc_id restore) using same engine
   - [ ] No plan-specific code in orchestrator.py

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Breaking existing safe_merge | Keep old PS script as fallback during migration |
| Database schema conflicts | Use separate `plan_executions` table if needed |
| Timeout kills critical ops | Add `critical_grace_period_sec` to step schema |
| Variable substitution bugs | Use `string.Template` with safe defaults |

---

## Next Steps

**Immediate**: Start with Phase 1 (extend `core/engine/orchestrator.py`)

```bash
# Create feature branch
git checkout -b feature/orchestrator-plan-execution

# Implement execute_plan()
code core/engine/orchestrator.py

# Add tests
code tests/engine/test_plan_execution.py

# Run tests
pytest tests/engine/test_plan_execution.py -v
```

**Questions before starting?**
- Schema design approval needed?
- Should we use separate DB table or extend `runs`?
- Timeline adjustments needed?
