"""Subprocess Tool Adapter - WS-03-02A

Executes tools via subprocess with timeout and error handling.
"""

# DOC_ID: DOC-CORE-ADAPTERS-SUBPROCESS-ADAPTER-135

import subprocess
import time
from typing import Any, Dict, Optional

from .base import ExecutionResult, ToolAdapter, ToolConfig


class SubprocessAdapter(ToolAdapter):
    """Adapter that executes tools via subprocess

    Handles:
    - Command execution with timeout
    - stdout/stderr capture
    - Exit code handling
    - Error reporting
    """

    def __init__(self, config: ToolConfig):
        super().__init__(config)

    def validate_request(self, request: Dict[str, Any]) -> bool:
        """Validate request has required fields"""
        required = ["request_id", "task_kind", "project_id"]
        return all(field in request for field in required)

    def execute(
        self, request: Dict[str, Any], timeout: Optional[int] = None
    ) -> ExecutionResult:
        """Execute the tool via subprocess

        Args:
            request: ExecutionRequest with task details
            timeout: Optional timeout override

        Returns:
            ExecutionResult with success/output
        """
        if not self.validate_request(request):
            return ExecutionResult(
                success=False, error_message="Invalid request: missing required fields"
            )

        # Determine timeout
        timeout_secs = timeout or self.get_timeout()

        # Build command
        cmd = self._build_command(request)

        # Execute
        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_secs,
                shell=True,  # Allow complex commands
            )

            duration = time.time() - start_time

            return ExecutionResult(
                success=(result.returncode == 0),
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
                duration_seconds=duration,
                metadata={
                    "command": " ".join(cmd) if isinstance(cmd, list) else cmd,
                    "timeout": timeout_secs,
                },
            )

        except subprocess.TimeoutExpired as e:
            duration = time.time() - start_time
            return ExecutionResult(
                success=False,
                stdout=e.stdout.decode() if e.stdout else "",
                stderr=e.stderr.decode() if e.stderr else "",
                exit_code=-1,
                duration_seconds=duration,
                error_message=f"Command timed out after {timeout_secs}s",
                metadata={
                    "command": " ".join(cmd) if isinstance(cmd, list) else cmd,
                    "timeout": timeout_secs,
                    "timeout_exceeded": True,
                },
            )

        except Exception as e:
            duration = time.time() - start_time
            return ExecutionResult(
                success=False,
                exit_code=-1,
                duration_seconds=duration,
                error_message=f"Execution failed: {str(e)}",
                metadata={
                    "command": " ".join(cmd) if isinstance(cmd, list) else cmd,
                    "exception_type": type(e).__name__,
                },
            )

    def _build_command(self, request: Dict[str, Any]) -> str:
        """Build the command string from request

        Args:
            request: ExecutionRequest

        Returns:
            Command string to execute
        """
        # Base command from config
        cmd = self.config.command

        # Add request-specific args
        # This is a simple implementation - production would need more sophistication

        # For now, just return the base command
        # Future: parse request to build arguments
        return cmd
