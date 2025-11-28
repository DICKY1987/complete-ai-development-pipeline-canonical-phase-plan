# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Context

This is the **GUI module** of the Complete AI Development Pipeline project. It contains:
- **Design documentation** for a hybrid GUI/TUI/Terminal architecture
- **Python UI infrastructure** for pipeline state visualization
- **CLI tools** for querying pipeline state (for TUI/GUI consumption)
- **Configuration** for interactive tool selection and UI settings

**Critical**: This directory is primarily **design and infrastructure**, not a full GUI implementation yet. The actual execution engine lives in `../engine/` and core pipeline in `../core/`.

## Architecture Overview

### Hybrid Shell Pattern

The GUI follows a **hybrid shell** architecture:

```
┌─────────────────────────────┐
│   GUI/TUI Shell (PyQt6)     │  ← Visualization layer
│   - Dashboard panels        │
│   - Pipeline Radar          │
│   - Read-only queries       │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│   UI Infrastructure         │  ← Data layer (THIS DIRECTORY)
│   - ui_cli.py               │     Query CLI
│   - ui_models.py            │     Data models
│   - ui_settings.yaml        │     Tool configs
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│   Engine Orchestrator       │  ← Located in ../engine/
│   - Job dispatch            │
│   - State persistence       │
└─────────────────────────────┘
```

### Key Design Principles

From `gui/README.md` and `gui/GUI_DEVELOPMENT_GUIDE.md`:

1. **Read-heavy, write-light**: GUI primarily observes state, rarely mutates
2. **Headless-first**: Everything GUI does must work via CLI/API
3. **Safe-by-default**: Explicit confirmation for destructive actions
4. **Panel-based plugins**: Extensible dashboard architecture
5. **No direct file system access**: All queries through state API

## File Structure

```
gui/
├── ui_cli.py                 # CLI for querying pipeline state (JSON output)
├── ui_models.py              # Data models (FileState, ToolHealth, etc.)
├── ui_settings.yaml          # Tool mode configuration
├── ui_settings.py            # Settings management
├── ui_settings_cli.py        # Settings CLI interface
├── test_ui_settings.py       # Unit tests
├── ui_infrastructure_usage.py    # Usage examples
├── ui_tool_selection_demo.py     # Interactive tool selection demo
└── *.md                      # Design documentation
```

## Common Commands

### Query Pipeline State

```bash
# Dashboard summary
python ui_cli.py dashboard --json

# List files by state
python ui_cli.py files --state in_flight --json

# List workstreams for a run
python ui_cli.py workstreams --run-id run-123 --json

# Get tool health status
python ui_cli.py tools --json

# Query errors by severity
python ui_cli.py errors --severity error --json

# Get file counts by state
python ui_cli.py file-counts --run-id run-123 --json
```

### UI Settings Management

```bash
# View current settings
python ui_settings_cli.py show

# Change default interactive tool
python ui_settings_cli.py set default_interactive_tool codex

# Toggle tool headless mode
python ui_settings_cli.py toggle-headless aim
```

### Testing

```bash
# Run UI tests (from gui/ directory)
python -m pytest test_ui_settings.py

# Run all project tests (from parent directory)
cd .. && python -m pytest tests/
```

## Integration with Parent Project

### Import Patterns

When integrating with the parent pipeline:

```python
# State client (queries database)
from core.ui_clients import StateClient, LogsClient, ToolsClient

# Data models
from core.ui_models import (
    FileState,
    FileLifecycleRecord,
    ToolStatus,
    WorkstreamStatus,
    ErrorSeverity
)

# Example: Query files in a specific state
client = StateClient()
files = client.list_files(state=FileState.IN_FLIGHT, limit=50)
```

### Data Flow

1. **Engine** (in `../engine/`) executes jobs and updates state DB
2. **UI CLI** (`ui_cli.py`) reads state DB and emits JSON
3. **TUI/GUI** consumes JSON to render panels

### Database Location

Default: `../.worktrees/pipeline_state.db`

Override via:
- `--db-path` argument to `ui_cli.py`
- Environment variable (see parent project settings)

## UI Data Models

From `ui_models.py`:

### File Lifecycle States

