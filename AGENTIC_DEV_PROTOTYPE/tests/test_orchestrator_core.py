#!/usr/bin/env python3
"""
Test Suite for Orchestrator Core - PH-3B
"""

import json
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "orchestrator"))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from state_machine import StateMachine, PhaseState, StateTransitionError
from core import OrchestratorCore


class TestStateMachine:
    """Test state machine functionality."""
    
    @pytest.fixture
    def sm(self):
        """Create StateMachine instance."""
        return StateMachine()
    
    def test_initialization(self, sm):
        """Test state machine initialization."""
        assert sm.get_state() == PhaseState.NOT_STARTED
        assert len(sm.get_history()) == 0
    
    def test_valid_transition_not_started_to_queued(self, sm):
        """Test valid transition from NOT_STARTED to QUEUED."""
        assert sm.can_transition(PhaseState.NOT_STARTED, PhaseState.QUEUED)
        success = sm.transition(PhaseState.QUEUED, trigger="test")
        
        assert success is True
        assert sm.get_state() == PhaseState.QUEUED
        assert len(sm.get_history()) == 1
    
    def test_valid_transition_queued_to_running(self, sm):
        """Test valid transition from QUEUED to RUNNING."""
        sm.transition(PhaseState.QUEUED)
        success = sm.transition(PhaseState.RUNNING)
        
        assert success is True
        assert sm.get_state() == PhaseState.RUNNING
    
    def test_valid_transition_running_to_complete(self, sm):
        """Test valid transition from RUNNING to COMPLETE."""
        sm.transition(PhaseState.QUEUED)
        sm.transition(PhaseState.RUNNING)
        success = sm.transition(PhaseState.COMPLETE)
        
        assert success is True
        assert sm.get_state() == PhaseState.COMPLETE
    
    def test_invalid_transition_queued_to_complete(self, sm):
        """Test invalid transition from QUEUED to COMPLETE."""
        sm.transition(PhaseState.QUEUED)
        
        with pytest.raises(StateTransitionError):
            sm.transition(PhaseState.COMPLETE)
    
    def test_invalid_transition_from_complete(self, sm):
        """Test that COMPLETE is a terminal state."""
        sm.transition(PhaseState.QUEUED)
        sm.transition(PhaseState.RUNNING)
        sm.transition(PhaseState.COMPLETE)
        
        with pytest.raises(StateTransitionError):
            sm.transition(PhaseState.RUNNING)
    
    def test_retry_after_failure(self, sm):
        """Test that failed phases can be retried."""
        sm.transition(PhaseState.QUEUED)
        sm.transition(PhaseState.RUNNING)
        sm.transition(PhaseState.FAILED)
        
        # Should be able to re-queue
        success = sm.transition(PhaseState.QUEUED, trigger="retry")
        assert success is True
    
    def test_transition_history(self, sm):
        """Test transition history tracking."""
        sm.transition(PhaseState.QUEUED, trigger="user action")
        sm.transition(PhaseState.RUNNING, trigger="auto start")
        
        history = sm.get_history()
        assert len(history) == 2
        assert history[0]["from_state"] == "not_started"
        assert history[0]["to_state"] == "queued"
        assert history[1]["from_state"] == "queued"
        assert history[1]["to_state"] == "running"
    
    def test_is_terminal(self, sm):
        """Test terminal state detection."""
        assert sm.is_terminal() is False
        
        sm.transition(PhaseState.QUEUED)
        assert sm.is_terminal() is False
        
        sm.transition(PhaseState.RUNNING)
        sm.transition(PhaseState.COMPLETE)
        assert sm.is_terminal() is True
    
    def test_reset(self, sm):
        """Test state machine reset."""
        sm.transition(PhaseState.QUEUED)
        sm.transition(PhaseState.RUNNING)
        
        sm.reset()
        
        assert sm.get_state() == PhaseState.NOT_STARTED
        assert len(sm.get_history()) == 0


