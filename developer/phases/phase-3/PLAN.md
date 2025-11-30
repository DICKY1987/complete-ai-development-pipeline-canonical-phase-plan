---
doc_id: DOC-GUIDE-PLAN-1277
---

# Phase 3: GUI Foundation - Implementation Plan

**Status**: Ready to Implement  
**Priority**: High (Recommended)  
**Estimated Duration**: 4-6 hours  
**Dependencies**: Phase 2 (Engine + State) Complete ✅

## Overview

Build a PyQt6-based GUI that provides visual interface for the job execution engine, following the hybrid GUI/Terminal architecture specified in `gui/` folder.

## Goals

1. Create production-ready GUI shell with panel plugin system
2. Enable visual monitoring of jobs, runs, and workstreams
3. Provide user-friendly alternative to CLI operations
4. Support real-time status updates and event streaming

## Architecture

### Component Stack

```
┌─────────────────────────────────────────┐
│         PyQt6 Main Window               │
│  (gui/shell/main_window.py)             │
└────────────┬────────────────────────────┘
             │
    ┌────────┴────────┐
    │   Panel System  │
    │   (plugin-based)│
    └────────┬────────┘
             │
    ┌────────┴────────────────────┐
    │      Service Layer          │
    ├─────────────────────────────┤
    │  • StateClient              │
    │  • EngineClient             │
    │  • EventBus                 │
    └────────┬────────────────────┘
             │
    ┌────────┴────────────────────┐
    │    Backend Integration      │
    ├─────────────────────────────┤
    │  • engine.state_store       │
    │  • engine.orchestrator      │
    │  • events table (polling)   │
    └─────────────────────────────┘
```

### Panel Plugin System

Each panel is a standalone plugin with:
- Manifest (metadata, version, dependencies)
- Widget class (PyQt6 QWidget)
- Data model (interacts with services)
- Lifecycle hooks (init, activate, deactivate)

## Phase Breakdown

### Phase 3A: GUI Shell & Service Layer (2 hours)

**Deliverables:**
- Main window with menu bar and toolbar
- Panel container with tab/dock support
- StateClient (wraps JobStateStore)
- EngineClient (wraps Orchestrator)
- EventBus (pub/sub for panels)
- Basic configuration system

**Files Created:**
```
gui/
├── shell/
│   ├── __init__.py
│   ├── main_window.py          # Main GUI window
│   ├── panel_manager.py        # Panel lifecycle
│   └── config.py               # GUI configuration
├── services/
│   ├── __init__.py
│   ├── state_client.py         # State store wrapper
│   ├── engine_client.py        # Orchestrator wrapper
│   └── event_bus.py            # Event distribution
└── __init__.py
```

**Key Features:**
- Clean PyQt6 window with dark theme support
- Panel registration and loading system
- Thread-safe service layer
- Event polling (500ms intervals)

### Phase 3B: Dashboard Panel (1.5 hours)

**Deliverables:**
- Run overview panel
- Recent jobs list
- Success/failure statistics
- Quick actions (start job, view logs)

**Files Created:**
```
gui/panels/
├── __init__.py
├── dashboard/
│   ├── __init__.py
│   ├── manifest.json           # Panel metadata
│   ├── panel.py                # Dashboard widget
│   ├── models.py               # Data models
│   └── widgets.py              # Custom widgets (charts, cards)
```

**UI Components:**
- Run status cards (pending, running, completed)
- Recent jobs table with status indicators
- Success rate chart (last 10 runs)
- Quick action buttons
- Auto-refresh (configurable interval)

### Phase 3C: Pipeline Radar Panel (1.5 hours)

**Deliverables:**
- File status visualization (grid/tree view)
- Workstream progress tracking
- Color-coded status indicators
- Interactive filtering

**Files Created:**
```
gui/panels/
└── pipeline_radar/
    ├── __init__.py
    ├── manifest.json
    ├── panel.py                # Radar widget
    ├── models.py               # File/workstream models
    ├── visualizations.py       # Status grid/tree
    └── filters.py              # Filter controls
```

**UI Components:**
- File grid with status colors:
  - 🟢 Green: Completed successfully
  - 🟡 Yellow: In progress
  - 🔴 Red: Failed/quarantined
  - ⚪ Gray: Not started
- Workstream grouping
- Search and filter controls
- Drill-down to job details

### Phase 3D: Integration & Testing (1 hour)

**Deliverables:**
- Panel integration tests
- Service layer tests
- GUI workflow tests
- Documentation and examples

**Files Created:**
```
tests/gui/
├── __init__.py
├── test_services.py            # Service layer tests
├── test_panels.py              # Panel loading tests
└── test_integration.py         # End-to-end GUI tests

docs/
└── GUI_USER_GUIDE.md          # User documentation
```

**Tests:**
- Panel loading and activation
- Service communication
- Event bus delivery
- Data refresh cycles

## Technical Specifications

### Technology Stack

**Core:**
- Python 3.12+
- PyQt6 6.6+
- QtDesigner for complex layouts (optional)

**Data Visualization:**
- PyQtGraph for charts (lightweight)
- Custom widgets for status grids

