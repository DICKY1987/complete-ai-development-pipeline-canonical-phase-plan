---
doc_id: DOC-PLAN-DECISION-ELIMINATION-IMPLEMENTATION-001
phase_id: PH-DECISION-ELIM-001
date: 2025-12-05
status: proposed
execution_pattern: EXEC-002 (Module-Centric Parallel Development)
---

# Decision Elimination Implementation - Phase Plan

## Executive Summary

**Objective**: Eliminate nondeterministic decision points in the pipeline and implement decision elimination patterns from UTE playbook.

**Scope**: Address 7 categories of nondeterminism + implement decision tracking/logging infrastructure

**Timeline**: 3-5 days (with parallel workstreams)

**Success Criteria**:
- ✅ Scheduler produces deterministic task execution order
- ✅ Router provides reproducible tool selection
- ✅ Decision log infrastructure operational
- ✅ Deterministic testing mode available
- ✅ Pattern templates formalized in repository

---

## Phase Overview

### Discovery Review (Completed)

**Files Reviewed**:
1. ✅ `patterns/schemas/decision_elimination_bootstrap.schema.*` - Schema structure
2. ✅ `patterns/specs/decision_elimination_bootstrap.pattern.yaml` - Pattern spec
3. ✅ `.state/routing_decisions.json` - Current decision logging
4. ✅ `templates/decision_log_template.md` - Decision documentation template
5. ✅ `patterns/decisions/decision_template.yaml` - MADR-style decision records
6. ✅ `UTE_Decision Elimination Through Pattern Recognition6.md` - Core technique
7. ✅ `UTE_decision-elimination-playbook.md` - Replication playbook
8. ✅ `NONDETERMINISM_ANALYSIS.md` - System nondeterminism scan

**Key Findings**:
- 🔴 **HIGH**: Scheduler dict iteration causes nondeterministic task execution
- 🟡 **MEDIUM**: Router round-robin state is non-persistent
- 🟡 **MEDIUM**: Async operations return in completion order
- 🟢 **LOW**: UUID/timestamp usage is expected but blocks replay testing
- 🟢 **LOW**: Filesystem traversal order varies by OS

**Decision Elimination Framework Status**:
- ✅ Pattern schema exists (`PAT-DECISION-ELIMINATION-BOOTSTRAP-001`)
- ✅ Decision templates available (YAML + Markdown)
- ✅ Executor stub exists (`decision_elimination_bootstrap_executor.ps1`)
- ⚠️ Examples are minimal/placeholder only
- ❌ No integration with core orchestrator
- ❌ No deterministic mode flag in codebase

---

## Workstream Distribution

### Strategy: 3 Independent Parallel Workstreams

Following **EXEC-002** (Module-Centric Parallel Development):
- Each workstream targets independent modules/files
- Minimal cross-workstream dependencies
- Can execute in parallel sessions
- Merge-friendly (different files)

```
WS-01: Deterministic Execution (core/engine)
WS-02: Decision Infrastructure (patterns, .state)
WS-03: Testing & Validation (tests, docs)
```

---

## Workstream 1: Deterministic Execution

**DOC_ID**: `DOC-WS-DECISION-ELIM-DETERMINISTIC-EXEC-001`

**Objective**: Fix nondeterministic decision points in core execution engine

**Execution Pattern**: EXEC-001 (Atomic File Edits)

### Tasks

#### Task 1.1: Fix Scheduler Task Ordering
**File**: `core/engine/scheduler.py`
**Line**: 69
**Current**:
```python
for task_id, task in self.tasks.items():
```

**Fix**:
```python
for task_id, task in sorted(self.tasks.items()):
```

**Impact**: Deterministic task execution order when multiple tasks are ready

**Time**: 5 minutes
**Risk**: NONE (pure ordering change, no logic change)

---

#### Task 1.2: Make Router Candidate Selection Deterministic
**File**: `core/engine/router.py`

**Location 1**: `_find_capable_tools()` method (returns unsorted list)
**Location 2**: `_select_by_metrics()` method (needs tie-breaking)

