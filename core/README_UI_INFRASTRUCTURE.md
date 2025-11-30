---
doc_id: DOC-CORE-README-UI-INFRASTRUCTURE-059
---

# User-Facing Interface Infrastructure

This directory contains the core infrastructure for building TUI/GUI frontends on top of the AI Development Pipeline.

## Overview

The UI infrastructure provides:

1. **Unified Event System** - Comprehensive event tracking across all pipeline components
2. **File Lifecycle Tracking** - Complete visibility into file states and transformations
3. **Tool Health Monitoring** - Real-time metrics and status for all tools/adapters
4. **Error & Quarantine Management** - Structured error records for troubleshooting
5. **Query APIs** - Read-only clients for accessing pipeline state
6. **CLI Interface** - JSON-emitting commands for programmatic access

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     UI Layer (TUI/GUI)                  │
│  - Dashboard Panel    - Workstream Explorer             │
│  - File Lifecycle     - Tool Health                     │
│  - Error Center       - Event Stream                    │
│  - Controls Panel                                       │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ JSON API / CLI
                   │
┌──────────────────▼──────────────────────────────────────┐
│                   Query Clients                          │
│  - StateClient    - ToolsClient    - LogsClient         │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ Direct DB Access
                   │
┌──────────────────▼──────────────────────────────────────┐
│                  State Database (SQLite)                 │
│  - file_lifecycle          - error_records              │
│  - tool_health_metrics     - uet_events                 │
│  - workstreams             - runs                       │
└─────────────────────────────────────────────────────────┘
```

## Core Modules

### Event Bus (`core/engine/event_bus.py`)
Central event logging and routing system.

**Features**:
- 40+ event types covering all pipeline events
- Correlation IDs (run_id, ws_id, job_id, file_id, tool_id)
- Event severity levels (debug, info, warning, error, critical)
- Flexible querying with multiple filters
- JSONL export for external analysis

**Usage**:
```python
from core.engine.event_bus import Event, EventBus, EventType, EventSeverity

bus = EventBus()

# Emit an event
bus.emit(Event(
    event_type=EventType.TOOL_INVOKED,
    timestamp=datetime.now(timezone.utc),
    severity=EventSeverity.INFO,
    message="Aider invoked for refactor",
    run_id=run_id,
    file_id=file_id,
    tool_id="aider",
    payload={"action": "refactor"}
))

# Query events
events = bus.query(
    run_id=run_id,
    tool_id="aider",
    limit=100
)
```

### UI Data Models (`core/ui_models.py`)
Strongly-typed data models for all UI components.

**Models**:
- `FileLifecycleRecord` - Complete file tracking
- `ToolHealthStatus` - Tool metrics and status
- `WorkstreamRecord` - Workstream progress
- `ErrorRecord` - Structured errors
- `PipelineSummary` - Dashboard data

### Query Clients (`core/ui_clients.py`)
Read-only APIs for querying pipeline state.

**StateClient**:
```python
from core.ui_clients import StateClient

client = StateClient()

# Get dashboard summary
summary = client.get_pipeline_summary(run_id)

# List files by state
files = client.list_files(state=FileState.IN_FLIGHT, limit=100)

# List workstreams
workstreams = client.list_workstreams(run_id=run_id)

# List errors
errors = client.list_errors(severity=ErrorSeverity.ERROR)
```

**ToolsClient**:
```python
from core.ui_clients import ToolsClient

client = ToolsClient()

# Get all tools
tools = client.list_tools()

# Get specific tool health
tool = client.get_tool_health("aider")

# Get summary for dashboard
summaries = client.get_tools_summary()
```

### CLI Interface (`core/ui_cli.py`)
Command-line interface with JSON output.

**Commands**:
```bash
# Dashboard summary
python -m core.ui_cli dashboard --json

# File queries
python -m core.ui_cli files --state in_flight --json
python -m core.ui_cli file-counts --run-id run-123 --json

# Workstream queries
python -m core.ui_cli workstreams --run-id run-123 --json
python -m core.ui_cli workstream-counts --json

# Error queries
python -m core.ui_cli errors --severity error --json
python -m core.ui_cli errors --category syntax --json

# Tool health
python -m core.ui_cli tools --json
python -m core.ui_cli tools --summary --json
```

### Tool Instrumentation (`core/tool_instrumentation.py`)
Helpers for tool adapters to emit metrics and events.

**Usage**:
```python
from core.tool_instrumentation import track_tool_invocation

# Track tool invocation automatically
with track_tool_invocation(
    tool_id="aider",
    tool_name="Aider",
    action="refactor",
    run_id=run_id,
    file_id=file_id
) as tracker:
    # Run tool
    result = run_aider()
    tracker.set_output_size(len(result))
    # Metrics automatically recorded on exit
