"""
Base state machine classes and exceptions.

This module provides the foundational classes for all state machines
in the AI development pipeline, per SSOT §1-2.

Reference: DOC-SSOT-STATE-MACHINES-001
"""

from enum import Enum
from typing import Dict, Set, Optional, List, Tuple, Any
from datetime import datetime, timezone
from abc import ABC, abstractmethod


class StateTransitionError(Exception):
    """
    Raised when an invalid state transition is attempted.
    
    This enforces the monotonic progress policy (SSOT §8.1) and
    terminal state policy (SSOT §8.2).
    """
    pass


class TerminalStateViolation(StateTransitionError):
    """Raised when attempting to transition from a terminal state."""
    pass


class MonotonicProgressViolation(StateTransitionError):
    """Raised when attempting a backward transition."""
    pass


class BaseState(Enum):
    """
    Base class for all state enums.
    
    All state machines in the system extend this class to ensure
    consistent behavior and validation.
    
    Reference: SSOT §1-2 (all state machines)
    """
    
    @classmethod
    def is_terminal(cls, state: 'BaseState') -> bool:
        """
        Check if a state is terminal.
        
        Terminal states cannot transition to any other state per
        the Terminal State Policy (SSOT §8.2).
        
        Args:
            state: State to check
            
        Returns:
            True if state is terminal
        """
        return state in cls.get_terminal_states()
    
    @classmethod
    @abstractmethod
    def get_terminal_states(cls) -> Set['BaseState']:
        """
        Define terminal states for this state machine.
        
        Override in subclass to define which states are terminal.
        
        Returns:
            Set of terminal states
        """
        raise NotImplementedError(
            f"{cls.__name__} must implement get_terminal_states()"
        )
    
    @classmethod
    @abstractmethod
    def get_valid_transitions(cls) -> Dict['BaseState', Set['BaseState']]:
        """
        Define valid state transitions for this state machine.
        
        Override in subclass to define the transition map.
        
        Returns:
            Dictionary mapping each state to its valid next states
        """
        raise NotImplementedError(
            f"{cls.__name__} must implement get_valid_transitions()"
        )


class BaseStateMachine(ABC):
    """
    Base state machine with transition validation and audit trail.
    
    Provides common functionality for all state machines:
    - Transition validation (SSOT §8.1, §8.2)
    - State history tracking (SSOT §8.5)
    - Event logging (SSOT §7.2)
    - Timestamp management (SSOT §8.3)
    
    Reference: SSOT §1-2 (all state machines)
    """
    
    def __init__(
        self,
        entity_id: str,
        entity_type: str,
        initial_state: BaseState,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize state machine.
        
        Args:
            entity_id: Unique identifier for the entity
            entity_type: Type of entity (run, workstream, task, etc.)
            initial_state: Starting state
            metadata: Optional metadata dictionary
        """
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.current_state = initial_state
        self.metadata = metadata or {}
        
        # State history (append-only per SSOT §8.5)
        self.history: List[Tuple[BaseState, datetime, str]] = [
            (initial_state, datetime.now(timezone.utc), "created")
        ]
    
    def transition(
        self,
        to_state: BaseState,
        reason: str = "",
        trigger: str = "",
        operator: Optional[str] = None
    ) -> bool:
        """
        Transition to new state with full validation.
        
        Enforces:
        - Valid transition rules (SSOT §1-2)
        - Terminal state policy (SSOT §8.2)
        - Monotonic progress policy (SSOT §8.1)
        
        Args:
            to_state: Target state
            reason: Human-readable reason for transition
            trigger: Event trigger name
            operator: Username if manual transition
            
        Returns:
            True if transition succeeded
            
        Raises:
            TerminalStateViolation: If current state is terminal
            StateTransitionError: If transition is invalid
        """
        # Enforce terminal state policy (SSOT §8.2)
        if self.is_terminal():
            raise TerminalStateViolation(
                f"Cannot transition from terminal state: "
                f"{self.current_state.value}"
            )
        
        # Validate transition
        if not self._is_valid_transition(to_state):
            raise StateTransitionError(
                f"Invalid transition for {self.entity_type}: "
                f"{self.current_state.value} → {to_state.value}"
            )
        
        # Record transition
        old_state = self.current_state
        self.current_state = to_state
        
        # Append to history (SSOT §8.5 - append-only)
        self.history.append((
            to_state,
            datetime.now(timezone.utc),
            reason or trigger
        ))
        
        # Log event (SSOT §7.2)
        self._log_transition(old_state, to_state, reason, trigger, operator)
        
        return True
    
    def _is_valid_transition(self, to_state: BaseState) -> bool:
        """
        Check if transition from current_state to to_state is valid.
        
        Args:
            to_state: Proposed next state
            
        Returns:
            True if transition is valid
        """
        valid_next_states = self.current_state.get_valid_transitions()[
            self.current_state
        ]
        return to_state in valid_next_states
    
    def _log_transition(
        self,
        from_state: BaseState,
        to_state: BaseState,
        reason: str,
        trigger: str,
        operator: Optional[str]
    ):
        """
        Log state transition event per SSOT §7.2.
        
        Args:
            from_state: Previous state
            to_state: New state
            reason: Transition reason
            trigger: Event trigger
            operator: User who initiated (if manual)
        """
        from core.events import emit_event
        
        event = {
            'event_type': f'{self.entity_type}_state_transition',
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'from_state': from_state.value,
            'to_state': to_state.value,
            'reason': reason,
            'trigger': trigger,
            'operator': operator,
            'severity': self._get_severity(to_state),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'metadata': self.metadata
        }
        
        emit_event(event)
    
    def _get_severity(self, state: BaseState) -> str:
        """
        Determine event severity based on state per SSOT §7.2.2.
        
        Args:
            state: State to evaluate
            
        Returns:
            Severity level: debug, info, warning, error, critical
        """
        # Default severity mapping
        # Override in subclass for custom mapping
        state_value = state.value.lower()
        
        if 'completed' in state_value or 'succeeded' in state_value:
            return 'info'
        elif 'retrying' in state_value or 'blocked' in state_value:
            return 'warning'
        elif 'failed' in state_value or 'cancelled' in state_value:
            return 'error'
        elif 'rolled_back' in state_value or 'quarantined' in state_value:
            return 'critical'
        else:
            return 'info'
    
    def can_transition_to(self, to_state: BaseState) -> bool:
        """
        Check if transition is possible without attempting it.
        
        Args:
            to_state: Proposed next state
            
        Returns:
            True if transition would be valid
        """
        if self.is_terminal():
            return False
        return self._is_valid_transition(to_state)
    
    def is_terminal(self) -> bool:
        """
        Check if current state is terminal per SSOT §8.2.
        
        Returns:
            True if current state is terminal
        """
        return self.current_state.is_terminal(self.current_state)
    
    def get_state_history(self) -> List[Tuple[str, str, str]]:
        """
        Get state transition history.
        
        Returns list of (state, timestamp, reason) tuples per SSOT §8.5.
        
        Returns:
            List of state history entries
        """
        return [
            (state.value, ts.isoformat(), reason)
            for state, ts, reason in self.history
        ]
    
    def get_time_in_state(self) -> float:
        """
        Get time spent in current state (seconds).
        
        Returns:
            Seconds in current state
        """
        if len(self.history) == 0:
            return 0.0
        
        last_transition = self.history[-1][1]
        now = datetime.now(timezone.utc)
        return (now - last_transition).total_seconds()
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"{self.__class__.__name__}("
            f"id={self.entity_id}, "
            f"state={self.current_state.value}, "
            f"terminal={self.is_terminal()})"
        )
