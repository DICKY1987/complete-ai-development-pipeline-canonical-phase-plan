# Configuration Directory

**Purpose**: Centralized configuration for tool profiles, agent settings, circuit breakers, and pipeline behavior.

## Overview

The `config/` directory contains YAML and JSON files that define how the pipeline invokes external tools, manages agent escalation, and handles failure recovery.

## Structure

```
config/
├── tool_profiles.json        # Tool invocation profiles (pytest, ruff, aider, etc.)
├── agent_profiles.json       # Agent settings (Aider, Codex, Claude)
├── circuit_breakers.yaml     # Circuit breaker thresholds and recovery timeouts
├── decomposition_rules.yaml  # Workstream decomposition rules
├── aim_config.yaml           # AIM+ registry settings
├── ccpm.yaml                 # Critical Chain Project Management settings
├── github.yaml               # GitHub sync configuration
├── router.config.yaml        # Router configuration for multi-agent systems
├── section_map.yaml          # Repository section mappings
├── path_index.yaml           # Path index for refactoring tracking
├── ui_settings.yaml          # UI/TUI settings for engine GUI
└── examples/                 # Example configurations
    └── tool_profile_annotated.yaml
```

## Core Configuration Files

### Tool Profiles (`tool_profiles.json`)

Defines invocation patterns for external tools used by adapters and plugins.

**Schema**:
```json
{
  "tool_name": {
    "type": "test|static-check|utility|formatter",
    "command": "executable_name",
    "args": ["arg1", "arg2"],
    "env": {"VAR": "value"},
    "working-dir": "{repo_root}|{cwd}",
    "timeout-sec": 120,
    "success-exit-codes": [0],
    "capture-output": true,
    "headless_mode_supported": false
  }
}
```

**Example**:
```json
{
  "pytest": {
    "type": "test",
    "command": "pytest",
    "args": ["-q", "--tb=short"],
    "env": {},
    "working-dir": "{repo_root}",
    "timeout-sec": 600,
    "success-exit-codes": [0, 5],
    "capture-output": true,
    "headless_mode_supported": true
  },
  "ruff": {
    "type": "static-check",
    "command": "ruff",
    "args": ["check", "--output-format", "json", "{file}"],
    "working-dir": "{cwd}",
    "timeout-sec": 120,
    "success-exit-codes": [0, 1],
    "capture-output": true
  }
}
```

**Placeholder Variables**:
- `{repo_root}` - Repository root directory
- `{cwd}` - Current working directory
- `{file}` - Target file path
- `{message}` - Message content (for echo/logging tools)

**Used By**:
- `core/engine/tools_adapter.py` - Tool invocation
- `error/plugins/*/plugin.py` - Plugin execution
- `engine/adapters/` - Standalone engine adapters

### Agent Profiles (`agent_profiles.json`)

Configuration for AI agent escalation (Aider, Codex, Claude).

**Schema**:
```json
{
  "agents": {
    "agent_name": {
      "enabled": true,
      "model": "model_name",
      "timeout_seconds": 300,
      "max_attempts": 1,
      "env_vars": {"VAR": "value"},
      "flags": ["--flag1", "--flag2"],
      "api_key_env": "API_KEY_VAR"
    }
  },
  "escalation": {
    "enable_mechanical_autofix": true,
    "enable_aider": true,
    "enable_codex": false,
    "enable_claude": false,
    "strict_mode": true,
    "max_total_attempts": 4
  },
  "prompt_templates": {
    "aider_fix": "Fix template for Aider",
    "codex_fix": "Fix template for Codex"
  }
}
```

**Example**:
```json
{
  "agents": {
    "aider": {
      "enabled": true,
      "model": "gpt-4",
      "timeout_seconds": 300,
      "max_attempts": 1,
      "env_vars": {
        "AIDER_AUTO_COMMITS": "true"
      },
      "flags": ["--yes", "--no-pretty"]
    }
  },
  "escalation": {
    "enable_mechanical_autofix": true,
    "enable_aider": true,
    "strict_mode": true,
    "max_total_attempts": 4
  }
}
```

**Used By**:
- `error/engine/agent_adapters.py` - Agent invocation
- `error/engine/error_state_machine.py` - Escalation logic

### Circuit Breakers (`circuit_breakers.yaml`)

Failure thresholds and recovery timeouts for resilience.

**Schema**:
```yaml
circuit_breakers:
  agent_name:
    failure_threshold: 3
    recovery_timeout_seconds: 300
    half_open_attempts: 1
```

**Example**:
```yaml
circuit_breakers:
  aider:
    failure_threshold: 3          # Open circuit after 3 consecutive failures
    recovery_timeout_seconds: 300 # Wait 5 minutes before attempting recovery
    half_open_attempts: 1         # Allow 1 test attempt in half-open state
  
  codex:
    failure_threshold: 2
    recovery_timeout_seconds: 180
    half_open_attempts: 1
  
  claude:
    failure_threshold: 2
    recovery_timeout_seconds: 180
    half_open_attempts: 1
```

