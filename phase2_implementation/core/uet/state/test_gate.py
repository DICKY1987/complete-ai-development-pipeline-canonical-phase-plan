"""
Test Gate State Machine implementation.

Implements the Test Gate state machine per SSOT §2.3.
Gates control task progression based on test results.

States: PENDING, RUNNING, PASSED, FAILED, BLOCKED
Reference: DOC-SSOT-STATE-MACHINES-001 §2.3
"""

from typing import Dict, Set, Optional
from datetime import datetime, timezone

from core.state.base import BaseState, BaseStateMachine


class TestGateState(BaseState):
    """
    Test Gate states per SSOT §2.3.1.
    """
    
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    
    @classmethod
    def get_terminal_states(cls) -> Set['TestGateState']:
        """Terminal states: PASSED, FAILED."""
        return {cls.PASSED, cls.FAILED}
    
    @classmethod
    def get_valid_transitions(cls) -> Dict['TestGateState', Set['TestGateState']]:
        """Valid transitions per SSOT §2.3.4."""
        return {
            cls.PENDING: {cls.RUNNING, cls.BLOCKED},
            cls.RUNNING: {cls.PASSED, cls.FAILED},
            cls.BLOCKED: {cls.PENDING},
            cls.PASSED: set(),
            cls.FAILED: set()
        }


class TestGateStateMachine(BaseStateMachine):
    """
    Test Gate state machine for test-based task blocking.
    
    Manages test gate lifecycle per SSOT §2.3.
    """
    
    def __init__(self, gate_id: str, task_id: str, metadata: Optional[Dict] = None):
        super().__init__(
            entity_id=gate_id,
            entity_type="test_gate",
            initial_state=TestGateState.PENDING,
            metadata=metadata or {}
        )
        
        self.gate_id = gate_id
        self.task_id = task_id
        
        # Gate configuration
        self.test_suite: Optional[str] = None
        self.timeout_seconds = 300
        
        # Execution
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.test_results: Optional[Dict] = None
    
    def start_execution(self):
        """Start gate test execution."""
        self.transition(
            TestGateState.RUNNING,
            reason="Test execution started",
            trigger="execution_started"
        )
        self.started_at = datetime.now(timezone.utc)
    
    def block(self, reason: str):
        """Block gate execution."""
        self.transition(
            TestGateState.BLOCKED,
            reason=reason,
            trigger="gate_blocked"
        )
    
    def unblock(self):
        """Unblock gate."""
        self.transition(
            TestGateState.PENDING,
            reason="Blockers resolved",
            trigger="gate_unblocked"
        )
    
    def pass_gate(self, test_results: Dict = None):
        """Mark gate as passed."""
        if test_results:
            self.test_results = test_results
        self.transition(
            TestGateState.PASSED,
            reason="All tests passed",
            trigger="gate_passed"
        )
        self.completed_at = datetime.now(timezone.utc)
    
    def fail_gate(self, test_results: Dict = None, reason: str = "Tests failed"):
        """Mark gate as failed."""
        if test_results:
            self.test_results = test_results
        self.transition(
            TestGateState.FAILED,
            reason=reason,
            trigger="gate_failed"
        )
        self.completed_at = datetime.now(timezone.utc)
    
    def set_test_suite(self, test_suite: str, timeout: int = 300):
        """Configure gate test suite."""
        self.test_suite = test_suite
        self.timeout_seconds = timeout
    
    def get_gate_info(self) -> Dict:
        """Get gate information."""
        info = {
            'gate_id': self.gate_id,
            'task_id': self.task_id,
            'state': self.current_state.value,
            'test_suite': self.test_suite,
            'timeout_seconds': self.timeout_seconds,
            'is_terminal': self.is_terminal()
        }
        
        if self.started_at and self.completed_at:
            duration = (self.completed_at - self.started_at).total_seconds()
            info['execution_time'] = duration
        
        if self.test_results:
            info['test_results'] = self.test_results
        
        return info
