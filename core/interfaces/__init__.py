"""Core Interfaces Package - Protocol definitions for abstraction layer."""

from core.interfaces.process_executor import (
    ProcessExecutor,
    ProcessResult,
    ProcessHandle,
    ProcessExecutionError,
)
from core.interfaces.state_store import (
    StateStore,
    StateStoreError,
    WorkstreamNotFoundError,
    ExecutionNotFoundError,
)
from core.interfaces.tool_adapter import (
    ToolAdapter,
    ToolAdapterError,
    CapabilityNotSupportedError,
    JobPreparationError,
)

__all__ = [
    "ProcessExecutor",
    "ProcessResult", 
    "ProcessHandle",
    "ProcessExecutionError",
    "StateStore",
    "StateStoreError",
    "WorkstreamNotFoundError",
    "ExecutionNotFoundError",
    "ToolAdapter",
    "ToolAdapterError",
    "CapabilityNotSupportedError",
    "JobPreparationError",
]
