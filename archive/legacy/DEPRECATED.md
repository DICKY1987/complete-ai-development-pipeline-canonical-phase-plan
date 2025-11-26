# ⚠️ DEPRECATED - DO NOT USE

This directory contains archived code from previous architecture iterations.

**Status**: READ-ONLY - Kept for reference only  
**Last Active**: 2025-11-19  
**Reason**: Section-based refactor (src.pipeline → core.*)

---

## What Was Here

This directory contains code from deprecated architecture approaches:
- Old pipeline implementation (src/pipeline/)
- Legacy error detection (MOD_ERROR_PIPELINE/)
- Archived utilities and experiments
- Prototypes and proof-of-concepts

**All functionality has been reimplemented in the current section-based architecture.**

---

## Current Replacements

| Deprecated Path | Use Instead | Module |
|-----------------|-------------|--------|
| `src.pipeline.*` | `core.*` | Core orchestration |
| `src.pipeline.db` | `core.state.db` | Database operations |
| `src.pipeline.orchestrator` | `core.orchestrator` | Orchestrator |
| `MOD_ERROR_PIPELINE.*` | `error.*` | Error detection |
| `MOD_ERROR_PIPELINE.error_engine` | `error.engine.error_engine` | Error engine |
| `legacy.utils.*` | `core.state.dag_utils` | DAG utilities |

**Complete mapping**: [docs/SECTION_REFACTOR_MAPPING.md](../docs/SECTION_REFACTOR_MAPPING.md)

---

## Migration Guide

### Step 1: Identify Deprecated Import
```python
# Your old code (will fail CI)
from src.pipeline.db import init_db
```

### Step 2: Find Replacement
Check [docs/SECTION_REFACTOR_MAPPING.md](../docs/SECTION_REFACTOR_MAPPING.md) or use this table above.

### Step 3: Update Import
```python
# New correct import
from core.state.db import init_db
```

### Step 4: Validate
```bash
python scripts/paths_index_cli.py gate --db refactor_paths.db
```

**CI will block** any PR with deprecated imports.

---

## For AI Tools

### ❌ DO NOT
- **Suggest code from this directory**
- **Import from** `src.pipeline`, `MOD_ERROR_PIPELINE`, `legacy.*`
- **Reference these paths** in new code
- **Copy patterns** from deprecated code
- **Recommend** these imports to users

### ✅ DO
- **Use section-based paths**: `core.*`, `error.*`, `aim.*`, `pm.*`
- **Check** [docs/SECTION_REFACTOR_MAPPING.md](../docs/SECTION_REFACTOR_MAPPING.md) for replacements
- **Validate imports** via `python scripts/paths_index_cli.py gate`
- **Read** [.ai-context.md](../.ai-context.md) for correct patterns
- **Follow** import standards in [docs/CI_PATH_STANDARDS.md](../docs/CI_PATH_STANDARDS.md)

### If User Asks About Legacy Code
1. **Explain** it's deprecated
2. **Point to** current replacement in table above
3. **Link to** [docs/SECTION_REFACTOR_MAPPING.md](../docs/SECTION_REFACTOR_MAPPING.md)
4. **Suggest** correct section-based import

---

## Why Was This Deprecated?

### Old Architecture Issues
- **Monolithic structure** - Everything in src/pipeline/
- **Poor separation of concerns** - State, execution, tools mixed
- **Difficult to test** - Tight coupling
- **Hard to navigate** - Flat module hierarchy
- **Import path confusion** - Inconsistent naming

### New Architecture Benefits
- **Section-based organization** - Clear module boundaries
- **Layered architecture** - Infra → Domain → API → UI
- **Better testability** - Loose coupling, dependency injection
- **Clear navigation** - Hierarchical structure
- **Consistent imports** - `core.*`, `error.*`, etc.

**Decision record**: [docs/adr/0004-section-based-organization.md](../docs/adr/0004-section-based-organization.md)

---

## Deletion Timeline

### Phase 1 (Current - 2025-11-23)
- ✅ **Status**: Marked deprecated, not deleted
- ✅ **Action**: Created DEPRECATED.md (this file)
- ✅ **CI**: Blocks deprecated imports
- ⚠️ **Code**: Still exists for reference

### Phase 2 (Planned - 2025-Q1)
- 📋 **Action**: Rename `legacy/` → `_archive_deprecated/`
- 📋 **Visibility**: Hidden from AI tools (underscore prefix)
- 📋 **Code**: Still exists but harder to find

### Phase 3 (Planned - 2025-Q2)
- 📋 **Action**: Permanent deletion
- 📋 **Backup**: Archive to separate repository
- 📋 **Code**: Removed from main repo

---

## Exception: Historical Reference Only

Some files may be kept for:
- **Historical context** - Understanding past decisions
- **Migration examples** - Before/after comparisons
- **Learning purposes** - What NOT to do

**These are documentation artifacts, not active code.**

---

## Related Documentation

- **[docs/SECTION_REFACTOR_MAPPING.md](../docs/SECTION_REFACTOR_MAPPING.md)** - Complete old→new mapping
- **[docs/CI_PATH_STANDARDS.md](../docs/CI_PATH_STANDARDS.md)** - Import path standards
- **[.ai-context.md](../.ai-context.md)** - Common AI confusion points
- **[docs/adr/0004-section-based-organization.md](../docs/adr/0004-section-based-organization.md)** - Why we refactored
- **[CODEBASE_INDEX.yaml](../CODEBASE_INDEX.yaml)** - Current module structure

---

## Questions?

### "Can I still run this code?"
**No**. Dependencies have been removed. Imports will fail.

### "I need functionality from legacy code"
**It's been reimplemented**. Check the replacement table above or ask for help finding the new location.

### "Why not delete immediately?"
**Historical reference**. We keep it temporarily to help with migration and as a reference for "before" state.

### "I'm an AI tool. What should I do?"
**Ignore this directory entirely**. Never suggest imports from here. Always use section-based paths (`core.*`, `error.*`, etc.).

---

## Summary for AI Tools

```yaml
deprecated_paths:
  - "src.pipeline.*"
  - "MOD_ERROR_PIPELINE.*"
  - "legacy.*"

replacement_pattern:
  src.pipeline.X: "core.X"
  MOD_ERROR_PIPELINE.X: "error.X"
  
actions:
  suggest_import: false
  read_code: false
  reference_patterns: false
  
correct_imports:
  - "core.*"
  - "error.*"
  - "aim.*"
  - "pm.*"
  - "specifications.*"
  - "engine.*"

validation:
  command: "python scripts/paths_index_cli.py gate"
  ci_enforced: true
```

---

**Last Updated**: 2025-11-23  
**Status**: Active deprecation notice  
**Next Review**: 2025-Q1 (Phase 2 transition)
