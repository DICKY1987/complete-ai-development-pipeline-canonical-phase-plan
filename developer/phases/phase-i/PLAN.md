---
doc_id: DOC-GUIDE-PLAN-1301
---

# Phase I: UET Production Integration & Enhancement

**Created**: 2025-11-21  
**Status**: Planning  
**Depends On**: Phase H (UET Foundation) - Complete  
**Target Duration**: 8-10 weeks  
**Expected Impact**: Production-ready parallel execution with 3.0x speedup

---

## Executive Summary

Phase I integrates the UET framework components built in Phase H into the production orchestrator, enabling real parallel workstream execution with full observability, cost control, and crash recovery. This phase transforms the theoretical 3.0x speedup into actual wall-clock performance gains.

**Key Goals**:
- Integrate parallel scheduler with existing orchestrator
- Implement real worker process spawning
- Enable production execution with monitoring
- Add integration worker for merge conflict resolution
- Deploy cost budgets and enforcement

**Expected Outcomes**:
- 40-50% reduction in phase execution time (proven by analysis)
- Production-grade crash recovery
- Real-time cost tracking and budget enforcement
- Automated merge conflict detection

---

## Phase Overview

```
Phase I-1: Core Integration (3 weeks)
    ↓
Phase I-2: Production Execution (3 weeks)
    ↓
Phase I-3: Advanced Features (2 weeks)
    ↓
Phase I-4: Performance & Polish (2 weeks)
```

---

## Phase I-1: Core Integration (Weeks 1-3)

**Goal**: Connect UET components to production orchestrator  
**Risk**: Medium  

### Workstream WS-I1: Orchestrator Integration

**Priority**: Critical Path  
**Estimated Time**: 12-15 hours  
**Files**: `core/engine/orchestrator.py`, `core/engine/scheduler.py`

#### Tasks

1. **Extend Orchestrator with Parallel Mode**
   ```python
   # core/engine/orchestrator.py
   
   def execute_workstreams_parallel(
       bundles: List[WorkstreamBundle],
       max_workers: int = 4,
       dry_run: bool = False
   ) -> Dict[str, Any]:
       """Execute workstreams in parallel using UET scheduler.
       
       High-level flow:
       1. Validate bundles and build execution plan
       2. Initialize worker pool
       3. Spawn workers
       4. For each wave:
           - Assign ready tasks to idle workers
           - Monitor execution
           - Handle task completion/failure
           - Collect results
       5. Merge phase (integration worker)
       6. Cleanup and metrics
       """
       from core.engine.scheduler import build_execution_plan, TaskScheduler
       from core.engine.worker import WorkerPool
       from core.engine.event_bus import EventBus, Event, EventType
       from core.engine.plan_validator import validate_phase_plan
       
       # Validate plan
       report = validate_phase_plan(bundles, max_workers=max_workers)
       if not report.valid:
           raise ValueError(f"Invalid plan: {report.errors}")
       
       # Build execution plan
       plan = build_execution_plan(bundles, max_workers)
       
       if dry_run:
           return {
               'dry_run': True,
               'plan': plan,
               'estimated_speedup': report.parallelism_profile.estimated_speedup
           }
       
       # Initialize components
       worker_pool = WorkerPool(max_workers=max_workers)
       scheduler = TaskScheduler(worker_pool)
       event_bus = EventBus()
       
       # Spawn workers
       for i in range(max_workers):
           worker = worker_pool.spawn_worker(adapter_type='aider')
           event_bus.emit(Event(
               event_type=EventType.WORKER_SPAWNED,
               timestamp=datetime.now(timezone.utc),
               worker_id=worker.worker_id
           ))
       
       # Execute waves
       results = _execute_waves(plan, scheduler, worker_pool, event_bus, bundles)
       
       # Cleanup
       for worker_id in list(worker_pool.workers.keys()):
           worker_pool.terminate_worker(worker_id)
       
       return results
   ```

2. **Wave Execution Loop**
   ```python
   def _execute_waves(
       plan: ExecutionPlan,
       scheduler: TaskScheduler,
       worker_pool: WorkerPool,
       event_bus: EventBus,
       bundles: List[WorkstreamBundle]
   ) -> Dict[str, Any]:
       """Execute workstreams wave by wave."""
       completed = set()
       failed = set()
       results = {}
       
       bundle_map = {b.id: b for b in bundles}
       
       for wave_idx, wave in enumerate(plan.waves):
           print(f"\n=== Wave {wave_idx + 1}/{len(plan.waves)} ===")
           print(f"Workstreams: {', '.join(sorted(wave.workstream_ids))}")
           
           # Assign tasks in this wave
           for ws_id in wave.workstream_ids:
               if ws_id in completed or ws_id in failed:
                   continue
               
               # Wait for idle worker
               worker = worker_pool.get_idle_worker()
               while not worker:
                   time.sleep(1)
                   worker = worker_pool.get_idle_worker()
               
               # Assign task
               worker_id = scheduler.assign_task(ws_id)
               
               # Execute workstream (async)
               _execute_workstream_async(
                   bundle_map[ws_id],
                   worker_id,
                   worker_pool,
                   event_bus,
                   completed,
                   failed,
                   results
               )
           
           # Wait for wave to complete
           while len(completed) + len(failed) < sum(len(w.workstream_ids) for w in plan.waves[:wave_idx+1]):
               time.sleep(1)
       
       return {
           'completed': list(completed),
           'failed': list(failed),
           'results': results
       }
   ```

3. **CLI Integration**
   ```python
   # scripts/run_workstream.py (extend)
   
   parser.add_argument('--parallel', action='store_true', help='Enable parallel execution')
   parser.add_argument('--max-workers', type=int, default=4, help='Max parallel workers')
   
   if args.parallel:
       result = execute_workstreams_parallel(
           bundles,
           max_workers=args.max_workers,
           dry_run=args.dry_run
       )
   else:
       # Existing sequential execution
       result = execute_workstreams_sequential(bundles)
   ```

#### Acceptance Criteria

