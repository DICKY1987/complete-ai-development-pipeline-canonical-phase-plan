---
doc_id: DOC-GUIDE-NEXT-STEPS-PHASE-PLAN-1144
---

# Next Steps Phase Plan

**Created**: 2025-11-23T18:35:17Z  
**Status**: READY  
**Priority**: HIGH  
**Estimated Duration**: 16-20 hours

---

## Executive Summary

Based on the comprehensive codebase review (commit c31486f), the framework is **~80% complete** with strong foundations:
- ✅ 17 JSON schemas (100% complete)
- ✅ Database layer (90% complete)
- ✅ Engine components (75% complete)
- ✅ 129 existing tests

This plan outlines 3 phases to reach **100% completion** and **production readiness**.

---

## Phase Overview

| Phase | Name | Duration | Priority | Dependencies |
|-------|------|----------|----------|--------------|
| **PH-NEXT-001** | Test Execution & Coverage | 4h | CRITICAL | None |
| **PH-NEXT-002** | Missing Components | 8h | HIGH | PH-NEXT-001 |
| **PH-NEXT-003** | Integration & Polish | 4-8h | MEDIUM | PH-NEXT-002 |

**Total Estimated Time**: 16-20 hours

---

## Phase PH-NEXT-001: Test Execution & Coverage Analysis

**Duration**: 4 hours  
**Priority**: CRITICAL  
**Goal**: Validate existing implementation and establish baseline metrics

### Workstreams

#### WS-NEXT-001-001: Run Existing Test Suite (1.5h)

**Objective**: Execute all 129 existing tests and document results

**Tasks**:
1. **TSK-001-001-001**: Run engine tests
   ```bash
   pytest tests/engine/test_routing.py -v
   pytest tests/engine/test_run_lifecycle.py -v
   pytest tests/engine/test_scheduling.py -v
   ```
   - Expected: 107 tests
   - Acceptance: ≥90% pass rate

2. **TSK-001-001-002**: Run monitoring tests
   ```bash
   pytest tests/monitoring/test_progress_tracker.py -v
   pytest tests/monitoring/test_run_monitor.py -v
   ```
   - Expected: 16 tests
   - Acceptance: ≥90% pass rate

3. **TSK-001-001-003**: Run schema tests
   ```bash
   pytest tests/schema/test_all_schemas.py -v
   pytest tests/schema/test_doc_meta.py -v
   ```
   - Expected: 6 tests
   - Acceptance: 100% pass (schemas are critical)

**Acceptance Criteria**:
- [ ] All test files execute without import errors
- [ ] Overall pass rate ≥90%
- [ ] All schema tests pass (17/17 schemas valid)
- [ ] Test execution report generated
- [ ] Failure log created for any failing tests

**Deliverables**:
- `TEST_EXECUTION_REPORT.md` - Results summary
- `test_failures.log` - Detailed failure information (if any)

---

#### WS-NEXT-001-002: Generate Coverage Reports (1.5h)

**Objective**: Establish coverage baseline for all components

**Tasks**:
1. **TSK-001-002-001**: Generate coverage for engine
   ```bash
   pytest tests/engine/ --cov=core/engine --cov-report=html --cov-report=term
   ```
   - Target: ≥75% coverage
   - Output: `htmlcov/engine/index.html`

2. **TSK-001-002-002**: Generate coverage for monitoring
   ```bash
   pytest tests/monitoring/ --cov=core/engine/monitoring --cov-report=html --cov-report=term
   ```
   - Target: ≥80% coverage
   - Output: `htmlcov/monitoring/index.html`

3. **TSK-001-002-003**: Generate coverage for state layer
   ```bash
   pytest tests/engine/test_run_lifecycle.py --cov=core/state --cov-report=html --cov-report=term
   ```
   - Target: ≥90% coverage
   - Output: `htmlcov/state/index.html`

4. **TSK-001-002-004**: Generate unified coverage report
   ```bash
   pytest tests/ --cov=core --cov=schema --cov-report=html --cov-report=json --cov-report=term
   ```
   - Target: Overall ≥80% coverage
   - Output: `htmlcov/index.html`, `coverage.json`

