---
doc_id: DOC-GUIDE-GUI-DEVELOPMENT-GUIDE-924
---

# GUI Development Guide - Next Steps

This guide shows how to proceed with implementing the GUI layer now that the engine foundation is complete.

## Prerequisites

✅ **Completed** (Phase 1):
- Engine directory structure
- Protocol interfaces
- Job schema and examples
- Aider adapter
- Orchestrator CLI
- Validation tests

## GUI Architecture Overview

The GUI follows the **hybrid shell pattern** from `gui/Hybrid UI_GUI shell_terminal_TUI engine.md`:

```
┌─────────────────────────────────┐
│       GUI Shell (PyQt6)         │  ← Mission Control Dashboard
│  - Panels (Dashboard, Runs,     │
│    Workstreams, Pipeline Radar) │
│  - Read-only state queries      │
│  - Job submission (via CLI)     │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│    Engine Orchestrator          │  ← Job Coordinator
│  - Dispatches to adapters       │
│  - Manages state transitions    │
│  - Handles retries/escalation   │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│      Tool Adapters              │  ← Terminal/CLI Wrappers
│  - Aider, Codex, Tests, Git     │
│  - Execute in subprocesses      │
│  - Capture logs and results     │
└─────────────────────────────────┘
```

## Phase 2A: State Store Integration

**Goal**: Connect orchestrator to existing database for job tracking.

### Files to Create

1. **`engine/state_store/job_state_store.py`**
   ```python
   """
   Job-centric state store implementation.
   Wraps existing core/state/db.py with StateInterface.
   """
   from typing import Dict, Any, List
   from engine.interfaces import StateInterface
   from core.state import db, crud

   class JobStateStore:
       """Implements StateInterface using existing DB."""

       def __init__(self, db_path: str = None):
           self.db_path = db_path or "state/pipeline.db"
           db.init_db(self.db_path)

       def mark_job_running(self, job_id: str) -> None:
           # Update status in DB
           ...

       # Implement remaining StateInterface methods
   ```

2. **Update `engine/orchestrator/orchestrator.py`**
   ```python
   from engine.state_store.job_state_store import JobStateStore

   class Orchestrator:
       def __init__(self, state_store: StateInterface = None):
           self.state_store = state_store or JobStateStore()
   ```

### Testing
```bash
python -m pytest tests/engine/test_state_store.py
```

## Phase 2B: Additional Adapters

**Goal**: Implement Codex, tests, and git adapters.

### Codex Adapter Template

**File**: `engine/adapters/codex_adapter.py`

```python
"""
ADAPTER_ROLE: terminal_tool_adapter
TOOL: codex
VERSION: 0.1.0
"""

from engine.types import JobResult

class CodexAdapter:
    def run_job(self, job: dict) -> JobResult:
        # Similar to AiderAdapter but for Codex CLI
        ...

    def validate_job(self, job: dict) -> bool:
        return job.get("tool") == "codex"

    def get_tool_info(self) -> dict:
        return {
            "tool": "codex",
            "capabilities": ["code_review", "escalation"]
        }

def run_codex_job(job: dict) -> JobResult:
    return CodexAdapter().run_job(job)
```

### Register in Orchestrator
```python
from engine.adapters.codex_adapter import run_codex_job

TOOL_RUNNERS = {
    "aider": run_aider_job,
    "codex": run_codex_job,  # Add here
}
```

## Phase 3: GUI Foundation

**Goal**: Create the GUI shell with plugin system.

### Directory Structure
```
gui/
├── __init__.py
├── main.py                    # Application entry point
├── app_shell.py              # Main window and plugin loader
├── services/                  # Service layer
│   ├── __init__.py
│   ├── service_locator.py    # Dependency injection
│   ├── state_client.py       # Read-only state queries
│   └── engine_client.py      # Orchestrator CLI wrapper
├── panels/                    # Panel plugins
│   ├── __init__.py
│   ├── dashboard/
│   │   ├── dashboard.panel.json
│   │   └── dashboard_view.py
│   └── runs/
│       ├── runs.panel.json
│       └── runs_view.py
└── widgets/                   # Reusable UI components
    ├── __init__.py
    └── run_selector.py
```

### Panel Plugin Pattern

**File**: `gui/panels/dashboard/dashboard.panel.json`
```json
{
  "id": "dashboard",
  "type": "panel",
  "title": "Dashboard",
  "entry_point": "gui.panels.dashboard.dashboard_view:DashboardPanel",
  "requires_services": ["state_client", "engine_client"],
  "enabled_by_default": true,
  "order": 10
}
```

**File**: `gui/panels/dashboard/dashboard_view.py`
```python
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from gui.plugin_base import PanelPluginBase

class DashboardPanel(PanelPluginBase):
    @classmethod
    def plugin_id(cls) -> str:
        return "dashboard"

    @classmethod
    def plugin_title(cls) -> str:
        return "Dashboard"

    def create_widget(self, parent=None) -> QWidget:
        widget = QWidget(parent)
        layout = QVBoxLayout()

        # Read state via service
        state = self.services.get("state_client")
        runs = state.list_recent_runs()

        layout.addWidget(QLabel(f"Recent Runs: {len(runs)}"))
        widget.setLayout(layout)
        return widget

    def on_activate(self):
        # Start timer for updates
        pass

    def on_deactivate(self):
        # Stop timer
        pass
```

