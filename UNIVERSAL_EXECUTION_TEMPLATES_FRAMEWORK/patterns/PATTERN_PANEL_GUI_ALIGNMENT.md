# Pattern Activity Panel - GUI Framework Alignment

**Document Version**: 1.0.0
**Created**: 2025-11-26
**Purpose**: Ensure Pattern Activity Panel integrates modularly with existing GUI/TUI architecture

---

## Table of Contents

1. [Alignment Summary](#1-alignment-summary)
2. [Architecture Integration](#2-architecture-integration)
3. [Modular Component Design](#3-modular-component-design)
4. [Data Client Integration](#4-data-client-integration)
5. [Event System Alignment](#5-event-system-alignment)
6. [API Contract Compliance](#6-api-contract-compliance)
7. [Implementation Roadmap](#7-implementation-roadmap)

---

## 1. Alignment Summary

### Current GUI Architecture (from `gui/`)

The existing framework uses a **Hybrid UI/GUI/Terminal/TUI** architecture:

- **GUI Shell**: Mission control dashboard with panels, cards, and boards
- **Orchestrator/Job Manager**: Queue management and process spawning
- **Terminal/TUI Adapters**: Tool-specific command wrappers
- **State & Storage Layer**: Structured records in SQLite/JSONL

### Pattern Activity Panel Positioning

The Pattern Activity Panel is **Component #8** in the modular panel system, complementing:

1. Global Pipeline Dashboard
2. Workstream & Job Explorer
3. File Lifecycle & Routing View
4. Application / Tool Health Panel
5. Error & Quarantine Center
6. Live Logs & Event Stream
7. Controls & Settings Panel
8. **← Pattern Activity Panel (NEW)**

### Design Alignment

✅ **Fully Compatible** - The pattern visualization design aligns with:
- Event-driven architecture
- Panel-based modular design
- Python API + CLI + WebSocket layers
- SQLite state persistence
- JSON-RPC/REST communication
- Read-mostly GUI philosophy

---

## 2. Architecture Integration

### Layered Integration Model

```
┌─────────────────────────────────────────────────────────────┐
│  PRESENTATION LAYER (GUI Shell)                             │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │  Dashboard   │  │ Workstreams  │  │ Pattern Panel   │  │
│  │   Panel      │  │    Panel     │  │    (NEW)        │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬────────┘  │
│         │                  │                    │            │
└─────────┼──────────────────┼────────────────────┼────────────┘
          │                  │                    │
┌─────────┼──────────────────┼────────────────────┼────────────┐
│  API LAYER (Clients)       │                    │            │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌────────▼────────┐  │
│  │ StateClient  │  │ ToolsClient  │  │ PatternClient   │  │
│  │              │  │              │  │    (NEW)        │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬────────┘  │
│         │                  │                    │            │
└─────────┼──────────────────┼────────────────────┼────────────┘
          │                  │                    │
┌─────────┼──────────────────┼────────────────────┼────────────┐
│  ENGINE LAYER (Orchestrator)                                 │
│  ┌──────▼────────────────────────────────────────▼────────┐ │
│  │         Pattern Executor (with Event Emitter)          │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
          │                  │                    │
┌─────────┼──────────────────┼────────────────────┼────────────┐
│  PERSISTENCE LAYER (State Store)                             │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌────────▼────────┐  │
│  │ runs table   │  │ steps table  │  │ pattern_runs    │  │
│  │ events table │  │ files table  │  │ pattern_events  │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### Integration Points

**1. Shares Existing Infrastructure**
- Same SQLite database (add `pattern_runs` and `pattern_events` tables)
- Same event bus architecture
- Same WebSocket server for live updates
- Same REST API pattern (FastAPI)

**2. Follows Modular Panel Contract**
- Self-contained component
- Communicates via `PatternClient` API only
- No direct database access from GUI
- Emits/subscribes to events via event bus

**3. Reuses Existing Components**
- Timeline view pattern (similar to Live Logs & Event Stream)
- Summary cards (similar to Tool Health Panel)
- Detail drawer pattern (similar to Workstream Explorer)

---

## 3. Modular Component Design

### Component Independence

The Pattern Activity Panel is designed as a **standalone, pluggable module**:

```python
# patterns/gui/pattern_activity_panel.py

class PatternActivityPanel:
    """
    Modular panel for pattern execution visualization.
    Can be embedded in any GUI framework (tkinter, PyQt, web).
    """

    def __init__(self, client: PatternClient, event_bus: EventBus):
        """
        Initialize panel with dependencies injected.

        Args:
            client: API client for pattern data (HTTP or Python API)
            event_bus: Event subscription interface
        """
        self.client = client
        self.event_bus = event_bus
        self.subscriptions = []

    def initialize(self, parent_container):
        """
        Set up UI components within parent container.
        Framework-agnostic initialization.
        """
        # Create summary header
        self.summary_header = self._create_summary_header()

        # Create timeline view
        self.timeline_view = self._create_timeline_view()

        # Create detail drawer (hidden by default)
        self.detail_drawer = self._create_detail_drawer()

        # Subscribe to events
        self._subscribe_to_events()

    def _subscribe_to_events(self):
        """Subscribe to pattern-related events."""
        self.subscriptions.append(
            self.event_bus.subscribe("pattern.*", self._on_pattern_event)
        )

    def _on_pattern_event(self, event: dict):
        """Handle incoming pattern events."""
        # Update timeline
        self.timeline_view.add_event(event)

        # Update summary if needed
        if event["event_type"] == "pattern.result.persisted":
            self._refresh_summary()

    def cleanup(self):
        """Clean up resources when panel is closed."""
        for sub in self.subscriptions:
            self.event_bus.unsubscribe(sub)

    # ... rest of implementation
```

### Module Interface Contract

```python
# patterns/gui/interfaces.py

from typing import Protocol, Any, Dict, List

class IPatternPanel(Protocol):
    """
    Interface that Pattern Activity Panel must implement
    to be compatible with the GUI framework.
    """

    def initialize(self, parent_container: Any) -> None:
        """Initialize panel UI within parent container."""
        ...

    def refresh(self) -> None:
        """Refresh panel data from backend."""
        ...

    def cleanup(self) -> None:
        """Clean up resources."""
        ...

    def set_filter(self, job_id: str | None) -> None:
        """Filter panel to show only specific job."""
        ...


class IPatternClient(Protocol):
    """
    Interface for pattern data access.
    Implementations: PatternHTTPClient, PatternPythonClient
    """

    def get_events_for_job(self, job_id: str, after_event_id: str | None) -> List[Dict]:
        """Get pattern events for a job."""
        ...

    def get_pattern_summary(self, job_id: str) -> Dict:
        """Get pattern execution summary for a job."""
        ...

    def get_run_detail(self, pattern_run_id: str) -> Dict:
        """Get detailed information for a pattern run."""
        ...
```

---

## 4. Data Client Integration

### New Client: `PatternClient`

Following the existing client pattern from `core/ui_clients.py`:

```python
# core/ui_clients/pattern_client.py

from typing import List, Dict, Optional
from core.state.pattern_state_store import PatternStateStore

class PatternClient:
    """
    Client for accessing pattern execution data.
    Follows same pattern as StateClient, ToolsClient, LogsClient.
    """

    def __init__(self, db_path: str = ".worktrees/pipeline_state.db"):
        self.store = PatternStateStore(db_path)

    def get_events_for_job(
        self,
        job_id: str,
        after_event_id: Optional[str] = None,
        limit: int = 500
    ) -> List[Dict]:
        """
        Get pattern events for a specific job.

        Args:
            job_id: Job ID to filter events
            after_event_id: Only return events after this ID (for polling)
            limit: Maximum number of events to return

        Returns:
            List of pattern event dictionaries
        """
        return self.store.get_events_for_job(job_id, after_event_id)[:limit]

    def get_pattern_summary(self, job_id: str) -> Dict:
        """
        Get aggregated pattern statistics for a job.

        Returns summary with:
        - total_runs, success_count, failed_count
        - total_duration, average_duration
        - by_pattern breakdown
        """
        runs = self.store.query_runs({"job_id": job_id})

        # Aggregate (same logic as REST API)
        total_runs = len(runs)
        success_count = sum(1 for r in runs if r["status"] == "success")
        failed_count = sum(1 for r in runs if r["status"] == "failure")
        # ... etc

        return {
            "summary": {
                "total_runs": total_runs,
                "success_count": success_count,
                "failed_count": failed_count,
                # ...
            },
            "by_pattern": self._group_by_pattern(runs)
        }

    def get_run_detail(self, pattern_run_id: str) -> Optional[Dict]:
        """Get detailed information for a specific pattern run."""
        return self.store.get_run_detail(pattern_run_id)

    def _group_by_pattern(self, runs: List[Dict]) -> List[Dict]:
        """Group runs by pattern_id with statistics."""
        # Implementation...
        pass
```

### CLI Integration

Add pattern commands to existing CLI:

```python
# core/ui_cli.py

import click
from core.ui_clients import PatternClient

@cli.command("pattern-events")
@click.option("--job-id", required=True, help="Job ID to query")
@click.option("--after", help="Return events after this event ID")
@click.option("--limit", default=500, help="Maximum events to return")
@click.option("--json", is_flag=True, help="Output as JSON")
def pattern_events(job_id, after, limit, json):
    """List pattern events for a job."""
    client = PatternClient()
    events = client.get_events_for_job(job_id, after_event_id=after, limit=limit)

    if json:
        click.echo(json_dumps(events))
    else:
        # Table format
        for event in events:
            click.echo(f"{event['timestamp']} {event['event_type']} {event['status']}")


@cli.command("pattern-summary")
@click.option("--job-id", required=True, help="Job ID to query")
@click.option("--json", is_flag=True, help="Output as JSON")
def pattern_summary(job_id, json):
    """Get pattern execution summary for a job."""
    client = PatternClient()
    summary = client.get_pattern_summary(job_id)

    if json:
        click.echo(json_dumps(summary))
    else:
        # Table format
        click.echo(f"Total Runs: {summary['summary']['total_runs']}")
        click.echo(f"Success: {summary['summary']['success_count']}")
        click.echo(f"Failed: {summary['summary']['failed_count']}")
        # ...


@cli.command("pattern-detail")
@click.option("--pattern-run-id", required=True, help="Pattern run ID")
@click.option("--json", is_flag=True, help="Output as JSON")
def pattern_detail(pattern_run_id, json):
    """Get detailed information for a pattern run."""
    client = PatternClient()
    detail = client.get_run_detail(pattern_run_id)

    if detail is None:
        click.echo(f"Pattern run {pattern_run_id} not found", err=True)
        return

    if json:
        click.echo(json_dumps(detail))
    else:
        # Formatted output
        click.echo(f"Pattern Run: {detail['pattern_run_id']}")
        click.echo(f"Pattern: {detail['pattern_id']}")
        click.echo(f"Status: {detail['status']}")
        # ...
```

### Usage Examples

```bash
# List pattern events for a job
python -m core.ui_cli pattern-events --job-id job-123

# Get pattern summary as JSON
python -m core.ui_cli pattern-summary --job-id job-123 --json

# Get detailed pattern run info
python -m core.ui_cli pattern-detail --pattern-run-id PRUN-01JH9FDZ...
```

---

## 5. Event System Alignment

### Unified Event Schema

Pattern events follow the **same event schema** as existing pipeline events:

```python
# core/events/event_schema.py

from enum import Enum
from typing import Literal

class EventCategory(Enum):
    """Top-level event categories."""
    RUN = "run"
    WORKSTREAM = "workstream"
    STEP = "step"
    TOOL = "tool"
    FILE = "file"
    ERROR = "error"
    PATTERN = "pattern"  # ← NEW CATEGORY

# Pattern events follow same structure
PatternEventType = Literal[
    "pattern.selection.started",
    "pattern.selection.resolved",
    "pattern.selection.failed",
    "pattern.template.expansion_started",
    "pattern.template.expanded",
    "pattern.template.expansion_failed",
    "pattern.validation.started",
    "pattern.validation.completed",
    "pattern.validation.failed",
    "pattern.execution.started",
    "pattern.execution.progress",
    "pattern.execution.completed",
    "pattern.execution.failed",
    "pattern.execution.timeout",
    "pattern.result.persisted"
]
```

### Event Bus Integration

Pattern events use the **existing event bus**:

```python
# core/events/event_bus.py

class EventBus:
    """
    Centralized event bus for all pipeline events.
    Pattern events are routed through same bus.
    """

    def emit(self, event: dict) -> None:
        """
        Emit event to all subscribers.
        Pattern events are emitted alongside run/step/tool events.
        """
        category = event["event_type"].split(".")[0]

        # Route to appropriate handlers
        if category == "pattern":
            self._route_pattern_event(event)
        elif category == "run":
            self._route_run_event(event)
        # ... etc

    def subscribe(self, event_pattern: str, callback: Callable) -> str:
        """
        Subscribe to events matching pattern.

        Examples:
            bus.subscribe("pattern.*", handler)         # All pattern events
            bus.subscribe("pattern.execution.*", handler)  # Execution events only
            bus.subscribe("*", handler)                  # All events
        """
        subscription_id = self._generate_subscription_id()
        self._subscriptions[subscription_id] = {
            "pattern": event_pattern,
            "callback": callback
        }
        return subscription_id
```

### Event Correlation

Pattern events **link to existing entities** via correlation IDs:

```python
{
  "event_id": "EVT-01JH9G6E...",
  "timestamp": "2025-11-26T07:15:12.123Z",
  "event_type": "pattern.execution.started",

  # Correlation IDs linking to existing entities
  "job_id": "JOB-01JH9F8P...",      # Links to jobs table
  "step_id": "STEP-003",             # Links to steps table
  "pattern_run_id": "PRUN-01JH9FDZ...",  # Links to pattern_runs table
  "pattern_id": "PAT-SEMGRP-001",    # Links to pattern registry

  "status": "in_progress",
  "details": { /* event-specific data */ }
}
```

This enables **cross-panel queries** like:
- "Show all events (pattern + run + step) for job-123"
- "Show pattern history for this file"
- "Show which patterns were used in this workstream"

---

## 6. API Contract Compliance

### REST API Endpoints

Pattern endpoints follow **existing REST API conventions**:

```python
# api/routes/patterns.py (NEW FILE)

from fastapi import APIRouter, Query
from core.ui_clients import PatternClient

router = APIRouter(prefix="/api/patterns", tags=["patterns"])

@router.get("/jobs/{job_id}/events")
async def get_pattern_events(
    job_id: str,
    after: str | None = Query(None, description="Return events after this ID"),
    limit: int = Query(500, le=1000)
):
    """
    Get pattern events for a job.
    Analogous to: GET /api/runs/{run_id}/events (existing endpoint)
    """
    client = PatternClient()
    events = client.get_events_for_job(job_id, after_event_id=after, limit=limit)
    return {"job_id": job_id, "events": events, "count": len(events)}


@router.get("/jobs/{job_id}/summary")
async def get_pattern_summary(job_id: str):
    """
    Get pattern execution summary for a job.
    Analogous to: GET /api/runs/{run_id}/summary (existing endpoint)
    """
    client = PatternClient()
    summary = client.get_pattern_summary(job_id)
    return summary


@router.get("/runs/{pattern_run_id}")
async def get_pattern_run_detail(pattern_run_id: str):
    """
    Get detailed information for a specific pattern run.
    Analogous to: GET /api/workstreams/{ws_id} (existing endpoint)
    """
    client = PatternClient()
    detail = client.get_run_detail(pattern_run_id)

    if not detail:
        raise HTTPException(status_code=404, detail="Pattern run not found")

    return detail
```

### WebSocket Endpoint

Pattern events streamed via **existing WebSocket infrastructure**:

```python
# api/websocket.py (EXISTING FILE - ADD PATTERN SUPPORT)

@app.websocket("/jobs/{job_id}/events")
async def job_event_stream(websocket: WebSocket, job_id: str):
    """
    Stream ALL events for a job (run, step, tool, pattern, etc.).
    Pattern events are multiplexed with existing event types.
    """
    await websocket.accept()

    # Subscribe to all event categories for this job
    def event_callback(event: dict):
        if event.get("job_id") == job_id:
            asyncio.create_task(websocket.send_json(event))

    subscription_id = event_bus.subscribe("*", event_callback)

    try:
        while True:
            await websocket.receive_text()  # Keep-alive ping
    finally:
        event_bus.unsubscribe(subscription_id)
```

Clients filter on the **frontend**:

```typescript
// Frontend filters pattern events from unified stream
ws.onmessage = (message) => {
  const event = JSON.parse(message.data);

  if (event.event_type.startsWith("pattern.")) {
    // Route to Pattern Activity Panel
    patternPanel.handleEvent(event);
  } else if (event.event_type.startsWith("run.")) {
    // Route to Run Dashboard
    runDashboard.handleEvent(event);
  }
  // ... etc
};
```

---

## 7. Implementation Roadmap

### Phase 1: Backend Foundation (Week 1)

**Goal**: Pattern execution + state persistence

- [ ] Add `pattern_runs` and `pattern_events` tables to existing SQLite schema
- [ ] Implement `PatternStateStore` (same pattern as existing stores)
- [ ] Add event emission to `PatternExecutor` at each lifecycle phase
- [ ] Integrate with existing event bus
- [ ] Write unit tests for state store and event emission

**Deliverables**:
- `core/state/pattern_state_store.py`
- Schema migration script
- Tests

### Phase 2: API Layer (Week 1-2)

**Goal**: Data access for UI components

- [ ] Implement `PatternClient` in `core/ui_clients/`
- [ ] Add CLI commands: `pattern-events`, `pattern-summary`, `pattern-detail`
- [ ] Add REST API endpoints in `api/routes/patterns.py`
- [ ] Extend WebSocket handler to include pattern events
- [ ] Write integration tests

**Deliverables**:
- `core/ui_clients/pattern_client.py`
- CLI commands working
- REST API working
- Tests

### Phase 3: GUI Component (Week 2-3)

**Goal**: Visual pattern activity panel

**Option A: Web-based GUI**
- [ ] Implement React `PatternActivityPanel` component
- [ ] Create `TimelineView`, `SummaryHeader`, `DetailDrawer` sub-components
- [ ] Connect to REST API + WebSocket
- [ ] Add to main GUI layout as new tab/panel
- [ ] Style with existing CSS framework

**Option B: TUI (Terminal UI)**
- [ ] Implement `textual` pattern panel widget
- [ ] Create timeline, summary, detail views
- [ ] Connect to Python API (`PatternClient`)
- [ ] Add to TUI layout

**Deliverables**:
- GUI panel implementation
- Integration with existing GUI/TUI
- Documentation

### Phase 4: Testing & Documentation (Week 3-4)

- [ ] End-to-end tests (pattern execution → event → UI update)
- [ ] Performance testing (handle 100+ events efficiently)
- [ ] User documentation
- [ ] Developer guide for adding new pattern visualizations
- [ ] Video demo

**Deliverables**:
- Test suite
- Documentation
- Demo materials

---

## Checklist: Modular Integration Compliance

### ✅ Architecture Compliance

- [x] Follows layered architecture (Presentation → API → Engine → Persistence)
- [x] No direct database access from GUI
- [x] Communicates via client APIs only
- [x] Self-contained module with clear boundaries
- [x] Reuses existing infrastructure (DB, event bus, WebSocket)

### ✅ API Compliance

- [x] Python client follows `StateClient`/`ToolsClient` pattern
- [x] CLI commands follow existing conventions (`--json`, `--limit`, etc.)
- [x] REST endpoints follow existing URL structure
- [x] WebSocket uses existing event stream (multiplexed)

### ✅ Event System Compliance

- [x] Events follow unified schema
- [x] Uses existing event bus
- [x] Correlation IDs link to existing entities
- [x] Event categories align with system taxonomy

### ✅ Data Model Compliance

- [x] SQLite tables in existing database
- [x] Consistent ID format (ULID)
- [x] JSON blobs for extensibility
- [x] Foreign key relationships to existing tables

### ✅ UI/UX Compliance

- [x] Panel-based design (fits into existing layout)
- [x] Timeline view (consistent with Logs panel)
- [x] Summary cards (consistent with Dashboard)
- [x] Detail drawer (consistent with Workstream Explorer)
- [x] Real-time updates via WebSocket

---

## Summary

The Pattern Activity Panel has been designed from the ground up to be **fully modular and compatible** with the existing GUI/TUI framework:

1. **Shares Infrastructure**: Same DB, event bus, WebSocket server, REST API pattern
2. **Follows Conventions**: Same client pattern, CLI pattern, endpoint pattern, event schema
3. **Standalone Module**: Can be developed, tested, and deployed independently
4. **Easy Integration**: Drop into existing GUI layout as new panel/tab
5. **No Breaking Changes**: Extends system without modifying existing components

The implementation roadmap shows how to build this incrementally, with each phase delivering working functionality that integrates seamlessly with the existing codebase.
