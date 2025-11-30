# Desktop-Launchable TUI Interface - Implementation Plan

**Goal**: Create a desktop-launchable, real-time monitoring TUI interface for the AI Development Pipeline that opens via Windows shortcut with live data integration.

**User Requirements**:
- Enhanced TUI (Terminal-based) - leverage existing Textual framework
- Real-time dashboard monitoring with auto-refresh
- Desktop shortcut launcher (one-click start from desktop)
- Best execution approach (recommendation: foreground with optional background service)

---

## Executive Summary

The TUI framework is **95% complete** (tui_app/, 27 files, 1,910 LOC, 26 passing tests). Missing pieces:
1. **Textual dependency** not in requirements.txt (imported but not declared)
2. **Real data integration** - currently using InMemoryStateBackend (mock data)
3. **Desktop launcher** - no Windows shortcut or Start Menu integration
4. **Auto-refresh** - static snapshots, no real-time updates
5. **3 skeleton panels** - FileLifecyclePanel, ToolHealthPanel, LogStreamPanel need implementation

**Recommended Approach**: Foreground-first with optional background service wrapper for future expansion.

---

## Gap Analysis

### What Exists ✅
- **Complete TUI Framework** (tui_app/main.py)
  - Textual-based app with 5 registered panels
  - PanelPlugin protocol, PanelRegistry, BasicLayoutManager
  - StateClient with pluggable backend architecture
  - PatternClient for pattern execution visualization
  - Key bindings: q (quit), d (dashboard), f (files), t (tools), l (logs), p (patterns)

- **Working Panels** (2/5 complete)
  - DashboardPanel - Pipeline summary, task list (COMPLETE)
  - PatternActivityPanel - Pattern execution timeline (COMPLETE)
  - FileLifecyclePanel (skeleton)
  - ToolHealthPanel (skeleton)
  - LogStreamPanel (skeleton)

- **Data Models & CLI** (gui/)
  - ui_cli.py - JSON-based state queries
  - ui_models.py - FileState, ToolHealth, WorkstreamStatus types
  - ui_settings.yaml - Tool configuration

- **Test Coverage**
  - 26 passing tests for TUI framework
  - test_panel_registry.py, test_state_client.py, test_pattern_client.py

### What's Missing ❌

1. **Dependency Declaration**
   - Textual not in config/requirements.txt
   - Need to add: `textual>=0.40.0`

2. **Real Database Backend**
   - StateClient uses InMemoryStateBackend (mock data)
   - Need: SQLiteStateBackend connecting to .worktrees/pipeline_state.db
   - Database exists but no backend implementation

3. **Desktop Launcher Infrastructure**
   - No Windows .lnk shortcut
   - No Start Menu integration
   - No launch script optimized for GUI execution
   - No terminal profile for dedicated window

4. **Auto-Refresh System**
   - Current: Static snapshots on panel mount
   - Need: Periodic refresh (1-5 seconds) or event-driven updates

5. **Panel Implementations**
   - FileLifecyclePanel - needs file tracking logic
   - ToolHealthPanel - needs tool status queries
   - LogStreamPanel - needs log tailing functionality

6. **Background Execution Mode** (optional, for future)
   - No system tray integration
   - No service wrapper
   - No background/foreground toggle

---

## Architecture Decisions

### 1. Execution Mode: **Foreground-First with Service Path**

**Recommended**: Foreground (simple, immediate)

**Rationale**:
- TUI apps naturally run in foreground (terminal window)
- User wants real-time monitoring → window should stay visible
- Simpler to implement and debug
- Future upgrade path: Add PowerShell service wrapper if needed

**Implementation**:
```
┌──────────────────────────────────┐
│   Windows Desktop Shortcut       │
│   (PipelineTUI.lnk)              │
│   Target: launch_tui.bat         │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│   launch_tui.bat                 │
│   - Set working directory        │
│   - Activate venv if present     │
│   - Launch: python -m gui.tui_app.main
│   - Keep window open on error    │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│   tui_app/main.py                │
│   - SQLiteStateBackend           │
│   - Auto-refresh enabled         │
│   - Full-screen TUI              │
└──────────────────────────────────┘
```

