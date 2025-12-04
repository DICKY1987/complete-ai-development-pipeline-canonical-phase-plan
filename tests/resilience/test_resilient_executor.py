"""Tests for resilient executor - WS-03-03A"""

import pytest
import sys
from pathlib import Path
import time

# Add framework root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.engine.resilience import ResilientExecutor, CircuitBreakerOpen, RetryExhausted


class TestResilientExecutor:
    """Test ResilientExecutor functionality"""
# DOC_ID: DOC-TEST-RESILIENCE-TEST-RESILIENT-EXECUTOR-188

    def test_create_executor(self):
        """Test creating resilient executor"""
        executor = ResilientExecutor()

        assert len(executor.circuit_breakers) == 0
        assert len(executor.retry_strategies) == 0

    def test_register_tool(self):
        """Test registering a tool"""
        executor = ResilientExecutor()

        executor.register_tool(
            "test-tool",
            failure_threshold=3,
            recovery_timeout=60,
            max_retries=5
        )

        assert "test-tool" in executor.circuit_breakers
        assert "test-tool" in executor.retry_strategies

    def test_execute_successful_call(self):
        """Test executing successful call"""
        executor = ResilientExecutor()
        executor.register_tool("test-tool")

        def success_func():
            return "success"

        result = executor.execute("test-tool", success_func)

        assert result == "success"

    def test_auto_register_on_execute(self):
        """Test tool is auto-registered on first execute"""
        executor = ResilientExecutor()

        def success_func():
            return "success"

        result = executor.execute("auto-tool", success_func)

        assert result == "success"
        assert "auto-tool" in executor.circuit_breakers

    def test_retry_on_failure(self):
        """Test retrying on failure"""
        executor = ResilientExecutor()
        executor.register_tool("test-tool", max_retries=3)

        call_count = {'count': 0}

        def fail_twice():
            call_count['count'] += 1
            if call_count['count'] < 3:
                raise ValueError("fail")
            return "success"

        result = executor.execute("test-tool", fail_twice)

        assert result == "success"
        assert call_count['count'] == 3

    def test_circuit_opens_after_threshold(self):
        """Test circuit opens after failure threshold"""
        executor = ResilientExecutor()
        executor.register_tool(
            "test-tool",
            failure_threshold=2,
            max_retries=1  # Fail fast
        )

        def always_fail():
            raise ValueError("fail")

        # First execution - retries exhausted
        with pytest.raises(RetryExhausted):
            executor.execute("test-tool", always_fail)

        # Second execution - retries exhausted again
        with pytest.raises(RetryExhausted):
            executor.execute("test-tool", always_fail)

        # Circuit should now be open
        state = executor.get_tool_state("test-tool")
        assert state['state'] == 'open'

    def test_circuit_blocks_when_open(self):
        """Test circuit blocks calls when open"""
        executor = ResilientExecutor()
        executor.register_tool(
            "test-tool",
            failure_threshold=2,
            max_retries=1
        )

        def always_fail():
            raise ValueError("fail")

        # Open the circuit
        for _ in range(2):
            with pytest.raises(RetryExhausted):
                executor.execute("test-tool", always_fail)

        # Next call should be blocked and retried (then exhausted)
        with pytest.raises(RetryExhausted) as exc_info:
            executor.execute("test-tool", lambda: "success")

        # The last exception should be CircuitBreakerOpen
        assert isinstance(exc_info.value.last_exception, CircuitBreakerOpen)

    def test_get_tool_state(self):
        """Test getting tool state"""
        executor = ResilientExecutor()
        executor.register_tool("test-tool")

        state = executor.get_tool_state("test-tool")

        assert state is not None
        assert state['name'] == "test-tool"
        assert state['state'] == 'closed'

    def test_get_nonexistent_tool_state(self):
        """Test getting state for nonexistent tool"""
        executor = ResilientExecutor()

        state = executor.get_tool_state("nonexistent")

        assert state is None

    def test_reset_tool(self):
        """Test manually resetting a tool"""
        executor = ResilientExecutor()
        executor.register_tool(
            "test-tool",
            failure_threshold=1,
            max_retries=1
        )

        def always_fail():
            raise ValueError("fail")

        # Open the circuit
        with pytest.raises(RetryExhausted):
            executor.execute("test-tool", always_fail)

        assert executor.get_tool_state("test-tool")['state'] == 'open'

        # Reset
        executor.reset_tool("test-tool")

        assert executor.get_tool_state("test-tool")['state'] == 'closed'

    def test_get_all_states(self):
        """Test getting all tool states"""
        executor = ResilientExecutor()
        executor.register_tool("tool1")
        executor.register_tool("tool2")

        states = executor.get_all_states()

        assert len(states) == 2
        assert "tool1" in states
        assert "tool2" in states

    def test_separate_circuits_per_tool(self):
        """Test each tool has independent circuit"""
        executor = ResilientExecutor()
        executor.register_tool("tool1", failure_threshold=1, max_retries=1)
        executor.register_tool("tool2", failure_threshold=1, max_retries=1)

        def always_fail():
            raise ValueError("fail")

        # Fail tool1
        with pytest.raises(RetryExhausted):
            executor.execute("tool1", always_fail)

        # tool1 should be open
        assert executor.get_tool_state("tool1")['state'] == 'open'

        # tool2 should still be closed
        assert executor.get_tool_state("tool2")['state'] == 'closed'

        # tool2 should still work
        result = executor.execute("tool2", lambda: "success")
        assert result == "success"
