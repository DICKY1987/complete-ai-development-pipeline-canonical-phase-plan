---
doc_id: DOC-GUIDE-CHECKLIST-1281
---

# Phase F Checklist - Post-Refactor Finalization

Quick reference checklist for completing Phase F optional tasks.

**Date Created**: 2025-11-19  
**Status**: Optional workstreams  
**Full Plan**: See [docs/PHASE_F_PLAN.md](PHASE_F_PLAN.md)

---

## 🎯 Quick Start

**Recommended order**: Complete WS-21 first, then choose others based on priority.

**Minimum viable**: WS-21 + partial WS-22 (10-12 hours)  
**Recommended**: WS-21 + WS-22 + WS-24 (20-24 hours)  
**Complete**: All workstreams (24-32 hours)

---

## ✅ WS-21: CI Gate Path Standards (HIGH PRIORITY)

**Estimated**: 3-4 hours | **Risk**: LOW | **Status**: ✅ COMPLETE

### Tasks
- [x] Create `.github/workflows/path_standards.yml`
- [x] Configure to run on every PR
- [x] Integrate `scripts/paths_index_cli.py`
- [x] Add checks for deprecated patterns:
  - [x] `from src.pipeline.*` imports
  - [x] `from MOD_ERROR_PIPELINE.*` imports
- [x] Configure failure conditions
- [x] Add workflow badge to README.md
- [x] Document violation fixes in `docs/CI_PATH_STANDARDS.md`
- [x] Test with intentional violations

### Acceptance
```bash
# ✅ Clean PR passes checks
✓ Clean PR with correct imports passes

# ✅ Violations are detected  
✓ PR with "src.pipeline.*" imports fails
✓ PR with "MOD_ERROR_PIPELINE.*" imports fails
```

### Deliverables
- [x] `.github/workflows/path_standards.yml`
- [x] `docs/CI_PATH_STANDARDS.md`
- [x] Updated README.md with badge
- [x] `tests/test_ci_path_standards.py` (example of correct imports)

---

## 📝 WS-22: Update Core Documentation (HIGH PRIORITY)

**Estimated**: 8-10 hours | **Risk**: LOW | **Status**: ✅ COMPLETE

### Part 1: README.md (2-3 hours)
- [x] Update "Project Structure" with new directory tree
- [x] Add section describing each directory (core/, error/, aim/, etc.)
- [x] Update "Quick Start" with new import examples
- [x] Add link to SECTION_REFACTOR_MAPPING.md
- [x] Update installation/setup instructions
- [x] Add "Migration Guide" section

### Part 2: CLAUDE.md (2-3 hours)
- [x] Update all file path references
- [x] Update import examples in code snippets
- [x] Update development workflow sections
- [x] Update "where to find functionality" section
- [x] Add note about backward compatibility

### Part 3: AGENTS.md (2-3 hours)
- [x] Update repository structure guidelines
- [x] Add section-specific coding conventions
- [x] Update import path examples
- [x] Update file organization rules
- [x] Add guidance on section usage

### Part 4: ARCHITECTURE.md (2 hours)
- [x] Rewrite for section-based organization
- [x] Add section for each major directory
- [x] Update dependency diagrams
- [x] Add data flow diagrams
- [x] Document shim layer and deprecation

### Acceptance
```bash
# ✅ Verified - outdated references only in migration examples
✓ README.md references old paths only in Migration Guide
✓ CLAUDE.md references old paths only in Phase E Refactor section
✓ AGENTS.md references old paths only in deprecated warnings
✓ ARCHITECTURE.md references old paths only in shim/migration sections
```

### Deliverables
- [x] Updated README.md
- [x] Updated CLAUDE.md
- [x] Updated AGENTS.md
- [x] Updated docs/ARCHITECTURE.md
- [x] Migration guidance integrated into README.md and ARCHITECTURE.md

---

## 📊 WS-23: Create Architecture Diagrams (MEDIUM PRIORITY)

**Estimated**: 6-8 hours | **Risk**: LOW | **Status**: ✅ COMPLETE

### Part 1: Directory Structure (2 hours)
- [x] Create visual tree diagram
- [x] Show relationships between sections
- [x] Highlight key files
- [x] Add color coding
- [x] Export as PNG/SVG (Mermaid source provided)

### Part 2: Module Dependencies (2-3 hours)
- [x] Create dependency graph
- [x] Show core/state → core/engine flow
- [x] Show core → error dependencies
- [x] Show aim → core dependencies
- [x] Document circular dependencies if any

### Part 3: Data Flow Diagrams (2-3 hours)
- [x] Workstream execution flow
- [x] Error detection flow
- [x] Database operations flow
- [x] AIM integration flow

### Part 4: Integration Diagram (1 hour)
- [x] Show section integration
- [x] Highlight shim layer
- [x] Show external integrations

### Tools Used
- ✅ Mermaid (inline markdown diagrams)

### Deliverables
- [x] `assets/diagrams/directory-structure.mmd`
- [x] `assets/diagrams/module-dependencies.mmd`
- [x] `assets/diagrams/data-flow-workstream.mmd`
- [x] `assets/diagrams/data-flow-error-detection.mmd`
- [x] `assets/diagrams/data-flow-database.mmd`
- [x] `assets/diagrams/data-flow-aim-integration.mmd`
- [x] `assets/diagrams/integration-overview.mmd`
- [x] `docs/ARCHITECTURE_DIAGRAMS.md`
- [x] Updated docs/ARCHITECTURE.md with references

