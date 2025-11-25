# Orchestration Specification Implementation Guide

## Overview

This guide provides step-by-step instructions for implementing the orchestration specification enhancements documented in `specifications/content/orchestration/spec.md`.

## What Was Implemented

This implementation includes:

1. **Enhanced Orchestration Specification** (`specifications/content/orchestration/spec.md`)
   - 15 major sections with 60+ stable requirement IDs
   - RFC 2119 compliant (MUST/SHOULD/MAY)
   - AI-first design for transparency without execution

2. **Supporting Documentation** (18 new files)
   - Execution model documentation
   - State machine definitions
   - Failure mode catalog
   - Schema migration guides
   - Operational procedures

3. **Validation Tools** (6 PowerShell scripts)
   - Individual validators for each requirement section
   - Master compliance validator
   - CI/CD ready with exit codes

## Directory Structure

```
complete-ai-development-pipeline-canonical-phase-plan/
├── specifications/content/orchestration/
│   └── spec.md                          # ✅ Enhanced orchestration spec
├── capabilities/
│   ├── registry.psd1                    # ✅ Capability catalog
│   └── resources.psd1                   # ✅ Resource registry
├── docs/
│   ├── execution_model/
│   │   ├── OVERVIEW.md                  # ✅ Architecture overview
│   │   ├── STATE_MACHINE.md             # ✅ State transitions
│   │   └── RECOVERY.md                  # ✅ Recovery procedures
│   ├── state_machines/
│   │   ├── task_lifecycle.yaml          # ✅ Task state machine
│   │   ├── workstream_lifecycle.yaml    # ✅ Workstream state machine
│   │   └── worker_lifecycle.yaml        # ✅ Worker state machine
│   ├── failure_modes/
│   │   └── CATALOG.md                   # ✅ Failure mode catalog
│   ├── schema_migrations/
│   │   └── task_v1_to_v2.md            # ✅ Migration guide
│   └── operations/
│       └── AUDIT_RETENTION.md           # ✅ Audit policy
└── scripts/validate/
    ├── README.md                        # ✅ Validation guide
    ├── validate_state_obs.ps1           # ✅ State validator
    ├── validate_task_defs.ps1           # ✅ Task validator
    ├── validate_dag_structure.ps1       # ✅ DAG validator
    ├── validate_failure_modes.ps1       # ✅ Failure mode validator
    └── validate_compliance.ps1          # ✅ Master validator
```

## Implementation Phases

### Phase 1: Critical Path (Weeks 1-2)

Implement core state observability and task definitions:

**STATE-OBS-001 through 006**:
1. Create `.state/` directory structure
2. Implement state snapshot writer (`.state/current.json`)
3. Implement transition logger (`.state/transitions.jsonl`)
4. Add atomic write mechanism (write to .tmp, rename)
5. Implement event schema with severity levels
6. Add optional index generation

**TASK-DEF-001, 002**:
1. Create `tasks/` directory structure
2. Implement task definition schema v2.0.0
3. Add context_requirements for AI tasks
4. Add validation_rules (pre/post execution)

**DAG-VIEW-001, 002, 003**:
1. Implement DAG builder from task dependencies
2. Add topological sort for execution order
3. Generate execution plans with stages
4. Calculate critical path and estimates

**SM-DEF-001**:
1. Implement task lifecycle state machine
2. Add state transition validation
3. Emit events on state changes

**Validation**: Run `validate_state_obs.ps1` and `validate_task_defs.ps1`

### Phase 2: Core Functionality (Weeks 3-4)

Implement execution model and integration points:

**EXEC-DOC-001 through 006**:
- Documentation already created ✅
- Review and refine based on implementation

**AIDER-INT-001, 002, 003**:
1. Create AiderAdapter worker class
2. Implement context boundary enforcement
3. Add structured output contract
4. Validate context requirements before execution

**ERR-FM-001, 002, 003**:
1. Document each failure mode (see CATALOG.md)
2. Implement automatic recovery for common failures
3. Add decision tree logic

**CAP-REG-001, 002**:
- Capability registry already created ✅
- Implement capability matching in scheduler

**Validation**: Run `validate_dag_structure.ps1` and `validate_failure_modes.ps1`

### Phase 3: Production Hardening (Weeks 5-6)

Add resource management and observability:

**CONC-REG-001, 002**:
1. Implement resource registry loading
2. Add resource tracking to execution plan
3. Implement resource allocation/release
4. Add deadlock detection

**AUDIT-001, 002**:
1. Implement audit log retention policy
2. Add log rotation scripts
3. Implement archive/restore procedures
4. Add compliance report generation

**OBS-001, 002**:
1. Implement metrics collection
2. Export to `.state/metrics.json`
3. Add Prometheus exporter
4. Create monitoring dashboards

**SCHEMA-VER-001, 002**:
1. Add schema version to all JSON files
2. Implement automatic migration for v1 to v2
3. Create migration scripts
4. Test backward compatibility

**Validation**: Run `validate_compliance.ps1` for full compliance check

### Phase 4: Polish (Week 7)

Final touches and documentation:

**MOD-IDX-001**:
1. Add module docstrings with stability info
2. Document public APIs
3. Add integration point documentation

**SM-DEF-002, 003**:
1. Implement workstream lifecycle state machine
2. Implement worker lifecycle state machine
3. Add state derivation logic

