# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK Folder Overlap Analysis

**DOC_ID**: DOC-ANALYSIS-FOLDER-OVERLAP-001  
**Created**: 2025-11-30  
**Status**: ANALYSIS_COMPLETE  
**Purpose**: Analyze overlap between UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK folders and root folders

---

## Executive Summary

The `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK` (UET) directory is **designed as a canonical consolidation target** for the repository. It contains folders with the same names as root-level folders because **UET is intended to replace those root folders** through a planned migration process.

### Key Finding

✅ **This is intentional, not duplication** - UET folders are the **target destination** for migrating code from root folders, per the `UET_CONSOLIDATION_MASTER_PLAN.md`.

---

## Overlapping Folder Names (14 Total)

| Root Folder | UET Folder | Overlap Type | Status |
|------------|-----------|--------------|--------|
| `aim/` | `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/aim/` | Partial | Migration Target |
| `bring_back_docs_/` | `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/bring_back_docs_/` | Different content | Tools subfolder |
| `config/` | `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/config/` | Different content | UET-specific config |
| `core/` | `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/` | Functional overlap | **Primary migration** |
| `docs/` | `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/docs/` | Partial | Governance docs only |
| `error/` | `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/error/` | Functional overlap | **Primary migration** |
| `gui/` | `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/gui/` | Partial | UI demos/examples |
| `pm/` | `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/pm/` | Partial | GitHub sync only |
| `schema/` | `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/schema/` | Complementary | Schema contracts |
| `scripts/` | `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/` | Partial | Migration scripts |
| `specifications/` | `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/specifications/` | Minimal | Tools only |
| `templates/` | `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/templates/` | Different content | Execution patterns |
| `tests/` | `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/tests/` | Complementary | UET-specific tests |
| `tools/` | `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/tools/` | Different content | Doc tools |

---

## Detailed Analysis by Folder

### 1. `aim/` - AI Module Manager

| Aspect | Root | UET |
|--------|------|-----|
| **Files** | 15+ files, full implementation | 3 files (audit.py, exceptions.py, __init__.py) |
| **Purpose** | Full AIM system with bridge, services, config | Audit functionality only |
| **Status** | Active production | Migration subset |

**Conclusion**: Root `aim/` is the current production version. UET `aim/` contains extracted audit functionality for migration.

---

### 2. `bring_back_docs_/` - Documentation Recovery

| Aspect | Root | UET |
|--------|------|-----|
| **Files** | 11 documentation files (.md) | 1 file (hardcoded_path_indexer.py) |
| **Purpose** | Recovered documentation archives | Tool for indexing paths |
| **Status** | Historical reference | Active tool |

**Conclusion**: Different content, same folder name by coincidence. No actual overlap.

---

### 3. `config/` - Configuration Files

| Aspect | Root | UET |
|--------|------|-----|
| **Files** | 20+ config files (yaml, json, py) | 3 files (UTE_QUALITY_GATE.yaml, UTE_ai_policies.yaml, .docs_ignore) |
| **Purpose** | Pipeline-wide configuration | UET framework-specific policies |
| **Status** | Active production | Active production |

**Conclusion**: Complementary - root has pipeline config, UET has framework policies. No conflict.

---

### 4. `core/` - Core Pipeline Implementation ⚠️ PRIMARY OVERLAP

| Aspect | Root | UET |
|--------|------|-----|
| **Files** | 40+ files (17 subdirectories) | 12+ files (8 subdirectories) |
| **Purpose** | State, engine, planning, AST | Bootstrap, engine, adapters, state |
| **Status** | Current production | **Migration target** |

**Overlap Analysis**:
- Both have `core/state/` - UET has additional migration state management
- Both have `core/engine/` - UET has resilience and monitoring sub-packages
- Both have `core/adapters/` - UET version more complete
- Root has `core/planning/` - Not yet migrated to UET
- UET has `core/bootstrap/` - New functionality not in root

**Conclusion**: **Significant functional overlap** - UET `core/` is designed to replace root `core/` per migration plan.

---

### 5. `docs/` - Documentation

| Aspect | Root | UET |
|--------|------|-----|
| **Files** | 60+ documentation files | 1 folder (governance/) |
| **Purpose** | Full project documentation | Framework governance docs only |
| **Status** | Active production | Specialized subset |

**Conclusion**: UET has a minimal subset focused on governance. Not a duplication concern.

---

### 6. `error/` - Error Pipeline ⚠️ PRIMARY OVERLAP

| Aspect | Root | UET |
|--------|------|-----|
| **Files** | 30+ files (engine, plugins, shared) | 25+ files (engine, plugins, shared) |
| **Purpose** | Error detection and fixing pipeline | Same - migration target |
| **Status** | Current production | **Migration target** |

**Overlap Analysis**:
- Root `error/engine/error_engine.py`: 90 lines, full implementation
- UET `error/engine/error_engine.py`: 3 lines, compatibility shim
- Root `error/plugins/`: 23 plugin directories
- UET `error/plugins/`: 21 plugin directories (subset)
- Root `error/shared/`: Utilities
- UET `error/shared/`: Same utilities copied

**Conclusion**: **High functional overlap** - UET contains migrated versions with shims pointing back to root.

---

### 7. `gui/` - GUI Components

| Aspect | Root | UET |
|--------|------|-----|
| **Files** | TUI app, config, docs, tests | 2 demo/example files |
| **Purpose** | Full GUI/TUI application | UI infrastructure demos |
| **Status** | Active development | Example code only |

**Conclusion**: Different purposes - root is app, UET has demos. No conflict.

---

### 8. `pm/` - Project Management

