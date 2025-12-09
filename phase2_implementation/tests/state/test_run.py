"""
Unit tests for Run State Machine.

Tests all valid and invalid transitions per SSOT §4.1.

Reference: DOC-SSOT-STATE-MACHINES-001 §1.2, §4.1
"""

import pytest
from datetime import datetime

from core.state.run import RunState, RunStateMachine
from core.state.base import StateTransitionError


class TestRunStateDefinitions:
    """Test run state definitions."""
    
    def test_initial_state_is_initializing(self):
        """Run starts in INITIALIZING state."""
        run = RunStateMachine("run-001")
        assert run.current_state == RunState.INITIALIZING
    
    def test_terminal_states(self):
        """Run has COMPLETED and FAILED as terminal states."""
        terminals = RunState.get_terminal_states()
        assert RunState.COMPLETED in terminals
        assert RunState.FAILED in terminals
        assert len(terminals) == 2


class TestRunValidTransitions:
    """Test all valid state transitions per SSOT §1.2.4."""
    
    def test_initializing_to_running(self):
        """INITIALIZING → RUNNING on start."""
        run = RunStateMachine("run-001")
        run.start()
        
        assert run.current_state == RunState.RUNNING
        assert run.started_at is not None
    
    def test_initializing_to_failed(self):
        """INITIALIZING → FAILED on setup failure."""
        run = RunStateMachine("run-001")
        run.fail("Setup failed")
        
        assert run.current_state == RunState.FAILED
        assert run.completed_at is not None
    
    def test_running_to_paused(self):
        """RUNNING → PAUSED on pause."""
        run = RunStateMachine("run-001")
        run.start()
        run.pause(operator="admin")
        
        assert run.current_state == RunState.PAUSED
        assert run.paused_at is not None
    
    def test_running_to_completed(self):
        """RUNNING → COMPLETED on success."""
        run = RunStateMachine("run-001")
        run.start()
        run.complete()
        
        assert run.current_state == RunState.COMPLETED
        assert run.completed_at is not None
        assert run.is_terminal()
    
    def test_running_to_failed(self):
        """RUNNING → FAILED on error."""
        run = RunStateMachine("run-001")
        run.start()
        run.fail("Critical error", error="Database connection lost")
        
        assert run.current_state == RunState.FAILED
        assert run.metadata['last_error'] == "Database connection lost"
    
    def test_paused_to_running(self):
        """PAUSED → RUNNING on resume."""
        run = RunStateMachine("run-001")
        run.start()
        run.pause()
        run.resume(operator="admin")
        
        assert run.current_state == RunState.RUNNING
        assert run.resumed_at is not None
    
    def test_paused_to_failed(self):
        """PAUSED → FAILED on abort."""
        run = RunStateMachine("run-001")
        run.start()
        run.pause()
        run.fail("Aborted by user")
        
        assert run.current_state == RunState.FAILED


class TestRunInvalidTransitions:
    """Test that invalid transitions are prevented."""
    
    def test_initializing_to_paused_invalid(self):
        """INITIALIZING → PAUSED is not valid."""
        run = RunStateMachine("run-001")
        
        with pytest.raises(StateTransitionError):
            run.transition(RunState.PAUSED)
    
    def test_initializing_to_completed_invalid(self):
        """INITIALIZING → COMPLETED is not valid."""
        run = RunStateMachine("run-001")
        
        with pytest.raises(StateTransitionError):
            run.transition(RunState.COMPLETED)
    
    def test_running_to_initializing_invalid(self):
        """RUNNING → INITIALIZING is not valid (no backward)."""
        run = RunStateMachine("run-001")
        run.start()
        
        with pytest.raises(StateTransitionError):
            run.transition(RunState.INITIALIZING)
    
    def test_completed_is_terminal(self):
        """COMPLETED state cannot transition."""
        run = RunStateMachine("run-001")
        run.start()
        run.complete()
        
        with pytest.raises(StateTransitionError):
            run.transition(RunState.RUNNING)
    
    def test_failed_is_terminal(self):
        """FAILED state cannot transition."""
        run = RunStateMachine("run-001")
        run.start()
        run.fail("Error")
        
        with pytest.raises(StateTransitionError):
            run.transition(RunState.RUNNING)


class TestRunProgressTracking:
    """Test run progress tracking functionality."""
    
    def test_workstream_count_updates(self):
        """Can update workstream counts."""
        run = RunStateMachine("run-001")
        run.update_workstream_counts(total=10, completed=3, failed=1)
        
        assert run.total_workstreams == 10
        assert run.completed_workstreams == 3
        assert run.failed_workstreams == 1
    
    def test_progress_calculation(self):
        """Progress percentage calculated correctly."""
        run = RunStateMachine("run-001")
        run.start()
        run.update_workstream_counts(total=10, completed=5)
        
        progress = run.get_progress()
        
        assert progress['completion_percentage'] == 50.0
        assert progress['total_workstreams'] == 10
        assert progress['completed_workstreams'] == 5
    
    def test_progress_with_no_workstreams(self):
        """Progress is 0% when no workstreams."""
        run = RunStateMachine("run-001")
        
        progress = run.get_progress()
        assert progress['completion_percentage'] == 0.0
    
    def test_duration_tracking(self):
        """Run duration is tracked."""
        run = RunStateMachine("run-001")
        run.start()
        
        progress = run.get_progress()
        
        assert 'duration_seconds' in progress
        assert progress['duration_seconds'] >= 0


class TestRunMetadata:
    """Test run metadata handling."""
    
    def test_custom_metadata(self):
        """Can provide custom metadata."""
        metadata = {
            'pipeline_version': '2.0',
            'triggered_by': 'github_webhook'
        }
        run = RunStateMachine("run-001", metadata=metadata)
        
        assert run.metadata['pipeline_version'] == '2.0'
        assert run.metadata['triggered_by'] == 'github_webhook'
    
    def test_error_metadata(self):
        """Error details stored in metadata."""
        run = RunStateMachine("run-001")
        run.start()
        run.fail("Error", error="Stack trace here")
        
        assert 'last_error' in run.metadata
        assert run.metadata['last_error'] == "Stack trace here"


class TestRunStateHistory:
    """Test state history tracking."""
    
    def test_complete_lifecycle_history(self):
        """State history tracks complete lifecycle."""
        run = RunStateMachine("run-001")
        
        run.start()
        run.pause()
        run.resume()
        run.complete()
        
        history = run.get_state_history()
        
        # Should have: INITIALIZING, RUNNING, PAUSED, RUNNING, COMPLETED
        assert len(history) == 5
        assert history[0][0] == "initializing"
        assert history[-1][0] == "completed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
