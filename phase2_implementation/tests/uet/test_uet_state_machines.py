"""
Tests for UET V2 state machines (Patch Ledger and Test Gate).

Reference: DOC-SSOT-STATE-MACHINES-001 §2.2, §2.3
"""

import pytest
from core.uet.state.patch_ledger import PatchLedgerState, PatchLedgerStateMachine
from core.uet.state.test_gate import TestGateState, TestGateStateMachine
from core.state.base import StateTransitionError


class TestPatchLedgerStateMachine:
    """Test Patch Ledger state machine."""
    
    def test_initial_state(self):
        patch = PatchLedgerStateMachine("patch-001", "task-001")
        assert patch.current_state == PatchLedgerState.PENDING
    
    def test_happy_path(self):
        """PENDING → VALIDATING → STAGED → APPLIED → VERIFIED."""
        patch = PatchLedgerStateMachine("patch-001", "task-001")
        patch.begin_validation()
        assert patch.current_state == PatchLedgerState.VALIDATING
        
        patch.stage()
        assert patch.current_state == PatchLedgerState.STAGED
        
        patch.apply_patch()
        assert patch.current_state == PatchLedgerState.APPLIED
        assert patch.applied_at is not None
        
        patch.verify()
        assert patch.current_state == PatchLedgerState.VERIFIED
        assert patch.is_terminal()
    
    def test_quarantine_path(self):
        """VALIDATING → QUARANTINED → VALIDATING."""
        patch = PatchLedgerStateMachine("patch-001", "task-001")
        patch.begin_validation()
        
        patch.quarantine("Invalid format", errors=["Syntax error"])
        assert patch.current_state == PatchLedgerState.QUARANTINED
        assert len(patch.validation_errors) == 1
        
        patch.begin_validation()
        assert patch.current_state == PatchLedgerState.VALIDATING
    
    def test_rollback(self):
        """APPLIED → ROLLED_BACK."""
        patch = PatchLedgerStateMachine("patch-001", "task-001")
        patch.begin_validation()
        patch.stage()
        patch.apply_patch()
        
        patch.rollback("Failed verification")
        assert patch.current_state == PatchLedgerState.ROLLED_BACK
        assert patch.is_terminal()
    
    def test_supersede(self):
        """STAGED → SUPERSEDED."""
        patch = PatchLedgerStateMachine("patch-001", "task-001")
        patch.begin_validation()
        patch.stage()
        
        patch.supersede("patch-002")
        assert patch.current_state == PatchLedgerState.SUPERSEDED
        assert patch.metadata['superseded_by'] == "patch-002"
    
    def test_expire(self):
        """PENDING → EXPIRED."""
        patch = PatchLedgerStateMachine("patch-001", "task-001")
        patch.expire()
        assert patch.current_state == PatchLedgerState.EXPIRED
        assert patch.is_terminal()
    
    def test_block_unblock(self):
        """STAGED → BLOCKED → STAGED."""
        patch = PatchLedgerStateMachine("patch-001", "task-001")
        patch.begin_validation()
        patch.stage()
        
        patch.block("Dependency not ready")
        assert patch.current_state == PatchLedgerState.BLOCKED
        
        patch.unblock()
        assert patch.current_state == PatchLedgerState.STAGED
    
    def test_patch_details(self):
        patch = PatchLedgerStateMachine("patch-001", "task-001")
        patch.set_patch_details(
            file_path="/src/module.py",
            format="unified_diff",
            scope="function"
        )
        
        info = patch.get_patch_info()
        assert info['file_path'] == "/src/module.py"
        assert info['patch_format'] == "unified_diff"
        assert info['scope'] == "function"


class TestTestGateStateMachine:
    """Test Test Gate state machine."""
    
    def test_initial_state(self):
        gate = TestGateStateMachine("gate-001", "task-001")
        assert gate.current_state == TestGateState.PENDING
    
    def test_happy_path_pass(self):
        """PENDING → RUNNING → PASSED."""
        gate = TestGateStateMachine("gate-001", "task-001")
        gate.start_execution()
        assert gate.current_state == TestGateState.RUNNING
        assert gate.started_at is not None
        
        gate.pass_gate(test_results={'passed': 10, 'failed': 0})
        assert gate.current_state == TestGateState.PASSED
        assert gate.is_terminal()
        assert gate.test_results['passed'] == 10
    
    def test_happy_path_fail(self):
        """PENDING → RUNNING → FAILED."""
        gate = TestGateStateMachine("gate-001", "task-001")
        gate.start_execution()
        
        gate.fail_gate(test_results={'passed': 8, 'failed': 2})
        assert gate.current_state == TestGateState.FAILED
        assert gate.is_terminal()
        assert gate.test_results['failed'] == 2
    
    def test_block_unblock(self):
        """PENDING → BLOCKED → PENDING."""
        gate = TestGateStateMachine("gate-001", "task-001")
        gate.block("Test environment not ready")
        assert gate.current_state == TestGateState.BLOCKED
        
        gate.unblock()
        assert gate.current_state == TestGateState.PENDING
    
    def test_test_suite_config(self):
        gate = TestGateStateMachine("gate-001", "task-001")
        gate.set_test_suite("unit_tests", timeout=600)
        
        info = gate.get_gate_info()
        assert info['test_suite'] == "unit_tests"
        assert info['timeout_seconds'] == 600
    
    def test_execution_time_tracking(self):
        gate = TestGateStateMachine("gate-001", "task-001")
        gate.start_execution()
        gate.pass_gate()
        
        info = gate.get_gate_info()
        assert 'execution_time' in info
        assert info['execution_time'] >= 0
    
    def test_terminal_states(self):
        terminals = TestGateState.get_terminal_states()
        assert TestGateState.PASSED in terminals
        assert TestGateState.FAILED in terminals
        assert len(terminals) == 2


class TestUETIntegration:
    """Integration tests for UET V2 components."""
    
    def test_gate_blocks_patch(self):
        """Test gate failure should block patch application."""
        gate = TestGateStateMachine("gate-001", "task-001")
        patch = PatchLedgerStateMachine("patch-001", "task-001")
        
        # Gate fails
        gate.start_execution()
        gate.fail_gate()
        
        # Patch should be blocked (simulated)
        patch.begin_validation()
        patch.stage()
        patch.block("Test gate failed")
        
        assert gate.current_state == TestGateState.FAILED
        assert patch.current_state == PatchLedgerState.BLOCKED
    
    def test_patch_lifecycle_with_gate(self):
        """Complete patch lifecycle with gate approval."""
        gate = TestGateStateMachine("gate-001", "task-001")
        patch = PatchLedgerStateMachine("patch-001", "task-001")
        
        # Gate passes
        gate.start_execution()
        gate.pass_gate()
        
        # Patch can proceed
        patch.begin_validation()
        patch.stage()
        patch.apply_patch()
        patch.verify()
        
        assert gate.current_state == TestGateState.PASSED
        assert patch.current_state == PatchLedgerState.VERIFIED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
