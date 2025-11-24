# Deprecation & Shim Removal Plan

**Date Created**: 2025-11-19  
**Phase**: F (Post-Refactor Finalization)  
**Workstream**: WS-24  
**Status**: Active - Phase 1

---

## Overview

This document outlines the timeline and process for deprecating backward-compatibility shims created during the Phase E section-based refactor.

**Goal**: Transition all code to use new import paths while maintaining backward compatibility during a grace period.

---

## Deprecation Timeline

### Phase 1: Silent Operation (Current - 2026-02-19)
**Duration**: 3 months  
**Status**: ✅ ACTIVE  

- Shims are fully functional with no warnings
- All new code should use new paths
- Legacy code continues to work without changes
- CI enforces new paths for new PRs (WS-21)

**Actions**:
- [x] Shims created and tested (Phase E)
- [x] CI gate prevents new deprecated imports (WS-21)
- [x] Documentation updated with new paths (WS-22)
- [x] Migration guide available in README.md and ARCHITECTURE.md

### Phase 2: Soft Warnings (2026-02-19 - 2026-05-19)
**Duration**: 3 months  
**Status**: ⏸️ PENDING  

- Shims emit deprecation warnings to stderr
- Warnings can be suppressed via environment variable
- Migration tools available to automate updates
- Weekly reminders in team communications

**Actions**:
- [ ] Add deprecation warnings to all shim files
- [ ] Create `scripts/migrate_imports.py` tool
- [ ] Create `scripts/check_deprecated_usage.py` scanner
- [ ] Update test suite to handle warnings
- [ ] Announce deprecation to team
- [ ] Add migration guide to onboarding docs

### Phase 3: Loud Warnings (2026-05-19 - 2026-11-19)
**Duration**: 6 months  
**Status**: ⏸️ PENDING  

- Warnings become more prominent
- Weekly automated scans for deprecated usage
- Individual notifications to file owners
- Migration assistance available

**Actions**:
- [ ] Increase warning verbosity
- [ ] Add CI job to report deprecated usage
- [ ] Generate weekly deprecation reports
- [ ] Identify and prioritize critical files
- [ ] Provide migration assistance PRs

### Phase 4: Removal (2026-11-19+)
**Duration**: Permanent  
**Status**: ⏸️ PENDING  

- Shims completely removed
- Old import paths no longer work
- CI blocks any reintroduction
- Clean, canonical structure

**Actions**:
- [ ] Verify zero internal usage of deprecated paths
- [ ] Remove all shim files under `src/pipeline/`
- [ ] Remove all shim files under `MOD_ERROR_PIPELINE/`
- [ ] Update CI to block old import patterns permanently
- [ ] Archive shim tests
- [ ] Update version to 2.0.0
- [ ] Create release notes

---

## Affected Paths

### High Priority - Core Pipeline Shims
Located in: `src/pipeline/`

| Shim File | New Location | Category |
|-----------|--------------|----------|
| `db.py` | `core/state/db.py` | State |
| `db_sqlite.py` | `core/state/db_sqlite.py` | State |
| `crud_operations.py` | `core/state/crud.py` | State |
| `bundles.py` | `core/state/bundles.py` | State |
| `worktree.py` | `core/state/worktree.py` | State |
| `orchestrator.py` | `core/engine/orchestrator.py` | Engine |
| `scheduler.py` | `core/engine/scheduler.py` | Engine |
| `executor.py` | `core/engine/executor.py` | Engine |
| `tools.py` | `core/engine/tools.py` | Engine |
| `circuit_breakers.py` | `core/engine/circuit_breakers.py` | Engine |
| `recovery.py` | `core/engine/recovery.py` | Engine |
| `planner.py` | `core/planning/planner.py` | Planning |
| `archive.py` | `core/planning/archive.py` | Planning |
| `aim_bridge.py` | `aim/bridge.py` | AIM |

### Medium Priority - Error Pipeline Shims
Located in: `MOD_ERROR_PIPELINE/`

| Shim File | New Location | Category |
|-----------|--------------|----------|
| `file_hash_cache.py` | `error/file_hash_cache.py` | Shared |
| `plugin_manager.py` | `error/plugin_manager.py` | Plugins |
| `pipeline_engine.py` | `error/pipeline_engine.py` | Engine |

