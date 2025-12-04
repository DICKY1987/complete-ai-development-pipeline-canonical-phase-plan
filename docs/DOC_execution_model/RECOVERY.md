---
doc_id: DOC-GUIDE-RECOVERY-784
---

# Recovery Procedures

## Purpose
This document describes checkpoint/rollback mechanisms, recovery from partial workstream failures, and manual intervention procedures.

## Overview

The orchestration system provides multiple levels of recovery:

1. **Automatic Recovery**: System-handled retries and reassignments
2. **Semi-Automatic Recovery**: User-triggered recovery scripts
3. **Manual Recovery**: Human investigation and intervention

---

## Checkpoint Mechanisms

### Task-Level Checkpoints

Tasks do not checkpoint mid-execution. Each task is atomic - either fully succeeds or fully fails.

**Rationale**: Tasks are designed to be small, focused units of work (typically < 10 minutes). Checkpointing within tasks adds complexity without significant benefit.

### Workstream-Level Checkpoints

Workstream state is checkpointed after each task transition:

```json
{
  "workstream_id": "ws-ulid-001",
  "checkpoint_at": "2024-01-15T10:30:00.000Z",
  "completed_tasks": ["task-001", "task-002"],
  "failed_tasks": [],
  "pending_tasks": ["task-003", "task-004"],
  "resources_held": {
    "git_repo_write": "task-003"
  }
}
```

**Location**: `.state/checkpoints/{workstream_id}_latest.json`

**Frequency**: After every task state transition

### State File Checkpoints

`.state/current.json` is backed up before each update:

```bash
.state/backups/
├── current_2024-01-15T10-00-00.json
├── current_2024-01-15T10-15-00.json
└── current_2024-01-15T10-30-00.json
```

**Retention**: Last 100 checkpoints (approximately 1-2 hours of history)

---

## Rollback Mechanisms

### Task Rollback

Individual tasks cannot be rolled back. If a task fails:

1. **Automatic Retry**: Task retried if retry_count < max_retries
2. **Manual Restart**: User can reset task to `pending` state
3. **Skip Task**: User can mark task as `completed` (with warning)

### Workstream Rollback

Workstream can be rolled back to last checkpoint:

```bash
python scripts/rollback_workstream.py --workstream-id ws-ulid-001 --to-checkpoint latest
```

**Actions**:
1. Load checkpoint state
2. Cancel all `running` tasks
3. Reset `queued` tasks to `pending`
4. Restore task states from checkpoint
5. Release all held resources
6. Emit rollback event

**Limitations**:
- Cannot rollback completed tasks (changes already applied)
- Cannot rollback merged workstreams
- Rollback to checkpoint, not arbitrary timestamps

### State File Rollback

If `.state/current.json` becomes corrupted:

```bash
python scripts/restore_state.py --from-backup latest
# or
python scripts/restore_state.py --from-transitions .state/transitions.jsonl
```

**Recovery Methods**:

1. **From Backup**: Restore from `.state/backups/`
   - Fast (< 1 second)
   - May lose up to 60 seconds of updates

2. **From Transitions Log**: Replay `.state/transitions.jsonl`
   - Slower (10-60 seconds depending on log size)
   - Complete accuracy, no data loss

---

## Failure Recovery Procedures

### Task Timeout Recovery

**Detection**:
```json
{"event": "task_timeout", "task_id": "task-001", "severity": "warning"}
```

**Automatic Recovery**:
1. Kill task process
2. Release worker
3. Increment retry_count
4. If retry_count < max_retries:
   - Schedule retry with exponential backoff (2^retry_count seconds)
5. Else:
   - Mark task as `failed`
   - Emit failure event with severity="error"

**Manual Intervention** (if retries exhausted):
```bash
# Investigate logs
cat .state/logs/task-001.log

# Check worker health
python scripts/check_worker.py --worker-id worker-001

# Options:
# 1. Increase timeout and retry
python scripts/retry_task.py --task-id task-001 --timeout 1200

# 2. Skip task (with confirmation)
python scripts/skip_task.py --task-id task-001 --reason "Timeout not indicative of failure"

# 3. Debug and fix underlying issue
python scripts/debug_task.py --task-id task-001 --interactive
```