| Aspect | Root | UET |
|--------|------|-----|
| **Files** | 20+ files (epics, PRDs, commands) | 2 files (github_sync.py, __init__.py) |
| **Purpose** | Full PM system with CCPM | GitHub sync tool only |
| **Status** | Active production | Extracted tool |

**Conclusion**: UET has a small subset. Root is production.

---

### 9. `schema/` - JSON Schemas

| Aspect | Root | UET |
|--------|------|-----|
| **Files** | 9 schema files (module, workstream, jobs) | 27 schema files (UET-specific) |
| **Purpose** | Pipeline data schemas | UET framework contracts |
| **Status** | Active production | Active production |

**Overlap Analysis**:
- Root: `module.schema.json`, `workstream.schema.json`, `registry_entry.schema.json`
- UET: `phase_spec.v1.json`, `execution_request.v1.json`, `project_profile.v1.json`, etc.
- **No file name overlap** - schemas are for different domains

**Conclusion**: **Complementary** - different schema domains, both needed.

---

### 10. `scripts/` - Utility Scripts

| Aspect | Root | UET |
|--------|------|-----|
| **Files** | 80+ scripts (validation, migration, analysis) | 16 scripts (migration-focused) |
| **Purpose** | General pipeline operations | UET migration tools |
| **Status** | Active production | Active production |

**Overlap Analysis**:
- Root `scripts/multi_agent_orchestrator.py`: Exact duplicate in UET
- Root `scripts/preflight_validator.py`: Exact duplicate in UET
- Root `scripts/worktree_manager.py`: Exact duplicate in UET

**Conclusion**: **3 exact duplicates** identified. These should be deduplicated.

---

### 11. `specifications/` - Spec Management

| Aspect | Root | UET |
|--------|------|-----|
| **Files** | Bridge, changes, content, tools (30+ files) | 1 tool directory, __init__.py |
| **Purpose** | Full specification system | Spec tools only |
| **Status** | Active production | Minimal subset |

**Conclusion**: UET has minimal footprint here. Not a duplication concern.

---

### 12. `templates/` - Template Files

| Aspect | Root | UET |
|--------|------|-----|
| **Files** | Migration templates, workstream templates | Execution patterns, orchestration |
| **Purpose** | Code migration templates | UET phase templates |
| **Status** | Active production | Active production |

**Overlap Analysis**:
- Root: `migrate_module.template.py`, `workstreams/`
- UET: `execution_patterns/`, `patterns/`, `orchestration/`
- **No file name overlap** - different template domains

**Conclusion**: **Complementary** - different purposes, both needed.

---

### 13. `tests/` - Test Suites

| Aspect | Root | UET |
|--------|------|-----|
| **Files** | 50+ test files (all modules) | 10 test directories (UET-specific) |
| **Purpose** | Full pipeline test coverage | UET framework tests |
| **Status** | Active production | Active production |

**Overlap Analysis**:
- Root: Tests for core, engine, error plugins, etc.
- UET: Tests for adapters, aim, bootstrap, engine, patterns, etc.
- Both have `tests/engine/` - different test files inside

**Conclusion**: **Complementary** - tests for different implementations.

---

### 14. `tools/` - Tool Utilities

| Aspect | Root | UET |
|--------|------|-----|
| **Files** | Validation, spec tools (10+ dirs) | 4 doc tools |
| **Purpose** | Pipeline development tools | Documentation tools |
| **Status** | Active production | Active production |

**Conclusion**: Different tools for different purposes. No conflict.

---

## Summary of Findings

### Overlap Categories

| Category | Folders | Action Needed |
|----------|---------|---------------|
| **Primary Migration Targets** | `core/`, `error/` | Continue per migration plan |
| **Exact Script Duplicates** | `scripts/` (3 files) | Deduplicate or symlink |
| **Complementary Schemas** | `schema/`, `templates/`, `tests/` | Keep both, different domains |
| **Different Content** | `bring_back_docs_/`, `config/`, `docs/`, `gui/`, `pm/`, `specifications/`, `tools/` | No action needed |
| **Partial Migration** | `aim/` | Complete migration per plan |

### Recommendations

1. **Follow Existing Migration Plan**: The `UET_CONSOLIDATION_MASTER_PLAN.md` already defines a 7-week migration strategy. Continue with that plan.

2. **Deduplicate Scripts** (3 files):
   - `multi_agent_orchestrator.py` - Keep in one location, symlink/import
   - `preflight_validator.py` - Keep in one location, symlink/import  
   - `worktree_manager.py` - Keep in one location, symlink/import

3. **No Folder Rename Needed**: The overlap is intentional. UET folders are migration targets.

4. **After Migration Complete**: Root folders will be archived per the plan:
   ```
   core/ → archive/2025-XX-XX_pre-consolidation/core/
   error/ → archive/2025-XX-XX_pre-consolidation/error/
   aim/ → archive/2025-XX-XX_pre-consolidation/aim/
   pm/ → archive/2025-XX-XX_pre-consolidation/pm/
   ```

---

## Conclusion

The folder naming overlap between `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK` and root directories is **intentional and planned**. The UET framework is designed as the **canonical destination** for code consolidation.

**Current State**: 67% code duplication (337 of 500 Python files)  
**Target State**: Single source of truth in UET with 60%+ file reduction  
**Existing Plan**: `UET_CONSOLIDATION_MASTER_PLAN.md` defines 16 workstreams for migration

**No immediate action required** - the migration plan addresses this systematically.

---

## References

- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/README.md` - Framework documentation
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/UET_CONSOLIDATION_MASTER_PLAN.md` - Migration plan
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/CODEBASE_INDEX.yaml` - Module registry
