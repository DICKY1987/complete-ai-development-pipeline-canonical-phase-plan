"""
Unit tests for Task State Machine.

Tests all valid and invalid transitions per SSOT §4.1.

Reference: DOC-SSOT-STATE-MACHINES-001 §1.4, §4.1
"""

import pytest

from core.state.task import TaskState, TaskStateMachine
from core.state.base import StateTransitionError


class TestTaskStateDefinitions:
    """Test task state definitions."""

    def test_initial_state_is_pending(self):
        """Task starts in PENDING state."""
        task = TaskStateMachine("task-001", "ws-001")
        assert task.current_state == TaskState.PENDING

    def test_terminal_states(self):
        """Task has COMPLETED, FAILED, CANCELLED as terminal."""
        terminals = TaskState.get_terminal_states()
        assert TaskState.COMPLETED in terminals
        assert TaskState.FAILED in terminals
        assert TaskState.CANCELLED in terminals
        assert len(terminals) == 3


class TestTaskValidTransitions:
    """Test all valid state transitions per SSOT §1.4.4."""

    def test_pending_to_queued(self):
        """PENDING → QUEUED when dependencies met."""
        task = TaskStateMachine("task-001", "ws-001")
        task.queue()

        assert task.current_state == TaskState.QUEUED
        assert task.queued_at is not None

    def test_pending_to_blocked(self):
        """PENDING → BLOCKED when dependency fails."""
        task = TaskStateMachine("task-001", "ws-001")
        task.block("Dependency task failed")

        assert task.current_state == TaskState.BLOCKED

    def test_queued_to_running(self):
        """QUEUED → RUNNING when worker assigned."""
        task = TaskStateMachine("task-001", "ws-001")
        task.queue()
        task.assign_worker("worker-123")

        assert task.current_state == TaskState.RUNNING
        assert task.worker_id == "worker-123"
        assert task.started_at is not None

    def test_blocked_to_pending(self):
        """BLOCKED → PENDING when dependency recovers."""
        task = TaskStateMachine("task-001", "ws-001")
        task.block("Dependency failed")
        task.unblock()

        assert task.current_state == TaskState.PENDING

    def test_running_to_validating(self):
        """RUNNING → VALIDATING when execution completes."""
        task = TaskStateMachine("task-001", "ws-001")
        task.queue()
        task.assign_worker("worker-123")
        task.begin_validation()

        assert task.current_state == TaskState.VALIDATING

    def test_running_to_retrying(self):
        """RUNNING → RETRYING on transient failure."""
        task = TaskStateMachine("task-001", "ws-001", max_retries=3)
        task.queue()
        task.assign_worker("worker-123")
        task.retry("Transient network error")

        # After retry, should auto-transition to QUEUED
        assert task.current_state == TaskState.QUEUED
        assert task.retry_count == 1
        assert task.worker_id is None

    def test_running_to_failed(self):
        """RUNNING → FAILED on permanent failure."""
        task = TaskStateMachine("task-001", "ws-001")
        task.queue()
        task.assign_worker("worker-123")
        task.fail("Permanent error", error="Invalid input", is_permanent=True)

        assert task.current_state == TaskState.FAILED
        assert task.is_terminal()
        assert task.metadata["last_error"] == "Invalid input"

    def test_running_to_cancelled(self):
        """RUNNING → CANCELLED on user cancellation."""
        task = TaskStateMachine("task-001", "ws-001")
        task.queue()
        task.assign_worker("worker-123")
        task.cancel("User cancelled", operator="admin")

        assert task.current_state == TaskState.CANCELLED
        assert task.is_terminal()

    def test_validating_to_completed(self):
        """VALIDATING → COMPLETED when validation passes."""
        task = TaskStateMachine("task-001", "ws-001")
        task.queue()
        task.assign_worker("worker-123")
        task.begin_validation()
        task.complete()

        assert task.current_state == TaskState.COMPLETED
        assert task.completed_at is not None
        assert task.worker_id is None

    def test_validating_to_failed(self):
        """VALIDATING → FAILED when validation fails."""
        task = TaskStateMachine("task-001", "ws-001")
        task.queue()
        task.assign_worker("worker-123")
        task.begin_validation()
        task.fail("Validation failed", is_permanent=True)

        assert task.current_state == TaskState.FAILED


class TestTaskInvalidTransitions:
    """Test that invalid transitions are prevented."""

    def test_pending_to_running_invalid(self):
        """PENDING → RUNNING is invalid (must queue first)."""
        task = TaskStateMachine("task-001", "ws-001")

        with pytest.raises(StateTransitionError):
            task.transition(TaskState.RUNNING)

    def test_queued_to_completed_invalid(self):
        """QUEUED → COMPLETED is invalid (must execute first)."""
        task = TaskStateMachine("task-001", "ws-001")
        task.queue()

        with pytest.raises(StateTransitionError):
            task.transition(TaskState.COMPLETED)

    def test_running_to_completed_invalid(self):
        """RUNNING → COMPLETED is invalid (must validate first)."""
        task = TaskStateMachine("task-001", "ws-001")
        task.queue()
        task.assign_worker("worker-123")

        with pytest.raises(StateTransitionError):
            task.transition(TaskState.COMPLETED)


