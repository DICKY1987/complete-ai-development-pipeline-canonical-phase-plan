---
status: draft
doc_type: guide
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-GUI_QUICK_START-118
---

# TUI Quick Start Guide

**AI Pipeline TUI - Desktop-Launchable Real-time Monitoring Dashboard**

---

## Installation

### Prerequisites
- Python 3.12+
- All project dependencies installed

### Setup

1. **Install Dependencies**
   ```bash
   pip install -r config/requirements.txt
   ```

   This will install Textual (>= 0.40.0) and all other required packages.

2. **Create Desktop Shortcut**

   The desktop shortcut has been created for you at:
   ```
   C:\Users\richg\OneDrive\Desktop\AI Pipeline TUI.lnk
   ```

   If you need to recreate it, run:
   ```bash
   powershell -ExecutionPolicy Bypass -File scripts\create_desktop_shortcut.ps1
   ```

---

## Launching the TUI

### Method 1: Desktop Shortcut (Recommended)
- Double-click **"AI Pipeline TUI"** icon on your desktop
- TUI opens in a dedicated terminal window

### Method 2: Command Line
```bash
# From project root
python -m gui.tui_app.main

# Or use the launcher script
scripts\launch_tui.bat
```

### Method 3: With Options
```bash
# Start with a specific panel
python -m gui.tui_app.main --panel pattern_activity

# Dual layout (primary + secondary panel side-by-side)
python -m gui.tui_app.main --layout dual --secondary-panel log_stream

# Use mock data instead of real database
python -m gui.tui_app.main --use-mock-data

# Run smoke test (launch and exit immediately)
python -m gui.tui_app.main --smoke-test
```

---

## Keyboard Shortcuts

| Key | Action | Description |
|-----|--------|-------------|
| **q** | Quit | Exit the TUI |
| **r** | Refresh | Force immediate refresh of current panel |
| **d** | Dashboard | Switch to Dashboard panel (default) |
| **f** | Files | Switch to File Lifecycle panel |
| **t** | Tools | Switch to Tool Health panel |
| **l** | Logs | Switch to Log Stream panel |
| **p** | Patterns | Switch to Pattern Activity panel |

---

## Panels Overview

### Dashboard (Press 'd')
Status: Implemented

Auto-refresh (default 2s) with:
- Pipeline status (IDLE, RUNNING, ERROR)
- Task counts: Total, Running, Completed, Failed
- Active workers and recent tasks with status indicators
- Last updated timestamp

### Pattern Activity (Press 'p')
Status: Implemented

Shows pattern execution timeline (default 5s refresh):
- Pattern runs with status and progress
- Event details for the selected run (derived from SQLite patch ledger)
- Current phase for running patterns

### File Lifecycle (Press 'f')
Status: Implemented

- Patch ledger table: patch ID, execution, state, created time, files touched
- Summary counters for validated, pending, failed patches and running executions
- Refresh: every 3 seconds (configurable)

### Tool Health (Press 't')
Status: Implemented

- Parses `logs/combined.log` for tool registration/health signals
- Grid: tool name, status (OK/WARN/ERROR), last seen time, latest message
- Refresh: every 4 seconds (configurable)

### Log Stream (Press 'l')
Status: Implemented

- Live tail of the configured log file
- Defaults: `logs/combined.log`, last 60 lines
- Refresh: every 3 seconds (configurable)


---

## Data Sources

The TUI connects to real pipeline data by default:

### Database
- **Path**: `.worktrees/pipeline_state.db`
- **Tables**:
  - `uet_executions` - Execution tracking
  - `uet_tasks` - Task management
  - `patch_ledger` - Patch tracking

### Configuration
- **TUI Config**: `tui_app/config/tui_config.yaml` (theme, refresh rates, log path)
- **Tool Modes**: Interactive vs headless configuration

### Auto-Refresh Rates (defaults)
- Dashboard: 2 seconds
- Pattern Activity: 5 seconds
- File Lifecycle: 3 seconds
- Tool Health: 4 seconds
- Log Stream: 3 seconds
- Configure via: `tui_app/config/tui_config.yaml`


---

## Troubleshooting

### TUI Won't Launch

**Problem**: Double-clicking shortcut does nothing
- **Solution**: Check that textual is installed: `pip install textual>=0.40.0`
- **Solution**: Run from command line to see error messages: `python -m gui.tui_app.main`

