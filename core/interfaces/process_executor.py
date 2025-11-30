"""Process Executor Protocol - Abstraction for subprocess management.

This module defines the ProcessExecutor protocol for centralizing all subprocess
operations with unified timeout, error handling, and dry-run support.

Example:
    >>> from core.execution.subprocess_executor import SubprocessExecutor
    >>> executor = SubprocessExecutor()
    >>> result = executor.run(['echo', 'Hello World'])
    >>> print(result.stdout)
    Hello World
"""
# DOC_ID: DOC-CORE-INTERFACES-PROCESS-EXECUTOR-101

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Optional, Sequence, runtime_checkable
from pathlib import Path


@dataclass
class ProcessResult:
    """Result of a process execution.
    
    Attributes:
        exit_code: Process exit code (0 = success)
        stdout: Standard output as string
        stderr: Standard error as string
        duration_s: Execution duration in seconds
        timed_out: Whether the process was killed due to timeout
        dry_run: Whether this was a dry-run (no actual execution)
        command: Command that was executed
    """
    exit_code: int
    stdout: str
    stderr: str
    duration_s: float
    timed_out: bool = False
    dry_run: bool = False
    command: list[str] | None = None
    
    @property
    def success(self) -> bool:
        """Whether the process succeeded (exit code 0)."""
        return self.exit_code == 0


@dataclass
class ProcessHandle:
    """Handle to an asynchronously running process.
    
    Attributes:
        pid: Process ID
        command: Command being executed
        started_at: Timestamp when process started
    """
    pid: int
    command: list[str]
    started_at: float


@runtime_checkable
class ProcessExecutor(Protocol):
    """Protocol for executing external processes.
    
    This abstraction centralizes all subprocess operations.
    """
    
    def run(
        self,
        command: Sequence[str],
        *,
        timeout: Optional[int] = None,
        cwd: Optional[Path] = None,
        env: Optional[dict[str, str]] = None,
        check: bool = False,
    ) -> ProcessResult:
        """Execute a command synchronously."""
        ...
    
    def run_async(
        self,
        command: Sequence[str],
        *,
        cwd: Optional[Path] = None,
        env: Optional[dict[str, str]] = None,
    ) -> ProcessHandle:
        """Execute a command asynchronously."""
        ...
    
    def kill(self, handle: ProcessHandle) -> None:
        """Kill a running process."""
        ...


class ProcessExecutionError(Exception):
    """Raised when a process fails and check=True."""
    
    def __init__(self, result: ProcessResult):
        self.result = result
        super().__init__(
            f"Command {result.command} failed with exit code {result.exit_code}"
        )
