---
status: draft
doc_type: guide
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-DOC-CONFIGURATION-GUIDE-816
---

# Configuration Guide - AI Development Pipeline

**Last Updated**: 2025-11-21
**Phase**: G (Invoke Adoption)
**Status**: Active

---

## Overview

The AI Development Pipeline uses **Invoke's hierarchical configuration system** to manage tool settings, orchestrator behavior, paths, and other runtime parameters.

Configuration is loaded in the following precedence order (highest to lowest):

1. **Environment variables** (prefix: `INVOKE_`)
2. **Runtime config** (`./.invoke.yaml` - gitignored, user-specific)
3. **Project config** (`./invoke.yaml` - versioned)
4. **User config** (`~/.invoke.yaml` - global user defaults)
5. **Hardcoded defaults** (in code)

---

## Configuration Files

### `invoke.yaml` (Project Config - Versioned)

**Location**: Repository root
**Purpose**: Project-wide defaults shared by all developers
**Version Control**: ✅ Committed to Git

Contains:
- Tool configurations (timeouts, arguments, environment)
- Orchestrator settings (retries, dry-run mode)
- Path mappings
- Error engine settings
- Circuit breaker thresholds

**Example**:
```yaml
tools:
  aider:
    timeout: 300
    model: "ollama/qwen2.5-coder:32b"
    flags:
      - "--yes-always"
      - "--no-auto-commits"

orchestrator:
  dry_run: false
  max_retries: 3
```

### `.invoke.yaml` (User Config - Local Override)

**Location**: Repository root (gitignored) or `~/.invoke.yaml` (global)
**Purpose**: User-specific overrides for local development
**Version Control**: ❌ NOT committed (in `.gitignore`)

Use cases:
- Override model choice (GPT-4 vs Ollama)
- Enable dry-run by default locally
- Change timeout values for debugging
- Point to alternate paths

**Example** (create from `.invoke.yaml.example`):
```yaml
tools:
  aider:
    model: "gpt-4"  # Override to use GPT-4 locally

orchestrator:
  dry_run: true  # Default to dry-run for testing
```

### Environment Variable Overrides

**Prefix**: `INVOKE_`
**Format**: `INVOKE_<SECTION>_<KEY>`
**Purpose**: CI/CD overrides and temporary changes

**Examples**:
```bash
# Override aider timeout to 600 seconds
export INVOKE_TOOLS_AIDER_TIMEOUT=600

# Enable dry-run mode
export INVOKE_ORCHESTRATOR_DRY_RUN=true

# Change worktree directory
export INVOKE_PATHS_WORKTREES_DIR="/tmp/worktrees"
```

**In CI** (GitHub Actions):
```yaml
- name: Run tests
  env:
    INVOKE_ORCHESTRATOR_DRY_RUN: "false"
    INVOKE_TOOLS_PYTEST_TIMEOUT: "900"
  run: invoke ci
```

---

## Configuration Sections

### `tools.*` - Tool Configurations

Defines settings for external tools (Aider, pytest, linters, etc.).

**Common fields**:
- `timeout`: Execution timeout in seconds
- `args`: Command-line arguments (list)
- `flags`: Additional flags (list)
- `env`: Environment variables (dict)
- `config`: Path to tool-specific config file

**Available tools**:
```yaml
tools:
  aider:          # AI code editor
  pytest:         # Test runner
  ruff:           # Python linter
  mypy:           # Type checker
  markdownlint:   # Markdown linter
```

**Example**:
```yaml
tools:
  pytest:
    timeout: 600
    args:
      - "-q"
      - "--tb=short"
    env:
      PYTHONPATH: "."
```

### `orchestrator.*` - Orchestrator Settings

Controls workstream execution behavior.

**Fields**:
- `dry_run` (bool): Skip external tool execution
- `max_retries` (int): Maximum step retry attempts
- `static_tools` (list): Tools to run in STATIC phase
- `runtime_tool` (str): Tool to run in RUNTIME phase

**Example**:
```yaml
orchestrator:
  dry_run: false
  max_retries: 3
  static_tools:
    - ruff
    - mypy
  runtime_tool: pytest
```

### `paths.*` - Path Configuration

Defines repository directory structure.

**Fields**:
- `repo_root`: Repository root (default: ".")
- `workstreams_dir`: Workstream bundles location
- `state_db`: SQLite database path
- `worktrees_dir`: Git worktree location
- `logs_dir`: Log files location
- `config_dir`: Config files location

**Example**:
```yaml
paths:
  repo_root: "."
  workstreams_dir: "workstreams"
  state_db: "state/workstream_pipeline.db"
  worktrees_dir: ".worktrees"
```

### `error_engine.*` - Error Detection

Controls error detection pipeline behavior.

**Fields**:
- `plugins_dir`: Plugin discovery location
- `cache_dir`: Hash cache for incremental detection
- `enabled`: Enable/disable error engine

**Example**:
```yaml
error_engine:
  plugins_dir: "error/plugins"
  cache_dir: "state/error_cache"
  enabled: true
```

### `circuit_breakers.*` - Failure Limits

Prevents infinite retry loops.

**Fields**:
- `max_step_attempts`: Max attempts per step
- `max_fix_attempts`: Max FIX iterations
- `max_identical_errors`: Duplicate error threshold
- `oscillation_window`: History window for oscillation detection

**Example**:
```yaml
circuit_breakers:
  max_step_attempts: 5
  max_fix_attempts: 3
  max_identical_errors: 2
  oscillation_window: 5
```

---

## Using Configuration in Code

### Python Code

**Load entire config**:
```python
from core.config_loader import load_project_config

config = load_project_config()
# Returns dict with all sections
```