```

### File Lifecycle (`core/file_lifecycle.py`)
Utilities for tracking files through the pipeline.

**Usage**:
```python
from core.file_lifecycle import (
    register_file,
    update_file_state,
    record_tool_touch,
    mark_file_committed,
    mark_file_quarantined
)

# Register file when discovered
file_id = register_file(
    file_path="src/module.py",
    file_role="code",
    workstream_id=ws_id,
    run_id=run_id
)

# Update state as file progresses
update_file_state(file_id, "processing", tool_id="aider")

# Record tool interaction
record_tool_touch(
    file_id=file_id,
    tool_id="aider",
    tool_name="Aider",
    action="refactor",
    status="success"
)

# Mark as committed
mark_file_committed(
    file_id=file_id,
    commit_sha="abc123",
    repo_path="src/module.py"
)
```

### Error Records (`core/error_records.py`)
Structured error tracking for the quarantine center.

**Usage**:
```python
from core.error_records import create_error_record

error_id = create_error_record(
    entity_type="file",
    human_message="Syntax error in generated code",
    severity="error",
    category="syntax",
    file_id=file_id,
    tool_id="aider",
    technical_details="SyntaxError at line 42",
    recommendation="Re-run with stricter validation",
    quarantine_path=".quarantine/file-123"
)
```

## Database Schema

See `schema/schema.sql` for the complete schema. Key tables:

### File Lifecycle
- `file_lifecycle` - Current file state and metadata
- `file_state_history` - State transition timeline
- `file_tool_touches` - Tool interaction log

### Error Tracking
- `error_records` - Structured error records
- `errors` - Legacy error table (still used by some components)

### Tool Health
- `tool_health_metrics` - Current tool status and metrics

### Events
- `uet_events` - Unified event log

## UI Component Data Requirements

See `docs/UI_DATA_REQUIREMENTS.md` for detailed specifications of what data each UI panel needs and how to query it.

**7 UI Components**:
1. Global Pipeline Dashboard
2. Workstream & Job Explorer
3. File Lifecycle & Routing View
4. Application / Tool Health Panel
5. Error & Quarantine Center
6. Live Logs & Event Stream
7. Controls & Settings Panel

## Examples

See `examples/ui_infrastructure_usage.py` for comprehensive usage examples:

```bash
# Run the examples
PYTHONPATH=. python examples/ui_infrastructure_usage.py
```

This demonstrates:
- File processing workflow with full tracking
- Tool health monitoring
- Dashboard queries
- CLI usage patterns

## Integration Guide

### For Tool Adapter Developers

Wrap your tool invocations with instrumentation:

```python
from core.tool_instrumentation import track_tool_invocation
from core.file_lifecycle import update_file_state, record_tool_touch

# Before invoking tool
update_file_state(file_id, "processing", tool_id="your_tool")

# Invoke with tracking
with track_tool_invocation(
    tool_id="your_tool",
    tool_name="Your Tool",
    action="your_action",
    run_id=run_id,
    file_id=file_id
):
    result = your_tool_command()

# Record the interaction
record_tool_touch(
    file_id=file_id,
    tool_id="your_tool",
    tool_name="Your Tool",
    action="your_action",
    status="success"
)
```

### For UI Developers

Use the clients to query data:

```python
from core.ui_clients import StateClient, ToolsClient

# Initialize clients
state_client = StateClient()
tools_client = ToolsClient()

# Get dashboard data
summary = state_client.get_pipeline_summary()
tool_summaries = tools_client.get_tools_summary()

# Update your UI
update_dashboard(
    workstreams_running=summary.workstreams_running,
    files_committed=summary.files_committed,
    tools=tool_summaries
)
```

Or use the CLI for JSON output:

```python
import subprocess
import json

result = subprocess.run(
    ["python", "-m", "core.ui_cli", "dashboard", "--json"],
    capture_output=True,
    text=True
)
data = json.loads(result.stdout)
```

## Correlation IDs

All events, files, errors, and metrics use consistent correlation IDs:

- **run_id**: Links to a pipeline run
- **workstream_id (ws_id)**: Links to a workstream
- **job_id**: Links to a job (job-based execution)
- **file_id**: Links to a specific file
- **tool_id**: Links to a tool/adapter

This enables powerful cross-component queries like:
- "Show all events for this file across all tools"
- "Show all files touched by this workstream"
- "Show tool health for tools used in this run"

## Future Work

- [ ] Real-time event subscriptions (WebSocket/SSE)
- [ ] EngineClient for control operations (pause/resume/cancel)
- [ ] Plugin system for UI panels
- [ ] Percentile-based latency metrics (P50, P95, P99)
- [ ] Time-window metrics (5m, 15m, 1h, 24h)
- [ ] Event replay and debugging tools
- [ ] Grafana/Prometheus exporter

## Testing

Run tests (when available):

```bash
pytest tests/test_ui_infrastructure.py -v
```

Manual testing with examples:

```bash
PYTHONPATH=. python examples/ui_infrastructure_usage.py
```

## License

Same as parent project.
