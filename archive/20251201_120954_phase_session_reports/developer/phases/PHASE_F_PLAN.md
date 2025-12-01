---
doc_id: DOC-GUIDE-PHASE-F-PLAN-1233
---

# Phase F: Post-Refactor Finalization & Long-Term Maintenance

**Status**: Optional - Can be executed incrementally  
**Date Created**: 2025-11-19  
**Dependencies**: Phases A-E must be complete (✅ DONE)  
**Estimated Total Effort**: 24-32 hours  

---

## Overview

Phase F completes the repository refactor by:
1. Establishing CI/CD enforcement of the new structure
2. Updating all user-facing and developer documentation
3. Creating visual documentation (architecture diagrams)
4. Planning the eventual removal of backward-compatibility shims
5. Adding monitoring to prevent regressions

**All items in this phase are optional** and can be executed independently based on priority.

---

## Workstream Breakdown

### WS-21: CI Gate Path Standards ⏸️
**Priority**: HIGH  
**Estimated Effort**: 3-4 hours  
**Risk Level**: LOW  

#### Objective
Create automated CI checks to prevent introduction of deprecated path patterns and ensure new code follows section-based structure.

#### Tasks
1. Create `.github/workflows/path_standards.yml`
2. Configure workflow to run on every PR
3. Integrate `scripts/paths_index_cli.py` into CI
4. Set up checks for deprecated patterns:
   - `from src.pipeline.*` imports
   - `from MOD_ERROR_PIPELINE.*` imports
   - Hardcoded references to old directory names
5. Configure failure conditions
6. Add workflow badge to README.md
7. Document how to fix violations
8. Test with intentional violations

#### Acceptance Tests
```yaml
# .github/workflows/path_standards.yml should:
- Run on: [pull_request, push to main]
- Check for deprecated import patterns
- Check for hardcoded old paths
- Fail PR if violations found
- Generate violation report

# Test scenarios:
1. PR with no violations → PASS
2. PR with "from src.pipeline.db import" → FAIL
3. PR with "MOD_ERROR_PIPELINE" string → FAIL
```

#### Deliverables
- `.github/workflows/path_standards.yml`
- `docs/CI_PATH_STANDARDS.md` - Documentation on enforcement
- Updated README.md with workflow badge

---

### WS-22: Update Core Documentation 📝
**Priority**: HIGH  
**Estimated Effort**: 8-10 hours  
**Risk Level**: LOW  

#### Objective
Update all user-facing and developer documentation to reflect the new section-based structure.

#### Tasks

**Part 1: README.md Updates (2-3 hours)**
1. Update "Project Structure" section with new directory tree
2. Add section describing each top-level directory (core/, error/, aim/, etc.)
3. Update "Quick Start" with new import examples
4. Add link to SECTION_REFACTOR_MAPPING.md
5. Update installation/setup instructions if affected
6. Add "Migration Guide" section for existing contributors

**Part 2: CLAUDE.md Updates (2-3 hours)**
1. Update all file path references to new locations
2. Update import examples in code snippets
3. Update development workflow sections
4. Update section on where to find specific functionality
5. Add note about backward compatibility via shims

**Part 3: AGENTS.md Updates (2-3 hours)**
1. Update repository structure guidelines
2. Add section-specific coding conventions:
   - `core/state/` - Database and state management
   - `core/engine/` - Orchestration and execution
   - `core/planning/` - Planning utilities
   - `error/` - Error detection and handling
   - `aim/`, `pm/`, `spec/` - Section-specific tools
3. Update import path examples
4. Update file organization rules
5. Add guidance on when to use which section

**Part 4: ARCHITECTURE.md Updates (2 hours)**
1. Rewrite to reflect section-based organization
2. Add section on each major directory (core/, error/, etc.)
3. Update dependency diagrams if present
4. Add data flow diagrams showing interaction between sections
5. Document the shim layer and deprecation plan

#### Acceptance Tests
```bash
# All documentation should:
✓ Use new import paths (core.*, error.*)
✓ Reference new file locations
✓ Include migration guidance
✓ Have no broken internal links
✓ Be consistent with SECTION_REFACTOR_MAPPING.md

# Specific checks:
$ grep -r "src/pipeline" README.md CLAUDE.md AGENTS.md docs/ARCHITECTURE.md
# Should only find references in "migration" or "old way" examples

$ grep -r "MOD_ERROR_PIPELINE" README.md CLAUDE.md AGENTS.md docs/ARCHITECTURE.md  
# Should only find references in "migration" or "old way" examples
```

