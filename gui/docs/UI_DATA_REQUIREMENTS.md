---
doc_id: DOC-GUIDE-UI-DATA-REQUIREMENTS-1424
---

# UI Component Data Requirements

This document defines the data requirements and API contracts for the 7 main UI components described in the interface specification.

## 1. Global Pipeline Dashboard

**Purpose**: Single overview of "factory health"

**Data Requirements**:
- Current workstreams/jobs running (count + list)
- File counts by lifecycle state
- Tool health summaries
- Throughput metrics (files/hour, jobs/hour)
- Error rates and top error types

**API Endpoints**:

```python
# Python API
from core.ui_clients import StateClient, ToolsClient

client = StateClient()
summary = client.get_pipeline_summary(run_id=optional_run_id)
# Returns: PipelineSummary with all dashboard metrics

tools_client = ToolsClient()
tool_summaries = tools_client.get_tools_summary()
# Returns: List[ToolSummary] for tool health cards
```

```bash
# CLI API
python -m core.ui_cli dashboard --json
python -m core.ui_cli tools --summary --json
```

**Response Format**:
```json
{
  "workstreams_running": 3,
  "workstreams_queued": 5,
  "workstreams_completed": 42,
  "workstreams_failed": 2,
  "files_intake": 10,
  "files_in_flight": 8,
  "files_committed": 120,
  "files_quarantined": 3,
  "files_per_hour": 45.2,
  "errors_per_hour": 1.5,
  "top_error_types": [
    ["syntax", 5],
    ["test_failed", 3]
  ]
}
```

---

## 2. Workstream & Job Explorer

**Purpose**: Drill-down into logical units of work

**Data Requirements**:
- List of active and recent workstreams
- Per-workstream: status, duration, phases, tools used, files touched
- Job records linked to workstreams

**API Endpoints**:

```python
from core.ui_clients import StateClient

client = StateClient()

# List workstreams
workstreams = client.list_workstreams(
    run_id=optional_run_id,
    status=optional_status,
    limit=100
)
# Returns: List[WorkstreamRecord]

# Get single workstream detail
ws = client.get_workstream(ws_id)
# Returns: WorkstreamRecord with full details

# Get workstream counts by status
counts = client.get_workstream_counts_by_status(run_id)
# Returns: Dict[str, int]
```

```bash
# CLI API
python -m core.ui_cli workstreams --run-id run-123 --json
python -m core.ui_cli workstream-counts --json
```

**Response Format**:
```json
{
  "ws_id": "ws-abc123",
  "run_id": "run-456",
  "status": "running",
  "label": "Phase 3 Refactor",
  "progress": {
    "current_phase": "PH-03",
    "completed_phases": 2,
    "total_phases": 5,
    "progress_percentage": 40.0
  },
  "start_time": "2025-01-15T10:00:00",
  "total_duration_sec": 3600.5,
  "files_processed": 15,
  "files_succeeded": 12,
  "files_quarantined": 1,
  "total_tool_invocations": 28,
  "worktree_path": ".worktrees/ws-abc123"
}
```

---

## 3. File Lifecycle & Routing View

**Purpose**: Track "where is my file?" through the pipeline

**Data Requirements**:
- One row per tracked file
- Current state, tool history, final disposition
- Filter by state/tool/workstream

**API Endpoints**:

```python
from core.ui_clients import StateClient
from core.ui_models import FileState

client = StateClient()

# List files with filters
files = client.list_files(
    state=FileState.IN_FLIGHT,
    workstream_id=optional_ws_id,
    tool_id=optional_tool_id,
    limit=100
)
# Returns: List[FileLifecycleRecord]

# Get single file detail
file = client.get_file_lifecycle(file_id)
# Returns: FileLifecycleRecord with complete history

# Get file counts by state
counts = client.get_file_counts_by_state(run_id)
# Returns: Dict[str, int]
```

```bash
# CLI API
python -m core.ui_cli files --state in_flight --json
python -m core.ui_cli file-counts --json
```

