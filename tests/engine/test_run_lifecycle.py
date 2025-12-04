"""Tests for Run Lifecycle - WS-03-01A"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add framework root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.state.db import Database
from core.engine.orchestrator import Orchestrator
from core.engine.state_machine import RunStateMachine, StepStateMachine


@pytest.fixture
def test_db(tmp_path):
    """Create a temporary test database"""
# DOC_ID: DOC-TEST-ENGINE-TEST-RUN-LIFECYCLE-176
    db_path = tmp_path / "test.db"
    db = Database(str(db_path))
    db.connect()
    yield db
    db.close()


@pytest.fixture
def orchestrator(test_db):
    """Create orchestrator with test database"""
    return Orchestrator(test_db)


class TestRunLifecycle:
    """Test run state machine and lifecycle"""

    def test_create_run(self, orchestrator):
        """Test creating a new run"""
        run_id = orchestrator.create_run(
            project_id="PRJ-TEST",
            phase_id="PH-01",
            workstream_id="WS-01-01A"
        )

        assert run_id is not None

        # Verify run was created
        run = orchestrator.get_run_status(run_id)
        assert run is not None
        assert run['project_id'] == "PRJ-TEST"
        assert run['phase_id'] == "PH-01"
        assert run['workstream_id'] == "WS-01-01A"
        assert run['state'] == 'pending'
        assert run['created_at'] is not None

    def test_start_run(self, orchestrator):
        """Test starting a pending run"""
        run_id = orchestrator.create_run("PRJ-TEST", "PH-01")

        # Start the run
        result = orchestrator.start_run(run_id)
        assert result is True

        # Verify state changed
        run = orchestrator.get_run_status(run_id)
        assert run['state'] == 'running'
        assert run['started_at'] is not None

    def test_complete_run_success(self, orchestrator):
        """Test completing a run successfully"""
        run_id = orchestrator.create_run("PRJ-TEST", "PH-01")
        orchestrator.start_run(run_id)

        # Complete successfully
        result = orchestrator.complete_run(run_id, 'succeeded', exit_code=0)
        assert result is True

        # Verify final state
        run = orchestrator.get_run_status(run_id)
        assert run['state'] == 'succeeded'
        assert run['ended_at'] is not None
        assert run['exit_code'] == 0

    def test_complete_run_failure(self, orchestrator):
        """Test completing a run with failure"""
        run_id = orchestrator.create_run("PRJ-TEST", "PH-01")
        orchestrator.start_run(run_id)

        # Complete with failure
        result = orchestrator.complete_run(
            run_id, 'failed',
            exit_code=1,
            error_message="Test failed"
        )
        assert result is True

        # Verify final state
        run = orchestrator.get_run_status(run_id)
        assert run['state'] == 'failed'
        assert run['exit_code'] == 1
        assert run['error_message'] == "Test failed"

    def test_quarantine_run(self, orchestrator):
        """Test quarantining a run"""
        run_id = orchestrator.create_run("PRJ-TEST", "PH-01")
        orchestrator.start_run(run_id)

        # Quarantine
        result = orchestrator.quarantine_run(run_id, "Safety violation")
        assert result is True

        # Verify state
        run = orchestrator.get_run_status(run_id)
        assert run['state'] == 'quarantined'
        assert run['error_message'] == "Safety violation"

    def test_cancel_run(self, orchestrator):
        """Test canceling a run"""
        run_id = orchestrator.create_run("PRJ-TEST", "PH-01")

        # Cancel before starting
        result = orchestrator.cancel_run(run_id, "User requested")
        assert result is True

        # Verify state
        run = orchestrator.get_run_status(run_id)
        assert run['state'] == 'canceled'
        assert run['error_message'] == "User requested"

    def test_invalid_state_transition(self, orchestrator):
        """Test that invalid transitions are rejected"""
        run_id = orchestrator.create_run("PRJ-TEST", "PH-01")

        # Try to complete without starting (pending -> succeeded)
        with pytest.raises(ValueError, match="Invalid transition"):
            orchestrator.complete_run(run_id, 'succeeded')

    def test_terminal_state_immutable(self, orchestrator):
        """Test that terminal states cannot be changed"""
        run_id = orchestrator.create_run("PRJ-TEST", "PH-01")
        orchestrator.start_run(run_id)
        orchestrator.complete_run(run_id, 'succeeded')

        # Try to transition from succeeded (terminal) to failed
        with pytest.raises(ValueError, match="terminal state"):
            orchestrator.complete_run(run_id, 'failed')


class TestStepAttempts:
    """Test step attempt management"""

    def test_create_step_attempt(self, orchestrator):
        """Test creating a step attempt"""
        run_id = orchestrator.create_run("PRJ-TEST", "PH-01")
        orchestrator.start_run(run_id)

        # Create step
        step_id = orchestrator.create_step_attempt(
            run_id=run_id,
            tool_id="aider",
            sequence=1,
            prompt="Test prompt"
        )

        assert step_id is not None

        # Verify step was created
        step = orchestrator.db.get_step_attempt(step_id)
        assert step is not None
        assert step['run_id'] == run_id
        assert step['tool_id'] == "aider"
        assert step['sequence'] == 1
        assert step['state'] == 'running'
        assert step['input_prompt'] == "Test prompt"

    def test_complete_step_success(self, orchestrator):
        """Test completing a step successfully"""
        run_id = orchestrator.create_run("PRJ-TEST", "PH-01")
        orchestrator.start_run(run_id)
        step_id = orchestrator.create_step_attempt(run_id, "aider", 1)

        # Complete step
        result = orchestrator.complete_step_attempt(
            step_id, 'succeeded',
            exit_code=0,
            output_patch_id="PATCH-001"
        )
        assert result is True

        # Verify state
        step = orchestrator.db.get_step_attempt(step_id)
        assert step['state'] == 'succeeded'
        assert step['exit_code'] == 0
        assert step['output_patch_id'] == "PATCH-001"
        assert step['ended_at'] is not None

    def test_complete_step_failure(self, orchestrator):
        """Test completing a step with failure"""
        run_id = orchestrator.create_run("PRJ-TEST", "PH-01")
        orchestrator.start_run(run_id)
        step_id = orchestrator.create_step_attempt(run_id, "aider", 1)

        # Complete with failure
        result = orchestrator.complete_step_attempt(
            step_id, 'failed',
            exit_code=1,
            error_log="Tool execution failed"
        )
        assert result is True

        # Verify state
        step = orchestrator.db.get_step_attempt(step_id)
        assert step['state'] == 'failed'
        assert step['exit_code'] == 1
        assert step['error_log'] == "Tool execution failed"

    def test_multiple_steps(self, orchestrator):
        """Test multiple sequential steps"""
        run_id = orchestrator.create_run("PRJ-TEST", "PH-01")
        orchestrator.start_run(run_id)

        # Create multiple steps
        step1_id = orchestrator.create_step_attempt(run_id, "aider", 1)
        step2_id = orchestrator.create_step_attempt(run_id, "codex", 2)
        step3_id = orchestrator.create_step_attempt(run_id, "aider", 3)

        # Get all steps for run
        steps = orchestrator.get_run_steps(run_id)
        assert len(steps) == 3
        assert steps[0]['sequence'] == 1
        assert steps[1]['sequence'] == 2
        assert steps[2]['sequence'] == 3


class TestEventEmission:
    """Test event emission and tracking"""

    def test_run_created_event(self, orchestrator):
        """Test that run_created event is emitted"""
        run_id = orchestrator.create_run("PRJ-TEST", "PH-01")

        events = orchestrator.get_run_events(run_id)
        assert len(events) >= 1

        created_event = events[0]
        assert created_event['event_type'] == 'run_created'
        assert created_event['run_id'] == run_id

    def test_run_started_event(self, orchestrator):
        """Test that run_started event is emitted"""
        run_id = orchestrator.create_run("PRJ-TEST", "PH-01")
        orchestrator.start_run(run_id)

        events = orchestrator.get_run_events(run_id)
        assert len(events) >= 2

        started_event = events[1]
        assert started_event['event_type'] == 'run_started'

    def test_run_completed_event(self, orchestrator):
        """Test that run_completed event is emitted"""
        run_id = orchestrator.create_run("PRJ-TEST", "PH-01")
        orchestrator.start_run(run_id)
        orchestrator.complete_run(run_id, 'succeeded')

        events = orchestrator.get_run_events(run_id)
        assert len(events) >= 3

        completed_event = events[2]
        assert completed_event['event_type'] == 'run_completed'
        assert completed_event['data']['status'] == 'succeeded'

    def test_step_events(self, orchestrator):
        """Test that step events are emitted"""
        run_id = orchestrator.create_run("PRJ-TEST", "PH-01")
        orchestrator.start_run(run_id)
        step_id = orchestrator.create_step_attempt(run_id, "aider", 1)
        orchestrator.complete_step_attempt(step_id, 'succeeded')

        events = orchestrator.get_run_events(run_id)

        # Should have: run_created, run_started, step_started, step_completed
        assert len(events) >= 4

        step_started = [e for e in events if e['event_type'] == 'step_started'][0]
        assert step_started['data']['step_attempt_id'] == step_id

        step_completed = [e for e in events if e['event_type'] == 'step_completed'][0]
        assert step_completed['data']['status'] == 'succeeded'


class TestQueryMethods:
    """Test query and listing methods"""

    def test_list_runs_by_project(self, orchestrator):
        """Test listing runs filtered by project"""
        # Create runs for different projects
        run1 = orchestrator.create_run("PRJ-A", "PH-01")
        run2 = orchestrator.create_run("PRJ-B", "PH-01")
        run3 = orchestrator.create_run("PRJ-A", "PH-02")

        # Query PRJ-A runs
        runs = orchestrator.list_runs(project_id="PRJ-A")
        assert len(runs) == 2
        assert all(r['project_id'] == "PRJ-A" for r in runs)

    def test_list_runs_by_state(self, orchestrator):
        """Test listing runs filtered by state"""
        run1 = orchestrator.create_run("PRJ-TEST", "PH-01")
        run2 = orchestrator.create_run("PRJ-TEST", "PH-01")
        orchestrator.start_run(run2)

        # Query pending runs
        pending = orchestrator.list_runs(state='pending')
        assert len(pending) == 1
        assert pending[0]['run_id'] == run1

        # Query running runs
        running = orchestrator.list_runs(state='running')
        assert len(running) == 1
        assert running[0]['run_id'] == run2


class TestStateMachine:
    """Test state machine logic"""

    def test_valid_run_transitions(self):
        """Test all valid run state transitions"""
        assert RunStateMachine.can_transition('pending', 'running') is True
        assert RunStateMachine.can_transition('running', 'succeeded') is True
        assert RunStateMachine.can_transition('running', 'failed') is True
        assert RunStateMachine.can_transition('failed', 'quarantined') is True
        assert RunStateMachine.can_transition('pending', 'canceled') is True

    def test_invalid_run_transitions(self):
        """Test invalid run state transitions"""
        assert RunStateMachine.can_transition('pending', 'succeeded') is False
        assert RunStateMachine.can_transition('succeeded', 'failed') is False
        assert RunStateMachine.can_transition('quarantined', 'running') is False

    def test_terminal_state_detection(self):
        """Test terminal state detection"""
        assert RunStateMachine.is_terminal('succeeded') is True
        assert RunStateMachine.is_terminal('quarantined') is True
        assert RunStateMachine.is_terminal('canceled') is True
        assert RunStateMachine.is_terminal('running') is False
        assert RunStateMachine.is_terminal('pending') is False

    def test_step_state_transitions(self):
        """Test step state machine"""
        assert StepStateMachine.can_transition('running', 'succeeded') is True
        assert StepStateMachine.can_transition('running', 'failed') is True
        assert StepStateMachine.can_transition('succeeded', 'failed') is False
