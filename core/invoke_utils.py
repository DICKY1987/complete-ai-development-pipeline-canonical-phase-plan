"""
Invoke Context utilities for AI Development Pipeline (Phase G - WS-G2).

Provides standardized subprocess execution via Invoke's Context API,
replacing fragmented subprocess.run() calls across the codebase.

Key features:
- Consistent error handling and timeout management
- Standardized result structure (CommandResult)
- Mock-friendly for testing (use MockContext)
- Configuration-aware (loads from invoke.yaml)
"""
DOC_ID: DOC-CORE-CORE-INVOKE-UTILS-044
DOC_ID: DOC-CORE-CORE-INVOKE-UTILS-021

from __future__ import annotations

import os
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from invoke import Context, Result, UnexpectedExit


@dataclass
class CommandResult:
    """
    Standardized result from command execution.
    
    Compatible with existing ToolResult interface for easy migration.
    
    Attributes:
        command: Full command that was executed
        exit_code: Process exit code (0 for success, -1 for timeout/error)
        stdout: Standard output from the process
        stderr: Standard error from the process
        success: Whether execution was successful
        started_at: ISO 8601 UTC timestamp when execution started
        completed_at: ISO 8601 UTC timestamp when execution completed
        duration_sec: Execution duration in seconds
        timed_out: Whether the process exceeded timeout limit
    """
    command: str
    exit_code: int
    stdout: str
    stderr: str
    success: bool
    started_at: str
    completed_at: str
    duration_sec: float
    timed_out: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert CommandResult to dictionary."""
        return asdict(self)


def run_command(
    cmd: str,
    *,
    context: Optional[Context] = None,
    timeout: Optional[int] = None,
    cwd: Optional[Path] = None,
    env: Optional[Dict[str, str]] = None,
    warn: bool = True,
    hide: bool = True,
) -> CommandResult:
    """
    Run a command via Invoke with standardized result.
    
    This is the primary subprocess wrapper for the pipeline. All subprocess.run()
    calls should be migrated to use this function.
    
    Args:
        cmd: Command string to execute (shell syntax supported)
        context: Invoke context (creates default if None)
        timeout: Timeout in seconds (uses config default if None)
        cwd: Working directory (default: current directory)
        env: Environment variables to merge with current env
        warn: Don't raise exception on non-zero exit (default: True)
        hide: Hide command output (default: True, capture to result)
    
    Returns:
        CommandResult with execution details
        
    Example:
        >>> from core.invoke_utils import run_command
        >>> result = run_command('pytest tests/unit -q', timeout=60)
        >>> if result.success:
        >>>     print(f"Tests passed: {result.stdout}")
        >>> else:
        >>>     print(f"Tests failed: {result.stderr}")
    """
    if context is None:
        context = Context()
    
    # Record start time
    started = datetime.utcnow()
    started_str = started.isoformat() + 'Z'
    
    try:
        # Prepare environment
        run_env = os.environ.copy()
        if env:
            run_env.update(env)
        
        # Execute command with optional working directory
        if cwd:
            with context.cd(str(cwd)):
                result = context.run(
                    cmd,
                    hide=hide,
                    warn=warn,
                    timeout=timeout,
                    env=run_env,
                    pty=False,  # Disable PTY for Windows compatibility
                )
        else:
            result = context.run(
                cmd,
                hide=hide,
                warn=warn,
                timeout=timeout,
                env=run_env,
                pty=False,
            )
        
        # Record completion time
        completed = datetime.utcnow()
        duration = (completed - started).total_seconds()
        
        return CommandResult(
            command=cmd,
            exit_code=result.return_code,
            stdout=result.stdout or '',
            stderr=result.stderr or '',
            success=result.ok,
            started_at=started_str,
            completed_at=completed.isoformat() + 'Z',
            duration_sec=duration,
            timed_out=False,
        )
        
    except Exception as e:
        # Handle timeouts and other errors
        completed = datetime.utcnow()
        duration = (completed - started).total_seconds()
        
        # Detect timeout specifically
        timed_out = 'timed out' in str(e).lower() or 'timeout' in str(e).lower()
        
        return CommandResult(
            command=cmd,
            exit_code=-1,
            stdout='',
            stderr=str(e),
            success=False,
            started_at=started_str,
            completed_at=completed.isoformat() + 'Z',
            duration_sec=duration,
            timed_out=timed_out,
        )


def run_tool_command(
    tool_id: str,
    cmd: str,
    *,
    context: Optional[Context] = None,
    timeout: Optional[int] = None,
    cwd: Optional[Path] = None,
    env: Optional[Dict[str, str]] = None,
) -> CommandResult:
    """
    Run a tool command with configuration from invoke.yaml.
    
    Convenience wrapper that loads tool timeout/env from config.
    
    Args:
        tool_id: Tool identifier (e.g., 'pytest', 'ruff')
        cmd: Command to execute
        context: Invoke context
        timeout: Override timeout (uses tool config if None)
        cwd: Working directory
        env: Additional environment variables
        
    Returns:
        CommandResult with execution details
        
    Example:
        >>> result = run_tool_command('pytest', 'pytest tests/ -q')
        >>> # Timeout and env loaded from invoke.yaml tools.pytest section
    """
    from core.config_loader import get_tool_config
    
    # Load tool configuration
    tool_cfg = get_tool_config(tool_id)
    
    # Use configured timeout if not overridden
    if timeout is None:
        timeout = tool_cfg.get('timeout')
    
    # Merge configured environment variables
    tool_env = tool_cfg.get('env', {})
    if env:
        tool_env = {**tool_env, **env}
    
    return run_command(
        cmd,
        context=context,
        timeout=timeout,
        cwd=cwd,
        env=tool_env if tool_env else None,
    )


def create_test_context(
    command_results: Optional[Dict[str, Result]] = None
) -> Context:
    """
    Create a MockContext for testing.
    
    Args:
        command_results: Mapping of command strings to Result objects
        
    Returns:
        MockContext configured with provided results
        
    Example:
        >>> from invoke import Result
        >>> test_ctx = create_test_context({
        ...     'pytest -q': Result(stdout='10 passed', exited=0),
        ...     'ruff check .': Result(stderr='error', exited=1),
        ... })
        >>> result = run_command('pytest -q', context=test_ctx)
        >>> assert result.success
    """
    from invoke import MockContext
    
    if command_results is None:
        command_results = {}
    
    return MockContext(run=command_results)
