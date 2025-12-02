---
doc_id: DOC-PAT-PATTERN-EVENT-INTEGRATION-808
---

# Pattern Event System - Integration Guide

**Quick Start**: Wire pattern event tracking into your existing engine in 3 steps.

## Overview

The Pattern Event System provides observable pattern execution with minimal code changes. Events flow like this:

```
Your Code                Pattern Event System           Storage
──────────               ────────────────────           ───────
execute_pattern() ──→    emit_pattern_event()    ──→    state/events/pattern_events.jsonl
                         PatternRunAggregator    ──→    engine/state_store (DB)
                                                        
GUI Panel         ←──    GET /api/pattern-events ←──    Read from JSONL/DB
```

## Step 1: Add Event Emission (5 minutes)

### In your pattern executor code

**Before** (hypothetical existing code):
```python
# engine/pattern_executor.py
def execute_pattern(pattern_id, job_id, step_id, inputs):
    # ... resolve pattern ...
    # ... expand template ...
    # ... run tool ...
    return result
```

**After** (with event emission):
```python
from core.engine.pattern_events import emit_pattern_event, PatternRun

def execute_pattern(pattern_id, job_id, step_id, inputs):
    # Create pattern run
    pattern_run = PatternRun.create(
        pattern_id=pattern_id,
        job_id=job_id,
        operation_kind=inputs.get("operation_kind", "unknown"),
        step_id=step_id,
    )
    
    # Emit: selection resolved
    emit_pattern_event(
        event_type="pattern.selection.resolved",
        job_id=job_id,
        pattern_run_id=pattern_run.pattern_run_id,
        pattern_id=pattern_id,
        status="in_progress",
        details={
            "operation_kind": inputs["operation_kind"],
            "selection_method": "auto",
            "inputs_preview": inputs,
        },
        step_id=step_id,
    )
    
    # ... expand template ...
    
    emit_pattern_event(
        event_type="pattern.template.expanded",
        job_id=job_id,
        pattern_run_id=pattern_run.pattern_run_id,
        pattern_id=pattern_id,
        status="in_progress",
        details={
            "variables_resolved": len(template_vars),
            "generated_artifacts": artifact_paths,
        },
        step_id=step_id,
    )
    
    # ... run tool ...
    
    emit_pattern_event(
        event_type="pattern.execution.started",
        job_id=job_id,
        pattern_run_id=pattern_run.pattern_run_id,
        pattern_id=pattern_id,
        status="in_progress",
        details={
            "executor": "subprocess",
            "command": command_str,
        },
        step_id=step_id,
    )
    
    result = run_tool(command_str)
    
    # Emit: completed or failed
    if result.exit_code == 0:
        emit_pattern_event(
            event_type="pattern.execution.completed",
            job_id=job_id,
            pattern_run_id=pattern_run.pattern_run_id,
            pattern_id=pattern_id,
            status="success",
            details={
                "exit_code": 0,
                "duration_seconds": result.duration,
                "result_summary": result.summary,
                "artifacts": result.artifacts,
            },
            step_id=step_id,
        )
    else:
        emit_pattern_event(
            event_type="pattern.execution.failed",
            job_id=job_id,
            pattern_run_id=pattern_run.pattern_run_id,
            pattern_id=pattern_id,
            status="failed",
            details={
                "exit_code": result.exit_code,
                "error_type": "tool_error",
                "error_message": result.stderr,
            },
            step_id=step_id,
        )
    
    return result
```

**That's it!** Events are now logged to `state/events/pattern_events.jsonl`.

## Step 2: Test with CLI (2 minutes)

```bash
# Run example to generate sample events
python examples/pattern_events_example.py

# View events
python -m core.engine.pattern_inspect events

# View specific pattern run
python -m core.engine.pattern_inspect run PRUN-...

# Follow live events (for testing)
python -m core.engine.pattern_inspect events --follow
```

## Step 3: Extend JobStateStore (Optional, 10 minutes)

To integrate with your existing state store:

```python
# engine/state_store/job_state_store.py

from core.engine.pattern_events import PatternEventEmitter, PatternRunAggregator

class JobStateStore:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        db.init_db(self.db_path)
        
        # Add pattern event support
        self.pattern_emitter = PatternEventEmitter()
        self.pattern_aggregator = PatternRunAggregator(self.pattern_emitter)
    
    def get_pattern_events(self, job_id: str) -> List[Dict]:
        """Get pattern events for a job."""
        events = self.pattern_emitter.get_events(job_id=job_id)
        return [e.to_dict() for e in events]
    
    def get_pattern_runs(self, job_id: str) -> List[Dict]:
        """Get pattern runs for a job."""
        runs = self.pattern_aggregator.rebuild_from_events(job_id)
        return [r.to_dict() for r in runs]
    
    def get_pattern_run(self, pattern_run_id: str) -> Optional[Dict]:
        """Get specific pattern run."""
        run = self.pattern_aggregator.get_run(pattern_run_id)
        return run.to_dict() if run else None
```

## GUI Integration (Phase 3)

### API Endpoints

Add these to your engine service / GUI backend:

```python
# engine/api.py (or wherever your API routes are)

from flask import Flask, jsonify
from engine.state_store.job_state_store import JobStateStore

app = Flask(__name__)
state_store = JobStateStore()

@app.route('/api/jobs/<job_id>/pattern-events')
def get_pattern_events(job_id):
    """Get pattern events for a job."""
    events = state_store.get_pattern_events(job_id)
    return jsonify(events)

@app.route('/api/jobs/<job_id>/pattern-runs')
def get_pattern_runs(job_id):
    """Get pattern runs for a job."""
    runs = state_store.get_pattern_runs(job_id)
    return jsonify(runs)

@app.route('/api/pattern-runs/<pattern_run_id>')
def get_pattern_run(pattern_run_id):
    """Get specific pattern run details."""
    run = state_store.get_pattern_run(pattern_run_id)
    if not run:
        return jsonify({"error": "Pattern run not found"}), 404
    return jsonify(run)

@app.route('/api/pattern-runs/<pattern_run_id>/logs')
def get_pattern_run_logs(pattern_run_id):
    """Get raw logs for a pattern run."""
    # TODO: Implement log retrieval from artifacts
    pass
```

### GUI Component (React example)

```jsx
// gui/components/PatternActivityPanel.jsx

import React, { useEffect, useState } from 'react';

export function PatternActivityPanel({ jobId }) {
  const [events, setEvents] = useState([]);
  const [runs, setRuns] = useState([]);
  
  useEffect(() => {
    // Fetch pattern events
    fetch(`/api/jobs/${jobId}/pattern-events`)
      .then(r => r.json())
      .then(setEvents);
    
    // Fetch pattern runs summary
    fetch(`/api/jobs/${jobId}/pattern-runs`)
      .then(r => r.json())
      .then(setRuns);
  }, [jobId]);
  
  return (
    <div className="pattern-activity-panel">
      <h3>Pattern Activity</h3>
      
      {/* Summary Table */}
      <table>
        <thead>
          <tr>
            <th>Pattern</th>
            <th>Operation</th>
            <th>Status</th>
            <th>Duration</th>
          </tr>
        </thead>
        <tbody>
          {runs.map(run => (
            <tr key={run.pattern_run_id}>
              <td>{run.pattern_id}</td>
              <td>{run.operation_kind}</td>
              <td>
                <StatusBadge status={run.status} />
                {run.outputs?.finding_count && ` (${run.outputs.finding_count} findings)`}
              </td>
              <td>{run.duration_seconds?.toFixed(1)}s</td>
            </tr>
          ))}
        </tbody>
      </table>
      
      {/* Timeline */}
      <div className="pattern-timeline">
        {events.map(event => (
          <div key={event.event_id} className="timeline-item">
            <span className="timestamp">{formatTime(event.timestamp)}</span>
            <span className="pattern-id">{event.pattern_id}</span>
            <span className="event-type">{event.event_type.split('.').pop()}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
```