- [ ] Parallel execution mode selectable via CLI flag
- [ ] Worker pool spawns and manages workers
- [ ] Waves execute in correct order
- [ ] Dependencies respected (no premature execution)
- [ ] Events logged for all lifecycle transitions
- [ ] Dry-run mode works without spawning workers

#### Files Changed
- `core/engine/orchestrator.py` - Add parallel execution
- `scripts/run_workstream.py` - Add --parallel flag
- `tests/test_parallel_orchestrator.py` - Integration tests

---

### Workstream WS-I2: Worker Process Spawning

**Priority**: Critical Path  
**Estimated Time**: 10-12 hours  
**Depends On**: WS-I1

#### Tasks

1. **Implement Real Worker Spawning**
   ```python
   # core/engine/worker.py (extend)
   
   class WorkerPool:
       def spawn_worker(self, adapter_type: str, worker_id: Optional[str] = None) -> Worker:
           """Spawn real worker process."""
           worker = super().spawn_worker(adapter_type, worker_id)
           
           # Create sandbox directory
           sandbox_path = Path(f"state/workers/{worker.worker_id}")
           sandbox_path.mkdir(parents=True, exist_ok=True)
           worker.sandbox_path = str(sandbox_path)
           
           # Spawn process based on adapter type
           if adapter_type == 'aider':
               process = self._spawn_aider_worker(worker)
           elif adapter_type == 'codex':
               process = self._spawn_codex_worker(worker)
           else:
               raise ValueError(f"Unknown adapter type: {adapter_type}")
           
           worker.metadata['process_id'] = process.pid
           self._persist_worker(worker)
           
           return worker
   ```

2. **Aider Worker Adapter**
   ```python
   def _spawn_aider_worker(self, worker: Worker) -> subprocess.Popen:
       """Spawn Aider process in sandbox."""
       from core.engine.tools import get_tool_config
       
       config = get_tool_config('aider')
       
       cmd = [
           'aider',
           '--yes-always',  # Auto-apply changes
           '--no-auto-commits',  # We handle commits
           '--message-file', f"{worker.sandbox_path}/prompt.txt"
       ]
       
       process = subprocess.Popen(
           cmd,
           cwd=worker.sandbox_path,
           stdout=subprocess.PIPE,
           stderr=subprocess.PIPE,
           text=True
       )
       
       return process
   ```

3. **Task Execution**
   ```python
   def execute_task(self, worker_id: str, bundle: WorkstreamBundle) -> Dict[str, Any]:
       """Execute workstream task on worker."""
       worker = self.workers[worker_id]
       
       # Prepare prompt
       prompt = self._build_prompt(bundle)
       prompt_file = Path(worker.sandbox_path) / "prompt.txt"
       prompt_file.write_text(prompt)
       
       # Send to worker process
       process = psutil.Process(worker.metadata['process_id'])
       
       # Monitor execution
       start_time = time.time()
       while True:
           # Check if process completed
           if process.poll() is not None:
               break
           
           # Check timeout
           if time.time() - start_time > bundle.metadata.get('timeout', 3600):
               process.kill()
               raise TimeoutError(f"Task {bundle.id} timed out")
           
           time.sleep(1)
       
       # Collect results
       output_file = Path(worker.sandbox_path) / "output.txt"
       result = output_file.read_text() if output_file.exists() else ""
       
       return {
           'success': process.returncode == 0,
           'output': result,
           'duration': time.time() - start_time
       }
   ```

#### Acceptance Criteria

- [ ] Worker processes spawn successfully
- [ ] Sandbox directories created and isolated
- [ ] Aider workers execute tasks
- [ ] Process monitoring detects completion
- [ ] Timeout handling works
- [ ] Worker cleanup on termination

#### Files Changed
- `core/engine/worker.py` - Add process spawning
- `core/engine/tools.py` - Worker adapters
- `tests/test_worker_spawning.py` - Process tests

---

### Workstream WS-I3: Event-Driven Monitoring

**Priority**: High  
**Estimated Time**: 6-8 hours  
**Depends On**: WS-I1

#### Tasks

1. **Real-Time Event Dashboard**
   ```python
   # scripts/monitor_execution.py (new)
   
   import curses
   from core.engine.event_bus import EventBus, EventType
   from datetime import datetime, timezone
   
   def monitor_execution(stdscr, run_id: str):
       """Real-time execution monitoring dashboard."""
       bus = EventBus()
       curses.curs_set(0)
       
       while True:
           stdscr.clear()
           height, width = stdscr.getmaxyx()
           
           # Header
           stdscr.addstr(0, 0, f"UET Execution Monitor - Run: {run_id}", curses.A_BOLD)
           stdscr.addstr(1, 0, "-" * width)
           
           # Recent events
           events = bus.query(run_id=run_id, limit=height - 10)
           
           row = 3
           for event in reversed(events):
               if row >= height - 2:
                   break
               
               timestamp = event.timestamp.strftime("%H:%M:%S")
               line = f"[{timestamp}] {event.event_type.value:20s}"
               
               if event.workstream_id:
                   line += f" WS: {event.workstream_id}"
               if event.worker_id:
                   line += f" Worker: {event.worker_id}"
               
               stdscr.addstr(row, 0, line[:width-1])
               row += 1
           
           # Worker status
           stdscr.addstr(height - 5, 0, "Workers:", curses.A_BOLD)
           # ... display worker states
           
           stdscr.refresh()
           time.sleep(1)
   
   if __name__ == '__main__':
       import sys
       run_id = sys.argv[1] if len(sys.argv) > 1 else 'current'
       curses.wrapper(monitor_execution, run_id)
   ```