**Acceptance Criteria**:
- [ ] HTML coverage reports generated
- [ ] JSON coverage data generated
- [ ] Coverage badge created (shields.io format)
- [ ] Uncovered lines identified and documented

**Deliverables**:
- `htmlcov/` directory with browsable reports
- `coverage.json` for CI/CD integration
- `COVERAGE_ANALYSIS.md` - Gaps and recommendations

---

#### WS-NEXT-001-003: Fix Critical Test Failures (1h)

**Objective**: Resolve any critical test failures blocking progress

**Tasks**:
1. **TSK-001-003-001**: Analyze test failures
   - Review `test_failures.log`
   - Categorize: Import errors, assertion failures, missing fixtures
   - Prioritize: Critical (blocks others) vs Minor (isolated)

2. **TSK-001-003-002**: Fix import/dependency issues
   - Ensure all test imports resolve
   - Fix missing `__init__.py` files
   - Update sys.path if needed

3. **TSK-001-003-003**: Fix fixture/setup issues
   - Ensure `conftest.py` fixtures work
   - Fix database initialization in tests
   - Validate `tmp_path` fixture usage

4. **TSK-001-003-004**: Re-run tests after fixes
   - Verify fixes resolved failures
   - Update test execution report
   - Document any remaining issues

**Acceptance Criteria**:
- [ ] All critical test failures resolved
- [ ] Pass rate ≥95%
- [ ] No import errors
- [ ] Test suite runs cleanly

**Deliverables**:
- `TEST_FIXES.md` - What was fixed and how
- Updated `TEST_EXECUTION_REPORT.md`

---

### Phase PH-NEXT-001 Completion Criteria

- [ ] All 129 tests executed
- [ ] Pass rate ≥95%
- [ ] Coverage reports generated (overall ≥80%)
- [ ] Critical failures resolved
- [ ] Documentation complete

**Phase Output**: Validated baseline with clear metrics for next steps

---

## Phase PH-NEXT-002: Implement Missing Components

**Duration**: 8 hours  
**Priority**: HIGH  
**Goal**: Complete the 20% of missing functionality

### Gap Analysis (from commit c31486f)

Missing components:
1. ❌ **WorkerLifecycle** table (state machine for worker processes)
2. ❌ **PatchLedger** table (patch state machine)
3. ❌ **TestGate** table (test gate state machine)
4. ❌ **CostTracker** (execution cost tracking)
5. ❌ **EventBus** (event distribution - partially implemented)

---

#### WS-NEXT-002-001: WorkerLifecycle Implementation (2.5h)

**Objective**: Implement worker lifecycle state machine and tracking

**Tasks**:
1. **TSK-002-001-001**: Create WorkerLifecycle schema
   - File: `schema/worker_lifecycle.v1.json`
   - States: idle, busy, paused, stopped, crashed
   - Transitions: start, assign_task, complete_task, pause, resume, crash, shutdown
   - Fields: worker_id, worker_type, current_state, current_task, started_at, last_heartbeat

2. **TSK-002-001-002**: Add workers table to database
   - Migration: `schema/migrations/002_add_workers_table.sql`
   ```sql
   CREATE TABLE workers (
       worker_id TEXT PRIMARY KEY,
       worker_type TEXT NOT NULL,
       state TEXT NOT NULL CHECK(state IN ('idle', 'busy', 'paused', 'stopped', 'crashed')),
       current_task_id TEXT,
       started_at TEXT NOT NULL,
       last_heartbeat TEXT,
       metadata TEXT
   );
   ```

3. **TSK-002-001-003**: Implement WorkerLifecycle class
   - File: `core/engine/worker_lifecycle.py`
   - Methods: create_worker(), start_worker(), assign_task(), complete_task(), shutdown_worker()
   - State machine transitions
   - Heartbeat tracking

4. **TSK-002-001-004**: Create tests
   - File: `tests/engine/test_worker_lifecycle.py`
   - Test: create, start, assign, complete, crash, resume
   - Test: state transition validation
   - Test: heartbeat timeout detection
   - Target: 25+ tests

