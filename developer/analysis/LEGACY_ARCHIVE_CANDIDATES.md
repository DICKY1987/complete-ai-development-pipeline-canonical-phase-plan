---
doc_id: DOC-GUIDE-LEGACY-ARCHIVE-CANDIDATES-1191
---

# Legacy Archive Candidates

**Date:** 2025-11-21  
**Phase:** H3.1 - Identify Legacy/Temporary Folders  
**Status:** Complete

## Summary

Three legacy/temporary folders identified for archival:
- `build/` - Single spec documentation file (legacy)
- `bundles/` - Test workstream bundle (should be in workstreams/)
- `pipeline_plus/` - Archive of previous implementation

## Detailed Analysis

### build/

**Last Modified:** 2025-11-16  
**Git Activity:** No recent commits  
**Contents:** Single file - `spec.md` (23,684 bytes)

**Analysis:**
- Contains comprehensive AI Development Pipeline Spec Suite documentation
- 619 lines of spec documentation covering:
  - Architecture (micro-kernel + plugins)
  - Operating contracts (versioning, identity)
  - Plugin contracts and CLI surface
  - Data contracts (Doc Cards, Ledger, Registry)
  - CI/CD gates and conformance
- Appears to be generated/exported documentation
- No code dependencies

**Disposition:** ARCHIVE
- Content is valuable reference material
- Should be moved to `docs/archive/` or `Multi-Document Versioning Automation final_spec_docs/`
- No active build process references this location

### bundles/

**Last Modified:** 2025-11-18  
**Git Activity:** Recent commits (Nov 18, 2025)  
**Contents:** Single file - `openspec-test-001.yaml` (250 bytes)

**Analysis:**
- Contains test OpenSpec bundle with 3 tasks
- Bundle ID: `openspec-test-001`
- Simple test structure for validation
- Recently active (modified 3 days ago)
- Should be with other workstream bundles

**Disposition:** RELOCATE
- Move to `workstreams/examples/openspec-test-001.yaml`
- This aligns with repository structure (workstreams/ for bundles)
- Not legacy - active test file

### pipeline_plus/

**Last Modified:** 2025-11-20  
**Git Activity:** Active development through Nov 20  
**Contents:** Archive of previous pipeline implementation

**Structure:**
```
pipeline_plus/
├── _archive/               # Already archived content
│   ├── exploration/
│   ├── external_copies/
│   └── reference/
├── AGENTIC_DEV_PROTOTYPE/  # Prototype code
├── .aicontext
├── .aiderignore
├── AGENT_OPERATIONS_SPEC version1.0.0/
├── Aider-optimized" workstreams.md
├── IMPLEMENTATION_SUMMARY.md
├── Key Innovations for File Passing Between CLI Tools.md
└── workstream-style" prompt structure.md
```

**Analysis:**
- Contains previous implementation of agentic development prototype
- Has its own `_archive/` subdirectory (already self-archiving)
- Implementation summaries and design documents
- CCPM integration work (Phase 09.1-09.4)
- Recently active but appears to be winding down

**Disposition:** ARCHIVE
- Entire directory should be archived
- Contains valuable reference implementation and design decisions
- AGENTIC_DEV_PROTOTYPE is duplicated in root (need to check)

## Consolidation Decisions

### build/ → ARCHIVE

**Target:** `docs/archive/phase-h-legacy/build/`

**Rationale:**
- Single documentation file
- No active build process
- Valuable reference but not actively maintained

### bundles/ → RELOCATE

**Target:** `workstreams/examples/openspec-test-001.yaml`

**Rationale:**
- Active test file
- Belongs with other workstream bundles
- Not legacy - just misplaced

### pipeline_plus/ → ARCHIVE

**Target:** `docs/archive/phase-h-legacy/pipeline_plus/`

**Rationale:**
- Previous implementation now superseded
- Already has internal _archive/ structure
- Historical value for design decisions
- AGENTIC_DEV_PROTOTYPE in root may be duplicate

## Additional Items to Check

### Root-level markdown cleanup reports
- `CLEANUP_EXECUTION_REPORT_PHASE1.md`
- `CLEANUP_EXECUTION_REPORT_PHASE2_COMPLETE.md`
- `CLEANUP_INDEX.md`
- `CLEANUP_PROJECT_SUMMARY.md`
- `CLEANUP_REORGANIZATION_STRATEGY.md`

**Disposition:** Move to `docs/archive/cleanup-reports/`

### Root-level miscellaneous files
- `Data Flow Analysis.md`
- `apply edits without asking you every time.md`
- `first place (per-tool headless contract.md`
- `id file consolidation checker.md`
- Various .txt files

**Disposition:** Review individually, likely archive or delete

## Risk Assessment

### build/ - ARCHIVE
**Risk:** LOW
- Single documentation file
- No code dependencies
- Easy to restore if needed

### bundles/ - RELOCATE
**Risk:** VERY LOW
- Single small test file
- Clear target location
- Still active

### pipeline_plus/ - ARCHIVE
**Risk:** LOW
- Self-contained directory
- Already has archive structure
- No external dependencies identified
- Historical reference value

## File Mapping

```
build/spec.md                              → docs/archive/phase-h-legacy/build/spec.md
bundles/openspec-test-001.yaml            → workstreams/examples/openspec-test-001.yaml
pipeline_plus/                             → docs/archive/phase-h-legacy/pipeline_plus/

# Cleanup reports
CLEANUP_*.md                               → docs/archive/cleanup-reports/
```

## Next Steps (Phase H3.2)

1. Create archive directory structure
2. Move identified folders with documentation
3. Update any references (if any)
4. Commit archival with clear documentation

---

**Analysis Complete:** 2025-11-21  
**Recommendation:** Archive build/ and pipeline_plus/, relocate bundles/  
**Approved for Execution:** Yes