**COMPLIANCE-001**:
- Validation scripts already created ✅
- Integrate into CI/CD pipeline

## Quick Start

### 1. Review the Specification

Read the enhanced orchestration specification:
```bash
cat specifications/content/orchestration/spec.md
```

Key sections to understand:
- Section 2: State Observability
- Section 4: Task Definitions
- Section 5: DAG and Execution Plans
- Section 9: State Machine Definitions

### 2. Set Up Validation

Test the validation scripts:
```bash
# Install PowerShell if needed
sudo apt-get install -y powershell  # Ubuntu/Debian
brew install powershell              # macOS

# Run validation (will fail initially - expected)
pwsh -File scripts/validate/validate_compliance.ps1
```

### 3. Implement Core State Management

Create initial state directory structure:
```bash
mkdir -p .state/{backups,archive,logs}
touch .state/current.json
touch .state/transitions.jsonl
```

Initialize current.json:
```json
{
  "schema_version": "2.0.0",
  "timestamp": "2024-01-15T10:00:00.000Z",
  "workstreams": [],
  "tasks": [],
  "workers": []
}
```

### 4. Implement Task Definitions

Create tasks directory:
```bash
mkdir -p tasks
```

Create example task (tasks/ws-001/task-001.json):
```json
{
  "schema_version": "2.0.0",
  "task_id": "task-001",
  "workstream_id": "ws-001",
  "name": "Example task",
  "description": "Example task for testing",
  "type": "aider",
  "status": "pending",
  "dependencies": [],
  "blocks": [],
  "worker_requirements": {
    "capabilities": ["aider"],
    "min_version": "1.0.0"
  },
  "execution": {
    "command": "aider --yes --message 'Test'",
    "timeout_seconds": 600,
    "max_retries": 3
  },
  "context_requirements": {
    "max_context_tokens": 8000,
    "required_files": [],
    "exclude_patterns": ["**/__pycache__/**"]
  },
  "validation_rules": {
    "pre_execution": ["git_clean"],
    "post_execution": ["no_lint_errors"]
  },
  "state": {
    "created_at": "2024-01-15T10:00:00.000Z",
    "retry_count": 0
  }
}
```

### 5. Run Validation Again

After implementing core components:
```bash
pwsh -File scripts/validate/validate_compliance.ps1 -VerboseOutput
```

Should see more passing checks.

## Testing Strategy

### Unit Tests

Test individual components:
```python
# tests/test_state_manager.py
def test_atomic_state_write():
    """Test STATE-OBS-003: Atomic state updates"""
    state_manager.update_state(new_state)
    assert not os.path.exists('.state/current.json.tmp')
    assert os.path.exists('.state/current.json')

# tests/test_task_schema.py
def test_task_definition_v2():
    """Test TASK-DEF-002: Task schema v2.0.0"""
    task = load_task('tasks/ws-001/task-001.json')
    assert task['schema_version'] == '2.0.0'
    assert 'context_requirements' in task
```

### Integration Tests

Test end-to-end workflows:
```python
# tests/integration/test_workstream_execution.py
def test_workstream_lifecycle():
    """Test SM-DEF-002: Workstream state machine"""
    ws = create_workstream('ws-test-001')
    assert ws.state == 'planned'
    
    ws.create_tasks()
    assert ws.state == 'ready'
    
    ws.start_execution()
    assert ws.state == 'executing'
```

### Validation Tests

Ensure validators work correctly:
```bash
# Test validators detect violations
pytest tests/validation/test_validators.py
```

## CI/CD Integration

### GitHub Actions

Add to `.github/workflows/compliance.yml`:
```yaml
name: Orchestration Compliance

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install PowerShell
        run: |
          sudo apt-get update
          sudo apt-get install -y powershell
      
      - name: Validate Compliance
        run: |
          pwsh -File scripts/validate/validate_compliance.ps1
```

## Common Issues

### Issue: Validation fails on fresh repository

**Cause**: No state files or tasks exist yet.

**Solution**: This is expected. Implement core components first, then validation will pass.

### Issue: PowerShell script won't run

**Cause**: Execution policy or permissions.

**Solution**:
```bash
chmod +x scripts/validate/*.ps1
pwsh -ExecutionPolicy Bypass -File scripts/validate/validate_compliance.ps1
```

### Issue: Schema version mismatch

**Cause**: Old task definitions without schema_version field.

**Solution**: Add migration script or manually update tasks:
```bash
python scripts/migrate_task_schema.py --from 1.0.0 --to 2.0.0
```

## Next Steps

1. **Review Specification**: Read `specifications/content/orchestration/spec.md` thoroughly
2. **Start Phase 1**: Implement state observability (STATE-OBS-*)
3. **Validate Early**: Run validators after each component
4. **Iterate**: Refine based on validation feedback
5. **Document**: Update docs as implementation progresses

## References

- [Orchestration Specification](../../specifications/content/orchestration/spec.md)
- [Validation Scripts README](../../scripts/validate/README.md)
- [State Machine Definitions](../../docs/state_machines/)
- [Failure Mode Catalog](../../docs/failure_modes/CATALOG.md)
- [Execution Model Overview](../../docs/execution_model/OVERVIEW.md)

## Support

For questions or issues:
1. Review specification requirement IDs (e.g., STATE-OBS-001)
2. Check validation script output for specific violations
3. Consult supporting documentation in `docs/`
4. Review example task definitions and state files in this guide
