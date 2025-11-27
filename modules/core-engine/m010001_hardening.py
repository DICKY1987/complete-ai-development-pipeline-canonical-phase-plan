"""Production hardening utilities.

Phase I WS-I11: Production-ready error handling and resilience.
"""

from __future__ import annotations

import logging
from typing import Optional, Callable, Any
from functools import wraps
import time


# Configure logging
logger = logging.getLogger(__name__)


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """Decorator for retry with exponential backoff.
    
    Args:
        max_retries: Maximum number of retries
        initial_delay: Initial delay in seconds
        backoff_factor: Backoff multiplier
        exceptions: Tuple of exceptions to catch
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {e}. "
                            f"Retrying in {delay}s..."
                        )
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(f"All {max_retries} retries failed for {func.__name__}")
            
            raise last_exception
        
        return wrapper
    return decorator


class CircuitBreaker:
    """Circuit breaker pattern for resilience."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception
    ):
        """Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Time to wait before trying again
            expected_exception: Exception type to catch
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Call function with circuit breaker protection.
        
        Args:
            func: Function to call
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerError: If circuit is open
        """
        if self.state == 'OPEN':
            # Check if recovery timeout has elapsed
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = 'HALF_OPEN'
                logger.info(f"Circuit breaker entering HALF_OPEN state")
            else:
                raise CircuitBreakerError("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            
            # Success - reset failure count
            if self.state == 'HALF_OPEN':
                self.state = 'CLOSED'
                self.failure_count = 0
                logger.info(f"Circuit breaker reset to CLOSED state")
            
            return result
        
        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
                logger.error(
                    f"Circuit breaker OPENED after {self.failure_count} failures"
                )
            
            raise


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open."""
    pass


class HealthCheck:
    """Health check utilities for production monitoring."""
    
    @staticmethod
    def check_database() -> dict:
        """Check database connectivity.
        
        Returns:
            Health check result
        """
        try:
            from modules.core_state import get_connection
            
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            
            return {
                'status': 'healthy',
                'component': 'database'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'component': 'database',
                'error': str(e)
            }
    
    @staticmethod
    def check_worker_pool() -> dict:
        """Check worker pool health.
        
        Returns:
            Health check result
        """
        try:
            from modules.core_state import get_connection
            
            conn = get_connection()
            cursor = conn.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN state = 'IDLE' THEN 1 ELSE 0 END) as idle,
                       SUM(CASE WHEN state = 'BUSY' THEN 1 ELSE 0 END) as busy
                FROM workers
                WHERE state NOT IN ('TERMINATED')
            """)
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                total, idle, busy = row
                return {
                    'status': 'healthy',
                    'component': 'worker_pool',
                    'total_workers': total,
                    'idle_workers': idle,
                    'busy_workers': busy
                }
            else:
                return {
                    'status': 'healthy',
                    'component': 'worker_pool',
                    'total_workers': 0
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'component': 'worker_pool',
                'error': str(e)
            }
    
    @staticmethod
    def check_all() -> dict:
        """Run all health checks.
        
        Returns:
            Combined health check results
        """
        checks = [
            HealthCheck.check_database(),
            HealthCheck.check_worker_pool()
        ]
        
        unhealthy = [c for c in checks if c['status'] == 'unhealthy']
        
        return {
            'overall_status': 'healthy' if not unhealthy else 'unhealthy',
            'checks': checks,
            'unhealthy_count': len(unhealthy)
        }


class RateLimiter:
    """Rate limiter for API calls."""
    
    def __init__(self, calls_per_minute: int = 60):
        """Initialize rate limiter.
        
        Args:
            calls_per_minute: Maximum calls per minute
        """
        self.calls_per_minute = calls_per_minute
        self.call_times = []
    
    def acquire(self) -> bool:
        """Acquire permission to make a call.
        
        Returns:
            True if call is allowed, False otherwise
        """
        now = time.time()
        
        # Remove calls older than 1 minute
        self.call_times = [t for t in self.call_times if now - t < 60]
        
        if len(self.call_times) < self.calls_per_minute:
            self.call_times.append(now)
            return True
        
        return False
    
    def wait_if_needed(self) -> None:
        """Wait until a call slot is available."""
        while not self.acquire():
            time.sleep(1)


def validate_input(schema: dict, data: dict) -> tuple[bool, Optional[str]]:
    """Validate input data against schema.
    
    Args:
        schema: Schema definition
        data: Data to validate
        
    Returns:
        Tuple of (valid, error_message)
    """
    for field, field_type in schema.items():
        if field not in data:
            return False, f"Missing required field: {field}"
        
        if not isinstance(data[field], field_type):
            return False, f"Field {field} must be of type {field_type.__name__}"
    
    return True, None