2. **Progress Tracking**
   ```python
   # core/engine/progress.py (new)
   
   class ProgressTracker:
       """Track execution progress."""
       
       def __init__(self, plan: ExecutionPlan):
           self.plan = plan
           self.completed = set()
           self.failed = set()
           self.in_progress = set()
       
       def update(self, ws_id: str, status: str):
           """Update workstream status."""
           if status == 'started':
               self.in_progress.add(ws_id)
           elif status == 'completed':
               self.in_progress.discard(ws_id)
               self.completed.add(ws_id)
           elif status == 'failed':
               self.in_progress.discard(ws_id)
               self.failed.add(ws_id)
       
       def get_progress(self) -> Dict[str, Any]:
           """Get current progress."""
           total = sum(len(w.workstream_ids) for w in self.plan.waves)
           
           return {
               'total': total,
               'completed': len(self.completed),
               'failed': len(self.failed),
               'in_progress': len(self.in_progress),
               'percent': (len(self.completed) / total * 100) if total > 0 else 0
           }
   ```

#### Acceptance Criteria

- [ ] Real-time dashboard displays events
- [ ] Worker status visible
- [ ] Progress percentage accurate
- [ ] Event filtering works
- [ ] Dashboard updates every second

#### Files Changed
- `scripts/monitor_execution.py` (new)
- `core/engine/progress.py` (new)
- `tests/test_monitoring.py` (new)

---

## Phase I-2: Production Execution (Weeks 4-6)

**Goal**: Enable reliable production parallel execution  
**Risk**: Medium-High  

### Workstream WS-I4: Integration Worker & Merge Strategy

**Priority**: Critical Path  
**Estimated Time**: 12-15 hours  

#### Tasks

1. **Complete Integration Worker**
   ```python
   # core/engine/integration_worker.py (complete from stub)
   
   class IntegrationWorker:
       """Merge orchestrator with conflict detection."""
       
       def merge_workstreams(
           self,
           completed_workstreams: List[str],
           target_branch: str = 'main'
       ) -> Dict[str, Any]:
           """Merge completed workstreams deterministically."""
           
           # Sort by priority
           candidates = self._prioritize_candidates(completed_workstreams)
           
           merged = []
           conflicts = []
           
           for ws_id in candidates:
               try:
                   # Attempt merge
                   result = self._merge_candidate(ws_id, target_branch)
                   
                   if result['success']:
                       merged.append(ws_id)
                   else:
                       conflicts.append({
                           'ws_id': ws_id,
                           'files': result['conflicted_files'],
                           'reason': result['error']
                       })
               
               except Exception as e:
                   conflicts.append({
                       'ws_id': ws_id,
                       'error': str(e)
                   })
           
           return {
               'merged': merged,
               'conflicts': conflicts,
               'success': len(conflicts) == 0
           }
   ```

2. **Git Worktree Integration**
   ```python
   def _merge_candidate(self, ws_id: str, target_branch: str) -> Dict[str, Any]:
       """Merge workstream using git worktree."""
       from core.state.worktree import get_worktree_path
       
       worktree_path = get_worktree_path(ws_id)
       
       # Check if worktree exists
       if not worktree_path.exists():
           return {'success': False, 'error': 'Worktree not found'}
       
       # Get changes
       result = subprocess.run(
           ['git', 'diff', '--name-only', target_branch],
           cwd=worktree_path,
           capture_output=True,
           text=True
       )
       
       changed_files = result.stdout.strip().split('\n')
       
       # Create patch
       patch_result = subprocess.run(
           ['git', 'format-patch', target_branch, '--stdout'],
           cwd=worktree_path,
           capture_output=True,
           text=True
       )
       
       # Apply to main
       apply_result = subprocess.run(
           ['git', 'apply', '--check'],
           input=patch_result.stdout,
           capture_output=True,
           text=True
       )
       
       if apply_result.returncode != 0:
           # Conflict detected
           return {
               'success': False,
               'conflicted_files': changed_files,
               'error': apply_result.stderr
           }
       
       # Apply for real
       subprocess.run(
           ['git', 'apply'],
           input=patch_result.stdout,
           check=True
       )
       
       # Commit
       subprocess.run(
           ['git', 'commit', '-m', f'Merge {ws_id}'],
           check=True
       )
       
       return {'success': True, 'files': changed_files}
   ```

3. **Conflict Resolution Agent**
   ```python
   def handle_conflict(
       self,
       conflict: Dict[str, Any]
   ) -> Dict[str, Any]:
       """Route conflict to resolution agent."""
       from error.engine.error_pipeline_service import ErrorPipelineService
       
       # Create merge conflict task
       svc = ErrorPipelineService()
       task_id = svc.create_merge_conflict_task(
           workstream_id=conflict['ws_id'],
           conflicted_files=conflict['files'],
           error_message=conflict.get('error', '')
       )
       
       # Try auto-resolution with Aider
       auto_resolved = self._auto_resolve_conflict(conflict)
       
       if auto_resolved:
           svc.mark_resolved(task_id, 'AUTO_RESOLVED')
           return {'resolved': True, 'method': 'auto'}
       
       # Escalate to human
       return {'resolved': False, 'task_id': task_id, 'method': 'manual'}
   ```

#### Acceptance Criteria

- [ ] Workstreams merged in deterministic order
- [ ] Conflicts detected before applying
- [ ] Auto-resolution attempted
- [ ] Manual conflicts escalated
- [ ] Merge commits created
- [ ] Integration tests pass

#### Files Changed
- `core/engine/integration_worker.py` (complete)
- `core/engine/merge_conflict_resolver.py` (extend)
- `tests/test_integration_worker.py` (complete)

---

### Workstream WS-I5: Crash Recovery Integration

**Priority**: High  
**Estimated Time**: 8-10 hours  

#### Tasks

1. **Orchestrator Restart Handler**
   ```python
   # core/engine/orchestrator.py (extend)
   
   def resume_from_crash() -> Dict[str, Any]:
       """Resume execution after orchestrator crash."""
       from core.engine.recovery_manager import RecoveryManager
       
       recovery = RecoveryManager()
       
       # Detect crash
       result = recovery.recover_from_crash()
       
       if result['orphaned_tasks'] > 0:
           print(f"⚠️  Recovered from crash: {result['orphaned_tasks']} orphaned tasks")
           
           # Load last execution state
           run_id = _get_last_run_id()
           bundles = _load_bundles_for_run(run_id)
           
           # Resume execution
           return execute_workstreams_parallel(
               bundles,
               max_workers=4,
               resume=True
           )
       
       return {'recovered': False}
   ```

