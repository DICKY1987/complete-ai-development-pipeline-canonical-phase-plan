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

**Estimated**: 3-4 hours | **Risk**: LOW

### Tasks
- [ ] Create `.github/workflows/path_standards.yml`
- [ ] Configure to run on every PR
- [ ] Integrate `scripts/paths_index_cli.py`
- [ ] Add checks for deprecated patterns:
  - [ ] `from src.pipeline.*` imports
  - [ ] `from MOD_ERROR_PIPELINE.*` imports
  - [ ] Hardcoded old directory names
- [ ] Configure failure conditions
- [ ] Add workflow badge to README.md
- [ ] Document violation fixes in `docs/CI_PATH_STANDARDS.md`
- [ ] Test with intentional violations

### Acceptance
```bash
# Should pass with no violations
✓ Clean PR passes checks

# Should fail with violations  
✗ PR with "from src.pipeline.db" fails
✗ PR with "MOD_ERROR_PIPELINE" reference fails
```

### Deliverables
- [ ] `.github/workflows/path_standards.yml`
- [ ] `docs/CI_PATH_STANDARDS.md`
- [ ] Updated README.md with badge

---

## 📝 WS-22: Update Core Documentation (HIGH PRIORITY)

**Estimated**: 8-10 hours | **Risk**: LOW

### Part 1: README.md (2-3 hours)
- [ ] Update "Project Structure" with new directory tree
- [ ] Add section describing each directory (core/, error/, aim/, etc.)
- [ ] Update "Quick Start" with new import examples
- [ ] Add link to SECTION_REFACTOR_MAPPING.md
- [ ] Update installation/setup instructions
- [ ] Add "Migration Guide" section

### Part 2: CLAUDE.md (2-3 hours)
- [ ] Update all file path references
- [ ] Update import examples in code snippets
- [ ] Update development workflow sections
- [ ] Update "where to find functionality" section
- [ ] Add note about backward compatibility

### Part 3: AGENTS.md (2-3 hours)
- [ ] Update repository structure guidelines
- [ ] Add section-specific coding conventions
- [ ] Update import path examples
- [ ] Update file organization rules
- [ ] Add guidance on section usage

### Part 4: ARCHITECTURE.md (2 hours)
- [ ] Rewrite for section-based organization
- [ ] Add section for each major directory
- [ ] Update dependency diagrams
- [ ] Add data flow diagrams
- [ ] Document shim layer and deprecation

### Acceptance
```bash
# Verify no outdated references (except in migration examples)
$ grep -r "src/pipeline" README.md CLAUDE.md AGENTS.md docs/ARCHITECTURE.md
$ grep -r "MOD_ERROR_PIPELINE" README.md CLAUDE.md AGENTS.md docs/ARCHITECTURE.md

# Should only appear in "old way" or "migration" contexts
```

### Deliverables
- [ ] Updated README.md
- [ ] Updated CLAUDE.md
- [ ] Updated AGENTS.md
- [ ] Updated docs/ARCHITECTURE.md
- [ ] New docs/MIGRATION_GUIDE.md

---

## 📊 WS-23: Create Architecture Diagrams (MEDIUM PRIORITY)

**Estimated**: 6-8 hours | **Risk**: LOW

### Part 1: Directory Structure (2 hours)
- [ ] Create visual tree diagram
- [ ] Show relationships between sections
- [ ] Highlight key files
- [ ] Add color coding
- [ ] Export as PNG/SVG

### Part 2: Module Dependencies (2-3 hours)
- [ ] Create dependency graph
- [ ] Show core/state → core/engine flow
- [ ] Show core → error dependencies
- [ ] Show aim → core dependencies
- [ ] Document circular dependencies if any

### Part 3: Data Flow Diagrams (2-3 hours)
- [ ] Workstream execution flow
- [ ] Error detection flow
- [ ] Database operations flow
- [ ] AIM integration flow

### Part 4: Integration Diagram (1 hour)
- [ ] Show section integration
- [ ] Highlight shim layer
- [ ] Show external integrations

### Tools to Use
- Mermaid (inline markdown diagrams)
- PlantUML (UML diagrams)
- GraphViz (dependency graphs)
- draw.io (custom diagrams)

### Deliverables
- [ ] `assets/diagrams/directory-structure.mmd` + PNG
- [ ] `assets/diagrams/module-dependencies.mmd` + PNG
- [ ] `assets/diagrams/data-flow-workstream.mmd` + PNG
- [ ] `docs/ARCHITECTURE_DIAGRAMS.md`
- [ ] Updated docs/ARCHITECTURE.md with references

---

## 🗑️ WS-24: Deprecation & Shim Removal Plan (LOW PRIORITY)

**Estimated**: 4-6 hours | **Risk**: LOW

### Part 1: Timeline (1 hour)
- [ ] Define deprecation phases:
  - [ ] Phase 1 (0-3 months): No warnings
  - [ ] Phase 2 (3-6 months): Soft warnings
  - [ ] Phase 3 (6-12 months): Loud warnings
  - [ ] Phase 4 (12+ months): Remove shims
- [ ] Set milestone dates
- [ ] Document in `docs/DEPRECATION_PLAN.md`

### Part 2: Add Warnings (2-3 hours)
- [ ] Update all shim files with deprecation warnings
- [ ] Make warnings configurable (env var)
- [ ] Add suppression guide
- [ ] Update tests to handle warnings

### Part 3: Migration Scripts (2 hours)
- [ ] Create `scripts/migrate_imports.py`:
  - [ ] Scan for old imports
  - [ ] Suggest replacements
  - [ ] Add auto-fix mode
- [ ] Create `scripts/check_deprecated_usage.py`:
  - [ ] Scan for deprecated patterns
  - [ ] Generate report
- [ ] Document in MIGRATION_GUIDE.md

### Part 4: Removal Checklist (1 hour)
- [ ] Create shim removal checklist
- [ ] Document in DEPRECATION_PLAN.md

### Acceptance
```python
# Test warnings work
import warnings
with warnings.catch_warnings(record=True) as w:
    from src.pipeline.db import init_db
    assert "deprecated" in str(w[-1].message).lower()

# Test migration script
$ python scripts/migrate_imports.py --check tests/
$ python scripts/migrate_imports.py --fix tests/ --dry-run
```

### Deliverables
- [ ] `docs/DEPRECATION_PLAN.md`
- [ ] Updated shim files with warnings
- [ ] `scripts/migrate_imports.py`
- [ ] `scripts/check_deprecated_usage.py`
- [ ] Updated docs/MIGRATION_GUIDE.md

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
- [x] Metrics tracking active (WS-25)

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
