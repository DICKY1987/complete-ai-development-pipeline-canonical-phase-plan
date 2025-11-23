# PHASE UET: Universal Execution Templates Integration

**Phase ID**: PH-UET  
**Created**: 2025-11-23  
**Status**: PLANNING  
**Duration**: 9-10 weeks (7 weeks MVP)  
**Estimated Cost**: $150-200 (AI token usage)

---

## 0. Phase Overview

### Purpose

Align the production pipeline with the Universal Execution Templates (UET) Framework by implementing:

1. **Worker Lifecycle Management** (UET_EXECUTION_KERNEL_PARALLELISM_STRATEGY_SPEC_V2)
   - Worker states, health checks, integration worker
   - Merge strategy, test gates, human review, rollback

2. **Patch Management System** (UET_PATCH_MANAGEMENT_SPEC)
   - PatchArtifact, PatchLedgerEntry, PatchPolicy
   - State machine, validation pipeline

3. **Patch-First Workflow** (Unified Diff & Optimal)
   - Unified diff only, no direct file edits
   - Language-aware validation (Python, PowerShell)
   - Task mode support (prompt, patch_review, patch_apply_validate)

### Success Criteria

- ✅ All 17 UET schemas copied to `schema/uet/`
- ✅ Patch ledger with full state machine (created → committed)
- ✅ Event bus with persistence to `run_events` table
- ✅ Worker lifecycle with health checks and quarantine
- ✅ DAG scheduler replacing current sequential scheduler
- ✅ Patch-first adapters (all tools output unified diffs)
- ✅ Test gates enforced (LINT, UNIT, INTEGRATION)
- ✅ Cost tracking with budget enforcement
- ✅ Compensation engine (Saga pattern rollback)

### Current State

**~40% UET-aligned** - Many components exist but need alignment:
- ✅ Worker lifecycle (80% - has states, needs health checks)
- ✅ Event bus (85% - has events, needs persistence)
- ✅ Patch manager (50% - basic parsing, needs ledger)
- ✅ Cost tracker (75% - needs per-phase tracking)
- ❌ Adapters (direct edits - needs patch-first refactor)
- ❌ ULIDs (using auto-increment IDs)
- ❌ Schema validation (not enforced)

---

## 1. Phase A: Quick Wins (Week 1-2)

**Duration**: 1-2 weeks  
**Goal**: Low-risk, high-value improvements  
**Estimated Cost**: $20

### Workstream WS-UET-A1: Schema Foundation

**Priority**: CRITICAL (blocks all other work)  
**Duration**: 2 hours  
**Files Created**:
- `schema/uet/patch_artifact.v1.json`
- `schema/uet/patch_ledger_entry.v1.json`
- `schema/uet/patch_policy.v1.json`
- `schema/uet/phase_spec.v1.json`
- `schema/uet/workstream_spec.v1.json`
- `schema/uet/task_spec.v1.json`
- `schema/uet/execution_request.v1.json`
- `schema/uet/run_record.v1.json`
- `schema/uet/run_event.v1.json`
- ... (17 total)

**Tasks**:
```json
{
  "step_id": "uet-a1-01",
  "name": "Copy UET Schemas to Production",
  "description": "Copy all 17 JSON schemas from UET Framework to production",
  "command": "Copy-Item UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\\schema\\*.json schema\\uet\\",
  "validation": {
    "command": "Test-Path schema/uet/*.json",
    "expected": "17 files"
  }
}
```

---

### Workstream WS-UET-A2: Worker Health Checks

**Priority**: HIGH  
**Duration**: 4 hours  
**Files Created**: `core/engine/worker_health.py`  
**Files Modified**: `core/engine/worker.py`

**Implementation**:

```python
# core/engine/worker_health.py
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

@dataclass
class HealthCheck:
    """Worker health check result."""
    worker_id: str
    healthy: bool
    last_heartbeat: datetime
    error_count: int
    last_error: Optional[str] = None
    checked_at: datetime = None
    
    def __post_init__(self):
        if self.checked_at is None:
            self.checked_at = datetime.now(timezone.utc)

class WorkerHealthMonitor:
    """Monitors worker health via heartbeat."""
    
    def __init__(self, heartbeat_timeout_sec: int = 300):
        """Initialize health monitor.
        
        Args:
            heartbeat_timeout_sec: Seconds before worker considered unhealthy
        """
        self.heartbeat_timeout_sec = heartbeat_timeout_sec
        self.health_checks: dict[str, HealthCheck] = {}
    
    def record_heartbeat(self, worker_id: str) -> None:
        """Record worker heartbeat."""
        if worker_id not in self.health_checks:
            self.health_checks[worker_id] = HealthCheck(
                worker_id=worker_id,
                healthy=True,
                last_heartbeat=datetime.now(timezone.utc),
                error_count=0
            )
        else:
            self.health_checks[worker_id].last_heartbeat = datetime.now(timezone.utc)
            self.health_checks[worker_id].healthy = True
    
    def record_error(self, worker_id: str, error: str) -> None:
        """Record worker error."""
        if worker_id in self.health_checks:
            self.health_checks[worker_id].error_count += 1
            self.health_checks[worker_id].last_error = error
    
    def check_health(self, worker_id: str) -> HealthCheck:
        """Check if worker is healthy."""
        if worker_id not in self.health_checks:
            return HealthCheck(
                worker_id=worker_id,
                healthy=False,
                last_heartbeat=datetime.min.replace(tzinfo=timezone.utc),
                error_count=0,
                last_error="No heartbeat recorded"
            )
        
        check = self.health_checks[worker_id]
        timeout = timedelta(seconds=self.heartbeat_timeout_sec)
        elapsed = datetime.now(timezone.utc) - check.last_heartbeat
        
        check.healthy = elapsed < timeout
        check.checked_at = datetime.now(timezone.utc)
        
        return check
    
    def quarantine_worker(self, worker_id: str) -> None:
        """Mark worker as quarantined (unhealthy)."""
        if worker_id in self.health_checks:
            self.health_checks[worker_id].healthy = False
```

