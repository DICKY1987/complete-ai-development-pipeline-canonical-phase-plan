---
doc_id: DOC-SCRIPT-ONEOFF-GENERATORS-ARCHIVED-819
---

# ARCHIVED: One-Off Generator Scripts

**Date:** 2025-12-04
**Status:** ARCHIVED - Tasks Complete

## Summary

One-off generator scripts have been archived after completing their intended tasks.

## Archived Scripts

1. **`generate_incomplete_report.py`** - Generated incomplete implementation reports
2. **`generate_module_inventory.py`** - Generated module inventory
3. **`generate_phase0_decisions.py`** - Generated Phase 0 architectural decisions
4. **`generate_registry_backfill_plan.py`** - Generated registry backfill plan

## Archive Location

```
_ARCHIVE/generators_oneoff_20251204_*/
```

## Rationale

These generators were created for one-time tasks during system bootstrap and migration:
- Module inventory has been generated and is maintained
- Phase 0 decisions documented and frozen
- Registry backfill completed
- Incomplete implementation tracking moved to continuous validation

## Active Generators

The following generators remain **active** for ongoing use:

### Framework Generators (Phase4)
Located in `phase4_routing/modules/tool_adapters/src/tools/generation/`:
- ✅ `generate_code_graph.py` - Code dependency graphs
- ✅ `generate_doc_index.py` - Documentation indexing
- ✅ `generate_implementation_map.py` - Implementation mapping
- ✅ `generate_repo_summary.py` - Repository summaries
- ✅ `generate_spec_index.py` - Specification indexing
- ✅ `generate_spec_mapping.py` - Spec to code mapping
- ✅ `generate_workstreams_from_openspec.py` - OpenSpec conversion
- ✅ `generate_workstreams.py` - Workstream generation

### Active Development Tools
- ✅ `scripts/dev/generate_path_index.py` - Path indexing for refactoring
- ✅ `scripts/generate_readmes.py` - Automated README updates
- ✅ `scripts/generate_repository_map.py` - Repository structure mapping

### System Analysis
- ✅ `System _Analyze/SYS_generate_incomplete_report.py` - Debugging tool

## Recovery

If historical generation is needed:
```bash
# Restore from archive
cp _ARCHIVE/generators_oneoff_20251204_*/*.py scripts/
```

## References

- **Generator Analysis:** `GENERATOR_ANALYSIS.md`
- **Deduplication Report:** `DEDUPLICATION_PROGRESS_REPORT.md`
