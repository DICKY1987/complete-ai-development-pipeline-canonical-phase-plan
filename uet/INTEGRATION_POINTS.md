---
doc_id: DOC-GUIDE-INTEGRATION-POINTS-1665
---

# UET V2 Integration Points

**Purpose**: Document how components call each other to prevent circular dependencies
**Status**: DRAFT
**Last Updated**: 2025-11-23

---

## Table of Contents

- [Component Call Graph](#component-call-graph)
- [Event Flow](#event-flow)
- [Database Transaction Boundaries](#database-transaction-boundaries)
- [Circular Dependency Prevention](#circular-dependency-prevention)
- [Integration Patterns](#integration-patterns)

---

## Component Call Graph

### Orchestrator (Root)

```
Orchestrator
  ├─> WorkerLifecycle.spawn_worker()
  ├─> WorkerLifecycle.get_idle_workers()
  ├─> PatchLedger.create_entry(patch)
  ├─> TestGateExecutor.evaluate_gates(phase_id)
  ├─> IntegrationWorker.orchestrate_merge()
  ├─> ContextManager.estimate_tokens(text)
  ├─> FeedbackLoop.handle_test_failure(step_id, results)
  └─> EventBus.emit(event_type, run_id, data)
```

**Purpose**: Central coordinator for workstream execution

**Responsibilities**:
- Spawn workers as needed
- Assign tasks to idle workers
- Capture patches from tool output
- Evaluate test gates at phase boundaries
- Trigger merge orchestration
- Emit execution events

**Called By**: Top-level execution scripts (`run_workstream.py`)

---

### IntegrationWorker (Merge Coordinator)

```
IntegrationWorker
  ├─> PatchLedger.get_patches_by_state('validated')
  ├─> MergeOrchestrator.order_candidates(patches)
  ├─> MergeOrchestrator.merge(patch)
  ├─> TestGateExecutor.validate_merge(patch_id)
  ├─> CompensationEngine.rollback_on_failure(patch_id)
  └─> EventBus.emit(MERGE_*, data)
```

**Purpose**: Deterministically merge parallel workstream results

**Responsibilities**:
- Collect validated patches
- Order patches by priority/dependencies/age
- Apply patches sequentially
- Validate after each merge
- Rollback on failure

**Called By**: Orchestrator (after parallel tasks complete)

---

### MergeOrchestrator (Merge Logic)

```
MergeOrchestrator
  ├─> PatchValidator.validate_scope(patch)
  ├─> git_ops.apply_patch(patch.diff_text)
  ├─> LanguageValidator.run_validators(files)
  ├─> PatchLedger.transition_state(ledger_id, 'applied')
  └─> EventBus.emit(MERGE_CONFLICT, conflict_data)
```

**Purpose**: Execute individual patch merges with validation

**Responsibilities**:
- Validate patch scope before apply
- Apply patch via git
- Run language-specific validators (ruff, black, pytest)
- Detect and report conflicts
- Update patch ledger state

**Called By**: IntegrationWorker

---

### PatchLedger (State Tracking)

```
PatchLedger
  ├─> PatchValidator.validate(patch)
  ├─> db.create_ledger_entry()
  ├─> db.update_ledger_state()
  ├─> db.query_patches_by_state()
  └─> EventBus.emit(PATCH_CREATED, patch_data)
```

**Purpose**: Track patch lifecycle from creation to commit

**Responsibilities**:
- Create ledger entries for new patches
- Enforce state machine transitions
- Run validation pipeline
- Quarantine failed patches
- Query patches by state/phase

**Called By**: Orchestrator, IntegrationWorker, MergeOrchestrator

---

### PatchValidator (Validation Logic)

```
PatchValidator
  ├─> PatchPolicyEngine.get_effective_policy(scope)
  ├─> diff_parser.parse_unified_diff(patch.diff_text)
  ├─> (No database calls - pure validation)
  └─> (No event emissions - returns ValidationResult)
```

**Purpose**: Validate patches against format/scope/constraints

**Responsibilities**:
- Check unified diff format
- Enforce scope limits (max files/lines)
- Check forbidden paths/patterns
- Validate against policy

**Called By**: PatchLedger, MergeOrchestrator

---

### TestGateExecutor (Gate Validation)

```
TestGateExecutor
  ├─> Scheduler.get_blocked_tasks(gate_id)
  ├─> subprocess.run(gate.command)
  ├─> db.update_gate_state()
  └─> EventBus.emit(GATE_PASSED/GATE_FAILED, gate_data)
```

**Purpose**: Execute test gates and block dependent tasks

**Responsibilities**:
- Run gate commands (lint, unit, integration, security)
- Record exit code and output
- Block/unblock dependent tasks
- Emit gate events

**Called By**: Orchestrator (at phase boundaries), IntegrationWorker (after merge)

---

### WorkerLifecycle (Worker Management)

```
WorkerLifecycle
  ├─> db.create_worker()
  ├─> db.update_worker_state()
  ├─> db.query_workers_by_state()
  ├─> WorkerHealthMonitor.check_health(worker_id)
  └─> EventBus.emit(WORKER_*, worker_data)
```

**Purpose**: Manage worker lifecycle from spawn to termination

**Responsibilities**:
- Spawn workers with affinity
- Transition worker states
- Record heartbeats
- Terminate workers gracefully
- Quarantine unhealthy workers

**Called By**: Orchestrator

---

### ContextManager (Token Management)

```
ContextManager
  ├─> tiktoken.encoding_for_model(model)
  ├─> (No database calls - pure computation)
  └─> (No event emissions - returns token count or reduced text)
```

**Purpose**: Estimate and reduce context size for LLM calls

**Responsibilities**:
- Estimate token count
- Apply pruning/summarization/chunking strategies
- Return optimized text

**Called By**: Orchestrator (before tool invocation)

---

### FeedbackLoop (Test-Driven Execution)

```
FeedbackLoop
  ├─> Orchestrator.enqueue_task(fix_task)
  ├─> (Analyzes test results, creates fix tasks)
  └─> EventBus.emit(FIX_TASK_CREATED, task_data)
```

**Purpose**: Auto-create fix tasks from test failures

**Responsibilities**:
- Detect test failures
- Extract affected files from errors
- Generate fix task descriptions
- Enqueue fix tasks with high priority

**Called By**: Orchestrator (after test execution)

---

### CompensationEngine (Rollback Logic)

```
CompensationEngine
  ├─> PatchLedger.get_patch(patch_id)
  ├─> git_ops.revert_patch(patch_id)
  ├─> PatchLedger.transition_state(ledger_id, 'rolled_back')
  └─> EventBus.emit(ROLLBACK_COMPLETED, rollback_data)
```

**Purpose**: Rollback failed patches (Saga pattern)

**Responsibilities**:
- Execute compensation actions
- Revert patches via git
- Update patch ledger state
- Emit rollback events

**Called By**: IntegrationWorker (on merge failure)

---

## Event Flow

### Execution Flow (Normal Path)

```
1. Orchestrator.run_step(step)
   └─> emits: STEP_STARTED

2. Orchestrator.spawn_worker(worker_type)
   └─> WorkerLifecycle.spawn_worker()
       └─> emits: WORKER_SPAWNED

3. Worker executes tool (via Executor)
   └─> produces: patch artifact (unified diff)

4. Orchestrator.capture_patch(tool_output)
   ├─> PatchLedger.create_entry(patch)
   │   ├─> PatchValidator.validate(patch)
   │   │   └─> PatchPolicyEngine.get_effective_policy()
   │   └─> emits: PATCH_CREATED or PATCH_QUARANTINED
   └─> updates: step.status = 'completed'

5. IntegrationWorker.orchestrate_merge()
   ├─> PatchLedger.get_patches_by_state('validated')
   ├─> MergeOrchestrator.order_candidates(patches)
   ├─> FOR EACH patch:
   │   ├─> MergeOrchestrator.merge(patch)
   │   │   ├─> git_ops.apply_patch()
   │   │   ├─> LanguageValidator.run_validators()
   │   │   └─> PatchLedger.transition_state(ledger_id, 'applied')
   │   ├─> TestGateExecutor.validate_merge(patch_id)
   │   │   └─> emits: GATE_PASSED or GATE_FAILED
   │   └─> IF gate passed:
   │       └─> PatchLedger.transition_state(ledger_id, 'committed')
   └─> emits: MERGE_COMPLETED or MERGE_FAILED

6. WorkerLifecycle.terminate_worker(worker_id)
   └─> emits: WORKER_TERMINATED
```

### Failure Flow (Rollback Path)

```
1. MergeOrchestrator.merge(patch)
   └─> git_ops.apply_patch() → CONFLICT

2. MergeOrchestrator
   ├─> PatchLedger.transition_state(ledger_id, 'apply_failed')
   └─> emits: MERGE_CONFLICT

3. IntegrationWorker.handle_conflict(conflict)
   ├─> CompensationEngine.rollback_on_failure(patch_id)
   │   ├─> git_ops.revert_patch(patch_id)
   │   ├─> PatchLedger.transition_state(ledger_id, 'rolled_back')
   │   └─> emits: ROLLBACK_COMPLETED
   └─> IF unresolvable:
       └─> HumanReview.create_review_task(conflict)
```

---

## Database Transaction Boundaries

### Transaction Scope

**Rule**: Each component method is atomic (one transaction)

**Small Transactions** (single table, single row):
- `WorkerLifecycle.heartbeat(worker_id)` - UPDATE workers SET last_heartbeat
- `PatchLedger.quarantine(ledger_id, reason)` - UPDATE patch_ledger_entries

**Medium Transactions** (single table, multiple rows OR multiple tables, related):
- `PatchLedger.create_entry(patch)` - INSERT patches + INSERT patch_ledger_entries
- `MergeOrchestrator.merge(patch)` - INSERT patches + UPDATE patch_ledger + INSERT run_events

**Large Transactions** (multiple tables, complex logic):
- `IntegrationWorker.orchestrate_merge(patches)` - Multiple merges in sequence, each atomic

### Transaction Isolation

**Patch Ledger State Transitions** (Optimistic Locking):
```python
# Read with version
SELECT state, updated_at FROM patch_ledger_entries WHERE ledger_id = ?

# Update with version check
UPDATE patch_ledger_entries
SET state = ?, updated_at = ?
WHERE ledger_id = ? AND updated_at = ?  -- Compare-and-swap
```

**Worker State Transitions** (Pessimistic Locking):
```python
# Acquire row lock
SELECT * FROM workers WHERE worker_id = ? FOR UPDATE

# Update state
UPDATE workers SET state = ?, updated_at = ? WHERE worker_id = ?

# Release lock on commit
```

### Rollback Scenarios

**Worker Spawn Failure**:
```python
try:
    db.execute("INSERT INTO workers (...) VALUES (...)")
    worker_process = subprocess.Popen(...)  # This might fail
except Exception:
    db.rollback()  # Remove worker from DB
    raise
```

**Patch Apply Failure**:
```python
try:
    git_ops.apply_patch(patch)  # This might fail
    db.execute("UPDATE patch_ledger_entries SET state = 'applied'")
    db.commit()
except GitApplyError:
    db.rollback()  # Keep patch in 'queued' state
    db.execute("UPDATE patch_ledger_entries SET state = 'apply_failed'")
    db.commit()
```

---

## Circular Dependency Prevention

### Forbidden Dependencies

**❌ CIRCULAR** (these create cycles):

```python
# PatchLedger → WorkerLifecycle (creates cycle)
class PatchLedger:
    def create_entry(self, patch):
        worker = WorkerLifecycle().get_worker(patch.worker_id)  # ❌ DON'T DO THIS

# TestGateExecutor → MergeOrchestrator (creates cycle)
class TestGateExecutor:
    def evaluate_gate(self, gate_id):
        merge_result = MergeOrchestrator().merge(...)  # ❌ DON'T DO THIS
```

### Allowed Dependencies

**✅ ALLOWED** (directed acyclic graph):

```python
# All components → EventBus (OK, EventBus is leaf)
class PatchLedger:
    def create_entry(self, patch):
        self.event_bus.emit(EventType.PATCH_CREATED, patch)  # ✅ OK

# All components → Database (OK, Database is leaf)
class WorkerLifecycle:
    def spawn_worker(self, worker_id):
        self.db.execute("INSERT INTO workers ...")  # ✅ OK

# Orchestrator → All components (OK, Orchestrator is root)
class Orchestrator:
    def run(self):
        self.worker_lifecycle.spawn_worker(...)  # ✅ OK
        self.patch_ledger.create_entry(...)      # ✅ OK
```

### Dependency Graph (Directed Acyclic)

```
Orchestrator (root)
  ├─> WorkerLifecycle
  ├─> PatchLedger ───> PatchValidator ───> PatchPolicyEngine
  ├─> TestGateExecutor
  ├─> IntegrationWorker ───> MergeOrchestrator ───> LanguageValidator
  │                       └─> CompensationEngine
  ├─> ContextManager
  └─> FeedbackLoop

All components (leaves)
  ├─> EventBus
  └─> Database
```

**Verify Acyclic**:
```bash
# Use dependency checker
python scripts/check_circular_dependencies.py

# Expected output:
# ✅ No circular dependencies detected
# Dependency graph is acyclic
```

---

## Integration Patterns

### Pattern 1: Event-Driven Coordination

**Problem**: Component A needs to notify Component B without direct coupling

**Solution**: Use EventBus

```python
# Component A (emitter)
class PatchLedger:
    def quarantine(self, ledger_id, reason):
        self.event_bus.emit(EventType.PATCH_QUARANTINED, {
            'ledger_id': ledger_id,
            'reason': reason
        })

# Component B (subscriber)
class HumanReview:
    def __init__(self, event_bus):
        event_bus.subscribe(EventType.PATCH_QUARANTINED, self.handle_quarantined_patch)

    def handle_quarantined_patch(self, event_data):
        # Create review task
        pass
```

**Benefits**:
- Loose coupling
- Easy to add new subscribers
- No circular dependencies

---

### Pattern 2: Dependency Injection

**Problem**: Component needs access to another component

**Solution**: Inject dependencies via constructor

```python
# ❌ BAD: Direct instantiation (tight coupling)
class IntegrationWorker:
    def __init__(self):
        self.patch_ledger = PatchLedger()  # Hard-coded

# ✅ GOOD: Dependency injection
class IntegrationWorker:
    def __init__(self, patch_ledger: PatchLedger):
        self.patch_ledger = patch_ledger  # Injected

# Usage
patch_ledger = PatchLedger(db)
integration_worker = IntegrationWorker(patch_ledger)
```

**Benefits**:
- Testable (easy to mock)
- Flexible (swap implementations)
- Explicit dependencies

---

### Pattern 3: Command Pattern (for Compensation)

**Problem**: Need to undo operations (rollback)

**Solution**: Use Command pattern with compensating actions

```python
@dataclass
class CompensationCommand:
    forward_action: Callable
    compensation_action: Callable
    description: str

class CompensationEngine:
    def execute_with_compensation(self, command: CompensationCommand):
        try:
            command.forward_action()
        except Exception:
            # Rollback
            command.compensation_action()
            raise

# Usage
command = CompensationCommand(
    forward_action=lambda: git_ops.apply_patch(patch),
    compensation_action=lambda: git_ops.revert_patch(patch.patch_id),
    description="Apply patch XYZ"
)
compensation_engine.execute_with_compensation(command)
```

---

### Pattern 4: Strategy Pattern (for Policies)

**Problem**: Different validation rules for different scopes

**Solution**: Use Strategy pattern with policy inheritance

```python
class PatchPolicyEngine:
    def get_effective_policy(self, scope: str) -> PatchPolicy:
        # Global policy (base)
        policy = self.policies['global']

        # Override with project policy
        if scope in self.policies:
            policy = self._merge_policies(policy, self.policies[scope])

        return policy
```

---

## Integration Testing

### Test Scenarios

**Scenario 1: Full Workflow** (Orchestrator → Workers → Patches → Merge)
```python
def test_full_workflow_happy_path():
    orchestrator = Orchestrator(db, event_bus)
    workstream = load_workstream("tests/fixtures/simple_workstream.json")

    result = orchestrator.run(workstream)

    assert result.status == "SUCCESS"
    # Verify events
    events = event_bus.get_events(result.run_id)
    assert EventType.STEP_STARTED in [e.type for e in events]
    assert EventType.PATCH_CREATED in [e.type for e in events]
    assert EventType.MERGE_COMPLETED in [e.type for e in events]
```

**Scenario 2: Conflict Handling** (MergeOrchestrator → CompensationEngine)
```python
def test_merge_conflict_triggers_rollback():
    merge_orch = MergeOrchestrator(db, event_bus)
    patch = create_conflicting_patch()  # Modifies same lines as previous patch

    with pytest.raises(MergeConflictError):
        merge_orch.merge(patch)

    # Verify rollback
    ledger_entry = patch_ledger.get_entry_by_patch_id(patch.patch_id)
    assert ledger_entry.state == PatchState.ROLLED_BACK
```

---

## Summary

**Key Principles**:
1. ✅ **Directed Acyclic Graph** - No circular dependencies
2. ✅ **Event-Driven** - Loose coupling via EventBus
3. ✅ **Dependency Injection** - Explicit dependencies
4. ✅ **Transaction Boundaries** - Atomic operations
5. ✅ **Command Pattern** - Compensation for rollback

**Dependency Flow**:
```
Orchestrator (root)
    ↓
Components (middle)
    ↓
EventBus + Database (leaves)
```

**Verification**:
```bash
python scripts/check_circular_dependencies.py
python scripts/validate_integration_points.py
```

---

## References

- **Component Contracts**: [COMPONENT_CONTRACTS.md](COMPONENT_CONTRACTS.md)
- **State Machines**: [STATE_MACHINES.md](STATE_MACHINES.md)
- **Testing Requirements**: [TESTING_REQUIREMENTS.md](TESTING_REQUIREMENTS.md)

---

**Last Updated**: 2025-11-23
**Next Review**: Before Phase A starts