**Alternative** (future enhancement): Background service mode
- PowerShell wrapper running TUI in background
- System tray icon with show/hide
- Deferred to Phase 5 (not in scope)

### 2. Data Refresh Strategy: **Polling with Configurable Interval**

**Recommended**: Timer-based polling (Textual set_interval)

**Rationale**:
- Simple to implement (Textual built-in support)
- Configurable refresh rate per panel
- No event bus infrastructure needed initially
- Works with current SQLite backend

**Implementation**:
```python
class DashboardPanel(PanelPlugin):
    def compose(self) -> ComposeResult:
        yield Static(id="dashboard-content")

    def on_mount(self) -> None:
        self.set_interval(2.0, self._refresh_data)  # 2-second refresh

    def _refresh_data(self) -> None:
        summary = self.context.state_client.get_pipeline_summary()
        self.query_one("#dashboard-content").update(self._render(summary))
```

**Refresh Rates**:
- DashboardPanel: 2 seconds
- PatternActivityPanel: 5 seconds
- FileLifecyclePanel: 3 seconds
- ToolHealthPanel: 10 seconds
- LogStreamPanel: 1 second (log streaming)

**Alternative** (future): Event-driven updates via EventBus
- Requires orchestrator integration
- More complex, deferred to Phase 4

### 3. Launcher Mechanism: **Batch Script + Windows Shortcut**

**Recommended**: .bat launcher + .lnk shortcut

**Components**:
1. `launch_tui.bat` - Bootstrap script
   - Sets PYTHONPATH, activates venv
   - Launches TUI with error handling
   - Keeps window open on crash

2. `PipelineTUI.lnk` - Desktop shortcut
   - Target: launch_tui.bat
   - Icon: Custom .ico (optional)
   - Run: Normal window
   - Start in: Project root

3. Start Menu integration (optional)
   - Copy .lnk to: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\`

**Implementation Pattern** (following existing scripts/bootstrap.ps1 style):
```batch
@echo off
setlocal EnableDelayedExpansion

REM Set working directory
cd /d "%~dp0"

REM Activate virtual environment if exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Launch TUI
python -m gui.tui_app.main

REM Keep window open on error
if errorlevel 1 (
    echo.
    echo TUI exited with error. Press any key to close...
    pause >nul
)
```

---

## Phase Plan

### Phase 1: Foundation Setup ⚡ (15 mins)

**Objective**: Add Textual dependency and verify TUI launches

**Steps**:
1. Add `textual>=0.40.0` to config/requirements.txt
2. Install: `pip install textual`
3. Smoke test: `python -m gui.tui_app.main --smoke-test`
4. Verify exit code 0

**Files Modified**:
- config/requirements.txt

**Success Criteria**:
- ✅ Textual installed without conflicts
- ✅ TUI launches and exits cleanly

**Testing**:
```bash
python -m gui.tui_app.main --smoke-test
echo Exit code: %ERRORLEVEL%
```

---

### Phase 2: Real Data Integration 🔌 (45 mins)

**Objective**: Connect TUI to real SQLite databases with live data

**Steps**:

#### 2A: Implement SQLiteStateBackend
1. Create `tui_app/core/sqlite_state_backend.py`
2. Implement StateBackend protocol:
   ```python
   class SQLiteStateBackend(StateBackend):
       def __init__(self, db_path: str = ".worktrees/pipeline_state.db"):
           self.db_path = db_path
           self.conn = sqlite3.connect(db_path, check_same_thread=False)

       def get_pipeline_summary(self) -> PipelineSummary:
           # Query: SELECT COUNT(*) FROM tasks WHERE status = 'running'
           # Query: SELECT COUNT(*) FROM tasks WHERE status = 'completed'
           # etc.

       def get_tasks(self, limit: int = 100) -> List[TaskInfo]:
           # Query: SELECT * FROM tasks ORDER BY start_time DESC LIMIT ?
   ```

3. Update tui_app/main.py to use SQLite backend:
   ```python
   from tui_app.core.sqlite_state_backend import SQLiteStateBackend

   # Change line 61:
   self.state_client = StateClient(SQLiteStateBackend())
   ```

#### 2B: Database Schema Validation
1. Verify tables exist in .worktrees/pipeline_state.db
2. Check columns: tasks table (task_id, name, status, worker_id, start_time, end_time, error_message)
3. If missing, seed with test data or integrate with orchestrator schema

#### 2C: Pattern Data Integration
1. Implement SQLitePatternStateStore (or use in-memory for now)
2. Hook into pattern automation.db (UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/metrics/)

**Files Created**:
- tui_app/core/sqlite_state_backend.py
- tui_app/core/sqlite_pattern_store.py (optional, can defer)

**Files Modified**:
- tui_app/main.py (change backend initialization)

**Success Criteria**:
- ✅ TUI displays real pipeline data (not mock)
- ✅ Dashboard shows actual running tasks
- ✅ No "No tasks" when tasks exist in DB

**Testing**:
```bash
# Verify database exists and has data
sqlite3 .worktrees/pipeline_state.db "SELECT COUNT(*) FROM tasks"

