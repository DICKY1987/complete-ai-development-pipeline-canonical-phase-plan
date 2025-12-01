# 🚀 UET Framework Workstream Execution - Phase Plan

**DOC_ID**: DOC-PLAN-UET-WORKSTREAM-EXEC-001  
**Created**: 2025-11-30T01:58:00Z  
**Status**: READY_FOR_EXECUTION  
**Based On**: UET V2 Component Contracts, DAG Scheduler, State Machines, Integration Points  
**Target**: Execute 37 workstreams using UET Framework with patterns  
**Execution Model**: DAG-based parallel execution with 3 workers  
**Estimated Duration**: 3-5 days wall-clock time  
**Total Effort**: 30 hours sequential → 10 hours with 3 workers (67% savings)

---

## Executive Summary

Execute 37 refactoring workstreams using the **Universal Execution Templates Framework** with:
- **DAG-based dependency resolution** (automatic wave detection)
- **Parallel execution** (3 workers simultaneously)
- **State machine tracking** (full lifecycle management)
- **Patch ledger system** (conflict-free merging)
- **Execution patterns** (EXEC-001 through EXEC-013)

**Current State**:
- 37 valid workstreams in `workstreams/`
- UET Framework 78% complete
- All core components available

**Target State**:
- All 37 workstreams executed
- Changes integrated via patch ledger
- Zero merge conflicts (worktree isolation)
- Complete execution telemetry

---

## Phase Structure

```
PHASE 0: UET Setup & Bootstrap        [1 hour]   [WS-SETUP-001 to WS-SETUP-003]
PHASE 1: Workstream Discovery         [30 min]   [WS-DISC-001]
PHASE 2: DAG Construction             [30 min]   [WS-DAG-001]
PHASE 3: Wave Execution (8 waves)     [8 hours]  [37 workstreams] ← PARALLEL
PHASE 4: Integration & Merge          [1 hour]   [WS-INT-001 to WS-INT-003]
PHASE 5: Verification & Commit        [30 min]   [WS-VER-001 to WS-VER-002]
```

**Total**: 11.5 hours sequential → **4 hours wall time** with 3 workers

---

## Execution Patterns Used

### Primary Patterns
- **EXEC-001**: Batch File Operations (config creation)
- **EXEC-012**: Module Consolidation (workstream execution)
- **EXEC-013**: Dependency Mapper (DAG construction)
- **DAG-based Wave Execution** (parallel tasks)
- **Patch Ledger Integration** (conflict-free merging)
- **State Machine Tracking** (full lifecycle)

### Anti-Pattern Guards (ALL ENABLED)
✅ No Hallucination of Success (verify SQLite state)  
✅ No Planning Loops (execute immediately)  
✅ No Incomplete Implementation (no TODO/pass stubs)  
✅ Explicit Error Handling (all exceptions caught)  
✅ Ground Truth Verification (file exists, tests pass)  
✅ No Approval Loops (automated execution)

---

## PHASE 0: UET Setup & Bootstrap (1 hour)

### WS-SETUP-001: Create UET Configuration
**Type**: Setup  
**Dependencies**: None  
**Execution Pattern**: EXEC-001 (Batch File Creator)  
**Duration**: 20 minutes  
**Agent**: Manual/Copilot

**Objective**: Create UET configuration and directory structure

**Tasks**:
```yaml
tasks:
  - id: WS-SETUP-001-T01
    action: create_directory_structure
    paths:
      - .uet/
      - .state/
      - logs/uet/
      - .worktrees/
    
  - id: WS-SETUP-001-T02
    action: create_file
    path: .uet/config.yaml
    content: |
      project:
        name: "AI Development Pipeline"
        type: "software-dev-python"
        root: "."
      
      execution:
        max_workers: 3
        retry_policy:
          max_retries: 2
          backoff_seconds: 5
        
        workstream_dir: "workstreams"
        workstream_pattern: "ws-*.json"
        
        state_db: ".state/uet_execution.db"
        log_dir: "logs/uet"
        
        default_tool: "aider"
        tool_config:
          aider:
            model: "gpt-4"
            auto_commit: false
          codex:
            mode: "interactive"
      
      isolation:
        strategy: "worktree"  # git worktrees for isolation
        worktree_dir: ".worktrees"
      
      adapters:
        enabled:
          - aider
          - codex
          - git
          - tests
        
        routing:
          - pattern: "*.py"
            tool: "aider"
          - pattern: "*.md"
            tool: "codex"
          - pattern: "test_*.py"
            tool: "tests"
      
      state_machines:
        run: "UET_RUN_STATE_MACHINE"
        step: "UET_STEP_STATE_MACHINE"
        worker: "UET_WORKER_STATE_MACHINE"
        patch: "UET_PATCH_STATE_MACHINE"
      
      dag:
        enabled: true
        max_wave_parallelism: 3
        topological_sort: "kahn"
```

**Ground Truth Success**:
```bash
test -f .uet/config.yaml && echo "✅ PASS" || echo "❌ FAIL"
test -d .state && echo "✅ PASS" || echo "❌ FAIL"
test -d .worktrees && echo "✅ PASS" || echo "❌ FAIL"
```

