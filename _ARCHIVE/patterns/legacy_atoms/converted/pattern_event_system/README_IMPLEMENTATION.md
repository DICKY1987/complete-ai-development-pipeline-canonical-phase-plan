---
doc_id: DOC-PAT-README-IMPLEMENTATION-813
---

# Pattern Event System - Implementation Task

**Created**: 2025-11-26
**Status**: Ready for Implementation
**Priority**: Medium
**Estimated Time**: 1-2 weeks

## 📋 Overview

Complete pattern execution tracking system for Universal Execution Templates (UET). Enables observable pattern lifecycle with GUI visualization support.

## 🎯 What This Delivers

**Automated Pattern Task Tracking:**
- Pattern selection & resolution
- Template expansion (variable substitution)
- Pre-flight validation
- Tool execution & result capture
- Artifact generation

**Visual Integration:**
- Pattern Activity Panel (timeline + summary)
- Real-time event streaming
- Pattern run details viewer
- CLI inspection tools

## 📦 Deliverables (9 Files)

### Documentation (4 files)
1. **`PATTERN_EVENT_SPEC.md`** (60KB)
   - Complete specification with 10 event types
   - PatternRun aggregation model
   - Storage & persistence guidelines
   - MUST/SHOULD field requirements

2. **`PATTERN_EVENT_INTEGRATION.md`** (12KB)
   - 3-step integration guide (5-15 minutes)
   - Code examples for engine integration
   - GUI API endpoint specs (Flask/FastAPI)
   - React component example
   - Best practices & troubleshooting

3. **`PATTERN_EVENT_DELIVERY_SUMMARY.md`** (9KB)
   - Validation results
   - Architecture fit analysis
   - Performance impact
   - Next steps roadmap

4. **`PATTERN_EVENTS_QUICK_REFERENCE.md`** (5KB)
   - Copy-paste code snippets
   - Event type table
   - CLI commands
   - Troubleshooting guide

### Schemas (2 files)
5. **`pattern_event.v1.json`** (6KB)
   - JSON schema for events
   - Type-specific detail validation
   - ULID pattern enforcement

6. **`pattern_run.v1.json`** (3KB)
   - JSON schema for pattern runs
   - Aggregated execution records

### Implementation (3 files)
7. **`pattern_events.py`** (12KB)
   - `PatternEvent` dataclass
   - `PatternRun` dataclass
   - `PatternEventEmitter` (JSONL persistence)
   - `PatternRunAggregator` (event aggregation)
   - `emit_pattern_event()` convenience function

8. **`pattern_inspect.py`** (7KB)
   - CLI tool for event inspection
   - `pattern_inspect events` - View timeline
   - `pattern_inspect run <PRUN-...>` - View details
   - `--follow` mode for real-time tailing
   - Color-coded status display

9. **`pattern_events_example.py`** (7KB)
   - Working demonstration
   - Full lifecycle simulation (7 events)
   - Validated with live execution ✅

## ⚡ Quick Start (5 minutes)

### Step 1: Install files
```powershell
# Copy implementation files to repository
Copy-Item "pattern_events.py" -Destination "..\..\..\core\engine\"
Copy-Item "pattern_inspect.py" -Destination "..\..\..\core\engine\"
Copy-Item "pattern_events_example.py" -Destination "..\..\..\examples\"

# Copy schemas
Copy-Item "pattern_event.v1.json" -Destination "..\..\..\schema\"
Copy-Item "pattern_run.v1.json" -Destination "..\..\..\schema\"

# Copy documentation
Copy-Item "PATTERN_EVENT_*.md" -Destination "..\..\..\docs\"
```

### Step 2: Add event emission to your pattern executor
```python
from core.engine.pattern_events import emit_pattern_event

# In your pattern execution code
emit_pattern_event(
    event_type="pattern.execution.started",
    job_id=job.id,
    pattern_run_id=pattern_run.id,
    pattern_id="PAT-SEMGRP-001",
    status="in_progress",
    details={"command": "semgrep ..."},
)

# ... run tool ...

emit_pattern_event(
    event_type="pattern.execution.completed",
    job_id=job.id,
    pattern_run_id=pattern_run.id,
    pattern_id="PAT-SEMGRP-001",
    status="success",
    details={
        "exit_code": 0,
        "duration_seconds": 18.7,
        "result_summary": {"finding_count": 12},
    },
)
```

### Step 3: Test
```bash
# Run example
python examples/pattern_events_example.py

# View events
python -m core.engine.pattern_inspect events

# View pattern run
python -m core.engine.pattern_inspect run PRUN-...
```

## 🗺️ Implementation Roadmap

### Phase 1: Core Event Emission (Week 1)
**Time**: 1 day
**Priority**: High