**Acceptance Criteria**:
- [ ] Schema valid (pytest tests/schema/)
- [ ] Database table created and tested
- [ ] State machine transitions validated
- [ ] Tests pass (≥90% coverage)

**Deliverables**:
- `schema/worker_lifecycle.v1.json`
- `schema/migrations/002_add_workers_table.sql`
- `core/engine/worker_lifecycle.py`
- `tests/engine/test_worker_lifecycle.py`

---

#### WS-NEXT-002-002: PatchLedger Implementation (2.5h)

**Objective**: Implement patch ledger state machine and tracking

**Tasks**:
1. **TSK-002-002-001**: Create PatchLedger schema
   - File: `schema/patch_ledger_entry.v1.json` (already exists - verify)
   - States: created, validated, queued, applied, verified, committed, apply_failed, quarantined, dropped
   - Transitions defined in existing schema

2. **TSK-002-002-002**: Add patch_ledger table to database
   - Migration: `schema/migrations/003_add_patch_ledger_table.sql`
   ```sql
   CREATE TABLE patch_ledger (
       entry_id TEXT PRIMARY KEY,
       patch_id TEXT NOT NULL,
       run_id TEXT NOT NULL,
       state TEXT NOT NULL CHECK(state IN (...)),
       created_at TEXT NOT NULL,
       applied_at TEXT,
       verified_at TEXT,
       committed_at TEXT,
       patch_content TEXT,
       validation_result TEXT,
       metadata TEXT,
       FOREIGN KEY(run_id) REFERENCES runs(run_id)
   );
   ```

3. **TSK-002-002-003**: Implement PatchLedger class
   - File: `core/engine/patch_ledger.py`
   - Methods: create_entry(), validate_patch(), queue_patch(), apply_patch(), verify_patch(), commit_patch()
   - State machine transitions
   - Patch validation logic

4. **TSK-002-002-004**: Create tests
   - File: `tests/engine/test_patch_ledger.py`
   - Test: full lifecycle (created → committed)
   - Test: failure paths (apply_failed, quarantined)
   - Test: state transition validation
   - Target: 30+ tests

**Acceptance Criteria**:
- [ ] Schema validated
- [ ] Database table created and tested
- [ ] Patch lifecycle works end-to-end
- [ ] Tests pass (≥90% coverage)

**Deliverables**:
- `schema/migrations/003_add_patch_ledger_table.sql`
- `core/engine/patch_ledger.py`
- `tests/engine/test_patch_ledger.py`

---

#### WS-NEXT-002-003: TestGate Implementation (2h)

**Objective**: Implement test gate state machine for quality gates

**Tasks**:
1. **TSK-002-003-001**: Create TestGate schema
   - File: `schema/test_gate.v1.json`
   - States: pending, running, passed, failed, skipped
   - Fields: gate_id, run_id, gate_type, test_command, started_at, ended_at, exit_code, output

2. **TSK-002-003-002**: Add test_gates table
   - Migration: `schema/migrations/004_add_test_gates_table.sql`
   ```sql
   CREATE TABLE test_gates (
       gate_id TEXT PRIMARY KEY,
       run_id TEXT NOT NULL,
       gate_type TEXT NOT NULL,
       state TEXT NOT NULL CHECK(state IN ('pending', 'running', 'passed', 'failed', 'skipped')),
       test_command TEXT,
       started_at TEXT,
       ended_at TEXT,
       exit_code INTEGER,
       output TEXT,
       FOREIGN KEY(run_id) REFERENCES runs(run_id)
   );
   ```

3. **TSK-002-003-003**: Implement TestGate class
   - File: `core/engine/test_gate.py`
   - Methods: create_gate(), run_gate(), get_gate_status()
   - Integration with pytest/other test runners
   - Output capture and parsing

4. **TSK-002-003-004**: Create tests
   - File: `tests/engine/test_test_gate.py`
   - Test: create and run gate
   - Test: pass/fail detection
   - Test: output capture
   - Target: 20+ tests

**Acceptance Criteria**:
- [ ] Schema validated
- [ ] Database table created
- [ ] Can execute test commands
- [ ] Tests pass (≥85% coverage)

