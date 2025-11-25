# Module-Centric Architecture Migration Guide

## Overview

This guide explains the migration from **artifact-type organization** (current) to **module-centric organization** for AI-oriented codebases.

## Current State vs Target State

### Current (Artifact-Type Organization)
```
core/
  state/
    db.py
    crud.py
tests/
  state/
    test_db.py
docs/
  STATE_GUIDE.md
schema/
  state.schema.json
```

**Problems**:
- AI must load context from 4 different locations
- SafePatch worktrees need complex file tracking
- No atomic module boundaries
- Cross-directory coordination for changes

### Target (Module-Centric Organization)
```
modules/
  core-state/
    01JDEX_db.py                    # Code
    01JDEX_db.test.py               # Test oracle
    01JDEX_db.schema.json           # Contract
    01JDEX_db.md                    # Documentation
    01JDEX_module.manifest.json     # Module metadata
    .state/
      current.json                  # Module state
```

**Benefits**:
- **Deterministic context loading**: `load_module("modules/core-state/")`
- **Atomic SafePatch**: Clone just one directory
- **ULID-based identity**: Machine-verifiable relationships (`01JDEX` prefix)
- **Parallel AI execution**: No shared bottlenecks

---

## Migration Strategy

### Phase 1: Create Schema & Proof of Concept (2 hours)
**Status**: ✅ COMPLETE

1. ✅ Create `schema/module.schema.json` - Unified module manifest schema
2. ⏳ Create example manifest for `error-plugin-ruff`
3. ⏳ Validate proof-of-concept structure

### Phase 2: Parallel Structure (Safe Coexistence, 1 week)

**Goal**: New module-centric structure coexists with current structure. No breaking changes.

```
# Current structure stays
core/state/db.py
tests/state/test_db.py

# New structure added
modules/
  core-state/
    01JDEX_db.py → symlink to ../../core/state/db.py
    01JDEX_db.test.py → symlink to ../../tests/state/test_db.py
    01JDEX_module.manifest.json
```

**Actions**:
1. Create `modules/` directory
2. For each logical module in `CODEBASE_INDEX.yaml`:
   - Create `modules/{module-id}/` directory
   - Generate ULID prefix (6 chars)
   - Create `module.manifest.json` from schema
   - Symlink existing files with ULID naming
3. Update `CODEBASE_INDEX.yaml` to reference both structures

**Validation**:
- All existing tests pass
- Import paths work unchanged
- CI gates pass

### Phase 3: Incremental Migration (2-4 weeks)

**Goal**: Move files to module-centric structure one module at a time.

**Order** (least risky to most risky):
1. **Error plugins** (already module-like)
2. **Specifications tools** (isolated utility modules)
3. **AIM** (self-contained)
4. **PM** (self-contained)
5. **Core.state** (critical but well-tested)
6. **Core.engine** (most central, migrate last)

**Per-module migration**:
1. Move files from symlinks to actual files in `modules/{id}/`
2. Update import paths via `paths_index_cli.py`
3. Run module tests
4. Run integration tests
5. Update documentation
6. Commit

**Validation per module**:
```bash
# Run module tests
pytest modules/core-state/*.test.py

# Validate imports
python scripts/paths_index_cli.py gate --db refactor_paths.db

# Run full test suite
pytest -q tests/
```

### Phase 4: Cleanup (1 week)

**Goal**: Archive old structure, make module-centric canonical.

1. Archive `core/`, `tests/`, `docs/` → `legacy/structure_archived_{date}/`
2. Update all documentation to reference `modules/`
3. Update `CODEBASE_INDEX.yaml` to only reference module structure
4. Remove symlinks
5. Update CI/CD to use module-centric paths

---

## Module Manifest Template

Every module contains `module.manifest.json`:

```json
{
  "module_id": "core-state",
  "ulid_prefix": "01JDEX",
  "purpose": "Database operations, CRUD, and state management",
  "layer": "infra",
  "version": "2.0.0",
  
  "state": {
    "enabled": true,
    "state_file": ".state/current.json",
    "snapshots_enabled": true
  },
  
  "artifacts": {
    "code": [
      {
        "path": "01JDEX_db.py",
        "ulid": "01JDEX000000000000000001",
        "entry_point": true,
        "exports": [
          {
            "name": "init_db",
            "type": "function",
            "signature": "init_db(db_path: str = 'pipeline.db') -> sqlite3.Connection"
          }
        ]
      }
    ],
    "schemas": [
      {
        "path": "01JDEX_db.schema.json",
        "ulid": "01JDEX000000000000000002",
        "validates": "database_config"
      }
    ],
    "tests": [
      {
        "path": "01JDEX_db.test.py",
        "ulid": "01JDEX000000000000000003",
        "test_type": "unit",
        "coverage_target": "01JDEX_db.py"
      }
    ],
    "docs": [
      {
        "path": "01JDEX_db.md",
        "ulid": "01JDEX000000000000000004",
        "doc_type": "API"
      }
    ]
  },
  
  "dependencies": {
    "modules": [],
    "external": [
      {
        "name": "sqlite3",
        "package_manager": "pip"
      }
    ]
  },
  
  "import_patterns": [
    {
      "pattern": "from core.state.db import init_db",
      "description": "Initialize database connection",
      "deprecated": false
    }
  ],
  
  "contracts": {
    "invariants": [
      {
        "statement": "Database connections always use connection pool",
        "enforced_by": "01JDEX_db.test.py::test_connection_pool"
      }
    ]
  },
  
  "ai_metadata": {
    "priority": "HIGH",
    "edit_policy": "safe",
    "context_tokens_estimate": 2500,
    "key_patterns": [
      "SQLite connection management",
      "Schema versioning via migrations"
    ],
    "common_tasks": [
      {
        "task": "Initialize database",
        "entry_point": "init_db",
        "example": "db = init_db('pipeline.db')"
      }
    ]
  },
  
  "metadata": {
    "created": "2025-11-25T21:00:00Z",
    "last_updated": "2025-11-25T21:00:00Z",
    "status": "active"
  }
}
```

---

## ULID Naming Convention

**ULID Structure**: `01JDEX_descriptive_name.ext`
- **Prefix (6 chars)**: `01JDEX` - Module-specific, time-based identifier
- **Underscore**: Separator
- **Name**: Descriptive snake_case name
- **Extension**: File type

**ULID Generation**:
```python
import ulid
module_prefix = ulid.create().str[:6]  # "01JDEX"
```

**Example**:
```
modules/core-state/
  01JDEX_db.py
  01JDEX_db.test.py
  01JDEX_db.schema.json
  01JDEX_db.md
  01JDEX_crud.py
  01JDEX_crud.test.py
```

All files with `01JDEX` prefix belong to the `core-state` module.

---

## Module Structure Standards

### Minimal Module
```
modules/my-module/
  {ULID}_code.py                  # At least one code file
  {ULID}_module.manifest.json     # Required manifest
```

### Standard Module
```
modules/my-module/
  {ULID}_code.py
  {ULID}_code.test.py             # Test oracle
  {ULID}_code.schema.json         # Input/output contracts
  {ULID}_code.md                  # Documentation
  {ULID}_module.manifest.json     # Module metadata
  .state/                         # Optional module state
    current.json
```

### Complex Module (with submodules)
```
modules/core/
  01JDEX_module.manifest.json     # Parent manifest
  submodules/
    state/
      {ULID}_module.manifest.json
      {ULID}_db.py
      {ULID}_db.test.py
    engine/
      {ULID}_module.manifest.json
      {ULID}_orchestrator.py
```

---

## Integration with Existing Systems

### CODEBASE_INDEX.yaml
```yaml
modules:
  - id: "core-state"
    name: "Core State Management"
    path: "modules/core-state/"  # Module-centric path
    manifest: "modules/core-state/01JDEX_module.manifest.json"
    layer: "infra"
    # ... rest of metadata from manifest
```

### SQLite Database
Add `modules` table:
```sql
CREATE TABLE modules (
  module_id TEXT PRIMARY KEY,
  ulid_prefix TEXT NOT NULL,
  path TEXT NOT NULL,
  layer TEXT NOT NULL,
  status TEXT DEFAULT 'active',
  version TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### Task Execution
Tasks now reference modules atomically:
```json
{
  "task_id": "t-001",
  "epic": "epic-001",
  "story": "story-001",
  "module": "modules/core-state/",
  "action": "modify",
  "files": ["01JDEX_db.py"],
  "tests": ["01JDEX_db.test.py"]
}
```

### SafePatch Worktrees
```bash
# Clone just the module being modified
git worktree add .worktrees/fix-state modules/core-state/

