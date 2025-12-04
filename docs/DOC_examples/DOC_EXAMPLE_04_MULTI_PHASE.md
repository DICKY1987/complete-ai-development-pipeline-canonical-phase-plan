---
status: draft
doc_type: guide
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-EXAMPLE_MULTI_PHASE-067
---

# Example 04: Multi-Phase Workflow - Data Pipeline

**Pattern**: Multi-phase with checkpointing and state transitions
**Complexity**: Advanced
**Estimated Duration**: 10-15 minutes
**Tool**: Aider with state management

---

## Purpose

This example demonstrates **complex multi-phase workflows** with checkpointing and resume capability. Use this pattern when you need to:

- Build long-running processes that can be paused/resumed
- Implement staged deployments or migrations
- Create fault-tolerant data pipelines
- Track progress through multiple distinct phases
- Save intermediate state for audit/recovery

---

## What This Example Demonstrates

✅ **Phase Management**
- Sequential phase execution
- Phase dependencies
- Per-phase checkpoints

✅ **State Machine**
- Formal state transitions
- Pause/resume capability
- Error state handling

✅ **Checkpointing**
- Automatic state saving
- Resume from last checkpoint
- Incremental progress tracking

---

## Architecture: Multi-Phase Execution

### Phase Flow

```
┌──────────────────┐
│  Phase 1: Setup  │
│  - Create modules│
│  - Validate env  │
└────────┬─────────┘
         │ Checkpoint saved
         ▼
┌──────────────────┐
│ Phase 2: Process │
│  - Validate data │
│  - Transform     │
└────────┬─────────┘
         │ Checkpoint saved
         ▼
┌──────────────────┐
│Phase 3: Reporting│
│  - Generate stats│
│  - Export results│
└────────┬─────────┘
         │ Checkpoint saved
         ▼
    ┌─────────┐
    │Complete │
    └─────────┘
```

### State Machine

```
         start
           │
           ▼
    ┌──────────┐
    │ Pending  │
    └─────┬────┘
          │
          ▼
 ┌─────────────────┐
 │ Phase 1 Running │
 └─────┬───────────┘
       │ success
       ▼
 ┌─────────────────┐
 │Phase 1 Complete │◄──┐
 └─────┬───────────┘   │ resume
       │               │
       ▼          ┌────┴────┐
 ┌─────────────────┐   │ Paused  │
 │ Phase 2 Running │   └─────────┘
 └─────┬───────────┘        ▲
       │ success            │ pause
       ▼                    │
 ┌─────────────────┐        │
 │Phase 2 Complete │────────┘
 └─────┬───────────┘
       │
       ▼
 ┌─────────────────┐
 │ Phase 3 Running │
 └─────┬───────────┘
       │ success
       ▼
   ┌──────────┐
   │Completed │
   └──────────┘

   error (any state)
         │
         ▼
    ┌────────┐
    │ Failed │
    └────────┘
```

---

## Checkpoint System

### What Gets Saved

Each checkpoint includes:

```json
{
  "checkpoint_id": "phase-02-20231122-1430",
  "timestamp": "2023-11-22T14:30:15Z",
  "phase": "phase-02-processing",
  "step": "step-02-create-validator",
  "state": "phase_02_running",

  "completed_phases": ["phase-01-setup"],
  "completed_steps": [
    "step-01-create-processor"
  ],

  "file_changes": [
    {
      "file": "examples/data_processor.py",
      "hash": "a1b2c3d4...",
      "status": "created"
    }
  ],

  "metrics": {
    "duration_so_far": 342,
    "steps_completed": 1,
    "steps_total": 3
  },

  "metadata": {
    "retry_count": 0,
    "last_error": null
  }
}
```

### When Checkpoints Are Created

1. **After each phase completes** (automatic)
2. **Every N seconds during long phases** (interval-based)
3. **Before risky operations** (manual triggers)
4. **After successful recovery** (post-retry)

---

## Resume Scenarios

### Scenario 1: Resume After Pause