**Deliverables**:
- `schema/test_gate.v1.json`
- `schema/migrations/004_add_test_gates_table.sql`
- `core/engine/test_gate.py`
- `tests/engine/test_test_gate.py`

---

#### WS-NEXT-002-004: CostTracker Implementation (1h)

**Objective**: Track execution costs (time, API calls, resources)

**Tasks**:
1. **TSK-002-004-001**: Create CostTracker schema
   - File: `schema/cost_record.v1.json`
   - Fields: cost_id, run_id, resource_type, quantity, unit_cost, total_cost, timestamp

2. **TSK-002-004-002**: Add costs table
   - Migration: `schema/migrations/005_add_costs_table.sql`

3. **TSK-002-004-003**: Implement CostTracker class
   - File: `core/engine/cost_tracker.py`
   - Methods: record_cost(), get_run_costs(), get_total_costs()

4. **TSK-002-004-004**: Create tests
   - File: `tests/engine/test_cost_tracker.py`
   - Target: 15+ tests

**Acceptance Criteria**:
- [ ] Schema validated
- [ ] Database table created
- [ ] Can track costs by run
- [ ] Tests pass (≥80% coverage)

**Deliverables**:
- `schema/cost_record.v1.json`
- `schema/migrations/005_add_costs_table.sql`
- `core/engine/cost_tracker.py`
- `tests/engine/test_cost_tracker.py`

---

### Phase PH-NEXT-002 Completion Criteria

- [ ] All 5 missing components implemented
- [ ] All migrations applied successfully
- [ ] All new tests pass (≥85% coverage)
- [ ] Integration with existing components verified
- [ ] Documentation updated

**Phase Output**: Framework at 100% feature complete

---

## Phase PH-NEXT-003: Integration & Production Readiness

**Duration**: 4-8 hours  
**Priority**: MEDIUM  
**Goal**: Ensure all components work together and are production-ready

### Workstreams

#### WS-NEXT-003-001: End-to-End Integration Testing (2h)

**Objective**: Verify all components work together in realistic scenarios

**Tasks**:
1. **TSK-003-001-001**: Create integration test suite
   - File: `tests/integration/test_full_workflow.py`
   - Test: Complete run lifecycle (create → execute → monitor → complete)
   - Test: Multi-step workstream execution
   - Test: Patch creation and application
   - Test: Test gate execution
   - Test: Cost tracking across run

2. **TSK-003-001-002**: Test realistic workstream scenarios
   - File: `tests/integration/test_scenarios.py`
   - Scenario: Software development workflow (code → test → review → deploy)
   - Scenario: Parallel task execution
   - Scenario: Error recovery and retry
   - Scenario: Worker lifecycle management

3. **TSK-003-001-003**: Performance testing
   - File: `tests/integration/test_performance.py`
   - Test: 100 concurrent tasks
   - Test: Large workstream (50+ tasks)
   - Test: Database performance (1000+ runs)

**Acceptance Criteria**:
- [ ] All integration tests pass
- [ ] No race conditions or deadlocks
- [ ] Performance meets targets (TBD)
- [ ] Memory usage acceptable

**Deliverables**:
- `tests/integration/` directory with 3+ test files
- Integration test report

---

#### WS-NEXT-003-002: Documentation & Examples (2h)

**Objective**: Provide comprehensive documentation and examples

**Tasks**:
1. **TSK-003-002-001**: Update API documentation
   - Document all public classes and methods
   - Add docstrings to undocumented functions
   - Generate API reference (Sphinx/MkDocs)

2. **TSK-003-002-002**: Create usage examples
   - Example: Creating and executing a workstream
   - Example: Monitoring run progress
   - Example: Working with patches
   - Example: Cost tracking

3. **TSK-003-002-003**: Update README and guides
   - Update main README with getting started
   - Create developer guide
   - Create deployment guide

**Acceptance Criteria**:
- [ ] All public APIs documented
- [ ] ≥3 working examples
- [ ] README up to date
- [ ] Documentation builds successfully

**Deliverables**:
- Updated docstrings throughout codebase
- `examples/` directory
- Updated README.md
- `docs/` with guides

---

