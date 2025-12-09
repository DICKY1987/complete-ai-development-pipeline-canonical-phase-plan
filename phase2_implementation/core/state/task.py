"""
Task State Machine implementation.

Implements the Task state machine per SSOT §1.4.
Tasks are the atomic units of work in the pipeline.

States: PENDING, QUEUED, BLOCKED, RUNNING, VALIDATING, COMPLETED, FAILED, RETRYING, CANCELLED
Reference: DOC-SSOT-STATE-MACHINES-001 §1.4
"""

from typing import Dict, Set, Optional, List
from datetime import datetime, timezone

from .base import BaseState, BaseStateMachine


class TaskState(BaseState):
    """
    Task lifecycle states per SSOT §1.4.1.

    - PENDING: Waiting for dependencies
    - QUEUED: Ready for execution
    - BLOCKED: Dependency failed/gate blocked
    - RUNNING: Currently executing
    - VALIDATING: Execution complete, validating results
    - COMPLETED: Successfully finished
    - FAILED: Failed permanently
    - RETRYING: Scheduled for retry
    - CANCELLED: Manually cancelled
    """

    PENDING = "pending"
    QUEUED = "queued"
    BLOCKED = "blocked"
    RUNNING = "running"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"

    @classmethod
    def get_terminal_states(cls) -> Set["TaskState"]:
        """Terminal states: COMPLETED, FAILED, CANCELLED."""
        return {cls.COMPLETED, cls.FAILED, cls.CANCELLED}

    @classmethod
    def get_valid_transitions(cls) -> Dict["TaskState", Set["TaskState"]]:
        """
        Valid transitions per SSOT §1.4.4.

        PENDING → QUEUED (dependencies met)
        PENDING → BLOCKED (dependency failed)
        QUEUED → RUNNING (worker assigned)
        BLOCKED → PENDING (retry dependency)
        RUNNING → VALIDATING (execution complete)
        RUNNING → RETRYING (transient failure)
        RUNNING → FAILED (permanent failure)
        RUNNING → CANCELLED (user cancellation)
        VALIDATING → COMPLETED (validation passed)
        VALIDATING → FAILED (validation failed)
        RETRYING → QUEUED (retry scheduled)
        """
        return {
            cls.PENDING: {cls.QUEUED, cls.BLOCKED},
            cls.QUEUED: {cls.RUNNING, cls.CANCELLED},
            cls.BLOCKED: {cls.PENDING, cls.CANCELLED},
            cls.RUNNING: {cls.VALIDATING, cls.RETRYING, cls.FAILED, cls.CANCELLED},
            cls.VALIDATING: {cls.COMPLETED, cls.FAILED},
            cls.RETRYING: {cls.QUEUED},
            cls.COMPLETED: set(),
            cls.FAILED: set(),
            cls.CANCELLED: set(),
        }