**Tasks**:
1. Create `core/engine/worker_health.py`
2. Add heartbeat monitoring to `WorkerPool`
3. Add quarantine logic for unhealthy workers
4. Unit tests in `tests/engine/test_worker_health.py`

**Validation**:
```bash
pytest tests/engine/test_worker_health.py -v
```

---

### Workstream WS-UET-A3: Event Persistence

**Priority**: HIGH  
**Duration**: 4 hours  
**Files Modified**:
- `core/engine/event_bus.py`
- `core/state/db.py`
- `schema/schema.sql`

**Database Schema**:

```sql
-- Add to schema/schema.sql
CREATE TABLE IF NOT EXISTS run_events (
    event_id TEXT PRIMARY KEY,          -- ULID
    run_id TEXT NOT NULL,
    event_type TEXT NOT NULL,           -- EventType enum value
    timestamp TEXT NOT NULL,            -- ISO 8601
    payload TEXT,                       -- JSON
    source TEXT,                        -- worker_id, task_id, etc.
    FOREIGN KEY (run_id) REFERENCES runs(run_id)
);

CREATE INDEX idx_run_events_run_id ON run_events(run_id);
CREATE INDEX idx_run_events_timestamp ON run_events(timestamp);
CREATE INDEX idx_run_events_type ON run_events(event_type);
```

**Implementation**:

```python
# core/engine/event_bus.py (enhance existing)
import json
from ulid import ULID
from core.state.db import get_connection

class EventBus:
    """Enhanced event bus with persistence."""
    
    def emit(self, event_type: EventType, run_id: str, payload: dict, source: str = None):
        """Emit event and persist to database."""
        event_id = str(ULID())
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Persist to database
        conn = get_connection()
        try:
            conn.execute("""
                INSERT INTO run_events (event_id, run_id, event_type, timestamp, payload, source)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (event_id, run_id, event_type.value, timestamp, json.dumps(payload), source))
            conn.commit()
        finally:
            conn.close()
        
        # Also emit to subscribers (existing logic)
        self._notify_subscribers(event_type, payload)
    
    def get_events(self, run_id: str, event_type: EventType = None) -> list[dict]:
        """Retrieve events for a run."""
        conn = get_connection()
        try:
            if event_type:
                cursor = conn.execute("""
                    SELECT event_id, event_type, timestamp, payload, source
                    FROM run_events
                    WHERE run_id = ? AND event_type = ?
                    ORDER BY timestamp
                """, (run_id, event_type.value))
            else:
                cursor = conn.execute("""
                    SELECT event_id, event_type, timestamp, payload, source
                    FROM run_events
                    WHERE run_id = ?
                    ORDER BY timestamp
                """, (run_id,))
            
            events = []
            for row in cursor.fetchall():
                events.append({
                    'event_id': row[0],
                    'event_type': row[1],
                    'timestamp': row[2],
                    'payload': json.loads(row[3]) if row[3] else {},
                    'source': row[4]
                })
            return events
        finally:
            conn.close()
```

**Tasks**:
1. Add `run_events` table to schema
2. Enhance `EventBus.emit()` to persist events
3. Add `EventBus.get_events()` for retrieval
4. Add event replay for debugging
5. Unit tests

**Validation**:
```bash
pytest tests/engine/test_event_bus.py -v
python scripts/validate_db_schema.py
```

---

### Workstream WS-UET-A4: Feedback Loop

**Priority**: MEDIUM  
**Duration**: 8 hours  
**Files Created**: `core/engine/feedback_loop.py`

**Implementation**:

```python
# core/engine/feedback_loop.py
from dataclasses import dataclass
from typing import List, Optional
from core.engine.event_bus import EventBus, EventType

@dataclass
class FeedbackAction:
    """Action to take based on feedback."""
    action_type: str  # 'create_task', 'adjust_priority', 'quarantine'
    target_id: str
    payload: dict

class FeedbackLoop:
    """Test-driven execution with automatic fix task creation."""
    
    def __init__(self, event_bus: EventBus):
        """Initialize feedback loop.
        
        Args:
            event_bus: Event bus for listening to test results
        """
        self.event_bus = event_bus
        self.event_bus.subscribe(EventType.TASK_FAILED, self._on_task_failed)
        self.event_bus.subscribe(EventType.TOOL_FAILED, self._on_tool_failed)
    
    def _on_task_failed(self, event: dict) -> None:
        """Handle task failure event."""
        task_id = event.get('task_id')
        error_message = event.get('error_message', '')
        
        # Analyze failure type
        if 'test' in error_message.lower():
            # Test failure - create fix task
            self._create_fix_task(task_id, 'test_failure', error_message)
        elif 'lint' in error_message.lower():
            # Lint failure - create lint fix task
            self._create_fix_task(task_id, 'lint_failure', error_message)
    
    def _on_tool_failed(self, event: dict) -> None:
        """Handle tool failure event."""
        tool_id = event.get('tool_id')
        error_code = event.get('error_code')
        
        # Tool failures might indicate need for circuit breaker adjustment
        self.event_bus.emit(EventType.CIRCUIT_OPENED, {
            'tool_id': tool_id,
            'reason': f'Tool failure: {error_code}'
        })
    
    def _create_fix_task(self, failed_task_id: str, failure_type: str, error_message: str) -> str:
        """Create a fix task for failed task."""
        # This would integrate with task queue/scheduler
        fix_task = {
            'task_id': f"FIX-{failed_task_id}",
            'description': f"Fix {failure_type} in {failed_task_id}",
            'parent_task_id': failed_task_id,
            'error_context': error_message,
            'priority': 'HIGH'
        }
        
        # Emit task creation event
        self.event_bus.emit(EventType.TASK_CREATED, fix_task)
        
        return fix_task['task_id']
```

