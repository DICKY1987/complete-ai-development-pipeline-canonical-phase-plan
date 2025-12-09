"""
Circuit Breaker state machine implementation.

Implements the Circuit Breaker pattern for tool execution protection
per SSOT §2.4.

The Circuit Breaker prevents cascading failures by monitoring tool
execution failures and temporarily blocking requests when failure
thresholds are exceeded.

States: CLOSED, OPEN, HALF_OPEN
Reference: DOC-SSOT-STATE-MACHINES-001 §2.4
"""

from typing import Dict, Set, Optional, Callable, Any
from datetime import datetime, timedelta, timezone
from enum import Enum

from .base import BaseState, BaseStateMachine, StateTransitionError


class CircuitBreakerState(BaseState):
    """
    Circuit Breaker states per SSOT §2.4.1.
    
    - CLOSED: Healthy - requests allowed
    - OPEN: Unhealthy - requests rejected (fast fail)
    - HALF_OPEN: Testing - single test request allowed
    """
    
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"
    
    @classmethod
    def get_terminal_states(cls) -> Set['CircuitBreakerState']:
        """Circuit Breaker has no terminal states - it can always recover."""
        return set()
    
    @classmethod
    def get_valid_transitions(cls) -> Dict['CircuitBreakerState', Set['CircuitBreakerState']]:
        """
        Valid transitions per SSOT §2.4.5.
        
        CLOSED → OPEN (failure threshold exceeded)
        OPEN → HALF_OPEN (cooldown expires)
        HALF_OPEN → CLOSED (test request succeeds)
        HALF_OPEN → OPEN (test request fails)
        """
        return {
            cls.CLOSED: {cls.OPEN},
            cls.OPEN: {cls.HALF_OPEN},
            cls.HALF_OPEN: {cls.CLOSED, cls.OPEN}
        }


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is OPEN and requests are rejected."""
    
    def __init__(self, tool_id: str, retry_after: int):
        self.tool_id = tool_id
        self.retry_after = retry_after
        super().__init__(
            f"Circuit breaker for '{tool_id}' is OPEN. "
            f"Retry in {retry_after} seconds."
        )


class CircuitBreaker(BaseStateMachine):
    """
    Circuit Breaker state machine for tool execution protection.
    
    Configuration per SSOT §2.4.4:
    - failure_threshold: Number of failures before opening
    - cooldown_seconds: Time to stay OPEN before testing
    - success_threshold: Successes needed in HALF_OPEN to close
    
    Reference: SSOT §2.4
    """
    
    def __init__(
        self,
        tool_id: str,
        failure_threshold: int = 5,
        cooldown_seconds: int = 60,
        success_threshold: int = 1
    ):
        """
        Initialize Circuit Breaker.
        
        Args:
            tool_id: Identifier for the tool being protected
            failure_threshold: Failures before opening circuit
            cooldown_seconds: Seconds to wait before testing recovery
            success_threshold: Successes needed to close from HALF_OPEN
        """
        super().__init__(
            entity_id=tool_id,
            entity_type="circuit_breaker",
            initial_state=CircuitBreakerState.CLOSED
        )
        
        self.tool_id = tool_id
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.success_threshold = success_threshold
        
        # Runtime state
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_success_time: Optional[datetime] = None
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.
        
        This is the main API per SSOT §2.4.6.
        
        Args:
            func: Function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
            
        Returns:
            Result from func
            
        Raises:
            CircuitBreakerOpenError: If circuit is OPEN
            Exception: Any exception from func execution
            
        Example:
            >>> cb = CircuitBreaker("aider", failure_threshold=3)
            >>> result = cb.call(run_aider_command, "fix bug")
        """
        # Check if we should attempt reset
        if self.current_state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self._attempt_reset()
            else:
                raise CircuitBreakerOpenError(
                    self.tool_id,
                    self._seconds_until_reset()
                )
        
        # Execute function
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """
        Handle successful request per SSOT §2.4.6.
        
        - CLOSED: Reset failure count
        - HALF_OPEN: Increment success count, close if threshold met
        """
        self.last_success_time = datetime.now(timezone.utc)
        
        if self.current_state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            
            if self.success_count >= self.success_threshold:
                # Test succeeded - close circuit
                self.transition(
                    CircuitBreakerState.CLOSED,
                    reason=f"Test request succeeded, closing circuit",
                    trigger="success_threshold_met"
                )
                self.failure_count = 0
                self.success_count = 0
        
        elif self.current_state == CircuitBreakerState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0
    
    def _on_failure(self):
        """
        Handle failed request per SSOT §2.4.6.
        
        - CLOSED: Increment failure count, open if threshold exceeded
        - HALF_OPEN: Immediately reopen circuit
        """
        self.failure_count += 1
        self.last_failure_time = datetime.now(timezone.utc)
        
        if self.current_state == CircuitBreakerState.HALF_OPEN:
            # Test failed - reopen circuit
            self.transition(
                CircuitBreakerState.OPEN,
                reason=f"Test request failed, reopening circuit",
                trigger="test_failed"
            )
            self.success_count = 0
        
        elif self.current_state == CircuitBreakerState.CLOSED:
            if self.failure_count >= self.failure_threshold:
                # Threshold exceeded - open circuit
                self.transition(
                    CircuitBreakerState.OPEN,
                    reason=f"Failure threshold exceeded ({self.failure_count} failures)",
                    trigger="failure_threshold_exceeded"
                )
    
    def _should_attempt_reset(self) -> bool:
        """
        Check if cooldown period has elapsed per SSOT §2.4.5.
        
        Returns:
            True if ready to attempt reset
        """
        if not self.last_failure_time:
            return True
        
        elapsed = (datetime.now(timezone.utc) - self.last_failure_time).total_seconds()
        return elapsed >= self.cooldown_seconds
    
    def _attempt_reset(self):
        """
        Attempt to reset circuit by transitioning to HALF_OPEN.
        
        Per SSOT §2.4.5: OPEN → HALF_OPEN when cooldown expires.
        """
        self.transition(
            CircuitBreakerState.HALF_OPEN,
            reason=f"Cooldown period elapsed ({self.cooldown_seconds}s), testing recovery",
            trigger="cooldown_expired"
        )
        self.success_count = 0
    
    def _seconds_until_reset(self) -> int:
        """
        Calculate seconds remaining in cooldown.
        
        Returns:
            Seconds until circuit can attempt reset
        """
        if not self.last_failure_time:
            return 0
        
        elapsed = (datetime.now(timezone.utc) - self.last_failure_time).total_seconds()
        remaining = max(0, self.cooldown_seconds - elapsed)
        return int(remaining)
    
    def force_open(self, reason: str = "Manual override"):
        """
        Manually open circuit breaker.
        
        Args:
            reason: Reason for manual override
        """
        if self.current_state != CircuitBreakerState.OPEN:
            self.failure_count = self.failure_threshold
            self.last_failure_time = datetime.now(timezone.utc)
            self.transition(
                CircuitBreakerState.OPEN,
                reason=reason,
                trigger="manual_override",
                operator="manual"
            )
    
    def force_close(self, reason: str = "Manual override"):
        """
        Manually close circuit breaker.
        
        Args:
            reason: Reason for manual override
        """
        if self.current_state != CircuitBreakerState.CLOSED:
            # Reset counters
            self.failure_count = 0
            self.success_count = 0
            
            # First go to HALF_OPEN if currently OPEN
            if self.current_state == CircuitBreakerState.OPEN:
                self.transition(
                    CircuitBreakerState.HALF_OPEN,
                    reason="Manual reset to test state",
                    trigger="manual_override",
                    operator="manual"
                )
            
            # Then close
            self.transition(
                CircuitBreakerState.CLOSED,
                reason=reason,
                trigger="manual_override",
                operator="manual"
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get circuit breaker statistics.
        
        Returns:
            Dictionary with current stats
        """
        return {
            'tool_id': self.tool_id,
            'state': self.current_state.value,
            'failure_count': self.failure_count,
            'failure_threshold': self.failure_threshold,
            'success_count': self.success_count,
            'success_threshold': self.success_threshold,
            'cooldown_seconds': self.cooldown_seconds,
            'seconds_until_reset': self._seconds_until_reset(),
            'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None,
            'last_success_time': self.last_success_time.isoformat() if self.last_success_time else None,
            'time_in_state': self.get_time_in_state()
        }
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"CircuitBreaker(tool={self.tool_id}, "
            f"state={self.current_state.value}, "
            f"failures={self.failure_count}/{self.failure_threshold})"
        )