2. **State Checkpointing**
   ```python
   # core/engine/checkpointing.py (extend)
   
   def checkpoint_execution_state(
       run_id: str,
       completed: Set[str],
       in_progress: Dict[str, str],  # ws_id -> worker_id
       plan: ExecutionPlan
   ):
       """Checkpoint current execution state."""
       from core.state.db import get_connection
       import json
       
       conn = get_connection()
       
       state = {
           'completed': list(completed),
           'in_progress': in_progress,
           'plan': {
               'waves': [[ws for ws in wave.workstream_ids] for wave in plan.waves]
           },
           'timestamp': datetime.now(timezone.utc).isoformat()
       }
       
       conn.execute("""
           INSERT OR REPLACE INTO execution_checkpoints
           (run_id, state_json, created_at)
           VALUES (?, ?, CURRENT_TIMESTAMP)
       """, (run_id, json.dumps(state)))
       
       conn.commit()
       conn.close()
   ```

3. **Resume Logic**
   ```python
   def _resume_execution(
       run_id: str,
       bundles: List[WorkstreamBundle]
   ) -> Dict[str, Any]:
       """Resume from checkpoint."""
       from core.state.db import get_connection
       
       # Load checkpoint
       conn = get_connection()
       cursor = conn.execute(
           "SELECT state_json FROM execution_checkpoints WHERE run_id = ? ORDER BY created_at DESC LIMIT 1",
           (run_id,)
       )
       row = cursor.fetchone()
       conn.close()
       
       if not row:
           raise ValueError(f"No checkpoint found for run {run_id}")
       
       state = json.loads(row[0])
       
       # Filter to incomplete workstreams
       completed = set(state['completed'])
       remaining = [b for b in bundles if b.id not in completed]
       
       print(f"Resuming: {len(completed)} completed, {len(remaining)} remaining")
       
       # Execute remaining
       return execute_workstreams_parallel(remaining, max_workers=4)
   ```

#### Acceptance Criteria

- [ ] Crash detection works
- [ ] Checkpoints created every 30 seconds
- [ ] Resume loads correct state
- [ ] No duplicate executions
- [ ] Orphaned workers cleaned up
- [ ] Integration test: kill orchestrator mid-execution, resume succeeds

#### Files Changed
- `core/engine/orchestrator.py` - Add resume logic
- `core/engine/checkpointing.py` - State persistence
- `schema/schema.sql` - Add execution_checkpoints table
- `tests/test_crash_recovery_integration.py` (new)

---

### Workstream WS-I6: Cost Budget Enforcement

**Priority**: Medium  
**Estimated Time**: 6-8 hours  

#### Tasks

1. **Budget Policy Engine**
   ```python
   # core/engine/budget_policy.py (extend from stub)
   
   class BudgetEnforcer:
       def __init__(self, policy: BudgetPolicy):
           self.policy = policy
           self.tracker = CostTracker()
       
       def enforce_budget(self, run_id: str) -> Dict[str, Any]:
           """Enforce budget limits during execution."""
           total_cost = self.tracker.get_total_cost(run_id)
           
           # Check total budget
           if total_cost >= self.policy.max_cost_total:
               return {
                   'action': 'HALT',
                   'reason': f'Total budget exceeded: ${total_cost:.2f} / ${self.policy.max_cost_total}',
                   'allow_continue': False
               }
           
           # Check warning threshold (90%)
           if total_cost >= self.policy.max_cost_total * 0.9:
               return {
                   'action': 'WARN',
                   'reason': f'Approaching budget limit: ${total_cost:.2f} / ${self.policy.max_cost_total}',
                   'allow_continue': True,
                   'reduce_parallelism': True
               }
           
           return {
               'action': 'CONTINUE',
               'allow_continue': True
           }
   ```

2. **Integration with Orchestrator**
   ```python
   # In execute_workstreams_parallel
   
   budget_enforcer = BudgetEnforcer(BudgetPolicy(
       max_cost_total=100.0,  # From config
       max_cost_per_task=5.0
   ))
   
   # Before each wave
   budget_check = budget_enforcer.enforce_budget(run_id)
   
   if not budget_check['allow_continue']:
       print(f"❌ {budget_check['reason']}")
       # Graceful shutdown
       for worker_id in worker_pool.workers:
           worker_pool.drain_worker(worker_id)
       break
   
   if budget_check.get('reduce_parallelism'):
       print(f"⚠️  {budget_check['reason']}")
       # Reduce parallelism
       max_workers = max(1, max_workers - 1)
   ```

3. **Budget Configuration**
   ```yaml
   # config/budget.yaml (new)
   
   default:
     max_cost_total: 100.0
     max_cost_per_phase: 20.0
     max_cost_per_task: 5.0
     warning_threshold: 0.9
     halt_threshold: 1.0
   
   models:
     gpt-4:
       input_cost_per_1k: 0.03
       output_cost_per_1k: 0.06
     gpt-3.5-turbo:
       input_cost_per_1k: 0.0015
       output_cost_per_1k: 0.002
   ```

#### Acceptance Criteria

- [ ] Budget limits enforced
- [ ] Warning at 90% threshold
- [ ] Halt at 100% threshold
- [ ] Parallelism reduced on warning
- [ ] Configuration file loaded
- [ ] Cost reports generated

#### Files Changed
- `core/engine/budget_policy.py` (complete)
- `config/budget.yaml` (new)
- `tests/test_budget_enforcement.py` (new)

---

## Phase I-3: Advanced Features (Weeks 7-8)

**Goal**: Add intelligence and optimization features  
**Risk**: Low  

### Workstream WS-I7: Test Gate Enforcement

**Priority**: Medium  
**Estimated Time**: 8-10 hours  

#### Tasks