**Changes**:
1. Sort capable tools by tool_id before returning:
   ```python
   return sorted(capable)  # Line ~297
   ```

2. Add deterministic tie-breaking in metrics-based selection:
   ```python
   # Sort by success rate, then by tool_id for determinism
   return sorted(
       candidates,
       key=lambda t: (
           -self._get_success_rate(t),  # Higher is better
           t  # Alphabetical tie-breaker
       )
   )[0]
   ```

**Time**: 10 minutes
**Risk**: LOW (preserves existing behavior, adds ordering)

---

#### Task 1.3: Persist Round-Robin State
**File**: `core/engine/router.py`

**Current**: `InMemoryStateStore` loses state on restart

**Options**:
- **Option A**: File-based persistence (`.state/router_state.json`)
- **Option B**: Database persistence (existing `db` instance)
- **Option C**: Keep in-memory but document limitation

**Recommendation**: Option A (simplest, no new dependencies)

**Implementation**:
```python
class FileBackedStateStore:
    def __init__(self, state_file=".state/router_state.json"):
        self.state_file = Path(state_file)
        self._load_state()

    def _load_state(self):
        if self.state_file.exists():
            data = json.loads(self.state_file.read_text())
            self._round_robin_indices = data.get("round_robin", {})
            self._tool_metrics = data.get("metrics", {})
        else:
            self._round_robin_indices = {}
            self._tool_metrics = {}

    def _save_state(self):
        self.state_file.parent.mkdir(exist_ok=True)
        self.state_file.write_text(json.dumps({
            "round_robin": self._round_robin_indices,
            "metrics": self._tool_metrics
        }))

    def set_round_robin_index(self, rule_id: str, index: int):
        self._round_robin_indices[rule_id] = index
        self._save_state()
```

**Time**: 20 minutes
**Risk**: LOW (new class, backward compatible)

---

#### Task 1.4: Add Deterministic Mode Flag
**File**: `core/engine/orchestrator.py`

**Purpose**: Allow deterministic UUID/timestamp generation for testing

**Implementation**:
```python
class Orchestrator:
    def __init__(
        self,
        db: Optional[Database] = None,
        event_bus: Optional[EventBus] = None,
        deterministic_mode: bool = False  # NEW
    ):
        self.deterministic_mode = deterministic_mode
        self._deterministic_counter = 0
        # ... existing code

def generate_ulid(self) -> str:
    """Generate ULID (deterministic if flag set)"""
    if self.deterministic_mode:
        # Use counter-based IDs for reproducibility
        self._deterministic_counter += 1
        return f"DET{self._deterministic_counter:022d}"
    else:
        return uuid.uuid4().hex.upper()[:26]

def now_iso(self) -> str:
    """Get timestamp (deterministic if flag set)"""
    if self.deterministic_mode:
        # Use epoch for deterministic timestamps
        return "2024-01-01T00:00:00.000000Z"
    else:
        return datetime.now(UTC).isoformat() + "Z"
```

**Time**: 15 minutes
**Risk**: NONE (default behavior unchanged)

---

### Workstream 1 Summary

**Total Time**: 50 minutes (atomic edits only)

**Files Changed**:
- `core/engine/scheduler.py` (1 line change)
- `core/engine/router.py` (~40 line additions, 3 line changes)
- `core/engine/orchestrator.py` (~20 line additions)

**Testing**:
- Run existing tests with `deterministic_mode=True`
- Verify task execution order is stable
- Verify router decisions are reproducible

**Dependencies**: NONE (can run immediately)

---

## Workstream 2: Decision Infrastructure

**DOC_ID**: `DOC-WS-DECISION-ELIM-INFRASTRUCTURE-002`

**Objective**: Implement decision tracking and pattern template infrastructure

**Execution Pattern**: EXEC-003 (Template-Based Creation)

### Tasks

#### Task 2.1: Enhance Decision Logging
**File**: `core/engine/router.py` (already emits decisions to `.state/routing_decisions.json`)

