---
doc_id: DOC-PAT-PATTERN-EVENT-SPEC-809
---

# Pattern Event Specification

**Version**: 1.0.0  
**Status**: Draft  
**Last Updated**: 2025-11-26

## Overview

This specification defines the event model for pattern execution lifecycle tracking. It enables real-time monitoring, GUI visualization, and post-execution analysis of Universal Execution Template (UET) pattern usage within the job-based execution engine.

## Goals

1. **Observable pattern execution** – Track when patterns are selected, expanded, executed, and completed
2. **GUI integration** – Provide structured data for Pattern Activity Panel visualization
3. **Debugging & telemetry** – Enable pattern performance analysis and failure diagnosis
4. **Minimal disruption** – Wire into existing `engine/` and `core/state/` infrastructure

## Event Model

### Event Types

Pattern lifecycle events follow this sequence:

```
pattern.selection.started
  ↓
pattern.selection.resolved | pattern.selection.failed
  ↓
pattern.template.expanded
  ↓
pattern.validation.started
  ↓
pattern.validation.completed | pattern.validation.failed
  ↓
pattern.execution.started
  ↓
pattern.execution.completed | pattern.execution.failed
```

### Core Event Schema

All pattern events **MUST** include these fields:

```json
{
  "event_id": "EVT-01JH9G6ERNRJX456M3HQE10ZB2",
  "event_type": "pattern.execution.started",
  "timestamp": "2025-11-26T07:15:12.123Z",
  "job_id": "JOB-01JH9F8P2ZJ1A8E5R6C792Q2EQ",
  "step_id": "STEP-003",
  "pattern_run_id": "PRUN-01JH9FDZKAG2J47A4WSK53JWZ1",
  "pattern_id": "PAT-SEMGRP-001",
  "status": "in_progress",
  "details": {}
}
```

#### Field Specifications

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `event_id` | `string` | **MUST** | ULID prefixed with `EVT-` |
| `event_type` | `string` | **MUST** | One of the defined event types (see below) |
| `timestamp` | `string` | **MUST** | ISO 8601 datetime with timezone (UTC) |
| `job_id` | `string` | **MUST** | ULID of parent job, prefixed `JOB-` |
| `step_id` | `string` | **SHOULD** | ULID of job step, prefixed `STEP-`. Null for job-level patterns |
| `pattern_run_id` | `string` | **MUST** | ULID of this pattern execution, prefixed `PRUN-` |
| `pattern_id` | `string` | **MUST** | Pattern identifier (e.g., `PAT-SEMGRP-001`) |
| `status` | `string` | **MUST** | Current status: `in_progress`, `success`, `failed`, `warning`, `skipped` |
| `details` | `object` | **MUST** | Event-specific metadata (see per-event schemas) |

### Event Type Definitions

#### 1. `pattern.selection.started`

Emitted when engine begins pattern resolution for a job step.

**Details schema**:
```json
{
  "operation_kind": "semgrep_scan",
  "context": {
    "tool": "semgrep",
    "language": "python",
    "file_types": [".py"]
  },
  "candidate_patterns": ["PAT-SEMGRP-001", "PAT-SEMGRP-002"]
}
```

#### 2. `pattern.selection.resolved`

Emitted when pattern is successfully selected and bound.

**Details schema**:
```json
{
  "operation_kind": "semgrep_scan",
  "pattern_id": "PAT-SEMGRP-001",
  "selection_method": "explicit",  // or "auto", "fallback"
  "inputs_preview": {
    "target_paths": ["src/", "tests/"],
    "severity": "medium+"
  }
}
```

#### 3. `pattern.selection.failed`

Emitted when no suitable pattern found or selection fails.

**Details schema**:
```json
{
  "operation_kind": "pytest_suite",
  "reason": "no_matching_pattern",
  "attempted_patterns": ["PAT-PYTEST-001"],
  "error": "Pattern requires pytest>=7.0, found 6.2.5"
}
```

#### 4. `pattern.template.expanded`

Emitted after successful template variable substitution.

**Details schema**:
```json
{
  "template_version": "1.2.0",
  "variables_resolved": 12,
  "generated_artifacts": [
    ".worktrees/JOB-../semgrep.config.yaml",
    ".worktrees/JOB-../run_semgrep.sh"
  ],
  "command_preview": "semgrep --config auto --severity medium ..."
}
```

#### 5. `pattern.validation.started`

Emitted when pre-flight validation begins.