**States**:
- **Closed**: Normal operation
- **Open**: Circuit breaker tripped, requests rejected immediately
- **Half-Open**: Testing recovery with limited attempts

**Used By**:
- `core/engine/circuit_breaker.py` - Circuit breaker implementation
- `error/engine/agent_adapters.py` - Agent invocation resilience

### Decomposition Rules (`decomposition_rules.yaml`)

Rules for breaking down workstreams into atomic steps.

**Schema**:
```yaml
decomposition:
  max_steps_per_workstream: 50
  max_files_per_step: 10
  prefer_atomic_changes: true
  
  step_categories:
    - setup
    - implementation
    - validation
    - cleanup
```

**Used By**:
- `core/planning/planner.py` - Workstream generation
- `specifications/bridge/converter.py` - OpenSpec → Workstream conversion

### AIM Config (`aim_config.yaml`)

AIM+ unified AI environment manager settings.

**Schema**:
```yaml
aim:
  registry_path: ".worktrees/aim_registry.json"
  health_check_interval_seconds: 60
  auto_install_missing: false
  
  tools:
    - aider
    - pytest
    - ruff
    - mypy
```

**Used By**:
- `aim/` - AIM+ modules

### CCPM Config (`ccpm.yaml`)

Critical Chain Project Management integration.

**Schema**:
```yaml
ccpm:
  buffer_percentage: 0.3
  critical_chain_mode: true
  slack_calculation: "automatic"
```

**Used By**:
- `pm/` - Project management modules

### GitHub Sync (`github.yaml`)

GitHub integration for issue/PR synchronization.

**Schema**:
```yaml
github:
  enabled: false
  sync_interval_minutes: 15
  repo_owner: "owner"
  repo_name: "repo"
  labels:
    - "workstream"
    - "automated"
```

**Used By**:
- `infra/sync/github_sync.py` - GitHub synchronization

### UI Settings (`ui_settings.yaml`)

GUI/TUI configuration for standalone engine.

**Schema**:
```yaml
ui:
  theme: "dark"
  refresh_rate_ms: 100
  show_progress_bars: true
  log_level: "INFO"
```

**Used By**:
- `engine/` - Standalone job runner GUI
- `gui/` - UI components

## Using Configuration

### Loading Tool Profiles

```python
from core.engine.tools_adapter import ToolsAdapter

adapter = ToolsAdapter(profiles_path="config/tool_profiles.json")
result = adapter.run_tool("pytest", args=["-v"])
```

### Loading Agent Profiles

```python
import json
from pathlib import Path

with open("config/agent_profiles.json") as f:
    config = json.load(f)

aider_config = config["agents"]["aider"]
if aider_config["enabled"]:
    # Invoke Aider
    pass
```

### Loading Circuit Breaker Config

```python
import yaml
from pathlib import Path

with open("config/circuit_breakers.yaml") as f:
    config = yaml.safe_load(f)

aider_breaker = config["circuit_breakers"]["aider"]
threshold = aider_breaker["failure_threshold"]
```

## Configuration Validation

**Validate all configs**:
```bash
python scripts/validate_configs.py
```

**Schema definitions**: `schema/config/`

## Environment Variable Overrides

Configuration values can be overridden via environment variables:

```bash
# Override tool timeout
export PIPELINE_PYTEST_TIMEOUT=1200

# Override agent model
export PIPELINE_AIDER_MODEL=gpt-4-turbo

# Override circuit breaker threshold
export PIPELINE_AIDER_FAILURE_THRESHOLD=5
```

**Naming Convention**:
- Prefix: `PIPELINE_`
- Section: `TOOL_NAME_` or `AGENT_NAME_`
- Key: `SETTING_NAME`
- Example: `PIPELINE_PYTEST_TIMEOUT`

## Best Practices

1. **Version control**: All configs tracked in git (except secrets)
2. **Secrets management**: Use environment variables for API keys, never commit
3. **Validation**: Run `validate_configs.py` before committing changes
4. **Documentation**: Add comments to YAML files for non-obvious settings
5. **Defaults**: Provide sensible defaults in code, allow config override
6. **Backwards compatibility**: Preserve old keys when adding new ones

## Testing Configuration Changes

```bash
# Dry-run with updated config
python scripts/run_workstream.py --workstream-id test --dry-run

# Test tool profile
python -c "from core.engine.tools_adapter import ToolsAdapter; ToolsAdapter().run_tool('pytest', ['--help'])"

# Test agent profile
python -c "from error.engine.agent_adapters import AiderAdapter; print(AiderAdapter().check_available())"
```

## Examples

See `config/examples/` for annotated example configurations.

## Related Sections

- **Core Engine**: `core/engine/` - Uses tool and agent profiles
- **Error Engine**: `error/engine/` - Uses agent profiles and circuit breakers
- **AIM+**: `aim/` - Uses AIM config
- **Schemas**: `schema/config/` - JSON schemas for validation

## See Also

- [Tool Adapter README](../core/engine/README.md)
- [Agent Adapters README](../error/engine/README.md)
- [Circuit Breaker Pattern](../docs/circuit_breaker.md)
- [Configuration Guide](../docs/configuration.md)
