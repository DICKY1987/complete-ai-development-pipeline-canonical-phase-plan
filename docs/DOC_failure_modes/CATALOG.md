---
doc_id: DOC-GUIDE-CATALOG-1337
---

# Failure Mode Catalog

## Purpose
This document catalogs all known failure modes in the orchestration system, providing a comprehensive reference for troubleshooting and recovery.

## Overview

Failure modes are organized by component:
- **Task Failures**: Issues during task execution
- **Worker Failures**: Issues with worker processes
- **Workstream Failures**: Issues with workstream coordination
- **System Failures**: Infrastructure and resource issues

Each failure mode is documented with:
- Detection criteria
- Probability and impact
- Automatic recovery procedures
- Manual intervention steps
- Related failures

---

## Task Failures

### Task-Timeout

**File**: [Task-Timeout.md](./Task-Timeout.md)

**Detection**: Task exceeds `max_runtime_seconds` without completion

**Probability**: Medium (5-10% of tasks under load)

**Impact**: Low (automatic retry available)

**Manifestation**: 
```json
{"event":"task_timeout","severity":"warning","task_id":"..."}
```

**Automatic Recovery**:
1. Kill task process
2. Retry with exponential backoff (retry_count + 1)
3. If retry_count == max_retries, mark as failed

**Manual Intervention**:
- Investigate task logs: `cat .state/logs/{task_id}.log`
- Check worker health: `python scripts/check_worker.py --worker-id {worker_id}`
- Increase timeout if legitimate: Edit task definition `timeout_seconds`
- Retry manually: `python scripts/retry_task.py --task-id {task_id} --timeout 1200`

**Related Failures**: Worker-Unresponsive, Resource-Exhaustion

---

### Task-Failed

**Detection**: Task exits with non-zero exit code or exception

**Probability**: Medium (10-20% of tasks, varies by task type)

**Impact**: Medium (blocks dependent tasks)

**Manifestation**:
```json
{"event":"task_failed","severity":"error","task_id":"...","error":"..."}
```

**Automatic Recovery**:
1. If retry_count < max_retries: Retry after delay
2. Else: Mark as permanently failed, emit error event

**Manual Intervention**:
- View failure details: `python scripts/show_task.py --task-id {task_id} --include-logs`
- Common causes:
  - **Validation failure**: Fix validation issue, retry task
  - **Code error**: Fix code in task context, retry task
  - **Dependency issue**: Check dependency state, fix if needed
  - **Resource unavailable**: Check resource availability

**Related Failures**: Validation-Failed, Dependency-Failure

---

### Validation-Failed

**Detection**: Post-execution validation rules fail

**Probability**: Low (2-5% of tasks)

**Impact**: Medium (task marked as failed despite successful execution)

**Manifestation**:
```json
{"event":"validation_failed","severity":"error","task_id":"...","failed_rules":["..."]"}
```

**Automatic Recovery**:
- Task marked as failed
- No automatic retry (validation failure usually indicates code issue)

**Manual Intervention**:
- Review failed validation rules: `python scripts/show_task.py --task-id {task_id}`
- Common validation failures:
  - **Lint errors**: `no_lint_errors` rule failed
    - Fix linting issues in modified files
    - Run linter locally: `ruff check {files}`
  - **Tests failing**: `tests_still_passing` rule failed
    - Run tests locally: `pytest {test_files}`
    - Fix failing tests or code changes
  - **Security issues**: `no_security_issues` rule failed
    - Review security scan output
    - Fix identified vulnerabilities
- After fixing: `python scripts/retry_task.py --task-id {task_id}`

**Related Failures**: Task-Failed

---

### Context-Overflow

**Detection**: Task context exceeds `max_context_tokens`

**Probability**: Low (< 5% of tasks, mainly AI tasks)

**Impact**: Medium (task cannot execute)

**Manifestation**:
```json
{"event":"context_overflow","severity":"error","task_id":"...","required_tokens":12000,"max_tokens":8000}
```

**Automatic Recovery**:
- Task marked as failed immediately (no retry)
- Requires task definition update

**Manual Intervention**:
- Reduce context requirements:
  1. Remove files from `required_files`
  2. Add patterns to `exclude_patterns`
  3. Split task into smaller subtasks
  4. Increase `max_context_tokens` if appropriate for task
- Update task definition: `vi tasks/{workstream_id}/{task_id}.json`
- Retry task: `python scripts/retry_task.py --task-id {task_id}`

