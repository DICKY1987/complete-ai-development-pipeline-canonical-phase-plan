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
python -m tui_app.main

# Or use the launcher script
scripts\launch_tui.bat
```

### Method 3: With Options
```bash
# Start with a specific panel
python -m tui_app.main --panel pattern_activity

# Use mock data instead of real database
python -m tui_app.main --use-mock-data

# Run smoke test (launch and exit immediately)
python -m tui_app.main --smoke-test
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
**Status**: ✅ Fully Implemented

Shows pipeline summary with auto-refresh every 2 seconds:
- **Pipeline Status**: Current state (IDLE, RUNNING, ERROR)
- **Task Counts**: Total, Running, Completed, Failed
- **Active Workers**: Number of active executions
- **Recent Tasks**: Last 5 tasks with status indicators
  - 🟢 Green = Completed
  - 🟡 Yellow = Running
  - 🔴 Red = Failed
- **Last Updated**: Timestamp showing last refresh

### Pattern Activity (Press 'p')
**Status**: ✅ Fully Implemented

Displays pattern execution timeline with auto-refresh every 5 seconds:
- **Pattern Runs**: List of recent pattern executions
  - ✓ Completed (green)
  - ⟳ Running (yellow)
  - ✗ Failed (red)
- **Event Details**: Event log for selected run
- **Progress Tracking**: Percentage completion for each run
- **Phase Information**: Current phase for running patterns

### File Lifecycle (Press 'f')
**Status**: ⏳ Skeleton (Minimal implementation)

Will show:
- Files tracked by pipeline
- Current state (DISCOVERED, PROCESSING, IN_FLIGHT, etc.)
- Last updated timestamp
- Processing tool

*Note: Full implementation pending (Phase 5)*

### Tool Health (Press 't')
**Status**: ⏳ Skeleton (Minimal implementation)

Will show:
- Tool registry status (aim, aider, codex, etc.)
- Health indicators
- Configuration from `gui/ui_settings.yaml`

*Note: Full implementation pending (Phase 5)*

### Log Stream (Press 'l')
**Status**: ⏳ Skeleton (Minimal implementation)

Will show:
- Live pipeline logs
- Orchestrator output
- Real-time streaming (tail -f style)

*Note: Full implementation pending (Phase 5)*

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
- **UI Settings**: `gui/ui_settings.yaml`
- **Tool Modes**: Interactive vs headless configuration

### Auto-Refresh Rates
- Dashboard: 2 seconds
- Pattern Activity: 5 seconds
- File Lifecycle: 3 seconds (when implemented)
- Tool Health: 10 seconds (when implemented)
- Log Stream: 1 second (when implemented)

---

## Troubleshooting

### TUI Won't Launch

**Problem**: Double-clicking shortcut does nothing
- **Solution**: Check that textual is installed: `pip install textual>=0.40.0`
- **Solution**: Run from command line to see error messages: `python -m tui_app.main`

**Problem**: ImportError or ModuleNotFoundError
- **Solution**: Install all dependencies: `pip install -r config/requirements.txt`

### No Data Showing

**Problem**: Dashboard shows 0 tasks despite pipeline running
- **Solution**: Verify database exists: Check for `.worktrees/pipeline_state.db`
- **Solution**: Run with mock data to test TUI: `python -m tui_app.main --use-mock-data`

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
*Future feature (Phase 7)*
Configuration file: `tui_app/config/tui_config.yaml` (planned)

Will support:
- Custom refresh intervals
- Database path override
- Theme/color scheme
- Panel visibility

### Testing

**Smoke Test** (verify TUI launches):
```bash
python -m tui_app.main --smoke-test
```

**Unit Tests**:
```bash
python -m pytest tests/tui_panel_framework -v
```

**Integration Tests** (future):
```bash
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

### Completed (Phases 1-4)
- ✅ Textual framework integration
- ✅ SQLite database backend
- ✅ Auto-refresh (Dashboard & Pattern Activity)
- ✅ Desktop shortcut launcher
- ✅ Real-time monitoring

### In Progress (Phase 5)
- ⏳ Complete File Lifecycle panel
- ⏳ Complete Tool Health panel
- ⏳ Complete Log Stream panel

### Planned (Phases 6-7)
- 📋 Integration tests
- 📋 Visual polish (custom color scheme, status indicators)
- 📋 Configuration file (tui_config.yaml)
- 📋 Panel resizing and layouts

### Future Enhancements
- 🔮 Background service mode
- 🔮 System tray integration
- 🔮 Web dashboard (browser-based)
- 🔮 Multi-panel layouts (split views)
- 🔮 Interactive controls (start/stop jobs)

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