**Tasks**:
1. Create `core/engine/feedback_loop.py`
2. Subscribe to task failure events
3. Auto-create fix tasks on test failures
4. Prioritize based on failure impact
5. Unit tests

**Validation**:
```bash
pytest tests/engine/test_feedback_loop.py -v
```

---

### Workstream WS-UET-A5: Context Manager Enhancements

**Priority**: MEDIUM  
**Duration**: 8 hours  
**Files Created**: `core/engine/context_manager.py`  
**Files Modified**: `core/engine/context_estimator.py`

**Implementation**:

```python
# core/engine/context_manager.py
from dataclasses import dataclass
from typing import List, Optional
import tiktoken

@dataclass
class ContextWindow:
    """Context window configuration."""
    max_tokens: int
    current_tokens: int
    pruning_threshold: float = 0.8  # Prune at 80% capacity
    
    @property
    def available_tokens(self) -> int:
        return self.max_tokens - self.current_tokens
    
    @property
    def is_near_limit(self) -> bool:
        return (self.current_tokens / self.max_tokens) >= self.pruning_threshold

class ContextManager:
    """Manages context window with pruning/summarization/chunking."""
    
    def __init__(self, max_tokens: int = 200000, model: str = "gpt-4"):
        """Initialize context manager.
        
        Args:
            max_tokens: Maximum context window size
            model: Model name for token counting
        """
        self.max_tokens = max_tokens
        self.encoder = tiktoken.encoding_for_model(model)
        self.window = ContextWindow(max_tokens=max_tokens, current_tokens=0)
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        return len(self.encoder.encode(text))
    
    def add_to_context(self, text: str, section_id: str, priority: int = 5) -> bool:
        """Add text to context window.
        
        Args:
            text: Text to add
            section_id: Identifier for this section
            priority: Priority (1-10, higher = keep longer)
        
        Returns:
            True if added successfully, False if exceeds limit
        """
        tokens = self.estimate_tokens(text)
        
        if self.window.current_tokens + tokens > self.max_tokens:
            # Need to make space
            if self.window.is_near_limit:
                self._prune_context(tokens_needed=tokens)
            else:
                return False
        
        self.window.current_tokens += tokens
        return True
    
    def _prune_context(self, tokens_needed: int) -> None:
        """Prune low-priority sections from context."""
        # Strategy 1: Remove lowest priority sections
        # Strategy 2: Summarize middle-priority sections
        # Strategy 3: Keep only highest priority
        pass
    
    def summarize_section(self, text: str, target_ratio: float = 0.3) -> str:
        """Summarize text to reduce token count.
        
        Args:
            text: Text to summarize
            target_ratio: Target size as ratio of original (0.3 = 30%)
        
        Returns:
            Summarized text
        """
        # Implement extractive summarization
        # Take first sentence of each paragraph, key definitions, etc.
        lines = text.split('\n')
        summary_lines = []
        
        for line in lines:
            if line.startswith('#') or line.startswith('def ') or line.startswith('class '):
                summary_lines.append(line)
        
        return '\n'.join(summary_lines)
    
    def chunk_task(self, task: dict, max_chunk_tokens: int = 50000) -> List[dict]:
        """Split large task into smaller chunks.
        
        Args:
            task: Task to chunk
            max_chunk_tokens: Maximum tokens per chunk
        
        Returns:
            List of sub-tasks
        """
        # Split by file scope
        files = task.get('files_scope', [])
        chunks = []
        
        current_chunk = []
        current_tokens = 0
        
        for file in files:
            file_tokens = self.estimate_tokens(str(file))
            
            if current_tokens + file_tokens > max_chunk_tokens:
                # Create chunk
                chunks.append({
                    **task,
                    'files_scope': current_chunk,
                    'task_id': f"{task['task_id']}-chunk-{len(chunks)+1}"
                })
                current_chunk = [file]
                current_tokens = file_tokens
            else:
                current_chunk.append(file)
                current_tokens += file_tokens
        
        # Add remaining chunk
        if current_chunk:
            chunks.append({
                **task,
                'files_scope': current_chunk,
                'task_id': f"{task['task_id']}-chunk-{len(chunks)+1}"
            })
        
        return chunks
```

**Tasks**:
1. Create `core/engine/context_manager.py`
2. Token estimation with tiktoken
3. Pruning strategy (remove low-priority sections)
4. Summarization (extractive summarization)
5. Chunking (split large tasks by file scope)
6. Unit tests

**Validation**:
```bash
pytest tests/engine/test_context_manager.py -v
```

---

## 2. Phase B: Patch System (Week 3-4)

**Duration**: 2-3 weeks  
**Goal**: Core patch infrastructure  
**Estimated Cost**: $40

### Workstream WS-UET-B1: Database Migration

**Priority**: CRITICAL  
**Duration**: 6 hours  
**Files Created**:
- `schema/migrations/001_uet_alignment.sql`
- `scripts/migrate_db_to_uet.py`
- `scripts/rollback_db_migration.py`

**Database Schema Changes**:

```sql
-- schema/migrations/001_uet_alignment.sql

-- 1. Patches table
CREATE TABLE IF NOT EXISTS patches (
    patch_id TEXT PRIMARY KEY,          -- ULID
    format TEXT NOT NULL DEFAULT 'unified_diff',
    target_repo TEXT NOT NULL,
    base_ref TEXT,
    base_commit TEXT,
    execution_request_id TEXT,          -- ULID
    tool_id TEXT NOT NULL,
    created_at TEXT NOT NULL,           -- ISO 8601
    diff_text TEXT NOT NULL,
    summary TEXT,
    files_touched TEXT,                 -- JSON array
    line_insertions INTEGER DEFAULT 0,
    line_deletions INTEGER DEFAULT 0,
    hunks INTEGER DEFAULT 0
);

CREATE INDEX idx_patches_execution_request ON patches(execution_request_id);
CREATE INDEX idx_patches_tool_id ON patches(tool_id);
CREATE INDEX idx_patches_created_at ON patches(created_at);

-- 2. Patch ledger entries
CREATE TABLE IF NOT EXISTS patch_ledger_entries (
    ledger_id TEXT PRIMARY KEY,         -- ULID
    patch_id TEXT NOT NULL,
    project_id TEXT NOT NULL,
    phase_id TEXT,
    workstream_id TEXT,
    execution_request_id TEXT,
    state TEXT NOT NULL,                -- State machine value
    state_history TEXT,                 -- JSON array
    
    -- Validation
    validation_format_ok INTEGER DEFAULT 0,
    validation_scope_ok INTEGER DEFAULT 0,
    validation_constraints_ok INTEGER DEFAULT 0,
    validation_tests_ran INTEGER DEFAULT 0,
    validation_tests_passed INTEGER DEFAULT 0,
    validation_errors TEXT,             -- JSON array
    
    -- Application
    apply_attempts INTEGER DEFAULT 0,
    apply_last_attempt_at TEXT,
    apply_last_error_code TEXT,
    apply_last_error_message TEXT,
    apply_workspace_path TEXT,
    apply_applied_files TEXT,           -- JSON array
    
    -- Quarantine
    quarantine_is_quarantined INTEGER DEFAULT 0,
    quarantine_reason TEXT,
    quarantine_path TEXT,
    quarantine_at TEXT,
    
    -- Relations
    relations_replaces_patch_id TEXT,
    relations_rollback_of_patch_id TEXT,
    relations_chain_id TEXT,
    
    FOREIGN KEY (patch_id) REFERENCES patches(patch_id)
);

CREATE INDEX idx_patch_ledger_patch_id ON patch_ledger_entries(patch_id);
CREATE INDEX idx_patch_ledger_state ON patch_ledger_entries(state);
CREATE INDEX idx_patch_ledger_workstream ON patch_ledger_entries(workstream_id);

-- 3. Add ULID columns to existing tables
ALTER TABLE runs ADD COLUMN run_ulid TEXT;
ALTER TABLE workstreams ADD COLUMN workstream_ulid TEXT;
ALTER TABLE attempts ADD COLUMN attempt_ulid TEXT;

-- 4. Create run_events table (if not exists from Phase A)
CREATE TABLE IF NOT EXISTS run_events (
    event_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    payload TEXT,
    source TEXT,
    FOREIGN KEY (run_id) REFERENCES runs(run_id)
);
```

**Migration Script**:

```python
# scripts/migrate_db_to_uet.py
import sqlite3
import sys
from pathlib import Path
from ulid import ULID
from datetime import datetime

def migrate_db_to_uet(db_path: str = ".worktrees/pipeline_state.db", dry_run: bool = False):
    """Migrate database to UET schema.
    
    Args:
        db_path: Path to SQLite database
        dry_run: If True, show what would be done without executing
    """
    print(f"{'[DRY RUN] ' if dry_run else ''}Migrating database: {db_path}")
    
    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        return False
    
    # Backup first
    backup_path = f"{db_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if not dry_run:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Backup created: {backup_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Read migration SQL
        migration_sql = Path("schema/migrations/001_uet_alignment.sql").read_text()
        
        if dry_run:
            print("\n📋 Migration SQL:")
            print(migration_sql)
            print("\n[DRY RUN] No changes made")
            return True
        
        # Execute migration
        cursor.executescript(migration_sql)
        
        # Populate ULIDs for existing records
        print("Generating ULIDs for existing records...")
        
        # Runs
        cursor.execute("SELECT run_id FROM runs WHERE run_ulid IS NULL")
        for (run_id,) in cursor.fetchall():
            ulid = str(ULID())
            cursor.execute("UPDATE runs SET run_ulid = ? WHERE run_id = ?", (ulid, run_id))
            print(f"  Run {run_id} → {ulid}")
        
        # Workstreams
        cursor.execute("SELECT ws_id FROM workstreams WHERE workstream_ulid IS NULL")
        for (ws_id,) in cursor.fetchall():
            ulid = str(ULID())
            cursor.execute("UPDATE workstreams SET workstream_ulid = ? WHERE ws_id = ?", (ulid, ws_id))
            print(f"  Workstream {ws_id} → {ulid}")
        
        # Attempts
        cursor.execute("SELECT attempt_id FROM attempts WHERE attempt_ulid IS NULL")
        for (attempt_id,) in cursor.fetchall():
            ulid = str(ULID())
            cursor.execute("UPDATE attempts SET attempt_ulid = ? WHERE attempt_id = ?", (ulid, attempt_id))
            print(f"  Attempt {attempt_id} → {ulid}")
        
        conn.commit()
        print("\n✅ Database migrated to UET schema")
        print(f"✅ Backup available at: {backup_path}")
        
        # Validate
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['patches', 'patch_ledger_entries', 'run_events']
        for table in required_tables:
            if table in tables:
                print(f"  ✅ Table '{table}' created")
            else:
                print(f"  ❌ Table '{table}' MISSING")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    success = migrate_db_to_uet(dry_run=dry_run)
    sys.exit(0 if success else 1)
```

**Tasks**:
1. Create migration SQL
2. Create migration script with ULID generation
3. Create rollback script
4. Test migration on copy of database
5. Validate schema changes

**Validation**:
```bash
# Dry run first
python scripts/migrate_db_to_uet.py --dry-run

# Actual migration (creates backup)
python scripts/migrate_db_to_uet.py

# Validate
python scripts/validate_db_schema.py
```

---

### Workstream WS-UET-B2: Patch Ledger System

**Priority**: HIGH  
**Duration**: 16 hours  
**Files Created**:
- `core/patches/__init__.py`
- `core/patches/patch_ledger.py`
- `core/patches/patch_artifact.py`

**State Machine**:

```
created → validated → queued → applied → verified → committed
   ↓         ↓          ↓         ↓         ↓
apply_failed, rolled_back, quarantined, dropped
```