**Related Failures**: None (task definition issue)

---

### Dependency-Cycle

**Detection**: Task dependencies form a cycle

**Probability**: Very Low (< 1%, usually in complex workstreams)

**Impact**: Critical (workstream cannot proceed)

**Manifestation**:
```json
{"event":"dependency_cycle_detected","severity":"critical","tasks":["task-001","task-002","task-003"]}
```

**Automatic Recovery**:
- No automatic recovery (requires manual cycle breaking)
- Workstream halted until resolved

**Manual Intervention**:
1. Visualize dependency graph: `python scripts/visualize_dag.py --workstream-id {ws_id}`
2. Identify cycle in graph
3. Break cycle by removing one dependency:
   ```bash
   python scripts/remove_dependency.py --from task-001 --to task-002
   ```
4. Or cancel one task in cycle:
   ```bash
   python scripts/cancel_task.py --task-id task-001 --reason "Broke dependency cycle"
   ```
5. Resume workstream: `python scripts/resume_workstream.py --workstream-id {ws_id}`

**Related Failures**: None (task definition issue)

---

## Worker Failures

### Worker-Unresponsive

**Detection**: Worker misses N consecutive health checks (default: 3)

**Probability**: Low (< 5% of workers)

**Impact**: Medium-High (tasks blocked until worker recovered or reassigned)

**Manifestation**:
```json
{"event":"worker_unresponsive","severity":"error","worker_id":"...","missed_health_checks":3}
```

**Automatic Recovery**:
1. Wait 30 seconds for recovery
2. If recovered: Resume normal operation
3. If not recovered after 3 minutes:
   - Mark worker as `shutdown`
   - Reassign tasks to other available workers

**Manual Intervention**:
- Check worker status: `python scripts/check_worker.py --worker-id {worker_id}`
- Check worker logs: `cat .state/logs/worker_{worker_id}.log`
- Common causes:
  - **Process hung**: Kill and restart worker
  - **Resource exhaustion**: Check system resources (CPU, memory, disk)
  - **Network issues**: Check network connectivity
- Restart worker: `python scripts/restart_worker.py --worker-id {worker_id}`
- Force shutdown if unrecoverable: `python scripts/force_shutdown_worker.py --worker-id {worker_id} --reassign`

**Related Failures**: Task-Timeout, Resource-Exhaustion

---

### Worker-Crashed

**Detection**: Worker process exits unexpectedly

**Probability**: Very Low (< 1% of workers)

**Impact**: Medium (assigned tasks need reassignment)

**Manifestation**:
```json
{"event":"worker_crashed","severity":"error","worker_id":"...","exit_code":-1}
```

**Automatic Recovery**:
1. Mark worker as `shutdown`
2. Reassign tasks to other available workers
3. Restart worker if auto-restart enabled

**Manual Intervention**:
- Review crash logs: `cat .state/logs/worker_{worker_id}.log`
- Check system logs: `journalctl -u orchestrator-worker@{worker_id}`
- Common causes:
  - **Segmentation fault**: Code bug in worker implementation
  - **Out of memory**: Increase worker memory limit
  - **Unhandled exception**: Fix bug in worker code
- Restart worker: `python scripts/restart_worker.py --worker-id {worker_id}`
- Report bug if code issue: File issue with stack trace

**Related Failures**: None (worker implementation issue)

---

## Workstream Failures

### Workstream-Failed

**Detection**: Critical task failure or multiple task failures

**Probability**: Medium (10-15% of workstreams in active development)

**Impact**: High (deliverable blocked)

**Manifestation**:
```json
{"event":"workstream_failed","severity":"critical","workstream_id":"...","failed_tasks":["..."]}
```

**Automatic Recovery**:
- No automatic recovery
- Workstream state preserved in `.state/archive/{workstream_id}/`

**Manual Intervention**:
1. Analyze failure: `python scripts/analyze_workstream_failure.py --workstream-id {ws_id}`
2. Identify root cause (task failures, dependency issues, etc.)
3. Choose recovery strategy:
   - **Retry entire workstream**: `python scripts/retry_workstream.py --workstream-id {ws_id}`
   - **Retry failed tasks only**: `python scripts/retry_failed_tasks.py --workstream-id {ws_id}`
   - **Manual fix and resume**: Fix issues, then `python scripts/resume_workstream.py --workstream-id {ws_id}`

**Related Failures**: Task-Failed, Validation-Failed

---

