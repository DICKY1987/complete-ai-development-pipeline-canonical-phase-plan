---
doc_id: DOC-PAT-README-846
---

# Schemas Directory

**Purpose**: JSON and YAML schemas validating pattern inputs, glossary workflows, and outputs.

**Status**: Active

---

## Contents

### Schema Types

| Type | Pattern |
|------|---------|
| **JSON Schemas** | `*.schema.json` - Validation schemas for pattern inputs/outputs |
| **ID Schemas** | `*.schema.id.yaml` - Identifier stubs for schema registration |

### Pattern Schemas

| Pattern | Schema Files |
|---------|--------------|
| **Atomic Create** | `atomic_create.schema.json`, `atomic_create_001.schema.json`, `atomic_create_template.schema.json`, `atomic_create_template_001.schema.json` |
| **Batch Create** | `batch_create.schema.json`, `batch_create_001.schema.json`, `batch_file_creation.schema.json`, `batch_file_gen_001.schema.json` |
| **Module Creation** | `module_creation.schema.json`, `module_creation_001.schema.json`, `module_creation_convergence.schema.json` |
| **Self Heal** | `self_heal.schema.json`, `self_heal_001.schema.json` |
| **Verify Commit** | `verify_commit.schema.json`, `verify_commit_001.schema.json` |
| **Refactor Patch** | `refactor_patch.schema.json`, `refactor_patch_001.schema.json` |
| **Worktree Lifecycle** | `worktree_lifecycle.schema.json`, `worktree_lifecycle_001.schema.json` |
| **Glossary Operations** | `glossary_export.schema.json`, `glossary_link_check.schema.json`, `glossary_patch_apply.schema.json`, `glossary_sync.schema.json`, `glossary_term_add.schema.json`, `glossary_validate.schema.json` |
| **Other Patterns** | `grep_view_edit.schema.json`, `view_edit_verify.schema.json`, `preflight_verify.schema.json`, `pytest_green_verify.schema.json`, `config_setup_001.schema.json`, `database_setup_001.schema.json`, `phase_discovery_001.schema.json`, `integration_hook_001.schema.json`, `e2e_validation_001.schema.json`, `decision_elimination_bootstrap.schema.json`, `create_test_commit.schema.json`, `multi_workstream_doc_suite_gen_001.schema.json` |

---

## Usage

### Validate Pattern Instance

```bash
# Using jsonschema (Python)
jsonschema -i instance.json atomic_create.schema.json

# Using ajv (Node.js)
ajv validate -s atomic_create.schema.json -d instance.json
```

### In Executors

```powershell
# Import validation library
. ..\executors\lib\validation.ps1

# Validate input
Validate-PatternInput -InputFile "input.yaml" -SchemaFile "atomic_create.schema.json"
```

---

## Schema Structure

Each schema defines:

- **Required properties** - Mandatory inputs
- **Property types** - Expected data types
- **Constraints** - Validation rules
- **Defaults** - Default values

---

## Related

- `../specs/` - Pattern specifications (schemas derived from specs)
- `../executors/` - Executors use schemas for validation
- `../examples/` - Example inputs that conform to schemas