**Threading:**
- QThread for background tasks
- Signal/slot for thread-safe updates

### Data Flow

```
User Action (GUI)
    ↓
EngineClient/StateClient (service layer)
    ↓
engine.orchestrator / engine.state_store
    ↓
Database / Job Execution
    ↓
EventBus notification
    ↓
Panel refresh
```

### Event System

**Event Types:**
- `job.started` - Job execution began
- `job.completed` - Job finished (success/failure)
- `job.quarantined` - Job moved to quarantine
- `run.status_changed` - Run status updated
- `state.updated` - General state change

**Event Payload:**
```python
{
    "event_type": "job.completed",
    "timestamp": "2025-11-21T01:00:00Z",
    "data": {
        "job_id": "job-001",
        "run_id": "run-001",
        "status": "completed",
        "exit_code": 0
    }
}
```

## Implementation Steps

### Step 1: Setup (30 min)
```bash
# Install dependencies
pip install PyQt6 PyQt6-tools pyqtgraph

# Create GUI structure
mkdir -p gui/{shell,services,panels/{dashboard,pipeline_radar}}
touch gui/__init__.py gui/shell/__init__.py gui/services/__init__.py
```

### Step 2: Main Window (1 hour)
```python
# gui/shell/main_window.py
from PyQt6.QtWidgets import QMainWindow, QTabWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Development Pipeline")
        self.setup_ui()
        
    def setup_ui(self):
        # Menu bar, toolbar, central widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
```

### Step 3: Service Layer (1 hour)
```python
# gui/services/state_client.py
from engine.state_store.job_state_store import JobStateStore

class StateClient:
    def __init__(self):
        self.store = JobStateStore()
        
    def get_recent_runs(self, limit=10):
        return self.store.list_recent_runs(limit)
```

### Step 4: Dashboard Panel (1.5 hours)
- Create panel structure
- Build UI with QtDesigner or code
- Connect to services
- Implement refresh logic

### Step 5: Pipeline Radar (1.5 hours)
- Design file grid visualization
- Implement status color coding
- Add filtering and search
- Connect to workstream data

### Step 6: Testing & Polish (1 hour)
- Write integration tests
- Test panel switching
- Verify data refresh
- Document usage

## Testing Strategy

### Unit Tests
```python
# tests/gui/test_services.py
def test_state_client_get_runs():
    client = StateClient()
    runs = client.get_recent_runs(limit=5)
    assert len(runs) <= 5
```

### Integration Tests
```python
# tests/gui/test_integration.py
def test_panel_loads_data(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    
    dashboard = window.panels['dashboard']
    assert dashboard.data is not None
```

### Manual Testing
- Launch GUI: `python -m gui.shell.main_window`
- Verify panels load
- Test data refresh
- Check event updates

## Success Criteria

- [x] GUI launches without errors
- [x] Both panels load and display data
- [x] Service layer communicates with backend
- [x] Events update panels in real-time
- [x] All tests pass (10+ tests)
- [x] Documentation complete
- [x] User can run jobs from GUI
- [x] Status updates visible within 1 second

## Risks & Mitigations

### Risk 1: PyQt6 Learning Curve
**Mitigation:** Use simple layouts initially, leverage existing examples

### Risk 2: Threading Issues
**Mitigation:** Use QThread and signals/slots properly, no direct GUI updates from threads

### Risk 3: Event Polling Performance
**Mitigation:** Configurable refresh rate (500ms default), optimize queries

### Risk 4: Panel Complexity
**Mitigation:** Start with simple tables/lists, add visualizations incrementally

## Future Enhancements (Post-Phase 3)

### Phase 3+: Additional Panels
- Logs Panel (real-time log streaming)
- Workstreams Panel (Kanban board)
- Settings Panel (configuration UI)
- Error Panel (quarantine management)

### Advanced Features
- WebSocket for real-time events (replace polling)
- Custom themes and layouts
- Panel state persistence
- Export to reports (PDF/HTML)

## Dependencies

**Required:**
- Phase 2A: State Integration ✅
- Phase 2B: Additional Adapters ✅
- SQLite database with events table ✅

**External:**
- PyQt6 >= 6.6
- Python >= 3.12

## Deliverables Summary

### Code (15+ files)
- GUI shell and main window
- Service layer (3 clients)
- Dashboard panel (complete)
- Pipeline Radar panel (complete)
- Panel plugin system

### Tests (8+ tests)
- Service layer tests
- Panel integration tests
- Event bus tests

### Documentation
- User guide (GUI_USER_GUIDE.md)
- Panel developer guide
- API reference for services

## Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| 3A | 2 hours | Shell + Services |
| 3B | 1.5 hours | Dashboard Panel |
| 3C | 1.5 hours | Pipeline Radar |
| 3D | 1 hour | Testing & Docs |
| **Total** | **6 hours** | **Complete GUI** |

## Next Steps After Completion

1. Phase 4: Job Queue System (async execution)
2. Phase 5: Advanced Panels (logs, settings, errors)
3. Phase 6: Production Deployment

---

**Ready to implement?** This plan provides a clear path to a functional GUI while maintaining the quality and testing standards established in Phase 2.
