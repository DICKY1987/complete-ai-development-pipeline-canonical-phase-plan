"""Tests for retry strategies - WS-03-03A"""

import pytest
import sys
from pathlib import Path
import time

# Add framework root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.engine.resilience import (
    RetryStrategy,
    SimpleRetry,
    ExponentialBackoff,
    RetryExhausted
)


class TestSimpleRetry:
    """Test SimpleRetry strategy"""
# DOC_ID: DOC-TEST-RESILIENCE-TEST-RETRY-189

    def test_create_simple_retry(self):
        """Test creating simple retry strategy"""
        retry = SimpleRetry(max_attempts=3, delay=0.5)

        assert retry.max_attempts == 3
        assert retry.delay == 0.5

    def test_get_delay_is_constant(self):
        """Test simple retry has constant delay"""
        retry = SimpleRetry(max_attempts=3, delay=1.0)

        assert retry.get_delay(1) == 1.0
        assert retry.get_delay(2) == 1.0
        assert retry.get_delay(3) == 1.0

    def test_successful_execution(self):
        """Test successful execution on first try"""
        retry = SimpleRetry(max_attempts=3)

        def success_func():
            return "success"

        result = retry.execute(success_func)

        assert result == "success"
        assert retry.attempt_count == 1

    def test_retry_after_failure(self):
        """Test retrying after failure"""
        retry = SimpleRetry(max_attempts=3, delay=0.1)

        call_count = {'count': 0}

        def fail_twice_func():
            call_count['count'] += 1
            if call_count['count'] < 3:
                raise ValueError("fail")
            return "success"

        start_time = time.time()
        result = retry.execute(fail_twice_func)
        duration = time.time() - start_time

        assert result == "success"
        assert call_count['count'] == 3
        assert retry.attempt_count == 3
        # Should have waited for 2 retries
        assert duration >= 0.2  # 2 * 0.1

    def test_exhaust_retries(self):
        """Test exhausting all retries"""
        retry = SimpleRetry(max_attempts=2, delay=0.01)

        def always_fail():
            raise ValueError("always fails")

        with pytest.raises(RetryExhausted) as exc_info:
            retry.execute(always_fail)

        assert exc_info.value.attempts == 2
        assert isinstance(exc_info.value.last_exception, ValueError)


class TestExponentialBackoff:
    """Test ExponentialBackoff strategy"""

    def test_create_exponential_backoff(self):
        """Test creating exponential backoff strategy"""
        retry = ExponentialBackoff(
            max_attempts=5,
            base_delay=1.0,
            max_delay=60.0,
            exponential_base=2.0
        )

        assert retry.max_attempts == 5
        assert retry.base_delay == 1.0
        assert retry.max_delay == 60.0

    def test_exponential_delay_growth(self):
        """Test delay grows exponentially"""
        retry = ExponentialBackoff(
            base_delay=1.0,
            exponential_base=2.0,
            jitter=False  # Disable jitter for predictable testing
        )

        # Delays should be: 2, 4, 8, 16, ...
        assert retry.get_delay(1) == 2.0  # 1 * 2^1
        assert retry.get_delay(2) == 4.0  # 1 * 2^2
        assert retry.get_delay(3) == 8.0  # 1 * 2^3

    def test_max_delay_cap(self):
        """Test delay is capped at max_delay"""
        retry = ExponentialBackoff(
            base_delay=1.0,
            max_delay=10.0,
            exponential_base=2.0,
            jitter=False
        )

        # Delay would be 16, but capped at 10
        assert retry.get_delay(4) == 10.0
        assert retry.get_delay(5) == 10.0

    def test_jitter_adds_randomness(self):
        """Test jitter adds randomness to delay"""
        retry = ExponentialBackoff(
            base_delay=1.0,
            exponential_base=2.0,
            jitter=True
        )

        # Get multiple delays for same attempt
        delays = [retry.get_delay(1) for _ in range(10)]

        # Should have different values due to jitter
        assert len(set(delays)) > 1

        # All should be in reasonable range (0.5 * delay to 1.5 * delay)
        for delay in delays:
            assert 1.0 <= delay <= 3.0  # 2.0 * (0.5 to 1.5)

    def test_successful_after_retries(self):
        """Test success after some retries"""
        retry = ExponentialBackoff(
            max_attempts=5,
            base_delay=0.01,
            jitter=False
        )

        call_count = {'count': 0}

        def fail_three_times():
            call_count['count'] += 1
            if call_count['count'] < 4:
                raise ValueError("fail")
            return "success"

        result = retry.execute(fail_three_times)

        assert result == "success"
        assert call_count['count'] == 4


class TestRetryExhausted:
    """Test RetryExhausted exception"""

    def test_exception_has_metadata(self):
        """Test exception contains attempt count and last exception"""
        retry = SimpleRetry(max_attempts=2, delay=0.01)

        def always_fail():
            raise ValueError("test error")

        with pytest.raises(RetryExhausted) as exc_info:
            retry.execute(always_fail)

        exc = exc_info.value
        assert exc.attempts == 2
        assert isinstance(exc.last_exception, ValueError)
        assert str(exc.last_exception) == "test error"
