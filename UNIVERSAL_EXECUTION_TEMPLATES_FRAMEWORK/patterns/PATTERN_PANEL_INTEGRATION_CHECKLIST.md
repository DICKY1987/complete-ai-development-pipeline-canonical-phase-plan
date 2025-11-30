---
doc_id: DOC-PAT-PATTERN-PANEL-INTEGRATION-CHECKLIST-761
---

# Pattern Activity Panel - Integration Checklist

**Quick reference for integrating Pattern Activity Panel into existing GUI framework**

---

## Pre-Integration Checklist

### ✅ Files to Create

```
core/
├── state/
│   └── pattern_state_store.py          # NEW - Pattern data persistence
├── ui_clients/
│   └── pattern_client.py                # NEW - Pattern data access client
└── events/
    └── pattern_events.py                # NEW - Pattern event definitions (optional)

api/
└── routes/
    └── patterns.py                      # NEW - REST endpoints for patterns

patterns/
├── gui/
│   ├── __init__.py
│   ├── pattern_activity_panel.py        # NEW - Main panel component
│   ├── timeline_view.py                 # NEW - Timeline component
│   ├── summary_header.py                # NEW - Summary component
│   └── detail_drawer.py                 # NEW - Detail drawer component
└── engine/
    └── pattern_executor.py              # MODIFY - Add event emission

schema/
└── migrations/
    └── 006_add_pattern_tables.sql       # NEW - DB schema for patterns
```

---

## Integration Steps

### Step 1: Database Schema (5 min)

**File**: `schema/migrations/006_add_pattern_tables.sql`

```sql
-- Pattern runs table
CREATE TABLE IF NOT EXISTS pattern_runs (
  pattern_run_id TEXT PRIMARY KEY,
  pattern_id TEXT NOT NULL,
  job_id TEXT NOT NULL,
  step_id TEXT NOT NULL,
  status TEXT NOT NULL,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  duration_seconds REAL,
  exit_code INTEGER,
  finding_count INTEGER,
  lines_changed INTEGER,
  tests_passed INTEGER,
  resolved_inputs TEXT,      -- JSON
  commands_run TEXT,          -- JSON
  artifacts TEXT,             -- JSON
  FOREIGN KEY (job_id) REFERENCES jobs(job_id)
);

CREATE INDEX idx_pattern_runs_job ON pattern_runs(job_id);
CREATE INDEX idx_pattern_runs_pattern ON pattern_runs(pattern_id);
CREATE INDEX idx_pattern_runs_status ON pattern_runs(status);

-- Pattern events table
CREATE TABLE IF NOT EXISTS pattern_events (
  event_id TEXT PRIMARY KEY,
  timestamp TEXT NOT NULL,
  event_type TEXT NOT NULL,
  pattern_run_id TEXT NOT NULL,
  job_id TEXT NOT NULL,
  step_id TEXT NOT NULL,
  pattern_id TEXT NOT NULL,
  status TEXT NOT NULL,
  details TEXT NOT NULL,      -- JSON
  FOREIGN KEY (pattern_run_id) REFERENCES pattern_runs(pattern_run_id)
);

CREATE INDEX idx_pattern_events_run ON pattern_events(pattern_run_id);
CREATE INDEX idx_pattern_events_job ON pattern_events(job_id);
CREATE INDEX idx_pattern_events_type ON pattern_events(event_type);
CREATE INDEX idx_pattern_events_timestamp ON pattern_events(timestamp);
```

**Run migration**:
```bash
sqlite3 .worktrees/pipeline_state.db < schema/migrations/006_add_pattern_tables.sql
```

---

### Step 2: State Store Implementation (30 min)

**File**: `core/state/pattern_state_store.py`

Copy implementation from `PATTERN_EXECUTION_VISUALIZATION_DESIGN.md` Section 5.2

**Key methods to implement**:
- `save_run(record: dict) -> None`
- `save_event(event: dict) -> None`
- `get_events_for_job(job_id: str, after_event_id: str | None) -> list[dict]`
- `get_run_detail(pattern_run_id: str) -> dict | None`
- `query_runs(filter: dict) -> list[dict]`