```bash
# Start workflow
$ python scripts/run_workstream.py --ws-id ws-example-04-multi-phase

[INFO] Phase 1: Running...
[INFO] Phase 1: Complete ✓ (checkpoint saved)
[INFO] Phase 2: Running...

# User pauses (Ctrl+C or explicit pause)
^C
[INFO] Pausing workstream...
[INFO] Saving checkpoint: phase-02 (step in progress)
[INFO] Workstream paused

# Later, resume
$ python scripts/run_workstream.py --ws-id ws-example-04-multi-phase --resume

[INFO] Resuming from checkpoint: phase-02-20231122-1430
[INFO] Validating state... ✓
[INFO] Checking file integrity... ✓
[INFO] Phase 1: Skipped (already complete)
[INFO] Phase 2: Resuming from step-02...
[INFO] Phase 2: Complete ✓
[INFO] Phase 3: Running...
[INFO] Phase 3: Complete ✓
✓ Workstream complete
```

---

### Scenario 2: Resume After Failure

```bash
$ python scripts/run_workstream.py --ws-id ws-example-04-multi-phase

[INFO] Phase 1: Complete ✓
[INFO] Phase 2: Running...
[ERROR] Phase 2: Failed (network timeout)
[INFO] Checkpoint saved: phase-02 (failed state)
✗ Workstream failed

# Fix the issue (e.g., restore network)
# Then resume
$ python scripts/run_workstream.py --ws-id ws-example-04-multi-phase --resume

[INFO] Resuming from checkpoint: phase-02-20231122-1430
[INFO] Retry attempt 1/2 for Phase 2
[INFO] Phase 2: Complete ✓
[INFO] Phase 3: Running...
[INFO] Phase 3: Complete ✓
✓ Workstream complete
```

---

### Scenario 3: Resume from Specific Phase

```bash
# Skip to Phase 3 (for debugging)
$ python scripts/run_workstream.py \
    --ws-id ws-example-04-multi-phase \
    --resume-from phase-03-reporting \
    --assume-previous-complete

[WARN] Skipping phases 1-2 (assumed complete)
[INFO] Phase 3: Running...
[INFO] Phase 3: Complete ✓
✓ Workstream complete (partial run)
```

---

## Configuration Deep Dive

### Phase Definition

```json
{
  "phases": [
    {
      "id": "phase-01-setup",
      "name": "Setup and Validation",
      "description": "Prepare environment",

      "steps": [...],

      "checkpoint": {
        "enabled": true,
        "strategy": "automatic",
        "location": ".checkpoints/phase-01.json",
        "include": ["step_status", "file_changes", "metadata"]
      }
    }
  ]
}
```

**Key options**:
- `checkpoint.enabled`: Turn on/off checkpoint saving
- `checkpoint.strategy`: `automatic` (after phase) or `manual` (explicit)
- `checkpoint.include`: What data to save

---

### Resume Configuration

```json
{
  "resume": {
    "enabled": true,
    "strategy": "from_last_checkpoint",

    "on_resume": {
      "validate_state": true,
      "check_file_changes": true,
      "verify_dependencies": true
    },

    "cleanup_on_complete": false
  }
}
```

**Validation on resume**:
- `validate_state`: Ensure state machine is consistent
- `check_file_changes`: Verify files haven't changed externally
- `verify_dependencies`: Check all dependencies still met

---

## Execution Examples

### Full Execution (No Issues)

```
$ python scripts/run_workstream.py --ws-id ws-example-04-multi-phase

[INFO] Starting workstream: ws-example-04-multi-phase
[INFO] State: pending → phase_01_running

=== Phase 1: Setup and Validation ===
[INFO] Step 1/1: Create data processor
[INFO] Executing with Aider...
✓ examples/data_processor.py created
✓ Acceptance tests passed
[INFO] Checkpoint saved: .checkpoints/phase-01.json
[INFO] State: phase_01_running → phase_01_complete

=== Phase 2: Data Processing ===
[INFO] Step 1/1: Create data validator
[INFO] Executing with Aider...
✓ examples/data_validator.py created
✓ Acceptance tests passed
[INFO] Checkpoint saved: .checkpoints/phase-02.json
[INFO] State: phase_02_running → phase_02_complete

=== Phase 3: Generate Reports ===
[INFO] Step 1/1: Create reporting module
[INFO] Executing with Aider...
✓ examples/data_reporter.py created
✓ Acceptance tests passed
[INFO] Checkpoint saved: .checkpoints/phase-03.json
[INFO] State: phase_03_running → completed

✓ Workstream complete in 12m 34s

Summary:
- Phases: 3/3 complete
- Steps: 3/3 complete
- Checkpoints: 3 saved
- Total duration: 12m 34s
- Resumable: yes (checkpoints retained for 7 days)
```

