# Error Detection Engine

**Purpose**: Incremental, plugin-based error detection system with state machine-driven escalation.

## Overview

The error engine discovers and executes detection plugins in dependency order, caches file hashes for incremental validation, and drives a multi-agent escalation workflow through a deterministic state machine.

## Architecture

```
error/engine/
├── error_engine.py           # Main entry point: run_error_pipeline()
├── error_state_machine.py    # Deterministic state transitions (S_INIT → S_SUCCESS/S4_QUARANTINE)
├── error_pipeline_service.py # Service layer: coordinates agent invocations and tool runs
├── error_pipeline_cli.py     # CLI interface for error pipeline
├── plugin_manager.py         # Plugin discovery and DAG ordering
├── pipeline_engine.py        # Per-file plugin execution and result aggregation
├── file_hash_cache.py        # Incremental validation via file hashing
├── agent_adapters.py         # Adapters for Aider, Codex, Claude
└── error_context.py          # Shared context dataclass for pipeline state
```

## Core Components

### Error Engine (`error_engine.py`)

Main orchestrator that:
- Loads file hash cache from `.state/validation_cache.json`
- Instantiates PluginManager and PipelineEngine
- Aggregates issues across all files
- Normalizes output to Operating Contract schema

**Usage**:
```python
from error.engine.error_engine import run_error_pipeline
from error.engine.error_context import ErrorPipelineContext

ctx = ErrorPipelineContext()
ctx.file_path = "path/to/file.py"
ctx.current_state = "S_INIT"

report = run_error_pipeline(
    python_files=["src/module.py"],
    powershell_files=[],
    ctx=ctx
)
```

### State Machine (`error_state_machine.py`)

Deterministic state machine implementing the Operating Contract escalation strategy:

**States**:
- `S_INIT` → Initial state
- `S0_BASELINE_CHECK` → Run all detection plugins
- `S0_MECHANICAL_AUTOFIX` → Apply auto-fixers (Black, isort, Prettier, etc.)
- `S0_MECHANICAL_RECHECK` → Verify auto-fix results
- `S1_AIDER_FIX` → Escalate to Aider
- `S1_AIDER_RECHECK` → Verify Aider fixes
- `S2_CODEX_FIX` → Escalate to GitHub Copilot CLI
- `S2_CODEX_RECHECK` → Verify Codex fixes
- `S3_CLAUDE_FIX` → Escalate to Claude API
- `S3_CLAUDE_RECHECK` → Verify Claude fixes
- `S4_QUARANTINE` → Max attempts exhausted
- `S_SUCCESS` → No issues remaining
- `S_ERROR_INFRA` → Infrastructure failure

**Function**:
```python
from error.engine.error_state_machine import advance_state

# Mutates ctx.current_state based on last_error_report
advance_state(ctx)
```

### Plugin Manager (`plugin_manager.py`)

Discovers plugins from `error/plugins/` and orders them via topological sort based on `requires` dependencies.

**Features**:
- Auto-discovery via `manifest.json` + `plugin.py`
- Tool availability checking
- File extension filtering
- DAG-based execution order

**Usage**:
```python
from error.engine.plugin_manager import PluginManager

pm = PluginManager()
pm.discover()
plugins = pm.get_plugins_for_file(Path("file.py"))
```

### Pipeline Engine (`pipeline_engine.py`)

Executes applicable plugins for a single file and aggregates results.

**Features**:
- Incremental validation via hash cache
- Issue normalization to `PluginIssue` schema
- Auto-fix detection (compares input/output file content)

**Usage**:
```python
from error.engine.pipeline_engine import PipelineEngine

engine = PipelineEngine(plugin_manager, file_hash_cache)
result = engine.process_file(Path("src/module.py"))
```

### Agent Adapters (`agent_adapters.py`)

Thin wrappers for invoking Aider, Codex, and Claude with standardized interfaces.

**Features**:
- Timeout enforcement
- Error report formatting
- Prompt template integration

**Configured via**: `config/agent_profiles.json`

### Error Context (`error_context.py`)

Shared dataclass that tracks pipeline state across service layer invocations.

**Fields**:
- `file_path`: Current file being processed
- `current_state`: Current state machine state
- `current_agent`: Active agent ("aider", "codex", "claude", "none")
- `attempt_number`: Retry counter for current agent
- `last_error_report`: Most recent error report dict
- `mechanical_fix_applied`: Whether auto-fixers ran
- `final_status`: "success", "quarantine", or "error_infra"

## CLI Interface

