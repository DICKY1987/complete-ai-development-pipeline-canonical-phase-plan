"""
Worker State Machines implementation.

Implements worker state machines per SSOT §1.5 and §2.1.

Reference: DOC-SSOT-STATE-MACHINES-001 §1.5, §2.1
"""

from typing import Dict, Set, Optional
from datetime import datetime, timezone

from .base import BaseState, BaseStateMachine


class WorkerState(BaseState):
    """
    Worker lifecycle states per SSOT §1.5.1 / §2.1.1.
    """

    IDLE = "idle"
    BUSY = "busy"
    PAUSED = "paused"
    FAILED = "failed"
    SHUTDOWN = "shutdown"

    @classmethod
    def get_terminal_states(cls) -> Set["WorkerState"]:
        """Terminal state: SHUTDOWN."""
        return {cls.SHUTDOWN}

    @classmethod
    def get_valid_transitions(cls) -> Dict["WorkerState", Set["WorkerState"]]:
        """Valid transitions per SSOT §1.5.4 / §2.1.4."""
        return {
            cls.IDLE: {cls.BUSY, cls.PAUSED, cls.SHUTDOWN},
            cls.BUSY: {cls.IDLE, cls.FAILED, cls.SHUTDOWN},
            cls.PAUSED: {cls.IDLE, cls.SHUTDOWN},
            cls.FAILED: {cls.IDLE, cls.SHUTDOWN},
            cls.SHUTDOWN: set(),
        }


class WorkerStateMachine(BaseStateMachine):
    """
    Worker state machine for worker lifecycle tracking.
    """

    def __init__(
        self,
        worker_id: str,
        worker_type: str = "orchestration",
        metadata: Optional[Dict] = None,
    ):
        super().__init__(
            entity_id=worker_id,
            entity_type="worker",
            initial_state=WorkerState.IDLE,
            metadata=metadata or {},
        )

        self.worker_id = worker_id
        self.worker_type = worker_type
        self.current_task_id: Optional[str] = None
        self.last_heartbeat: Optional[datetime] = None

    def assign_task(self, task_id: str):
        """Assign task to worker."""
        self.current_task_id = task_id
        self.transition(
            WorkerState.BUSY, reason=f"Assigned task {task_id}", trigger="task_assigned"
        )

    def complete_task(self):
        """Complete current task."""
        self.current_task_id = None
        self.transition(
            WorkerState.IDLE, reason="Task completed", trigger="task_completed"
        )

    def pause(self):
        """Pause worker."""
        self.transition(WorkerState.PAUSED, reason="Worker paused", trigger="paused")

    def resume(self):
        """Resume worker."""
        self.transition(WorkerState.IDLE, reason="Worker resumed", trigger="resumed")

    def fail(self, reason: str):
        """Mark worker as failed."""
        self.transition(WorkerState.FAILED, reason=reason, trigger="worker_failed")
        self.current_task_id = None

    def recover(self):
        """Recover from failed state."""
        self.transition(
            WorkerState.IDLE, reason="Worker recovered", trigger="recovered"
        )

    def shutdown(self):
        """Shutdown worker."""
        self.transition(
            WorkerState.SHUTDOWN, reason="Worker shutdown", trigger="shutdown"
        )
        self.current_task_id = None

    def heartbeat(self):
        """Record worker heartbeat."""
        self.last_heartbeat = datetime.now(timezone.utc)

    def is_healthy(self, timeout_seconds: int = 60) -> bool:
        """Check if worker is healthy based on heartbeat."""
        if not self.last_heartbeat:
            return False

        elapsed = (datetime.now(timezone.utc) - self.last_heartbeat).total_seconds()
        return elapsed < timeout_seconds
