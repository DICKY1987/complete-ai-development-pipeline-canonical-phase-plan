---
doc_id: DOC-GUIDE-PHASE-CONTRACT-ENFORCEMENT-TASKS-001
created: 2025-12-05
status: active
---

# Phase I/O Contract Enforcement - Implementation Tasks

## Purpose

Define concrete tasks needed to ensure **automated enforcement** of phase I/O contracts across the pipeline (Phases 0-7).

## Current State

**What we have:**
- ✅ Phase I/O contracts documented in phase README.md files
- ✅ UET_SUBMODULE_IO_CONTRACTS.md with versioned data shapes
- ✅ JSON schemas in `schema/` directory (17 schemas)
- ✅ Bootstrap validator (`core/bootstrap/validator.py`)
- ⚠️ Manual validation scripts (scattered across `scripts/`, `phase*/modules/`)
- ❌ No centralized contract enforcement framework
- ❌ No runtime contract validation gates
- ❌ No contract version compatibility checking

**What we need:**
Automated, fail-fast validation at **every phase boundary**.

---

## Priority 1: Core Contract Enforcement Infrastructure

### Task 1.1: Create Contract Validator Framework
**File**: `core/contracts/validator.py`

**Requirements:**
```python
class PhaseContractValidator:
    """Validates phase entry/exit contracts"""

    def validate_entry(self, phase_id: str, context: dict) -> ValidationResult:
        """
        Validate phase entry requirements:
        - required_files exist
        - required_db_tables exist
        - required_state_flags are set
        """

    def validate_exit(self, phase_id: str, artifacts: dict) -> ValidationResult:
        """
        Validate phase exit artifacts:
        - produced_files exist and valid
        - updated_db_tables have correct schema
        - emitted_events are logged
        """

    def validate_schema(self, data: dict, schema_version: str) -> ValidationResult:
        """Validate data against versioned schema"""
```

**Acceptance Criteria:**
- [ ] Loads phase contracts from phase README.md files
- [ ] Validates file existence (required_files)
- [ ] Validates DB table schemas (required_db_tables)
- [ ] Validates state flags from `.state/orchestration.db`
- [ ] Returns structured ValidationResult with errors/warnings
- [ ] Logs validation results to audit trail

**Estimated Effort**: 8 hours

---

### Task 1.2: Schema Version Registry
**File**: `core/contracts/schema_registry.py`

**Requirements:**
```python
class SchemaRegistry:
    """Central registry for all versioned schemas"""

    def get_schema(self, name: str, version: str) -> dict:
        """Load schema by name and version"""

    def validate_compatibility(
        self, old_version: str, new_version: str
    ) -> CompatibilityResult:
        """Check if version upgrade is compatible"""

    def list_schemas(self) -> list[SchemaInfo]:
        """List all available schemas with versions"""
```

**Schema Discovery:**
- Scan `schema/*.json` files
- Parse version from filename (e.g., `execution_request.v1.json`)
- Build in-memory index on startup
- Support schema migrations

**Acceptance Criteria:**
- [ ] Auto-discovers all schemas in `schema/` directory
- [ ] Caches schemas in memory for fast access
- [ ] Validates schema format (JSON Schema Draft 7)
- [ ] Supports backward compatibility checking
- [ ] Provides clear error messages for missing/invalid schemas

**Estimated Effort**: 6 hours

---

### Task 1.3: Contract Enforcement Decorators
**File**: `core/contracts/decorators.py`

**Requirements:**
```python
@enforce_entry_contract(phase="phase2_request_building")
def create_execution_request(workstream_id: str) -> ExecutionRequest:
    """Entry contract automatically validated before execution"""

@enforce_exit_contract(phase="phase2_request_building")
def finalize_run(run_id: str) -> RunRecord:
    """Exit contract automatically validated after execution"""

@validate_schema(schema="ExecutionRequestV1")
def build_request(data: dict) -> ExecutionRequest:
    """Data automatically validated against schema"""
```