### Main Application

**File**: `gui/main.py`
```python
import sys
from PyQt6.QtWidgets import QApplication
from gui.app_shell import AppShell

def main():
    app = QApplication(sys.argv)
    shell = AppShell()
    shell.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

### Service Layer

**File**: `gui/services/engine_client.py`
```python
"""Wrapper for orchestrator CLI."""
import subprocess
import json

class EngineClient:
    def run_job(self, job_file: str) -> dict:
        """Submit job to orchestrator."""
        result = subprocess.run(
            ["python", "-m", "engine.orchestrator", "run-job",
             "--job-file", job_file],
            capture_output=True,
            text=True
        )
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    def get_job_status(self, job_id: str) -> str:
        # Query via state_client
        pass
```

## Phase 4: Pipeline Radar Panel

**Goal**: Implement the "where is each file in the pipeline" view.

Following `gui/Pipeline Radar plugin.md`:

### Panel Features
1. **Run Selector** - Choose which run to inspect
2. **Workstream View** - Kanban board (Waiting → Running → Fixing → Done)
3. **File View** - Table showing file status across pipeline
4. **Detail Inspector** - Timeline and error details

### Implementation Steps

1. Create panel manifest and spec:
   - `gui/panels/pipeline_radar/pipeline_radar.panel.json`
   - `gui/panels/pipeline_radar/pipeline_radar.spec.md`

2. Implement view:
   - `gui/panels/pipeline_radar/pipeline_radar_view.py`

3. Add to main window via plugin loader

## Phase 5: Permissions & Safety

**Goal**: Enforce read-heavy, write-light constraints from `gui/GUI_PIPELINE.txt`.

### Permission Matrix Implementation

**File**: `gui/services/permissions.py`
```python
class PermissionLevel:
    NONE = 0
    READ = 1
    WRITE = 2

class PermissionsManager:
    """Enforces GUI permission matrix."""

    PERMISSIONS = {
        "runs": {
            "list": PermissionLevel.READ,
            "get": PermissionLevel.READ,
            "start": PermissionLevel.WRITE,  # requires confirmation
            "cancel": PermissionLevel.WRITE,
            "delete": PermissionLevel.NONE,
        },
        # ... more capabilities
    }

    def can_perform(self, resource: str, action: str) -> bool:
        level = self.PERMISSIONS.get(resource, {}).get(action, PermissionLevel.NONE)
        return level > PermissionLevel.NONE

    def requires_confirmation(self, resource: str, action: str) -> bool:
        # Check if write action needs user confirmation
        level = self.PERMISSIONS.get(resource, {}).get(action)
        return level == PermissionLevel.WRITE
```

## Testing Strategy

### Unit Tests
```bash
tests/engine/
├── test_adapters.py          # Adapter interface compliance
├── test_orchestrator.py      # Job dispatch logic
└── test_state_store.py       # State persistence

tests/gui/
├── test_panels.py            # Panel loading and lifecycle
├── test_services.py          # Service layer
└── test_permissions.py       # Permission enforcement
```

### Integration Tests
```bash
# End-to-end: submit job via GUI, execute, update state
python -m pytest tests/integration/test_job_workflow.py
```

## Development Workflow

1. **State Integration** → Connect orchestrator to DB
2. **More Adapters** → Codex, tests, git
3. **GUI Shell** → Main window + plugin loader
4. **First Panel** → Dashboard or Pipeline Radar
5. **Service Layer** → State and engine clients
6. **Permissions** → Enforce read/write constraints
7. **Testing** → Unit and integration tests
8. **Documentation** → Usage guides and examples

## Quick Reference

### Commands
```bash
# Validate engine
python scripts/validate_engine.py

# Run job
python -m engine.orchestrator run-job --job-file path/to/job.json

# Start GUI (future)
python -m gui.main

# Run tests
pytest tests/engine/
pytest tests/gui/
```

### Key Documents
- Architecture: `gui/Hybrid UI_GUI shell_terminal_TUI engine.md`
- Permissions: `gui/GUI_PIPELINE.txt`
- Panel Example: `gui/Pipeline Radar plugin.md`
- Migration: `gui/Plan Map coreStructure to engine Hybrid Architecture.md`

## Next Immediate Actions

1. ✅ **Phase 1 Complete**: Engine foundation
2. 🔄 **Phase 2A Start**: Implement `JobStateStore`
3. ⏳ **Phase 2B**: Add Codex adapter
4. ⏳ **Phase 3**: Create GUI shell skeleton

Choose Phase 2A (state integration) or Phase 2B (more adapters) based on priorities.