class TestTaskRetryLogic:
    """Test task retry functionality."""

    def test_retry_increments_count(self):
        """Retry count increments on each retry."""
        task = TaskStateMachine("task-001", "ws-001", max_retries=3)
        task.queue()
        task.assign_worker("worker-123")

        task.retry("Error 1")
        assert task.retry_count == 1

        task.assign_worker("worker-456")
        task.retry("Error 2")
        assert task.retry_count == 2

    def test_max_retries_reached_fails(self):
        """Task fails permanently when max retries reached."""
        task = TaskStateMachine("task-001", "ws-001", max_retries=2)
        task.queue()
        task.assign_worker("worker-123")

        # First failure - retry
        task.fail("Error", is_permanent=False)
        assert task.current_state == TaskState.QUEUED
        assert task.retry_count == 1

        # Second failure - retry again
        task.assign_worker("worker-123")
        task.fail("Error", is_permanent=False)
        assert task.current_state == TaskState.QUEUED
        assert task.retry_count == 2

        # Third failure - max retries reached, fail permanently
        task.assign_worker("worker-123")
        task.fail("Error", is_permanent=False)
        assert task.current_state == TaskState.FAILED
        assert task.retry_count == 2  # Doesn't increment past max

    def test_permanent_failure_skips_retry(self):
        """Permanent failures don't retry."""
        task = TaskStateMachine("task-001", "ws-001", max_retries=3)
        task.queue()
        task.assign_worker("worker-123")

        task.fail("Permanent error", is_permanent=True)

        assert task.current_state == TaskState.FAILED
        assert task.retry_count == 0


class TestTaskDependencies:
    """Test task dependency management."""

    def test_set_task_dependencies(self):
        """Can set task dependencies."""
        task = TaskStateMachine("task-001", "ws-001")
        task.set_dependencies(tasks=["task-000", "task-002"])

        assert task.task_dependencies == ["task-000", "task-002"]

    def test_set_gate_dependencies(self):
        """Can set gate dependencies."""
        task = TaskStateMachine("task-001", "ws-001")
        task.set_dependencies(gates=["gate-001", "gate-002"])

        assert task.gate_dependencies == ["gate-001", "gate-002"]

    def test_set_mixed_dependencies(self):
        """Can set both task and gate dependencies."""
        task = TaskStateMachine("task-001", "ws-001")
        task.set_dependencies(tasks=["task-000"], gates=["gate-001", "gate-002"])

        assert task.task_dependencies == ["task-000"]
        assert task.gate_dependencies == ["gate-001", "gate-002"]


class TestTaskExecutionInfo:
    """Test task execution information tracking."""

    def test_execution_info_complete_lifecycle(self):
        """Execution info tracks complete lifecycle."""
        task = TaskStateMachine("task-001", "ws-001")
        task.set_dependencies(tasks=["task-000"])

        task.queue()
        task.assign_worker("worker-123")
        task.begin_validation()
        task.complete()

        info = task.get_execution_info()

        assert info["task_id"] == "task-001"
        assert info["workstream_id"] == "ws-001"
        assert info["state"] == "completed"
        assert info["worker_id"] is None  # Cleared on completion
        assert info["is_terminal"] is True
        assert info["task_dependencies"] == ["task-000"]
        assert "execution_time_seconds" in info

    def test_execution_time_calculation(self):
        """Execution time calculated when task completes."""
        task = TaskStateMachine("task-001", "ws-001")
        task.queue()
        task.assign_worker("worker-123")
        task.begin_validation()
        task.complete()

        info = task.get_execution_info()
        assert "execution_time_seconds" in info
        assert info["execution_time_seconds"] >= 0


class TestTaskCancellation:
    """Test task cancellation from various states."""

    def test_cancel_from_queued(self):
        """Can cancel from QUEUED state."""
        task = TaskStateMachine("task-001", "ws-001")
        task.queue()
        task.cancel("Not needed", operator="admin")

        assert task.current_state == TaskState.CANCELLED

    def test_cancel_from_running(self):
        """Can cancel from RUNNING state."""
        task = TaskStateMachine("task-001", "ws-001")
        task.queue()
        task.assign_worker("worker-123")
        task.cancel("Taking too long", operator="admin")

        assert task.current_state == TaskState.CANCELLED
        assert task.worker_id is None

    def test_cancel_from_blocked(self):
        """Can cancel from BLOCKED state."""
        task = TaskStateMachine("task-001", "ws-001")
        task.block("Dependency failed")
        task.cancel("Give up on dependency")

        assert task.current_state == TaskState.CANCELLED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