**Details schema**:
```json
{
  "validation_type": "preflight",
  "checks": [
    "tool_availability",
    "target_paths_exist",
    "config_file_valid"
  ]
}
```

#### 6. `pattern.validation.completed`

Emitted when validation passes.

**Details schema**:
```json
{
  "validation_type": "preflight",
  "checks_passed": 3,
  "checks_failed": 0,
  "warnings": []
}
```

#### 7. `pattern.validation.failed`

Emitted when validation fails.

**Details schema**:
```json
{
  "validation_type": "preflight",
  "checks_passed": 2,
  "checks_failed": 1,
  "failed_checks": [
    {
      "check": "target_paths_exist",
      "error": "Path does not exist: tests/integration/"
    }
  ]
}
```

#### 8. `pattern.execution.started`

Emitted when pattern executor begins tool invocation.

**Details schema**:
```json
{
  "executor": "subprocess",
  "command": "semgrep --config auto --severity medium+ src/ tests/",
  "working_dir": "/path/to/.worktrees/JOB-01JH9F8P2ZJ1A8E5R6C792Q2EQ",
  "timeout_seconds": 300
}
```

#### 9. `pattern.execution.completed`

Emitted when pattern execution finishes successfully.

**Details schema**:
```json
{
  "exit_code": 0,
  "duration_seconds": 18.74,
  "result_summary": {
    "finding_count": 12,
    "files_scanned": 47,
    "errors": 0
  },
  "artifacts": [
    "state/reports/semgrep/JOB-01JH9F8P2ZJ1A8E5R6C792Q2EQ/semgrep_report.json",
    "state/reports/semgrep/JOB-01JH9F8P2ZJ1A8E5R6C792Q2EQ/semgrep_summary.html"
  ],
  "stdout_lines": 124,
  "stderr_lines": 2
}
```

#### 10. `pattern.execution.failed`

Emitted when pattern execution fails.

**Details schema**:
```json
{
  "exit_code": 1,
  "duration_seconds": 5.32,
  "error_type": "tool_error",
  "error_message": "semgrep: config file invalid: duplicate rule ID 'python.security.injection'",
  "stdout_preview": "...",
  "stderr_preview": "..."
}
```

## Pattern Run Object

The `pattern_run` object represents the complete execution record for a pattern instance. It aggregates all events into a single, queryable entity.

### Schema

```json
{
  "pattern_run_id": "PRUN-01JH9FDZKAG2J47A4WSK53JWZ1",
  "pattern_id": "PAT-SEMGRP-001",
  "pattern_version": "1.2.0",
  "job_id": "JOB-01JH9F8P2ZJ1A8E5R6C792Q2EQ",
  "step_id": "STEP-003",
  "operation_kind": "semgrep_scan",
  "status": "success",
  "started_at": "2025-11-26T07:15:12.123Z",
  "finished_at": "2025-11-26T07:15:30.891Z",
  "duration_seconds": 18.768,
  "inputs": {
    "target_paths": ["src/", "tests/"],
    "severity": "medium+",
    "config_profile": "default"
  },
  "outputs": {
    "exit_code": 0,
    "finding_count": 12,
    "files_scanned": 47,
    "errors": 0
  },
  "artifacts": [
    "state/reports/semgrep/JOB-01JH9F8P2ZJ1A8E5R6C792Q2EQ/semgrep_report.json"
  ],
  "events": [
    "EVT-01JH9G6ERNRJX456M3HQE10ZB2",
    "EVT-01JH9G6ERNRJX456M3HQE10ZB3",
    "EVT-01JH9G6ERNRJX456M3HQE10ZB4"
  ],
  "metrics": {
    "template_expansion_ms": 234,
    "validation_ms": 89,
    "execution_ms": 18768,
    "artifact_generation_ms": 412
  },
  "tool_metadata": {
    "tool_name": "semgrep",
    "tool_version": "1.45.0",
    "command": "semgrep --config auto --severity medium+ src/ tests/"
  }
}
```

## Storage & Persistence

### Event Storage (JSONL)

Pattern events **MUST** be written to JSONL files for durability and queryability:

**Global event log**:
```
state/events/pattern_events.jsonl
```

**Job-scoped event log** (optional, for isolation):
```
state/events/jobs/JOB-01JH9F8P2ZJ1A8E5R6C792Q2EQ/pattern_events.jsonl
```

### Pattern Run Storage

