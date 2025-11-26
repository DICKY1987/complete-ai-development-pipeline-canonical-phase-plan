# Pattern Events - Quick Reference Card

## 🚀 Quick Start (Copy-Paste)

```python
from core.engine.pattern_events import emit_pattern_event

# Start execution
emit_pattern_event(
    event_type="pattern.execution.started",
    job_id="JOB-...",
    pattern_run_id="PRUN-...",
    pattern_id="PAT-SEMGRP-001",
    status="in_progress",
    details={"command": "semgrep --config auto ..."},
)

# Complete execution
emit_pattern_event(
    event_type="pattern.execution.completed",
    job_id="JOB-...",
    pattern_run_id="PRUN-...",
    pattern_id="PAT-SEMGRP-001",
    status="success",
    details={
        "exit_code": 0,
        "duration_seconds": 18.7,
        "result_summary": {"finding_count": 12}
    },
)
```

## 📊 Event Types (Lifecycle Order)

| # | Event Type | Status | When |
|---|------------|--------|------|
| 1 | `pattern.selection.started` | `in_progress` | Pattern resolution begins |
| 2 | `pattern.selection.resolved` | `in_progress` | Pattern selected |
| 3 | `pattern.template.expanded` | `in_progress` | Variables substituted |
| 4 | `pattern.validation.started` | `in_progress` | Pre-flight checks begin |
| 5 | `pattern.validation.completed` | `in_progress` | Validation passed |
| 6 | `pattern.execution.started` | `in_progress` | Tool invocation begins |
| 7 | `pattern.execution.completed` | `success` | Execution succeeded |

**Failure events**: `pattern.selection.failed`, `pattern.validation.failed`, `pattern.execution.failed`

## 🎯 Required Details (Per Event)

### `pattern.execution.started`
```python
details={
    "executor": "subprocess",
    "command": "semgrep --config auto ...",
}
```

### `pattern.execution.completed`
```python
details={
    "exit_code": 0,
    "duration_seconds": 18.74,
    "result_summary": {
        "finding_count": 12,
        "files_scanned": 47,
    },
    "artifacts": [
        "state/reports/semgrep/.../report.json"
    ],
}
```

### `pattern.execution.failed`
```python
details={
    "exit_code": 1,
    "error_type": "tool_error",
    "error_message": "semgrep: config file invalid",
}
```

## 🔍 CLI Commands

```bash
# View all events
python -m core.engine.pattern_inspect events

# View events for specific job
python -m core.engine.pattern_inspect events --job-id JOB-...

# View pattern run details
python -m core.engine.pattern_inspect run PRUN-...

# Follow events in real-time
python -m core.engine.pattern_inspect events --follow

# Run example
python examples/pattern_events_example.py
```

## 📁 File Locations

```
state/events/pattern_events.jsonl              # Global event log
state/events/jobs/{job_id}/pattern_events.jsonl # Job-scoped log
```

## 🧩 Pattern Run Object

```python
{
    "pattern_run_id": "PRUN-...",
    "pattern_id": "PAT-SEMGRP-001",
    "job_id": "JOB-...",
    "status": "success",
    "started_at": "2025-11-26T14:46:52Z",
    "finished_at": "2025-11-26T14:47:10Z",
    "duration_seconds": 18.7,
    "inputs": {"target_paths": ["src/", "tests/"]},
    "outputs": {"exit_code": 0, "finding_count": 12},
    "artifacts": ["state/reports/.../report.json"],
    "events": ["EVT-...", "EVT-...", ...],
}
```

## ⚡ Integration Checklist

- [ ] Import `emit_pattern_event` in your pattern executor
- [ ] Emit `pattern.execution.started` before tool invocation
- [ ] Emit `pattern.execution.completed` OR `pattern.execution.failed` after
- [ ] Include `exit_code`, `duration_seconds`, `result_summary` in completed event
- [ ] Test with `python -m core.engine.pattern_inspect events`

## 🎨 Status Values

| Status | Meaning | Color |
|--------|---------|-------|
| `pending` | Not started | Gray |
| `in_progress` | Running | Blue |
| `success` | Completed successfully | Green |
| `failed` | Execution failed | Red |
| `warning` | Completed with issues | Yellow |
| `skipped` | Not executed | Gray |

## 📚 Documentation

- **Spec**: `docs/PATTERN_EVENT_SPEC.md`
- **Integration**: `docs/PATTERN_EVENT_INTEGRATION.md`
- **Delivery Summary**: `docs/PATTERN_EVENT_DELIVERY_SUMMARY.md`
- **Schemas**: `schema/pattern_event.v1.json`, `schema/pattern_run.v1.json`
- **Code**: `core/engine/pattern_events.py`

## 🐛 Troubleshooting

**Events not appearing?**
```bash
# Check if file exists
ls -lh state/events/pattern_events.jsonl

# Tail events file
tail -f state/events/pattern_events.jsonl
```

**Module not found?**
```bash
# Set PYTHONPATH
export PYTHONPATH=$PWD  # Linux/Mac
$env:PYTHONPATH = "$PWD"  # Windows PowerShell
```

**Invalid event?**
- Ensure `details` is a dict, not a string
- Check all required fields are present
- Validate against schema: `schema/pattern_event.v1.json`

## 💡 Pro Tips

1. **Always pair start/complete events** - Every `started` needs a `completed` or `failed`
2. **Include artifacts** - List all generated files in `completed` event
3. **Use job-scoped logs** - Pass `job_scoped=True` to `emitter.emit()` for isolation
4. **Aggregate on-demand** - Use `PatternRunAggregator` to rebuild runs from events
5. **Follow pattern**: Selection → Template → Validation → Execution

## 🔗 Quick Links

- Example: `examples/pattern_events_example.py`
- CLI: `core/engine/pattern_inspect.py`
- API: `core/engine/pattern_events.py`

---

**Need more?** See `docs/PATTERN_EVENT_INTEGRATION.md` for step-by-step guide.