**Response Format**:
```json
{
  "file_id": "file-xyz789",
  "current_path": "src/module.py",
  "origin_path": "sandbox_repos/project/src/module.py",
  "file_role": "code",
  "current_state": "processing",
  "workstream_id": "ws-abc123",
  "state_timestamps": {
    "discovered": "2025-01-15T10:00:00",
    "classified": "2025-01-15T10:00:05",
    "processing": "2025-01-15T10:00:10"
  },
  "tools_touched": [
    {
      "timestamp": "2025-01-15T10:00:15",
      "tool_id": "aider",
      "tool_name": "Aider",
      "action": "refactor",
      "status": "success"
    }
  ],
  "first_seen": "2025-01-15T10:00:00",
  "last_processed": "2025-01-15T10:00:30"
}
```

---

## 4. Application / Tool Health Panel

**Purpose**: Per-adapter view of tool health and metrics

**Data Requirements**:
- Tool status (healthy/degraded/unreachable)
- Performance metrics (requests, latency, success rate)
- Capacity (concurrency, queue length)

**API Endpoints**:

```python
from core.ui_clients import ToolsClient

client = ToolsClient()

# List all tools
tools = client.list_tools()
# Returns: List[ToolHealthStatus]

# Get single tool health
tool = client.get_tool_health(tool_id)
# Returns: ToolHealthStatus

# Get summary for dashboard
summaries = client.get_tools_summary()
# Returns: List[ToolSummary]
```

```bash
# CLI API
python -m core.ui_cli tools --json
python -m core.ui_cli tools --tool-id aider --json
```

**Response Format**:
```json
{
  "tool_id": "aider",
  "display_name": "Aider",
  "category": "ai_editor",
  "version": "0.45.0",
  "status": "healthy",
  "last_successful_invocation": "2025-01-15T10:30:00",
  "metrics": {
    "requests_5min": 12,
    "requests_15min": 35,
    "requests_60min": 120,
    "success_count": 115,
    "failure_count": 5,
    "success_rate": 0.958,
    "mean_latency": 12.5,
    "p95_latency": 18.2,
    "max_concurrency": 4,
    "current_in_flight": 2,
    "queue_length": 3
  }
}
```

---

## 5. Error & Quarantine Center

**Purpose**: Central view of failures and quarantined files

**Data Requirements**:
- List of quarantined files and failed jobs
- Group by error type/plugin
- Remediation suggestions

**API Endpoints**:

```python
from core.ui_clients import StateClient
from core.ui_models import ErrorSeverity, ErrorCategory

client = StateClient()

# List errors with filters
errors = client.list_errors(
    run_id=optional_run_id,
    severity=ErrorSeverity.ERROR,
    category=ErrorCategory.SYNTAX,
    limit=100
)
# Returns: List[ErrorRecord]

# Get single error detail
error = client.get_error_record(error_id)
# Returns: ErrorRecord
```

```bash
# CLI API
python -m core.ui_cli errors --severity error --json
python -m core.ui_cli errors --category syntax --json
```

**Response Format**:
```json
{
  "error_id": "err-123",
  "entity_type": "file",
  "file_id": "file-xyz789",
  "ws_id": "ws-abc123",
  "tool_id": "aider",
  "severity": "error",
  "category": "syntax",
  "human_message": "Syntax error in generated code",
  "technical_details": "SyntaxError at line 42: unexpected indent",
  "recommendation": "Re-run with stricter syntax validation",
  "first_seen": "2025-01-15T10:00:00",
  "last_seen": "2025-01-15T10:05:00",
  "occurrence_count": 3,
  "quarantine_path": ".quarantine/file-xyz789",
  "can_retry": true,
  "auto_fix_available": false
}
```

---

## 6. Live Logs & Event Stream

**Purpose**: Cross-cutting event console with chronological view

**Data Requirements**:
- Event stream across all systems
- Filter by file/job/tool/severity/time
- Correlation IDs for linking