**Current State**: Basic logging exists
**Enhancement**: Add more decision types

**New Decision Categories**:
1. `scheduling_decision` - Which tasks to run next
2. `retry_decision` - Whether to retry failed task
3. `circuit_breaker_decision` - Whether to open circuit breaker
4. `tool_selection_decision` - Already exists (routing)

**Implementation**: Add decision logging to:
- `core/engine/scheduler.py::get_ready_tasks()` - log which tasks selected
- `core/engine/resilience/retry.py::should_retry()` - log retry decisions
- `core/engine/resilience/circuit_breaker.py::call()` - log circuit breaker state changes

**Time**: 30 minutes (3 small additions)
**Risk**: LOW (additive only, no behavior change)

---

#### Task 2.2: Create Pattern Template Library
**Directory**: `patterns/templates/`

**Objective**: Formalize reusable templates from UTE playbook

**Templates to Create** (using EXEC-003 - template-based creation):

1. **Module Manifest Template** (`module_manifest.template`)
   - Based on `.ai-module-manifest` pattern
   - Variables: `{module_name}`, `{purpose}`, `{layer}`, `{maturity}`
   - Lines: 50-100
   - Time: 10 minutes

2. **API Endpoint Template** (`api_endpoint.py.template`)
   - CRUD pattern from playbook
   - Variables: `{resource}`, `{schema}`, `{table}`
   - Time: 8 minutes

3. **Test Case Template** (`test_case.py.template`)
   - Happy path + 2 error cases
   - Variables: `{function_name}`, `{valid_input}`, `{invalid_cases}`
   - Time: 8 minutes

4. **Decision Record Template** (`decision_record.md.template`)
   - Enhanced version of existing `decision_template.yaml`
   - Includes ROI tracking, pattern links
   - Time: 10 minutes

**Total Time**: 36 minutes
**Output**: 4 template files in `patterns/templates/`

---

#### Task 2.3: Decision Registry Implementation
**File**: `patterns/decisions/decision_registry.py`

**Purpose**: Track all decisions made by the system

**Schema**:
```python
@dataclass
class Decision:
    decision_id: str
    timestamp: str
    category: str  # routing, scheduling, retry, circuit_breaker
    context: Dict[str, Any]
    options: List[str]
    selected_option: str
    rationale: str
    metadata: Dict[str, Any]

class DecisionRegistry:
    def __init__(self, storage_path=".state/decisions.db"):
        self.db = sqlite3.connect(storage_path)
        self._init_schema()

    def log_decision(self, decision: Decision):
        """Record a decision"""
        ...

    def query_decisions(
        self,
        category: Optional[str] = None,
        since: Optional[str] = None,
        run_id: Optional[str] = None
    ) -> List[Decision]:
        """Query decision history"""
        ...

    def get_decision_stats(self) -> Dict[str, Any]:
        """Get decision statistics"""
        ...
```

**Time**: 45 minutes
**Output**: New module with SQLite-backed decision tracking

---

#### Task 2.4: Integrate Decision Registry with Orchestrator
**Files**:
- `core/engine/orchestrator.py`
- `core/engine/router.py`
- `core/engine/scheduler.py`

**Changes**:
1. Add `decision_registry` parameter to constructors
2. Call `registry.log_decision()` at decision points
3. Emit decisions to event bus (existing pattern)

**Example**:
```python
# In router.py
decision = Decision(
    decision_id=generate_decision_id(),
    timestamp=now_iso(),
    category="routing",
    context={"task_kind": task_kind, "run_id": run_id},
    options=candidates,
    selected_option=selected_tool,
    rationale=f"Strategy: {strategy}",
    metadata={"rule_id": rule_id}
)
self.decision_registry.log_decision(decision)
```

**Time**: 30 minutes (3 small integrations)
**Risk**: LOW (optional parameter, backward compatible)

---

### Workstream 2 Summary

**Total Time**: 141 minutes (~2.5 hours)