# Launch TUI and verify data
python -m gui.tui_app.main --panel dashboard
# Press 'q' to quit
```

---

### Phase 3: Auto-Refresh Implementation 🔄 (30 mins)

**Objective**: Enable real-time monitoring with periodic data refresh

**Steps**:

1. Update DashboardPanel with auto-refresh:
   ```python
   # tui_app/panels/dashboard_panel.py

   def on_mount(self) -> None:
       self.set_interval(2.0, self._refresh_dashboard)  # 2s refresh

   def _refresh_dashboard(self) -> None:
       summary = self.context.state_client.get_pipeline_summary()
       tasks = self.context.state_client.get_tasks(limit=10)
       # Update widgets with new data
   ```

2. Update PatternActivityPanel with 5s refresh

3. Add refresh indicator to panels:
   ```python
   # Show "Last updated: HH:MM:SS" in panel footer
   from datetime import datetime

   def _refresh_dashboard(self) -> None:
       # ... fetch data ...
       self.last_updated = datetime.now().strftime("%H:%M:%S")
       # Update UI with last_updated
   ```

4. Add manual refresh keybinding:
   ```python
   # tui_app/main.py - add to BINDINGS:
   ("r", "refresh", "Refresh"),
   ```

**Files Modified**:
- tui_app/panels/dashboard_panel.py
- tui_app/panels/pattern_activity_panel.py
- tui_app/main.py (add refresh keybinding)

**Success Criteria**:
- ✅ Dashboard updates every 2 seconds automatically
- ✅ "Last updated" timestamp visible
- ✅ 'r' key forces immediate refresh

**Testing**:
```bash
# Launch TUI and watch for updates
python -m gui.tui_app.main --panel dashboard
# Watch task counts change (if pipeline is running)
# Press 'r' to force refresh
```

---

### Phase 4: Desktop Launcher 🚀 (30 mins)

**Objective**: Create Windows desktop shortcut for one-click TUI launch

**Steps**:

#### 4A: Create Launch Script
1. Create `scripts/launch_tui.bat`:
   ```batch
   @echo off
   REM AI Pipeline TUI Launcher

   cd /d "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan"

   if exist ".venv\Scripts\activate.bat" (
       call .venv\Scripts\activate.bat
   )

   REM Set window title
   title AI Pipeline TUI - Monitoring Dashboard

   REM Launch TUI
   python -m gui.tui_app.main

   REM Keep window open on error
   if errorlevel 1 (
       echo.
       echo [ERROR] TUI crashed. Check logs above.
       pause
   )
   ```

2. Make script executable and test:
   ```cmd
   scripts\launch_tui.bat
   ```

#### 4B: Create Desktop Shortcut
1. Create PowerShell shortcut generator: `scripts/create_desktop_shortcut.ps1`:
   ```powershell
   $WshShell = New-Object -ComObject WScript.Shell
   $DesktopPath = [System.Environment]::GetFolderPath('Desktop')
   $ShortcutPath = Join-Path $DesktopPath "AI Pipeline TUI.lnk"
   $Shortcut = $WshShell.CreateShortcut($ShortcutPath)

   $ProjectRoot = "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan"
   $Shortcut.TargetPath = "$ProjectRoot\scripts\launch_tui.bat"
   $Shortcut.WorkingDirectory = $ProjectRoot
   $Shortcut.Description = "AI Pipeline TUI - Real-time Monitoring Dashboard"
   # Optional: $Shortcut.IconLocation = "$ProjectRoot\gui\icon.ico,0"

   $Shortcut.Save()
   Write-Host "Desktop shortcut created: $ShortcutPath"
   ```

2. Run shortcut generator:
   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts\create_desktop_shortcut.ps1
   ```