**API Endpoints**:

```python
from core.ui_clients import LogsClient
from datetime import datetime, timedelta

client = LogsClient()

# Query events with filters
events = client.query_events(
    run_id=optional_run_id,
    tool_id=optional_tool_id,
    event_type=optional_event_type,
    severity=optional_severity,
    since=datetime.now() - timedelta(hours=1),
    limit=500
)
# Returns: List[Dict] of event records

# Export logs to file
count = client.export_logs(run_id, output_path)
# Returns: int (number of events exported)
```

```bash
# CLI API (future)
python -m core.ui_cli events --run-id run-123 --json
python -m core.ui_cli events --tool-id aider --since 1h --json
```

**Event Format**:
```json
{
  "event_type": "tool_invoked",
  "timestamp": "2025-01-15T10:00:00.123456",
  "severity": "info",
  "message": "Aider invoked for file refactor",
  "run_id": "run-456",
  "workstream_id": "ws-abc123",
  "file_id": "file-xyz789",
  "tool_id": "aider",
  "payload": {
    "command": "aider --message-file /tmp/msg.txt",
    "working_dir": ".worktrees/ws-abc123"
  }
}
```

---

## 7. Controls & Settings Panel

**Purpose**: Control surface for pipeline execution

**Data Requirements**:
- Current run mode (running/draining/paused)
- Concurrency limits
- Headless policy settings
- Sandbox/worktree configuration

**API Endpoints**:

```python
# Future: EngineClient
from core.ui_clients import EngineClient

client = EngineClient()

# Get current control state
state = client.get_control_state()
# Returns: PipelineControlState

# Update settings (write operations)
client.set_run_mode(RunMode.DRAINING)
client.set_concurrency(global_max=8, per_tool={"aider": 2})
```

**Response Format**:
```json
{
  "run_mode": "running",
  "global_max_workers": 4,
  "per_tool_concurrency": {
    "aider": 2,
    "codex": 1,
    "tests": 4
  },
  "headless_policy": "require_review_if_risky",
  "active_worktree": ".worktrees/ws-abc123",
  "log_level": "info"
}
```

---

## Data Correlation

All data models use consistent correlation IDs for cross-component linking:

- **run_id**: Links to a specific pipeline run
- **workstream_id (ws_id)**: Links to a workstream
- **job_id**: Links to a job (job-based execution)
- **file_id**: Links to a specific file
- **tool_id**: Links to a tool/adapter

These IDs enable:
1. "Show all events for this file" across tools
2. "Show all files touched by this workstream"
3. "Show all tool invocations in this run"
4. "Show error history for this file"

## Implementation Status

✅ **Completed**:
- Enhanced event bus with unified event schema
- Database schema extensions for file lifecycle and errors
- Data models for all 7 UI components
- StateClient, ToolsClient, LogsClient
- CLI interface for all query operations

⏳ **Pending**:
- EngineClient for control operations
- Tool adapter instrumentation
- Event emission from orchestrator/scheduler
- Real-time event subscriptions
- WebSocket API for live updates

## Usage Examples

### TUI Implementation
```python
from core.ui_clients import StateClient, ToolsClient

# Dashboard panel
state_client = StateClient()
summary = state_client.get_pipeline_summary()
print(f"Running: {summary.workstreams_running}")
print(f"Files committed: {summary.files_committed}")

# Tool health panel
tools_client = ToolsClient()
for tool in tools_client.list_tools():
    print(f"{tool.display_name}: {tool.status.value}")
```

### GUI Implementation
```python
import json
import subprocess

# Call CLI and parse JSON
result = subprocess.run(
    ["python", "-m", "core.ui_cli", "dashboard", "--json"],
    capture_output=True,
    text=True
)
dashboard_data = json.loads(result.stdout)

# Update UI widgets
update_workstreams_widget(dashboard_data["workstreams_running"])
update_files_widget(dashboard_data["files_committed"])
```