**Files Created**:
- `patterns/templates/module_manifest.template`
- `patterns/templates/api_endpoint.py.template`
- `patterns/templates/test_case.py.template`
- `patterns/templates/decision_record.md.template`
- `patterns/decisions/decision_registry.py`

**Files Modified**:
- `core/engine/router.py` (add registry integration)
- `core/engine/scheduler.py` (add decision logging)
- `core/engine/orchestrator.py` (add registry parameter)

**Dependencies**: None (independent of WS-01)

---

## Workstream 3: Testing & Validation

**DOC_ID**: `DOC-WS-DECISION-ELIM-TESTING-003`

**Objective**: Validate deterministic behavior and document decision elimination patterns

**Execution Pattern**: EXEC-004 (Test-First Development)

### Tasks

#### Task 3.1: Create Determinism Tests
**File**: `tests/test_deterministic_execution.py`

**Test Cases**:

1. **Test Scheduler Determinism**:
   ```python
   def test_scheduler_produces_deterministic_task_order():
       """Verify tasks with same dependencies execute in sorted order"""
       scheduler = ExecutionScheduler()

       # Add 5 tasks with no dependencies
       tasks = [Task(f"task_{i}", "test") for i in [5, 2, 8, 1, 9]]
       for task in tasks:
           scheduler.add_task(task)

       # Get ready tasks twice
       ready_1 = [t.task_id for t in scheduler.get_ready_tasks()]
       ready_2 = [t.task_id for t in scheduler.get_ready_tasks()]

       # Should be identical and sorted
       assert ready_1 == ready_2
       assert ready_1 == sorted(ready_1)
   ```

2. **Test Router Determinism**:
   ```python
   def test_router_produces_reproducible_selections():
       """Verify same input produces same routing decision"""
       router = TaskRouter(config_path, deterministic=True)

       # Route same task 10 times
       selections = [
           router.route_task("code_edit", risk_tier="low")
           for _ in range(10)
       ]

       # All selections should be identical
       assert len(set(selections)) == 1
   ```

3. **Test Orchestrator Determinism**:
   ```python
   def test_orchestrator_generates_deterministic_ids():
       """Verify deterministic mode produces reproducible IDs"""
       orch_1 = Orchestrator(deterministic_mode=True)
       orch_2 = Orchestrator(deterministic_mode=True)

       run_1 = orch_1.create_run("proj", "phase")
       run_2 = orch_2.create_run("proj", "phase")

       assert run_1 == run_2  # Should be identical
   ```

**Time**: 40 minutes
**Output**: 8-10 test functions covering determinism

---

#### Task 3.2: Create Decision Tracking Tests
**File**: `tests/test_decision_registry.py`

**Test Cases**:

1. **Test Decision Logging**:
   ```python
   def test_decision_registry_logs_decisions():
       registry = DecisionRegistry(":memory:")

       decision = Decision(
           decision_id="DEC-001",
           timestamp=now_iso(),
           category="routing",
           context={"task": "edit"},
           options=["aider", "claude"],
           selected_option="aider",
           rationale="First in sorted list"
       )

       registry.log_decision(decision)

       retrieved = registry.query_decisions(category="routing")
       assert len(retrieved) == 1
       assert retrieved[0].decision_id == "DEC-001"
   ```

2. **Test Decision Query**:
   ```python
   def test_query_decisions_by_run_id():
       # Test filtering by run_id
       # Test filtering by category
       # Test filtering by time range
   ```

**Time**: 30 minutes
**Output**: 5-6 test functions for decision registry

---

#### Task 3.3: Update Documentation
**Files**:
- `docs/DECISION_ELIMINATION_GUIDE.md` (NEW)
- `README.md` (update with determinism section)
- `NONDETERMINISM_ANALYSIS.md` (update with fixes)

**Content**:

1. **Decision Elimination Guide** (from UTE playbook):
   - Pattern recognition workflow
   - Template creation steps
   - Replication recipes
   - ROI calculations
   - Time: 30 minutes (use playbook as source)