class TestOrchestratorCore:
    """Test orchestrator core functionality."""
    
    @pytest.fixture
    def orchestrator(self, tmp_path):
        """Create OrchestratorCore instance with temp ledger."""
        ledger_dir = tmp_path / ".ledger"
        return OrchestratorCore(ledger_dir=str(ledger_dir))
    
    @pytest.fixture
    def sample_spec_file(self, tmp_path):
        """Create a sample phase spec file."""
        spec = {
            "phase_id": "PH-TEST",
            "workstream_id": "WS-TEST",
            "phase_name": "Test Phase",
            "objective": "Test objective for orchestrator testing and validation",
            "dependencies": [],
            "file_scope": ["test.py"],
            "pre_flight_checks": [],
            "acceptance_tests": [
                {"test_id": "AT-001", "description": "Test", "command": "test", "expected": "pass"},
                {"test_id": "AT-002", "description": "Test", "command": "test", "expected": "pass"},
                {"test_id": "AT-003", "description": "Test", "command": "test", "expected": "pass"}
            ],
            "deliverables": ["test output"],
            "estimated_effort_hours": 1
        }
        
        spec_file = tmp_path / "test_spec.json"
        with open(spec_file, 'w') as f:
            json.dump(spec, f)
        
        return str(spec_file)
    
    def test_initialization(self, orchestrator):
        """Test orchestrator initialization."""
        assert orchestrator.validator is not None
        assert orchestrator.prompt_renderer is not None
        assert orchestrator.ledger_dir.exists()
    
    def test_queue_phase(self, orchestrator, sample_spec_file):
        """Test queueing a phase."""
        success = orchestrator.queue_phase(sample_spec_file, force=True)
        
        assert success is True
        assert "PH-TEST" in orchestrator.state_machines
        assert orchestrator.state_machines["PH-TEST"].get_state() == PhaseState.QUEUED
    
    def test_queue_phase_creates_ledger(self, orchestrator, sample_spec_file):
        """Test that queueing creates a ledger file."""
        orchestrator.queue_phase(sample_spec_file, force=True)
        
        ledger_file = orchestrator.ledger_dir / "PH-TEST.json"
        assert ledger_file.exists()
        
        with open(ledger_file, 'r') as f:
            ledger = json.load(f)
        
        assert ledger["phase_id"] == "PH-TEST"
        assert ledger["execution_status"] == "QUEUED"
    
    def test_start_phase(self, orchestrator, sample_spec_file):
        """Test starting a queued phase."""
        orchestrator.queue_phase(sample_spec_file, force=True)
        success = orchestrator.start_phase("PH-TEST")
        
        assert success is True
        assert orchestrator.state_machines["PH-TEST"].get_state() == PhaseState.RUNNING
    
    def test_complete_phase(self, orchestrator, sample_spec_file):
        """Test completing a running phase."""
        orchestrator.queue_phase(sample_spec_file, force=True)
        orchestrator.start_phase("PH-TEST")
        success = orchestrator.complete_phase("PH-TEST")
        
        assert success is True
        assert orchestrator.state_machines["PH-TEST"].get_state() == PhaseState.COMPLETE
    
    def test_fail_phase(self, orchestrator, sample_spec_file):
        """Test failing a running phase."""
        orchestrator.queue_phase(sample_spec_file, force=True)
        orchestrator.start_phase("PH-TEST")
        success = orchestrator.fail_phase("PH-TEST", reason="test failure")
        
        assert success is True
        assert orchestrator.state_machines["PH-TEST"].get_state() == PhaseState.FAILED
    
    def test_get_status(self, orchestrator, sample_spec_file):
        """Test getting phase status."""
        orchestrator.queue_phase(sample_spec_file, force=True)
        status = orchestrator.get_status("PH-TEST")
        
        assert status is not None
        assert status["phase_id"] == "PH-TEST"
        assert status["current_state"] == "queued"
        assert status["ledger_exists"] is True
    
    def test_get_status_nonexistent_phase(self, orchestrator):
        """Test getting status of nonexistent phase."""
        status = orchestrator.get_status("PH-NONEXISTENT")
        assert status is None
    
    def test_list_phases(self, orchestrator, sample_spec_file):
        """Test listing all phases."""
        orchestrator.queue_phase(sample_spec_file, force=True)
        phases = orchestrator.list_phases()
        
        assert len(phases) >= 1
        assert any(p["phase_id"] == "PH-TEST" for p in phases)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
