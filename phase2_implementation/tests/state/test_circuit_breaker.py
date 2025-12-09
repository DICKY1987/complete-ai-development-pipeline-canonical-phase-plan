"""
Unit tests for Circuit Breaker state machine.

Tests all valid and invalid transitions per SSOT §4.1.

Reference: DOC-SSOT-STATE-MACHINES-001 §2.4, §4.1
"""

import pytest
import time

from core.state.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerState,
    CircuitBreakerOpenError,
)
from core.state.base import StateTransitionError


class TestCircuitBreakerStates:
    """Test circuit breaker state definitions."""

    def test_initial_state_is_closed(self):
        """Circuit breaker starts in CLOSED state."""
        cb = CircuitBreaker("test-tool")
        assert cb.current_state == CircuitBreakerState.CLOSED

    def test_no_terminal_states(self):
        """Circuit breaker has no terminal states."""
        assert len(CircuitBreakerState.get_terminal_states()) == 0

        cb = CircuitBreaker("test-tool")
        assert not cb.is_terminal()


class TestCircuitBreakerValidTransitions:
    """Test all valid state transitions per SSOT §2.4.5."""

    def test_closed_to_open_on_failure_threshold(self):
        """CLOSED → OPEN when failure threshold exceeded."""
        cb = CircuitBreaker("test-tool", failure_threshold=3)

        # Simulate failures
        for i in range(3):
            try:
                cb.call(lambda: 1 / 0)  # Raise exception
            except ZeroDivisionError:
                pass

        assert cb.current_state == CircuitBreakerState.OPEN
        assert cb.failure_count == 3

    def test_open_to_half_open_on_cooldown(self):
        """OPEN → HALF_OPEN when cooldown expires."""
        cb = CircuitBreaker("test-tool", failure_threshold=1, cooldown_seconds=1)

        # Trigger failure to open circuit
        try:
            cb.call(lambda: 1 / 0)
        except ZeroDivisionError:
            pass

        assert cb.current_state == CircuitBreakerState.OPEN

        # Wait for cooldown
        time.sleep(1.1)

        # Next call should attempt reset
        try:
            cb.call(lambda: 1 / 0)
        except ZeroDivisionError:
            pass

        # Should be back to OPEN after failed test
        assert cb.current_state == CircuitBreakerState.OPEN

    def test_half_open_to_closed_on_success(self):
        """HALF_OPEN → CLOSED when test request succeeds."""
        cb = CircuitBreaker("test-tool", failure_threshold=1, cooldown_seconds=1)

        # Open circuit
        try:
            cb.call(lambda: 1 / 0)
        except ZeroDivisionError:
            pass

        # Wait for cooldown
        time.sleep(1.1)

        # Successful test request
        result = cb.call(lambda: "success")

        assert result == "success"
        assert cb.current_state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0

    def test_half_open_to_open_on_failure(self):
        """HALF_OPEN → OPEN when test request fails."""
        cb = CircuitBreaker("test-tool", failure_threshold=1, cooldown_seconds=1)

        # Open circuit
        try:
            cb.call(lambda: 1 / 0)
        except ZeroDivisionError:
            pass

        assert cb.current_state == CircuitBreakerState.OPEN

        # Wait for cooldown
        time.sleep(1.1)

        # Failed test request
        try:
            cb.call(lambda: 1 / 0)
        except ZeroDivisionError:
            pass

        assert cb.current_state == CircuitBreakerState.OPEN


class TestCircuitBreakerInvalidTransitions:
    """Test that invalid transitions are prevented."""

    def test_closed_to_half_open_invalid(self):
        """CLOSED → HALF_OPEN is not valid."""
        cb = CircuitBreaker("test-tool")

        with pytest.raises(StateTransitionError):
            cb.transition(CircuitBreakerState.HALF_OPEN)

    def test_open_to_closed_invalid(self):
        """OPEN → CLOSED is not valid (must go through HALF_OPEN)."""
        cb = CircuitBreaker("test-tool", failure_threshold=1)

        # Open circuit
        try:
            cb.call(lambda: 1 / 0)
        except ZeroDivisionError:
            pass

        with pytest.raises(StateTransitionError):
            cb.transition(CircuitBreakerState.CLOSED)