### Low Priority - Kept in Place
These files remain in original locations:

| File | Reason |
|------|--------|
| `src/pipeline/prompts.py` | Aider integration requirement |
| `src/pipeline/__init__.py` | Package marker (empty) |

---

## Migration Process

### For Internal Development

1. **Run deprecation checker**:
   ```bash
   python scripts/check_deprecated_usage.py
   ```

2. **Review report**:
   - Identify files using old imports
   - Prioritize by frequency and criticality

3. **Auto-migrate** (safe):
   ```bash
   python scripts/migrate_imports.py --check <file_or_directory>
   python scripts/migrate_imports.py --fix <file_or_directory> --dry-run
   python scripts/migrate_imports.py --fix <file_or_directory>
   ```

4. **Test changes**:
   ```bash
   pytest <affected_test_files>
   ```

5. **Commit with clear message**:
   ```bash
   git commit -m "refactor: migrate imports from src.pipeline to core.*"
   ```

### For External Users (if applicable)

1. **Check documentation**:
   - Read migration guide in README.md
   - Review ARCHITECTURE.md for new structure

2. **Use migration tool**:
   ```bash
   python scripts/migrate_imports.py --fix <your_code_directory>
   ```

3. **Suppress warnings** (temporary):
   ```bash
   export SUPPRESS_DEPRECATION_WARNINGS=1
   ```

4. **Report issues**:
   - File GitHub issue if migration tool fails
   - Request assistance for complex cases

---

## Suppressing Warnings

During Phase 2 and 3, warnings can be suppressed if needed:

### Temporary Suppression (for a single session)
```bash
export SUPPRESS_DEPRECATION_WARNINGS=1
python your_script.py
```

### Permanent Suppression (not recommended)
Add to `.env.local`:
```
SUPPRESS_DEPRECATION_WARNINGS=1
```

### Selective Suppression (Python code)
```python
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
```

**Note**: Suppressing warnings delays the inevitable migration. It's recommended to fix imports instead.

---

## Shim Removal Checklist

Before removing shims in Phase 4, verify:

### Pre-Removal Verification
- [ ] No internal code uses old imports (run `check_deprecated_usage.py`)
- [ ] All tests pass with new imports
- [ ] All scripts updated to use new paths
- [ ] All documentation references new paths only
- [ ] CI reports zero deprecated usage for 30+ days
- [ ] Team notified of upcoming removal
- [ ] Deprecation period (12+ months) completed

### Removal Steps
1. [ ] Create backup branch: `git checkout -b pre-shim-removal`
2. [ ] Remove shim files in `src/pipeline/` (except `prompts.py`, `__init__.py`)
3. [ ] Remove shim files in `MOD_ERROR_PIPELINE/`
4. [ ] Update CI workflows to permanently block old patterns
5. [ ] Remove shim-specific tests from test suite
6. [ ] Update `.gitignore` if needed
7. [ ] Run full test suite
8. [ ] Update version to 2.0.0
9. [ ] Create release notes documenting breaking changes
10. [ ] Merge to main after approval
11. [ ] Tag release: `git tag v2.0.0`
12. [ ] Announce removal in release notes

### Post-Removal Verification
- [ ] CI passes on main branch
- [ ] No import errors in production
- [ ] Documentation updated
- [ ] CHANGELOG.md includes breaking changes
- [ ] Users notified via release announcement

---

## Migration Tools

### 1. `scripts/check_deprecated_usage.py`
Scans codebase for deprecated import patterns.

**Usage**:
```bash
python scripts/check_deprecated_usage.py
python scripts/check_deprecated_usage.py --path <directory>
python scripts/check_deprecated_usage.py --json > report.json
```

**Output**:
- List of files using old imports
- Count of deprecated imports per file
- Suggested replacements
- Actionable recommendations

### 2. `scripts/migrate_imports.py`
Automatically updates imports to new paths.

**Usage**:
```bash
# Check what would change
python scripts/migrate_imports.py --check <path>

# Preview changes without writing
python scripts/migrate_imports.py --fix <path> --dry-run

# Apply changes
python scripts/migrate_imports.py --fix <path>

# Fix entire project
python scripts/migrate_imports.py --fix . --exclude tests/legacy
```

