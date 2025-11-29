"""Logger Protocol - Abstraction for structured logging."""

from __future__ import annotations

from typing import Protocol, Any, runtime_checkable


@runtime_checkable
class Logger(Protocol):
    """Protocol for structured logging.
    
    Features:
    - Structured log messages with context
    - Multiple log levels
    - Job-specific event logging
    """
    
    def info(self, msg: str, **context: Any) -> None:
        """Log info message with context."""
        ...
    
    def error(self, msg: str, **context: Any) -> None:
        """Log error message with context."""
        ...
    
    def warning(self, msg: str, **context: Any) -> None:
        """Log warning message with context."""
        ...
    
    def debug(self, msg: str, **context: Any) -> None:
        """Log debug message with context."""
        ...
    
    def job_event(self, job_id: str, event: str, **data: Any) -> None:
        """Log job-specific event.
        
        Args:
            job_id: Job identifier
            event: Event name (e.g., 'started', 'completed')
            **data: Additional event data
        """
        ...


class LoggerError(Exception):
    """Base exception for logger errors."""
    pass