#### Deliverables
- Updated README.md
- Updated CLAUDE.md
- Updated AGENTS.md
- Updated docs/ARCHITECTURE.md
- docs/MIGRATION_GUIDE.md (new)

---

### WS-23: Create Architecture Diagrams 📊
**Priority**: MEDIUM  
**Estimated Effort**: 6-8 hours  
**Risk Level**: LOW  

#### Objective
Create visual documentation showing the new repository structure, data flows, and module dependencies.

#### Tasks

**Part 1: Directory Structure Diagram (2 hours)**
1. Create visual tree diagram of new structure
2. Show relationship between core/, error/, and other sections
3. Highlight key files in each section
4. Add color coding for different types (state, engine, plugins, etc.)
5. Export as PNG/SVG for documentation

**Part 2: Module Dependency Graph (2-3 hours)**
1. Create diagram showing dependencies between sections
2. Show core/state → core/engine dependencies
3. Show core → error dependencies
4. Show aim → core dependencies
5. Identify and document circular dependencies (if any)
6. Use tools like `pydeps` or manual creation

**Part 3: Data Flow Diagrams (2-3 hours)**
1. Workstream execution flow (user → scripts → core/engine → tools)
2. Error detection flow (code → error/plugins → error/engine)
3. Database operations (core/engine → core/state → DB)
4. AIM integration flow (core/engine → aim/bridge → external tools)

**Part 4: Integration Diagram (1 hour)**
1. Show how all sections integrate
2. Highlight the shim layer
3. Show external integrations (Aider, AIM, etc.)

#### Tools to Consider
- **Mermaid**: For inline diagrams in markdown
- **PlantUML**: For detailed UML diagrams
- **GraphViz**: For dependency graphs
- **draw.io**: For custom diagrams
- **pydeps**: For automatic Python dependency graphs

#### Acceptance Tests
```bash
# Diagrams should:
✓ Be readable at standard screen resolution
✓ Be version-controlled (source + rendered)
✓ Be referenced in documentation
✓ Accurately reflect current structure
✓ Use consistent notation/styling

# Files to create:
- assets/diagrams/directory-structure.mmd (Mermaid source)
- assets/diagrams/directory-structure.png (rendered)
- assets/diagrams/module-dependencies.mmd
- assets/diagrams/module-dependencies.png
- assets/diagrams/data-flow-workstream.mmd
- assets/diagrams/data-flow-workstream.png
```

#### Deliverables
- assets/diagrams/ directory with all diagrams
- docs/ARCHITECTURE_DIAGRAMS.md explaining each diagram
- Updated docs/ARCHITECTURE.md with diagram references
- Mermaid source files for future maintenance

---

### WS-24: Deprecation & Shim Removal Plan 🗑️
**Priority**: LOW  
**Estimated Effort**: 4-6 hours  
**Risk Level**: LOW  

#### Objective
Create a concrete plan for deprecating and eventually removing backward-compatibility shims.

#### Tasks

**Part 1: Deprecation Timeline (1 hour)**
1. Define deprecation periods:
   - Phase 1 (0-3 months): Shims active, no warnings
   - Phase 2 (3-6 months): Shims active, deprecation warnings added
   - Phase 3 (6-12 months): Shims active, loud warnings
   - Phase 4 (12+ months): Shims removed
2. Document timeline in DEPRECATION_PLAN.md
3. Set specific milestone dates

**Part 2: Add Deprecation Warnings (2-3 hours)**
1. Update all shim files to include deprecation warnings:
   ```python
   import warnings
   warnings.warn(
       "Importing from src.pipeline.db is deprecated. "
       "Use 'from core.state.db import *' instead. "
       "This shim will be removed in version X.X.X",
       DeprecationWarning,
       stacklevel=2
   )
   from core.state.db import *
   ```
2. Make warnings configurable (environment variable)
3. Add warning suppression guide for users
4. Update tests to handle deprecation warnings

**Part 3: Migration Scripts (2 hours)**
1. Create `scripts/migrate_imports.py` to automate import updates:
   - Scan Python files for old imports
   - Suggest replacements
   - Optional: auto-fix mode