---

### Step 3: Client Implementation (30 min)

**File**: `core/ui_clients/pattern_client.py`

Copy implementation from `PATTERN_PANEL_GUI_ALIGNMENT.md` Section 4

**Key methods**:
- `get_events_for_job(job_id, after_event_id, limit) -> list[dict]`
- `get_pattern_summary(job_id) -> dict`
- `get_run_detail(pattern_run_id) -> dict | None`

**Register in** `core/ui_clients/__init__.py`:
```python
from .pattern_client import PatternClient

__all__ = ["StateClient", "ToolsClient", "LogsClient", "PatternClient"]
```

---

### Step 4: CLI Commands (20 min)

**File**: `core/ui_cli.py` (MODIFY - add new commands)

Add three new commands following existing pattern:

```python
from core.ui_clients import PatternClient

@cli.command("pattern-events")
@click.option("--job-id", required=True)
@click.option("--after", help="Event ID to start after")
@click.option("--limit", default=500)
@click.option("--json", is_flag=True)
def pattern_events(job_id, after, limit, json):
    """List pattern events for a job."""
    # Implementation from alignment doc
    pass

@cli.command("pattern-summary")
@click.option("--job-id", required=True)
@click.option("--json", is_flag=True)
def pattern_summary(job_id, json):
    """Get pattern execution summary."""
    # Implementation from alignment doc
    pass

@cli.command("pattern-detail")
@click.option("--pattern-run-id", required=True)
@click.option("--json", is_flag=True)
def pattern_detail(pattern_run_id, json):
    """Get pattern run details."""
    # Implementation from alignment doc
    pass
```

**Test**:
```bash
python -m core.ui_cli pattern-events --job-id test-job --json
python -m core.ui_cli pattern-summary --job-id test-job
```

---

### Step 5: REST API Endpoints (30 min)

**File**: `api/routes/patterns.py` (NEW)

```python
from fastapi import APIRouter, Query, HTTPException
from core.ui_clients import PatternClient

router = APIRouter(prefix="/api/patterns", tags=["patterns"])

@router.get("/jobs/{job_id}/events")
async def get_pattern_events(
    job_id: str,
    after: str | None = Query(None),
    limit: int = Query(500, le=1000)
):
    """Get pattern events for a job."""
    # Implementation from alignment doc
    pass

@router.get("/jobs/{job_id}/summary")
async def get_pattern_summary(job_id: str):
    """Get pattern execution summary."""
    # Implementation from alignment doc
    pass

@router.get("/runs/{pattern_run_id}")
async def get_pattern_run_detail(pattern_run_id: str):
    """Get pattern run detail."""
    # Implementation from alignment doc
    pass
```

**Register router in** `api/main.py`:
```python
from api.routes import patterns

app.include_router(patterns.router)
```

**Test**:
```bash
curl http://localhost:8080/api/patterns/jobs/test-job/events
curl http://localhost:8080/api/patterns/jobs/test-job/summary
```

---

### Step 6: Event Emission in Pattern Executor (45 min)

**File**: `patterns/engine/pattern_executor.py` (MODIFY)

Add event emission at each lifecycle phase:

```python
from core.events.event_bus import event_bus
from core.state.pattern_state_store import PatternStateStore
import ulid

class PatternExecutor:
    def __init__(self):
        self.state_store = PatternStateStore()
        self.event_bus = event_bus  # Use global event bus

    def execute_pattern(self, request: dict) -> dict:
        pattern_run_id = f"PRUN-{ulid.new()}"

        # PHASE 1: Selection
        self._emit_event(
            pattern_run_id=pattern_run_id,
            event_type="pattern.selection.started",
            status="in_progress",
            details={"operation_kind": request["operation_kind"]}
        )

        # ... rest of phases with event emissions

    def _emit_event(self, pattern_run_id, event_type, status, details):
        event = {
            "event_id": f"EVT-{ulid.new()}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            "pattern_run_id": pattern_run_id,
            "job_id": self.current_job_id,
            "step_id": self.current_step_id,
            "pattern_id": self.current_pattern_id,
            "status": status,
            "details": details
        }

        # Persist to database
        self.state_store.save_event(event)

        # Emit to event bus for live updates
        self.event_bus.emit(event)
```

