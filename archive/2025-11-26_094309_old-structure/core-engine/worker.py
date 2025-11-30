"""Worker lifecycle management.

Manages the lifecycle of execution workers including state transitions,
heartbeat monitoring, and task assignment.

Phase I: Added process spawning integration.
"""
DOC_ID: DOC-PAT-CORE-ENGINE-WORKER-404

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional


class WorkerState(Enum):
    """Worker state machine states."""
    SPAWNING = "SPAWNING"
    IDLE = "IDLE"
    BUSY = "BUSY"
    DRAINING = "DRAINING"
    TERMINATED = "TERMINATED"


@dataclass
class Worker:
    """Worker instance."""
    worker_id: str
    adapter_type: str  # 'aider', 'codex', 'claude', etc.
    state: WorkerState
    current_task_id: Optional[str] = None
    sandbox_path: Optional[str] = None
    pid: Optional[int] = None
    heartbeat_at: Optional[datetime] = None
    spawned_at: Optional[datetime] = None
    terminated_at: Optional[datetime] = None
    metadata: Dict[str, any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.spawned_at is None:
            self.spawned_at = datetime.now(timezone.utc)
        if self.heartbeat_at is None:
            self.heartbeat_at = self.spawned_at


class WorkerPool:
    """Manages lifecycle of N workers."""
    
    def __init__(self, max_workers: int = 4, enable_processes: bool = False):
        self.max_workers = max_workers
        self.workers: Dict[str, Worker] = {}
        self.idle_queue: List[str] = []
        self.enable_processes = enable_processes
        
        # Process spawner (optional)
        self.process_spawner = None
        if enable_processes:
            from modules.core_engine.m010001_process_spawner import ProcessSpawner
            self.process_spawner = ProcessSpawner()
    
    def spawn_worker(self, adapter_type: str, worker_id: Optional[str] = None) -> Worker:
        """Create new worker instance.
        
        Args:
            adapter_type: Tool adapter type (aider, codex, etc.)
            worker_id: Optional worker ID (generated if not provided)
            
        Returns:
            Worker instance
        """
        if len(self.workers) >= self.max_workers:
            raise RuntimeError(f"Worker pool full (max={self.max_workers})")
        
        if worker_id is None:
            import uuid
            worker_id = f"worker-{uuid.uuid4().hex[:8]}"
        
        worker = Worker(
            worker_id=worker_id,
            adapter_type=adapter_type,
            state=WorkerState.SPAWNING
        )
        
        self.workers[worker_id] = worker
        
        # Spawn actual process if enabled
        if self.enable_processes and self.process_spawner:
            from pathlib import Path
            repo_root = Path.cwd()
            worker_process = self.process_spawner.spawn_worker_process(
                worker_id=worker_id,
                adapter_type=adapter_type,
                repo_root=repo_root
            )
            worker.sandbox_path = str(worker_process.sandbox_path)
            worker.pid = worker_process.pid
        
        # Transition to IDLE after spawning
        self._transition(worker_id, WorkerState.IDLE)
        
        # Persist to DB
        self._persist_worker(worker)
        
        return worker
    
    def assign_task(self, worker_id: str, task_id: str) -> None:
        """Transition worker IDLE → BUSY.
        
        Args:
            worker_id: Worker ID
            task_id: Task/step ID to assign
        """
        worker = self.workers.get(worker_id)
        if not worker:
            raise ValueError(f"Worker not found: {worker_id}")
        
        if worker.state != WorkerState.IDLE:
            raise ValueError(f"Worker {worker_id} not idle (state={worker.state})")
        
        worker.current_task_id = task_id
        self._transition(worker_id, WorkerState.BUSY)
        
        # Remove from idle queue
        if worker_id in self.idle_queue:
            self.idle_queue.remove(worker_id)
        
        # Persist
        self._persist_worker(worker)
    
    def release_worker(self, worker_id: str) -> None:
        """Transition worker BUSY → IDLE.
        
        Args:
            worker_id: Worker ID
        """
        worker = self.workers.get(worker_id)
        if not worker:
            raise ValueError(f"Worker not found: {worker_id}")
        
        if worker.state != WorkerState.BUSY:
            raise ValueError(f"Worker {worker_id} not busy (state={worker.state})")
        
        worker.current_task_id = None
        self._transition(worker_id, WorkerState.IDLE)
        
        # Add to idle queue
        if worker_id not in self.idle_queue:
            self.idle_queue.append(worker_id)
        
        # Persist
        self._persist_worker(worker)
    
    def complete_task(self, worker_id: str) -> None:
        """Mark task as complete and release worker. Alias for release_worker."""
        self.release_worker(worker_id)
    
    def drain_worker(self, worker_id: str) -> None:
        """Transition worker to DRAINING (no new tasks).
        
        Args:
            worker_id: Worker ID
        """
        worker = self.workers.get(worker_id)
        if not worker:
            raise ValueError(f"Worker not found: {worker_id}")
        
        self._transition(worker_id, WorkerState.DRAINING)
        
        # Remove from idle queue
        if worker_id in self.idle_queue:
            self.idle_queue.remove(worker_id)
        
        # Persist
        self._persist_worker(worker)
    
    def terminate_worker(self, worker_id: str) -> None:
        """Transition worker to TERMINATED.
        
        Args:
            worker_id: Worker ID
        """
        worker = self.workers.get(worker_id)
        if not worker:
            raise ValueError(f"Worker not found: {worker_id}")
        
        worker.terminated_at = datetime.now(timezone.utc)
        worker.current_task_id = None
        self._transition(worker_id, WorkerState.TERMINATED)
        
        # Terminate actual process if enabled
        if self.enable_processes and self.process_spawner:
            self.process_spawner.terminate_worker_process(worker_id)
        
        # Remove from idle queue
        if worker_id in self.idle_queue:
            self.idle_queue.remove(worker_id)
        
        # Persist
        self._persist_worker(worker)
    
    def get_idle_worker(self, adapter_type: Optional[str] = None) -> Optional[Worker]:
        """Get next available idle worker.
        
        Args:
            adapter_type: Optional filter by adapter type
            
        Returns:
            Worker instance or None if no idle workers
        """
        for worker_id in self.idle_queue:
            worker = self.workers.get(worker_id)
            if not worker or worker.state != WorkerState.IDLE:
                continue
            
            if adapter_type and worker.adapter_type != adapter_type:
                continue
            
            return worker
        
        return None
    
    def heartbeat(self, worker_id: str) -> None:
        """Update worker heartbeat timestamp.
        
        Args:
            worker_id: Worker ID
        """
        worker = self.workers.get(worker_id)
        if not worker:
            return
        
        worker.heartbeat_at = datetime.now(timezone.utc)
        
        # Persist to DB
        from modules.core_state.m010003_db import get_connection
        conn = get_connection()
        try:
            conn.execute(
                "UPDATE workers SET heartbeat_at = ? WHERE worker_id = ?",
                (worker.heartbeat_at.isoformat(), worker_id)
            )
            conn.commit()
        finally:
            conn.close()
    
    def check_heartbeats(self, timeout_sec: int = 300) -> List[str]:
        """Return worker_ids with stale heartbeats.
        
        Args:
            timeout_sec: Heartbeat timeout in seconds (default 5 min)
            
        Returns:
            List of worker IDs with stale heartbeats
        """
        stale = []
        now = datetime.now(timezone.utc)
        
        for worker_id, worker in self.workers.items():
            if worker.state == WorkerState.TERMINATED:
                continue
            
            if not worker.heartbeat_at:
                stale.append(worker_id)
                continue
            
            elapsed = (now - worker.heartbeat_at).total_seconds()
            if elapsed > timeout_sec:
                stale.append(worker_id)
        
        return stale
    
    def _transition(self, worker_id: str, new_state: WorkerState) -> None:
        """Internal state transition with validation.
        
        Args:
            worker_id: Worker ID
            new_state: New state
        """
        worker = self.workers[worker_id]
        old_state = worker.state
        
        # Validate transition
        valid_transitions = {
            WorkerState.SPAWNING: {WorkerState.IDLE, WorkerState.TERMINATED},
            WorkerState.IDLE: {WorkerState.BUSY, WorkerState.DRAINING, WorkerState.TERMINATED},
            WorkerState.BUSY: {WorkerState.IDLE, WorkerState.TERMINATED},
            WorkerState.DRAINING: {WorkerState.TERMINATED},
            WorkerState.TERMINATED: set(),  # Terminal state
        }
        
        if new_state not in valid_transitions.get(old_state, set()):
            raise ValueError(
                f"Invalid state transition for worker {worker_id}: "
                f"{old_state.value} -> {new_state.value}"
            )
        
        worker.state = new_state
    
    def _persist_worker(self, worker: Worker) -> None:
        """Persist worker to database.
        
        Args:
            worker: Worker instance
        """
        from modules.core_state.m010003_db import get_connection
        import json
        
        conn = get_connection()
        try:
            conn.execute("""
                INSERT OR REPLACE INTO workers 
                (worker_id, adapter_type, state, current_task_id, sandbox_path, 
                 heartbeat_at, spawned_at, terminated_at, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                worker.worker_id,
                worker.adapter_type,
                worker.state.value,
                worker.current_task_id,
                worker.sandbox_path,
                worker.heartbeat_at.isoformat() if worker.heartbeat_at else None,
                worker.spawned_at.isoformat() if worker.spawned_at else None,
                worker.terminated_at.isoformat() if worker.terminated_at else None,
                json.dumps(worker.metadata) if worker.metadata else None
            ))
            conn.commit()
        finally:
            conn.close()