2. Create `scripts/check_deprecated_usage.py`:
   - Scan codebase for deprecated patterns
   - Generate report of files needing updates
3. Document usage in MIGRATION_GUIDE.md

**Part 4: Removal Checklist (1 hour)**
1. Create checklist for shim removal:
   - [ ] Verify no internal code uses old imports
   - [ ] Verify all tests use new imports
   - [ ] Verify all documentation uses new imports
   - [ ] Announce deprecation to users
   - [ ] Wait for deprecation period
   - [ ] Remove shim files
   - [ ] Update CI to block old patterns
   - [ ] Remove shim tests
2. Document in DEPRECATION_PLAN.md

#### Acceptance Tests
```python
# Test deprecation warnings work:
import warnings
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    from src.pipeline.db import init_db
    assert len(w) == 1
    assert issubclass(w[-1].category, DeprecationWarning)
    assert "deprecated" in str(w[-1].message).lower()

# Test migration script:
$ python scripts/migrate_imports.py --check tests/
# Should detect old import patterns

$ python scripts/migrate_imports.py --fix tests/ --dry-run
# Should show what would be changed
```

#### Deliverables
- docs/DEPRECATION_PLAN.md
- Updated shim files with warnings
- scripts/migrate_imports.py
- scripts/check_deprecated_usage.py
- Updated docs/MIGRATION_GUIDE.md

---

### WS-25: Add Monitoring & Metrics 📈
**Priority**: LOW  
**Estimated Effort**: 3-4 hours  
**Risk Level**: LOW  

#### Objective
Add monitoring to track adoption of new structure and identify areas still using deprecated patterns.

#### Tasks

**Part 1: Usage Metrics Script (2 hours)**
1. Create `scripts/analyze_import_patterns.py`:
   - Scan codebase for import patterns
   - Count usage of new vs old imports
   - Generate adoption percentage report
   - Identify files still using old patterns
2. Output formats: JSON, markdown table, CSV

**Part 2: CI Integration (1 hour)**
1. Add metric collection to CI workflow
2. Track metrics over time (store in repo or external)
3. Add trend visualization (optional)
4. Set thresholds for warnings (e.g., "less than 90% adoption")

**Part 3: Dashboard/Report (1 hour)**
1. Create `docs/REFACTOR_METRICS.md`
2. Auto-generate adoption metrics
3. Show trends over time
4. Highlight areas needing attention

#### Acceptance Tests
```bash
# Metrics script should:
$ python scripts/analyze_import_patterns.py
✓ Output adoption percentage
✓ List files using old patterns
✓ Provide actionable recommendations

# Sample output:
Import Pattern Adoption Report
==============================
New patterns (core.*, error.*): 95.2%
Old patterns (src.pipeline.*): 3.1%
Old patterns (MOD_ERROR_PIPELINE.*): 1.7%

Files needing migration:
- tests/legacy/old_test.py (3 old imports)
- scripts/legacy_tool.py (2 old imports)
```

#### Deliverables
- scripts/analyze_import_patterns.py
- .github/workflows/track_metrics.yml (optional)
- docs/REFACTOR_METRICS.md

---

## Execution Strategy

### Recommended Order

1. **WS-21 (CI Gate)** - Prevent regressions immediately
2. **WS-22 (Documentation)** - Help developers understand new structure
3. **WS-23 (Diagrams)** - Visual aids for onboarding
4. **WS-24 (Deprecation Plan)** - Set timeline for shim removal
5. **WS-25 (Monitoring)** - Track ongoing compliance

### Parallel Execution Opportunities

- WS-22 and WS-23 can be done in parallel (different team members)
- WS-24 and WS-25 can be done in parallel
- WS-21 should be done first to prevent new issues

### Incremental Approach

**Week 1-2**: WS-21 (CI enforcement)  
**Week 3-4**: WS-22 (documentation updates)  
**Week 5-6**: WS-23 (create diagrams)  
**Week 7**: WS-24 (deprecation planning)  
**Week 8**: WS-25 (monitoring setup)

Or tackle one workstream per sprint as time allows.

---

## Success Criteria

Phase F is considered complete when:

✅ CI automatically prevents deprecated patterns (WS-21)  
✅ All core documentation reflects new structure (WS-22)  
✅ Architecture diagrams exist and are referenced (WS-23)  
✅ Deprecation timeline is documented and warnings active (WS-24)  
✅ Metrics dashboard shows adoption trends (WS-25)  

