---
doc_id: DOC-GUIDE-CLAUDE-CLAUDE-001
---

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Context

This is the **GUI module** of the Complete AI Development Pipeline project. It contains:
- **Design documentation** for a hybrid GUI/TUI/Terminal architecture
- **Python TUI implementation** for pipeline state visualization
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
│   - TUI implementation      │
│   - Configuration           │     Tool configs
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

From `gui/README.md` and `gui/docs/GUI_DEVELOPMENT_GUIDE.md`:

1. **Read-heavy, write-light**: GUI primarily observes state, rarely mutates
2. **Headless-first**: Everything GUI does must work via CLI/API
3. **Safe-by-default**: Explicit confirmation for destructive actions
4. **Panel-based plugins**: Extensible dashboard architecture
5. **No direct file system access**: All queries through state API

## Current File Structure (as of merge)

```
gui/
├── config/                   # Configuration files (e.g., tool_settings.yaml)
│   └── tool_settings.yaml    # Renamed from ui_settings.yaml
├── docs/                     # Design documentation (moved from gui/)
├── tests/                    # Test files
│   └── tui_panel_framework/  # TUI Panel Framework tests
├── tui_app/                  # TUI implementation
│   ├── __init__.py           # Python package initializer
│   ├── main.py               # TUI application entry point
│   ├── README.md             # TUI usage documentation
│   ├── config/               # TUI specific configuration
│   ├── core/                 # TUI core logic (panels, state, pattern clients)
│   └── panels/               # TUI panel implementations
├── .ai-module-manifest       # AI module manifest
├── CLAUDE.md                 # This guidance document
└── README.md                 # Combined GUI/TUI overview
```

## Testing

```bash
# Run GUI tests (from gui/ directory)
python -m pytest gui/tests/tui_panel_framework/

# Run all project tests (from parent directory)
cd .. && python -m pytest tests/
```

## Integration with Parent Project

### Import Patterns

When integrating with the parent pipeline:

```python
# State client (queries database)
from core.ui_clients import StateClient, LogsClient, ToolsClient # Assuming these exist in core

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
2. **TUI/GUI** consumes state DB via `StateClient` and `PatternClient` to render panels

### Database Location

Default: `../.worktrees/pipeline_state.db`

Override via:
- Environment variable (see parent project settings)

## Development Phases

From `gui/docs/GUI_DEVELOPMENT_GUIDE.md`:

- ✅ **Phase 1**: Engine foundation (in `../engine/`)
- ✅ **Phase 2A**: State store integration
- ✅ **Phase 2B**: Additional adapters (Codex, Tests, Git)
- ⏳ **Phase 3**: GUI shell with panel plugins (NOT YET IMPLEMENTED)
- ⏳ **Phase 4**: Pipeline Radar panel
- ⏳ **Phase 5**: Permission enforcement

### Next Steps for GUI Implementation

When implementing GUI panels:

1. Create panel plugin structure in `gui/tui_app/panels/`
2. Implement `ServiceLocator` pattern for dependency injection
3. Follow panel plugin manifest format (see `gui/docs/GUI_DEVELOPMENT_GUIDE.md`)
4. Enforce permissions matrix (see `gui/README.md`)

## Tool Configuration

From `gui/config/tool_settings.yaml`:

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
- `gui/docs/GUI_DEVELOPMENT_GUIDE.md` - Implementation roadmap
- `gui/docs/hybrid-ui-architecture.md` - Multi-mode UI design
- `gui/docs/pipeline-radar-plugin.md` - Real-time pipeline monitoring spec
- `gui/docs/GUI_PLAN_EXECUTION_PATTERNS.md` - Execution patterns
- `gui/docs/UI_QUICK_REFERENCE.md` - Quick reference guide

## Security & Permissions

From `gui/docs/GUI_PERMISSIONS_MATRIX.md` (referenced in `gui/README.md`):

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
- Dataclasses for models
- Enum for state constants
- JSON output via `json.dumps(indent=2)` for CLI tools

## Testing Strategy

- **Unit tests**: `gui/tests/tui_panel_framework/` (settings management)
- **Integration tests**: In `../tests/` (cross-module)
- **GUI tests**: Not yet implemented (Phase 3+)

When adding tests:
```bash
# Run from gui/ directory
python -m pytest gui/tests/tui_panel_framework/ -v

# Run with coverage
python -m pytest --cov=gui/tui_app gui/tests/tui_panel_framework/
```

## Notes for Future Development

1. **Panel Plugins**: Follow `dashboard.panel.json` manifest pattern (see `gui/docs/GUI_DEVELOPMENT_GUIDE.md`)
2. **Real-time Updates**: Consider WebSocket or polling (design docs suggest both)
3. **PyQt6 vs Web**: Design supports both (not decided yet)
4. **State Client**: Wrapper around `../core/state/db.py` queries

## Related Directories

- `../engine/` - Job orchestrator and adapters
- `../core/state/` - Database and state management
- `../core/engine/` - Execution orchestrator
- `../examples/` - Usage examples
- `../docs/` - Project-wide documentation
