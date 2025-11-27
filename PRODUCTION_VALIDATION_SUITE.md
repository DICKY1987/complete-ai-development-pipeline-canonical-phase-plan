# Production-Ready Validation Suite

**Purpose**: Comprehensive validation framework for module migration completion  
**Coverage**: Quick checks, module validation, integration tests, performance benchmarks  
**Time**: 5-60 minutes depending on depth

---

## Quick Validation (5 min)

Fast sanity checks for immediate feedback:

```bash
# Compilation check
python -m compileall modules/ tests/ -q

# Basic import tests
python -c "from modules.core_engine import Orchestrator"
python -c "from modules.core_state import get_db"
python -c "from modules.error_engine import ErrorEngine"
python -c "from modules.error_shared import PluginManifest"

# Test suite pass/fail
python -m pytest tests/ -q --tb=no
```

**Success Criteria**:
- Exit code 0 for compilation
- All imports successful
- Test suite passes

---

## Standard Validation (15 min)

Thorough checks for module integrity:

### Module Import Verification
```bash
# Test all 31 modules import successfully
python -c "
import importlib
modules = ['core_engine', 'core_state', 'error_engine', 'error_shared', 
           'pm_workstream', 'pm_task', 'pm_step']
for m in modules:
    try:
        importlib.import_module(f'modules.{m}')
        print(f'✅ {m}')
    except Exception as e:
        print(f'❌ {m}: {e}')
"
```

### Deprecated Path Scanning
```bash
# Verify no deprecated imports in production code
! grep -r "from src\." modules/
! grep -r "from legacy\." modules/
! grep -r "from MOD_" modules/

# Expected: No matches (exit code 1 means no matches = success)
```

### YAML Syntax Validation
```bash
# Verify module inventory is valid
python -c "
import yaml
with open('MODULES_INVENTORY.yaml') as f:
    data = yaml.safe_load(f)
    print(f'✅ Valid YAML: {len(data)} modules')
"
```

### Module Inventory Accuracy
```bash
# Count actual modules vs inventory
python -c "
import yaml
from pathlib import Path

with open('MODULES_INVENTORY.yaml') as f:
    inventory = yaml.safe_load(f)

modules_dir = Path('modules')
actual_modules = [d.name for d in modules_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]

print(f'Inventory: {len(inventory)} modules')
print(f'Actual: {len(actual_modules)} directories')
print(f'Match: {len(inventory) == len(actual_modules)}')
"
```

**Success Criteria**:
- All modules import without errors
- Zero deprecated path matches
- YAML valid and inventory matches filesystem

---

## Integration Tests (30 min)

End-to-end validation of critical workflows:

### Pattern Automation End-to-End

**Objective**: Verify execution data capture and pattern detection

```python
# Test: Pattern automation integration
from modules.core_engine import Orchestrator
import sqlite3
from pathlib import Path

# Create orchestrator with hooks
orch = Orchestrator()

# Verify hooks initialized
if not hasattr(orch, 'pattern_hooks') or orch.pattern_hooks is None:
    raise RuntimeError("Pattern hooks not initialized")

# Create test run
run_id = orch.create_run('test_project', 'test_phase')
orch.start_run(run_id)
orch.complete_run(run_id, 'succeeded')

# Verify database capture
db_path = Path('UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/metrics/pattern_automation.db')
if db_path.exists():
    conn = sqlite3.connect(db_path)
    count = conn.execute(
        'SELECT COUNT(*) FROM execution_logs WHERE operation_kind = ?',
        ('run_execution',)
    ).fetchone()[0]
    conn.close()
    if count == 0:
        raise RuntimeError("No execution logs captured")
    print(f'✅ Pattern automation working ({count} logs)')
else:
    raise RuntimeError("Pattern automation database not found")
```

**Expected Output**: `✅ Pattern automation working (N logs)` where N > 0

### Orchestrator Lifecycle

**Objective**: Verify run creation, execution, and completion

```python
# Test: Orchestrator lifecycle
from modules.core_engine import Orchestrator
from modules.core_state import get_db

orch = Orchestrator()
db = get_db()

# Full lifecycle test
run_id = orch.create_run('lifecycle_test', 'phase1')
orch.start_run(run_id)

# Verify run created
run = db.get_run(run_id)
assert run is not None, "Run not created"
assert run['status'] == 'running', f"Expected running, got {run['status']}"

orch.complete_run(run_id, 'succeeded')
run = db.get_run(run_id)
assert run['status'] == 'succeeded', f"Expected succeeded, got {run['status']}"

print('✅ Orchestrator lifecycle OK')
```

**Expected Output**: `✅ Orchestrator lifecycle OK`

### Error Pipeline Integration

**Objective**: Verify plugin loading and error detection

```python
# Test: Error pipeline integration
from modules.error_engine import PluginManager
from modules.error_shared import PluginManifest

# Test plugin loading
pm = PluginManager()
plugins = pm.discover_plugins('modules/error-plugin-python-ruff')

assert len(plugins) > 0, "No plugins discovered"
print(f'✅ Error pipeline OK ({len(plugins)} plugins)')
```

**Expected Output**: `✅ Error pipeline OK (N plugins)` where N > 0

**Success Criteria**:
- Pattern automation captures execution data
- Orchestrator manages full run lifecycle
- Error plugins load successfully

---

## Performance Tests (15 min)

Benchmark critical operations:

### Import Time Benchmarks

