"""
Worker Lifecycle Management

Manages worker process lifecycle with state machine transitions.
Tracks worker status, heartbeats, and execution statistics.

State Machine:
    idle -> busy -> idle (normal cycle)
    idle -> paused -> idle (pause/resume)
    any -> stopped (shutdown)
    any -> crashed (error)

Author: AI Development Pipeline
Created: 2025-11-23
WS: WS-NEXT-002-001
"""
DOC_ID: DOC-CORE-ENGINE-WORKER-LIFECYCLE-162

from datetime import datetime, UTC
from typing import Dict, Optional, List
from dataclasses import dataclass
import json


@dataclass
class WorkerStatistics:
    """Worker execution statistics"""
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_execution_time: float = 0.0
    
    @property
    def avg_task_duration(self) -> float:
        """Calculate average task duration"""
        total_tasks = self.tasks_completed + self.tasks_failed
        if total_tasks == 0:
            return 0.0
        return self.total_execution_time / total_tasks
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'total_execution_time': self.total_execution_time,
            'avg_task_duration': self.avg_task_duration
        }


class WorkerLifecycle:
    """
    Manages worker lifecycle state machine and tracking.
    
    States:
        - idle: Worker is ready but not executing
        - busy: Worker is currently executing a task
        - paused: Worker is temporarily suspended
        - stopped: Worker has been shut down
        - crashed: Worker encountered an error
    
    Transitions:
        - start: Initialize worker -> idle
        - assign_task: idle -> busy
        - complete_task: busy -> idle
        - pause: idle/busy -> paused
        - resume: paused -> idle
        - crash: any -> crashed
        - shutdown: any -> stopped
    """
    
    VALID_STATES = {'idle', 'busy', 'paused', 'stopped', 'crashed'}
    VALID_TYPES = {'executor', 'monitor', 'validator', 'scheduler', 'custom'}
    TERMINAL_STATES = {'stopped', 'crashed'}
    
    STATE_TRANSITIONS = {
        'idle': ['busy', 'paused', 'stopped', 'crashed'],
        'busy': ['idle', 'paused', 'stopped', 'crashed'],
        'paused': ['idle', 'stopped', 'crashed'],
        'stopped': [],  # Terminal state
        'crashed': []   # Terminal state
    }
    
    def __init__(self, db):
        """
        Initialize WorkerLifecycle manager.
        
        Args:
            db: Database instance for persistence
        """
        self.db = db
        self._ensure_table()
    
    def _ensure_table(self):
        """Ensure workers table exists"""
        # Table should be created by migration, but verify
        try:
            self.db.conn.execute("SELECT 1 FROM workers LIMIT 1")
        except Exception:
            # Table doesn't exist, create it
            with open('schema/migrations/002_add_workers_table.sql', 'r') as f:
                self.db.conn.executescript(f.read())
            self.db.conn.commit()
    
    def create_worker(
        self,
        worker_id: str,
        worker_type: str,
        config: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Create a new worker.
        
        Args:
            worker_id: Unique worker identifier (ULID)
            worker_type: Type of worker (executor, monitor, etc.)
            config: Worker configuration
            metadata: Additional metadata
        
        Returns:
            worker_id
        
        Raises:
            ValueError: If worker_type invalid or worker_id exists
        """
        if worker_type not in self.VALID_TYPES:
            raise ValueError(f"Invalid worker_type: {worker_type}")
        
        worker_data = {
            'worker_id': worker_id,
            'worker_type': worker_type,
            'state': 'idle',
            'current_task_id': None,
            'started_at': datetime.now(UTC).isoformat(),
            'last_heartbeat': datetime.now(UTC).isoformat(),
            'stopped_at': None,
            'crash_info': None,
            'statistics': json.dumps(WorkerStatistics().to_dict()),
            'config': json.dumps(config) if config else None,
            'metadata': json.dumps(metadata) if metadata else None
        }
        
        self.db.conn.execute(
            """
            INSERT INTO workers (
                worker_id, worker_type, state, current_task_id,
                started_at, last_heartbeat, stopped_at, crash_info,
                statistics, config, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                worker_data['worker_id'],
                worker_data['worker_type'],
                worker_data['state'],
                worker_data['current_task_id'],
                worker_data['started_at'],
                worker_data['last_heartbeat'],
                worker_data['stopped_at'],
                worker_data['crash_info'],
                worker_data['statistics'],
                worker_data['config'],
                worker_data['metadata']
            )
        )
        self.db.conn.commit()
        
        return worker_id
    
    def get_worker(self, worker_id: str) -> Optional[Dict]:
        """
        Get worker by ID.
        
        Args:
            worker_id: Worker identifier
        
        Returns:
            Worker data dict or None if not found
        """
        row = self.db.conn.execute(
            "SELECT * FROM workers WHERE worker_id = ?",
            (worker_id,)
        ).fetchone()
        
        if not row:
            return None
        
        return self._row_to_dict(row)
    
    def _row_to_dict(self, row) -> Dict:
        """Convert database row to dict"""
        data = dict(row)
        
        # Deserialize JSON fields
        if data.get('statistics'):
            data['statistics'] = json.loads(data['statistics'])
        if data.get('config'):
            data['config'] = json.loads(data['config'])
        if data.get('metadata'):
            data['metadata'] = json.loads(data['metadata'])
        if data.get('crash_info'):
            data['crash_info'] = json.loads(data['crash_info'])
        
        return data
    
    def assign_task(self, worker_id: str, task_id: str) -> bool:
        """
        Assign a task to worker (idle -> busy transition).
        
        Args:
            worker_id: Worker identifier
            task_id: Task identifier to assign
        
        Returns:
            True if successful
        
        Raises:
            ValueError: If transition invalid
        """
        worker = self.get_worker(worker_id)
        if not worker:
            raise ValueError(f"Worker not found: {worker_id}")
        
        if not self._can_transition(worker['state'], 'busy'):
            raise ValueError(
                f"Cannot assign task: worker in {worker['state']} state"
            )
        
        self.db.conn.execute(
            """
            UPDATE workers 
            SET state = 'busy', 
                current_task_id = ?,
                last_heartbeat = ?
            WHERE worker_id = ?
            """,
            (task_id, datetime.now(UTC).isoformat(), worker_id)
        )
        self.db.conn.commit()
        
        return True
    
    def complete_task(
        self,
        worker_id: str,
        success: bool = True,
        execution_time: float = 0.0
    ) -> bool:
        """
        Mark task complete (busy -> idle transition).
        
        Args:
            worker_id: Worker identifier
            success: Whether task succeeded
            execution_time: Task execution time in seconds
        
        Returns:
            True if successful
        """
        worker = self.get_worker(worker_id)
        if not worker:
            raise ValueError(f"Worker not found: {worker_id}")
        
        if worker['state'] != 'busy':
            raise ValueError(
                f"Cannot complete task: worker not busy (state: {worker['state']})"
            )
        
        # Update statistics
        stats_data = worker['statistics']
        stats = WorkerStatistics(
            tasks_completed=stats_data['tasks_completed'],
            tasks_failed=stats_data['tasks_failed'],
            total_execution_time=stats_data['total_execution_time']
        )
        if success:
            stats.tasks_completed += 1
        else:
            stats.tasks_failed += 1
        stats.total_execution_time += execution_time
        
        self.db.conn.execute(
            """
            UPDATE workers 
            SET state = 'idle',
                current_task_id = NULL,
                last_heartbeat = ?,
                statistics = ?
            WHERE worker_id = ?
            """,
            (
                datetime.now(UTC).isoformat(),
                json.dumps(stats.to_dict()),
                worker_id
            )
        )
        self.db.conn.commit()
        
        return True
    
    def heartbeat(self, worker_id: str) -> bool:
        """
        Update worker heartbeat timestamp.
        
        Args:
            worker_id: Worker identifier
        
        Returns:
            True if successful
        """
        self.db.conn.execute(
            "UPDATE workers SET last_heartbeat = ? WHERE worker_id = ?",
            (datetime.now(UTC).isoformat(), worker_id)
        )
        self.db.conn.commit()
        return True
    
    def pause_worker(self, worker_id: str) -> bool:
        """
        Pause worker (idle/busy -> paused transition).
        
        Args:
            worker_id: Worker identifier
        
        Returns:
            True if successful
        """
        worker = self.get_worker(worker_id)
        if not worker:
            raise ValueError(f"Worker not found: {worker_id}")
        
        if not self._can_transition(worker['state'], 'paused'):
            raise ValueError(
                f"Cannot pause: worker in {worker['state']} state"
            )
        
        self.db.conn.execute(
            "UPDATE workers SET state = 'paused' WHERE worker_id = ?",
            (worker_id,)
        )
        self.db.conn.commit()
        
        return True
    
    def resume_worker(self, worker_id: str) -> bool:
        """
        Resume worker (paused -> idle transition).
        
        Args:
            worker_id: Worker identifier
        
        Returns:
            True if successful
        """
        worker = self.get_worker(worker_id)
        if not worker:
            raise ValueError(f"Worker not found: {worker_id}")
        
        if worker['state'] != 'paused':
            raise ValueError(
                f"Cannot resume: worker not paused (state: {worker['state']})"
            )
        
        self.db.conn.execute(
            """
            UPDATE workers 
            SET state = 'idle',
                last_heartbeat = ?
            WHERE worker_id = ?
            """,
            (datetime.now(UTC).isoformat(), worker_id)
        )
        self.db.conn.commit()
        
        return True
    
    def crash_worker(
        self,
        worker_id: str,
        error_message: str,
        stack_trace: Optional[str] = None
    ) -> bool:
        """
        Mark worker as crashed (any -> crashed transition).
        
        Args:
            worker_id: Worker identifier
            error_message: Error description
            stack_trace: Optional stack trace
        
        Returns:
            True if successful
        """
        crash_info = {
            'crashed_at': datetime.now(UTC).isoformat(),
            'error_message': error_message,
            'stack_trace': stack_trace
        }
        
        self.db.conn.execute(
            """
            UPDATE workers 
            SET state = 'crashed',
                crash_info = ?,
                current_task_id = NULL
            WHERE worker_id = ?
            """,
            (json.dumps(crash_info), worker_id)
        )
        self.db.conn.commit()
        
        return True
    
    def shutdown_worker(self, worker_id: str) -> bool:
        """
        Shutdown worker (any -> stopped transition).
        
        Args:
            worker_id: Worker identifier
        
        Returns:
            True if successful
        """
        self.db.conn.execute(
            """
            UPDATE workers 
            SET state = 'stopped',
                stopped_at = ?,
                current_task_id = NULL
            WHERE worker_id = ?
            """,
            (datetime.now(UTC).isoformat(), worker_id)
        )
        self.db.conn.commit()
        
        return True
    
    def list_workers(
        self,
        state: Optional[str] = None,
        worker_type: Optional[str] = None
    ) -> List[Dict]:
        """
        List workers with optional filters.
        
        Args:
            state: Filter by state
            worker_type: Filter by type
        
        Returns:
            List of worker dicts
        """
        query = "SELECT * FROM workers WHERE 1=1"
        params = []
        
        if state:
            query += " AND state = ?"
            params.append(state)
        
        if worker_type:
            query += " AND worker_type = ?"
            params.append(worker_type)
        
        query += " ORDER BY started_at DESC"
        
        rows = self.db.conn.execute(query, params).fetchall()
        return [self._row_to_dict(row) for row in rows]
    
    def get_stale_workers(self, timeout_seconds: int = 60) -> List[Dict]:
        """
        Get workers with stale heartbeats.
        
        Args:
            timeout_seconds: Heartbeat timeout threshold
        
        Returns:
            List of workers with stale heartbeats
        """
        cutoff = datetime.now(UTC).timestamp() - timeout_seconds
        
        # This is a simplified check - would need datetime parsing in production
        workers = self.list_workers()
        stale = []
        
        for worker in workers:
            if worker['state'] in self.TERMINAL_STATES:
                continue
            
            if worker['last_heartbeat']:
                try:
                    heartbeat_dt = datetime.fromisoformat(
                        worker['last_heartbeat'].replace('Z', '+00:00')
                    )
                    if heartbeat_dt.timestamp() < cutoff:
                        stale.append(worker)
                except (ValueError, AttributeError):
                    stale.append(worker)
        
        return stale
    
    def _can_transition(self, from_state: str, to_state: str) -> bool:
        """
        Check if state transition is valid.
        
        Args:
            from_state: Current state
            to_state: Target state
        
        Returns:
            True if transition is valid
        """
        if from_state in self.TERMINAL_STATES:
            return False
        
        return to_state in self.STATE_TRANSITIONS.get(from_state, [])
    
    @staticmethod
    def is_terminal(state: str) -> bool:
        """Check if state is terminal"""
        return state in WorkerLifecycle.TERMINAL_STATES