## Event Types Reference

| Event Type | When to Emit | Required Details |
|------------|--------------|------------------|
| `pattern.selection.started` | When pattern resolution begins | `operation_kind`, `candidate_patterns` |
| `pattern.selection.resolved` | When pattern selected successfully | `pattern_id`, `selection_method`, `inputs_preview` |
| `pattern.selection.failed` | When no suitable pattern found | `reason`, `attempted_patterns` |
| `pattern.template.expanded` | After template variable substitution | `variables_resolved`, `generated_artifacts` |
| `pattern.validation.started` | When pre-flight checks begin | `validation_type`, `checks` |
| `pattern.validation.completed` | When validation passes | `checks_passed`, `checks_failed` |
| `pattern.validation.failed` | When validation fails | `failed_checks` with errors |
| `pattern.execution.started` | When tool invocation begins | `executor`, `command` |
| `pattern.execution.completed` | When execution succeeds | `exit_code`, `duration_seconds`, `result_summary`, `artifacts` |
| `pattern.execution.failed` | When execution fails | `exit_code`, `error_type`, `error_message` |

## Best Practices

### 1. Emit events consistently

Always emit at least:
- `pattern.execution.started`
- `pattern.execution.completed` OR `pattern.execution.failed`

### 2. Use descriptive details

Good:
```python
details={
    "result_summary": {
        "finding_count": 12,
        "files_scanned": 47,
        "severity_breakdown": {"high": 2, "medium": 10}
    }
}
```

Bad:
```python
details={"result": "done"}
```

### 3. Include artifacts

Always list generated files:
```python
details={
    "artifacts": [
        "state/reports/semgrep/JOB-.../semgrep_report.json",
        "state/reports/semgrep/JOB-.../semgrep_summary.html",
    ]
}
```

### 4. Handle errors gracefully

```python
try:
    result = execute_tool(command)
    emit_pattern_event(..., status="success", ...)
except Exception as e:
    emit_pattern_event(
        event_type="pattern.execution.failed",
        status="failed",
        details={
            "error_type": type(e).__name__,
            "error_message": str(e),
        }
    )
    raise
```

## Validation

Validate events before using in production:

```bash
# Validate event schema
python -m core.validation validate-pattern-event < event.json

# Validate pattern run
python -m core.validation validate-pattern-run < pattern_run.json
```

## Troubleshooting

### Events not appearing in CLI

Check that events are being written:
```bash
ls -lh state/events/pattern_events.jsonl
tail -f state/events/pattern_events.jsonl
```

### Events missing details

Ensure you're passing a dict to `details=`:
```python
# ✓ Good
details={"operation_kind": "semgrep_scan"}

# ✗ Bad
details="semgrep_scan"  # Must be dict!
```

### Pattern run not rebuilding

Check events have correct `pattern_run_id`:
```bash
python -m core.engine.pattern_inspect events --pattern-run-id PRUN-...
```

All events for a run MUST share the same `pattern_run_id`.

## Next Steps

1. ✅ Add emission calls to your pattern executor
2. ✅ Test with CLI inspector
3. ✅ Extend JobStateStore (optional)
4. ⏳ Build GUI Pattern Activity Panel (Phase 3)
5. ⏳ Add WebSocket support for real-time updates (Phase 4)

## References

- **Specification**: [`docs/PATTERN_EVENT_SPEC.md`](PATTERN_EVENT_SPEC.md)
- **Schemas**: [`schema/pattern_event.v1.json`](../schema/pattern_event.v1.json), [`schema/pattern_run.v1.json`](../schema/pattern_run.v1.json)
- **Implementation**: [`core/engine/pattern_events.py`](../core/engine/pattern_events.py)
- **CLI Inspector**: [`core/engine/pattern_inspect.py`](../core/engine/pattern_inspect.py)
- **Example**: [`examples/pattern_events_example.py`](../examples/pattern_events_example.py)