2. **README Update**:
   - Add "Deterministic Mode" section
   - Document `deterministic_mode=True` flag
   - Time: 10 minutes

3. **Nondeterminism Analysis Update**:
   - Mark fixed issues as ✅ RESOLVED
   - Add "Implementation" section
   - Time: 10 minutes

**Total Time**: 50 minutes

---

#### Task 3.4: Integration Testing
**Test**: Full pipeline run with deterministic mode

**Steps**:
1. Create test plan (3 tasks, 2 dependencies)
2. Run orchestrator with `deterministic_mode=True`
3. Capture all decision logs
4. Run again with same input
5. Compare decision logs (should be identical)
6. Compare execution order (should be identical)

**Script**: `tests/integration/test_deterministic_pipeline.py`

**Time**: 40 minutes
**Output**: End-to-end validation script

---

### Workstream 3 Summary

**Total Time**: 160 minutes (~2.7 hours)

**Files Created**:
- `tests/test_deterministic_execution.py`
- `tests/test_decision_registry.py`
- `tests/integration/test_deterministic_pipeline.py`
- `docs/DECISION_ELIMINATION_GUIDE.md`

**Files Modified**:
- `README.md` (add deterministic mode docs)
- `NONDETERMINISM_ANALYSIS.md` (mark fixes)

**Dependencies**: Requires WS-01 complete (deterministic_mode flag)

---

## Dependency Graph

```
WS-01: Deterministic Execution
  ├─ Task 1.1: Scheduler ordering ──┐
  ├─ Task 1.2: Router sorting       ├─> WS-03: Task 3.1 (determinism tests)
  ├─ Task 1.3: Round-robin state    │
  └─ Task 1.4: Deterministic flag ──┘

WS-02: Decision Infrastructure
  ├─ Task 2.1: Decision logging ────> (independent)
  ├─ Task 2.2: Template library ────> (independent)
  ├─ Task 2.3: Decision registry ───┐
  └─ Task 2.4: Registry integration ├─> WS-03: Task 3.2 (registry tests)
                                      └─> WS-03: Task 3.4 (integration test)

WS-03: Testing & Validation
  ├─ Task 3.1: Determinism tests ──> Requires WS-01
  ├─ Task 3.2: Registry tests ─────> Requires WS-02.3
  ├─ Task 3.3: Documentation ──────> (independent)
  └─ Task 3.4: Integration test ───> Requires WS-01 + WS-02.4
```

**Parallel Execution Strategy**:
- **Day 1**: WS-01 (Tasks 1.1-1.4) + WS-02 (Tasks 2.1-2.2) in parallel
- **Day 2**: WS-02 (Tasks 2.3-2.4) + WS-03 (Task 3.3) in parallel
- **Day 3**: WS-03 (Tasks 3.1-3.2-3.4) sequentially (depends on WS-01+WS-02)

---

## Execution Patterns Used

### EXEC-001: Atomic File Edits
**Used in**: WS-01 (Tasks 1.1, 1.2)
**Why**: Single-line or small targeted changes to existing files
**Benefit**: Low risk, easy to verify, no coordination overhead

### EXEC-002: Module-Centric Parallel Development
**Used in**: Overall workstream structure
**Why**: Workstreams target different modules (engine, patterns, tests)
**Benefit**: True parallelism, merge-friendly, independent development

### EXEC-003: Template-Based Creation
**Used in**: WS-02 (Task 2.2)
**Why**: Creating 4 similar template files
**Benefit**: 3x speed improvement from pattern reuse

### EXEC-004: Test-First Development
**Used in**: WS-03 (Tasks 3.1, 3.2, 3.4)
**Why**: Validating deterministic behavior requires tests
**Benefit**: Clear success criteria, prevents regressions

---

## Success Criteria

### Functional Requirements

✅ **Deterministic Execution**:
- [ ] Scheduler returns tasks in sorted order
- [ ] Router returns same tool for same input
- [ ] Orchestrator with `deterministic_mode=True` produces reproducible IDs
- [ ] Round-robin state persists across restarts

