"""
Abstract base adapter for tool integration.

All coverage analysis tool adapters (coverage.py, Pester, mutmut, Radon, etc.)
must inherit from BaseAdapter and implement the execute() method.
"""

import logging
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class BaseAdapter(ABC):
    """
    Abstract base class for all tool adapters.

    Adapters wrap external tools (coverage.py, Pester, Bandit, etc.) and
    provide a consistent interface for execution and result parsing.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the adapter.

        Args:
            config: Optional configuration dictionary for the tool
        """
        self.config = config or {}
        self.tool_name = self._get_tool_name()

    @abstractmethod
    def _get_tool_name(self) -> str:
        """Return the name of the wrapped tool."""
        pass

    @abstractmethod
    def execute(self, target_path: str, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool and return parsed results.

        Args:
            target_path: Path to code to analyze
            **kwargs: Tool-specific arguments

        Returns:
            Dictionary containing parsed tool output

        Raises:
            ToolExecutionError: If tool execution fails
        """
        pass

    def is_tool_available(self) -> bool:
        """
        Check if the tool is installed and available.

        Returns:
            True if tool is available, False otherwise
        """
        try:
            result = self._run_command([self.tool_name, "--version"])
            return result.returncode == 0
        except (FileNotFoundError, subprocess.SubprocessError):
            return False

    def _run_command(
        self, command: list, cwd: Optional[Path] = None, timeout: int = 300
    ) -> subprocess.CompletedProcess:
        """
        Run a command and return the result.

        Args:
            command: Command and arguments as list
            cwd: Working directory for command execution
            timeout: Command timeout in seconds

        Returns:
            CompletedProcess instance

        Raises:
            ToolExecutionError: If command fails
        """
        try:
            logger.debug(f"Running command: {' '.join(command)}")
            result = subprocess.run(
                command, cwd=cwd, capture_output=True, text=True, timeout=timeout
            )

            if result.returncode != 0 and result.stderr:
                logger.warning(f"Command stderr: {result.stderr}")

            return result

        except subprocess.TimeoutExpired as e:
            raise ToolExecutionError(
                f"Command timed out after {timeout}s: {' '.join(command)}"
            ) from e
        except Exception as e:
            raise ToolExecutionError(
                f"Command execution failed: {' '.join(command)}"
            ) from e

    def validate_target_path(self, target_path: str) -> Path:
        """
        Validate that target path exists.

        Args:
            target_path: Path to validate

        Returns:
            Validated Path object

        Raises:
            ValueError: If path doesn't exist
        """
        path = Path(target_path)
        if not path.exists():
            raise ValueError(f"Target path does not exist: {target_path}")
        return path


class ToolExecutionError(Exception):
    """Raised when a tool execution fails."""

    pass


class ToolNotAvailableError(Exception):
    """Raised when a required tool is not installed."""

    pass
