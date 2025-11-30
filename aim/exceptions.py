"""Custom exceptions for AIM module.

Provides domain-specific exception classes for better error handling
and debugging of AIM registry operations.
"""
DOC_ID: DOC-AIM-AIM-EXCEPTIONS-081
DOC_ID: DOC-AIM-AIM-EXCEPTIONS-076
DOC_ID: DOC-AIM-AIM-EXCEPTIONS-073
DOC_ID: DOC-AIM-AIM-EXCEPTIONS-071

from typing import Any, Dict, List, Tuple


class AIMError(Exception):
    """Base exception for all AIM-related errors."""
    pass


class AIMRegistryNotFoundError(AIMError):
    """AIM registry directory not found.
    
    Raised when the AIM registry directory cannot be located
    via environment variable or auto-detection.
    """
    pass


class AIMRegistryLoadError(AIMError):
    """Failed to load or parse AIM registry files.
    
    Raised when registry JSON files are malformed or cannot be read.
    """
    pass


class AIMCapabilityNotFoundError(AIMError):
    """Requested capability not defined in coordination rules.
    
    Raised when attempting to route a capability that doesn't exist
    in the coordination rules configuration.
    """
    
    def __init__(self, capability: str, available_capabilities: List[str] = None):
        self.capability = capability
        self.available_capabilities = available_capabilities or []
        
        msg = f"Capability '{capability}' not defined in coordination rules"
        if self.available_capabilities:
            msg += f". Available: {', '.join(sorted(self.available_capabilities))}"
        
        super().__init__(msg)


class AIMToolNotFoundError(AIMError):
    """Requested tool not found in AIM registry.
    
    Raised when attempting to invoke a tool that doesn't exist
    in the registry.
    """
    
    def __init__(self, tool_id: str, available_tools: List[str] = None):
        self.tool_id = tool_id
        self.available_tools = available_tools or []
        
        msg = f"Tool '{tool_id}' not found in AIM registry"
        if self.available_tools:
            msg += f". Available: {', '.join(sorted(self.available_tools))}"
        
        super().__init__(msg)


class AIMAdapterNotFoundError(AIMError):
    """Adapter script not found for tool.
    
    Raised when a tool's adapter script path is invalid or
    the file doesn't exist.
    """
    
    def __init__(self, tool_id: str, adapter_path: str):
        self.tool_id = tool_id
        self.adapter_path = adapter_path
        super().__init__(
            f"Adapter script not found for tool '{tool_id}': {adapter_path}"
        )


class AIMAdapterInvocationError(AIMError):
    """Adapter subprocess invocation failed.
    
    Raised when the PowerShell adapter process exits with
    a non-zero code or produces invalid output.
    """
    
    def __init__(self, tool_id: str, exit_code: int, stderr: str):
        self.tool_id = tool_id
        self.exit_code = exit_code
        self.stderr = stderr
        super().__init__(
            f"Adapter '{tool_id}' failed with exit code {exit_code}: {stderr}"
        )


class AIMAdapterTimeoutError(AIMError):
    """Adapter subprocess timed out.
    
    Raised when an adapter invocation exceeds the configured
    timeout period.
    """
    
    def __init__(self, tool_id: str, timeout_sec: int):
        self.tool_id = tool_id
        self.timeout_sec = timeout_sec
        super().__init__(
            f"Adapter '{tool_id}' timed out after {timeout_sec} seconds"
        )


class AIMAdapterOutputError(AIMError):
    """Adapter produced invalid or unparseable output.
    
    Raised when adapter stdout cannot be parsed as JSON or
    is missing required fields.
    """
    
    def __init__(self, tool_id: str, output: str, parse_error: str):
        self.tool_id = tool_id
        self.output = output
        self.parse_error = parse_error
        super().__init__(
            f"Adapter '{tool_id}' produced invalid output: {parse_error}"
        )


class AIMAllToolsFailedError(AIMError):
    """All tools in fallback chain failed.
    
    Raised when both the primary tool and all fallback tools
    fail to successfully execute a capability.
    """
    
    def __init__(self, capability: str, attempts: List[Tuple[str, Dict[str, Any]]]):
        self.capability = capability
        self.attempts = attempts
        
        # Build detailed error message
        msg = f"All tools failed for capability '{capability}'"
        if attempts:
            msg += ":\n"
            for tool_id, result in attempts:
                error_msg = result.get("message", "Unknown error")
                msg += f"  - {tool_id}: {error_msg}\n"
        
        super().__init__(msg.rstrip())


class AIMValidationError(AIMError):
    """Input payload failed validation.
    
    Raised when a payload violates security constraints or
    capability requirements.
    """
    
    def __init__(self, field: str, reason: str):
        self.field = field
        self.reason = reason
        super().__init__(f"Validation failed for '{field}': {reason}")


class AIMAuditLogError(AIMError):
    """Failed to write audit log entry.
    
    Raised when audit logging fails due to permission issues,
    disk space, or other I/O errors.
    """
    
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Failed to write audit log: {reason}")