✅ **Decision Infrastructure**:
- [ ] Decision registry logs all decision types
- [ ] Query API works for category/run_id/time filters
- [ ] Template library has 4+ production-ready templates
- [ ] Decision logging integrated in 3+ modules

✅ **Testing**:
- [ ] 15+ tests covering determinism
- [ ] Integration test passes with deterministic mode
- [ ] All existing tests still pass
- [ ] Documentation updated with examples

### Performance Requirements

- Decision logging adds <5ms overhead per decision
- Template application saves 80% time vs manual (from playbook)
- Deterministic mode has zero performance impact when disabled

### Quality Requirements

- All code follows existing patterns (Black, PEP8)
- No breaking changes to public APIs
- Backward compatible (deterministic_mode defaults to False)
- Documentation includes migration guide

---

## Risk Assessment

### HIGH PRIORITY RISKS

None identified (all changes are additive or low-impact)

### MEDIUM PRIORITY RISKS

1. **Round-Robin State Persistence**:
   - **Risk**: File-based state could have race conditions
   - **Mitigation**: Use file locking or switch to DB persistence
   - **Fallback**: Document limitation, keep in-memory

2. **Test Flakiness**:
   - **Risk**: Determinism tests could be flaky on different systems
   - **Mitigation**: Use deterministic_mode in all tests
   - **Fallback**: Mark as "may require specific environment"

### LOW PRIORITY RISKS

3. **Template Adoption**:
   - **Risk**: Templates might not fit all use cases
   - **Mitigation**: Start with 4 proven patterns, iterate
   - **Fallback**: Templates are optional, manual approach still works

---

## Timeline

### Optimistic (Parallel Execution)

| Day | Workstream | Tasks | Time | Cumulative |
|-----|-----------|-------|------|------------|
| 1 | WS-01 | 1.1-1.4 | 50 min | 50 min |
| 1 | WS-02 | 2.1-2.2 | 66 min | 50 min (parallel) |
| 2 | WS-02 | 2.3-2.4 | 75 min | 125 min |
| 2 | WS-03 | 3.3 | 50 min | 125 min (parallel) |
| 3 | WS-03 | 3.1-3.2-3.4 | 110 min | 235 min |

**Total**: 235 minutes = **3.9 hours** (with parallelism)

### Realistic (Sequential + Testing Buffer)

| Day | Workstream | Tasks | Time | Notes |
|-----|-----------|-------|------|-------|
| 1 | WS-01 | All | 1.5 hours | Includes testing/debugging |
| 2 | WS-02 | All | 3 hours | Includes template iteration |
| 3 | WS-03 | All | 3.5 hours | Includes integration debugging |

**Total**: **8 hours** (1 full work day)

### Conservative (With Documentation)

Add 4 hours for:
- Comprehensive documentation
- Team review/feedback
- Production readiness checks
- Migration guide writing

**Total**: **12 hours** (1.5 work days)

---

## Validation Plan

### Phase 1: Unit Testing (WS-03.1, WS-03.2)
- Run determinism tests 100 times
- Verify 100% pass rate
- Check no flaky tests

### Phase 2: Integration Testing (WS-03.4)
- Run full pipeline in deterministic mode
- Compare 10 runs (should be identical)
- Verify decision logs are complete

### Phase 3: Regression Testing
- Run entire test suite
- Verify no existing tests broken
- Check performance benchmarks

