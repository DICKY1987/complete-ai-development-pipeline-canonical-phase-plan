---
doc_id: DOC-GUIDE-PIPELINE-RADAR-PLUGIN-927
---

# Pipeline Radar Plugin

## Overview

The **Pipeline Radar** is a real-time monitoring plugin for the AI Development Pipeline. It provides a visual dashboard for tracking pipeline runs, workstreams, and individual steps as they execute.

## Purpose

Provide developers and stakeholders with immediate visibility into:
- Active pipeline runs
- Workstream progress and status
- Step-level execution details
- Real-time error detection
- Performance metrics

## Architecture

### Data Flow

```
Pipeline Engine → Event Bus → Pipeline Radar → UI Display
      ↓              ↓              ↓              ↓
   Execution      Publish        Subscribe      Render
   Events         Events         Events         View
```

### Components

1. **Event Listener**: Subscribes to pipeline events
2. **State Aggregator**: Maintains current pipeline state
3. **Visualization Engine**: Renders radar view
4. **Alert Manager**: Handles error notifications

## Features

### Real-Time Run Tracking

Display all active pipeline runs with:
- Run ID and status
- Start time and duration
- Progress percentage
- Current step/workstream

### Workstream Monitoring

For each run, show:
- Workstream name and status
- Number of completed/total steps
- Duration per workstream
- Resource utilization

### Step-Level Visibility

Drill down to individual steps:
- Step name and type
- Execution status (queued, running, completed, failed)
- Duration
- Output/logs preview

### Error Highlighting

Visual indicators for:
- Failed steps (red)
- Warning states (yellow)
- Blocked workstreams (orange)
- Critical errors (flashing red)

### Performance Metrics

Track pipeline health:
- Average step duration
- Throughput (steps/hour)
- Success rate
- Queue depth

## UI Design

### Radar View

```
┌────────────────────────────────────────────────────────────┐
│                     PIPELINE RADAR                         │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Run: ci-validation-001              [████████░░] 80%     │
│  ├─ validate-python     ✓ Complete   2.3s                 │
│  ├─ validate-docs       ⏳ Running    1.1s                 │
│  └─ validate-config     ○ Pending    -                    │
│                                                            │
│  Run: feature-xyz-002                [███░░░░░░░] 30%     │
│  ├─ lint-check          ✓ Complete   1.8s                 │
│  ├─ type-check          ✗ Failed     0.5s                 │
│  └─ test-suite          ○ Blocked    -                    │
│                                                            │
├────────────────────────────────────────────────────────────┤
│  Recent Errors:                                            │
│  ⚠ ruff: E501 line too long (src/main.py:42)              │
│  ⚠ mypy: Incompatible types (src/utils.py:15)             │
│                                                            │
├────────────────────────────────────────────────────────────┤
│  Performance:                                              │
│  Throughput: 12 steps/hour  |  Success Rate: 95.5%        │
│  Avg Duration: 1.8s         |  Queue Depth: 3             │
└────────────────────────────────────────────────────────────┘
```

### Status Icons

- `✓` - Completed successfully
- `⏳` - Currently running
- `○` - Pending (not started)
- `✗` - Failed
- `⊗` - Blocked (dependency failed)
- `⚠` - Warning (non-fatal error)

### Color Coding

- **Green**: Successful completion
- **Blue**: Running
- **Gray**: Pending
- **Red**: Failed
- **Orange**: Blocked/Warning
- **Yellow**: Degraded performance

## Event Subscriptions

The Pipeline Radar subscribes to these events:

```python
events = [
    "run.started",
    "run.completed",
    "run.failed",
    "workstream.started",
    "workstream.completed",
    "workstream.failed",
    "step.started",
    "step.completed",
    "step.failed",
    "step.warning"
]
```

## API Integration

### REST API

```python
# Get all active runs
GET /api/radar/runs/active

# Get run details
GET /api/radar/runs/{run_id}

# Get workstream details
GET /api/radar/workstreams/{workstream_id}

# Get performance metrics
GET /api/radar/metrics
```

### WebSocket

```javascript
// Subscribe to radar updates
socket.on('radar:update', (data) => {
  updateRadarView(data);
});

// Handle new run
socket.on('run:started', (run) => {
  addRunToRadar(run);
});

// Handle completed run
socket.on('run:completed', (run) => {
  markRunComplete(run);
});
```

## Configuration

```yaml
# config/pipeline_radar.yaml
radar:
  refresh_interval: 1.0  # seconds
  max_runs_displayed: 10
  show_completed_runs: true
  completed_run_ttl: 300  # seconds (5 minutes)
  error_notification: true
  performance_tracking: true
```

## Implementation Notes

### State Management

The radar maintains an in-memory state of all active runs:

```python
class RadarState:
    active_runs: Dict[str, RunStatus]
    completed_runs: List[RunStatus]
    metrics: PerformanceMetrics

    def update_run(self, run_id: str, status: RunStatus):
        """Update run status"""

    def add_run(self, run: RunStatus):
        """Add new run to radar"""

    def remove_run(self, run_id: str):
        """Remove completed run after TTL"""
```

### Performance Considerations

- **Throttle updates**: Max 10 updates/second
- **Debounce rapid events**: Group events within 100ms window
- **Lazy loading**: Only render visible runs
- **Memory management**: Purge old completed runs

### Error Handling

- **Connection loss**: Show offline indicator, queue events
- **State desync**: Periodic state refresh from engine
- **Event replay**: On reconnect, fetch missed events

## Integration with TUI

The Pipeline Radar can be embedded as a panel in the TUI:

```python
from gui.tui_app.core.panel_registry import register_panel
from gui.tui_app.core.panel_plugin import PanelPlugin

@register_panel("radar")
class PipelineRadarPanel(PanelPlugin):
    @property
    def panel_id(self) -> str:
        return "radar"

    @property
    def title(self) -> str:
        return "Pipeline Radar"

    def create_widget(self, context):
        return RadarWidget(context)
```

## Future Enhancements

1. **Filtering**: Filter by run status, tags, or timeframe
2. **Search**: Search for specific runs or workstreams
3. **Historical view**: View past runs and trends
4. **Alerts**: Configurable alerts for failures
5. **Export**: Export radar state as JSON/CSV
6. **Graphs**: Visualize metrics over time

## Related Documents

- [GUI Development Guide](GUI_DEVELOPMENT_GUIDE.md)
- [TUI Panel Framework Guide](TUI_PANEL_FRAMEWORK_COMPLETION_REPORT.md)
- [Architecture Boundaries](architecture-boundaries.md)
