# Module Refactor Patterns - Quick Reference

## Overview

Four reusable execution patterns for safely refactoring your repository into a module-centric architecture:

| Pattern ID | Name | Purpose | Time Savings |
|------------|------|---------|--------------|
| `PAT-MODULE-REFACTOR-SCAN-001` | Scan Documents | Build document inventory | 95% |
| `PAT-MODULE-REFACTOR-INVENTORY-002` | Create Inventory | Define modules & dependencies | 90% |
| `PAT-MODULE-REFACTOR-MIGRATE-003` | Migrate Module | Move one module safely | 92% |
| `PAT-MODULE-REFACTOR-ORCHESTRATE-004` | Complete Migration | Full end-to-end refactor | 98% |

---

## Quick Start

### Option 1: Full Automated Refactor (Recommended for First-Time Dry Run)

```bash
# Dry run first - ALWAYS!
Execute pattern PAT-MODULE-REFACTOR-ORCHESTRATE-004 with:
  dry_run: true
  
# Review reports, then run live
Execute pattern PAT-MODULE-REFACTOR-ORCHESTRATE-004 with:
  dry_run: false
  auto_commit_each_module: false
  stop_on_error: true
```

### Option 2: Step-by-Step Manual Control

```bash
# Step 1: Scan documents
Execute pattern PAT-MODULE-REFACTOR-SCAN-001

# Step 2: Create module inventory
Execute pattern PAT-MODULE-REFACTOR-INVENTORY-002

# Step 3: Migrate modules one at a time
Execute pattern PAT-MODULE-REFACTOR-MIGRATE-003 with:
  module_id: "registry_core"
  dry_run: false
  run_tests: true
  auto_commit: false

# Repeat step 3 for each module in dependency order
```

---

## Pattern Details

### PAT-MODULE-REFACTOR-SCAN-001: Scan Documents

**Purpose**: Discover and classify all .md/.txt files in repository

**Inputs**:
- `repo_root` (default: ".")
- `output_path` (default: ".state/docs_inventory.jsonl")
- `compute_hash` (default: false)

**Outputs**:
- `.state/docs_inventory.jsonl` - Machine-readable inventory
- `.state/docs_inventory.jsonl.summary.json` - Classification summary

**What it does**:
1. Recursively scans repository for documentation
2. Extracts metadata (size, headings, frontmatter, keywords)
3. Classifies by module_kind and zone
4. Generates JSONL inventory for downstream patterns

**Example**:
```yaml
inputs:
  compute_hash: false
  max_preview_chars: 4000
```

---

### PAT-MODULE-REFACTOR-INVENTORY-002: Create Module Inventory

**Purpose**: Define the canonical list of modules and their dependencies

**Inputs**:
- `output_path` (default: "modules/MODULES_INVENTORY.yaml")
- `include_dependencies` (default: true)

**Outputs**:
- `modules/MODULES_INVENTORY.yaml` - Complete module definitions
- `modules/MODULE_DEPENDENCIES.yaml` - Dependency graph

**What it does**:
1. Creates MODULES_INVENTORY.yaml with 12 modules:
   - **Pipeline**: intake_spec, planning, scheduling, execution, error_recovery, state_lifecycle, reporting
   - **Services**: aim_tools, patterns_engine, spec_bridge, registry_core
   - **Interface**: gui_shell
2. Defines dependencies between modules
3. Provides migration ordering recommendations

**Example**:
```yaml
inputs:
  include_dependencies: true
  validate_against_dataflows: true
```

---

### PAT-MODULE-REFACTOR-MIGRATE-003: Migrate Single Module

**Purpose**: Safely migrate one module from legacy paths to `modules/<module_id>/`

**Inputs**:
- `module_id` (required) - e.g., "aim_tools"
- `dry_run` (default: false)
- `run_tests` (default: true)
- `auto_commit` (default: false)

**Outputs**:
- `modules/<module_id>/` - New module structure
- `reports/module_migrations/<module_id>_migration_<timestamp>.md` - Migration report

**What it does**:
1. Creates recovery point (for rollback)
2. Creates module skeleton (src/, docs/, schemas/, tests/, config/)
3. Builds file move plan from docs inventory
4. Moves files using `git mv` (preserves history)
5. Updates registry paths
6. Validates files exist at new locations
7. Runs module tests
8. Generates migration report

