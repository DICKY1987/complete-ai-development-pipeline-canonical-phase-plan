---
doc_id: DOC-TEST-README-163
---

# Tests Directory

**Purpose**: Deterministic PowerShell test harnesses for pattern executors.

**Status**: Active

---

## Contents

### Test Files

Each executor has a corresponding test file:

| Pattern Type | Test Files |
|--------------|------------|
| **Atomic Create** | `test_atomic_create_executor.ps1`, `test_atomic_create_001_executor.ps1`, `test_atomic_create_template_executor.ps1`, `test_atomic_create_template_001_executor.ps1` |
| **Batch Create** | `test_batch_create_executor.ps1`, `test_batch_create_001_executor.ps1`, `test_batch_file_creation_executor.ps1`, `test_batch_file_gen_001_executor.ps1` |
| **Module Creation** | `test_module_creation_executor.ps1`, `test_module_creation_001_executor.ps1`, `test_module_creation_convergence_executor.ps1` |
| **Self Heal** | `test_self_heal_executor.ps1`, `test_self_heal_001_executor.ps1` |
| **Verify Commit** | `test_verify_commit_executor.ps1`, `test_verify_commit_001_executor.ps1` |
| **Refactor Patch** | `test_refactor_patch_executor.ps1`, `test_refactor_patch_001_executor.ps1` |
| **Worktree Lifecycle** | `test_worktree_lifecycle_executor.ps1`, `test_worktree_lifecycle_001_executor.ps1` |
| **Other** | `test_grep_view_edit_executor.ps1`, `test_view_edit_verify_executor.ps1`, `test_preflight_verify_executor.ps1`, `test_pytest_green_verify_executor.ps1`, `test_config_setup_001_executor.ps1`, `test_database_setup_001_executor.ps1`, `test_phase_discovery_001_executor.ps1`, `test_integration_hook_001_executor.ps1`, `test_e2e_validation_001_executor.ps1`, `test_decision_elimination_bootstrap_executor.ps1`, `test_create_test_commit_executor.ps1`, `test_multi_workstream_doc_suite_gen_001_executor.ps1` |

---

## Usage

### Run All Tests

```powershell
# Run all executor tests
Get-ChildItem -Filter "test_*.ps1" | ForEach-Object { & $_.FullName }
```

### Run Single Test

```powershell
# Test specific executor
.\test_atomic_create_executor.ps1
```

### Test Coverage

Tests validate:

- Input validation
- Step execution
- Output generation
- Error handling
- Edge cases

---

## Test Structure

Each test file follows this pattern:

```powershell
# test_pattern_executor.ps1

Describe "Pattern Executor Tests" {
    Context "Valid Input" {
        It "Should execute successfully" {
            # Test implementation
        }
    }

    Context "Invalid Input" {
        It "Should handle errors gracefully" {
            # Test implementation
        }
    }
}
```

---

## Adding New Tests

When adding a new pattern executor:

1. Create `test_<pattern_name>_executor.ps1`
2. Mirror naming from `../executors/`
3. Include positive and negative test cases
4. Verify all steps execute correctly

---

## Related

- `../executors/` - Executor implementations (tested here)
- `../executors/lib/testing.ps1` - Test harness utilities
- `../examples/` - Test fixtures and sample data