```python
FileState.DISCOVERED       # Initial detection
FileState.CLASSIFIED       # Type identified
FileState.INTAKE           # Queued for processing
FileState.PROCESSING       # Tool actively working
FileState.IN_FLIGHT        # Between tools
FileState.AWAITING_REVIEW  # Ready for human review
FileState.COMMITTED        # Merged to repo
FileState.QUARANTINED      # Isolated due to errors
```

### Workstream Status

```python
WorkstreamStatus.QUEUED
WorkstreamStatus.RUNNING
WorkstreamStatus.SUCCEEDED
WorkstreamStatus.FAILED
WorkstreamStatus.CANCELLED
```

### Error Severity

```python
ErrorSeverity.INFO
ErrorSeverity.WARNING
ErrorSeverity.ERROR
ErrorSeverity.CRITICAL
```

## Development Phases

From `GUI_DEVELOPMENT_GUIDE.md`:

- ✅ **Phase 1**: Engine foundation (in `../engine/`)
- ✅ **Phase 2A**: State store integration
- ✅ **Phase 2B**: Additional adapters (Codex, Tests, Git)
- ⏳ **Phase 3**: GUI shell with panel plugins (NOT YET IMPLEMENTED)
- ⏳ **Phase 4**: Pipeline Radar panel
- ⏳ **Phase 5**: Permission enforcement

### Next Steps for GUI Implementation

When implementing GUI panels:

1. Create panel plugin structure in `gui/panels/`
2. Use `ui_cli.py` for data fetching (already works)
3. Implement `ServiceLocator` pattern for dependency injection
4. Follow panel plugin manifest format (see `GUI_DEVELOPMENT_GUIDE.md`)
5. Enforce permissions matrix (see `README.md`)

## Tool Configuration

From `ui_settings.yaml`:

```yaml
default_interactive_tool: aim

tool_modes:
  aim:
    default_mode: interactive
    supports_headless: true
  aider:
    default_mode: headless
    supports_headless: true
  codex:
    default_mode: headless
    supports_headless: true
```

**Interactive vs Headless**:
- **Interactive**: Requires user input (terminal session)
- **Headless**: Fully automated (JSON input/output)

## Design Documents

Key architecture documents in this directory:

- `README.md` - GUI overview and permissions matrix
- `GUI_DEVELOPMENT_GUIDE.md` - Implementation roadmap
- `Hybrid UI_GUI shell_terminal_TUI engine.md` - Multi-mode UI design
- `Pipeline Radar" plugin.md` - Real-time pipeline monitoring spec
- `GUI_PLAN_EXECUTION_PATTERNS.md` - Execution patterns
- `UI_QUICK_REFERENCE.md` - Quick reference guide

## Security & Permissions

From `GUI_PERMISSIONS_MATRIX.md` (referenced in `README.md`):

**GUI is NOT allowed to**:
- Modify code directly
- Install tools
- Execute arbitrary shell commands
- Access file system directly (must use state API)

**GUI is allowed to**:
- Query pipeline state (read-only)
- Start/pause/cancel runs (with confirmation)
- View logs via API
- Configure tool execution modes

## Code Style

- Python 3.12+
- Type hints for public functions
- Dataclasses for models (see `ui_models.py`)
- Enum for state constants
- JSON output via `json.dumps(indent=2)` for CLI tools

## Testing Strategy

- **Unit tests**: `test_ui_settings.py` (settings management)
- **Integration tests**: In `../tests/` (cross-module)
- **GUI tests**: Not yet implemented (Phase 3+)

When adding tests:
```bash
# Run from gui/ directory
python -m pytest test_*.py -v

# Run with coverage
python -m pytest --cov=. test_*.py
```

## Notes for Future Development

1. **Panel Plugins**: Follow `dashboard.panel.json` manifest pattern (see `GUI_DEVELOPMENT_GUIDE.md`)
2. **Real-time Updates**: Consider WebSocket or polling (design docs suggest both)
3. **PyQt6 vs Web**: Design supports both (not decided yet)
4. **State Client**: Wrapper around `../core/state/db.py` queries

## Related Directories

- `../engine/` - Job orchestrator and adapters
- `../core/state/` - Database and state management
- `../core/engine/` - Execution orchestrator
- `../examples/` - Usage examples
- `../docs/` - Project-wide documentation