**Implementation**:

```python
# core/patches/patch_artifact.py
from dataclasses import dataclass, field
from typing import List, Optional
from ulid import ULID
from datetime import datetime, timezone

@dataclass
class PatchOrigin:
    """Origin metadata for patch."""
    execution_request_id: str
    tool_id: str
    created_at: datetime
    prompt_id: Optional[str] = None
    phase_id: Optional[str] = None
    workstream_id: Optional[str] = None
    tool_run_id: Optional[str] = None

@dataclass
class PatchScope:
    """Scope metrics for patch."""
    files_touched: List[str]
    line_insertions: int = 0
    line_deletions: int = 0
    hunks: int = 0

@dataclass
class PatchArtifact:
    """Canonical patch representation (UET-aligned)."""
    patch_id: str
    format: str  # 'unified_diff'
    target_repo: str
    origin: PatchOrigin
    diff_text: str
    base_ref: Optional[str] = None
    base_commit: Optional[str] = None
    summary: Optional[str] = None
    scope: Optional[PatchScope] = None
    
    @classmethod
    def from_diff(cls, diff_text: str, target_repo: str, tool_id: str, 
                  execution_request_id: str, **kwargs) -> 'PatchArtifact':
        """Create PatchArtifact from unified diff text."""
        patch_id = str(ULID())
        origin = PatchOrigin(
            execution_request_id=execution_request_id,
            tool_id=tool_id,
            created_at=datetime.now(timezone.utc),
            **{k: v for k, v in kwargs.items() if k in ['prompt_id', 'phase_id', 'workstream_id', 'tool_run_id']}
        )
        
        # Parse scope from diff
        scope = cls._parse_scope(diff_text)
        
        return cls(
            patch_id=patch_id,
            format='unified_diff',
            target_repo=target_repo,
            origin=origin,
            diff_text=diff_text,
            scope=scope,
            **{k: v for k, v in kwargs.items() if k in ['base_ref', 'base_commit', 'summary']}
        )
    
    @staticmethod
    def _parse_scope(diff_text: str) -> PatchScope:
        """Parse scope from unified diff."""
        files_touched = []
        line_insertions = 0
        line_deletions = 0
        hunks = 0
        
        for line in diff_text.split('\n'):
            if line.startswith('diff --git'):
                # Extract file path
                parts = line.split()
                if len(parts) >= 4:
                    file_path = parts[2].lstrip('a/')
                    files_touched.append(file_path)
            elif line.startswith('@@'):
                hunks += 1
            elif line.startswith('+') and not line.startswith('+++'):
                line_insertions += 1
            elif line.startswith('-') and not line.startswith('---'):
                line_deletions += 1
        
        return PatchScope(
            files_touched=files_touched,
            line_insertions=line_insertions,
            line_deletions=line_deletions,
            hunks=hunks
        )


# core/patches/patch_ledger.py
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional
import json
from datetime import datetime, timezone
from ulid import ULID

from core.state.db import get_connection
from core.patches.patch_artifact import PatchArtifact

class PatchState(Enum):
    """Patch state machine states."""
    CREATED = "created"
    VALIDATED = "validated"
    QUEUED = "queued"
    APPLIED = "applied"
    APPLY_FAILED = "apply_failed"
    VERIFIED = "verified"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    QUARANTINED = "quarantined"
    DROPPED = "dropped"

@dataclass
class StateTransition:
    """State transition record."""
    state: PatchState
    at: datetime
    reason: Optional[str] = None

@dataclass
class ValidationResult:
    """Patch validation result."""
    format_ok: bool
    scope_ok: bool
    constraints_ok: bool
    tests_ran: bool = False
    tests_passed: bool = False
    validation_errors: List[str] = field(default_factory=list)

class InvalidTransitionError(Exception):
    """Raised when invalid state transition attempted."""
    pass

class PatchLedger:
    """Manages patch lifecycle with state machine."""
    
    # Valid state transitions
    VALID_TRANSITIONS = {
        PatchState.CREATED: [PatchState.VALIDATED, PatchState.DROPPED],
        PatchState.VALIDATED: [PatchState.QUEUED, PatchState.QUARANTINED],
        PatchState.QUEUED: [PatchState.APPLIED, PatchState.APPLY_FAILED],
        PatchState.APPLIED: [PatchState.VERIFIED, PatchState.ROLLED_BACK],
        PatchState.APPLY_FAILED: [PatchState.QUARANTINED, PatchState.QUEUED],
        PatchState.VERIFIED: [PatchState.COMMITTED, PatchState.ROLLED_BACK],
        PatchState.COMMITTED: [],  # Terminal state
        PatchState.ROLLED_BACK: [PatchState.DROPPED],
        PatchState.QUARANTINED: [PatchState.DROPPED],
        PatchState.DROPPED: []  # Terminal state
    }
    
    def __init__(self):
        """Initialize patch ledger."""
        pass
    
    def create_entry(self, patch: PatchArtifact, project_id: str, 
                    phase_id: str = None, workstream_id: str = None) -> str:
        """Create ledger entry for patch.
        
        Returns:
            ledger_id (ULID)
        """
        ledger_id = str(ULID())
        
        # Store patch
        self._store_patch(patch)
        
        # Create ledger entry
        conn = get_connection()
        try:
            conn.execute("""
                INSERT INTO patch_ledger_entries (
                    ledger_id, patch_id, project_id, phase_id, workstream_id,
                    execution_request_id, state, state_history,
                    validation_format_ok, validation_scope_ok, validation_constraints_ok
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0)
            """, (
                ledger_id,
                patch.patch_id,
                project_id,
                phase_id,
                workstream_id,
                patch.origin.execution_request_id,
                PatchState.CREATED.value,
                json.dumps([{
                    'state': PatchState.CREATED.value,
                    'at': datetime.now(timezone.utc).isoformat(),
                    'reason': 'Initial creation'
                }])
            ))
            conn.commit()
        finally:
            conn.close()
        
        return ledger_id
    
    def _store_patch(self, patch: PatchArtifact) -> None:
        """Store patch in patches table."""
        conn = get_connection()
        try:
            conn.execute("""
                INSERT INTO patches (
                    patch_id, format, target_repo, base_ref, base_commit,
                    execution_request_id, tool_id, created_at, diff_text,
                    summary, files_touched, line_insertions, line_deletions, hunks
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                patch.patch_id,
                patch.format,
                patch.target_repo,
                patch.base_ref,
                patch.base_commit,
                patch.origin.execution_request_id,
                patch.origin.tool_id,
                patch.origin.created_at.isoformat(),
                patch.diff_text,
                patch.summary,
                json.dumps(patch.scope.files_touched) if patch.scope else None,
                patch.scope.line_insertions if patch.scope else 0,
                patch.scope.line_deletions if patch.scope else 0,
                patch.scope.hunks if patch.scope else 0
            ))
            conn.commit()
        finally:
            conn.close()
    
    def get_state(self, ledger_id: str) -> PatchState:
        """Get current state of patch."""
        conn = get_connection()
        try:
            cursor = conn.execute(
                "SELECT state FROM patch_ledger_entries WHERE ledger_id = ?",
                (ledger_id,)
            )
            row = cursor.fetchone()
            if row:
                return PatchState(row[0])
            raise ValueError(f"Ledger entry not found: {ledger_id}")
        finally:
            conn.close()
    
    def transition(self, ledger_id: str, new_state: PatchState, reason: str = None) -> None:
        """Transition patch to new state.
        
        Raises:
            InvalidTransitionError: If transition is not allowed
        """
        current_state = self.get_state(ledger_id)
        
        # Validate transition
        valid_next_states = self.VALID_TRANSITIONS.get(current_state, [])
        if new_state not in valid_next_states:
            raise InvalidTransitionError(
                f"Invalid transition from {current_state.value} to {new_state.value}. "
                f"Valid next states: {[s.value for s in valid_next_states]}"
            )
        
        # Update state
        conn = get_connection()
        try:
            # Get current state history
            cursor = conn.execute(
                "SELECT state_history FROM patch_ledger_entries WHERE ledger_id = ?",
                (ledger_id,)
            )
            row = cursor.fetchone()
            state_history = json.loads(row[0]) if row and row[0] else []
            
            # Add new transition
            state_history.append({
                'state': new_state.value,
                'at': datetime.now(timezone.utc).isoformat(),
                'reason': reason
            })
            
            # Update
            conn.execute("""
                UPDATE patch_ledger_entries
                SET state = ?, state_history = ?
                WHERE ledger_id = ?
            """, (new_state.value, json.dumps(state_history), ledger_id))
            conn.commit()
        finally:
            conn.close()
    
    def update_validation(self, ledger_id: str, validation: ValidationResult) -> None:
        """Update validation results."""
        conn = get_connection()
        try:
            conn.execute("""
                UPDATE patch_ledger_entries
                SET validation_format_ok = ?,
                    validation_scope_ok = ?,
                    validation_constraints_ok = ?,
                    validation_tests_ran = ?,
                    validation_tests_passed = ?,
                    validation_errors = ?
                WHERE ledger_id = ?
            """, (
                1 if validation.format_ok else 0,
                1 if validation.scope_ok else 0,
                1 if validation.constraints_ok else 0,
                1 if validation.tests_ran else 0,
                1 if validation.tests_passed else 0,
                json.dumps(validation.validation_errors),
                ledger_id
            ))
            conn.commit()
        finally:
            conn.close()
    
    def quarantine(self, ledger_id: str, reason: str, quarantine_path: str) -> None:
        """Quarantine a patch."""
        # Transition to quarantined state
        self.transition(ledger_id, PatchState.QUARANTINED, reason)
        
        # Update quarantine metadata
        conn = get_connection()
        try:
            conn.execute("""
                UPDATE patch_ledger_entries
                SET quarantine_is_quarantined = 1,
                    quarantine_reason = ?,
                    quarantine_path = ?,
                    quarantine_at = ?
                WHERE ledger_id = ?
            """, (reason, quarantine_path, datetime.now(timezone.utc).isoformat(), ledger_id))
            conn.commit()
        finally:
            conn.close()
```