---

### Step 7: WebSocket Integration (15 min)

**File**: `api/websocket.py` (MODIFY - if not already streaming all events)

Ensure WebSocket endpoint streams **all** event types including patterns:

```python
@app.websocket("/jobs/{job_id}/events")
async def job_event_stream(websocket: WebSocket, job_id: str):
    await websocket.accept()

    def event_callback(event: dict):
        # Stream all events for this job (run, step, pattern, etc.)
        if event.get("job_id") == job_id:
            asyncio.create_task(websocket.send_json(event))

    subscription_id = event_bus.subscribe("*", event_callback)

    try:
        while True:
            await websocket.receive_text()
    finally:
        event_bus.unsubscribe(subscription_id)
```

---

### Step 8: GUI Panel Component (1-2 hours)

**Option A: React/Web GUI**

**File**: `patterns/gui/web/PatternActivityPanel.tsx`

Copy implementation from `PATTERN_EXECUTION_VISUALIZATION_DESIGN.md` Section 5.5

**Add to main GUI layout**:
```typescript
// In main GUI app
import { PatternActivityPanel } from './patterns/gui/web/PatternActivityPanel';

function JobDetailView({ jobId }) {
  return (
    <div className="job-detail">
      <Tabs>
        <Tab label="Overview">...</Tab>
        <Tab label="Files">...</Tab>
        <Tab label="Logs">...</Tab>
        <Tab label="Patterns">              {/* NEW TAB */}
          <PatternActivityPanel jobId={jobId} />
        </Tab>
      </Tabs>
    </div>
  );
}
```

**Option B: Textual/TUI**

**File**: `patterns/gui/tui/pattern_panel.py`

```python
from textual.app import ComposeResult
from textual.widgets import Static, DataTable
from textual.containers import Container
from core.ui_clients import PatternClient

class PatternActivityPanel(Container):
    """TUI panel for pattern activity."""

    def __init__(self, job_id: str):
        super().__init__()
        self.job_id = job_id
        self.client = PatternClient()

    def compose(self) -> ComposeResult:
        yield Static("Pattern Activity", classes="panel-header")
        yield DataTable(id="pattern-timeline")

    async def on_mount(self) -> None:
        # Load initial data
        events = self.client.get_events_for_job(self.job_id)
        table = self.query_one("#pattern-timeline", DataTable)

        table.add_columns("Time", "Event", "Status")
        for event in events:
            table.add_row(
                event["timestamp"][:19],
                event["event_type"],
                event["status"]
            )

        # Set up polling for live updates
        self.set_interval(2.0, self.refresh_events)

    async def refresh_events(self):
        # Poll for new events
        # ... implementation
```

**Add to TUI layout**:
```python
# In main TUI app
from patterns.gui.tui.pattern_panel import PatternActivityPanel

class JobDetailScreen(Screen):
    def compose(self):
        yield Header()
        yield TabbedContent(
            TabPane("Overview", id="overview"),
            TabPane("Files", id="files"),
            TabPane("Logs", id="logs"),
            TabPane("Patterns", PatternActivityPanel(self.job_id)),  # NEW
        )
```

---

### Step 9: Testing (30 min)

**Test end-to-end flow**:

```python
# Test script: test_pattern_integration.py

from patterns.engine.pattern_executor import PatternExecutor
from core.ui_clients import PatternClient
import time

def test_pattern_flow():
    # 1. Execute a pattern
    executor = PatternExecutor()
    result = executor.execute_pattern({
        "job_id": "test-job-001",
        "step_id": "step-001",
        "operation_kind": "semgrep_scan",
        "context": {"language": "python"},
        "inputs": {"target_paths": ["src/"]}
    })

    # 2. Verify events were created
    client = PatternClient()
    events = client.get_events_for_job("test-job-001")
    assert len(events) > 0
    assert events[0]["event_type"] == "pattern.selection.started"

    # 3. Verify summary works
    summary = client.get_pattern_summary("test-job-001")
    assert summary["summary"]["total_runs"] == 1

    # 4. Verify detail works
    pattern_run_id = result["pattern_run_id"]
    detail = client.get_run_detail(pattern_run_id)
    assert detail is not None
    assert detail["status"] == "success"

    print("✅ All tests passed!")

if __name__ == "__main__":
    test_pattern_flow()
```