- [x] Files created and validated
- [ ] Copy files to repository locations
- [ ] Add `emit_pattern_event()` calls to pattern executor
- [ ] Test with example and CLI
- [ ] Verify events written to `state/events/pattern_events.jsonl`

**Success Criteria**: Events appear in CLI inspector

### Phase 2: State Store Integration (Week 1)
**Time**: 2-3 hours
**Priority**: Medium

- [ ] Extend `engine/state_store/job_state_store.py` with pattern event methods:
  - `get_pattern_events(job_id)`
  - `get_pattern_runs(job_id)`
  - `get_pattern_run(pattern_run_id)`
- [ ] Add pattern run storage to state DB
- [ ] Write tests for state store methods

**Success Criteria**: Pattern runs queryable via JobStateStore API

### Phase 3: GUI Integration (Week 2)
**Time**: 3-4 days
**Priority**: Medium

- [ ] Add API endpoints (see `PATTERN_EVENT_INTEGRATION.md` § GUI Integration):
  - `GET /api/jobs/{job_id}/pattern-events`
  - `GET /api/jobs/{job_id}/pattern-runs`
  - `GET /api/pattern-runs/{pattern_run_id}`
  - `GET /api/pattern-runs/{pattern_run_id}/logs`
- [ ] Build Pattern Activity Panel component (React)
  - Summary table (patterns used per job)
  - Timeline view (chronological events)
  - Detail drawer (pattern run details)
- [ ] Wire into Job Detail view

**Success Criteria**: GUI displays pattern activity for any job

### Phase 4: Real-time Updates (Optional)
**Time**: 1 day
**Priority**: Low

- [ ] Add WebSocket event stream
- [ ] Update GUI to subscribe to pattern events
- [ ] Implement live timeline updates

**Success Criteria**: GUI updates in real-time as patterns execute

## 📊 Event Types Reference

| Event Type | When | Required Details |
|------------|------|------------------|
| `pattern.selection.started` | Pattern resolution begins | `operation_kind`, `candidate_patterns` |
| `pattern.selection.resolved` | Pattern selected | `pattern_id`, `selection_method`, `inputs_preview` |
| `pattern.selection.failed` | No suitable pattern | `reason`, `attempted_patterns` |
| `pattern.template.expanded` | Variables substituted | `variables_resolved`, `generated_artifacts` |
| `pattern.validation.started` | Pre-flight checks begin | `validation_type`, `checks` |
| `pattern.validation.completed` | Validation passed | `checks_passed`, `checks_failed` |
| `pattern.validation.failed` | Validation failed | `failed_checks` with errors |
| `pattern.execution.started` | Tool invocation begins | `executor`, `command` |
| `pattern.execution.completed` | Execution succeeded | `exit_code`, `duration_seconds`, `result_summary`, `artifacts` |
| `pattern.execution.failed` | Execution failed | `exit_code`, `error_type`, `error_message` |

**Minimum required**: `pattern.execution.started` + (`pattern.execution.completed` OR `pattern.execution.failed`)

## 🏗️ Architecture

```
Pattern Executor          Pattern Event System         Storage
────────────────          ────────────────────         ───────
engine/orchestrator  ──→  emit_pattern_event()   ──→  state/events/*.jsonl
engine/pattern_executor   PatternRunAggregator   ──→  engine/state_store (DB)
UNIVERSAL_EXECUTION_
  TEMPLATES_FRAMEWORK/
  patterns/

GUI (Phase 3)        ←──  GET /api/pattern-events ←──  JSONL + DB
```

### Integration Points

**Existing Infrastructure Used:**
- ✅ `engine/state_store/job_state_store.py` - Extend for pattern events
- ✅ UET pattern specs - Referenced via `pattern_id`
- ✅ Job-based execution model - Events scoped to jobs
- ✅ ULID identifier system - `EVT-*`, `PRUN-*` prefixes
- ✅ JSONL event logging - Matches error pipeline pattern

**No Changes Required:**
- ✅ UET framework core
- ✅ Existing schemas
- ✅ Engine orchestrator (just add emission calls)

## ✅ Validation Checklist

### Pre-Implementation
- [x] All files created
- [x] Example runs successfully
- [x] CLI inspector works
- [x] Events validate against schemas

### Post-Implementation (Phase 1)
- [ ] Events emitted from pattern executor
- [ ] Events visible in CLI inspector
- [ ] Pattern runs aggregate correctly
- [ ] JSONL files created in `state/events/`

### Post-Implementation (Phase 2)
- [ ] JobStateStore methods work
- [ ] Pattern runs queryable by job ID
- [ ] State DB contains pattern run records

### Post-Implementation (Phase 3)
- [ ] API endpoints respond correctly
- [ ] GUI Panel displays pattern activity
- [ ] Timeline updates on job execution
- [ ] Detail drawer shows full pattern run

