#!/bin/bash
# DOC_LINK: DOC-SCRIPT-RUN-PRODUCTION-VALIDATION-285
set -e

echo "=== Production-Ready Validation Suite ==="
echo ""

# Track results
PASS_COUNT=0
FAIL_COUNT=0
TOTAL_TESTS=0

run_test() {
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -n "[$TOTAL_TESTS] $1... "
    if eval "$2" > /dev/null 2>&1; then
        echo "✅ PASS"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo "❌ FAIL"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        echo "  Command: $2"
    fi
}

echo "## Quick Validation"
run_test "Compilation check" "python -m compileall modules/ tests/ -q"
run_test "Core imports" "python -c 'from modules.core_engine import Orchestrator'"
run_test "State imports" "python -c 'from modules.core_state import get_db'"
run_test "Error imports" "python -c 'from modules.error_engine import ErrorEngine'"
run_test "Shared imports" "python -c 'from modules.error_shared import PluginManifest'"
run_test "Test suite" "python -m pytest tests/ -q --tb=no"

echo ""
echo "## Module Validation"
run_test "All core modules import" "python -c 'import importlib; all([importlib.import_module(f\"modules.{m}\") for m in [\"core_engine\", \"core_state\", \"error_engine\", \"error_shared\"]])'"
run_test "No src imports in modules" "! grep -r 'from src\\.' modules/"
run_test "No legacy imports" "! grep -r 'from legacy\\.' modules/"
run_test "YAML syntax valid" "python -c 'import yaml; yaml.safe_load(open(\"MODULES_INVENTORY.yaml\"))'"

echo ""
echo "## Integration Tests"

# Pattern Automation Integration
run_test "Pattern automation imports" "python -c 'from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.patterns.automation.integration.orchestrator_hooks import get_hooks'"
run_test "Database exists" "test -f UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/metrics/pattern_automation.db"

echo "  Running pattern automation end-to-end test..."
python << 'PYTEST'
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
    count = conn.execute('SELECT COUNT(*) FROM execution_logs WHERE operation_kind = ?', ('run_execution',)).fetchone()[0]
    conn.close()
    if count == 0:
        raise RuntimeError(f"No execution logs captured for test run")
    print(f"✅ Pattern automation working ({count} logs)")
else:
    raise RuntimeError("Pattern automation database not found")
PYTEST
PASS_COUNT=$((PASS_COUNT + 1))
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Orchestrator Lifecycle
echo "  Running orchestrator lifecycle test..."
python << 'PYTEST2'
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

print("✅ Orchestrator lifecycle OK")
PYTEST2
PASS_COUNT=$((PASS_COUNT + 1))
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Error Pipeline Integration
echo "  Running error pipeline integration test..."
python << 'PYTEST3'
from modules.error_engine import PluginManager
from modules.error_shared import PluginManifest

# Test plugin loading
pm = PluginManager()
plugins = pm.discover_plugins('modules/error-plugin-python-ruff')

assert len(plugins) > 0, "No plugins discovered"
print(f"✅ Error pipeline OK ({len(plugins)} plugins)")
PYTEST3
PASS_COUNT=$((PASS_COUNT + 1))
TOTAL_TESTS=$((TOTAL_TESTS + 1))

echo ""
echo "## Performance Tests"

# Import timing
echo "  Measuring import performance..."
IMPORT_TIME=$(python -c "
import time
start = time.time()
from modules.core_engine import Orchestrator
from modules.core_state import Database
from modules.error_engine import ErrorEngine
from modules.error_shared import PluginManifest
elapsed = time.time() - start
print(f'{elapsed:.3f}')
")
echo "  Import time: ${IMPORT_TIME}s"
if (( $(echo "$IMPORT_TIME < 1.0" | bc -l) )); then
    echo "  ✅ Import performance OK (<1s)"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo "  ⚠️  Import slow (>1s)"
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Hook overhead
echo "  Measuring hook overhead..."
HOOK_TIME=$(python -c "
import time
from modules.core_engine import Orchestrator

orch = Orchestrator()
start = time.time()
for i in range(10):
    run_id = orch.create_run(f'perf_test_{i}', 'phase1')
    orch.start_run(run_id)
    orch.complete_run(run_id, 'succeeded')
elapsed = time.time() - start
print(f'{elapsed:.3f}')
")
echo "  10 runs with hooks: ${HOOK_TIME}s ($(echo "$HOOK_TIME / 10" | bc -l | xargs printf "%.3f")s per run)"
PASS_COUNT=$((PASS_COUNT + 1))
TOTAL_TESTS=$((TOTAL_TESTS + 1))

echo ""
echo "=== Validation Summary ==="
echo "Total Tests: $TOTAL_TESTS"
echo "Passed: $PASS_COUNT"
echo "Failed: $FAIL_COUNT"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo "✅ ALL VALIDATION PASSED - PRODUCTION READY"
    exit 0
else
    echo "❌ VALIDATION FAILED - $FAIL_COUNT test(s) failed"
    exit 1
fi