1. **Test Gate Runner**
   ```python
   # core/engine/test_gates.py (new)
   
   from enum import Enum
   
   class GateType(Enum):
       GATE_LINT = "GATE_LINT"
       GATE_UNIT = "GATE_UNIT"
       GATE_INTEGRATION = "GATE_INTEGRATION"
       GATE_SECURITY = "GATE_SECURITY"
   
   class TestGateRunner:
       def run_gates(
           self,
           bundle: WorkstreamBundle,
           sandbox_path: Path
       ) -> Dict[str, Any]:
           """Run all test gates for workstream."""
           results = []
           
           for gate in bundle.test_gates:
               gate_type = GateType(gate['type'])
               required = gate.get('required', False)
               blocking = gate.get('blocking', False)
               
               result = self._run_gate(gate_type, sandbox_path)
               
               if not result['passed'] and blocking:
                   return {
                       'passed': False,
                       'gate': gate_type.value,
                       'results': results + [result]
                   }
               
               results.append(result)
           
           return {
               'passed': all(r['passed'] for r in results if r.get('required')),
               'results': results
           }
   ```

2. **Gate Implementations**
   ```python
   def _run_gate(self, gate_type: GateType, sandbox_path: Path) -> Dict[str, Any]:
       """Run specific gate type."""
       if gate_type == GateType.GATE_LINT:
           return self._run_lint(sandbox_path)
       elif gate_type == GateType.GATE_UNIT:
           return self._run_unit_tests(sandbox_path)
       elif gate_type == GateType.GATE_INTEGRATION:
           return self._run_integration_tests(sandbox_path)
       elif gate_type == GateType.GATE_SECURITY:
           return self._run_security_scan(sandbox_path)
   
   def _run_lint(self, sandbox_path: Path) -> Dict[str, Any]:
       """Run linters."""
       # Python
       result = subprocess.run(
           ['ruff', 'check', '.'],
           cwd=sandbox_path,
           capture_output=True
       )
       
       return {
           'gate': 'GATE_LINT',
           'passed': result.returncode == 0,
           'output': result.stdout.decode()
       }
   ```

3. **Integration with Execution**
   ```python
   # In execute_workstream
   
   # After task execution
   if bundle.test_gates:
       gate_runner = TestGateRunner()
       gate_results = gate_runner.run_gates(bundle, worker.sandbox_path)
       
       if not gate_results['passed']:
           # Fail the workstream
           return {
               'success': False,
               'reason': 'Test gates failed',
               'gate_results': gate_results
           }
   ```

#### Acceptance Criteria

- [ ] All 4 gate types implemented
- [ ] Required gates enforced
- [ ] Blocking gates halt execution
- [ ] Non-blocking gates logged as warnings
- [ ] Results saved to database
- [ ] Integration test: gate failure prevents completion

#### Files Changed
- `core/engine/test_gates.py` (new)
- `core/engine/orchestrator.py` - Integrate gates
- `tests/test_gate_enforcement.py` (new)

---

### Workstream WS-I8: Context Optimization

**Priority**: Low  
**Estimated Time**: 6-8 hours  

#### Tasks

1. **Context Pruning**
   ```python
   # core/engine/context_pruner.py (extend from stub)
   
   def prune_context(
       files: List[str],
       target_tokens: int
   ) -> Tuple[List[str], int]:
       """Prune files to fit context limit."""
       from core.engine.context_estimator import ContextEstimator
       
       estimator = ContextEstimator()
       total_tokens = estimator.estimate_tokens(files)
       
       if total_tokens <= target_tokens:
           return files, total_tokens
       
       # Priority: keep source files, prune tests/docs
       prioritized = _prioritize_files(files)
       
       pruned = []
       current_tokens = 0
       
       for file_path in prioritized:
           file_tokens = estimator.estimate_tokens([file_path])
           
           if current_tokens + file_tokens > target_tokens:
               break
           
           pruned.append(file_path)
           current_tokens += file_tokens
       
       return pruned, current_tokens
   ```

2. **Smart Summarization**
   ```python
   def summarize_large_files(
       files: List[str],
       max_tokens_per_file: int = 2000
   ) -> Dict[str, str]:
       """Summarize files that exceed token limit."""
       summaries = {}
       
       for file_path in files:
           tokens = estimator.estimate_tokens([file_path])
           
           if tokens > max_tokens_per_file:
               # Generate summary
               summary = _generate_summary(file_path)
               summaries[file_path] = summary
       
       return summaries
   ```

#### Acceptance Criteria

- [ ] Context pruning reduces tokens by 20-30%
- [ ] File prioritization preserves important files
- [ ] Summaries generated for large files
- [ ] Context limit enforced before execution
- [ ] Warning logged when pruning occurs

#### Files Changed
- `core/engine/context_pruner.py` (complete)
- `core/engine/orchestrator.py` - Apply pruning
- `tests/test_context_optimization.py` (new)

---

### Workstream WS-I9: Metrics & Reporting

**Priority**: Medium  
**Estimated Time**: 6-8 hours  

#### Tasks

1. **Execution Report Generator**
   ```python
   # scripts/generate_report.py (new)
   
   def generate_execution_report(run_id: str) -> str:
       """Generate comprehensive execution report."""
       from core.engine.metrics import MetricsAggregator
       from core.engine.cost_tracker import CostTracker
       from core.engine.event_bus import EventBus
       
       aggregator = MetricsAggregator()
       tracker = CostTracker()
       bus = EventBus()
       
       metrics = aggregator.compute_metrics(run_id)
       events = bus.query(run_id=run_id, limit=1000)
       
       report = f"""
# Execution Report: {run_id}

## Summary

- Duration: {metrics.total_duration_sec:.1f}s
- Total Cost: ${metrics.total_cost_usd:.2f}
- Total Tokens: {metrics.total_tokens:,}
- Workstreams Completed: {metrics.workstreams_completed}
- Workstreams Failed: {metrics.workstreams_failed}
- Parallelism Efficiency: {metrics.parallelism_efficiency:.1%}

## Timeline

"""
       
       # Event timeline
       for event in events[:50]:
           report += f"- [{event.timestamp}] {event.event_type.value}\n"
       
       return report
   ```