cd .worktrees/fix-state
# All code, tests, docs, schemas are RIGHT HERE
pytest *.test.py
```

---

## AI Context Loading

### Before (Scattered)
```python
load_context([
    "core/state/db.py",           # Code
    "tests/state/test_db.py",     # Tests
    "docs/STATE_GUIDE.md",        # Docs
    "schema/state.schema.json"    # Schema
])
# AI must know repository conventions
```

### After (Atomic)
```python
load_module("modules/core-state/")
# Everything in one place
# Manifest defines structure
```

**Deterministic token budget**:
```python
manifest = load_json("modules/core-state/01JDEX_module.manifest.json")
estimated_tokens = manifest["ai_metadata"]["context_tokens_estimate"]
# 2500 tokens - fits in context window
```

---

## Validation Scripts

### Validate Module Structure
```python
# scripts/validate_modules.py
import json
from pathlib import Path
from jsonschema import validate

def validate_module(module_path: Path):
    manifest_path = module_path / "module.manifest.json"
    schema_path = Path("schema/module.schema.json")
    
    manifest = json.loads(manifest_path.read_text())
    schema = json.loads(schema_path.read_text())
    
    validate(instance=manifest, schema=schema)
    
    # Check ULID consistency
    ulid_prefix = manifest["ulid_prefix"]
    for artifact_type in manifest["artifacts"].values():
        for artifact in artifact_type:
            assert artifact["path"].startswith(ulid_prefix), \
                f"Artifact {artifact['path']} does not match prefix {ulid_prefix}"
    
    print(f"✅ {module_path} valid")

# Run for all modules
for module_path in Path("modules").iterdir():
    if module_path.is_dir():
        validate_module(module_path)
```

### Check Import Paths
```bash
# All imports updated to module-centric
python scripts/paths_index_cli.py gate --db refactor_paths.db
```

---

## Rollback Strategy

If migration fails at any phase:

### Phase 1 (Schema only)
- Delete `schema/module.schema.json`
- No impact

### Phase 2 (Parallel structure)
- Delete `modules/` directory
- Remove symlinks
- Continue using current structure
- No code changes needed

### Phase 3 (During migration)
- Revert last module migration commit
- Fix issues
- Re-run migration for that module

### Phase 4 (After completion)
- Restore from `legacy/structure_archived_{date}/`
- Revert import path changes via git
- Re-run tests

---

## Success Criteria

### Phase 1
- [ ] `schema/module.schema.json` validates successfully
- [ ] Example manifest for one plugin passes validation

### Phase 2
- [ ] All modules have manifests in `modules/*/module.manifest.json`
- [ ] Symlinks created for all artifacts
- [ ] All existing tests pass
- [ ] CI gates pass

### Phase 3 (per module)
- [ ] Module files moved to `modules/{id}/`
- [ ] Import paths updated
- [ ] Module tests pass
- [ ] Integration tests pass
- [ ] Documentation updated

### Phase 4
- [ ] Old structure archived
- [ ] All references updated
- [ ] `CODEBASE_INDEX.yaml` only references `modules/`
- [ ] CI/CD updated
- [ ] Full test suite passes

---

## Next Steps

1. **Immediate**: Create proof-of-concept for `error-plugin-ruff`
2. **This week**: Validate manifest schema with existing modules
3. **Next week**: Begin Phase 2 (parallel structure)
4. **Month 1**: Complete migration of low-risk modules
5. **Month 2**: Migrate core modules
6. **Month 3**: Cleanup and documentation

---

## Questions & Answers

**Q: What about cross-module imports?**
A: Import paths stay the same initially. Manifests track dependencies. Later, we can evolve to module-relative imports.

**Q: How do submodules work?**
A: Parent manifest lists submodules. Each submodule has its own manifest. Enables hierarchical organization.

**Q: What about generated files?**
A: Manifests track generated artifacts. ULID naming applies. `.state/` holds runtime state.

**Q: How does this affect CI/CD?**
A: Phase 4 updates CI to use module paths. Tests run per-module. Parallel execution enabled.

**Q: Migration time estimate?**
A: Phase 1: 2 hours, Phase 2: 1 week, Phase 3: 2-4 weeks, Phase 4: 1 week. Total: 4-6 weeks for full migration.

---

**Status**: Schema created ✅  
**Next**: Create proof-of-concept manifest  
**Date**: 2025-11-25
