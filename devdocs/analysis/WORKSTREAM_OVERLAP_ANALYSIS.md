# Workstream File Scope Overlap Analysis

**Date:** 2025-11-23  
**Issue:** Multiple workstreams claim the same files in their `files_scope`  
**Impact:** Medium - Can cause conflicts during parallel execution  
**Status:** Analysis complete, resolution plan ready

---

## Detected Overlaps

### 1. README.md
**Conflicting workstreams:**
- `ws-20-final-documentation-mapping`
- `ws-test-001`

**Recommendation:** `ws-test-001` should not modify README.md (test workstream). Remove from ws-test-001.

---

### 2. config/router.config.yaml
**Conflicting workstreams:**
- `ws-22-pipeline-plus-phase0-schema`
- `ws-29-pipeline-plus-phase6-router`

**Recommendation:** Split scope:
- ws-22: Schema validation only (read-only)
- ws-29: Router configuration (write)

---

### 3. docs/ (directory)
**Conflicting workstreams:**
- `ws-01-hardcoded-path-index`
- `ws-03-refactor-meta-section`

**Recommendation:** Narrow scope:
- ws-01: `docs/HARDCODED_PATH_INDEX.md` only
- ws-03: `docs/meta/` subdirectory only

---

### 4. docs/PHASE_PLAN.md
**Conflicting workstreams:**
- `ws-12-error-shared-utils`
- `ws-20-final-documentation-mapping`

**Recommendation:** Sequential dependency:
- ws-12 should complete first (creates/updates)
- ws-20 depends on ws-12 (final mapping)

---

### 5. docs/ccpm-openspec-workflow.md
**Conflicting workstreams:**
- `ws-10-openspec-integration`
- `ws-20-final-documentation-mapping`

**Recommendation:** Sequential dependency:
- ws-10 creates the file
- ws-20 depends on ws-10 (adds to index)

---

### 6. pytest.ini
**Conflicting workstreams:**
- `ws-05-refactor-infra-ci`
- `ws-19-test-suite-updates`

**Recommendation:** Sequential dependency:
- ws-05 completes first (infra setup)
- ws-19 depends on ws-05 (test configuration)

---

### 7. scripts/check-path-standards.sh
**Conflicting workstreams:**
- `ws-18-update-infrastructure-scripts`
- `ws-21-ci-gate-path-standards`

**Recommendation:** Sequential dependency:
- ws-18 creates/updates scripts
- ws-21 depends on ws-18 (integrates into CI)

---

### 8. scripts/fix-path-standards.sh
**Conflicting workstreams:**
- `ws-18-update-infrastructure-scripts`
- `ws-21-ci-gate-path-standards`

**Recommendation:** Sequential dependency:
- ws-18 creates/updates scripts
- ws-21 depends on ws-18 (integrates into CI)

---

### 9. scripts/generate_workstreams_from_openspec.py
**Conflicting workstreams:**
- `ws-10-openspec-integration`
- `ws-18-update-infrastructure-scripts`

**Recommendation:** Sequential dependency:
- ws-10 creates the script
- ws-18 depends on ws-10 (updates/refactors)

---

### 10. scripts/paths_index_cli.py
**Conflicting workstreams:**
- `ws-18-update-infrastructure-scripts`
- `ws-21-ci-gate-path-standards`

**Recommendation:** Sequential dependency:
- ws-18 creates/updates
- ws-21 depends on ws-18 (uses in CI)

---

### 11. scripts/run_error_engine.py
**Conflicting workstreams:**
- `ws-12-error-shared-utils`
- `ws-18-update-infrastructure-scripts`

**Recommendation:** Sequential dependency:
- ws-12 creates error utilities
- ws-18 depends on ws-12 (infrastructure integration)

---

### 12. scripts/run_workstream.py
**Conflicting workstreams:**
- `ws-18-update-infrastructure-scripts`
- `ws-30-pipeline-plus-phase7-integration`

**Recommendation:** Sequential dependency:
- ws-18 creates/updates base script
- ws-30 depends on ws-18 (final integration)

---

## Resolution Strategy

### Category A: Remove from Test Workstreams (1 overlap)
- **ws-test-001**: Remove `README.md` from files_scope

### Category B: Narrow Scope with Specific Paths (2 overlaps)
- **ws-01**: Change `docs/` → `docs/HARDCODED_PATH_INDEX.md`
- **ws-03**: Change `docs/` → `docs/meta/`
- **ws-22**: Add `"read_only": true` metadata for router config

### Category C: Add Dependency Relationships (9 overlaps)
Add `depends_on` to enforce sequential execution:

```json
{
  "ws-19": ["ws-05"],
  "ws-20": ["ws-10", "ws-12"],
  "ws-21": ["ws-18"],
  "ws-18": ["ws-10", "ws-12"],
  "ws-30": ["ws-18"]
}
```

---

## Implementation Plan

### Step 1: Update files_scope (Category A & B)
- Edit `ws-test-001.json` - remove README.md
- Edit `ws-01-hardcoded-path-index.json` - narrow to specific file
- Edit `ws-03-refactor-meta-section.json` - narrow to subdirectory

### Step 2: Add dependencies (Category C)
- Edit 5 workstream files to add `depends_on` fields

### Step 3: Validate
```bash
python scripts/validate_workstreams.py
```

Expected: No overlaps detected

---

## Validation Command

```bash
# Before fixes
python scripts/validate_workstreams.py
# Expected: ERROR with 12 overlapping file scopes

# After fixes
python scripts/validate_workstreams.py
# Expected: Bundles: 45; no cycles; no overlaps detected.
```

---

## Risk Assessment

**Risk Level:** LOW
- Changes are additive (adding dependencies)
- Scope narrowing prevents conflicts
- No code changes required
- Validation ensures correctness

**Testing:**
- Workstream validation passes
- Dependency graph remains acyclic
- No breaking changes to existing workstreams

---

## Timeline

- **Analysis:** ✅ Complete
- **Implementation:** 15 minutes (8 file edits)
- **Validation:** 2 minutes
- **Total:** ~20 minutes

---

## Files to Edit

1. `workstreams/ws-test-001.json`
2. `workstreams/ws-01-hardcoded-path-index.json`
3. `workstreams/ws-03-refactor-meta-section.json`
4. `workstreams/ws-19-test-suite-updates.json`
5. `workstreams/ws-20-final-documentation-mapping.json`
6. `workstreams/ws-21-ci-gate-path-standards.json`
7. `workstreams/ws-18-update-infrastructure-scripts.json`
8. `workstreams/ws-30-pipeline-plus-phase7-integration.json`

---

**Next Step:** Begin implementation with Step 1 (files_scope updates)
