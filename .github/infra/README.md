---
doc_id: DOC-GUIDE-README-428
---

# Infrastructure and CI/CD

**Purpose**: Continuous integration, deployment workflows, and infrastructure automation for the AI Development Pipeline.

## Overview

The `infra/` directory contains CI/CD configuration, GitHub Actions workflows, and synchronization utilities that ensure code quality, enforce standards, and automate deployment.

## Structure

```
infra/
├── ci/                              # Continuous integration configuration
│   ├── workflows/
│   │   └── ci.yml                   # GitHub Actions workflow
│   ├── requirements.txt             # CI-specific Python dependencies
│   ├── pytest.ini                   # CI pytest configuration (if different from root)
│   └── sandbox_repos/               # Test repositories for CI integration tests
└── sync/                            # Synchronization utilities
    ├── GitAutoSync.ps1              # PowerShell auto-sync script
    ├── Install-GitAutoSync.ps1      # Installation script
    ├── Start-AutoSync.ps1           # Start sync daemon
    ├── README.md                    # Sync documentation
    ├── INSTALLATION_COMPLETE.md     # Installation guide
    ├── PROFILE_SETUP.md             # Profile configuration
    └── TEST_BIDIRECTIONAL_SYNC.md   # Bidirectional sync testing
```

## CI Configuration (`infra/ci/`)

### GitHub Actions Workflow

**File**: `infra/ci/workflows/ci.yml`

**Triggers**:
- Push to any branch
- Pull request to any branch

**Jobs**:

#### 1. Unit Tests (`tests`)

Runs on: Ubuntu Latest, Windows Latest

**Steps**:
1. Checkout repository
2. Setup Python 3.12
3. Install dependencies from `infra/ci/requirements.txt`
4. Run pytest (excluding integration tests):
   ```bash
   python -m pytest -q --ignore=tests/integration
   ```

**Matrix**:
- OS: `ubuntu-latest`, `windows-latest`
- Python: `3.12`

#### 2. GitHub Sync Tests (`tests-ghsync`)

Runs on: Ubuntu Latest

**Environment**:
- `ENABLE_GH_SYNC=true`

**Steps**:
1. Checkout repository
2. Setup Python 3.12
3. Install dependencies
4. Run GitHub sync tests:
   ```bash
   python -m pytest -q -k "github_sync" --ignore=tests/integration
   ```

### CI Dependencies

**File**: `infra/ci/requirements.txt`

**Purpose**: Python dependencies for CI environment (may differ from `requirements.txt` at root).

**Typical contents**:
```txt
pytest>=7.0
pytest-cov>=4.0
pyyaml>=6.0
jsonschema>=4.0
# CI-specific tools
pytest-timeout>=2.0
pytest-xdist>=3.0  # Parallel test execution
```

### CI-Specific Configuration

If `infra/ci/pytest.ini` exists, it overrides root `pytest.ini` for CI runs.

**Example**:
```ini
[pytest]
minversion = 7.0
addopts = -ra --strict-markers --tb=short
testpaths = tests
pythonpath = .
norecursedirs = sandbox_repos .git .venv venv build dist
asyncio_mode = auto
timeout = 300  # Global timeout for CI
```

### Sandbox Repositories

**Location**: `infra/ci/sandbox_repos/`

Self-contained test repositories used for CI integration tests.

**Purpose**:
- Test workstream execution in isolated environments
- Validate git worktree lifecycle
- Test cross-repository operations

**Usage**:
```bash
# CI runs integration tests on sandbox repos
pytest tests/integration/ --sandbox-repos=infra/ci/sandbox_repos/
```

## Synchronization Utilities (`infra/sync/`)

### Git Auto-Sync

**Purpose**: Automated bidirectional git synchronization for development environments.

**Main Script**: `GitAutoSync.ps1`

**Features**:
- Auto-commit and push on file changes
- Pull remote changes automatically
- Conflict detection and resolution
- Background daemon mode
- Logging and error handling

**Installation**:
```powershell
# Run installation script
.\infra\sync\Install-GitAutoSync.ps1

# Follow prompts to configure sync settings
```

**Usage**:
```powershell
# Start auto-sync daemon
.\infra\sync\Start-AutoSync.ps1

# Check sync status
.\infra\sync\GitAutoSync.ps1 -Status

# Stop sync daemon
.\infra\sync\GitAutoSync.ps1 -Stop
```

**Configuration**:
- **Interval**: Sync every N seconds (default: 60)
- **Auto-commit**: Automatic commit messages
- **Conflict strategy**: `merge`, `rebase`, or `manual`

### Installation Guide

**File**: `infra/sync/INSTALLATION_COMPLETE.md`

Step-by-step guide for setting up auto-sync on new machines.

**Steps**:
1. Clone repository
2. Run `Install-GitAutoSync.ps1`
3. Configure PowerShell profile (see `PROFILE_SETUP.md`)
4. Start sync daemon
5. Verify bidirectional sync (see `TEST_BIDIRECTIONAL_SYNC.md`)

