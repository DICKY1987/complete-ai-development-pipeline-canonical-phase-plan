"""
Run State Machine implementation.

Implements the top-level Run state machine per SSOT §1.2.
A Run represents a complete pipeline execution.

States: INITIALIZING, RUNNING, PAUSED, COMPLETED, FAILED
Reference: DOC-SSOT-STATE-MACHINES-001 §1.2
"""

from typing import Dict, Set, Optional
from datetime import datetime, timezone

from .base import BaseState, BaseStateMachine


class RunState(BaseState):
    """
    Run lifecycle states per SSOT §1.2.1.

    - INITIALIZING: Run setup in progress
    - RUNNING: Run actively executing
    - PAUSED: Run temporarily paused
    - COMPLETED: Run finished successfully
    - FAILED: Run terminated with errors
    """

    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"

    @classmethod
    def get_terminal_states(cls) -> Set["RunState"]:
        """Terminal states: COMPLETED, FAILED."""
        return {cls.COMPLETED, cls.FAILED}

    @classmethod
    def get_valid_transitions(cls) -> Dict["RunState", Set["RunState"]]:
        """
        Valid transitions per SSOT §1.2.4.

        INITIALIZING → RUNNING (setup complete)
        RUNNING → PAUSED (manual pause)
        RUNNING → COMPLETED (all workstreams complete)
        RUNNING → FAILED (critical failure)
        PAUSED → RUNNING (resume)
        PAUSED → FAILED (abort while paused)
        """
        return {
            cls.INITIALIZING: {cls.RUNNING, cls.FAILED},
            cls.RUNNING: {cls.PAUSED, cls.COMPLETED, cls.FAILED},
            cls.PAUSED: {cls.RUNNING, cls.FAILED},
            cls.COMPLETED: set(),  # Terminal
            cls.FAILED: set(),  # Terminal
        }


class RunStateMachine(BaseStateMachine):
    """
    Run state machine for pipeline execution tracking.

    Manages the top-level run lifecycle per SSOT §1.2.
    """

    def __init__(self, run_id: str, metadata: Optional[Dict] = None):
        """
        Initialize Run state machine.

        Args:
            run_id: Unique run identifier
            metadata: Optional run metadata
        """
        super().__init__(
            entity_id=run_id,
            entity_type="run",
            initial_state=RunState.INITIALIZING,
            metadata=metadata or {},
        )

        self.run_id = run_id
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.paused_at: Optional[datetime] = None
        self.resumed_at: Optional[datetime] = None

        # Workstream tracking
        self.total_workstreams = 0
        self.completed_workstreams = 0
        self.failed_workstreams = 0

    def start(self, reason: str = "Run initialization complete"):
        """
        Transition from INITIALIZING to RUNNING.

        Args:
            reason: Reason for starting
        """
        self.transition(RunState.RUNNING, reason=reason, trigger="run_started")
        self.started_at = datetime.now(timezone.utc)

    def pause(self, reason: str = "Manual pause", operator: str = None):
        """
        Pause the run.

        Args:
            reason: Reason for pausing
            operator: User who paused
        """
        self.transition(
            RunState.PAUSED, reason=reason, trigger="run_paused", operator=operator
        )
        self.paused_at = datetime.now(timezone.utc)

    def resume(self, reason: str = "Manual resume", operator: str = None):
        """
        Resume from paused state.

        Args:
            reason: Reason for resuming
            operator: User who resumed
        """
        self.transition(
            RunState.RUNNING, reason=reason, trigger="run_resumed", operator=operator
        )
        self.resumed_at = datetime.now(timezone.utc)

    def complete(self, reason: str = "All workstreams completed"):
        """
        Mark run as completed.

        Args:
            reason: Completion reason
        """
        self.transition(RunState.COMPLETED, reason=reason, trigger="run_completed")
        self.completed_at = datetime.now(timezone.utc)

    def fail(self, reason: str, error: Optional[str] = None):
        """
        Mark run as failed.

        Args:
            reason: Failure reason
            error: Error message/details
        """
        if error:
            self.metadata["last_error"] = error

        self.transition(RunState.FAILED, reason=reason, trigger="run_failed")
        self.completed_at = datetime.now(timezone.utc)

    def update_workstream_counts(
        self,
        total: Optional[int] = None,
        completed: Optional[int] = None,
        failed: Optional[int] = None,
    ):
        """
        Update workstream progress counts.

        Args:
            total: Total workstreams (if changed)
            completed: Completed workstreams count
            failed: Failed workstreams count
        """
        if total is not None:
            self.total_workstreams = total
        if completed is not None:
            self.completed_workstreams = completed
        if failed is not None:
            self.failed_workstreams = failed

    def get_progress(self) -> Dict:
        """
        Get run progress statistics.

        Returns:
            Dictionary with progress metrics
        """
        progress = {
            "run_id": self.run_id,
            "state": self.current_state.value,
            "is_terminal": self.is_terminal(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "total_workstreams": self.total_workstreams,
            "completed_workstreams": self.completed_workstreams,
            "failed_workstreams": self.failed_workstreams,
        }

        # Calculate duration
        if self.started_at:
            end_time = self.completed_at or datetime.now(timezone.utc)
            duration = (end_time - self.started_at).total_seconds()
            progress["duration_seconds"] = duration

        # Calculate completion percentage
        if self.total_workstreams > 0:
            progress["completion_percentage"] = (
                self.completed_workstreams / self.total_workstreams
            ) * 100
        else:
            progress["completion_percentage"] = 0.0

        return progress

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"RunStateMachine(id={self.run_id}, "
            f"state={self.current_state.value}, "
            f"progress={self.completed_workstreams}/{self.total_workstreams})"
        )