**Safety**:
- Creates backups before modification
- Dry-run mode for preview
- Excludes specified directories
- Logs all changes

---

## Import Mapping Reference

### Quick Reference Table

| Old Import | New Import |
|------------|------------|
| `from src.pipeline.db import *` | `from core.state.db import *` |
| `from src.pipeline.orchestrator import *` | `from core.engine.orchestrator import *` |
| `from src.pipeline.planner import *` | `from core.planning.planner import *` |
| `from src.pipeline.aim_bridge import *` | `from aim.bridge import *` |
| `from MOD_ERROR_PIPELINE.pipeline_engine import *` | `from error.pipeline_engine import *` |
| `from MOD_ERROR_PIPELINE.plugin_manager import *` | `from error.plugin_manager import *` |

### Complete Mapping

See [SECTION_REFACTOR_MAPPING.md](SECTION_REFACTOR_MAPPING.md) for the full old → new path mapping.

---

## Metrics & Tracking

### Current Status (Phase 1)
- **Total shim files**: 17 (src/pipeline: 14, MOD_ERROR_PIPELINE: 3)
- **Deprecated import usage**: To be measured in Phase 2
- **New import adoption**: ~95% (external code), 100% (new code via CI)

### Success Metrics
- **Phase 2 Goal**: <20% deprecated usage within 3 months
- **Phase 3 Goal**: <5% deprecated usage within 6 months
- **Phase 4 Goal**: 0% deprecated usage (shims removed)

### Tracking
- Weekly scans during Phase 2-3
- Monthly reports during Phase 1
- CI dashboard shows real-time adoption rate (WS-25)

---

## Communication Plan

### Phase 1 Announcements
- [x] Documentation updated (WS-22)
- [x] Architecture diagrams created (WS-23)
- [x] Migration guide published

### Phase 2 Announcements
- [ ] Email to team announcing deprecation warnings
- [ ] Update README.md with prominent notice
- [ ] Add banner to documentation site
- [ ] Post in team chat channels

### Phase 3 Announcements
- [ ] Monthly reminders about upcoming removal
- [ ] Individual notifications to file owners
- [ ] Update contribution guidelines

### Phase 4 Announcements
- [ ] Final warning 1 month before removal
- [ ] Release notes with breaking changes
- [ ] Post-removal announcement
- [ ] Updated version and changelog

---

## Rollback Plan

If issues arise during any phase:

### Phase 2-3: Disable Warnings
```bash
# Disable warnings globally
export SUPPRESS_DEPRECATION_WARNINGS=1

# Or revert warning commits
git revert <warning-commit-sha>
```

### Phase 4: Restore Shims
```bash
# Revert removal commit
git revert <removal-commit-sha>

# Or restore from backup branch
git checkout pre-shim-removal -- src/pipeline/
git checkout pre-shim-removal -- MOD_ERROR_PIPELINE/
```

---

## Version History

| Date | Phase | Action | Version |
|------|-------|--------|---------|
| 2025-11-19 | Phase 1 | Shims created, no warnings | 1.5.0 |
| 2026-02-19 | Phase 2 | Deprecation warnings added | 1.6.0 |
| 2026-05-19 | Phase 3 | Loud warnings enabled | 1.7.0 |
| 2026-11-19 | Phase 4 | Shims removed (target) | 2.0.0 |

---

## Related Documentation

- [SECTION_REFACTOR_MAPPING.md](SECTION_REFACTOR_MAPPING.md) - Complete path mapping
- [ARCHITECTURE.md](ARCHITECTURE.md) - New repository structure
- [README.md](../README.md) - Migration guide section
- [PHASE_F_PLAN.md](PHASE_F_PLAN.md) - Full Phase F plan
- [WS-21_COMPLETE.md](WS-21_COMPLETE.md) - CI enforcement
- [WS-22_COMPLETE.md](WS-22_COMPLETE.md) - Documentation updates

---

**Status**: Active (Phase 1)  
**Next Review**: 2026-02-19 (Phase 2 start)  
**Owner**: Development Team  
**Last Updated**: 2025-11-19