**Run the error pipeline**:
```bash
# Scan Python files
python scripts/run_error_engine.py --python src/

# Dry-run (no auto-fixes)
python scripts/run_error_engine.py --python src/ --dry-run

# With agent escalation
python scripts/run_error_engine.py --python src/ --enable-agents
```

**CLI tool**:
```bash
python -m error.engine.error_pipeline_cli --help
```

## Configuration

### Agent Profiles (`config/agent_profiles.json`)

```json
{
  "agents": {
    "aider": {
      "enabled": true,
      "model": "gpt-4",
      "timeout_seconds": 300,
      "max_attempts": 1
    },
    "codex": { "enabled": false },
    "claude": { "enabled": false }
  },
  "escalation": {
    "enable_mechanical_autofix": true,
    "enable_aider": true,
    "strict_mode": true,
    "max_total_attempts": 4
  }
}
```

### Circuit Breakers (`config/circuit_breakers.yaml`)

```yaml
circuit_breakers:
  aider:
    failure_threshold: 3
    recovery_timeout_seconds: 300
  codex:
    failure_threshold: 2
    recovery_timeout_seconds: 180
```

## Integration with Core Pipeline

The error engine is invoked via `core/engine/orchestrator.py` for quality gate validation:

```python
from error.engine.error_engine import run_error_pipeline
from error.engine.error_context import ErrorPipelineContext

ctx = ErrorPipelineContext()
report = run_error_pipeline(python_files, powershell_files, ctx)

if report["summary"]["has_hard_fail"]:
    # Halt orchestration
    raise QualityGateError(report)
```

## State Machine Diagram

```
S_INIT
  ↓
S0_BASELINE_CHECK
  ↓ (issues found)
S0_MECHANICAL_AUTOFIX
  ↓
S0_MECHANICAL_RECHECK
  ↓ (still issues)
S1_AIDER_FIX
  ↓
S1_AIDER_RECHECK
  ↓ (still issues)
S2_CODEX_FIX
  ↓
S2_CODEX_RECHECK
  ↓ (still issues)
S3_CLAUDE_FIX
  ↓
S3_CLAUDE_RECHECK
  ↓ (still issues)
S4_QUARANTINE

(Any state with 0 issues → S_SUCCESS)
(Infrastructure errors → S_ERROR_INFRA)
```

## File Hash Cache

Location: `.state/validation_cache.json`

**Format**:
```json
{
  "src/module.py": {
    "hash": "abc123...",
    "last_checked_utc": "2025-01-15T10:30:00Z",
    "status": "pass"
  }
}
```

**Behavior**:
- Files with unchanged hash → skipped
- Files with changed hash → re-validated
- New files → always validated

## Testing

```bash
# Unit tests
pytest tests/error/ -v

# Integration tests
pytest tests/pipeline/test_fix_loop.py -v

# State machine determinism
pytest tests/test_engine_determinism.py -v
```

## Related Sections

- **Plugins**: `error/plugins/` - Detection plugin implementations
- **Shared Utils**: `error/shared/utils/` - Types, hashing, JSONL management
- **Core Engine**: `core/engine/` - Workstream orchestration (separate from error engine)
- **Configuration**: `config/` - Agent profiles, circuit breakers

## Environment Variables

- `PIPELINE_ERROR_PLUGINS_PATH` - Override plugin discovery path (default: `error/plugins/`)
- `PIPELINE_STATE_DIR` - Override state directory (default: `.state/`)

## Best Practices

1. **Incremental validation**: Always use `file_hash_cache` to avoid redundant checks
2. **Deterministic state transitions**: State machine logic is pure; side-effects live in service layer
3. **Plugin isolation**: Each plugin runs in isolation; failures don't cascade
4. **Agent escalation**: Enable agents only when human intervention is unavailable
5. **Schema compliance**: All outputs conform to `error/shared/utils/types.py` contracts

## Troubleshooting

**Issue**: Plugins not discovered
- Check `manifest.json` exists in plugin directory
- Verify `plugin.py` exports `register()` function
- Ensure tool is available in PATH

**Issue**: State machine stuck
- Review `ctx.last_error_report` for malformed data
- Check agent adapters for timeout/error handling
- Verify circuit breaker thresholds in `config/circuit_breakers.yaml`

**Issue**: Cache not updating
- Delete `.state/validation_cache.json` and re-run
- Check file permissions on cache directory

## See Also

- [Error Plugins README](../plugins/README.md)
- [Operating Contract](../../docs/operating_contract.md)
- [CI Path Standards](../../docs/CI_PATH_STANDARDS.md)