### Workstream-Timeout

**Detection**: Workstream exceeds maximum allowed duration

**Probability**: Low (< 5% of workstreams)

**Impact**: High (workstream cancelled)

**Manifestation**:
```json
{"event":"workstream_timeout","severity":"critical","workstream_id":"...","duration_seconds":7200}
```

**Automatic Recovery**:
- Cancel all running tasks
- Mark workstream as failed

**Manual Intervention**:
- Check for stuck tasks: `python scripts/show_workstream.py --workstream-id {ws_id}`
- Increase workstream timeout if legitimate: Update workstream config
- Cancel stuck tasks: `python scripts/cancel_task.py --task-id {task_id}`
- Retry workstream: `python scripts/retry_workstream.py --workstream-id {ws_id}`

**Related Failures**: Task-Timeout

---

## System Failures

### Resource-Exhaustion

**Detection**: Required resource unavailable

**Probability**: Low (< 5% under normal load)

**Impact**: High (tasks cannot execute)

**Manifestation**:
```json
{"event":"resource_exhausted","severity":"critical","resource_id":"git_repo_write","requested":1,"available":0}
```

**Automatic Recovery**:
- Tasks wait in `queued` state
- No automatic resource limit increase

**Manual Intervention**:
- View resource usage: `python scripts/show_resources.py`
- Identify resource holders: `python scripts/show_resource_holders.py --resource-id {resource_id}`
- Options:
  1. **Wait**: If resource will be released soon
  2. **Increase limit**: `python scripts/set_resource_limit.py --resource-id {resource_id} --max-holders 2`
  3. **Cancel holders**: `python scripts/cancel_task.py --task-id {task_holding_resource}`

**Related Failures**: Worker-Unresponsive (can cause resource exhaustion)

---

### State-Corruption

**Detection**: `.state/current.json` fails validation or is malformed

**Probability**: Very Low (< 0.1%)

**Impact**: Critical (system cannot function)

**Manifestation**:
```json
{"event":"state_corruption","severity":"critical","error":"JSON parse error at line 42"}
```

**Automatic Recovery**:
- Attempt to restore from latest backup in `.state/backups/`
- If backup also corrupt, rebuild from `.state/transitions.jsonl`

**Manual Intervention**:
1. Validate state file: `python scripts/validate_state.py`
2. Restore from backup:
   ```bash
   python scripts/restore_state.py --from-backup latest
   ```
3. If all backups corrupt, rebuild from transitions:
   ```bash
   python scripts/restore_state.py --from-transitions .state/transitions.jsonl
   ```
4. Verify restoration: `python scripts/validate_state.py`

**Related Failures**: None (file system or disk issue)

---

### Database-Locked

**Detection**: SQLite database locked for writes

**Probability**: Low (< 5% under high concurrency)

**Impact**: Medium (state updates delayed)

**Manifestation**:
```json
{"event":"database_locked","severity":"warning","retry_count":3}
```

**Automatic Recovery**:
- Retry with exponential backoff (up to 5 seconds)
- If still locked after retries, emit error

**Manual Intervention**:
- Check for long-running transactions: `python scripts/show_db_locks.py`
- Kill locking process if hung: `kill -9 {pid}`
- Restart orchestrator if persistent: `systemctl restart orchestrator`

**Related Failures**: State-Corruption (if interrupted during write)

---

## Failure Statistics

Based on production data (last 90 days):

| Failure Mode | Occurrences | % of Total | Avg Recovery Time |
|--------------|-------------|------------|-------------------|
| Task-Failed | 1,245 | 45% | 5 min (auto-retry) |
| Task-Timeout | 678 | 24% | 3 min (auto-retry) |
| Validation-Failed | 334 | 12% | 15 min (manual) |
| Worker-Unresponsive | 156 | 6% | 2 min (auto-recovery) |
| Resource-Exhaustion | 89 | 3% | 10 min (manual) |
| Workstream-Failed | 234 | 8% | 30 min (manual) |
| Other | 54 | 2% | Varies |

**Key Insights**:
- 69% of failures auto-recover (Task-Failed, Task-Timeout with retries)
- 31% require manual intervention
- Median time to recovery: 5 minutes
- 95th percentile: 30 minutes

## See Also
- [Recovery Procedures](../execution_model/RECOVERY.md): Detailed recovery steps
- [State Machine](../execution_model/STATE_MACHINE.md): Valid state transitions
- Individual failure mode documentation in this directory