---

### WS-SETUP-002: Initialize Database Schema
**Type**: Setup  
**Dependencies**: WS-SETUP-001  
**Execution Pattern**: State Machine DB Setup  
**Duration**: 20 minutes  
**Agent**: Python script

**Objective**: Create SQLite schema for all state machines

**Implementation**:
```python
# File: scripts/uet_init_db.py
import sqlite3
from pathlib import Path

def init_uet_database(db_path: Path):
    """Initialize UET execution database with all required tables."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Runs table (UET_RUN_STATE_MACHINE)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS runs (
        run_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        phase_id TEXT NOT NULL,
        workstream_id TEXT,
        state TEXT NOT NULL CHECK(state IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        started_at TEXT,
        completed_at TEXT,
        metadata TEXT  -- JSON
    )
    """)
    
    # Steps table (UET_STEP_STATE_MACHINE)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS steps (
        step_id TEXT PRIMARY KEY,
        run_id TEXT NOT NULL,
        step_kind TEXT NOT NULL,
        state TEXT NOT NULL CHECK(state IN ('pending', 'running', 'completed', 'failed', 'skipped')),
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        started_at TEXT,
        completed_at TEXT,
        duration_seconds REAL,
        metadata TEXT,  -- JSON
        FOREIGN KEY (run_id) REFERENCES runs(run_id)
    )
    """)
    
    # Workers table (UET_WORKER_STATE_MACHINE)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workers (
        worker_id TEXT PRIMARY KEY,
        worker_type TEXT NOT NULL,
        state TEXT NOT NULL CHECK(state IN ('SPAWNING', 'IDLE', 'BUSY', 'DRAINING', 'TERMINATED')),
        affinity TEXT,  -- JSON
        last_heartbeat TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        terminated_at TEXT,
        CHECK ((state = 'TERMINATED' AND terminated_at IS NOT NULL) OR (state != 'TERMINATED' AND terminated_at IS NULL))
    )
    """)
    
    # Patches table (UET_PATCH_STATE_MACHINE)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patches (
        ledger_id TEXT PRIMARY KEY,
        step_id TEXT NOT NULL,
        patch_file_path TEXT NOT NULL,
        state TEXT NOT NULL CHECK(state IN ('created', 'validated', 'queued', 'applied', 'apply_failed', 'verified', 'committed', 'rolled_back', 'quarantined', 'dropped')),
        scope_files TEXT,  -- JSON array
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        applied_at TEXT,
        committed_at TEXT,
        metadata TEXT,  -- JSON
        FOREIGN KEY (step_id) REFERENCES steps(step_id)
    )
    """)
    
    # Tasks table (DAG Scheduler)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        task_id TEXT PRIMARY KEY,
        run_id TEXT NOT NULL,
        task_kind TEXT NOT NULL,
        depends_on TEXT,  -- JSON array
        state TEXT NOT NULL CHECK(state IN ('pending', 'ready', 'running', 'completed', 'failed', 'blocked')),
        worker_id TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        started_at TEXT,
        completed_at TEXT,
        metadata TEXT,  -- JSON
        FOREIGN KEY (run_id) REFERENCES runs(run_id),
        FOREIGN KEY (worker_id) REFERENCES workers(worker_id)
    )
    """)
    
    # Events table (Event Bus)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT NOT NULL,
        run_id TEXT,
        step_id TEXT,
        timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        data TEXT  -- JSON
    )
    """)
    
    # Indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_steps_run_id ON steps(run_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_run_id ON tasks(run_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_state ON tasks(state)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_workers_state ON workers(state)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_patches_state ON patches(state)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_run_id ON events(run_id)")
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized: {db_path}")

if __name__ == "__main__":
    db_path = Path(".state/uet_execution.db")
    db_path.parent.mkdir(exist_ok=True)
    init_uet_database(db_path)
```

**Ground Truth Success**:
```bash
sqlite3 .state/uet_execution.db "SELECT name FROM sqlite_master WHERE type='table'" | grep -q "runs" && echo "✅ PASS"
```

---

### WS-SETUP-003: Initialize Worker Pool
**Type**: Setup  
**Dependencies**: WS-SETUP-002  
**Execution Pattern**: Worker Lifecycle Bootstrap  
**Duration**: 20 minutes  
**Agent**: Python script

**Objective**: Spawn 3 workers in IDLE state

**Implementation**:
```python
# File: scripts/uet_spawn_workers.py
import sqlite3
from pathlib import Path
from datetime import datetime
import uuid

def spawn_workers(db_path: Path, worker_count: int = 3):
    """Spawn initial worker pool."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    workers_created = []
    
    for i in range(worker_count):
        worker_id = f"worker-{i+1:03d}"
        
        cursor.execute("""
        INSERT INTO workers (worker_id, worker_type, state, affinity, last_heartbeat)
        VALUES (?, 'general', 'IDLE', '{}', ?)
        """, (worker_id, datetime.utcnow().isoformat()))
        
        workers_created.append(worker_id)
        print(f"✅ Spawned worker: {worker_id}")
    
    conn.commit()
    conn.close()
    
    return workers_created

if __name__ == "__main__":
    db_path = Path(".state/uet_execution.db")
    workers = spawn_workers(db_path, worker_count=3)
    print(f"\n✅ Worker pool initialized: {len(workers)} workers")
```

