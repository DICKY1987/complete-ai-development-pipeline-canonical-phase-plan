"""Core Interfaces Package - Protocol definitions for abstraction layer."""

from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.interfaces.process_executor import (
    ProcessExecutor,
    ProcessResult,
    ProcessHandle,
    ProcessExecutionError,
)
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.interfaces.state_store import (
    StateStore,
    StateStoreError,
    WorkstreamNotFoundError,
    ExecutionNotFoundError,
)
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.interfaces.tool_adapter import (
    ToolAdapter,
    ToolAdapterError,
    CapabilityNotSupportedError,
    JobPreparationError,
)
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.interfaces.config_manager import (
    ConfigManager,
    ConfigError,
    ConfigValidationError,
    ToolProfileNotFoundError,
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
    "ConfigManager",
    "ConfigError",
    "ConfigValidationError",
    "ToolProfileNotFoundError",
]
# DOC_LINK: DOC-CORE-INTERFACES-INIT-106