**Tasks**:
1. Create `PatchArtifact` class with UET schema alignment
2. Create `PatchLedger` with state machine
3. Implement state transition validation
4. Add validation result tracking
5. Add quarantine logic
6. Unit tests for state machine
7. Integration tests with database

**Validation**:
```bash
pytest tests/patches/test_patch_ledger.py -v
pytest tests/patches/test_state_machine.py -v
```

---

### Workstream WS-UET-B3: Patch Validator

**Priority**: HIGH  
**Duration**: 8 hours  
**Files Created**: `core/patches/patch_validator.py`

**Implementation**:

```python
# core/patches/patch_validator.py
import re
from typing import List
from pathlib import Path
from core.patches.patch_artifact import PatchArtifact, PatchScope
from core/patches.patch_ledger import ValidationResult

class PatchValidator:
    """Validates patches against format, scope, and policy constraints."""
    
    def __init__(self, max_files_changed: int = 10, max_lines_changed: int = 500):
        """Initialize validator.
        
        Args:
            max_files_changed: Maximum files that can be modified
            max_lines_changed: Maximum total lines changed (insertions + deletions)
        """
        self.max_files_changed = max_files_changed
        self.max_lines_changed = max_lines_changed
    
    def validate(self, patch: PatchArtifact) -> ValidationResult:
        """Validate patch.
        
        Returns:
            ValidationResult with detailed validation status
        """
        errors = []
        
        # 1. Format validation
        format_ok = self._validate_format(patch, errors)
        
        # 2. Scope validation
        scope_ok = self._validate_scope(patch, errors)
        
        # 3. Constraint validation
        constraints_ok = self._validate_constraints(patch, errors)
        
        return ValidationResult(
            format_ok=format_ok,
            scope_ok=scope_ok,
            constraints_ok=constraints_ok,
            validation_errors=errors
        )
    
    def _validate_format(self, patch: PatchArtifact, errors: List[str]) -> bool:
        """Validate patch format (must be unified diff)."""
        if patch.format != 'unified_diff':
            errors.append(f"Invalid format: {patch.format}. Only 'unified_diff' supported.")
            return False
        
        # Check for unified diff headers
        if not re.search(r'^diff --git', patch.diff_text, re.MULTILINE):
            errors.append("Missing 'diff --git' header in unified diff")
            return False
        
        if not re.search(r'^@@', patch.diff_text, re.MULTILINE):
            errors.append("Missing hunk headers (@@) in unified diff")
            return False
        
        return True
    
    def _validate_scope(self, patch: PatchArtifact, errors: List[str]) -> bool:
        """Validate patch scope (files, lines changed)."""
        if not patch.scope:
            errors.append("Patch scope not available")
            return False
        
        # Check file count
        if len(patch.scope.files_touched) > self.max_files_changed:
            errors.append(
                f"Too many files changed: {len(patch.scope.files_touched)} > {self.max_files_changed}"
            )
            return False
        
        # Check total lines changed
        total_lines = patch.scope.line_insertions + patch.scope.line_deletions
        if total_lines > self.max_lines_changed:
            errors.append(
                f"Too many lines changed: {total_lines} > {self.max_lines_changed}"
            )
            return False
        
        return True
    
    def _validate_constraints(self, patch: PatchArtifact, errors: List[str]) -> bool:
        """Validate policy constraints."""
        # Check for forbidden paths
        forbidden_patterns = [
            r'\.git/',
            r'\.env',
            r'secrets\.yaml',
            r'__pycache__/',
            r'\.venv/'
        ]
        
        for file_path in patch.scope.files_touched:
            for pattern in forbidden_patterns:
                if re.search(pattern, file_path):
                    errors.append(f"Forbidden path pattern in {file_path}: {pattern}")
                    return False
        
        # Check for binary patches (not allowed)
        if re.search(r'Binary files .* differ', patch.diff_text):
            errors.append("Binary patches not allowed")
            return False
        
        return True
```