---

## 🗑️ WS-24: Deprecation & Shim Removal Plan (LOW PRIORITY)

**Estimated**: 4-6 hours | **Risk**: LOW | **Status**: ✅ COMPLETE

### Part 1: Timeline (1 hour)
- [x] Define deprecation phases:
  - [x] Phase 1 (0-3 months): No warnings
  - [x] Phase 2 (3-6 months): Soft warnings
  - [x] Phase 3 (6-12 months): Loud warnings
  - [x] Phase 4 (12+ months): Remove shims
- [x] Set milestone dates
- [x] Document in `docs/DEPRECATION_PLAN.md`

### Part 2: Add Warnings (2-3 hours)
- [x] Document deprecation warning template
- [x] Make warnings configurable (env var)
- [x] Add suppression guide
- [x] Document test handling (ready for Phase 2)

### Part 3: Migration Scripts (2 hours)
- [x] Create `scripts/migrate_imports.py`:
  - [x] Scan for old imports
  - [x] Suggest replacements
  - [x] Add auto-fix mode
- [x] Create `scripts/check_deprecated_usage.py`:
  - [x] Scan for deprecated patterns
  - [x] Generate report
- [x] Document in DEPRECATION_PLAN.md

### Part 4: Removal Checklist (1 hour)
- [x] Create shim removal checklist
- [x] Document in DEPRECATION_PLAN.md

### Acceptance
```python
# Test migration tools work
$ python scripts/check_deprecated_usage.py --path .
✓ Only 1 false positive found (comment in aider/engine.py)

$ python scripts/migrate_imports.py --check tests/
✓ Script works correctly

$ python scripts/migrate_imports.py --fix error/engine/error_pipeline_service.py
✓ Successfully migrated deprecated import
```

### Deliverables
- [x] `docs/DEPRECATION_PLAN.md`
- [x] Deprecation warning template in DEPRECATION_PLAN.md
- [x] `scripts/migrate_imports.py`
- [x] `scripts/check_deprecated_usage.py`
- [x] Migration guide integrated into DEPRECATION_PLAN.md

---

## 📈 WS-25: Add Monitoring & Metrics (LOW PRIORITY)

**Estimated**: 3-4 hours | **Risk**: LOW

### Part 1: Metrics Script (2 hours)
- [ ] Create `scripts/analyze_import_patterns.py`:
  - [ ] Scan for import patterns
  - [ ] Count new vs old imports
  - [ ] Generate adoption report
  - [ ] Identify files with old patterns
- [ ] Support JSON, markdown, CSV output

### Part 2: CI Integration (1 hour)
- [ ] Add metric collection to workflow
- [ ] Track metrics over time
- [ ] Add trend visualization (optional)
- [ ] Set warning thresholds

### Part 3: Dashboard (1 hour)
- [ ] Create `docs/REFACTOR_METRICS.md`
- [ ] Auto-generate metrics
- [ ] Show trends
- [ ] Highlight action items

### Acceptance
```bash
$ python scripts/analyze_import_patterns.py

Expected output:
- Adoption percentage (e.g., 95.2%)
- Files using old patterns
- Actionable recommendations
```

### Deliverables
- [ ] `scripts/analyze_import_patterns.py`
- [ ] `.github/workflows/track_metrics.yml` (optional)
- [ ] `docs/REFACTOR_METRICS.md`

---

## 📅 Recommended Timeline

### Week 1-2
- [ ] Complete WS-21 (CI Gate)
- [ ] Prevents new regressions immediately

### Week 3-4
- [ ] Complete WS-22 (Documentation)
- [ ] Helps team understand new structure

### Week 5-6
- [ ] Complete WS-23 (Diagrams)
- [ ] Visual aids for onboarding

### Week 7
- [ ] Complete WS-24 (Deprecation Plan)
- [ ] Sets clear timeline

### Week 8
- [ ] Complete WS-25 (Monitoring)
- [ ] Tracks ongoing compliance

**Alternative**: One workstream per sprint at your own pace.

---

## ✅ Success Criteria

Phase F complete when:

- [x] CI prevents deprecated patterns (WS-21)
- [x] All docs reflect new structure (WS-22)
- [x] Architecture diagrams exist (WS-23)
- [x] Deprecation timeline set (WS-24)
- [ ] Metrics tracking active (WS-25)

---

## 🚀 Getting Started

1. **Choose your priority**:
   - Need to prevent regressions? → Start with WS-21
   - Need to onboard new developers? → Start with WS-22
   - Planning for future? → Start with WS-24

2. **Read the full plan**: [docs/PHASE_F_PLAN.md](PHASE_F_PLAN.md)

3. **Track progress**: Use this checklist as you go

4. **Update documentation**: Mark items complete as you finish

---

## 📚 Resources

- **Full Phase F Plan**: [docs/PHASE_F_PLAN.md](PHASE_F_PLAN.md)
- **Refactor Mapping**: [docs/SECTION_REFACTOR_MAPPING.md](SECTION_REFACTOR_MAPPING.md)
- **Verification Log**: [docs/SECTION_REFACTOR_VERIFICATION.md](SECTION_REFACTOR_VERIFICATION.md)
- **Completion Summary**: [PHASE_E_COMPLETE.md](../PHASE_E_COMPLETE.md)

---

**Last Updated**: 2025-11-19  
**Status**: Ready to begin  
**Next Action**: Choose first workstream and start!
