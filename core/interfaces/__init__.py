"""Core Interfaces Package - Protocol definitions for abstraction layer."""

from core.interfaces.process_executor import (
    ProcessExecutor,
    ProcessResult,
    ProcessHandle,
    ProcessExecutionError,
)

__all__ = [
    "ProcessExecutor",
    "ProcessResult", 
    "ProcessHandle",
    "ProcessExecutionError",
]
