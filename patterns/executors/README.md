---
doc_id: DOC-PAT-README-794
---

# Executors Directory

**Purpose**: PowerShell executors implementing pattern actions plus shared helper library.

**Status**: Active

---

## Contents

### Subdirectories

| Directory | Purpose |
|-----------|---------|
| `lib/` | Shared helper modules for executor development |

### Shared Library Modules (`lib/`)

| Module | Purpose |
|--------|---------|
| `error_rules.ps1` | Error handling and reporting |
| `parallel.ps1` | Parallel execution utilities |
| `reporting.ps1` | Output and report generation |
| `templates.ps1` | Template processing |
| `testing.ps1` | Test harness utilities |
| `transactions.ps1` | Transaction management |
| `validation.ps1` | Input/output validation |

### Pattern Executors

| Pattern Type | Executor Files |
|--------------|----------------|
| **Atomic Create** | `atomic_create_executor.ps1`, `atomic_create_001_executor.ps1`, `atomic_create_template_executor.ps1`, `atomic_create_template_001_executor.ps1` |
| **Batch Create** | `batch_create_executor.ps1`, `batch_create_001_executor.ps1`, `batch_file_creation_executor.ps1`, `batch_file_gen_001_executor.ps1` |
| **Module Creation** | `module_creation_executor.ps1`, `module_creation_001_executor.ps1`, `module_creation_convergence_executor.ps1` |
| **Self Heal** | `self_heal_executor.ps1`, `self_heal_001_executor.ps1` |
| **Verify Commit** | `verify_commit_executor.ps1`, `verify_commit_001_executor.ps1` |
| **Refactor Patch** | `refactor_patch_executor.ps1`, `refactor_patch_001_executor.ps1` |
| **Worktree Lifecycle** | `worktree_lifecycle_executor.ps1`, `worktree_lifecycle_001_executor.ps1` |
| **Glossary Operations** | `glossary_export_executor.ps1`, `glossary_link_check_executor.ps1`, `glossary_patch_apply_executor.ps1`, `glossary_sync_executor.ps1`, `glossary_term_add_executor.ps1`, `glossary_validate_executor.ps1` |
| **Other** | `grep_view_edit_executor.ps1`, `view_edit_verify_executor.ps1`, `preflight_verify_executor.ps1`, `pytest_green_verify_executor.ps1`, `config_setup_001_executor.ps1`, `database_setup_001_executor.ps1`, `phase_discovery_001_executor.ps1`, `integration_hook_001_executor.ps1`, `e2e_validation_001_executor.ps1`, `decision_elimination_bootstrap_executor.ps1`, `create_test_commit_executor.ps1`, `multi_workstream_doc_suite_gen_001_executor.ps1` |

---

## Usage

### Run Executor Directly

```powershell
# Execute a pattern
.\atomic_create_executor.ps1 -InputFile "input.yaml" -OutputDir "./output"
```

### Via CLI Tooling

```powershell
# Use pattern CLI
..\scripts\pattern_cli.ps1 -Action execute -PatternId PAT-ATOMIC-CREATE-001 -InstancePath instance.json
```

### Develop New Executor

```powershell
# Import shared library
. .\lib\validation.ps1
. .\lib\reporting.ps1

# Use library functions in your executor
```

---

## Related

- `../specs/` - Pattern specifications (source of truth)
- `../schemas/` - Input validation schemas
- `../tests/` - Executor test suites
- `../examples/` - Sample inputs/outputs
