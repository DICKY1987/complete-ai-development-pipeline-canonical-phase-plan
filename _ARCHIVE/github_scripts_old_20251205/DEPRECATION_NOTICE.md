# Deprecated GitHub Scripts

**Archive Date**: 2025-12-05
**Reason**: Consolidation to `.github/github_integration_v2/`

## What Happened

These scripts were part of an older GitHub integration implementation that has been superseded by the unified `github_integration_v2` system.

## Old Structure (DEPRECATED)

```
.github/scripts/
├── github_project_utils.py      → Moved to .github/shared/github_client.py
├── milestone_completion_sync.py → Moved to .github/github_integration_v2/scripts/
├── project_item_sync.py         → Moved to .github/github_integration_v2/scripts/
└── project_id_hydration.py      → Archived (unused)
```

## New Structure (ACTIVE)

```
.github/
├── shared/
│   └── github_client.py         ← Unified API client
└── github_integration_v2/
    └── scripts/
        ├── milestone_completion_sync.py
        ├── project_item_sync.py
        ├── splinter_sync_phase_to_github.py
        ├── gh_issue_update.py
        └── gh_epic_sync.py
```

## Migration Guide

If you need to reference the old code:

1. **Old import**: `from github_project_utils import GitHubProjectClient`
2. **New import**:
   ```python
   import sys
   from pathlib import Path
   sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))
   from github_client import GitHubProjectClient
   ```

## Workflows Updated

- ✅ `milestone_completion.yml` → Now uses `.github/github_integration_v2/scripts/`
- ✅ `project_item_sync.yml` → Now uses `.github/github_integration_v2/scripts/`
- ✅ `splinter_phase_sync.yml` → Already using v2

## Restoration

If you need to restore these files temporarily:

```bash
git checkout HEAD~1 -- .github/scripts/
```

Or copy from this archive directory.

---

**Consolidation Phase**: PH-GITHUB-CONSOLIDATION-001
**Archived By**: Automated consolidation script
**Safe to Delete**: After 2026-01-01 (30 day retention)