### Task Failure Recovery

**Detection**:
```json
{"event": "task_failed", "task_id": "task-002", "severity": "error"}
```

**Automatic Recovery**:
1. If retry_count < max_retries: Retry (same as timeout)
2. Else: Mark as permanently failed

**Manual Intervention**:
```bash
# View failure details
python scripts/show_task.py --task-id task-002 --include-logs

# Common failure types and fixes:

# Validation failure → Fix validation issue, retry
python scripts/fix_validation.py --task-id task-002
python scripts/retry_task.py --task-id task-002

# Dependency failure → Check dependency state
python scripts/show_dependencies.py --task-id task-002

# Worker failure → Check worker logs
python scripts/show_worker_logs.py --worker-id worker-001
```

### Worker Unresponsive Recovery

**Detection**:
```json
{"event": "worker_unresponsive", "worker_id": "worker-001", "severity": "error"}
```

**Automatic Recovery**:
1. Wait for health check recovery (30 seconds)
2. If recovered:
   - Return worker to `idle` pool
   - Continue normally
3. If not recovered after 3 minutes:
   - Mark worker as `shutdown`
   - Reassign tasks to other workers

**Manual Intervention**:
```bash
# Check worker status
python scripts/check_worker.py --worker-id worker-001

# Restart worker
python scripts/restart_worker.py --worker-id worker-001

# Force shutdown and reassign tasks
python scripts/force_shutdown_worker.py --worker-id worker-001 --reassign
```

### Resource Exhaustion Recovery

**Detection**:
```json
{"event": "resource_exhausted", "resource_id": "git_repo_write", "severity": "critical"}
```

**Automatic Recovery**:
- Tasks requiring resource wait in `queued` state
- System does NOT automatically increase resource limits

**Manual Intervention**:
```bash
# View resource usage
python scripts/show_resources.py

# Options:
# 1. Wait for resource to be released (if temporary)
# 2. Increase resource limit (if permanent)
python scripts/set_resource_limit.py --resource-id git_repo_write --max-holders 2

# 3. Cancel tasks holding resources
python scripts/cancel_task.py --task-id task-holding-resource
```

### Dependency Cycle Detection

**Detection**:
```json
{"event": "dependency_cycle_detected", "tasks": ["task-001", "task-002"], "severity": "critical"}
```

**Automatic Recovery**:
- No automatic recovery (cycle must be manually broken)

**Manual Intervention**:
```bash
# View dependency graph
python scripts/visualize_dag.py --workstream-id ws-ulid-001

# Break cycle by removing dependency
python scripts/remove_dependency.py --from task-001 --to task-002

# Or cancel one task in cycle
python scripts/cancel_task.py --task-id task-001
```

### Workstream Failure Recovery

**Detection**:
```json
{"event": "workstream_failed", "workstream_id": "ws-ulid-001", "severity": "critical"}
```

**Automatic Recovery**:
- Workstream state preserved in `.state/archive/`
- No automatic retry (workstream failures require investigation)

**Manual Intervention**:
```bash
# Analyze failure
python scripts/analyze_workstream_failure.py --workstream-id ws-ulid-001

# Options:
# 1. Retry entire workstream
python scripts/retry_workstream.py --workstream-id ws-ulid-001

# 2. Retry only failed tasks
python scripts/retry_failed_tasks.py --workstream-id ws-ulid-001

# 3. Manual fix and resume
python scripts/resume_workstream.py --workstream-id ws-ulid-001 --from-task task-005
```

---

## Recovery Decision Trees

### Task Recovery Decision Tree

```
Task Failed
├─ Retry count < max_retries?
│  ├─ Yes → Automatic retry with backoff
│  └─ No → Manual investigation required
│     ├─ Transient failure? (timeout, network)
│     │  └─ Increase timeout/retries, retry task
│     ├─ Code issue? (validation, tests)
│     │  └─ Fix code, retry task
│     ├─ Dependency issue?
│     │  └─ Fix dependency, retry task
│     └─ Task definition issue?
│        └─ Update task definition, retry
```