**Run test**:
```bash
python test_pattern_integration.py
```

---

## Verification Checklist

### Backend ✅

- [ ] Database tables created (`pattern_runs`, `pattern_events`)
- [ ] `PatternStateStore` implemented and tested
- [ ] `PatternClient` implemented and tested
- [ ] CLI commands work (`pattern-events`, `pattern-summary`, `pattern-detail`)
- [ ] REST endpoints work and return correct data
- [ ] Events are emitted from `PatternExecutor`
- [ ] Events are persisted to database
- [ ] Events are broadcast via event bus

### Frontend ✅

- [ ] Panel component implemented (React or Textual)
- [ ] WebSocket connection works for live updates
- [ ] Summary header displays correct statistics
- [ ] Timeline view shows events in chronological order
- [ ] Detail drawer opens and shows run details
- [ ] Panel integrates into main GUI layout
- [ ] Styling matches existing GUI theme

### Integration ✅

- [ ] Pattern events appear in WebSocket stream
- [ ] Panel updates in real-time when patterns execute
- [ ] Filtering by job_id works correctly
- [ ] Panel can be opened/closed without issues
- [ ] No performance issues with 100+ events
- [ ] Cross-panel links work (e.g., job → patterns)

---

## Common Issues & Solutions

### Issue: Events not appearing in GUI

**Check**:
1. Event emission in `PatternExecutor._emit_event()`
2. Event bus subscription in panel component
3. WebSocket connection status
4. Browser console for errors

**Solution**:
```python
# Add debug logging
self._emit_event(..., details={...})
print(f"Emitted event: {event['event_type']}")  # Temporary debug
```

---

### Issue: Database locked errors

**Cause**: Multiple processes accessing SQLite simultaneously

**Solution**:
```python
# In PatternStateStore.__init__
conn.execute("PRAGMA journal_mode=WAL")  # Enable Write-Ahead Logging
```

---

### Issue: WebSocket disconnects

**Cause**: No keep-alive messages

**Solution**:
```typescript
// Client-side keep-alive
setInterval(() => {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: 'ping' }));
  }
}, 30000);  // Every 30 seconds
```

---

## Quick Start Command Sequence

```bash
# 1. Create schema
sqlite3 .worktrees/pipeline_state.db < schema/migrations/006_add_pattern_tables.sql

# 2. Test pattern client
python -c "from core.ui_clients import PatternClient; print(PatternClient())"

# 3. Test CLI
python -m core.ui_cli pattern-summary --job-id test-job --json

# 4. Start API server
uvicorn api.main:app --reload

# 5. Test REST endpoint
curl http://localhost:8080/api/patterns/jobs/test-job/summary

# 6. Start GUI
python -m gui.main  # or npm start for web GUI

# 7. Execute test pattern
python test_pattern_integration.py
```

---

## File Size Estimates

- `pattern_state_store.py`: ~300 lines
- `pattern_client.py`: ~150 lines
- `patterns.py` (API routes): ~100 lines
- `pattern_activity_panel.tsx`: ~400 lines (React)
- `pattern_panel.py`: ~200 lines (Textual)
- Migration SQL: ~40 lines
- Tests: ~200 lines

**Total**: ~1,390 lines of code for complete integration

---

## Next Steps After Integration

1. **Add more pattern types** - Create patterns for common operations
2. **Add pattern analytics** - Show trends, success rates over time
3. **Add pattern recommendations** - Suggest patterns based on context
4. **Add pattern templates** - UI for creating new patterns
5. **Add pattern scheduling** - Queue patterns for execution

---

**Questions or issues?** See `PATTERN_EXECUTION_VISUALIZATION_DESIGN.md` for detailed design or `PATTERN_PANEL_GUI_ALIGNMENT.md` for architecture details.