#### 4C: Start Menu Integration (Optional)
1. Copy shortcut to Start Menu:
   ```powershell
   $StartMenuPath = [System.Environment]::GetFolderPath('Programs')
   Copy-Item "$DesktopPath\AI Pipeline TUI.lnk" "$StartMenuPath\"
   ```

**Files Created**:
- scripts/launch_tui.bat
- scripts/create_desktop_shortcut.ps1
- Desktop: "AI Pipeline TUI.lnk"

**Success Criteria**:
- ✅ Double-click desktop shortcut opens TUI in new window
- ✅ Window title shows "AI Pipeline TUI - Monitoring Dashboard"
- ✅ TUI launches with correct working directory
- ✅ Window stays open on error with helpful message

**Testing**:
1. Double-click "AI Pipeline TUI.lnk" on desktop
2. Verify TUI opens in dedicated terminal
3. Test error handling: corrupt database path → window should stay open

---

### Phase 5: Panel Completion 📊 (60 mins)

**Objective**: Implement 3 skeleton panels with real functionality

**Steps**:

#### 5A: FileLifecyclePanel
```python
# tui_app/panels/file_lifecycle_panel.py

from textual.widgets import DataTable

def compose(self) -> ComposeResult:
    table = DataTable()
    table.add_columns("File", "State", "Last Updated", "Tool")
    yield table

def on_mount(self) -> None:
    self.set_interval(3.0, self._refresh_files)

def _refresh_files(self) -> None:
    # Query files from StateClient (needs get_files method)
    files = self.context.state_client.get_files(limit=50)
    table = self.query_one(DataTable)
    table.clear()
    for file in files:
        table.add_row(file.path, file.state, file.updated_at, file.tool)
```

**Data Source**:
- Extend StateClient with `get_files()` method
- Query: `SELECT path, state, updated_at, tool FROM files ORDER BY updated_at DESC LIMIT ?`

#### 5B: ToolHealthPanel
```python
# tui_app/panels/tool_health_panel.py

from textual.widgets import Static
from textual.containers import Grid

def compose(self) -> ComposeResult:
    yield Grid(id="tool-grid")

def on_mount(self) -> None:
    self.set_interval(10.0, self._refresh_tools)

def _refresh_tools(self) -> None:
    tools = self.context.state_client.get_tool_status()
    grid = self.query_one("#tool-grid")
    grid.remove_children()
    for tool in tools:
        grid.mount(Static(f"{tool.name}: {tool.status}"))
```

**Data Source**:
- Extend StateClient with `get_tool_status()` method
- Read from gui/ui_settings.yaml tool_modes
- Optional: Query tool heartbeat from database

#### 5C: LogStreamPanel
```python
# tui_app/panels/log_stream_panel.py

from textual.widgets import RichLog

def compose(self) -> ComposeResult:
    yield RichLog(highlight=True, markup=True)

def on_mount(self) -> None:
    self.set_interval(1.0, self._tail_logs)
    self.log_position = 0

def _tail_logs(self) -> None:
    log_widget = self.query_one(RichLog)
    # Read new log lines from file (tail -f style)
    with open("logs/pipeline.log", "r") as f:
        f.seek(self.log_position)
        new_lines = f.readlines()
        self.log_position = f.tell()
        for line in new_lines:
            log_widget.write(line.strip())
```

