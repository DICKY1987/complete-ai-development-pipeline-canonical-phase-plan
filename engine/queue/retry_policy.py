"""
Retry Policy - Retry logic with backoff strategies.

Provides retry mechanisms with:
- Multiple backoff strategies
- Configurable retry limits
- Retry delay calculation
"""
# DOC_ID: DOC-PAT-QUEUE-RETRY-POLICY-456

from enum import Enum
from typing import Optional
import math


class BackoffStrategy(Enum):
    """Retry backoff strategies."""
    IMMEDIATE = "immediate"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    FIBONACCI = "fibonacci"


class RetryPolicy:
    """
    Retry policy with configurable backoff.
    
    Features:
    - Multiple backoff strategies
    - Configurable max retries
    - Delay calculation
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL,
        base_delay: float = 1.0,
        max_delay: float = 300.0
    ):
        """
        Initialize retry policy.
        
        Args:
            max_retries: Maximum number of retries
            strategy: Backoff strategy to use
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds
        """
        self.max_retries = max_retries
        self.strategy = strategy
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def should_retry(self, attempt: int) -> bool:
        """
        Check if should retry.
        
        Args:
            attempt: Current attempt number (0-indexed)
            
        Returns:
            True if should retry
        """
        return attempt < self.max_retries
    
    def get_delay(self, attempt: int) -> float:
        """
        Calculate retry delay.
        
        Args:
            attempt: Current attempt number (0-indexed)
            
        Returns:
            Delay in seconds
        """
        if self.strategy == BackoffStrategy.IMMEDIATE:
            delay = 0
        
        elif self.strategy == BackoffStrategy.LINEAR:
            delay = self.base_delay * (attempt + 1)
        
        elif self.strategy == BackoffStrategy.EXPONENTIAL:
            delay = self.base_delay * (2 ** attempt)
        
        elif self.strategy == BackoffStrategy.FIBONACCI:
            delay = self.base_delay * self._fibonacci(attempt + 1)
        
        else:
            delay = self.base_delay
        
        # Cap at max_delay
        return min(delay, self.max_delay)
    
    def _fibonacci(self, n: int) -> int:
        """Calculate nth Fibonacci number."""
        if n <= 1:
            return n
        
        a, b = 0, 1
        for _ in range(n - 1):
            a, b = b, a + b
        return b
    
    @classmethod
    def from_config(cls, config: dict) -> 'RetryPolicy':
        """
        Create retry policy from config.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            RetryPolicy instance
        """
        return cls(
            max_retries=config.get('max_attempts', 3),
            strategy=BackoffStrategy(config.get('strategy', 'exponential')),
            base_delay=config.get('base_delay', 1.0),
            max_delay=config.get('max_delay', 300.0)
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'max_retries': self.max_retries,
            'strategy': self.strategy.value,
            'base_delay': self.base_delay,
            'max_delay': self.max_delay
        }


# Default retry policies for different scenarios
DEFAULT_RETRY_POLICY = RetryPolicy(
    max_retries=3,
    strategy=BackoffStrategy.EXPONENTIAL,
    base_delay=1.0
)

FAST_RETRY_POLICY = RetryPolicy(
    max_retries=2,
    strategy=BackoffStrategy.LINEAR,
    base_delay=0.5
)

SLOW_RETRY_POLICY = RetryPolicy(
    max_retries=5,
    strategy=BackoffStrategy.EXPONENTIAL,
    base_delay=2.0,
    max_delay=600.0
)

NO_RETRY_POLICY = RetryPolicy(
    max_retries=0,
    strategy=BackoffStrategy.IMMEDIATE
)