**Problem**: ImportError or ModuleNotFoundError
- **Solution**: Install all dependencies: `pip install -r config/requirements.txt`

### No Data Showing

**Problem**: Dashboard shows 0 tasks despite pipeline running
- **Solution**: Verify database exists: Check for `.worktrees/pipeline_state.db`
- **Solution**: Run with mock data to test TUI: `python -m gui.tui_app.main --use-mock-data`

**Problem**: Database file not found
- **Solution**: Create the database directory: `mkdir .worktrees`
- **Solution**: Run a pipeline execution to populate database

### Performance Issues

**Problem**: TUI feels slow or laggy
- **Solution**: Adjust refresh rates in panel code (reduce frequency)
- **Solution**: Disable auto-refresh: Press 'r' only when needed (future: add config option)

**Problem**: High CPU usage
- **Solution**: Check database size - large databases slow queries
- **Solution**: Use Windows Terminal instead of cmd.exe for better performance

### Display Issues

**Problem**: Characters not displaying correctly (boxes, missing symbols)
- **Solution**: Use Windows Terminal (recommended) instead of cmd.exe
- **Solution**: Install a Nerd Font for better Unicode support

**Problem**: Colors not showing
- **Solution**: Enable ANSI color support in terminal
- **Solution**: Use Windows Terminal which supports colors by default

---

## Advanced Usage

### Running in Background
*Future feature (Phase 8)*
Currently, TUI runs in foreground only. Background service mode planned.

### Custom Configuration
Configuration file: `tui_app/config/tui_config.yaml`

Supports:
- Refresh intervals per panel
- Theme/color palette
- Log path and tail length
- Panel defaults and shortcuts
- Dual layout defaults (secondary panel selection)

### Testing

**Smoke Test** (verify TUI launches):
```bash
python -m gui.tui_app.main --smoke-test
```

**Panel and client tests**:
```bash
python -m pytest tests/tui_panel_framework -v
```

**Backend + TUI integration**:
```bash
python -m pytest tests/test_sqlite_backend.py -v
python -m pytest tests/test_tui_integration.py -v
```


---

## Tips & Best Practices

### Recommended Terminal
- **Windows Terminal** - Best performance, full color support, modern UI
- **cmd.exe** - Works but limited color support
- **PowerShell** - Good alternative

### Database Management
- Database is READ-ONLY from TUI perspective
- Pipeline orchestrator writes to database
- TUI queries database via SQLiteStateBackend

### Panel Switching
- Switch panels frequently to monitor different aspects
- Use 'r' to force refresh when you see stale data
- Dashboard is best for quick overview

### Workflow Integration
1. Start TUI from desktop shortcut
2. Watch dashboard for active tasks
3. Switch to Pattern Activity to monitor pattern execution
4. Keep TUI open in background for real-time monitoring

---

## What's Next?

### Completed (Phases 1-7)
- Textual framework integration
- SQLite database backend
- Auto-refresh across panels
- Desktop shortcut launcher
- File Lifecycle panel
- Tool Health panel
- Log Stream panel
- TUI config + theme polish
- Integration tests
- Optional dual-pane layout (primary + secondary panel)
- Background-friendly launch script (`scripts/run_tui_background.ps1`)

### Planned (Phase 8+)
- Background service mode
- System tray integration
- Web dashboard (browser-based)
- Multi-panel layouts (split views)
- Interactive controls (start/stop jobs)


---

## Support

### Documentation
- **TUI Framework Guide**: `docs/gui/TUI_PANEL_FRAMEWORK_GUIDE.md`
- **GUI Development Guide**: `gui/GUI_DEVELOPMENT_GUIDE.md`
- **UI Templates**: `gui/README_UI.md`

### Getting Help
- Check `gui/CLAUDE.md` for project-specific instructions
- Review implementation plan: `C:\Users\richg\.claude\plans\enumerated-cuddling-frost.md`

---

## Summary

The AI Pipeline TUI is now **desktop-launchable** with:
- ✅ One-click launch from desktop shortcut
- ✅ Real-time data from SQLite database
- ✅ Auto-refresh every 2-5 seconds
- ✅ 5 panels (2 fully functional, 3 skeleton)
- ✅ Keyboard shortcuts for quick navigation

**Launch it now**: Double-click the "AI Pipeline TUI" icon on your desktop!