Pattern run objects **SHOULD** be stored in:

1. **State DB** (`core/state/db.py`) in `pattern_runs` table
2. **JSONL archive** at `state/pattern_runs/{YYYY-MM}/{PRUN-...}.jsonl`

### Integration with Existing State Store

Leverage `engine/state_store/job_state_store.py`:

```python
# Extend JobStateStore to include pattern runs
class JobStateStore:
    def record_pattern_event(self, event: PatternEvent):
        """Write event to JSONL and update pattern_run in memory."""
        pass
    
    def get_pattern_events(self, job_id: str) -> List[PatternEvent]:
        """Retrieve all pattern events for a job."""
        pass
    
    def get_pattern_run(self, pattern_run_id: str) -> PatternRun:
        """Retrieve full pattern run object."""
        pass
```

## GUI Integration

### API Endpoints

Expose these endpoints for the Pattern Activity Panel:

```python
# GET /api/jobs/{job_id}/pattern-events
# Returns: List[PatternEvent] sorted by timestamp

# GET /api/jobs/{job_id}/pattern-runs
# Returns: List[PatternRun] with summary data

# GET /api/pattern-runs/{pattern_run_id}
# Returns: Full PatternRun object with artifacts

# GET /api/pattern-runs/{pattern_run_id}/logs
# Returns: Raw stdout/stderr from execution
```

### WebSocket Events (Optional)

For real-time GUI updates:

```javascript
// Subscribe to pattern events for a job
socket.emit('subscribe:pattern-events', { job_id: 'JOB-...' });

// Receive events
socket.on('pattern.event', (event) => {
  // Update timeline UI
});
```

## Validation

### Event Validation

All events **MUST** pass JSON schema validation before persistence:

```bash
# Validate against schema
python -m core.validation validate-pattern-event < event.json
```

### Pattern Run Validation

Pattern runs **MUST**:

1. Have exactly one `pattern.execution.started` event
2. Have exactly one terminal event (`completed` or `failed`)
3. Have sequential timestamps
4. Reference a valid `pattern_id` in UET pattern registry

## CLI Tools

### Inspection Commands

```bash
# View pattern events for a job
python -m engine.inspect pattern-events --job-id JOB-...

# View pattern run details
python -m engine.inspect pattern-run --pattern-run-id PRUN-...

# Tail live pattern events
python -m engine.inspect pattern-events --follow
```

### Example Output

```
JOB-01JH9F8P2ZJ1A8E5R6C792Q2EQ Pattern Activity
─────────────────────────────────────────────────────
[07:15:12] PAT-SEMGRP-001 selection.resolved → step STEP-003
[07:15:13] PAT-SEMGRP-001 template.expanded  → 2 targets, 3 artifacts
[07:15:13] PAT-SEMGRP-001 validation.completed → 3 checks passed
[07:15:14] PAT-SEMGRP-001 execution.started  → semgrep --config auto ...
[07:15:30] PAT-SEMGRP-001 execution.completed → success (12 findings, 18.7s)

Artifacts:
  - state/reports/semgrep/.../semgrep_report.json
  - state/reports/semgrep/.../semgrep_summary.html
```

## Implementation Roadmap

### Phase 1: Core Event Emission (Week 1)

- [ ] Create `core/engine/pattern_events.py` with `emit_pattern_event()`
- [ ] Add event schema validation
- [ ] Wire into existing pattern execution points in `engine/`
- [ ] Write events to JSONL

### Phase 2: Pattern Run Aggregation (Week 1)

- [ ] Extend `JobStateStore` with pattern run methods
- [ ] Aggregate events into `PatternRun` objects
- [ ] Store in state DB

### Phase 3: CLI Inspection (Week 2)

- [ ] Implement `engine.inspect pattern-events` command
- [ ] Implement `engine.inspect pattern-run` command
- [ ] Add `--follow` mode for live tailing

### Phase 4: GUI Integration (Week 3-4)

- [ ] Add API endpoints to engine service
- [ ] Build Pattern Activity Panel component
- [ ] Wire WebSocket events (optional)

## References

- **Existing Telemetry**: `core/state/pattern_telemetry_db.py`
- **UET Schemas**: `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/schema/pattern_execution_result.v1.json`
- **Job State Store**: `engine/state_store/job_state_store.py`
- **Engine Docs**: `engine/README.md`, `docs/ENGINE_IMPLEMENTATION_SUMMARY.md`

## Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-26 | Initial specification |
