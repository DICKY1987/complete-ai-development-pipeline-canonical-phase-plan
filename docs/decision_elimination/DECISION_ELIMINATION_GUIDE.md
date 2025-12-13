---
doc_id: DOC-GUIDE-DECISION-ELIMINATION-001
title: Decision Elimination Guide
date: 2025-12-05
version: 1.0.0
---

# Decision Elimination Guide

## Overview

This guide explains how to use the decision elimination infrastructure to:
1. **Eliminate nondeterministic behavior** for reproducible testing
2. **Track system decisions** for debugging and auditing
3. **Use pattern templates** for faster development

## Table of Contents

- [Deterministic Execution](#deterministic-execution)
- [Decision Tracking](#decision-tracking)
- [Pattern Templates](#pattern-templates)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## Deterministic Execution

### When to Use

Use deterministic mode when you need:
- **Regression testing** - Bit-identical results across runs
- **Debugging race conditions** - Reproducible execution order
- **Validating reproducibility** - Prove system is deterministic
- **Test replay scenarios** - Re-run exact same sequence

### How to Enable

```python
from core.engine.orchestrator import Orchestrator

# Enable deterministic mode
orch = Orchestrator(deterministic_mode=True)

# Creates deterministic IDs
run_id = orch.create_run("project", "phase")
print(run_id)  # Output: DET0000000000000000000001

# Fixed timestamp
timestamp = orch.now_iso()
print(timestamp)  # Output: 2024-01-01T00:00:00.000000Z
```

### Deterministic Features

#### 1. Sequential ULIDs
Counter-based IDs instead of random UUIDs:
```python
orch = Orchestrator(deterministic_mode=True)
ids = [orch.generate_ulid() for _ in range(3)]
# ['DET0000000000000000000001',
#  'DET0000000000000000000002',
#  'DET0000000000000000000003']
```

#### 2. Fixed Timestamps
Always returns same timestamp:
```python
orch = Orchestrator(deterministic_mode=True)
ts1 = orch.now_iso()
ts2 = orch.now_iso()
assert ts1 == ts2  # Both are "2024-01-01T00:00:00.000000Z"
```

#### 3. Sorted Task Selection
Tasks execute in alphabetical order when dependencies allow:
```python
from core.engine.scheduler import ExecutionScheduler, Task

scheduler = ExecutionScheduler()
scheduler.add_task(Task("task_z", "test"))
scheduler.add_task(Task("task_a", "test"))
scheduler.add_task(Task("task_m", "test"))

ready = scheduler.get_ready_tasks()
# Returns tasks in sorted order: [task_a, task_m, task_z]
```

#### 4. Deterministic Routing
Same input always selects same tool:
```python
from core.engine.router import TaskRouter

router = TaskRouter("config/router_config.json")
tool_1 = router.route_task("code_edit", risk_tier="low")
tool_2 = router.route_task("code_edit", risk_tier="low")
assert tool_1 == tool_2  # Always same tool
```

### Performance Impact

| Mode | Overhead | Use Case |
|------|----------|----------|
| **Disabled (default)** | 0% | Production |
| **Enabled** | <1% | Testing/debugging |

The overhead comes from counter increment vs UUID generation, which is negligible.

### Example: Full Pipeline Test

```python
def test_pipeline_deterministic():
    """Verify pipeline produces identical results"""
    from core.engine.orchestrator import Orchestrator
    from core.engine.scheduler import ExecutionScheduler, Task

    def run_pipeline():
        orch = Orchestrator(deterministic_mode=True)
        scheduler = ExecutionScheduler()

        # Add tasks
        tasks = [
            Task("build", "code_edit"),
            Task("test", "test_run", depends_on=["build"]),
        ]
        for task in tasks:
            scheduler.add_task(task)

        # Execute
        run_id = orch.create_run("proj", "phase")
        ready = [t.task_id for t in scheduler.get_ready_tasks()]

        return {"run_id": run_id, "ready_tasks": ready}

    # Run twice
    result_1 = run_pipeline()
    result_2 = run_pipeline()

    # Should be identical
    assert result_1 == result_2
    assert result_1["run_id"] == "DET0000000000000000000001"
    assert result_1["ready_tasks"] == ["build"]
```

---

## Decision Tracking

### Decision Categories

The system logs 4 types of decisions:

1. **routing** - Tool selection decisions
2. **scheduling** - Task execution order decisions
3. **retry** - Retry/give-up decisions (TODO)
4. **circuit_breaker** - Circuit state transitions (TODO)

### Using DecisionRegistry

#### Basic Usage

```python
from patterns.decisions.decision_registry import Decision, DecisionRegistry

# Create registry
registry = DecisionRegistry(".state/decisions.db")

# Log a decision
decision = Decision(
    decision_id="DEC-001",
    timestamp="2024-01-01T00:00:00Z",
    category="routing",
    context={"task_kind": "code_edit"},
    options=["aider", "claude", "cursor"],
    selected_option="aider",
    rationale="First in sorted list",
    metadata={"run_id": "RUN-123"}
)
registry.log_decision(decision)

# Query decisions
routing_decisions = registry.query_decisions(category="routing")
print(f"Found {len(routing_decisions)} routing decisions")

# Close when done
registry.close()
```

#### Context Manager (Recommended)

```python
with DecisionRegistry() as registry:
    decision = Decision(...)
    registry.log_decision(decision)

    # Query
    decisions = registry.query_decisions(category="routing")
# Auto-closed
```

### Query API

#### Filter by Category

```python
routing = registry.query_decisions(category="routing")
scheduling = registry.query_decisions(category="scheduling")
```

#### Filter by Run ID

```python
run_decisions = registry.query_decisions(run_id="RUN-123")
```

#### Filter by Time Range

```python
from datetime import datetime, timedelta, timezone

since = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
recent = registry.query_decisions(since=since)
```

#### Combine Filters

```python
# Routing decisions for specific run in last hour
decisions = registry.query_decisions(
    category="routing",
    run_id="RUN-123",
    since="2024-01-01T12:00:00Z",
    limit=100
)
```

### Statistics

```python
stats = registry.get_decision_stats()
print(f"Total decisions: {stats['total']}")
print(f"By category: {stats['by_category']}")
print(f"Last 24h: {stats['last_24h']}")

# Example output:
# Total decisions: 1,247
# By category: {'routing': 823, 'scheduling': 424}
# Last 24h: 156
```

### Integration with Orchestrator

```python
from core.engine.orchestrator import Orchestrator
from patterns.decisions.decision_registry import DecisionRegistry

# Enable decision logging
registry = DecisionRegistry()
orch = Orchestrator(
    deterministic_mode=False,  # Normal UUIDs
    decision_registry=registry  # Log decisions
)

# Decisions automatically logged during execution
run_id = orch.create_run("proj", "phase")

# Query decisions for this run
decisions = registry.query_decisions(run_id=run_id)
print(f"Logged {len(decisions)} decisions for run {run_id}")

registry.close()
```

---

## Pattern Templates

### Available Templates

Four production-ready templates in `patterns/templates/`:

1. **module_manifest.template** - Module documentation
2. **api_endpoint.py.template** - CRUD API endpoints
3. **test_case.py.template** - Test functions
4. **decision_record.md.template** - Decision documentation

### Time Savings

Based on UTE Decision Elimination Playbook:

| Task | Without Template | With Template | Savings |
|------|-----------------|---------------|---------|
| API endpoint | 30 min | 5 min | **83%** |
| Test suite | 25 min | 8 min | **68%** |
| Module docs | 20 min | 5 min | **75%** |
| Decision record | 45 min | 10 min | **78%** |

**ROI**: Break-even after just 2-3 uses per template

### Using Templates

#### Manual Approach

```bash
# Copy template
cp patterns/templates/api_endpoint.py.template api/users.py

# Edit and replace variables:
# {resource_singular} → user
# {resource_plural} → users
# {ResourceSchema} → UserSchema
# {resource_table} → users
```

#### Automated Approach (Recommended)

```bash
# Using template application script
python scripts/apply_template.py \
    --template patterns/templates/api_endpoint.py.template \
    --output api/users.py \
    --vars "resource_singular=user,resource_plural=users,ResourceSchema=UserSchema,resource_table=users"
```

### Template Examples

#### API Endpoint Template

```python
# Input variables:
# - resource_singular: user
# - resource_plural: users
# - ResourceSchema: UserSchema
# - resource_table: users

# Output (after template application):
@app.post("/api/users")
def create_user(request: Request) -> Dict[str, Any]:
    """Create a new user"""
    validate(request.data, UserSchema)
    result = db.insert("users", request.data)
    return {"status": "ok", "data": result}

@app.get("/api/users/{id}")
def get_user(id: str) -> Dict[str, Any]:
    """Get user by ID"""
    result = db.get("users", id)
    if not result:
        return {"status": "error", "error": "user not found"}
    return {"status": "ok", "data": result}
```

#### Test Case Template

```python
# Input variables:
# - function_name: validate_user
# - valid_input: {"name": "John", "email": "j@example.com"}
# - invalid_case_1: {"name": "John"}  # missing email
# - error_message_1: "email"

# Output:
def test_validate_user_happy_path():
    """Test validate_user with valid input"""
    valid_input = {"name": "John", "email": "j@example.com"}
    result = validate_user(valid_input)
    assert result.success == True
    assert result.data is not None

def test_validate_user_error_case_1():
    """Test validate_user with missing email"""
    invalid_input = {"name": "John"}
    result = validate_user(invalid_input)
    assert result.success == False
    assert "email" in str(result.errors)
```

---

## Testing

### Running Determinism Tests

```bash
# All deterministic execution tests
pytest tests/test_deterministic_execution.py -v --import-mode=importlib

# Specific test
pytest tests/test_deterministic_execution.py::test_scheduler_produces_deterministic_task_order -v
```

### Running Decision Registry Tests

```bash
# All decision registry tests
pytest tests/test_decision_registry.py -v --import-mode=importlib

# Specific test
pytest tests/test_decision_registry.py::test_decision_registry_logs_decisions -v
```

### Integration Tests

```bash
# Full pipeline determinism test
pytest tests/integration/test_deterministic_pipeline.py -v

# Slow tests (large-scale determinism)
pytest tests/integration/test_deterministic_pipeline.py::test_large_pipeline_deterministic -v --import-mode=importlib
```

### Test Requirements

**Important**: Use `--import-mode=importlib` flag due to patterns module structure:

```bash
# ✅ Correct
pytest tests/ -v --import-mode=importlib

# ❌ Will fail with "No module named 'patterns.decisions'"
pytest tests/ -v
```

---

## Troubleshooting

### Issue: Tests fail with "No module named 'patterns.decisions'"

**Solution**: Run pytest with `--import-mode=importlib` flag:
```bash
pytest tests/test_decision_registry.py -v --import-mode=importlib
```

### Issue: Decision registry file locked

**Cause**: DecisionRegistry connection not closed

**Solution**: Use context manager:
```python
# ✅ Correct
with DecisionRegistry() as reg:
    reg.log_decision(decision)
# Auto-closed

# ❌ Can cause locks
reg = DecisionRegistry()
reg.log_decision(decision)
# Forgot to call reg.close()
```

### Issue: Deterministic IDs not sequential

**Cause**: `deterministic_mode` not set or set to `False`

**Solution**: Verify flag is `True`:
```python
orch = Orchestrator(deterministic_mode=True)
assert orch.deterministic_mode == True
```

### Issue: Router still nondeterministic

**Cause**: Using old `InMemoryStateStore` instead of `FileBackedStateStore`

**Solution**: Use file-backed store:
```python
from core.engine.router import TaskRouter, FileBackedStateStore

state_store = FileBackedStateStore(".state/router_state.json")
router = TaskRouter("config/router_config.json", state_store=state_store)
```

### Issue: Decisions not logged

**Cause**: `decision_registry` parameter not provided

**Solution**: Pass registry to components:
```python
registry = DecisionRegistry()
orch = Orchestrator(decision_registry=registry)
scheduler = ExecutionScheduler(decision_registry=registry)
router = TaskRouter(config_path, decision_registry=registry)
```

---

## Best Practices

### 1. Use Deterministic Mode Only in Tests

```python
# ✅ Good - Testing
if os.getenv("TESTING") == "true":
    orch = Orchestrator(deterministic_mode=True)

# ❌ Bad - Production
orch = Orchestrator(deterministic_mode=True)  # No real UUIDs!
```

### 2. Query Decisions by run_id

```python
# ✅ Efficient - Indexed query
decisions = registry.query_decisions(run_id="RUN-123")

# ⚠️ Less efficient - Full table scan
all_decisions = registry.query_decisions()
filtered = [d for d in all_decisions if d.metadata.get("run_id") == "RUN-123"]
```

### 3. Use Templates Early

**ROI is positive after just 2-3 uses**:
- Template creation: 30 min (one-time)
- Time saved: 25 min per use
- Break-even: 2 uses

```python
# ✅ Good - Use template after 3 similar tasks
for resource in ["users", "projects", "tasks"]:
    apply_template("api_endpoint.py.template", resource)

# ❌ Bad - Manual creation each time
# 30 min × 3 = 90 min wasted
```

### 4. Log All Decision Points

```python
# ✅ Good - Log decision with context
decision = Decision(
    decision_id=f"DEC-{task_id}",
    category="routing",
    context={"task_kind": task_kind, "complexity": complexity},
    options=candidates,
    selected_option=selected,
    rationale=f"Strategy: {strategy}",
    metadata={"run_id": run_id}
)
registry.log_decision(decision)

# ❌ Bad - No logging
selected = candidates[0]  # Why this one? Can't debug later
```

### 5. Close Registries Properly

```python
# ✅ Good - Context manager
with DecisionRegistry() as reg:
    reg.log_decision(decision)

# ✅ Also good - Explicit close
registry = DecisionRegistry()
try:
    registry.log_decision(decision)
finally:
    registry.close()

# ❌ Bad - No cleanup
registry = DecisionRegistry()
registry.log_decision(decision)
# File handle leaked
```

### 6. Clean Old Decision Logs

```python
# Set up periodic cleanup (e.g., in cron job)
from patterns.decisions.decision_registry import DecisionRegistry

with DecisionRegistry() as reg:
    # Keep last 30 days
    reg.db.execute("""
        DELETE FROM decisions
        WHERE created_at < datetime('now', '-30 days')
    """)
    reg.db.commit()
```

---

## References

### Documentation
- **NONDETERMINISM_ANALYSIS.md** - Issue identification and resolutions
- **DECISION_ELIMINATION_PHASE_PLAN.md** - Implementation plan
- **DECISION_ELIMINATION_CONSOLIDATION_PLAN.md** - Consolidation guide

### Source Materials
- **UTE_Decision Elimination Through Pattern Recognition6.md** - Core technique
- **UTE_decision-elimination-playbook.md** - Replication playbook

### Code Files
- **core/engine/scheduler.py** - Deterministic task scheduling
- **core/engine/router.py** - Deterministic routing + FileBackedStateStore
- **core/engine/orchestrator.py** - Deterministic mode implementation
- **patterns/decisions/decision_registry.py** - Decision tracking

### Tests
- **tests/test_deterministic_execution.py** - 8 determinism tests
- **tests/test_decision_registry.py** - 10 registry tests
- **tests/integration/test_deterministic_pipeline.py** - End-to-end tests

---

## Quick Reference

### Deterministic Mode Checklist
- [ ] Import Orchestrator with `deterministic_mode=True`
- [ ] Run twice, compare results
- [ ] Check IDs start with "DET"
- [ ] Verify timestamps are fixed

### Decision Logging Checklist
- [ ] Create DecisionRegistry
- [ ] Pass to Orchestrator/Scheduler/Router
- [ ] Query by run_id or category
- [ ] Close registry when done

### Template Usage Checklist
- [ ] Copy template from `patterns/templates/`
- [ ] Identify variables to replace
- [ ] Apply template (manual or scripted)
- [ ] Verify generated code compiles/runs

---

**Guide Version**: 1.0.0
**Last Updated**: 2025-12-05
**Status**: ✅ Production Ready
