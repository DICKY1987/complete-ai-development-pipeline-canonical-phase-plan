"""
Unit tests for RetryPolicy (Phase 4B)
Tests retry logic, backoff strategies, and delay calculations.
"""
DOC_ID: DOC-TEST-TESTS-TEST-RETRY-POLICY-103
DOC_ID: DOC-TEST-TESTS-TEST-RETRY-POLICY-064
import pytest
from engine.queue.retry_policy import (
    RetryPolicy, BackoffStrategy,
    DEFAULT_RETRY_POLICY, FAST_RETRY_POLICY, SLOW_RETRY_POLICY, NO_RETRY_POLICY
)


def test_backoff_strategy_enum():
    """Test backoff strategy enum values"""
    assert BackoffStrategy.IMMEDIATE.value == "immediate"
    assert BackoffStrategy.LINEAR.value == "linear"
    assert BackoffStrategy.EXPONENTIAL.value == "exponential"
    assert BackoffStrategy.FIBONACCI.value == "fibonacci"


def test_retry_policy_defaults():
    """Test default retry policy values"""
    policy = RetryPolicy()
    
    assert policy.max_retries == 3
    assert policy.strategy == BackoffStrategy.EXPONENTIAL
    assert policy.base_delay == 1.0
    assert policy.max_delay == 300.0


def test_should_retry():
    """Test retry limit checking"""
    policy = RetryPolicy(max_retries=3)
    
    assert policy.should_retry(0) is True
    assert policy.should_retry(1) is True
    assert policy.should_retry(2) is True
    assert policy.should_retry(3) is False
    assert policy.should_retry(4) is False


def test_immediate_backoff():
    """Test immediate backoff (no delay)"""
    policy = RetryPolicy(strategy=BackoffStrategy.IMMEDIATE, base_delay=5.0)
    
    assert policy.get_delay(0) == 0
    assert policy.get_delay(1) == 0
    assert policy.get_delay(5) == 0


def test_linear_backoff():
    """Test linear backoff strategy"""
    policy = RetryPolicy(strategy=BackoffStrategy.LINEAR, base_delay=2.0)
    
    assert policy.get_delay(0) == 2.0  # 2.0 * (0 + 1)
    assert policy.get_delay(1) == 4.0  # 2.0 * (1 + 1)
    assert policy.get_delay(2) == 6.0  # 2.0 * (2 + 1)
    assert policy.get_delay(3) == 8.0  # 2.0 * (3 + 1)


def test_exponential_backoff():
    """Test exponential backoff strategy"""
    policy = RetryPolicy(strategy=BackoffStrategy.EXPONENTIAL, base_delay=1.0)
    
    assert policy.get_delay(0) == 1.0   # 1.0 * 2^0
    assert policy.get_delay(1) == 2.0   # 1.0 * 2^1
    assert policy.get_delay(2) == 4.0   # 1.0 * 2^2
    assert policy.get_delay(3) == 8.0   # 1.0 * 2^3
    assert policy.get_delay(4) == 16.0  # 1.0 * 2^4


def test_fibonacci_backoff():
    """Test Fibonacci backoff strategy"""
    policy = RetryPolicy(strategy=BackoffStrategy.FIBONACCI, base_delay=1.0)
    
    # Fibonacci sequence: fib(0)=0, fib(1)=1, fib(2)=1, fib(3)=2, fib(4)=3, fib(5)=5, fib(6)=8, fib(7)=13
    assert policy.get_delay(0) == 1.0   # 1.0 * fib(1) = 1.0
    assert policy.get_delay(1) == 1.0   # 1.0 * fib(2) = 1.0
    assert policy.get_delay(2) == 2.0   # 1.0 * fib(3) = 2.0
    assert policy.get_delay(3) == 3.0   # 1.0 * fib(4) = 3.0
    assert policy.get_delay(4) == 5.0   # 1.0 * fib(5) = 5.0
    assert policy.get_delay(5) == 8.0   # 1.0 * fib(6) = 8.0