class TestCircuitBreakerBehavior:
    """Test circuit breaker behavior and functionality."""

    def test_successful_execution_when_closed(self):
        """Successful function execution when circuit is CLOSED."""
        cb = CircuitBreaker("test-tool")

        result = cb.call(lambda x: x * 2, 21)

        assert result == 42
        assert cb.current_state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0

    def test_exception_propagated_when_closed(self):
        """Exceptions are propagated when circuit is CLOSED."""
        cb = CircuitBreaker("test-tool")

        with pytest.raises(ValueError, match="test error"):
            cb.call(lambda: (_ for _ in ()).throw(ValueError("test error")))

    def test_fast_fail_when_open(self):
        """Requests fail fast when circuit is OPEN."""
        cb = CircuitBreaker("test-tool", failure_threshold=2, cooldown_seconds=10)

        # Open circuit
        for _ in range(2):
            try:
                cb.call(lambda: 1 / 0)
            except ZeroDivisionError:
                pass

        assert cb.current_state == CircuitBreakerState.OPEN

        # Should fail fast without executing function
        with pytest.raises(CircuitBreakerOpenError) as exc_info:
            cb.call(lambda: "should not execute")

        assert exc_info.value.tool_id == "test-tool"
        assert exc_info.value.retry_after > 0

    def test_failure_count_resets_on_success_when_closed(self):
        """Failure count resets after success when CLOSED."""
        cb = CircuitBreaker("test-tool", failure_threshold=3)

        # Accumulate some failures
        try:
            cb.call(lambda: 1 / 0)
        except ZeroDivisionError:
            pass

        assert cb.failure_count == 1

        # Successful call resets count
        cb.call(lambda: "success")

        assert cb.failure_count == 0
        assert cb.current_state == CircuitBreakerState.CLOSED

    def test_multiple_successes_needed_in_half_open(self):
        """Can require multiple successes to close from HALF_OPEN."""
        cb = CircuitBreaker(
            "test-tool", failure_threshold=1, cooldown_seconds=1, success_threshold=3
        )

        # Open circuit
        try:
            cb.call(lambda: 1 / 0)
        except ZeroDivisionError:
            pass

        time.sleep(1.1)

        # First 2 successes keep it in HALF_OPEN
        cb.call(lambda: "success")
        assert cb.current_state == CircuitBreakerState.HALF_OPEN

        cb.call(lambda: "success")
        assert cb.current_state == CircuitBreakerState.HALF_OPEN

        # Third success closes it
        cb.call(lambda: "success")
        assert cb.current_state == CircuitBreakerState.CLOSED


class TestCircuitBreakerManualControl:
    """Test manual override functionality."""

    def test_force_open(self):
        """Can manually open circuit."""
        cb = CircuitBreaker("test-tool")
        assert cb.current_state == CircuitBreakerState.CLOSED

        cb.force_open("Manual test")

        assert cb.current_state == CircuitBreakerState.OPEN

        # Should reject requests
        with pytest.raises(CircuitBreakerOpenError):
            cb.call(lambda: "test")

    def test_force_close(self):
        """Can manually close circuit."""
        cb = CircuitBreaker("test-tool", failure_threshold=1)

        # Open circuit
        try:
            cb.call(lambda: 1 / 0)
        except ZeroDivisionError:
            pass

        assert cb.current_state == CircuitBreakerState.OPEN

        # Force close
        cb.force_close("Manual reset")

        assert cb.current_state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0

        # Should accept requests
        result = cb.call(lambda: "success")
        assert result == "success"


class TestCircuitBreakerStats:
    """Test statistics reporting."""

    def test_get_stats(self):
        """Can retrieve circuit breaker statistics."""
        cb = CircuitBreaker("test-tool", failure_threshold=5, cooldown_seconds=60)

        stats = cb.get_stats()

        assert stats["tool_id"] == "test-tool"
        assert stats["state"] == "CLOSED"
        assert stats["failure_count"] == 0
        assert stats["failure_threshold"] == 5
        assert stats["cooldown_seconds"] == 60
        assert "time_in_state" in stats

    def test_stats_after_failure(self):
        """Stats reflect failure state."""
        cb = CircuitBreaker("test-tool", failure_threshold=3)

        # Cause 2 failures
        for _ in range(2):
            try:
                cb.call(lambda: 1 / 0)
            except ZeroDivisionError:
                pass

        stats = cb.get_stats()

        assert stats["failure_count"] == 2
        assert stats["last_failure_time"] is not None


class TestCircuitBreakerStateHistory:
    """Test state history tracking."""

    def test_history_tracks_all_transitions(self):
        """State history records all transitions."""
        cb = CircuitBreaker("test-tool", failure_threshold=1, cooldown_seconds=1)

        # Open circuit
        try:
            cb.call(lambda: 1 / 0)
        except ZeroDivisionError:
            pass

        # Wait and test
        time.sleep(1.1)
        cb.call(lambda: "success")

        history = cb.get_state_history()

        # Should have: CLOSED (initial), OPEN, HALF_OPEN, CLOSED
        assert len(history) >= 4
        assert history[0][0] == "CLOSED"  # Initial state

    def test_history_is_append_only(self):
        """State history never shrinks."""
        cb = CircuitBreaker("test-tool")

        initial_len = len(cb.history)

        cb.force_open()
        open_len = len(cb.history)

        cb.force_close()
        closed_len = len(cb.history)

        assert open_len > initial_len
        assert closed_len > open_len


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
