# GitHub Integration v2 - File Inventory

**Generated**: 2025-12-04
**Status**: All files consolidated under `.github/github_integration_v2/`

## Directory Structure

```
.github/github_integration_v2/
├── README.md                                              (New - Overview)
├── GITHUB_INTEGRATION_V2_COMPLETE.md                     (Completion report)
├── FILE_INVENTORY.md                                      (This file)
│
├── executors/
│   ├── phase_sync.py                                      (485 LOC - Core GraphQL executor)
│   └── README.md                                          (Executor documentation)
│
├── scripts/
│   ├── splinter_sync_phase_to_github.py                  (195 LOC - CLI sync tool)
│   ├── gh_issue_update.py                                (Issue update utility)
│   └── gh_epic_sync.py                                    (Epic sync utility)
│
├── specs/
│   ├── GH_SYNC_PHASE_V1.pattern.yaml                     (Pattern specification)
│   ├── PAT-EXEC-GHPROJECT-PHASE-PLAN-SYNC-V1.md         (Phase plan sync pattern)
│   └── PAT-EXEC-GHPROJECT-PHASE-STATUS-SYNC-V1.md       (Phase status sync pattern)
│
├── tests/
│   ├── GH_SYNC_PHASE_V1_test.py                          (Unit tests - 8 tests ✓)
│   ├── test_github_sync.py                               (Integration tests)
│   ├── test_github_sync_cli_path.py                      (CLI path tests)
│   └── test_orchestrator_lifecycle_sync.py               (Orchestrator lifecycle tests)
│
└── docs/
    ├── EXAMPLE.md                                         (End-to-end example walkthrough)
    ├── README_GITHUB_PROJECT_INTEGRATION.md              (Integration README)
    └── MASTER_SPLINTER_GITHUB_ADD_ON.md                  (Full integration guide)
```

## Files by Category

### Core Implementation (3 files)
- `executors/phase_sync.py` - GraphQL executor with full Projects v2 support
- `scripts/splinter_sync_phase_to_github.py` - CLI tool with dry-run mode
- `scripts/gh_issue_update.py` - Issue update utility

### Pattern Specifications (3 files)
- `specs/GH_SYNC_PHASE_V1.pattern.yaml` - Main pattern spec
- `specs/PAT-EXEC-GHPROJECT-PHASE-PLAN-SYNC-V1.md` - Phase plan sync
- `specs/PAT-EXEC-GHPROJECT-PHASE-STATUS-SYNC-V1.md` - Phase status sync

### Tests (4 files)
- `tests/GH_SYNC_PHASE_V1_test.py` - 8 unit tests (all passing)
- `tests/test_github_sync.py` - Integration tests
- `tests/test_github_sync_cli_path.py` - CLI path tests
- `tests/test_orchestrator_lifecycle_sync.py` - Lifecycle tests

### Documentation (5 files)
- `README.md` - Quick start and overview
- `GITHUB_INTEGRATION_V2_COMPLETE.md` - Completion report
- `docs/EXAMPLE.md` - Example walkthrough
- `docs/README_GITHUB_PROJECT_INTEGRATION.md` - Integration docs
- `docs/MASTER_SPLINTER_GITHUB_ADD_ON.md` - Full guide
- `executors/README.md` - Executor documentation

### Supporting Files (1 file)
- `scripts/gh_epic_sync.py` - Epic sync utility

## Total Files: 17

## Related Files (External)

### GitHub Actions Workflows
- `.github/workflows/splinter_phase_sync.yml` - Auto-sync workflow
- `.github/workflows/project_item_sync.yml` - Project item sync workflow

### Legacy/Archive (Not moved)
- `_ARCHIVE/modules_legacy_m-prefix_implementation/pm-integrations/m01001F_github_sync.py`
- `phase1_planning/modules/workstream_planner/docs/plans/pm/github_sync.py`

## Migration Notes

All active GitHub Integration v2 files have been consolidated into `.github/github_integration_v2/`.

Original locations preserved for reference but should be deprecated in favor of this centralized location.

### Import Path Updates Required

If code references the old paths, update to:
```python
# Old
from patterns.executors.github_sync.phase_sync import sync_phase_to_github

# New
import sys
sys.path.insert(0, '.github/github_integration_v2')
from executors.phase_sync import sync_phase_to_github
```

Or add `.github/github_integration_v2` to PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:.github/github_integration_v2"
```

## Next Steps

1. ✅ All files consolidated
2. ⏳ Update import references in codebase
3. ⏳ Update CI/CD workflows to use new paths
4. ⏳ Archive old file locations
5. ⏳ Update documentation links

---

**Consolidation completed**: 2025-12-04