def test_max_delay_cap():
    """Test that delays are capped at max_delay"""
    policy = RetryPolicy(
        strategy=BackoffStrategy.EXPONENTIAL,
        base_delay=1.0,
        max_delay=10.0
    )
    
    assert policy.get_delay(0) == 1.0   # 1.0 * 2^0 = 1.0
    assert policy.get_delay(1) == 2.0   # 1.0 * 2^1 = 2.0
    assert policy.get_delay(2) == 4.0   # 1.0 * 2^2 = 4.0
    assert policy.get_delay(3) == 8.0   # 1.0 * 2^3 = 8.0
    assert policy.get_delay(4) == 10.0  # 1.0 * 2^4 = 16.0 -> capped at 10.0
    assert policy.get_delay(5) == 10.0  # 1.0 * 2^5 = 32.0 -> capped at 10.0


def test_from_config():
    """Test creating retry policy from config dict"""
    config = {
        'max_attempts': 5,
        'strategy': 'linear',
        'base_delay': 2.5,
        'max_delay': 100.0
    }
    
    policy = RetryPolicy.from_config(config)
    
    assert policy.max_retries == 5
    assert policy.strategy == BackoffStrategy.LINEAR
    assert policy.base_delay == 2.5
    assert policy.max_delay == 100.0


def test_from_config_defaults():
    """Test from_config with missing values uses defaults"""
    config = {}
    
    policy = RetryPolicy.from_config(config)
    
    assert policy.max_retries == 3  # default
    assert policy.strategy == BackoffStrategy.EXPONENTIAL  # default
    assert policy.base_delay == 1.0  # default
    assert policy.max_delay == 300.0  # default


def test_to_dict():
    """Test converting policy to dict"""
    policy = RetryPolicy(
        max_retries=5,
        strategy=BackoffStrategy.LINEAR,
        base_delay=2.0,
        max_delay=120.0
    )
    
    policy_dict = policy.to_dict()
    
    assert policy_dict['max_retries'] == 5
    assert policy_dict['strategy'] == 'linear'
    assert policy_dict['base_delay'] == 2.0
    assert policy_dict['max_delay'] == 120.0


def test_default_retry_policy():
    """Test DEFAULT_RETRY_POLICY constant"""
    assert DEFAULT_RETRY_POLICY.max_retries == 3
    assert DEFAULT_RETRY_POLICY.strategy == BackoffStrategy.EXPONENTIAL
    assert DEFAULT_RETRY_POLICY.base_delay == 1.0


def test_fast_retry_policy():
    """Test FAST_RETRY_POLICY constant"""
    assert FAST_RETRY_POLICY.max_retries == 2
    assert FAST_RETRY_POLICY.strategy == BackoffStrategy.LINEAR
    assert FAST_RETRY_POLICY.base_delay == 0.5


def test_slow_retry_policy():
    """Test SLOW_RETRY_POLICY constant"""
    assert SLOW_RETRY_POLICY.max_retries == 5
    assert SLOW_RETRY_POLICY.strategy == BackoffStrategy.EXPONENTIAL
    assert SLOW_RETRY_POLICY.base_delay == 2.0
    assert SLOW_RETRY_POLICY.max_delay == 600.0


def test_no_retry_policy():
    """Test NO_RETRY_POLICY constant"""
    assert NO_RETRY_POLICY.max_retries == 0
    assert NO_RETRY_POLICY.strategy == BackoffStrategy.IMMEDIATE
    assert NO_RETRY_POLICY.should_retry(0) is False


def test_fibonacci_helper():
    """Test internal Fibonacci calculation"""
    policy = RetryPolicy(strategy=BackoffStrategy.FIBONACCI)
    
    assert policy._fibonacci(0) == 0
    assert policy._fibonacci(1) == 1
    assert policy._fibonacci(2) == 1
    assert policy._fibonacci(3) == 2
    assert policy._fibonacci(4) == 3
    assert policy._fibonacci(5) == 5
    assert policy._fibonacci(6) == 8
    assert policy._fibonacci(7) == 13
    assert policy._fibonacci(8) == 21
