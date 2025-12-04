# ARCHIVED: Migration Validation Scripts

**Date:** 2025-12-04
**Status:** ARCHIVED - Migration Complete

## Summary

One-off migration validation scripts have been archived after successful migration completion.

## Archived Scripts

1. **`validate_migration.py`** - Main migration validator
2. **`validate_migration_phase1.py`** - Phase 1 migration validator
3. **`validate_extracted_templates.py`** - Template extraction validator
4. **`validate_module_manifests.py`** - Module manifest validator
5. **`validate_modules.py`** - Module structure validator

## Archive Location

```
_ARCHIVE/validators_migration_oneoff_20251204_*/
```

## Rationale

These validators were created to ensure safe migration from legacy module structure to the new canonical structure. Migration has been completed successfully, making these scripts obsolete.

**Migration milestones:**
- ✅ Legacy `src/pipeline/` → `core.engine` (Complete)
- ✅ Legacy `MOD_ERROR_PIPELINE/` → `error.engine` (Complete)
- ✅ Module manifests standardized (Complete)
- ✅ Import paths updated to canonical format (Complete)

## Active Validators

The following validators remain **active** for ongoing use:

### Framework Validators
- ✅ `scripts/validate_archival_safety.py` - Archive safety checks
- ✅ `scripts/validate_registry.py` - Registry validation
- ✅ `scripts/validate_phase_plan.py` - Phase plan validation

### Domain-Specific Validators
- ✅ `doc_id/validate_doc_id_coverage.py` - Doc ID coverage
- ✅ `glossary/scripts/validate_glossary.py` - Glossary terms
- ✅ `gui/validate_gui.py` - GUI components
- ✅ `patterns/validate_automation.py` - Pattern automation

### Tool Adapter Validators
- ✅ `phase4_routing/modules/tool_adapters/src/tools/validation/*` (7 validators)

## Recovery

If migration validation is needed again:
```bash
# Restore from archive
cp _ARCHIVE/validators_migration_oneoff_20251204_*/*.py scripts/
```

## References

- **Migration Plan:** `docs/SECTION_REFACTOR_MAPPING.md`
- **Import Standards:** `docs/CI_PATH_STANDARDS.md`
- **Deduplication Report:** `DEDUPLICATION_PROGRESS_REPORT.md`