### Workstream Recovery Decision Tree

```
Workstream Failed
├─ All tasks failed?
│  ├─ Yes → Systemic issue
│  │  ├─ Worker problems? → Investigate workers
│  │  ├─ Resource problems? → Check resources
│  │  └─ Configuration issue? → Review config
│  └─ No → Partial failure
│     ├─ Critical task failed?
│     │  └─ Fix critical task, retry workstream
│     └─ Non-critical task failed?
│        └─ Retry failed tasks only
```

### Worker Recovery Decision Tree

```
Worker Unresponsive
├─ Wait 30 seconds
├─ Worker recovered?
│  ├─ Yes → Resume normal operation
│  └─ No → Wait 3 minutes
│     ├─ Worker recovered?
│     │  ├─ Yes → Resume, monitor closely
│     │  └─ No → Force shutdown
│     │     ├─ Restart worker
│     │     └─ Reassign tasks
```

---

## Manual Intervention Triggers

### When to Intervene Manually

1. **Task failed after max_retries**
   - Severity: Error
   - Urgency: Medium (workstream blocked)
   - Action: Investigate failure reason

2. **Worker unresponsive > 3 minutes**
   - Severity: Error
   - Urgency: High (tasks blocked)
   - Action: Restart worker or reassign tasks

3. **Workstream failed**
   - Severity: Critical
   - Urgency: High (deliverable blocked)
   - Action: Analyze root cause, plan recovery

4. **Resource exhaustion**
   - Severity: Critical
   - Urgency: High (system stalled)
   - Action: Increase limits or cancel tasks

5. **Dependency cycle**
   - Severity: Critical
   - Urgency: High (workstream cannot proceed)
   - Action: Break cycle

### Escalation Paths

**Level 1: Automatic** (No human intervention)
- Task retries (< max_retries)
- Worker health check recovery
- Index regeneration

**Level 2: Script-Assisted** (Human triggers script)
- Manual task retry with modified parameters
- Worker restart
- Task cancellation

**Level 3: Manual Investigation** (Human debugging)
- Workstream failure analysis
- Dependency cycle resolution
- State corruption recovery

**Level 4: Code Changes Required** (Development intervention)
- Worker implementation bugs
- Scheduler algorithm issues
- State machine invariant violations

---

## Recovery Scripts Reference

### Task Recovery
```bash
scripts/recovery/
├── retry_task.py           # Retry task with custom parameters
├── skip_task.py            # Mark task as completed (with warning)
├── cancel_task.py          # Cancel task and unblock dependents
└── debug_task.py           # Interactive task debugging
```

### Workstream Recovery
```bash
scripts/recovery/
├── retry_workstream.py     # Retry entire workstream
├── retry_failed_tasks.py   # Retry only failed tasks
├── resume_workstream.py    # Resume from specific task
└── rollback_workstream.py  # Rollback to checkpoint
```

### Worker Recovery
```bash
scripts/recovery/
├── restart_worker.py       # Restart worker
├── force_shutdown_worker.py # Force worker shutdown
└── check_worker.py         # Worker health check
```

### State Recovery
```bash
scripts/recovery/
├── restore_state.py        # Restore from backup or transitions
├── validate_state.py       # Check state consistency
└── repair_state.py         # Attempt automatic state repair
```

---

## Best Practices

1. **Monitor First**: Always check `.state/metrics.json` and logs before intervening
2. **Least Invasive**: Start with automatic retries, escalate only if necessary
3. **Document Actions**: Log all manual interventions in `.state/interventions.log`
4. **Test Recovery**: Regularly test recovery procedures in non-production environment
5. **Learn from Failures**: Analyze failures to improve task definitions and worker implementations

## See Also
- [State Machine](./STATE_MACHINE.md): Valid state transitions
- [Failure Modes](../failure_modes/CATALOG.md): Detailed failure mode documentation
- [Scheduling](./SCHEDULING.md): Task scheduling and dependencies