**Tasks**:
1. Create `PatchValidator` class
2. Format validation (unified diff only)
3. Scope validation (file count, line count)
4. Constraint validation (forbidden paths, binary patches)
5. Unit tests with valid/invalid patches

**Validation**:
```bash
pytest tests/patches/test_patch_validator.py -v
```

---

### Workstream WS-UET-B4: Patch Policy Engine

**Priority**: MEDIUM  
**Duration**: 12 hours  
**Files Created**:
- `core/patches/patch_policy.py`
- `config/patch_policies/global.json`
- `config/patch_policies/python_strict.json`

**Implementation**:

```python
# core/patches/patch_policy.py
from dataclasses import dataclass
from typing import List, Optional
import json
from pathlib import Path

@dataclass
class PatchConstraints:
    """Patch policy constraints."""
    allowed_formats: List[str]
    patch_required: bool = True
    max_lines_changed: Optional[int] = None
    max_files_changed: Optional[int] = None
    forbid_binary_patches: bool = True
    forbid_touching_paths: List[str] = None
    require_tests_for_paths: List[str] = None
    require_issue_ref: bool = False
    min_reviewers: int = 0
    oscillation_window: Optional[int] = None
    oscillation_threshold: Optional[int] = None
    
    def __post_init__(self):
        if self.forbid_touching_paths is None:
            self.forbid_touching_paths = []
        if self.require_tests_for_paths is None:
            self.require_tests_for_paths = []

@dataclass
class PatchPolicyScope:
    """Scope where policy applies."""
    level: str  # 'global', 'project', 'phase', 'doc'
    project_id: Optional[str] = None
    phase_id: Optional[str] = None
    doc_ulid: Optional[str] = None

@dataclass
class PatchPolicy:
    """Patch policy definition."""
    patch_policy_id: str
    scope: PatchPolicyScope
    constraints: PatchConstraints
    
    @classmethod
    def from_file(cls, policy_file: Path) -> 'PatchPolicy':
        """Load policy from JSON file."""
        data = json.loads(policy_file.read_text())
        
        scope = PatchPolicyScope(
            level=data['scope']['level'],
            project_id=data['scope'].get('project_id'),
            phase_id=data['scope'].get('phase_id'),
            doc_ulid=data['scope'].get('doc_ulid')
        )
        
        constraints_data = data['constraints']
        constraints = PatchConstraints(
            allowed_formats=constraints_data.get('allowed_formats', ['unified_diff']),
            patch_required=constraints_data.get('patch_required', True),
            max_lines_changed=constraints_data.get('max_lines_changed'),
            max_files_changed=constraints_data.get('max_files_changed'),
            forbid_binary_patches=constraints_data.get('forbid_binary_patches', True),
            forbid_touching_paths=constraints_data.get('forbid_touching_paths', []),
            require_tests_for_paths=constraints_data.get('require_tests_for_paths', []),
            require_issue_ref=constraints_data.get('require_issue_ref', False),
            min_reviewers=constraints_data.get('min_reviewers', 0),
            oscillation_window=constraints_data.get('oscillation_window'),
            oscillation_threshold=constraints_data.get('oscillation_threshold')
        )
        
        return cls(
            patch_policy_id=data['patch_policy_id'],
            scope=scope,
            constraints=constraints
        )

class PatchPolicyEngine:
    """Enforces patch policies."""
    
    def __init__(self, policies_dir: Path = Path("config/patch_policies")):
        """Initialize policy engine.
        
        Args:
            policies_dir: Directory containing policy JSON files
        """
        self.policies_dir = policies_dir
        self.policies: List[PatchPolicy] = []
        self._load_policies()
    
    def _load_policies(self) -> None:
        """Load all policies from directory."""
        if not self.policies_dir.exists():
            return
        
        for policy_file in self.policies_dir.glob("*.json"):
            policy = PatchPolicy.from_file(policy_file)
            self.policies.append(policy)
    
    def get_applicable_policy(self, project_id: str = None, phase_id: str = None) -> PatchPolicy:
        """Get applicable policy for given scope.
        
        Priority: doc > phase > project > global
        """
        # For now, return global or first match
        for policy in self.policies:
            if policy.scope.level == 'global':
                return policy
            if policy.scope.level == 'project' and policy.scope.project_id == project_id:
                return policy
            if policy.scope.level == 'phase' and policy.scope.phase_id == phase_id:
                return policy
        
        # Default policy if none found
        return PatchPolicy(
            patch_policy_id="default",
            scope=PatchPolicyScope(level="global"),
            constraints=PatchConstraints(allowed_formats=['unified_diff'])
        )
```