**Data Source**:
- Log files in project (e.g., logs/pipeline.log)
- Or orchestrator output (capture stdout)

**Files Modified**:
- tui_app/panels/file_lifecycle_panel.py (complete implementation)
- tui_app/panels/tool_health_panel.py (complete implementation)
- tui_app/panels/log_stream_panel.py (complete implementation)
- tui_app/core/state_client.py (add get_files, get_tool_status methods)

**Success Criteria**:
- ✅ Press 'f' → file lifecycle table displays real files
- ✅ Press 't' → tool health shows aim, aider, codex status
- ✅ Press 'l' → log stream shows live pipeline logs

---

### Phase 6: Testing & Documentation 📝 (30 mins)

**Objective**: Validate all components and document usage

**Steps**:

#### 6A: Integration Testing
1. Create test script: `tests/test_tui_integration.py`
   ```python
   def test_tui_launches_with_sqlite_backend():
       from tui_app.main import PipelineTUI
       from tui_app.core.sqlite_state_backend import SQLiteStateBackend

       app = PipelineTUI(smoke_test=True)
       assert isinstance(app.state_client._backend, SQLiteStateBackend)

   def test_all_panels_render():
       # Test each panel creates widgets
       for panel_id in ["dashboard", "file_lifecycle", "tool_health", "log_stream", "pattern_activity"]:
           # ... validate panel ...
   ```

2. Run full test suite:
   ```bash
   python -m pytest tests/tui_panel_framework -v
   python -m pytest tests/test_tui_integration.py -v
   ```

#### 6B: User Documentation
1. Create `docs/GUI_QUICK_START.md`:
   ```markdown
   # TUI Quick Start Guide

   ## Installation
   1. Install dependencies: `pip install -r config/requirements.txt`
   2. Create desktop shortcut: `powershell scripts/create_desktop_shortcut.ps1`

   ## Launching
   - Double-click "AI Pipeline TUI" on desktop
   - Or: `python -m gui.tui_app.main`

   ## Keyboard Shortcuts
   - `d` - Dashboard (default)
   - `f` - File Lifecycle
   - `t` - Tool Health
   - `l` - Log Stream
   - `p` - Pattern Activity
   - `r` - Refresh Now
   - `q` - Quit

   ## Troubleshooting
   - TUI won't launch → Check `pip install textual`
   - No data showing → Verify `.worktrees/pipeline_state.db` exists
   - Slow refresh → Adjust interval in panel code
   ```

2. Update `tui_app/README.md` with desktop shortcut instructions

**Files Created**:
- tests/test_tui_integration.py
- docs/GUI_QUICK_START.md

**Files Modified**:
- tui_app/README.md

**Success Criteria**:
- ✅ All tests pass (30+ tests)
- ✅ Documentation covers installation, launch, usage
- ✅ Troubleshooting section addresses common issues

---

### Phase 7: Polish & Packaging 🎨 (20 mins)

**Objective**: Final touches for professional desktop experience

**Steps**:

#### 7A: Visual Polish
1. Add custom color scheme to tui_app/main.py:
   ```python
   CSS = """
   Screen {
       background: $surface;
   }

   Header {
       background: #2563eb;  /* Blue */
       color: white;
   }

   Footer {
       background: #1e40af;  /* Dark blue */
       color: white;
   }

   .success { color: #10b981; }  /* Green */
   .error { color: #ef4444; }    /* Red */
   .warning { color: #f59e0b; }  /* Orange */
   ```

2. Add status indicators to dashboard:
   - Green checkmark for running
   - Red X for failed
   - Yellow ! for warnings

