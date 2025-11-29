# Examples Directory

**Purpose**: Reference examples for each pattern, including generated outputs and glossary assets.

**Status**: Active

---

## Contents

### Subdirectories

This directory contains pattern-specific example folders:

| Pattern Type | Example Folders |
|--------------|-----------------|
| **Atomic Create** | `atomic_create/`, `atomic_create_001/`, `atomic_create_template/`, `atomic_create_template_001/` |
| **Batch Create** | `batch_create/`, `batch_create_001/`, `batch_file_creation/`, `batch_file_gen_001/` |
| **Module Creation** | `module_creation/`, `module_creation_001/`, `module_creation_convergence/` |
| **Self Heal** | `self_heal/`, `self_heal_001/` |
| **Verify Commit** | `verify_commit/`, `verify_commit_001/` |
| **Refactor Patch** | `refactor_patch/`, `refactor_patch_001/` |
| **Worktree Lifecycle** | `worktree_lifecycle/`, `worktree_lifecycle_001/` |
| **Utility Patterns** | `grep_view_edit/`, `view_edit_verify/`, `preflight_verify/`, `pytest_green_verify/` |
| **Setup Patterns** | `config_setup_001/`, `database_setup_001/` |
| **Other** | `phase_discovery_001/`, `integration_hook_001/`, `e2e_validation_001/`, `decision_elimination_bootstrap/`, `create_test_commit/`, `multi_workstream_doc_suite_gen_001/` |

### Special Folders

| Directory | Purpose |
|-----------|---------|
| `generated_docs/` | Consolidated generated documentation samples |
| `glossary/` | Glossary-related artifacts and exports |

---

## Usage

1. **Explore pattern-specific folders** to see expected inputs/outputs before executing patterns
2. **Use as templates** for new pattern instances
3. **Reference for testing** executor implementations

---

## Example Structure

Each pattern folder typically contains:

```
pattern_name/
├── input.yaml      # Sample input specification
├── output/         # Expected output files
└── notes.md        # Usage notes (optional)
```

---

## Related

- `../specs/` - Pattern specifications
- `../executors/` - Pattern executor implementations
- `../schemas/` - Input/output validation schemas
