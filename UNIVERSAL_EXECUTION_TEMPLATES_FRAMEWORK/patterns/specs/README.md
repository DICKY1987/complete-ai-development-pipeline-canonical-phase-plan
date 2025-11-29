# Specs Directory

**Purpose**: Canonical pattern specifications and supporting design docs.

**Status**: Active

---

## Contents

### Subdirectories

| Directory | Purpose |
|-----------|---------|
| `auto_approved/` | Automatically approved pattern specifications |

### Pattern Specifications (`*.pattern.yaml`)

| Pattern | Specification File |
|---------|-------------------|
| **Atomic Create** | `atomic_create.pattern.yaml`, `atomic_create_template.pattern.yaml` |
| **Batch Operations** | `batch_create.pattern.yaml`, `batch_file_creation.pattern.yaml`, `batch_file_generation.pattern.yaml` |
| **Module Creation** | `module_creation.pattern.yaml`, `module_creation_convergence.pattern.yaml` |
| **Self Heal** | `self_heal.pattern.yaml` |
| **Verification** | `verify_commit.pattern.yaml`, `preflight_verify.pattern.yaml`, `pytest_green_verify.pattern.yaml`, `validation_e2e.pattern.yaml` |
| **Refactoring** | `refactor_patch.pattern.yaml` |
| **Worktree** | `worktree_lifecycle.pattern.yaml` |
| **Configuration** | `configuration_setup.pattern.yaml`, `database_setup.pattern.yaml` |
| **Discovery** | `phase_discovery.pattern.yaml` |
| **Decision** | `decision_elimination_bootstrap.pattern.yaml` |
| **Utilities** | `grep_view_edit.pattern.yaml`, `view_edit_verify.pattern.yaml`, `create_test_commit.pattern.yaml`, `integration_hook.pattern.yaml`, `multi_workstream_doc_suite_generation.pattern.yaml` |

### Design Documents

| File | Description |
|------|-------------|
| `EXEC-009-docid-registration.md` | Document ID registration design |
| `EXEC-010-index-builder.md` | Index builder design |
| `EXEC-011-worktree-workflow.md` | Worktree workflow design |
| `PAT-PATCH-001_patch_lifecycle_management.md` | Patch lifecycle guidance |
| `PAT-SEARCH-001_deep_directory_search.md` | Deep directory search spec |
| `PAT-SEARCH-002_readme_presence_audit.md` | README audit specification |

---

## Pattern Specification Structure

Each `*.pattern.yaml` file contains:

```yaml
id: PAT-XXX-001
name: Pattern Name
version: 1.0.0
category: creation | verification | refactoring | ...
description: What this pattern does
inputs:
  - name: input_name
    type: string
    required: true
outputs:
  - name: output_name
    type: file
steps:
  - action: step_action
    description: What this step does
verification:
  - check: Verification check description
```

---

## Usage

### View Pattern Details

```powershell
# Via CLI
..\scripts\pattern_cli.ps1 -Action info -PatternId PAT-ATOMIC-CREATE-001
```

### Create New Pattern

1. Copy existing specification as template
2. Update ID, name, and metadata
3. Define inputs, outputs, and steps
4. Add verification checks
5. Register in `../registry/PATTERN_INDEX.yaml`

---

## Source of Truth

**Pattern specifications are the source of truth for:**

- `../executors/` - Executor implementations
- `../schemas/` - Validation schemas
- `../tests/` - Test cases

---

## Related

- `../registry/PATTERN_INDEX.yaml` - Pattern registry
- `../executors/` - Executor implementations
- `../schemas/` - Validation schemas
- `../examples/` - Usage examples