#### WS-NEXT-003-003: CI/CD Pipeline Setup (2-4h)

**Objective**: Automate testing and validation

**Tasks**:
1. **TSK-003-003-001**: Setup GitHub Actions
   - File: `.github/workflows/test.yml`
   - Run: All tests on push/PR
   - Generate: Coverage reports
   - Upload: Coverage to codecov.io

2. **TSK-003-003-002**: Setup quality gates
   - Enforce: 80% minimum coverage
   - Check: No failing tests
   - Validate: All schemas
   - Lint: Code style (black, ruff)

3. **TSK-003-003-003**: Setup release automation
   - Version bumping
   - Changelog generation
   - Tagged releases

**Acceptance Criteria**:
- [ ] CI/CD pipeline runs on all PRs
- [ ] Quality gates enforced
- [ ] Coverage tracking enabled
- [ ] Release process automated

**Deliverables**:
- `.github/workflows/` with CI/CD configs
- Quality gate configuration
- Release automation scripts

---

### Phase PH-NEXT-003 Completion Criteria

- [ ] All integration tests pass
- [ ] Documentation complete
- [ ] CI/CD pipeline operational
- [ ] Framework production-ready

**Phase Output**: Production-ready framework with 100% feature completion

---

## Success Metrics

### Phase PH-NEXT-001
- ✅ Test execution: 100% of tests run
- ✅ Pass rate: ≥95%
- ✅ Coverage: ≥80% overall
- ✅ Critical failures: 0

### Phase PH-NEXT-002
- ✅ Missing components: 5/5 implemented
- ✅ New tests: ≥90 added
- ✅ Coverage: ≥85% for new code
- ✅ Integration: All components work together

### Phase PH-NEXT-003
- ✅ Integration tests: All pass
- ✅ Documentation: 100% of public APIs
- ✅ CI/CD: Automated and passing
- ✅ Production ready: Yes

---

## Risk Mitigation

### High Risks
1. **Test failures block progress**
   - Mitigation: Fix critical failures in PH-NEXT-001 before proceeding
   - Fallback: Document issues and continue with working components

2. **Missing dependencies for new components**
   - Mitigation: Identify dependencies early in each workstream
   - Fallback: Stub out dependencies, implement later

3. **Integration issues between components**
   - Mitigation: Integration tests in PH-NEXT-003 catch issues early
   - Fallback: Add adapter layer if needed

### Medium Risks
1. **Coverage targets not met**
   - Mitigation: Add tests incrementally during implementation
   - Fallback: Document uncovered areas, plan future coverage

2. **Performance issues**
   - Mitigation: Performance tests identify bottlenecks
   - Fallback: Optimize critical paths, defer non-critical

---

## Resource Requirements

### Tools & Dependencies
- Python 3.10+
- pytest with coverage plugin
- jsonschema (for schema validation)
- SQLite3 (for database)
- Optional: codecov.io account for coverage tracking

### Time Allocation
- Developer time: 16-20 hours
- Review time: 2-4 hours
- Total: 18-24 hours

---

## Execution Strategy

### Recommended Approach
1. **Sequential execution**: Complete PH-NEXT-001 fully before starting PH-NEXT-002
2. **Incremental commits**: Commit after each workstream completes
3. **Continuous validation**: Run full test suite after each component added
4. **Documentation as you go**: Update docs alongside implementation

### Parallel Opportunities
Within PH-NEXT-002, workstreams can be parallelized:
- WS-NEXT-002-001 (WorkerLifecycle) + WS-NEXT-002-004 (CostTracker) - Independent
- WS-NEXT-002-002 (PatchLedger) + WS-NEXT-002-003 (TestGate) - Independent

---

## Next Actions

### Immediate (Today)
1. ✅ Review and approve this phase plan
2. ⏳ Execute WS-NEXT-001-001 (Run existing tests)
3. ⏳ Generate initial coverage reports

### Short-term (This Week)
1. Complete Phase PH-NEXT-001 (Test execution & coverage)
2. Begin Phase PH-NEXT-002 (Missing components)
3. Implement WorkerLifecycle and PatchLedger

