"""Base Tool Adapter - WS-03-02A

Abstract interface for tool adapters.
"""
# DOC_ID: DOC-CORE-ADAPTERS-BASE-133

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime


@dataclass
class ToolConfig:
    """Configuration for a tool"""

    tool_id: str
    kind: str  # 'tool', 'validator', 'analyzer'
    command: str
    capabilities: Dict[str, Any]
    limits: Optional[Dict[str, Any]] = None
    safety_tier: str = "medium"

    def supports_task(self, task_kind: str, domain: Optional[str] = None) -> bool:
        """Check if this tool supports the given task kind and domain"""
        caps = self.capabilities

        # Check task_kinds
        if 'task_kinds' in caps:
            if task_kind not in caps['task_kinds']:
                return False

        # Check domains (if specified)
        if domain and 'domains' in caps:
            if domain not in caps['domains']:
                return False

        return True

    def get_timeout(self) -> int:
        """Get timeout in seconds, or default"""
        if self.limits and 'timeout_seconds' in self.limits:
            return self.limits['timeout_seconds']
        return 300  # 5 minute default

    def get_max_parallel(self) -> int:
        """Get max parallel executions, or default"""
        if self.limits and 'max_parallel' in self.limits:
            return self.limits['max_parallel']
        return 1


@dataclass
class ExecutionResult:
    """Result of a tool execution"""

    success: bool
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    duration_seconds: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'success': self.success,
            'stdout': self.stdout,
            'stderr': self.stderr,
            'exit_code': self.exit_code,
            'duration_seconds': self.duration_seconds,
            'error_message': self.error_message,
            'metadata': self.metadata,
        }


class ToolAdapter(ABC):
    """Abstract base class for tool adapters

    Adapters handle execution of tasks via external tools.
    Each adapter implements the protocol for a specific tool type.
    """

    def __init__(self, config: ToolConfig):
        self.config = config

    @abstractmethod
    def execute(
        self,
        request: Dict[str, Any],
        timeout: Optional[int] = None
    ) -> ExecutionResult:
        """Execute a task request

        Args:
            request: ExecutionRequest dictionary
            timeout: Optional timeout override (seconds)

        Returns:
            ExecutionResult with success/failure and output
        """
        pass

    @abstractmethod
    def validate_request(self, request: Dict[str, Any]) -> bool:
        """Validate that this adapter can handle the request

        Args:
            request: ExecutionRequest dictionary

        Returns:
            True if request is valid for this adapter
        """
        pass

    def supports_task(self, task_kind: str, domain: Optional[str] = None) -> bool:
        """Check if this adapter supports the task kind/domain"""
        return self.config.supports_task(task_kind, domain)

    def get_timeout(self) -> int:
        """Get configured timeout"""
        return self.config.get_timeout()