#### 7B: Error Handling
1. Add database connection retry logic:
   ```python
   def _connect_with_retry(db_path: str, max_retries: int = 3):
       for attempt in range(max_retries):
           try:
               return sqlite3.connect(db_path, check_same_thread=False)
           except sqlite3.Error as e:
               if attempt == max_retries - 1:
                   raise
               time.sleep(1)
   ```

2. Add graceful degradation:
   - If database unavailable → show error panel with instructions
   - If panel fails to render → show fallback message

#### 7C: Configuration File
1. Create `tui_app/config/tui_config.yaml`:
   ```yaml
   database:
     path: .worktrees/pipeline_state.db
     timeout: 5.0

   refresh:
     dashboard: 2.0
     pattern_activity: 5.0
     file_lifecycle: 3.0
     tool_health: 10.0
     log_stream: 1.0

   appearance:
     theme: dark
     show_timestamps: true
     max_log_lines: 1000
   ```

2. Load config in main.py

**Files Created**:
- tui_app/config/tui_config.yaml

**Files Modified**:
- tui_app/main.py (add CSS, load config)
- tui_app/core/sqlite_state_backend.py (add retry logic)

**Success Criteria**:
- ✅ TUI has professional color scheme
- ✅ Status indicators use color coding
- ✅ Database errors show helpful messages
- ✅ Configuration loaded from YAML

---

## Implementation Summary

### Files to Create (11 new files)
1. `tui_app/core/sqlite_state_backend.py` - Real database backend
2. `tui_app/core/sqlite_pattern_store.py` - Pattern data backend (optional)
3. `tui_app/config/tui_config.yaml` - TUI configuration
4. `scripts/launch_tui.bat` - Windows launcher script
5. `scripts/create_desktop_shortcut.ps1` - Shortcut generator
6. `tests/test_tui_integration.py` - Integration tests
7. `tests/test_sqlite_backend.py` - Backend unit tests
8. `docs/GUI_QUICK_START.md` - User documentation
9. Desktop: `AI Pipeline TUI.lnk` - Shortcut file (generated)

### Files to Modify (8 files)
1. `config/requirements.txt` - Add textual>=0.40.0
2. `tui_app/main.py` - Switch to SQLiteStateBackend, add CSS, config loading
3. `tui_app/panels/dashboard_panel.py` - Add auto-refresh
4. `tui_app/panels/pattern_activity_panel.py` - Add auto-refresh
5. `tui_app/panels/file_lifecycle_panel.py` - Complete implementation
6. `tui_app/panels/tool_health_panel.py` - Complete implementation
7. `tui_app/panels/log_stream_panel.py` - Complete implementation
8. `tui_app/core/state_client.py` - Add get_files(), get_tool_status()

### Files to Read (critical references during implementation)
1. `.worktrees/pipeline_state.db` - Database schema inspection
2. `gui/ui_models.py` - Data model definitions
3. `gui/ui_settings.yaml` - Tool configuration
4. `tui_app/core/panel_plugin.py` - Panel protocol
5. `TUI_PANEL_FRAMEWORK_COMPLETION_REPORT.md` - Architecture reference

---

## Testing Strategy

### Unit Tests
- `test_sqlite_backend.py` - SQLiteStateBackend queries
- `test_state_client.py` - Extended with new methods
- `test_panel_registry.py` - Existing (no changes)

### Integration Tests
- `test_tui_integration.py` - End-to-end TUI launch with real backend
- `test_panels_smoke.py` - Extend to validate all 5 panels render with real data

### Manual Testing
1. **Desktop Shortcut**: Double-click, verify window opens
2. **Real-time Updates**: Launch TUI, run pipeline, watch dashboard update
3. **Panel Navigation**: Press d/f/t/l/p, verify panels switch
4. **Error Handling**: Corrupt database, verify graceful error message
5. **Performance**: Monitor CPU/memory with auto-refresh enabled

---

## Success Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| Desktop Launch Time | < 3 seconds | Stopwatch from double-click to dashboard visible |
| Refresh Rate | 2s dashboard, 1s logs | Check last_updated timestamp |
| Test Coverage | 100% new code | pytest --cov |
| Memory Usage | < 100 MB | Task Manager while running |
| Database Query Time | < 100ms per query | Add logging to backend |
| All Panels Functional | 5/5 panels | Manual test: press each key binding |

