---
doc_id: DOC-GUIDE-MODULE-CENTRIC-QUICK-REFERENCE-391
---

# Module-Centric Architecture - Quick Reference

**TL;DR**: Organize by module (not artifact type). Each module = atomic, self-contained unit.

---

## Core Concept

### ❌ Before (Artifact-Type)
```
core/state/db.py
tests/state/test_db.py
docs/STATE_GUIDE.md
schema/state.schema.json
```
**Problem**: AI loads from 4 locations

### ✅ After (Module-Centric)
```
modules/core-state/
  01JDEX_db.py
  01JDEX_db.test.py
  01JDEX_db.schema.json
  01JDEX_db.md
  01JDEX_module.manifest.json
```
**Benefit**: AI loads one directory atomically

---

## ULID Naming

**Format**: `{PREFIX}_{name}.{ext}`
- **Prefix**: 6-char ULID (e.g., `01JDEX`)
- **Name**: Descriptive (e.g., `db`, `orchestrator`)
- **Extension**: File type

**Example**:
```
01JDEX_db.py              # Code
01JDEX_db.test.py         # Test
01JDEX_db.schema.json     # Schema
01JDEX_db.md              # Docs
```

All files with `01JDEX` → Same module ✅

---

## Module Structure

### Minimal
```
modules/my-module/
  {ULID}_code.py
  {ULID}_module.manifest.json
```

### Standard
```
modules/my-module/
  {ULID}_code.py
  {ULID}_code.test.py
  {ULID}_code.schema.json
  {ULID}_code.md
  {ULID}_module.manifest.json
  .state/current.json
```

---

## Module Manifest (manifest.json)

**Required fields**:
```json
{
  "module_id": "core-state",
  "ulid_prefix": "01JDEX",
  "purpose": "Database operations",
  "layer": "infra"
}
```

**Full example**: See `docs/examples/module.manifest.example.json`

---

## Commands

### Validate Manifests
```bash
# Single file
python scripts/validate_modules.py path/to/manifest.json

# All modules
python scripts/validate_modules.py --all
```

### Generate ULID
```python
import ulid
prefix = ulid.new().str[:6]  # "01KAYE"
```

---

## Migration Phases

1. **Schema** (✅ DONE) - Define structure
2. **Parallel** (1 week) - Symlinks, safe coexistence
3. **Migrate** (2-4 weeks) - Move files incrementally
4. **Cleanup** (1 week) - Archive old structure

---

## Key Files

- **Schema**: `schema/module.schema.json`
- **Guide**: `docs/MODULE_CENTRIC_MIGRATION_GUIDE.md`
- **Example**: `docs/examples/module.manifest.example.json`
- **Validator**: `scripts/validate_modules.py`
- **Summary**: `docs/MODULE_CENTRIC_IMPLEMENTATION_SUMMARY.md`

---

## Benefits Summary

| Benefit | Before | After |
|---------|--------|-------|
| **Context loading** | 4+ locations | 1 directory |
| **Relationships** | Parse imports | ULID prefix |
| **SafePatch** | Complex tracking | Clone one dir |
| **Parallel AI** | Bottlenecks | Independent modules |
| **Self-documenting** | Human conventions | Machine manifest |

---

## Next Actions

1. ✅ Schema created
2. ✅ Example validated
3. ⏳ Create first real module
4. ⏳ Start Phase 2 (parallel structure)

---

**Questions?** See `docs/MODULE_CENTRIC_IMPLEMENTATION_SUMMARY.md`