**Safety features**:
- PowerShell recovery point before changes
- `git mv` preserves history
- Validation at each step
- Can rollback on failure
- Dry-run mode

**Example**:
```yaml
inputs:
  module_id: "aim_tools"
  dry_run: false
  run_tests: true
  auto_commit: false
```

**Rollback**:
```powershell
$recoveryId = Get-Content ".state/current_recovery_point.txt"
Restore-RecoveryPoint -RecoveryId $recoveryId
```

---

### PAT-MODULE-REFACTOR-ORCHESTRATE-004: Complete Migration

**Purpose**: Orchestrate end-to-end refactor of all modules

**Inputs**:
- `dry_run` (default: false)
- `auto_commit_each_module` (default: false)
- `stop_on_error` (default: true)
- `skip_tests` (default: false)

**Outputs**:
- `reports/module_refactor_complete_<timestamp>.md` - Final report
- All module directories created
- Registry fully updated

**What it does**:
Executes complete refactor in 6 phases:

1. **Phase 0 (Preparation)**:
   - Scan documents → `.state/docs_inventory.jsonl`
   - Create module inventory → `modules/MODULES_INVENTORY.yaml`

2. **Phase 1 (Independent)**: `registry_core`, `state_lifecycle`
3. **Phase 2 (Services)**: `spec_bridge`, `patterns_engine`, `aim_tools`
4. **Phase 3 (Early Pipeline)**: `intake_spec`, `planning`
5. **Phase 4 (Core Pipeline)**: `scheduling`, `execution`
6. **Phase 5 (Late Pipeline)**: `error_recovery`, `reporting`
7. **Phase 6 (Interface)**: `gui_shell`

Each phase migrates modules in dependency order.

**Example - Dry Run**:
```yaml
inputs:
  dry_run: true
```

**Example - Live Migration**:
```yaml
inputs:
  dry_run: false
  auto_commit_each_module: false
  stop_on_error: true
  skip_tests: false
```

---

## Migration Order (Dependency-Based)

**CRITICAL**: Modules must be migrated in this order:

```
Phase 1: Independent (no dependencies)
├─ registry_core
└─ state_lifecycle

Phase 2: Feature Services
├─ spec_bridge
├─ patterns_engine
└─ aim_tools

Phase 3-6: Pipeline + Interface
├─ intake_spec
├─ planning
├─ scheduling
├─ execution
├─ error_recovery
├─ reporting
└─ gui_shell
```

---

## File Structure After Refactor

```
modules/
├─ registry_core/
│  ├─ src/          # Python/PS code
│  ├─ docs/         # Module documentation
│  ├─ schemas/      # JSON/YAML schemas
│  ├─ tests/        # Unit/integration tests
│  ├─ config/       # Config files
│  ├─ examples/     # Usage examples
│  └─ README.md     # Module overview
├─ state_lifecycle/
│  └─ [same structure]
├─ aim_tools/
│  └─ [same structure]
... (all 12 modules)
```

---

## Common Workflows

### Workflow 1: First-Time Full Refactor

```bash
# 1. Dry run to preview
Execute PAT-MODULE-REFACTOR-ORCHESTRATE-004 with dry_run=true

# 2. Review reports in reports/module_refactor_complete_*.md

# 3. Run live migration
Execute PAT-MODULE-REFACTOR-ORCHESTRATE-004 with:
  dry_run: false
  auto_commit_each_module: false

# 4. Manually review and test
pytest modules/
python scripts/paths_index_cli.py gate

# 5. Commit when satisfied
git commit -m "refactor: complete module-centric migration"
```

### Workflow 2: Migrate One Module Only

```bash
# Prerequisites: Run scan and inventory first
Execute PAT-MODULE-REFACTOR-SCAN-001
Execute PAT-MODULE-REFACTOR-INVENTORY-002

# Migrate specific module
Execute PAT-MODULE-REFACTOR-MIGRATE-003 with:
  module_id: "aim_tools"
  dry_run: false
  run_tests: true
  auto_commit: false

# Review and commit
git add -A
git commit -m "refactor: migrate aim_tools module"
```

