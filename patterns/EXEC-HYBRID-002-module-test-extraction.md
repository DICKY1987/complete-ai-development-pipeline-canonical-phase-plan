# Execution Pattern: EXEC-HYBRID-002 - Module Test Extraction

**Pattern ID**: EXEC-HYBRID-002
**Date**: 2025-12-03
**Purpose**: Extract module-specific tests from global tests/ directory
**Scope**: 196 test files → 31 module test directories
**Estimated Time**: 1 hour
**Speedup**: 4x faster than manual (4h → 1h)

---

## Pattern Overview

**Problem**: All tests live in global `tests/` directory. Hard to know which tests belong to which module.

**Solution**: Extract module-specific tests into `module/tests/`, keep only integration tests at root.

**Key Principle**: Module owns its tests - if you modify a module, run its tests.

---

## Pre-Execution Decisions

**Test Organization**: Module-specific in module/tests/, integration in tests/integration/
**Naming**: Keep original test file names
**Verification**: pytest must still discover all tests
**Success**: Each module has its tests, pytest finds them all

**NOT Deciding**:
- Test refactoring
- Coverage improvements
- Test performance
- Mock strategy

---

## Execution Pattern

### Discovery Phase

Analyze current test structure:

```powershell
# Count tests by category
Get-ChildItem tests/ -Recurse -Filter "test_*.py" | Group-Object Directory | Sort-Object Count -Descending
```

Expected categories:
- tests/bootstrap/ → phase0_bootstrap/modules/bootstrap_orchestrator/tests/
- tests/engine/ → stays in tests/ (integration)
- tests/adapters/ → phase4_routing/modules/tool_adapters/tests/
- tests/aim/ → phase4_routing/modules/aim_tools/tests/
- tests/error/engine/ → phase6_error_recovery/modules/error_engine/tests/
- tests/error/plugins/* → phase6_error_recovery/modules/plugins/*/tests/
- tests/integration/ → stays at root

### Template Phase

Test file mapping template:

```yaml
test_mappings:
  bootstrap:
    source: tests/bootstrap/
    dest: phase0_bootstrap/modules/bootstrap_orchestrator/tests/

  adapters:
    source: tests/adapters/
    dest: phase4_routing/modules/tool_adapters/tests/

  aim:
    source: tests/aim/
    dest: phase4_routing/modules/aim_tools/tests/

  error_engine:
    source: tests/error/engine/
    dest: phase6_error_recovery/modules/error_engine/tests/

  plugins:
    # Each plugin separately
    python_ruff:
      source: tests/error/plugins/python_ruff/
      dest: phase6_error_recovery/modules/plugins/python_ruff/tests/
```

### Batch Execution

**Batch 1: Phase 0 Tests**

```powershell
# Copy bootstrap tests
$source = "tests/bootstrap"
$dest = "phase0_bootstrap/modules/bootstrap_orchestrator/tests"

if (Test-Path $source) {
    Copy-Item -Path "$source/*" -Destination $dest -Recurse -Force
    Write-Host "✅ Copied bootstrap tests" -ForegroundColor Green
}

# Verify
$testCount = (Get-ChildItem $dest -Filter "test_*.py" -Recurse).Count
Write-Host "Bootstrap tests: $testCount"
```

**Batch 2: Phase 4 Tests**

```powershell
# AIM tests
$source = "tests/aim"
$dest = "phase4_routing/modules/aim_tools/tests"
if (Test-Path $source) {
    Copy-Item -Path "$source/*" -Destination $dest -Recurse -Force
}

# Adapter tests
$source = "tests/adapters"
$dest = "phase4_routing/modules/tool_adapters/tests"
if (Test-Path $source) {
    Copy-Item -Path "$source/*" -Destination $dest -Recurse -Force
}

# Verify
$aimTests = (Get-ChildItem "phase4_routing/modules/aim_tools/tests" -Filter "test_*.py" -Recurse).Count
$adapterTests = (Get-ChildItem "phase4_routing/modules/tool_adapters/tests" -Filter "test_*.py" -Recurse).Count
Write-Host "AIM tests: $aimTests, Adapter tests: $adapterTests"
```

**Batch 3: Phase 6 Tests (Error Engine + 21 Plugins)**

