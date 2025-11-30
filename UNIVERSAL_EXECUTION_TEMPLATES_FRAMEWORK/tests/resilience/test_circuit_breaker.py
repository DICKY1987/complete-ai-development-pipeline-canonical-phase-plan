"""Tests for circuit breaker - WS-03-03A"""

import pytest
import sys
from pathlib import Path
import time

# Add framework root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.engine.resilience import CircuitBreaker, CircuitBreakerState, CircuitBreakerOpen


class TestCircuitBreaker:
    """Test CircuitBreaker functionality"""
# DOC_ID: DOC-TEST-RESILIENCE-TEST-CIRCUIT-BREAKER-187
    
    def test_create_circuit_breaker(self):
        """Test creating a circuit breaker"""
        cb = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=60,
            name="test"
        )
        
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0
        assert cb.name == "test"
    
    def test_successful_calls(self):
        """Test successful calls pass through"""
        cb = CircuitBreaker(failure_threshold=3)
        
        def success_func():
            return "success"
        
        result = cb.call(success_func)
        
        assert result == "success"
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.success_count == 1
    
    def test_failed_calls_increment_counter(self):
        """Test failed calls increment failure counter"""
        cb = CircuitBreaker(failure_threshold=3)
        
        def fail_func():
            raise ValueError("test error")
        
        # First failure
        with pytest.raises(ValueError):
            cb.call(fail_func)
        
        assert cb.failure_count == 1
        assert cb.state == CircuitBreakerState.CLOSED
    
    def test_circuit_opens_after_threshold(self):
        """Test circuit opens after failure threshold"""
        cb = CircuitBreaker(failure_threshold=3)
        
        def fail_func():
            raise ValueError("test error")
        
        # Trigger failures to reach threshold
        for i in range(3):
            with pytest.raises(ValueError):
                cb.call(fail_func)
        
        assert cb.state == CircuitBreakerState.OPEN
        assert cb.failure_count == 3
    
    def test_open_circuit_blocks_calls(self):
        """Test open circuit blocks calls"""
        cb = CircuitBreaker(failure_threshold=2)
        
        def fail_func():
            raise ValueError("test error")
        
        # Open the circuit
        for i in range(2):
            with pytest.raises(ValueError):
                cb.call(fail_func)
        
        assert cb.state == CircuitBreakerState.OPEN
        
        # Next call should be blocked
        with pytest.raises(CircuitBreakerOpen):
            cb.call(lambda: "success")
    
    def test_circuit_transitions_to_half_open(self):
        """Test circuit transitions to half-open after timeout"""
        cb = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=1  # 1 second
        )
        
        def fail_func():
            raise ValueError("test error")
        
        # Open the circuit
        for i in range(2):
            with pytest.raises(ValueError):
                cb.call(fail_func)
        
        assert cb.state == CircuitBreakerState.OPEN
        
        # Wait for recovery timeout
        time.sleep(1.1)
        
        # Next call should transition to half-open
        def success_func():
            return "success"
        
        result = cb.call(success_func)
        
        assert result == "success"
        assert cb.state == CircuitBreakerState.CLOSED  # Recovered
    
    def test_half_open_failure_reopens_circuit(self):
        """Test failure in half-open state reopens circuit"""
        cb = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=1
        )
        
        def fail_func():
            raise ValueError("test error")
        
        # Open the circuit
        for i in range(2):
            with pytest.raises(ValueError):
                cb.call(fail_func)
        
        # Wait for recovery
        time.sleep(1.1)
        
        # Fail in half-open state
        with pytest.raises(ValueError):
            cb.call(fail_func)
        
        assert cb.state == CircuitBreakerState.OPEN
    
    def test_manual_reset(self):
        """Test manual circuit reset"""
        cb = CircuitBreaker(failure_threshold=2)
        
        def fail_func():
            raise ValueError("test error")
        
        # Open the circuit
        for i in range(2):
            with pytest.raises(ValueError):
                cb.call(fail_func)
        
        assert cb.state == CircuitBreakerState.OPEN
        
        # Manual reset
        cb.reset()
        
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0
    
    def test_get_state(self):
        """Test getting circuit state"""
        cb = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=60,
            name="test-cb"
        )
        
        state = cb.get_state()
        
        assert state['name'] == "test-cb"
        assert state['state'] == "closed"
        assert state['failure_count'] == 0
        assert state['failure_threshold'] == 3