2. **Performance Comparison**
   ```python
   def compare_executions(run_ids: List[str]) -> Dict[str, Any]:
       """Compare multiple execution runs."""
       comparisons = []
       
       for run_id in run_ids:
           metrics = MetricsAggregator().compute_metrics(run_id)
           comparisons.append({
               'run_id': run_id,
               'duration': metrics.total_duration_sec,
               'cost': metrics.total_cost_usd,
               'efficiency': metrics.parallelism_efficiency
           })
       
       return {
           'runs': comparisons,
           'best_duration': min(comparisons, key=lambda x: x['duration']),
           'best_cost': min(comparisons, key=lambda x: x['cost']),
           'best_efficiency': max(comparisons, key=lambda x: x['efficiency'])
       }
   ```

#### Acceptance Criteria

- [ ] Report generated for completed runs
- [ ] Timeline includes key events
- [ ] Cost breakdown by workstream
- [ ] Comparison tool shows trends
- [ ] Export to JSON/HTML/PDF

#### Files Changed
- `scripts/generate_report.py` (new)
- `core/engine/metrics.py` (extend)
- `tests/test_reporting.py` (new)

---

## Phase I-4: Performance & Polish (Weeks 9-10)

**Goal**: Optimize performance and production readiness  
**Risk**: Low  

### Workstream WS-I10: Performance Optimization

**Priority**: Medium  
**Estimated Time**: 8-10 hours  

#### Tasks

1. **Database Connection Pooling**
   ```python
   # core/state/db.py (optimize)
   
   from contextlib import contextmanager
   import threading
   
   _connection_pool = threading.local()
   
   @contextmanager
   def get_connection_pooled():
       """Get pooled database connection."""
       if not hasattr(_connection_pool, 'conn'):
           _connection_pool.conn = sqlite3.connect(
               str(_resolve_db_path(None)),
               check_same_thread=False
           )
       
       try:
           yield _connection_pool.conn
       finally:
           pass  # Don't close, reuse
   ```

2. **Event Bus Batching**
   ```python
   # core/engine/event_bus.py (optimize)
   
   class EventBus:
       def __init__(self):
           self.batch = []
           self.batch_size = 100
       
       def emit(self, event: Event) -> None:
           """Batch events for performance."""
           self.batch.append(event)
           
           if len(self.batch) >= self.batch_size:
               self._flush_batch()
       
       def _flush_batch(self):
           """Flush batch to database."""
           if not self.batch:
               return
           
           conn = get_connection()
           cursor = conn.cursor()
           
           cursor.executemany("""
               INSERT INTO uet_events 
               (event_type, worker_id, task_id, run_id, workstream_id, timestamp, payload_json)
               VALUES (?, ?, ?, ?, ?, ?, ?)
           """, [
               (e.event_type.value, e.worker_id, e.task_id, e.run_id, 
                e.workstream_id, e.timestamp.isoformat(), 
                json.dumps(e.payload) if e.payload else None)
               for e in self.batch
           ])
           
           conn.commit()
           conn.close()
           
           self.batch.clear()
   ```

3. **Scheduler Optimization**
   ```python
   # core/engine/scheduler.py (optimize)
   
   # Cache dependency graph
   @lru_cache(maxsize=1)
   def _build_dependency_graph_cached(bundles_tuple):
       """Cached dependency graph building."""
       return build_dependency_graph(list(bundles_tuple))
   
   # Parallel graph analysis
   from concurrent.futures import ThreadPoolExecutor
   
   def detect_parallel_opportunities_fast(bundles, max_workers=4):
       """Parallel analysis of opportunities."""
       with ThreadPoolExecutor(max_workers=4) as executor:
           # Analyze levels in parallel
           futures = []
           for level in levels:
               future = executor.submit(_analyze_level, level, bundles)
               futures.append(future)
           
           results = [f.result() for f in futures]
       
       return results
   ```

#### Acceptance Criteria

- [ ] Database queries < 50ms
- [ ] Event batching reduces writes by 90%
- [ ] Scheduler overhead < 100ms for 50 workstreams
- [ ] Memory usage < 500MB for 100 workstreams
- [ ] Performance benchmarks documented

#### Files Changed
- `core/state/db.py` - Connection pooling
- `core/engine/event_bus.py` - Batching
- `core/engine/scheduler.py` - Caching
- `tests/test_performance.py` (new)

---

### Workstream WS-I11: Production Hardening

**Priority**: High  
**Estimated Time**: 8-10 hours  

#### Tasks

1. **Error Handling & Retries**
   ```python
   # core/engine/executor.py (extend)
   
   from tenacity import retry, stop_after_attempt, wait_exponential
   
   @retry(
       stop=stop_after_attempt(3),
       wait=wait_exponential(multiplier=1, min=4, max=10)
   )
   def execute_task_with_retry(
       worker_id: str,
       bundle: WorkstreamBundle
   ) -> Dict[str, Any]:
       """Execute task with automatic retry."""
       try:
           return execute_task(worker_id, bundle)
       except TimeoutError:
           # Don't retry timeouts
           raise
       except Exception as e:
           # Log and retry
           print(f"Task {bundle.id} failed: {e}, retrying...")
           raise
   ```

2. **Health Checks**
   ```python
   # scripts/health_check.py (new)
   
   def health_check() -> Dict[str, Any]:
       """Check system health."""
       checks = {
           'database': _check_database(),
           'workers': _check_workers(),
           'disk_space': _check_disk_space(),
           'memory': _check_memory()
       }
       
       return {
           'healthy': all(c['ok'] for c in checks.values()),
           'checks': checks
       }
   
   def _check_database() -> Dict[str, Any]:
       """Check database connectivity."""
       try:
           conn = get_connection()
           conn.execute("SELECT 1")
           conn.close()
           return {'ok': True}
       except Exception as e:
           return {'ok': False, 'error': str(e)}
   ```