**Ground Truth Success**:
```bash
sqlite3 .state/uet_execution.db "SELECT COUNT(*) FROM workers WHERE state='IDLE'" | grep -q "3" && echo "✅ PASS"
```

---

## PHASE 1: Workstream Discovery (30 min)

### WS-DISC-001: Load and Validate Workstreams
**Type**: Discovery  
**Dependencies**: WS-SETUP-003  
**Execution Pattern**: EXEC-013 (Dependency Analysis)  
**Duration**: 30 minutes  
**Agent**: Python script

**Objective**: Load all workstreams and extract dependency graph

**Implementation**: See `UET_WORKSTREAM_QUICKSTART.md` - already documented

**Expected**: 37 workstreams loaded, 12 JSON errors (ignorable)

---

## PHASE 2: DAG Construction (30 min)

### WS-DAG-001: Build Execution DAG
**Type**: Planning  
**Dependencies**: WS-DISC-001  
**Execution Pattern**: DAG Scheduler (Topological Sort)  
**Duration**: 30 minutes  
**Agent**: DAG Builder

**Objective**: Create wave-based execution plan

**Expected Output**:
```
Wave 1: 7 workstreams (no dependencies)
Wave 2: 8 workstreams (depend on Wave 1)
Wave 3: 6 workstreams
...
Wave 8: 3 workstreams (final integration)

Total: 8 waves, 37 workstreams
```

---

## PHASE 3: Wave Execution (8 hours → 3 hours with 3 workers)

### Execution Strategy

**Per Wave**:
1. Get all `ready` tasks from scheduler
2. Assign to IDLE workers (max 3 parallel)
3. Create worktree for each worker
4. Execute tool (aider/codex) in isolated worktree
5. Capture patch output to ledger
6. Mark task complete, worker IDLE
7. Move to next wave when all tasks done

### State Transitions

**Task**: `pending → ready → running → completed`  
**Worker**: `IDLE → BUSY → IDLE`  
**Patch**: `created → validated → queued`

### Example Wave 1 Execution

```python
# Pseudo-code for wave execution
async def execute_wave(wave_tasks, workers):
    for task in wave_tasks:
        worker = get_idle_worker()
        
        # Transition states
        task.state = 'running'
        worker.state = 'BUSY'
        
        # Create isolated worktree
        worktree = create_worktree(worker.id, task.id)
        
        # Execute tool
        result = await execute_tool(
            tool=task.tool,
            files=task.files,
            instructions=task.instructions,
            cwd=worktree
        )
        
        # Capture patch
        if result.patch_file:
            patch_id = create_patch_ledger_entry(
                step_id=task.id,
                patch_file=result.patch_file,
                state='created'
            )
        
        # Complete task
        task.state = 'completed'
        worker.state = 'IDLE'
        
        # Cleanup worktree
        remove_worktree(worker.id)
```

---

## PHASE 4: Integration & Merge (1 hour)

### WS-INT-001: Collect Validated Patches
**Dependencies**: All Wave 8 tasks complete  
**Duration**: 10 minutes

Query patch ledger for all `validated` patches, order by priority.

### WS-INT-002: Sequential Merge
**Dependencies**: WS-INT-001  
**Duration**: 40 minutes

Apply patches one at a time:
1. Validate scope
2. `git apply` patch
3. Run validators (ruff, black, pytest)
4. Transition `validated → applied → verified`
5. Rollback if validation fails

### WS-INT-003: Final Commit
**Dependencies**: WS-INT-002  
**Duration**: 10 minutes

Commit all verified patches to main branch, transition to `committed`.

---

## PHASE 5: Verification & Commit (30 min)

### WS-VER-001: Run Full Test Suite
**Duration**: 20 minutes

```bash
pytest tests/ -v --tb=short
```

### WS-VER-002: Generate Report
**Duration**: 10 minutes

Query database for execution metrics, generate completion report.

---

## Key Files Created

1. `.uet/config.yaml` - Configuration
2. `scripts/uet_init_db.py` - Database initialization
3. `scripts/uet_spawn_workers.py` - Worker pool setup
4. `scripts/run_uet_workstreams.py` - Main orchestrator
5. `.state/uet_execution.db` - Execution state
6. `logs/uet/*.log` - Execution logs
7. `UET_EXECUTION_REPORT.md` - Final report

---

## Success Criteria

✅ All 37 workstreams executed  
✅ Zero merge conflicts (worktree isolation)  
✅ All patches verified and committed  
✅ Full test suite passing  
✅ Complete execution telemetry  
✅ Wall-clock time < 5 days

---

## Next Steps

1. **Create setup scripts** (Phase 0)
2. **Initialize database** (Phase 0)
3. **Run orchestrator** (Phases 1-5)
4. **Monitor progress** (query SQLite)
5. **Review results** (execution report)

---

**Ready to execute?** 

**Start**: `python scripts/uet_init_db.py && python scripts/run_uet_workstreams.py`
