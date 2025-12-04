# GitHub Integration v2

**Status**: Production Ready 🚀

This folder contains the complete GitHub Integration v2 solution for syncing phase plans to GitHub Issues and Projects.

## Folder Structure

```
.github/github_integration_v2/
├── README.md                           ← This file
├── GITHUB_INTEGRATION_V2_COMPLETE.md  ← Completion report
├── executors/
│   ├── phase_sync.py                  ← Core GraphQL executor (485 LOC)
│   └── README.md                      ← Executor documentation
├── scripts/
│   ├── splinter_sync_phase_to_github.py  ← CLI sync tool (195 LOC)
│   ├── gh_issue_update.py            ← Issue update utility
│   └── gh_epic_sync.py                ← Epic sync utility
├── specs/
│   ├── GH_SYNC_PHASE_V1.pattern.yaml ← Pattern specification
│   ├── PAT-EXEC-GHPROJECT-PHASE-PLAN-SYNC-V1.md
│   └── PAT-EXEC-GHPROJECT-PHASE-STATUS-SYNC-V1.md
├── tests/
│   ├── GH_SYNC_PHASE_V1_test.py      ← Unit tests (8 tests ✓)
│   ├── test_github_sync.py
│   ├── test_github_sync_cli_path.py
│   └── test_orchestrator_lifecycle_sync.py
└── docs/
    ├── EXAMPLE.md                     ← End-to-end example walkthrough
    ├── README_GITHUB_PROJECT_INTEGRATION.md
    └── MASTER_SPLINTER_GITHUB_ADD_ON.md  ← Full integration guide
```

## Quick Start

### 1. Install Dependencies
```bash
pip install pyyaml requests jsonschema
```

### 2. Set GitHub Token
```bash
export GITHUB_TOKEN="ghp_your_token_here"
```

### 3. Run Sync (Dry Run)
```bash
python .github/github_integration_v2/scripts/splinter_sync_phase_to_github.py \
  --phase-file phases/my_phase.yaml \
  --github-repo owner/repo \
  --dry-run
```

### 4. Run Sync (Live)
```bash
python .github/github_integration_v2/scripts/splinter_sync_phase_to_github.py \
  --phase-file phases/my_phase.yaml \
  --github-repo owner/repo
```

## Features

- ✅ Full GraphQL Projects v2 integration
- ✅ Automatic project resolution (user/org)
- ✅ Issue node ID lookup
- ✅ Project item find/create operations
- ✅ Custom field updates (TEXT, DATE, NUMBER, SINGLE_SELECT)
- ✅ Field type auto-detection and value conversion
- ✅ Pagination support for large projects
- ✅ CLI sync script with dry-run mode
- ✅ Complete unit test suite (8 tests, all passing)

## Testing

```bash
# Run unit tests
python .github/github_integration_v2/tests/GH_SYNC_PHASE_V1_test.py -v

# Run all integration tests
pytest .github/github_integration_v2/tests/ -v
```

## Documentation

- **[GITHUB_INTEGRATION_V2_COMPLETE.md](./GITHUB_INTEGRATION_V2_COMPLETE.md)** - Completion report
- **[docs/EXAMPLE.md](./docs/EXAMPLE.md)** - Example walkthrough
- **[docs/MASTER_SPLINTER_GITHUB_ADD_ON.md](./docs/MASTER_SPLINTER_GITHUB_ADD_ON.md)** - Full guide
- **[executors/README.md](./executors/README.md)** - Executor documentation

## GitHub Actions

The solution integrates with GitHub Actions via:
- **`.github/workflows/splinter_phase_sync.yml`** - Auto-sync on phase file changes
- **`.github/workflows/project_item_sync.yml`** - Project item sync

## Version History

- **v1** (2025-12-04): Pattern spec, schemas, validation, Issue sync
- **v2** (2025-12-04): Complete Projects v2 GraphQL, CLI tool, tests ✓

## Support

See [docs/EXAMPLE.md](./docs/EXAMPLE.md) for troubleshooting and common scenarios.
