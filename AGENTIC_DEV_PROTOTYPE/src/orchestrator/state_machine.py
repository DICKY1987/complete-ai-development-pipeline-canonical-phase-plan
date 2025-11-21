#!/usr/bin/env python3
"""
State Machine - PH-3B

Manages phase execution lifecycle with state transitions.
States: NOT_STARTED → QUEUED → RUNNING → COMPLETE/FAILED
"""

from enum import Enum
from typing import Dict, List, Optional, Set
from datetime import datetime


class PhaseState(Enum):
    """Valid phase execution states."""
    NOT_STARTED = "not_started"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"
    BLOCKED = "blocked"


class StateTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""
    pass


class StateMachine:
    """Manages state transitions for phase execution."""
    
    # Valid state transitions
    VALID_TRANSITIONS = {
        PhaseState.NOT_STARTED: {PhaseState.QUEUED, PhaseState.BLOCKED},
        PhaseState.QUEUED: {PhaseState.RUNNING, PhaseState.BLOCKED},
        PhaseState.RUNNING: {PhaseState.COMPLETE, PhaseState.FAILED},
        PhaseState.COMPLETE: set(),  # Terminal state
        PhaseState.FAILED: {PhaseState.QUEUED},  # Can retry
        PhaseState.BLOCKED: {PhaseState.QUEUED}  # Can unblock
    }
    
    def __init__(self):
        self.current_state = PhaseState.NOT_STARTED
        self.transition_history: List[Dict] = []
    
    def can_transition(self, from_state: PhaseState, to_state: PhaseState) -> bool:
        """
        Check if a state transition is valid.
        
        Args:
            from_state: Current state
            to_state: Target state
        
        Returns:
            True if transition is valid
        """
        if from_state not in self.VALID_TRANSITIONS:
            return False
        
        return to_state in self.VALID_TRANSITIONS[from_state]
    
    def transition(
        self,
        to_state: PhaseState,
        trigger: Optional[str] = None
    ) -> bool:
        """
        Transition to a new state.
        
        Args:
            to_state: Target state
            trigger: Optional description of what triggered the transition
        
        Returns:
            True if transition succeeded
        
        Raises:
            StateTransitionError: If transition is invalid
        """
        if not self.can_transition(self.current_state, to_state):
            raise StateTransitionError(
                f"Invalid transition from {self.current_state.value} to {to_state.value}"
            )
        
        # Record transition
        transition = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "from_state": self.current_state.value,
            "to_state": to_state.value,
            "trigger": trigger or "manual"
        }
        self.transition_history.append(transition)
        
        # Update state
        self.current_state = to_state
        return True
    
    def get_state(self) -> PhaseState:
        """Get current state."""
        return self.current_state
    
    def get_history(self) -> List[Dict]:
        """Get transition history."""
        return self.transition_history.copy()
    
    def is_terminal(self) -> bool:
        """Check if current state is terminal (no further transitions)."""
        return len(self.VALID_TRANSITIONS.get(self.current_state, set())) == 0
    
    def reset(self) -> None:
        """Reset to initial state."""
        self.current_state = PhaseState.NOT_STARTED
        self.transition_history.clear()