### Medium-term (Next 2 Weeks)
1. Complete Phase PH-NEXT-002 (All missing components)
2. Begin Phase PH-NEXT-003 (Integration)
3. Setup CI/CD pipeline

---

## Appendix A: File Checklist

### Files to Create (Phase PH-NEXT-001)
- [ ] `TEST_EXECUTION_REPORT.md`
- [ ] `test_failures.log` (if any failures)
- [ ] `COVERAGE_ANALYSIS.md`
- [ ] `TEST_FIXES.md` (if fixes needed)

### Files to Create (Phase PH-NEXT-002)
- [ ] `schema/worker_lifecycle.v1.json`
- [ ] `schema/test_gate.v1.json`
- [ ] `schema/cost_record.v1.json`
- [ ] `schema/migrations/002_add_workers_table.sql`
- [ ] `schema/migrations/003_add_patch_ledger_table.sql`
- [ ] `schema/migrations/004_add_test_gates_table.sql`
- [ ] `schema/migrations/005_add_costs_table.sql`
- [ ] `core/engine/worker_lifecycle.py`
- [ ] `core/engine/patch_ledger.py`
- [ ] `core/engine/test_gate.py`
- [ ] `core/engine/cost_tracker.py`
- [ ] `tests/engine/test_worker_lifecycle.py`
- [ ] `tests/engine/test_patch_ledger.py`
- [ ] `tests/engine/test_test_gate.py`
- [ ] `tests/engine/test_cost_tracker.py`

### Files to Create (Phase PH-NEXT-003)
- [ ] `tests/integration/test_full_workflow.py`
- [ ] `tests/integration/test_scenarios.py`
- [ ] `tests/integration/test_performance.py`
- [ ] `examples/basic_workstream.py`
- [ ] `examples/monitoring_example.py`
- [ ] `examples/patch_workflow.py`
- [ ] `.github/workflows/test.yml`
- [ ] `.github/workflows/release.yml`

---

## Appendix B: Command Reference

### Phase PH-NEXT-001 Commands
```bash
# Run all tests
pytest tests/ -v

# Generate coverage
pytest tests/ --cov=core --cov=schema --cov-report=html --cov-report=json

# Run specific test file
pytest tests/engine/test_routing.py -v

# Run with verbose failure output
pytest tests/ -vv --tb=short
```

### Phase PH-NEXT-002 Commands
```bash
# Apply database migrations
python -c "from core.state.db import init_db; init_db('.ledger/framework.db')"

# Validate new schema
pytest tests/schema/test_all_schemas.py -v

# Run new component tests
pytest tests/engine/test_worker_lifecycle.py -v --cov=core/engine/worker_lifecycle
```

### Phase PH-NEXT-003 Commands
```bash
# Run integration tests
pytest tests/integration/ -v

# Generate full documentation
sphinx-build -b html docs/ docs/_build/html

# Run CI/CD locally (if using act)
act -j test
```

---

## Appendix C: Success Checklist

### Phase PH-NEXT-001 Complete When:
- [ ] All 129 existing tests executed
- [ ] Pass rate ≥95%
- [ ] Coverage reports generated (HTML + JSON)
- [ ] Coverage ≥80% overall
- [ ] Critical failures documented and resolved
- [ ] `TEST_EXECUTION_REPORT.md` created
- [ ] `COVERAGE_ANALYSIS.md` created

### Phase PH-NEXT-002 Complete When:
- [ ] WorkerLifecycle implemented with ≥25 tests
- [ ] PatchLedger implemented with ≥30 tests
- [ ] TestGate implemented with ≥20 tests
- [ ] CostTracker implemented with ≥15 tests
- [ ] All 5 migrations applied successfully
- [ ] All new tests pass (≥90 total)
- [ ] Integration with existing components verified
- [ ] Coverage ≥85% for new code

### Phase PH-NEXT-003 Complete When:
- [ ] Integration tests created (≥3 files)
- [ ] All integration tests pass
- [ ] Performance tests pass
- [ ] API documentation complete
- [ ] ≥3 usage examples created
- [ ] CI/CD pipeline operational
- [ ] All quality gates passing
- [ ] Framework production-ready

---

**End of Phase Plan**