3. **Graceful Shutdown**
   ```python
   # core/engine/orchestrator.py (extend)
   
   import signal
   
   def setup_signal_handlers(worker_pool: WorkerPool):
       """Setup graceful shutdown on signals."""
       
       def shutdown_handler(signum, frame):
           print("\n⚠️  Graceful shutdown initiated...")
           
           # Drain all workers
           for worker_id in worker_pool.workers:
               worker_pool.drain_worker(worker_id)
           
           # Wait for in-progress tasks
           timeout = 300  # 5 minutes
           start = time.time()
           
           while time.time() - start < timeout:
               busy_workers = [
                   w for w in worker_pool.workers.values()
                   if w.state == WorkerState.BUSY
               ]
               
               if not busy_workers:
                   break
               
               print(f"Waiting for {len(busy_workers)} workers to finish...")
               time.sleep(5)
           
           # Terminate remaining
           for worker_id in worker_pool.workers:
               worker_pool.terminate_worker(worker_id)
           
           print("✅ Shutdown complete")
           sys.exit(0)
       
       signal.signal(signal.SIGINT, shutdown_handler)
       signal.signal(signal.SIGTERM, shutdown_handler)
   ```

#### Acceptance Criteria

- [ ] Retries work for transient failures
- [ ] Health checks pass
- [ ] Graceful shutdown completes in-progress work
- [ ] Signal handlers catch SIGINT/SIGTERM
- [ ] No data loss on shutdown
- [ ] Production deployment successful

#### Files Changed
- `core/engine/executor.py` - Retry logic
- `scripts/health_check.py` (new)
- `core/engine/orchestrator.py` - Signal handlers
- `tests/test_production_hardening.py` (new)

---

### Workstream WS-I12: Documentation & Training

**Priority**: Medium  
**Estimated Time**: 6-8 hours  

#### Tasks

1. **User Guide**
   ```markdown
   # docs/UET_USER_GUIDE.md
   
   # UET Parallel Execution User Guide
   
   ## Quick Start
   
   ### 1. Validate Your Plan
   
   \`\`\`bash
   python scripts/validate_plan.py --workstreams-dir workstreams
   \`\`\`
   
   ### 2. Run in Parallel
   
   \`\`\`bash
   python scripts/run_workstream.py --parallel --max-workers 4
   \`\`\`
   
   ### 3. Monitor Execution
   
   \`\`\`bash
   python scripts/monitor_execution.py <run-id>
   \`\`\`
   
   ## Configuration
   
   ### Budget Limits
   
   Edit `config/budget.yaml`:
   
   \`\`\`yaml
   default:
     max_cost_total: 100.0
     max_cost_per_task: 5.0
   \`\`\`
   
   ## Troubleshooting
   
   ### Crash Recovery
   
   If orchestrator crashes:
   
   \`\`\`bash
   python scripts/run_workstream.py --resume
   \`\`\`
   ```

2. **API Documentation**
   ```python
   # Generate API docs
   # scripts/generate_api_docs.py
   
   import pdoc
   
   modules = [
       'core.engine.orchestrator',
       'core.engine.scheduler',
       'core.engine.worker',
       'core.planning.parallelism_detector'
   ]
   
   pdoc.pdoc(*modules, output_directory='docs/api')
   ```

3. **Migration Guide**
   ```markdown
   # docs/MIGRATION_TO_PARALLEL.md
   
   # Migrating to Parallel Execution
   
   ## Step 1: Add UET Metadata
   
   Update your workstream bundles:
   
   \`\`\`json
   {
     "id": "ws-example",
     "parallel_ok": true,
     "estimated_context_tokens": 50000,
     "max_cost_usd": 2.0,
     "test_gates": [
       {"type": "GATE_LINT", "required": true, "blocking": true}
     ]
   }
   \`\`\`
   
   ## Step 2: Run Migration
   
   \`\`\`bash
   sqlite3 state/pipeline_state.db < schema/migrations/002_uet_foundation.sql
   \`\`\`
   
   ## Step 3: Test with Dry-Run
   
   \`\`\`bash
   python scripts/validate_plan.py --dry-run
   \`\`\`
   ```

#### Acceptance Criteria

- [ ] User guide covers all features
- [ ] API documentation generated
- [ ] Migration guide tested
- [ ] Example workstreams provided
- [ ] Troubleshooting section complete

#### Files Changed
- `docs/UET_USER_GUIDE.md` (new)
- `docs/UET_API_REFERENCE.md` (new)
- `docs/MIGRATION_TO_PARALLEL.md` (new)
- `scripts/generate_api_docs.py` (new)

---

## Testing Strategy

### Unit Tests
- All new modules have 80%+ coverage
- Worker lifecycle tests
- Scheduler tests
- Event bus tests
- Cost tracking tests
- Gate enforcement tests

### Integration Tests
- End-to-end parallel execution
- Crash recovery scenarios
- Merge conflict handling
- Budget enforcement
- Gate failures

### Performance Tests
- 10 workstreams: < 5 seconds overhead
- 50 workstreams: < 30 seconds overhead
- 100 workstreams: < 60 seconds overhead
- Memory usage stable
- No memory leaks

### Chaos Tests
- Kill orchestrator mid-execution
- Kill worker processes
- Simulate network failures
- Database corruption scenarios

---

## Deployment Plan

### Week 9: Staging Deployment

1. Deploy to staging environment
2. Run Phase G workstreams in parallel
3. Monitor metrics and events
4. Validate crash recovery
5. Test budget enforcement

### Week 10: Production Rollout

1. Canary deployment (10% of workstreams)
2. Monitor for 48 hours
3. Gradual rollout (25%, 50%, 100%)
4. Full production deployment
5. Performance validation

### Post-Deployment

1. Monitor metrics daily for 2 weeks
2. Tune budget limits based on actual costs
3. Optimize worker pool sizes
4. Document lessons learned

---

## Success Metrics

### Quantitative

- ✅ **Execution Speedup**: 40-50% reduction in wall-clock time (3.0x theoretical)
- ✅ **Cost Accuracy**: Token estimates within 10% of actual
- ✅ **Crash Recovery**: < 5 minutes to restore
- ✅ **Test Coverage**: > 80% for all new code
- ✅ **Performance**: < 100ms scheduler overhead

### Qualitative