class TaskStateMachine(BaseStateMachine):
    """
    Task state machine for work execution tracking.

    Manages individual task lifecycle per SSOT §1.4.
    """

    def __init__(
        self,
        task_id: str,
        workstream_id: str,
        metadata: Optional[Dict] = None,
        max_retries: int = 3,
    ):
        """
        Initialize Task state machine.

        Args:
            task_id: Unique task identifier
            workstream_id: Parent workstream ID
            metadata: Optional task metadata
            max_retries: Maximum retry attempts
        """
        super().__init__(
            entity_id=task_id,
            entity_type="task",
            initial_state=TaskState.PENDING,
            metadata=metadata or {},
        )

        self.task_id = task_id
        self.workstream_id = workstream_id
        self.max_retries = max_retries

        # Execution tracking
        self.worker_id: Optional[str] = None
        self.retry_count = 0
        self.is_critical = False

        # Timestamps
        self.queued_at: Optional[datetime] = None
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

        # Dependencies
        self.task_dependencies: List[str] = []
        self.gate_dependencies: List[str] = []

    def queue(self, reason: str = "Dependencies satisfied"):
        """
        Transition to QUEUED state.

        Args:
            reason: Reason for queuing
        """
        self.transition(TaskState.QUEUED, reason=reason, trigger="dependencies_met")
        self.queued_at = datetime.now(timezone.utc)

    def block(self, reason: str):
        """
        Block task due to dependency failure.

        Args:
            reason: Reason for blocking
        """
        self.transition(TaskState.BLOCKED, reason=reason, trigger="dependency_failed")

    def unblock(self, reason: str = "Dependency recovered"):
        """
        Unblock task to retry.

        Args:
            reason: Reason for unblocking
        """
        self.transition(
            TaskState.PENDING, reason=reason, trigger="dependency_recovered"
        )

    def assign_worker(self, worker_id: str):
        """
        Assign task to worker and start execution.

        Args:
            worker_id: ID of assigned worker
        """
        self.worker_id = worker_id
        self.transition(
            TaskState.RUNNING,
            reason=f"Assigned to worker {worker_id}",
            trigger="worker_assigned",
        )
        self.started_at = datetime.now(timezone.utc)

    def begin_validation(self):
        """Begin validation of task results."""
        self.transition(
            TaskState.VALIDATING,
            reason="Execution complete, validating results",
            trigger="execution_complete",
        )

    def complete(self, reason: str = "Validation passed"):
        """
        Mark task as successfully completed.

        Args:
            reason: Completion reason
        """
        self.transition(TaskState.COMPLETED, reason=reason, trigger="validation_passed")
        self.completed_at = datetime.now(timezone.utc)
        self.worker_id = None

    def fail(self, reason: str, error: Optional[str] = None, is_permanent: bool = True):
        """
        Mark task as failed.

        Args:
            reason: Failure reason
            error: Error details
            is_permanent: If False and retries available, will retry
        """
        if error:
            self.metadata["last_error"] = error

        # Check if should retry
        if not is_permanent and self.retry_count < self.max_retries:
            self.retry(reason=reason)
        else:
            self.transition(TaskState.FAILED, reason=reason, trigger="task_failed")
            self.completed_at = datetime.now(timezone.utc)
            self.worker_id = None

    def retry(self, reason: str):
        """
        Schedule task for retry.

        Args:
            reason: Retry reason
        """
        self.retry_count += 1
        self.transition(
            TaskState.RETRYING,
            reason=f"{reason} (retry {self.retry_count}/{self.max_retries})",
            trigger="retry_scheduled",
        )
        self.worker_id = None

        # Auto-transition to queued after marking retry
        self.transition(
            TaskState.QUEUED,
            reason=f"Retry {self.retry_count} queued",
            trigger="retry_queued",
        )

    def cancel(self, reason: str, operator: Optional[str] = None):
        """
        Cancel task execution.

        Args:
            reason: Cancellation reason
            operator: User who cancelled
        """
        self.transition(
            TaskState.CANCELLED,
            reason=reason,
            trigger="task_cancelled",
            operator=operator,
        )
        self.completed_at = datetime.now(timezone.utc)
        self.worker_id = None

    def set_dependencies(self, tasks: List[str] = None, gates: List[str] = None):
        """
        Set task dependencies.

        Args:
            tasks: List of task IDs this depends on
            gates: List of gate IDs that must pass
        """
        if tasks is not None:
            self.task_dependencies = tasks
        if gates is not None:
            self.gate_dependencies = gates

    def get_execution_info(self) -> Dict:
        """
        Get task execution information.

        Returns:
            Dictionary with execution details
        """
        info = {
            "task_id": self.task_id,
            "workstream_id": self.workstream_id,
            "state": self.current_state.value,
            "worker_id": self.worker_id,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "is_critical": self.is_critical,
            "is_terminal": self.is_terminal(),
            "queued_at": self.queued_at.isoformat() if self.queued_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "task_dependencies": self.task_dependencies,
            "gate_dependencies": self.gate_dependencies,
        }

        # Calculate execution time
        if self.started_at and self.completed_at:
            duration = (self.completed_at - self.started_at).total_seconds()
            info["execution_time_seconds"] = duration

        return info

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"TaskStateMachine(id={self.task_id}, "
            f"state={self.current_state.value}, "
            f"worker={self.worker_id}, "
            f"retries={self.retry_count}/{self.max_retries})"
        )