### Workflow 3: Rollback Failed Migration

```powershell
# Find recovery point ID
$recoveryId = Get-Content ".state/current_recovery_point.txt"

# Restore
Restore-RecoveryPoint -RecoveryId $recoveryId

# Verify rollback
git status
```

---

## Validation Checks

Each pattern includes built-in validation:

### Scan (001)
- ✓ Inventory file created
- ✓ Valid JSONL format
- ✓ Minimum 10 documents found

### Inventory (002)
- ✓ MODULES_INVENTORY.yaml created
- ✓ Valid YAML
- ✓ All module_ids defined

### Migrate (003)
- ✓ Module skeleton created
- ✓ All files moved successfully
- ✓ Registry paths updated
- ✓ Tests pass (if enabled)

### Orchestrate (004)
- ✓ All 12 modules created
- ✓ Each module has expected structure
- ✓ Final validation passes

---

## Outputs & Reports

### During Migration

- `.state/docs_inventory.jsonl` - Full document inventory
- `.state/docs_inventory.jsonl.summary.json` - Classification summary
- `.state/move_plan_<module_id>.json` - File move plan per module
- `.state/move_result_<module_id>.json` - Move results per module
- `.state/current_recovery_point.txt` - Latest recovery point ID

### Final Reports

- `modules/MODULES_INVENTORY.yaml` - Module definitions
- `modules/MODULE_DEPENDENCIES.yaml` - Dependency graph
- `reports/module_migrations/<module_id>_migration_<timestamp>.md` - Per-module report
- `reports/module_refactor_complete_<timestamp>.md` - Final summary

---

## Prerequisites

### Before Running Patterns

1. **Clean git working tree**:
   ```bash
   git status  # Should be clean
   ```

2. **Python 3.8+** installed:
   ```bash
   python --version
   ```

3. **PowerShell recovery functions** available:
   - `New-RecoveryPoint`
   - `Restore-RecoveryPoint`
   - `Release-ModuleLock`

4. **(Optional) Pytest** for test validation:
   ```bash
   pip install pytest
   ```

---

## Troubleshooting

### "Module not found in inventory"
**Solution**: Run `PAT-MODULE-REFACTOR-INVENTORY-002` first

### "Dependencies not migrated"
**Solution**: Migrate modules in correct order (see dependency graph in `MODULE_DEPENDENCIES.yaml`)

### "Recovery point not found"
**Solution**: Check `.state/current_recovery_point.txt` exists. If migration failed early, no recovery point was created.

### "Tests failed after migration"
**Solution**: 
1. Review test output
2. Check import paths (run `python scripts/paths_index_cli.py gate`)
3. Rollback if needed: `Restore-RecoveryPoint -RecoveryId <id>`

---

## Best Practices

✅ **DO**:
- Always run dry_run=true first
- Migrate modules in dependency order
- Run tests after each module
- Review migration reports
- Commit after each successful module

❌ **DON'T**:
- Skip scan/inventory steps
- Migrate dependent modules before dependencies
- Skip tests to "save time"
- Delete recovery points until refactor is complete
- Touch SANDBOX or ARCHIVE directories

---

## Time Estimates

| Task | Manual | Automated | Savings |
|------|--------|-----------|---------|
| Document scan | 4 hours | 2 min | 99% |
| Module inventory | 8 hours | 1 min | 99% |
| Migrate 1 module | 3-4 hours | 1 min | 98% |
| Full refactor (12 modules) | 40-60 hours | 15 min | 98% |

---

## Pattern Registry

All patterns are registered in:
```
UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/registry/PATTERN_INDEX.yaml
```

Pattern specs located at:
```
UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/specs/
├─ module_refactor_scan_docs.pattern.yaml
├─ module_refactor_create_inventory.pattern.yaml
├─ module_refactor_migrate_single_module.pattern.yaml
└─ module_refactor_complete_migration.pattern.yaml
```

---

## Support

For issues or questions:
1. Check pattern validation output
2. Review migration reports
3. Check `.state/` for detailed logs
4. Rollback using recovery points if needed

---

**Last Updated**: 2025-11-28  
**Pattern Version**: 1.0.0  
**Status**: Active