- ✅ **Reliability**: Zero data loss in crash scenarios
- ✅ **Observability**: Real-time monitoring works
- ✅ **Developer Experience**: Simple CLI commands
- ✅ **Documentation**: Comprehensive and clear

---

## Risk Mitigation

### High Risks

1. **Worker Process Management**
   - **Risk**: Process spawning failures, zombie processes
   - **Mitigation**: Health checks, automatic cleanup, retries
   - **Fallback**: Fall back to sequential execution

2. **Merge Conflicts**
   - **Risk**: Complex conflicts block integration
   - **Mitigation**: Conservative conflict detection, human escalation
   - **Fallback**: Manual merge workflow

### Medium Risks

3. **Performance**
   - **Risk**: Parallel overhead negates speedup
   - **Mitigation**: Performance testing, optimization
   - **Fallback**: Adjust worker pool size

4. **Database Locking**
   - **Risk**: SQLite locks under high concurrency
   - **Mitigation**: Connection pooling, batching
   - **Fallback**: Migrate to PostgreSQL

### Low Risks

5. **Budget Overruns**
   - **Risk**: Unexpected cost spikes
   - **Mitigation**: Conservative limits, monitoring
   - **Fallback**: Manual budget approval

---

## Dependencies

### External
- ✅ Python 3.10+
- ✅ SQLite 3.35+
- ✅ Git 2.30+
- ✅ Aider (latest)
- ⚠️ Sufficient disk space for worker sandboxes

### Internal
- ✅ Phase H complete (UET framework)
- ✅ Error pipeline operational
- ✅ Worktree support functional

---

## Future Enhancements (Post Phase I)

### Phase J: Advanced Parallelism
- Dynamic worker scaling
- Multi-machine distribution
- GPU worker support
- Workflow engine integration (Prefect/Temporal)

### Phase K: AI Optimization
- ML-based cost prediction
- Automatic bottleneck detection
- Intelligent workstream grouping
- Adaptive parallelism tuning

---

## Appendix A: File Inventory

### New Files (Est. 30-35)

**Core Engine**
- `core/engine/orchestrator.py` (extend with parallel mode)
- `core/engine/progress.py`
- `core/engine/test_gates.py`
- `core/engine/context_pruner.py` (complete)

**Scripts**
- `scripts/monitor_execution.py`
- `scripts/generate_report.py`
- `scripts/health_check.py`
- `scripts/generate_api_docs.py`

**Tests** (20+ files)
- `tests/test_parallel_orchestrator.py`
- `tests/test_worker_spawning.py`
- `tests/test_integration_worker.py`
- `tests/test_crash_recovery_integration.py`
- `tests/test_budget_enforcement.py`
- `tests/test_gate_enforcement.py`
- `tests/test_context_optimization.py`
- `tests/test_reporting.py`
- `tests/test_performance.py`
- `tests/test_production_hardening.py`

**Documentation**
- `docs/UET_USER_GUIDE.md`
- `docs/UET_API_REFERENCE.md`
- `docs/MIGRATION_TO_PARALLEL.md`

**Configuration**
- `config/budget.yaml`

**Database**
- `schema/migrations/003_execution_checkpoints.sql`

### Modified Files (10+)
- `core/engine/orchestrator.py` - Parallel execution
- `core/engine/worker.py` - Process spawning
- `core/engine/scheduler.py` - Optimizations
- `core/engine/integration_worker.py` - Complete
- `core/engine/budget_policy.py` - Complete
- `core/engine/event_bus.py` - Batching
- `core/state/db.py` - Connection pooling
- `scripts/run_workstream.py` - Parallel flag
- `schema/schema.sql` - Checkpoints table

---

## Appendix B: Workstream Summary

| ID | Name | Duration | Priority | Dependencies |
|----|------|----------|----------|--------------|
| WS-I1 | Orchestrator Integration | 12-15h | Critical | Phase H |
| WS-I2 | Worker Spawning | 10-12h | Critical | WS-I1 |
| WS-I3 | Event Monitoring | 6-8h | High | WS-I1 |
| WS-I4 | Integration Worker | 12-15h | Critical | WS-I1 |
| WS-I5 | Crash Recovery | 8-10h | High | WS-I1 |
| WS-I6 | Budget Enforcement | 6-8h | Medium | WS-I1 |
| WS-I7 | Test Gates | 8-10h | Medium | WS-I2 |
| WS-I8 | Context Optimization | 6-8h | Low | WS-I2 |
| WS-I9 | Metrics & Reporting | 6-8h | Medium | WS-I1 |
| WS-I10 | Performance Optimization | 8-10h | Medium | All |
| WS-I11 | Production Hardening | 8-10h | High | All |
| WS-I12 | Documentation | 6-8h | Medium | All |

**Total Estimated Time**: 96-119 hours (8-10 weeks at 12 hours/week)

---

## Appendix C: CLI Commands Reference

### Execution
```bash
# Sequential (existing)
python scripts/run_workstream.py --workstreams-dir workstreams

# Parallel (new)
python scripts/run_workstream.py --parallel --max-workers 4

# Dry-run validation
python scripts/validate_plan.py --workstreams-dir workstreams

# Resume after crash
python scripts/run_workstream.py --resume --run-id <run-id>
```

### Monitoring
```bash
# Real-time dashboard
python scripts/monitor_execution.py <run-id>

# View events
python scripts/view_events.py --run-id <run-id> --tail 50

# Health check
python scripts/health_check.py
```

### Reporting
```bash
# Generate execution report
python scripts/generate_report.py --run-id <run-id> --output report.html

# Compare runs
python scripts/compare_runs.py <run-id-1> <run-id-2>

# Cost breakdown
python scripts/cost_report.py --run-id <run-id>
```

---

**End of Phase I Plan**

**Next Steps**: 
1. Review with team
2. Create workstream bundles for WS-I1 through WS-I12
3. Set up staging environment
4. Begin implementation of WS-I1

**Questions/Concerns**:
- Worker pool size tuning methodology
- PostgreSQL migration trigger point
- Budget limit policy approvals
- Production deployment schedule