```powershell
# Error engine tests
$source = "tests/error/engine"
$dest = "phase6_error_recovery/modules/error_engine/tests"
if (Test-Path $source) {
    Copy-Item -Path "$source/*" -Destination $dest -Recurse -Force
}

# Plugin tests (21 plugins)
$plugins = Get-ChildItem "tests/error/plugins" -Directory -ErrorAction SilentlyContinue
foreach ($plugin in $plugins) {
    $dest = "phase6_error_recovery/modules/plugins/$($plugin.Name)/tests"
    New-Item -ItemType Directory -Path $dest -Force | Out-Null
    Copy-Item -Path "$($plugin.FullName)/*" -Destination $dest -Recurse -Force
}

# Verify
$engineTests = (Get-ChildItem "phase6_error_recovery/modules/error_engine/tests" -Filter "test_*.py" -Recurse).Count
$pluginTests = (Get-ChildItem "phase6_error_recovery/modules/plugins/*/tests" -Filter "test_*.py" -Recurse).Count
Write-Host "Error engine tests: $engineTests, Plugin tests: $pluginTests"
```

### Verification Phase

**Test Discovery Check**:

```powershell
# pytest should discover all tests
pytest --collect-only > test_collection.txt

# Count discovered tests
$collected = (Select-String "test session starts" test_collection.txt -Context 0,50 | Select-String "collected" | Select-String -Pattern "(\d+) items").Matches.Groups[1].Value

Write-Host "Collected tests: $collected (Expected: 196 or similar)"
```

**Module Test Isolation**:

```powershell
# Each module's tests should be runnable independently
$modules = Get-ChildItem "phase*/modules/*/tests" -Directory -Recurse

foreach ($module in $modules) {
    $moduleName = $module.Parent.Name
    $testCount = (Get-ChildItem $module.FullName -Filter "test_*.py" -Recurse).Count

    if ($testCount -gt 0) {
        Write-Host "Testing $moduleName ($testCount tests)..."
        pytest $module.FullName -q
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Tests failed for $moduleName" -ForegroundColor Red
        }
    }
}
```

---

## Validation Gates

### Gate 1: All Module Tests Extracted

```powershell
# Modules with source code should have tests
$modulesWithCode = Get-ChildItem "phase*/modules/*/src" -Directory -Recurse | Where-Object {
    (Get-ChildItem $_.FullName -Recurse -File).Count -gt 0
}

foreach ($module in $modulesWithCode) {
    $testsPath = Join-Path $module.Parent.FullName "tests"
    if (-not (Test-Path $testsPath)) {
        Write-Host "⚠️ No tests dir: $($module.Parent.Name)" -ForegroundColor Yellow
    }
}
```

### Gate 2: pytest.ini Updated

```powershell
# Update pytest.ini to discover tests in modules
$pytestConfig = @'
[pytest]
testpaths =
    phase0_bootstrap/modules
    phase1_planning/modules
    phase4_routing/modules
    phase6_error_recovery/modules
    phase7_monitoring/modules
    tests/integration

python_files = test_*.py
python_classes = Test*
python_functions = test_*
'@

$pytestConfig | Out-File pytest.ini -Encoding UTF8
```

### Gate 3: Integration Tests Remain

```powershell
# Integration tests stay at root
Test-Path "tests/integration" | Should -Be $true

# Integration tests exist
$integrationTests = (Get-ChildItem "tests/integration" -Filter "test_*.py" -Recurse).Count
Write-Host "Integration tests: $integrationTests (should be > 0)"
```

---

## Success Metrics

**Completion Criteria**:
- ✅ Module-specific tests extracted to module/tests/
- ✅ Integration tests remain in tests/integration/
- ✅ pytest discovers all tests
- ✅ Each module's tests run independently
- ✅ pytest.ini updated

**Time Savings**:
- Manual: 4 hours (manual classification + copy)
- Pattern: 1 hour (automated extraction)
- Speedup: 4x faster

---

## Ground Truth Commands

```powershell
# Total test files
$totalTests = (Get-ChildItem "phase*/modules/*/tests" -Filter "test_*.py" -Recurse).Count + (Get-ChildItem "tests/integration" -Filter "test_*.py" -Recurse).Count
Write-Host "Total tests: $totalTests (Expected: ~196)"

# pytest collection
pytest --collect-only -q | Select-String "collected"

# All module tests pass
pytest phase0_bootstrap/modules/ phase1_planning/modules/ phase4_routing/modules/ phase6_error_recovery/modules/ phase7_monitoring/modules/ -v
```