**Objective**: Ensure module imports are fast (&lt;1s)

```python
# Test: Import performance
import time

start = time.time()
from modules.core_engine import Orchestrator
from modules.core_state import Database
from modules.error_engine import ErrorEngine
from modules.error_shared import PluginManifest
elapsed = time.time() - start

print(f'Import time: {elapsed:.3f}s')
if elapsed < 1.0:
    print('✅ Import performance OK (<1s)')
else:
    print('⚠️  Import slow (>1s)')
```

**Expected Output**: `✅ Import performance OK (<1s)`

### Module Load Performance

**Objective**: Measure dynamic import overhead

```python
# Test: Module load performance
import time
import importlib

modules = ['core_engine', 'core_state', 'error_engine', 'error_shared']
start = time.time()
for m in modules:
    importlib.import_module(f'modules.{m}')
elapsed = time.time() - start

print(f'Module load time ({len(modules)} modules): {elapsed:.3f}s')
print(f'Average per module: {elapsed/len(modules):.3f}s')
```

**Expected Output**: Average &lt; 0.5s per module

### Hook Overhead Measurement

**Objective**: Verify pattern hooks don't slow orchestrator

```python
# Test: Hook overhead
import time
from modules.core_engine import Orchestrator

orch = Orchestrator()
start = time.time()
for i in range(10):
    run_id = orch.create_run(f'perf_test_{i}', 'phase1')
    orch.start_run(run_id)
    orch.complete_run(run_id, 'succeeded')
elapsed = time.time() - start

print(f'10 runs with hooks: {elapsed:.3f}s ({elapsed/10:.3f}s per run)')
```

**Expected Output**: &lt; 0.5s per run average

**Success Criteria**:
- Imports &lt; 1s total
- Module load &lt; 0.5s per module
- Hook overhead &lt; 0.5s per run

---

## Validation Commands by Category

### Compilation & Syntax
```bash
# Check all Python files compile
python -m compileall modules/ tests/ -q

# Verify YAML syntax
python -c "import yaml; yaml.safe_load(open('MODULES_INVENTORY.yaml'))"
```

### Import Validation
```bash
# Test critical imports
python -c "from modules.core_engine import Orchestrator"
python -c "from modules.core_state import Database, get_db"
python -c "from modules.error_engine import ErrorEngine"
python -c "from modules.error_shared import PluginManifest, security"

# Verify no deprecated imports
! grep -r "from src\." modules/
! grep -r "from legacy\." modules/
```

### Test Execution
```bash
# Run full test suite
python -m pytest tests/ -v

# Run specific categories
python -m pytest tests/engine/ -v
python -m pytest tests/error/ -v
python -m pytest tests/pm/ -v

# Quick smoke test
python -m pytest tests/ -q --tb=no
```

### Integration Verification
```bash
# Run integration tests
python scripts/test_pattern_automation.py
python scripts/test_orchestrator_lifecycle.py
python scripts/test_error_pipeline.py
```

### Performance Benchmarks
```bash
# Run performance suite
python scripts/benchmark_imports.py
python scripts/benchmark_hooks.py
```

---

## Automated Validation Script

For convenience, run all checks via:

```bash
# Windows
.\scripts\run_production_validation.bat

# Unix/Linux
bash scripts/run_production_validation.sh
```

See `scripts/run_production_validation.sh` for full implementation (100 lines with all checks).

---

## Troubleshooting

### Import Errors

**Symptom**: `ModuleNotFoundError: No module named 'modules.X'`

**Solution**:
1. Verify module exists: `ls modules/X/`
2. Check `__init__.py` exists: `cat modules/X/__init__.py`
3. Verify PYTHONPATH includes repo root
4. Check MODULES_INVENTORY.yaml for entry

### Test Failures

**Symptom**: Tests pass &lt; 100%

**Solution**:
1. Run failed test in isolation: `pytest tests/path/test_file.py::test_name -v`
2. Check for deprecated imports in test: `grep "from src\." tests/path/test_file.py`
3. Verify test database is clean: `rm -f tests/test_*.db`

### Pattern Automation Not Working

**Symptom**: Hooks not capturing data

**Solution**:
1. Check orchestrator initialization: `python -c "from modules.core_engine import Orchestrator; o = Orchestrator(); print(hasattr(o, 'pattern_hooks'))"`
2. Verify database exists: `ls UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/metrics/pattern_automation.db`
3. Check for import errors in hook module

### Performance Issues

**Symptom**: Imports or hooks are slow

**Solution**:
1. Profile imports: `python -X importtime -c "from modules.core_engine import Orchestrator" 2>&1 | grep "import time"`
2. Check for circular dependencies
3. Verify no infinite loops in `__init__.py` dynamic imports

---

## Success Criteria Summary

**Quick Validation**: All imports succeed, tests pass  
**Standard Validation**: No deprecated imports, YAML valid, inventory accurate  
**Integration Tests**: Pattern automation, orchestrator, error pipeline all functional  
**Performance Tests**: Imports &lt; 1s, hooks &lt; 0.5s per run

**Overall**: 100% test pass rate, zero errors, production-ready state

---

## Related Documentation

- `MIGRATION_COMPLETION_REPORT.md` - Full migration metrics
- `CLAUDE.md` - Import patterns and coding standards
- `MODULES_INVENTORY.yaml` - Module registry
- `5_Phase Completion Plan Module Migration & Pattern Automation Integration.md` - Execution plan