---

## Risk Assessment

### Overall Risk: LOW

All items in Phase F are:
- Documentation and tooling improvements
- Non-breaking changes
- Can be rolled back easily if needed
- Do not affect runtime behavior

### Potential Issues

1. **Stale documentation** - Mitigated by making updates atomic
2. **CI false positives** - Mitigated by thorough testing of patterns
3. **Deprecation confusion** - Mitigated by clear migration guides

---

## Maintenance Plan

After Phase F completion:

### Quarterly Reviews
- Check metric trends (are old imports decreasing?)
- Update diagrams if structure changes
- Review deprecation timeline progress

### Annual Tasks
- Evaluate shim removal (after 12 months)
- Archive old documentation versions
- Update architecture diagrams for major changes

### Ongoing
- Keep CI checks updated with new patterns
- Update documentation for new features
- Monitor metrics dashboard

---

## Resources Required

### Tools
- GitHub Actions (CI)
- Diagram tools (Mermaid, PlantUML, or draw.io)
- Python scripting (deprecation warnings, metrics)

### Time Commitment
- **Minimum viable**: 10-12 hours (WS-21 + WS-22 partial)
- **Recommended**: 20-24 hours (WS-21 + WS-22 + WS-24)
- **Complete**: 24-32 hours (all workstreams)

### Skills Needed
- YAML (GitHub Actions)
- Python (scripting)
- Technical writing (documentation)
- Diagramming (architecture visuals)

---

## Optional Enhancements

### Beyond Phase F

1. **Automated Code Migration**
   - Create codemod scripts for automatic migration
   - Integrate with IDE plugins

2. **Performance Benchmarking**
   - Measure import overhead of shim layer
   - Benchmark before/after shim removal

3. **Training Materials**
   - Create onboarding video for new structure
   - Interactive tutorial for section-based development

4. **Tooling Improvements**
   - IDE plugins for quick navigation
   - Code snippets for common patterns

---

## Appendix: Template Files

### A. CI Workflow Template

```yaml
# .github/workflows/path_standards.yml
name: Path Standards Check

on:
  pull_request:
  push:
    branches: [main]

jobs:
  check-paths:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Check for deprecated import patterns
        run: |
          python scripts/check_deprecated_usage.py --strict
      
      - name: Scan for hardcoded old paths
        run: |
          python scripts/paths_index_cli.py scan --fail-on-deprecated
```

### B. Deprecation Warning Template

```python
# Shim file with deprecation warning
"""
DEPRECATED: This module has been moved.

Old location: src.pipeline.db
New location: core.state.db

This compatibility shim will be removed in version 2.0.0 (Target: 2026-06-01)

Please update your imports:
    from core.state.db import init_db
"""

import warnings
import os

# Allow disabling warnings via environment variable
if os.environ.get("SUPPRESS_DEPRECATION_WARNINGS") != "1":
    warnings.warn(
        "Importing from 'src.pipeline.db' is deprecated. "
        "Use 'from core.state.db import *' instead. "
        "This shim will be removed in version 2.0.0. "
        "See docs/MIGRATION_GUIDE.md for details.",
        DeprecationWarning,
        stacklevel=2
    )

from core.state.db import *  # noqa: F401, F403
```

### C. Metrics Report Template

```markdown
# Import Pattern Adoption Report

**Generated**: 2025-11-19  
**Codebase**: Complete AI Development Pipeline

## Summary

| Metric | Value | Target |
|--------|-------|--------|
| New pattern adoption | 95.2% | 100% |
| Files using old patterns | 4 | 0 |
| Test coverage | 98.5% | 95%+ |

## Trends

- Week 1: 85% adoption
- Week 2: 89% adoption
- Week 3: 92% adoption
- Week 4: 95.2% adoption ⬆️

## Files Needing Migration

1. `tests/legacy/old_integration_test.py` (3 old imports)
2. `scripts/legacy_analyzer.py` (2 old imports)

## Recommendations

- Update remaining 4 files in next sprint
- On track to remove shims in 6 months
```

---

**Phase F Status**: Ready for execution  
**Next Action**: Choose priority workstream and begin implementation  
**Estimated Completion**: 4-8 weeks (depending on pace)

---

*This phase plan can be executed incrementally. Start with high-priority items (WS-21, WS-22) and add others as resources permit.*