## 📁 File Installation Map

```
Source                           Destination
──────                           ───────────
pattern_events.py           →    core/engine/pattern_events.py
pattern_inspect.py          →    core/engine/pattern_inspect.py
pattern_events_example.py   →    examples/pattern_events_example.py

pattern_event.v1.json       →    schema/pattern_event.v1.json
pattern_run.v1.json         →    schema/pattern_run.v1.json

PATTERN_EVENT_SPEC.md       →    docs/PATTERN_EVENT_SPEC.md
PATTERN_EVENT_INTEGRATION.md →   docs/PATTERN_EVENT_INTEGRATION.md
PATTERN_EVENT_DELIVERY_SUMMARY.md → docs/PATTERN_EVENT_DELIVERY_SUMMARY.md
PATTERN_EVENTS_QUICK_REFERENCE.md → docs/PATTERN_EVENTS_QUICK_REFERENCE.md
```

## 🧪 Testing

### Manual Testing
```bash
# 1. Run example
python examples/pattern_events_example.py

# Expected: 7 events emitted, pattern run aggregated

# 2. View events
python -m core.engine.pattern_inspect events

# Expected: Timeline with color-coded events

# 3. View pattern run
python -m core.engine.pattern_inspect run <PRUN-from-example>

# Expected: Full pattern run details with inputs/outputs/artifacts
```

### Unit Tests (To Write)
- [ ] Test `PatternEvent.create()`
- [ ] Test `PatternRun.create()` and lifecycle methods
- [ ] Test `PatternEventEmitter.emit()` and `get_events()`
- [ ] Test `PatternRunAggregator.handle_event()` and `rebuild_from_events()`
- [ ] Test event schema validation
- [ ] Test pattern run schema validation

### Integration Tests (To Write)
- [ ] Test end-to-end pattern execution with events
- [ ] Test JobStateStore pattern event methods
- [ ] Test API endpoints
- [ ] Test GUI component rendering

## 🐛 Known Issues / Considerations

### ULID Library
- Implementation uses `ulid` package with fallback
- Fallback generates ULID-like IDs (timestamp + random)
- Consider: `pip install python-ulid` for production

### Storage
- JSONL files grow unbounded
- Consider: Log rotation or archival after N days
- Pattern run DB table not created yet (Phase 2)

### Performance
- Event emission: < 1ms (append to file)
- No impact on pattern execution performance
- Aggregation is on-demand (read from JSONL)

## 📚 Documentation Reading Order

1. **Start here**: `PATTERN_EVENTS_QUICK_REFERENCE.md` (5 min)
2. **For integration**: `PATTERN_EVENT_INTEGRATION.md` (15 min)
3. **For details**: `PATTERN_EVENT_SPEC.md` (30 min)
4. **For overview**: `PATTERN_EVENT_DELIVERY_SUMMARY.md` (10 min)

## 🔗 Related Systems

**Builds on:**
- UET Framework (`UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/`)
- Engine Architecture (`engine/`, `core/engine/`)
- State Management (`core/state/`, `engine/state_store/`)
- Existing telemetry (`core/state/pattern_telemetry_db.py`)

**Complements:**
- Error Pipeline (`error/engine/`, `error/plugins/`)
- Job-based execution (`engine/orchestrator/`)
- GUI Development (Phase 3 roadmap)

## 💡 Tips

1. **Start minimal**: Just add `started` and `completed` events first
2. **Use the example**: Copy patterns from `pattern_events_example.py`
3. **Test incrementally**: Run CLI inspector after each change
4. **Follow the spec**: Required details are documented per event type
5. **Check the logs**: `tail -f state/events/pattern_events.jsonl`

## 🎯 Success Metrics

**Phase 1 Complete When:**
- ✅ Events appear in CLI inspector
- ✅ Pattern runs aggregate with correct inputs/outputs
- ✅ JSONL files contain valid events

**Phase 2 Complete When:**
- ✅ JobStateStore methods return pattern data
- ✅ State DB contains pattern run records
- ✅ API can query pattern history

**Phase 3 Complete When:**
- ✅ GUI displays pattern activity panel
- ✅ Timeline shows events in chronological order
- ✅ Users can view pattern run details

## 📞 Questions?

**Reference Documentation:**
- Event types: `PATTERN_EVENT_SPEC.md` § Event Type Definitions
- Integration steps: `PATTERN_EVENT_INTEGRATION.md` § Step 1-3
- Code examples: `pattern_events_example.py`
- CLI usage: `PATTERN_EVENTS_QUICK_REFERENCE.md` § CLI Commands

---

**Status**: Ready for implementation
**Next Action**: Copy files and begin Phase 1
**Contact**: See delivery summary for architecture questions