---

## Execution Timeline

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Phase 1: Foundation | 15 mins | 0:15 |
| Phase 2: Data Integration | 45 mins | 1:00 |
| Phase 3: Auto-Refresh | 30 mins | 1:30 |
| Phase 4: Desktop Launcher | 30 mins | 2:00 |
| Phase 5: Panel Completion | 60 mins | 3:00 |
| Phase 6: Testing & Docs | 30 mins | 3:30 |
| Phase 7: Polish | 20 mins | 3:50 |

**Total**: ~4 hours (can be reduced to 2-3 hours if panels deferred)

---

## Risk Mitigation

### Risk 1: Database Schema Mismatch
- **Mitigation**: Inspect .worktrees/pipeline_state.db with sqlite3 browser first
- **Fallback**: If schema doesn't match, seed with test data

### Risk 2: Textual Version Conflicts
- **Mitigation**: Pin exact version: `textual==0.40.0`
- **Fallback**: Use older Textual version if conflicts arise

### Risk 3: Auto-Refresh Performance
- **Mitigation**: Make refresh rates configurable in tui_config.yaml
- **Fallback**: Disable auto-refresh, use manual 'r' key only

### Risk 4: Windows Terminal Compatibility
- **Mitigation**: Test on both cmd.exe and Windows Terminal
- **Fallback**: Document required terminal (Windows Terminal recommended)

### Risk 5: Database Lock Contention
- **Mitigation**: Use `check_same_thread=False` and readonly connections
- **Fallback**: Add connection pooling or WAL mode

---

## Future Enhancements (Out of Scope)

### Phase 8: Background Service Mode (optional)
- PowerShell service wrapper
- System tray icon (using pystray)
- Show/hide TUI window
- Auto-start on Windows login

### Phase 9: Web Dashboard (alternative UI)
- FastAPI backend
- React/Vue frontend
- Same StateClient backend (code reuse)
- Accessible via browser: http://localhost:8080

### Phase 10: Multi-Panel Layouts
- Implement MultiPanelLayoutManager
- Split views: dashboard + logs side-by-side
- Resizable panels

### Phase 11: Interactive Controls
- Start/pause/cancel buttons
- Error quarantine management
- Tool configuration UI

---

## Execution Pattern References

This plan follows these documented execution patterns:

1. **PAT-GUI-PANEL-FRAMEWORK-001** - Panel plugin architecture (already used in TUI framework)
2. **PAT-ATOMIC-CREATE-001** - Batch file creation in phases
3. **PAT-TUI-FIRST-BOOTSTRAP** - TUI-first with optional GUI wrapper (future)

Pattern files: `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/`

---

## Recommended Execution Order

**Priority 1** (MVP - Desktop-launchable TUI with real data):
- Phase 1: Foundation Setup
- Phase 2: Real Data Integration
- Phase 4: Desktop Launcher

**Priority 2** (Real-time monitoring):
- Phase 3: Auto-Refresh Implementation

**Priority 3** (Full panel suite):
- Phase 5: Panel Completion (FileLifecycle, ToolHealth, LogStream)

**Priority 4** (Production-ready):
- Phase 6: Testing & Documentation
- Phase 7: Polish & Packaging

**Can execute Phases 1-4 in ~2 hours** for immediate usable desktop TUI with real data.

---

## Notes

- All code follows project patterns: minimal changes, type hints, dataclasses
- SQLiteStateBackend reuses existing database schema (no schema modifications)
- Desktop shortcut uses PowerShell (Windows-native, follows existing scripts/bootstrap.ps1 pattern)
- Foreground execution chosen for simplicity; background mode deferred to future
- Panel implementations use Textual widgets: DataTable, RichLog, Grid, Static
- Auto-refresh uses Textual's built-in `set_interval()` (no external dependencies)