### Phase 4: Production Readiness
- Code review
- Documentation review
- Security review (decision logs don't leak secrets)
- Merge to main branch

---

## Rollout Strategy

### Stage 1: Deterministic Mode (Optional)
- Deploy with `deterministic_mode=False` by default
- Enable in testing/CI environments only
- Gather feedback on stability

### Stage 2: Decision Logging (Additive)
- Enable decision registry in production
- Monitor decision log volume
- Optimize storage if needed

### Stage 3: Template Library (Discovery)
- Publish templates for team use
- Encourage feedback/iterations
- Add more templates based on usage

### Stage 4: Full Determinism (When Stable)
- Option to enable deterministic_mode in production
- For debugging/replay scenarios
- Document use cases and limitations

---

## Appendix A: File Changes Summary

### Modified Files (11 total)

1. `core/engine/scheduler.py` - 1 line (sort tasks)
2. `core/engine/router.py` - ~60 lines (sorting, persistence, registry)
3. `core/engine/orchestrator.py` - ~30 lines (deterministic flag, registry)
4. `core/engine/resilience/retry.py` - ~10 lines (decision logging)
5. `core/engine/resilience/circuit_breaker.py` - ~10 lines (decision logging)
6. `README.md` - ~20 lines (determinism docs)
7. `NONDETERMINISM_ANALYSIS.md` - ~15 lines (mark resolved)

### Created Files (11 total)

1. `patterns/templates/module_manifest.template`
2. `patterns/templates/api_endpoint.py.template`
3. `patterns/templates/test_case.py.template`
4. `patterns/templates/decision_record.md.template`
5. `patterns/decisions/decision_registry.py`
6. `tests/test_deterministic_execution.py`
7. `tests/test_decision_registry.py`
8. `tests/integration/test_deterministic_pipeline.py`
9. `docs/DECISION_ELIMINATION_GUIDE.md`
10. `.state/router_state.json` (created at runtime)
11. `.state/decisions.db` (created at runtime)

**Total**: 22 files touched, ~350 lines added/modified

---

## Appendix B: Decision Elimination ROI

### Time Investment

**Template Creation**: 36 minutes (one-time)
**Infrastructure**: 141 minutes (one-time)
**Testing**: 160 minutes (one-time)

**Total Investment**: 337 minutes = **5.6 hours**

### Time Savings (Per Use)

**Without Templates**:
- Create API endpoint: 30 minutes
- Write test suite: 25 minutes
- Document module: 20 minutes
- Make architectural decision: 45 minutes

**With Templates**:
- Create API endpoint: 5 minutes (from template)
- Write test suite: 8 minutes (from template)
- Document module: 5 minutes (from template)
- Make architectural decision: 10 minutes (decision registry reference)

**Savings Per Repetition**:
- API endpoint: 25 min × N
- Test suite: 17 min × N
- Documentation: 15 min × N
- Decision: 35 min × N

### Break-Even Analysis

**API Endpoints**: 36 min / 25 min = **2 endpoints** to break even
**Test Suites**: 36 min / 17 min = **3 test suites** to break even
**Documentation**: 36 min / 15 min = **3 docs** to break even

**Realistic Usage (Next 3 Months)**:
- 20 API endpoints → 500 min saved
- 30 test suites → 510 min saved
- 15 docs → 225 min saved

**Total Savings**: 1235 minutes = **20.6 hours**

**ROI**: 20.6 hours saved / 5.6 hours invested = **368% ROI**

---

## Appendix C: References

1. `UTE_Decision Elimination Through Pattern Recognition6.md` - Core technique
2. `UTE_decision-elimination-playbook.md` - Replication guide
3. `NONDETERMINISM_ANALYSIS.md` - Baseline findings
4. `docs/reference/ai-agents/EXECUTION_PATTERNS_MANDATORY.md` - Execution patterns
5. `patterns/decisions/decision_template.yaml` - Decision record template
6. `.state/routing_decisions.json` - Current decision logging

---

## Next Steps

1. **Review this plan** with team/stakeholders
2. **Assign workstreams** to available resources
3. **Create feature branch**: `feature/decision-elimination`
4. **Execute WS-01 + WS-02** in parallel (Day 1-2)
5. **Execute WS-03** sequentially (Day 3)
6. **Merge to main** after validation passes

---

**Plan Status**: ✅ READY FOR EXECUTION
**Confidence**: HIGH (based on proven techniques from UTE playbook)
**Risk Level**: LOW (additive changes, backward compatible)
**Expected Duration**: 1-1.5 days with parallel execution