**Policy Files**:

```json
// config/patch_policies/global.json
{
  "patch_policy_id": "global-default",
  "scope": {
    "level": "global"
  },
  "constraints": {
    "allowed_formats": ["unified_diff"],
    "patch_required": true,
    "max_lines_changed": 500,
    "max_files_changed": 10,
    "forbid_binary_patches": true,
    "forbid_touching_paths": [
      "\\.git/",
      "\\.env",
      "secrets\\.yaml",
      "__pycache__/",
      "\\.venv/"
    ],
    "require_tests_for_paths": [
      "core/.*\\.py",
      "engine/.*\\.py"
    ],
    "require_issue_ref": false,
    "min_reviewers": 0
  }
}
```

```json
// config/patch_policies/python_strict.json
{
  "patch_policy_id": "python-strict",
  "scope": {
    "level": "project",
    "project_id": "complete-ai-pipeline"
  },
  "constraints": {
    "allowed_formats": ["unified_diff"],
    "patch_required": true,
    "max_lines_changed": 200,
    "max_files_changed": 5,
    "forbid_binary_patches": true,
    "forbid_touching_paths": [
      "\\.git/",
      "\\.env",
      "secrets\\.yaml",
      "__pycache__/",
      "\\.venv/",
      "legacy/.*"
    ],
    "require_tests_for_paths": [
      "core/.*\\.py",
      "engine/.*\\.py",
      "error/.*\\.py"
    ],
    "require_issue_ref": true,
    "min_reviewers": 1,
    "oscillation_window": 5,
    "oscillation_threshold": 3
  }
}
```

**Tasks**:
1. Create `PatchPolicy` and `PatchPolicyEngine`
2. Create global policy JSON
3. Create python-strict policy JSON
4. Add policy loading from directory
5. Add policy selection logic (scope-based)
6. Unit tests

**Validation**:
```bash
pytest tests/patches/test_patch_policy.py -v
```

---

## 3. Summary: Phase Plan Structure

This phase plan demonstrates how to build UET integration using:

### 1. UET_EXECUTION_KERNEL_PARALLELISM_STRATEGY_SPEC_V2 Concepts

**Worker Lifecycle** (WS-UET-A2):
- Worker states: SPAWNING → IDLE → BUSY → DRAINING → TERMINATED
- Health checks with heartbeat monitoring
- Quarantine for unhealthy workers

**Integration Worker** (future phase):
- Merge orchestration with deterministic order
- Conflict detection → E_MERGE_CONFLICT event
- Rollback on merge failure

**Test Gates** (future phase):
- GATE_LINT, GATE_UNIT, GATE_INTEGRATION
- Block dependent tasks until gate cleared
- Feedback loop creates fix tasks on failures

**Human Review** (future phase):
- Structured escalation workflow
- Compact summary + error context + proposed options
- Feedback: approve / reject / adjust

**Rollback/Compensation** (future phase):
- Saga pattern with forward_actions + compensation_actions
- Patch rollback (git revert)
- Phase rollback (compensation cascade)

### 2. UET_PATCH_MANAGEMENT_SPEC Concepts

**PatchArtifact** (WS-UET-B2):
- ULID identifier
- Unified diff format only
- Origin metadata (execution_request_id, tool_id, created_at)
- Scope metrics (files_touched, line_insertions, line_deletions, hunks)

**PatchLedgerEntry** (WS-UET-B2):
- Full lifecycle tracking
- State machine: created → validated → queued → applied → verified → committed
- Validation results (format_ok, scope_ok, constraints_ok, tests_passed)
- Quarantine metadata (reason, path, timestamp)

**PatchPolicy** (WS-UET-B4):
- Scope-based policies (global, project, phase, doc)
- Constraints (max_lines, max_files, forbidden paths, require tests)
- Oscillation detection

### 3. Patch-First Workflow Concepts

**Unified Diff Only** (all phases):
- No direct file edits
- Tools output unified diffs
- Orchestrator validates → applies → tests → commits

**Language-Aware Validation** (future):
- Python: ruff, black, pytest
- PowerShell: PSScriptAnalyzer, Pester

**Task Modes** (future adapter refactoring):
- `mode: "prompt"` - Tool generates patch
- `mode: "patch_review"` - Tool reviews existing patch (no edits)
- `mode: "patch_apply_validate"` - Apply patch + run tests

---

## 4. Next Steps

**Immediate** (This Week):
1. Copy UET schemas (2 hours)
2. Worker health checks (4 hours)
3. Event persistence (4 hours)

**Week 1-2** (Phase A):
- Feedback loop (8 hours)
- Context manager (8 hours)

**Week 3-4** (Phase B):
- Database migration (6 hours)
- Patch ledger system (16 hours)
- Patch validator (8 hours)
- Patch policy engine (12 hours)

**See**: `UET_INTEGRATION_PLAN_ANALYSIS.md` for complete 10-week roadmap.

---

**This phase plan provides a concrete, executable path to UET integration using workstream-based development.**