**Behavior:**
- Entry decorator: validates before function runs, raises `ContractViolationError` if invalid
- Exit decorator: validates after function completes, logs warnings for non-critical issues
- Schema decorator: validates data shape, coerces types where possible

**Acceptance Criteria:**
- [ ] Decorators integrate with PhaseContractValidator
- [ ] Clear error messages with remediation hints
- [ ] Performance overhead < 50ms per validation
- [ ] Supports dry-run mode (log violations, don't fail)
- [ ] Integrates with audit logger

**Estimated Effort**: 10 hours

---

## Priority 2: Phase-Specific Validators

### Task 2.1: Phase 0 (Bootstrap) Contract Enforcement
**Status**: ✅ Partially complete (`core/bootstrap/validator.py`)

**Enhancements Needed:**
- [ ] Add entry contract validation (check `.git/` exists)
- [ ] Add exit contract validation (verify `PROJECT_PROFILE.yaml` schema)
- [ ] Emit `BOOTSTRAP_COMPLETE` event to state DB
- [ ] Log validation results to `.ledger/framework.db`
- [ ] Add auto-fix for common issues (e.g., create missing directories)

**Estimated Effort**: 4 hours

---

### Task 2.2: Phase 1 (Planning) Contract Enforcement
**File**: `core/planning/contract_validator.py`

**Entry Requirements:**
- `PROJECT_PROFILE.yaml` exists (from phase0)
- `specifications/*.md` files exist
- `bootstrap_state` table exists
- `BOOTSTRAP_COMPLETE` flag is set

**Exit Artifacts:**
- `workstreams/*.json` files created
- `.state/spec_index.json` created
- `workstreams` table populated
- `PLANNING_COMPLETE` event emitted

**Implementation:**
```python
class PlanningContractValidator:
    def validate_entry(self) -> ValidationResult:
        # Check PROJECT_PROFILE.yaml exists and valid
        # Check specifications/*.md files exist
        # Check bootstrap_state in DB

    def validate_exit(self, workstreams: list) -> ValidationResult:
        # Validate each workstream against schema
        # Verify spec_index.json created
        # Check DB tables updated
```

**Acceptance Criteria:**
- [ ] Validates all entry requirements before planning starts
- [ ] Validates workstream JSON files against schema
- [ ] Verifies spec index completeness
- [ ] Logs planning metrics (# specs, # workstreams, # tasks)

**Estimated Effort**: 6 hours

---

### Task 2.3: Phase 2 (Request Building) Contract Enforcement
**File**: `core/engine/request_validator.py`

**Entry Requirements:**
- `workstreams/*.json` exist
- `schema/execution_request.v1.json` exists
- `workstreams` table exists
- `PLANNING_COMPLETE` flag set

**Exit Artifacts:**
- `.state/orchestration.db` updated
- `runs` table populated
- `RUN_CREATED` event emitted

**Implementation:**
```python
class RequestBuildingContractValidator:
    def validate_entry(self, workstream_id: str) -> ValidationResult:
        # Check workstream JSON exists and valid
        # Verify workstream in DB
        # Check PLANNING_COMPLETE flag

    def validate_execution_request(self, request: dict) -> ValidationResult:
        # Validate against execution_request.v1.json
        # Check all required fields present
        # Validate tool_profile_id references exist

    def validate_exit(self, run_id: str) -> ValidationResult:
        # Verify run record in DB
        # Check RUN_CREATED event logged
```

**Acceptance Criteria:**
- [ ] Validates workstream exists before building request
- [ ] Validates execution request against schema
- [ ] Verifies run record creation
- [ ] Supports idempotent reruns (detect duplicate run_id)

**Estimated Effort**: 6 hours

---

### Task 2.4: Phase 3 (Scheduling) Contract Enforcement
**File**: `core/engine/scheduling_validator.py`

**Entry Requirements:**
- `.state/orchestration.db` with run record
- `workstreams/*.json` exist
- `runs` table populated
- `RUN_CREATED` flag set

**Exit Artifacts:**
- `.state/task_queue.json` created
- `.state/dag_graph.json` created
- `tasks` table populated
- `DAG_BUILT`, `TASKS_QUEUED` events emitted

**Critical Validations:**
- DAG must be **acyclic** (no circular dependencies)
- All task dependencies must reference valid task IDs
- Task queue must respect DAG ordering

**Implementation:**
```python
class SchedulingContractValidator:
    def validate_entry(self, run_id: str) -> ValidationResult:
        # Check run record exists
        # Verify workstreams loaded

    def validate_dag(self, dag: nx.DiGraph) -> ValidationResult:
        # Check for cycles using core/state/dag_utils.py
        # Verify all dependencies exist
        # Check topological sort succeeds

    def validate_exit(self, task_queue: list) -> ValidationResult:
        # Verify task queue matches DAG
        # Check tasks table populated
        # Validate TASKS_QUEUED event
```

**Acceptance Criteria:**
- [ ] Detects cyclic dependencies and fails fast
- [ ] Validates task dependencies reference valid tasks
- [ ] Verifies task queue ordering matches DAG
- [ ] Logs DAG metrics (# tasks, # parallel, # sequential)

**Estimated Effort**: 8 hours

---

### Task 2.5: Phase 4 (Routing) Contract Enforcement
**File**: `core/engine/routing_validator.py`

**Entry Requirements:**
- `.state/task_queue.json` exists
- `config/tool_profiles/*.yaml` exist
- `tasks` table populated
- `TASKS_QUEUED` flag set

**Exit Artifacts:**
- `.state/routing_decisions.json` created
- `tasks` table updated (adapter_id assigned)
- `ROUTING_COMPLETE` event emitted

**Critical Validations:**
- All tasks assigned to valid adapters
- Adapter configurations valid
- Tool profiles exist for selected tools

**Acceptance Criteria:**
- [ ] Validates task queue exists
- [ ] Verifies tool profiles exist for all tasks
- [ ] Ensures adapter assignments are valid
- [ ] Detects missing/invalid tool configurations

**Estimated Effort**: 6 hours

---

### Task 2.6: Phase 5 (Execution) Contract Enforcement
**File**: `core/engine/execution_validator.py`

**Entry Requirements:**
- `.state/routing_decisions.json` exists
- `tasks` table with adapter_id
- `ROUTING_COMPLETE` flag set

**Exit Artifacts:**
- `.state/execution_results.json` created
- `tasks` table updated (status = COMPLETED/FAILED/TIMEOUT)
- `TASK_COMPLETED`/`TASK_FAILED` events emitted

**Critical Validations:**
- Adapter must be healthy and available
- Execution results must match schema
- Patch ledger must track all file changes

**Acceptance Criteria:**
- [ ] Validates adapter availability before execution
- [ ] Verifies execution results schema
- [ ] Ensures patch ledger integrity
- [ ] Validates acceptance test results

**Estimated Effort**: 8 hours

---

### Task 2.7: Phase 6 (Error Recovery) Contract Enforcement
**File**: `error/engine/recovery_validator.py`

**Entry Requirements:**
- `tasks` table with FAILED/TIMEOUT status
- `error/plugins/` available
- Execution logs exist

**Exit Artifacts:**
- `.state/error_analysis.json` created
- `error_log` table populated
- `ERROR_DETECTED`, `ERROR_CLASSIFIED` events emitted

**Critical Validations:**
- Error classification must be valid
- Fix patches must be valid and applicable
- Circuit breaker state must be respected

**Acceptance Criteria:**
- [ ] Validates error detection plugin availability
- [ ] Verifies error classification correctness
- [ ] Ensures fix patches are safe to apply
- [ ] Respects circuit breaker thresholds

**Estimated Effort**: 6 hours

---

### Task 2.8: Phase 7 (Monitoring) Contract Enforcement
**File**: `core/monitoring/archival_validator.py`

**Entry Requirements:**
- `.state/orchestration.db` exists
- `runs`, `tasks`, `workstreams` tables exist
- `RUN_CREATED` flag set

**Exit Artifacts:**
- `.archive/<run_id>/` created
- `reports/<run_id>_summary.json` created
- `runs` table updated (status = COMPLETED/FAILED/PARTIAL)
- `RUN_COMPLETED`, `RUN_ARCHIVED` events emitted

**Critical Validations:**
- All run artifacts archived
- Reports valid JSON
- Final run status correct

**Acceptance Criteria:**
- [ ] Validates archive completeness
- [ ] Verifies report generation
- [ ] Ensures run status finalization
- [ ] Validates artifact integrity

**Estimated Effort**: 6 hours

---

## Priority 3: CI/CD Integration

### Task 3.1: Pre-Commit Hook for Contract Validation
**File**: `.pre-commit-config.yaml` (update)

**Add Hook:**
```yaml
- id: phase-contract-validation
  name: Phase Contract Validation
  entry: python scripts/validate_phase_contracts.py
  language: python
  files: '(core/|phase[0-7]_.*/).*\.py$'
  pass_filenames: false
```

**Script**: `scripts/validate_phase_contracts.py`
```python
def validate_phase_contracts():
    """Validate all phase contracts in repository"""
    validator = PhaseContractValidator()
    results = []

    for phase in ["phase0", "phase1", ..., "phase7"]:
        result = validator.validate_phase_definition(phase)
        results.append(result)

    if any(r.has_errors() for r in results):
        print_errors(results)
        sys.exit(1)
```

**Acceptance Criteria:**
- [ ] Runs automatically on `git commit`
- [ ] Fast (< 5 seconds for full validation)
- [ ] Clear error messages
- [ ] Fails commit if contracts violated

**Estimated Effort**: 4 hours

---

### Task 3.2: CI Pipeline Contract Validation
**File**: `.github/workflows/contract-validation.yml`

**Workflow:**
```yaml
name: Contract Validation
on: [push, pull_request]
jobs:
  validate-contracts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Validate Phase Contracts
        run: python scripts/validate_all_contracts.py --strict
      - name: Validate Schema Versions
        run: python scripts/validate_schema_versions.py
      - name: Generate Contract Report
        run: python scripts/generate_contract_report.py
      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: contract-validation-report
          path: reports/contract_validation.json
```

**Acceptance Criteria:**
- [ ] Runs on every push/PR
- [ ] Blocks merge if contracts violated
- [ ] Generates detailed reports
- [ ] Notifies on violations

**Estimated Effort**: 6 hours

---

### Task 3.3: Runtime Contract Monitoring
**File**: `core/monitoring/contract_monitor.py`

**Requirements:**
```python
class ContractMonitor:
    """Monitors contract violations at runtime"""

    def record_violation(
        self,
        phase: str,
        contract_type: str,  # "entry" | "exit"
        violation: ContractViolation
    ):
        """Record contract violation in monitoring DB"""

    def get_violation_rate(self, phase: str, time_window: timedelta) -> float:
        """Calculate violation rate for phase"""

    def alert_on_threshold(self, threshold: float):
        """Alert if violation rate exceeds threshold"""
```

**Acceptance Criteria:**
- [ ] Tracks violations in real-time
- [ ] Calculates violation rates
- [ ] Sends alerts on thresholds
- [ ] Integrates with Phase 7 monitoring

**Estimated Effort**: 8 hours

---

## Priority 4: Documentation & Testing

### Task 4.1: Contract Enforcement Guide
**File**: `docs/DOC_operations/CONTRACT_ENFORCEMENT_GUIDE.md`

**Contents:**
- How contracts work
- How to add new contracts
- How to handle violations
- Debugging contract failures
- Best practices

**Estimated Effort**: 4 hours

---

### Task 4.2: Contract Validation Tests
**File**: `tests/contracts/test_contract_validation.py`

**Test Coverage:**
```python
def test_phase0_entry_contract():
    """Test Phase 0 entry contract validation"""

def test_phase0_exit_contract():
    """Test Phase 0 exit contract validation"""

# ... repeat for all phases

def test_schema_version_compatibility():
    """Test schema version compatibility checking"""

def test_contract_violation_reporting():
    """Test violation reporting and logging"""
```

**Acceptance Criteria:**
- [ ] 100% coverage of contract validators
- [ ] Tests for valid and invalid inputs
- [ ] Tests for edge cases (missing files, malformed data)
- [ ] Integration tests across phases

**Estimated Effort**: 12 hours

---

### Task 4.3: Contract Examples & Templates
**File**: `docs/DOC_examples/contract_examples.md`

**Examples:**
- Valid phase entry/exit contracts
- Invalid contracts with error messages
- Schema validation examples
- Migration examples (v1 → v2)

**Estimated Effort**: 3 hours

---

## Priority 5: Tooling & Utilities

### Task 5.1: Contract CLI Tool
**File**: `scripts/contract_cli.py`

**Commands:**
```bash
# Validate all contracts
python scripts/contract_cli.py validate --all

# Validate specific phase
python scripts/contract_cli.py validate --phase phase2_request_building

# Generate contract report
python scripts/contract_cli.py report --output contracts_report.json

# Check schema compatibility
python scripts/contract_cli.py schema-check --old v1 --new v2

# Auto-fix common issues
python scripts/contract_cli.py fix --phase phase0 --dry-run
```

**Acceptance Criteria:**
- [ ] User-friendly CLI interface
- [ ] JSON/YAML/Markdown output formats
- [ ] Supports batch operations
- [ ] Integrates with CI/CD

**Estimated Effort**: 8 hours

---

### Task 5.2: Contract Visualization Dashboard
**File**: `gui/contract_dashboard.py`

**Features:**
- Visual representation of phase flow
- Contract status indicators (✅ valid, ❌ violated)
- Violation history charts
- Real-time monitoring

**Acceptance Criteria:**
- [ ] Displays all phase contracts
- [ ] Shows contract violations in real-time
- [ ] Provides drill-down details
- [ ] Exports reports

**Estimated Effort**: 12 hours

---

## Summary: Estimated Total Effort

| Priority | Tasks | Estimated Hours |
|----------|-------|-----------------|
| 1. Core Infrastructure | 3 tasks | 24 hours |
| 2. Phase Validators | 8 tasks | 50 hours |
| 3. CI/CD Integration | 3 tasks | 18 hours |
| 4. Documentation & Testing | 3 tasks | 19 hours |
| 5. Tooling & Utilities | 2 tasks | 20 hours |
| **TOTAL** | **19 tasks** | **131 hours** |

**Estimated Timeline**: 3-4 weeks (1-2 developers)

---

## Success Criteria

Contract enforcement is **complete** when:

1. ✅ **Every phase has automated validators** (entry + exit)
2. ✅ **CI/CD fails on contract violations** (blocking merges)
3. ✅ **Runtime monitoring detects violations** (alerts sent)
4. ✅ **100% test coverage** for contract validators
5. ✅ **Documentation complete** (guides, examples, API reference)
6. ✅ **CLI tools available** for manual validation
7. ✅ **Dashboard shows contract health** (real-time status)

---

## Next Steps

**Immediate (Week 1):**
1. Task 1.1: Create Contract Validator Framework
2. Task 1.2: Schema Version Registry
3. Task 2.1: Enhance Phase 0 Bootstrap Validator

**Short-term (Week 2-3):**
4. Task 2.2-2.8: Implement all phase validators
5. Task 3.1: Pre-commit hook integration

**Medium-term (Week 4):**
6. Task 3.2-3.3: CI/CD and runtime monitoring
7. Task 4.1-4.3: Documentation and testing

**Long-term (Future):**
8. Task 5.1-5.2: Advanced tooling and dashboards

---

## References

- **Phase I/O Contracts**: See `phase*/README.md` files
- **Data Contracts**: See `docs/UET_SUBMODULE_IO_CONTRACTS.md`
- **Schemas**: See `schema/*.json` files
- **Existing Validators**: See `core/bootstrap/validator.py`
- **Validation Scripts**: See `scripts/validate_*.py` files
