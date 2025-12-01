---
doc_id: DOC-GUIDE-PROJECT-DEVELOPER-ARCHIVE-2025-11-PHASE-1583
---

# Phase H Legacy Archive

**Date:** 2025-11-21  
**Archived By:** Phase H3 Directory Consolidation

## What Was Archived

This directory contains legacy folders and files from the repository consolidation effort (Phase H3).

### build/

**Original Location:** `/build/`  
**Archived:** 2025-11-21  
**Reason:** Single generated specification document; no active build process

**Contents:**
- `spec.md` - Comprehensive AI Development Pipeline Spec Suite (23,684 bytes)
  - Micro-kernel + plugins architecture
  - Operating contracts and versioning
  - Plugin contracts and data schemas
  - CI/CD gates and conformance testing

**Why Archived:**
- No active build process references this location
- Documentation appears to be generated/exported
- Content duplicates or supersedes existing specs in `specifications/` and `Multi-Document Versioning Automation final_spec_docs/`
- Historical value as design reference

### pipeline_plus/

**Original Location:** `/pipeline_plus/`  
**Archived:** 2025-11-21  
**Reason:** Previous implementation superseded by current core/ structure

**Contents:**
- `_archive/` - Pre-existing archive subdirectory with exploration and reference materials
- `AGENTIC_DEV_PROTOTYPE/` - Prototype agentic development system
- `AGENT_OPERATIONS_SPEC version1.0.0/` - Agent operation specifications
- `IMPLEMENTATION_SUMMARY.md` - Implementation notes
- Various design documents and prompt templates

**Why Archived:**
- Previous pipeline implementation now superseded by refactored `core/` structure
- Contains valuable design decisions and prototype code for reference
- Was actively developed through Nov 2025 but superseded by Phase E+ refactoring
- Already had internal `_archive/` structure indicating sunset

**Historical Context:**
- Part of CCPM integration work (Phase 09.1-09.4)
- Agentic development prototype exploration
- Pre-refactor pipeline architecture

## What Was NOT Archived (Relocated)

### bundles/openspec-test-001.yaml

**Relocated To:** `/workstreams/examples/openspec-test-001.yaml`  
**Reason:** Active test file belongs with other workstream bundles, not archived

## Related Documentation

See also:
- `/docs/archive/cleanup-reports/` - Cleanup execution reports from previous phases
- `/docs/LEGACY_ARCHIVE_CANDIDATES.md` - Full analysis of archival candidates
- `/docs/PHASE_H_DIRECTORY_CONSOLIDATION_PLAN.md` - Overall consolidation plan

## Restoration

If any archived content needs to be restored:

```bash
# Restore build/
cp -r docs/archive/phase-h-legacy/build ./build

# Restore pipeline_plus/
cp -r docs/archive/phase-h-legacy/pipeline_plus ./pipeline_plus
```

## Archival Metadata

- **Phase:** H3 - Legacy Archive
- **Date:** 2025-11-21
- **Commit:** (see git log for this file)
- **Approved By:** Automated consolidation process
- **Review Period:** 90 days (until 2026-02-19)
- **Purge Eligibility:** After review period if no restoration requests

---

**Archive Complete:** 2025-11-21  
**Next Review:** 2026-02-19