### Profile Setup

**File**: `infra/sync/PROFILE_SETUP.md`

Instructions for configuring PowerShell profile to auto-start sync.

**Example**:
```powershell
# Add to $PROFILE
function Start-PipelineSync {
    & "C:\path\to\repo\infra\sync\Start-AutoSync.ps1"
}

# Auto-start on shell startup (optional)
# Start-PipelineSync
```

### Bidirectional Sync Testing

**File**: `infra/sync/TEST_BIDIRECTIONAL_SYNC.md`

Test procedures for validating sync functionality.

**Test Scenarios**:
1. **Local → Remote**: Create file locally, verify pushed
2. **Remote → Local**: Create file remotely, verify pulled
3. **Conflict**: Simultaneous edits, verify conflict resolution
4. **Large files**: Test with binary/large files

## CI Workflow Details

### Test Execution Strategy

**Unit Tests**:
- Fast (<10s per test)
- No external dependencies
- Isolated fixtures
- Run on every commit

**Integration Tests**:
- Slower (10s-60s per test)
- May require external tools
- Use sandbox repos
- Run on PR/merge only (excluded from main CI)

### Failure Handling

**On test failure**:
1. CI job fails
2. GitHub Check fails on PR
3. Notification sent to committer
4. Logs available in Actions tab

**On dependency failure**:
1. Retry up to 3 times
2. Cache dependencies for faster re-runs
3. Fallback to alternate package sources

### Performance Optimization

**Caching**:
- Python dependencies cached between runs
- Pip cache persists across jobs
- Database fixtures use in-memory SQLite where possible

**Parallelization**:
- Matrix builds run in parallel (Ubuntu + Windows)
- Pytest uses `pytest-xdist` for parallel test execution (CI only)

**Selective Testing**:
- PR tests: All unit tests
- Main branch: Unit + integration tests
- Tag/release: Full test suite + performance benchmarks

## Environment Variables

**CI-specific**:
- `CI=true` - Set automatically by GitHub Actions
- `ENABLE_GH_SYNC=true` - Enable GitHub sync tests
- `PIPELINE_DB_PATH` - Override database path for tests
- `PYTEST_TIMEOUT=300` - Global test timeout

**Secrets** (configured in GitHub repo settings):
- `ANTHROPIC_API_KEY` - For Claude agent tests (optional)
- `OPENAI_API_KEY` - For Aider tests (optional)
- `GITHUB_TOKEN` - Automatically provided by GitHub Actions

## Running CI Locally

**Simulate CI environment**:
```bash
# Install CI dependencies
pip install -r infra/ci/requirements.txt

# Run tests as CI would
pytest -q --ignore=tests/integration

# Run with timeout
pytest --timeout=300 -q
```

**Using act** (GitHub Actions local runner):
```bash
# Install act: https://github.com/nektos/act
act -j tests

# Run specific job
act -j tests-ghsync
```

## CI Standards Enforcement

### Path Standards

**Test**: `tests/test_ci_path_standards.py`

**Enforces**:
- No deprecated import paths (`src.pipeline.*`, `MOD_ERROR_PIPELINE.*`)
- Section-based imports (`core.*`, `error.*`, `specifications.*`)
- No absolute paths in code (except config)

**Example**:
```python
def test_no_deprecated_imports():
    for py_file in Path("core").rglob("*.py"):
        tree = ast.parse(py_file.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert not node.module.startswith("src.pipeline")
```

### Schema Validation

**Test**: `tests/test_validators.py`

**Validates**:
- Workstream bundles conform to schema
- Tool profiles match expected format
- Agent profiles are well-formed
- Config files are valid YAML/JSON

### Code Quality

**Tools** (run in CI):
- Ruff: Linting and style checking
- Mypy: Type checking (Python 3.12+)
- Black: Code formatting verification
- Markdownlint: Markdown style checking

**Commands**:
```bash
# Linting
ruff check .

# Type checking
mypy core/ error/ specifications/

# Format checking
black --check .

# Markdown linting
markdownlint-cli '**/*.md'
```

## Deployment

**Not yet implemented** - Placeholder for future CD workflows:

- **Build artifacts**: Package workstream bundles
- **Release automation**: Tag-based releases
- **Documentation deployment**: Auto-generate and deploy docs
- **Container images**: Docker images for standalone engine

## Monitoring and Alerts

**GitHub Actions**:
- Email notifications on failure
- Slack/Discord integration (configurable)
- Status badges in README

**Metrics**:
- Test duration trends
- Flaky test detection
- Code coverage trends

## Related Sections

- **Tests**: `tests/` - Test suite executed by CI
- **Scripts**: `scripts/` - Automation scripts
- **Config**: `config/` - Configuration validated by CI

## See Also

- [CI Path Standards](../docs/CI_PATH_STANDARDS.md)
- [Testing Guide](../docs/testing_guide.md)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [pytest Documentation](https://docs.pytest.org/)