**Load specific section**:
```python
from core.config_loader import (
    get_tool_config,
    get_orchestrator_config,
    get_paths_config,
    get_circuit_breaker_config,
)

# Get aider config
aider_cfg = get_tool_config('aider')
timeout = aider_cfg.get('timeout', 300)
model = aider_cfg.get('model', 'default')

# Get orchestrator config
orch_cfg = get_orchestrator_config()
dry_run = orch_cfg.get('dry_run', False)

# Get paths
paths_cfg = get_paths_config()
worktrees_dir = paths_cfg.get('worktrees_dir', '.worktrees')
```

**Backward compatibility** (migrate from `config/tool_profiles.json`):
```python
# OLD (Phase E and earlier)
from core.engine import tools
profiles = tools.load_tool_profiles('config/tool_profiles.json')

# NEW (Phase G)
from core.config_loader import get_tool_config
aider_config = get_tool_config('aider')
```

### Invoke Tasks (tasks.py)

Invoke Context automatically loads config from `invoke.yaml`:

```python
from invoke import task

@task
def example(c):
    """Access config via Context."""
    # Invoke native config (limited to run/sudo/tasks sections)
    # Use config_loader for custom sections

    from core.config_loader import get_tool_config
    pytest_cfg = get_tool_config('pytest')
    timeout = pytest_cfg.get('timeout', 600)

    c.run(f"pytest --timeout={timeout}")
```

---

## Migration from Legacy Config

### Old Structure (Phase E)

```
config/
├── tool_profiles.json       # Tool settings
├── circuit_breakers.yaml    # Breaker config
├── aim_config.yaml          # AIM settings
├── decomposition_rules.yaml # Planner rules
└── github.yaml              # GitHub sync
```

### New Structure (Phase G)

```
invoke.yaml                  # Unified project config
.invoke.yaml                 # User overrides (gitignored)
config/                      # Legacy files (deprecated)
```

### Migration Steps

1. **Keep legacy files** for 1-2 releases (backward compatibility)
2. **Add deprecation warnings** when loading old configs:
```python
import warnings

def load_tool_profiles(profile_path=None):
    if profile_path:
        warnings.warn(
            "Loading from config/tool_profiles.json is deprecated. "
            "Use invoke.yaml instead.",
            DeprecationWarning,
            stacklevel=2
        )
    # Fall back to invoke.yaml
    from core.config_loader import get_tool_config
    return get_tool_config(...)
```

3. **Update documentation** to point to `invoke.yaml`
4. **Remove old files** in Phase G+1

---

## Best Practices

### ✅ Do

- **Keep `invoke.yaml` minimal** - only project-wide defaults
- **Use `.invoke.yaml` for personal settings** - never commit it
- **Use env vars in CI** - for temporary overrides
- **Document new config keys** - add to this guide
- **Validate config on load** - fail fast on invalid values

### ❌ Don't

- **Don't commit `.invoke.yaml`** - it's user-specific
- **Don't hardcode values** - use config instead
- **Don't mix old and new** - migrate fully to `invoke.yaml`
- **Don't use complex nesting** - keep config flat and readable
- **Don't store secrets** - use environment variables or keyring

---

## Troubleshooting

### Config not loading

**Problem**: `KeyError` or `AttributeError` when accessing config

**Solution**: Use `config_loader` helpers instead of Invoke Context:
```python
# ❌ Won't work for custom sections
from invoke import Config
cfg = Config()
cfg.orchestrator  # KeyError

# ✅ Use config_loader
from core.config_loader import get_orchestrator_config
cfg = get_orchestrator_config()
```

### Environment variable not working

**Problem**: `INVOKE_*` env var not overriding config

**Solution**: Check naming convention:
```bash
# ❌ Wrong
export INVOKE_AIDER_TIMEOUT=600

# ✅ Correct (must include section)
export INVOKE_TOOLS_AIDER_TIMEOUT=600
```

### User config not applying

**Problem**: `.invoke.yaml` changes not taking effect

**Solution**: Ensure file is in the right location:
```bash
# Check if file exists
ls -la .invoke.yaml

# Verify it's not committed
git status .invoke.yaml
# Should show: "Untracked files" or not appear at all

# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('.invoke.yaml'))"
```

---

## Examples

### Local Development Override

```yaml
# .invoke.yaml (local, gitignored)
tools:
  aider:
    model: "gpt-4"
    timeout: 600

orchestrator:
  dry_run: true  # Always dry-run locally
  max_retries: 1  # Fail fast

paths:
  logs_dir: "/tmp/pipeline-logs"  # Use temp for logs
```

### CI/CD Configuration

```yaml
# .github/workflows/ci.yml
env:
  INVOKE_ORCHESTRATOR_DRY_RUN: "false"
  INVOKE_TOOLS_PYTEST_TIMEOUT: "900"
  INVOKE_TOOLS_AIDER_MODEL: "gpt-3.5-turbo"  # Cheaper for CI

steps:
  - name: Run CI
    run: invoke ci
```

### Production Override

```bash
# Production deployment script
export INVOKE_ORCHESTRATOR_MAX_RETRIES=5
export INVOKE_ERROR_ENGINE_ENABLED=true
export INVOKE_PATHS_WORKTREES_DIR="/data/worktrees"

invoke run-workstream --ws-id ws-prod-deploy
```

---

## Related Documentation

- [PHASE_G_INVOKE_ADOPTION.md](PHASE_G_INVOKE_ADOPTION.md) - Full adoption plan
- [tasks.py](../tasks.py) - Invoke task definitions
- [invoke.yaml](../invoke.yaml) - Project config
- [.invoke.yaml.example](../.invoke.yaml.example) - User config template

---

## Change Log

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2025-11-21 | Initial configuration guide for Phase G |
