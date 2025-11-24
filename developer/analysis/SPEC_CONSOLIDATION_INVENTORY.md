# Specification Consolidation Inventory

**Date:** 2025-11-21  
**Phase:** H1.1 - Audit Current Spec Folders  
**Status:** Complete

## Executive Summary

Three spec-related directories exist in the repository:
- `spec/` - Legacy spec tools (duplicate of `specifications/tools/`)
- `specs/` - Job schema and examples (active, needs integration)
- `specifications/` - Canonical specification management system (active)

## Detailed Inventory

### spec/ Directory

**Status:** DUPLICATE - Can be safely removed  
**Files:** 10 total (6 Python files, 4 __pycache__)  
**Last Modified:** 2025-11-19

**Contents:**
```
spec/
├── __init__.py                          (189 bytes - different from specifications/)
├── tools/
│   ├── __init__.py                      (189 bytes)
│   ├── spec_guard/
│   │   └── guard.py                     (4,665 bytes - IDENTICAL to specifications/tools/guard/guard.py)
│   ├── spec_indexer/
│   │   └── indexer.py                   (9,924 bytes - IDENTICAL to specifications/tools/indexer/indexer.py)
│   ├── spec_patcher/
│   │   └── patcher.py                   (5,005 bytes - IDENTICAL to specifications/tools/patcher/patcher.py)
│   ├── spec_renderer/
│   │   └── renderer.py                  (3,296 bytes - IDENTICAL to specifications/tools/renderer/renderer.py)
│   └── spec_resolver/
│       └── resolver.py                  (4,830 bytes - IDENTICAL to specifications/tools/resolver/resolver.py)
```

**Analysis:**
- All tool files are EXACT binary duplicates of `specifications/tools/` versions
- Only difference: folder structure (spec_*/file.py vs */file.py) and __init__.py content
- No imports found referencing `from spec.` or `import spec` in codebase
- **Disposition:** DELETE - This is a legacy duplicate

### specs/ Directory

**Status:** ACTIVE - Needs integration into specifications/  
**Files:** 5 JSON files  
**Last Modified:** 2025-11-20

**Contents:**
```
specs/
└── jobs/
    ├── job.schema.json                  (3,089 bytes - Job schema definition)
    ├── aider_job.example.json           (1,145 bytes)
    ├── codex_job.example.json           (861 bytes)
    ├── git_job.example.json             (768 bytes)
    └── tests_job.example.json           (889 bytes)
```

**Analysis:**
- Contains job schema and examples for tool execution
- Recently modified (Nov 20, 2025)
- Actively used for workstream-to-job conversion
- Schema defines standard job format for pipeline tools
- **Disposition:** INTEGRATE - Move to `specifications/schemas/jobs/` or `schema/jobs/`

### specifications/ Directory

**Status:** CANONICAL - Active and properly structured  
**Structure:**
```
specifications/
├── .index                               # Generated index
├── archive/                             # Archived specs
├── bridge/                              # OpenSpec → Workstream integration
├── changes/                             # Active OpenSpec change proposals
├── content/                             # Specification documents by domain
├── schemas/                             # Schema definitions
├── tools/                               # Processing utilities
│   ├── guard/                           # Spec validation
│   ├── indexer/                         # Index generation
│   ├── patcher/                         # Spec patching
│   ├── renderer/                        # Spec rendering
│   └── resolver/                        # Spec URI resolution
├── MIGRATION_COMPLETE.md
├── MIGRATION_REPORT.txt
└── README.md
```

**Analysis:**
- Well-structured canonical location
- Active development (per MIGRATION_COMPLETE.md)
- All tools have proper __init__.py modules
- **Disposition:** KEEP - This is the target structure

## Import Dependency Analysis

**Search Results:**
- ✅ No imports found for `from spec.` or `import spec`
- ✅ No imports found for `from specs.` or `import specs`
- ✅ All current imports use `from specifications.tools.*`

**Conclusion:** No code dependencies on `spec/` or `specs/` paths.

## Consolidation Decisions

### spec/ → DELETE
1. All files are exact duplicates of `specifications/tools/`
2. No code references this path
3. Structure is outdated (spec_*/file.py vs proper module structure)
4. **Action:** Remove entire directory after validation

### specs/ → INTEGRATE
1. Active job schema and examples
2. Recently modified (Nov 20, 2025)
3. No duplicate in specifications/
4. **Action:** Move to appropriate location

**Recommended Target Location for specs/jobs/:**

**Option A:** `specifications/schemas/jobs/` (Preferred)
- Aligns with `specifications/schemas/` for schema definitions
- Keeps job schemas with other spec-related schemas
- Clear separation of concerns

**Option B:** `schema/jobs/`
- Root `schema/` directory already exists
- Used for workstream and sidecar metadata contracts
- Job schemas are pipeline contracts

**Recommendation:** Use **Option B** - `schema/jobs/`
- Jobs are pipeline execution contracts, not specification documents
- Root `schema/` directory is the canonical location for JSON schemas per AGENTS.md
- Aligns with existing "JSON/YAML/SQL schemas that define workstream and sidecar metadata contracts"

## File Mapping for Migration

### specs/ Migration to schema/jobs/
```
specs/jobs/job.schema.json           → schema/jobs/job.schema.json
specs/jobs/aider_job.example.json    → schema/jobs/examples/aider_job.json
specs/jobs/codex_job.example.json    → schema/jobs/examples/codex_job.json
specs/jobs/git_job.example.json      → schema/jobs/examples/git_job.json
specs/jobs/tests_job.example.json    → schema/jobs/examples/tests_job.json
```

## References to Update

### Documentation
- [ ] `AGENTS.md` - Remove any references to `spec/` or `specs/`
- [ ] `docs/SECTION_REFACTOR_MAPPING.md` - Document this consolidation
- [ ] `README.md` - Update if structure is documented

### Scripts (potential references)
- [ ] Check `scripts/` for any hardcoded paths to `spec/` or `specs/`
- [ ] Update any scripts that generate or reference job schemas

### Configuration
- [ ] `.aiderignore` - Remove `spec/` if listed
- [ ] `pytest.ini` - Update if `spec/` is excluded/included

## Validation Checklist

- [x] All files inventoried
- [x] Import dependencies checked (none found)
- [x] File comparison completed (spec/ is exact duplicate)
- [x] Migration targets identified
- [x] No functional code dependencies on legacy paths

## Risk Assessment

**Risk Level:** LOW

**Justification:**
- No code imports from `spec/` or `specs/`
- All spec/ tools are exact duplicates
- specs/ contains only data files (schemas/examples)
- Clear migration path identified

## Next Steps (Phase H1.2)

1. Delete `spec/` directory and all contents
2. Move `specs/jobs/` → `schema/jobs/`
3. Create `schema/jobs/examples/` subdirectory
4. Update any script references
5. Run validation tests
6. Update documentation

---

**Inventory Complete:** 2025-11-21  
**Reviewed By:** Automated analysis  
**Approved for Consolidation:** Yes
