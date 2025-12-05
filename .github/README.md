# .github - GitHub Integration & Infrastructure

**Last Updated**: 2025-12-05
**Status**: ✅ Consolidated (Phase PH-GITHUB-CONSOLIDATION-001 Complete)

## Overview

This directory contains GitHub-specific integrations, workflows, and infrastructure for the Complete AI Development Pipeline.

## Directory Structure

```
.github/
├── shared/                      ← Unified GitHub API client (NEW)
│   ├── github_client.py         ← Single source of truth for GitHub API
│   ├── __init__.py
│   └── README.md
│
├── github_integration_v2/       ← Active GitHub Projects v2 integration
│   ├── scripts/                 ← All sync scripts (consolidated)
│   │   ├── milestone_completion_sync.py
│   │   ├── project_item_sync.py
│   │   ├── splinter_sync_phase_to_github.py
│   │   ├── gh_issue_update.py
│   │   └── gh_epic_sync.py
│   ├── executors/               ← Pattern executors
│   ├── tests/                   ← Unit tests
│   ├── specs/                   ← Pattern specifications
│   └── docs/                    ← Integration documentation
│
├── workflows/                   ← GitHub Actions workflows (13 files)
│   ├── milestone_completion.yml
│   ├── project_item_sync.yml
│   ├── splinter_phase_sync.yml
│   └── ...
│
├── infra/                       ← Infrastructure utilities
│   ├── sync/                    ← PowerShell auto-sync scripts (local dev)
│   ├── ci/                      ← CI/CD configurations
│   └── data/                    ← Persistent data (refactor_paths.db)
│
└── tree_sitter/                 ← Code parsing utilities
```

## Recent Changes (2025-12-05)

### ✅ Consolidation Complete

**Problem Solved**: Duplicate GitHub API clients and scattered scripts
**Solution**: Unified architecture with single client and consolidated scripts

**Changes Made**:
1. ✅ Created `.github/shared/github_client.py` - Single unified API client
2. ✅ Migrated all active scripts to `github_integration_v2/scripts/`
3. ✅ Updated all workflow files to use v2 paths
4. ✅ Archived old scripts to `_ARCHIVE/github_scripts_old_20251205/`
5. ✅ Updated imports in all scripts to use shared client

## Active Components

### 1. Shared GitHub Client (`shared/`)
- Unified GitHub Projects v2 API client
- Single source of truth for all GitHub operations

### 2. GitHub Integration v2 (`github_integration_v2/`)
- Complete GitHub Projects v2 integration suite
- 5 active sync scripts
- Pattern executors and tests

### 3. Workflows (`workflows/`)
- 13 active GitHub Actions workflows
- Automated quality gates and sync operations

### 4. Infrastructure (`infra/`)
- PowerShell sync utilities (local dev)
- CI/CD configurations
- Sandbox repos for testing

## Deprecated/Archived

### ❌ `.github/scripts/` (REMOVED)
- **Archived to**: `_ARCHIVE/github_scripts_old_20251205/`
- **Date**: 2025-12-05
- **Reason**: Consolidation to `github_integration_v2/`

## Related Documentation

- [`github_integration_v2/README.md`](github_integration_v2/README.md)
- [`shared/README.md`](shared/README.md)
- [`_ARCHIVE/github_scripts_old_20251205/DEPRECATION_NOTICE.md`](_ARCHIVE/github_scripts_old_20251205/DEPRECATION_NOTICE.md)

---

**Framework**: Universal Execution Templates (UET)
**Consolidation Phase**: PH-GITHUB-CONSOLIDATION-001
**Generated**: 2025-12-05
