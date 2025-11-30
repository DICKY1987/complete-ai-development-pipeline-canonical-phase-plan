"""Subprocess Executor - Concrete implementation of ProcessExecutor protocol."""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path
from typing import Optional, Sequence

from core.interfaces.process_executor import (
    ProcessExecutor,
    ProcessResult,
    ProcessHandle,
    ProcessExecutionError,
)


class SubprocessExecutor:
    """Concrete implementation of ProcessExecutor using subprocess module.
    
    Features:
    - Timeout enforcement with automatic process termination
    - Dry-run mode for safe testing
    - Consistent error handling
    - Output capture for stdout/stderr
    
    Example:
        >>> executor = SubprocessExecutor(dry_run=False)
        >>> result = executor.run(['echo', 'Hello'], timeout=10)
        >>> print(result.stdout)
        Hello
    """
# DOC_ID: DOC-CORE-EXECUTION-SUBPROCESS-EXECUTOR-087
    
    def __init__(self, dry_run: bool = False):
        """Initialize SubprocessExecutor.
        
        Args:
            dry_run: If True, commands are logged but not executed
        """
        self.dry_run = dry_run
        self._async_processes: dict[int, subprocess.Popen] = {}
    
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
        cmd_list = list(command)
        
        if self.dry_run:
            return ProcessResult(
                exit_code=0,
                stdout=f"[DRY-RUN] Would run: {' '.join(cmd_list)}",
                stderr="",
                duration_s=0.0,
                dry_run=True,
                command=cmd_list,
            )
        
        start_time = time.time()
        timed_out = False
        
        try:
            process = subprocess.Popen(
                cmd_list,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(cwd) if cwd else None,
                env=env or os.environ.copy(),
                text=True,
            )
            
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                exit_code = process.returncode
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                exit_code = -1
                timed_out = True
                
        except Exception as e:
            duration_s = time.time() - start_time
            result = ProcessResult(
                exit_code=-1,
                stdout="",
                stderr=str(e),
                duration_s=duration_s,
                command=cmd_list,
            )
            if check:
                raise ProcessExecutionError(result)
            return result
        
        duration_s = time.time() - start_time
        
        result = ProcessResult(
            exit_code=exit_code,
            stdout=stdout or "",
            stderr=stderr or "",
            duration_s=duration_s,
            timed_out=timed_out,
            command=cmd_list,
        )
        
        if check and not result.success:
            raise ProcessExecutionError(result)
        
        return result
    
    def run_async(
        self,
        command: Sequence[str],
        *,
        cwd: Optional[Path] = None,
        env: Optional[dict[str, str]] = None,
    ) -> ProcessHandle:
        """Execute a command asynchronously."""
        cmd_list = list(command)
        
        process = subprocess.Popen(
            cmd_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(cwd) if cwd else None,
            env=env or os.environ.copy(),
            text=True,
        )
        
        handle = ProcessHandle(
            pid=process.pid,
            command=cmd_list,
            started_at=time.time(),
        )
        
        self._async_processes[process.pid] = process
        
        return handle
    
    def kill(self, handle: ProcessHandle) -> None:
        """Kill a running process."""
        process = self._async_processes.get(handle.pid)
        if process and process.poll() is None:
            process.kill()
            process.wait()
        
        if handle.pid in self._async_processes:
            del self._async_processes[handle.pid]