---

## Checkpoint Management

### List Checkpoints

```bash
$ python scripts/list_checkpoints.py ws-example-04-multi-phase

Checkpoints for ws-example-04-multi-phase:

1. phase-01.json (2023-11-22 14:25:10)
   Phase: Setup and Validation
   State: phase_01_complete
   Duration: 3m 42s

2. phase-02.json (2023-11-22 14:30:15)
   Phase: Data Processing
   State: phase_02_complete
   Duration: 5m 05s

3. phase-03.json (2023-11-22 14:34:28)
   Phase: Generate Reports
   State: completed
   Duration: 4m 13s

Total: 3 checkpoints, 12m 34s elapsed
```

---

### Inspect Checkpoint

```bash
$ python scripts/inspect_checkpoint.py \
    .worktrees/ws-example-04-multi-phase/.checkpoints/phase-02.json

Checkpoint Details:
==================
ID: phase-02-20231122-1430
Timestamp: 2023-11-22T14:30:15Z
Phase: phase-02-processing
State: phase_02_complete

Completed:
- phase-01-setup ✓
- step-01-create-processor ✓
- step-02-create-validator ✓

Files Changed:
- examples/data_processor.py (created, 2.3KB)
- examples/data_validator.py (created, 1.8KB)

Metrics:
- Duration: 8m 47s
- Steps completed: 2/3
- Retries: 0

Can resume from: step-03-create-reporter
```

---

## Troubleshooting

### Issue: "Checkpoint validation failed"

**Cause**: Files changed externally since checkpoint
**Fix**: Review changes and either:
```bash
# Accept changes and continue
python scripts/run_workstream.py --ws-id <id> --resume --force

# Or reset to checkpoint state
python scripts/reset_to_checkpoint.py <id> phase-02.json
```

---

### Issue: "Cannot resume - state mismatch"

**Cause**: State machine in unexpected state
**Fix**:
```bash
# Check current state
python scripts/check_state.py ws-example-04-multi-phase

# Reset state machine
python scripts/reset_state.py ws-example-04-multi-phase --to phase_02_complete
```

---

### Issue: "Checkpoint not found"

**Cause**: Checkpoints expired or manually deleted
**Fix**: Start from beginning
```bash
python scripts/run_workstream.py --ws-id <id> --fresh-start
```

---

## Best Practices

### ✅ When to Use Multi-Phase Workflows

**Good candidates**:
- Data ETL pipelines (extract → transform → load)
- Deployment workflows (build → test → deploy → verify)
- Migration processes (backup → migrate → validate → cleanup)
- Long-running analysis (collect → process → analyze → report)

**Not recommended for**:
- Simple single-file changes
- Quick refactoring tasks
- Workflows that complete in <1 minute

---

### ⚠️ Common Pitfalls

1. **Too many phases** → Overhead exceeds benefit
   - **Fix**: Combine related operations into single phase

2. **Forgetting to save checkpoints** → Can't resume
   - **Fix**: Use `automatic` checkpoint strategy

3. **Large checkpoint files** → Slow I/O
   - **Fix**: Only save essential state, not full data

4. **Not validating on resume** → Inconsistent state
   - **Fix**: Enable all validation checks

---

## Learning Points

**Multi-phase workflows provide**:
- Resumability after failures
- Progress visibility
- Natural breakpoints for testing
- Audit trail of execution

**Checkpoints enable**:
- Incremental progress
- Fault tolerance
- State recovery
- Debugging capabilities

**State machines ensure**:
- Consistent transitions
- Clear current status
- Predictable behavior
- Error handling

---

## Next Steps

- **Example 05**: SAGA Pattern - Compensation and rollback

---

**Last Updated**: 2025-11-22
**Difficulty**: ⭐⭐⭐ Advanced
**Execution Time**: 10-15 minutes
**Success Rate**: ~80% (complexity increases failure chance, but resume helps)
