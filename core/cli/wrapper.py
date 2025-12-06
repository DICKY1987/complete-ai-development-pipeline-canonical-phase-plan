"""CLI wrapper for automated, non-interactive script execution with orchestrator integration."""
DOC_ID: DOC-CORE-CLI-WRAPPER-854

from __future__ import annotations

import os
import subprocess
import sys
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.events.event_bus import EventBus, EventType


@dataclass
class ExecutionResult:
    """Result of script execution."""
    
    script_path: str
    args: List[str]
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    timestamp: str
    run_id: Optional[str] = None
    timed_out: bool = False
    
    @property
    def succeeded(self) -> bool:
        """Check if execution was successful."""
        return self.exit_code == 0 and not self.timed_out
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class CLIWrapper:
    """Wrapper for CLI scripts with orchestrator integration, timeout, and state tracking."""
    
    def __init__(
        self,
        orchestrator: Optional[Any] = None,
        timeout: int = 300,
        event_bus: Optional[EventBus] = None,
        state_dir: Path = Path(".state")
    ):
        """Initialize CLI wrapper.
        
        Args:
            orchestrator: Optional orchestrator instance for run tracking
            timeout: Maximum execution time in seconds (default: 5 minutes)
            event_bus: Optional event bus for publishing execution events
            state_dir: Directory for storing execution state
        """
        self.orchestrator = orchestrator
        self.timeout = timeout
        self.event_bus = event_bus
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.execution_log = self.state_dir / "cli_executions.jsonl"
    
    def wrap(
        self,
        script_path: str,
        args: Optional[List[str]] = None,
        non_interactive: bool = True,
        timeout: Optional[int] = None,
        cwd: Optional[str] = None
    ) -> ExecutionResult:
        """Execute a script with full tracking and error handling.
        
        Args:
            script_path: Path to script to execute
            args: Command-line arguments
            non_interactive: Set NON_INTERACTIVE=1 environment variable
            timeout: Override default timeout
            cwd: Working directory for execution
            
        Returns:
            ExecutionResult with stdout, stderr, exit code, and metadata
        """
        args = args or []
        timeout = timeout or self.timeout
        
        env = os.environ.copy()
        if non_interactive:
            env['NON_INTERACTIVE'] = '1'
        
        run_id = None
        if self.orchestrator:
            run_id = self.orchestrator.create_run(
                script_path=script_path,
                args=args,
                timeout=timeout
            )
        
        if self.event_bus:
            self.event_bus.publish(
                EventType.TOOL_INVOKED.value,
                {
                    "run_id": run_id,
                    "script_path": script_path,
                    "args": args,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        start_time = datetime.now(timezone.utc)
        timed_out = False
        
        try:
            # Determine interpreter
            if script_path.endswith('.py'):
                cmd = [sys.executable, script_path] + args
            elif script_path.endswith('.ps1'):
                cmd = ['powershell', '-ExecutionPolicy', 'Bypass', '-File', script_path] + args
            else:
                cmd = [script_path] + args
            
            result = subprocess.run(
                cmd,
                timeout=timeout,
                env=env,
                capture_output=True,
                text=True,
                cwd=cwd
            )
            
            stdout = result.stdout
            stderr = result.stderr
            exit_code = result.returncode
            
        except subprocess.TimeoutExpired as e:
            timed_out = True
            stdout = e.stdout.decode() if e.stdout else ""
            stderr = e.stderr.decode() if e.stderr else ""
            exit_code = -1
            
        except Exception as e:
            stdout = ""
            stderr = f"CLI wrapper error: {str(e)}"
            exit_code = -2
        
        duration = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        exec_result = ExecutionResult(
            script_path=script_path,
            args=args,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            duration_seconds=duration,
            timestamp=start_time.isoformat(),
            run_id=run_id,
            timed_out=timed_out
        )
        
        self._record_execution(exec_result)
        
        if self.orchestrator:
            self.orchestrator.record_cli_execution(run_id, exec_result)
        
        if self.event_bus:
            event_type = EventType.TOOL_SUCCEEDED if exec_result.succeeded else EventType.TOOL_FAILED
            self.event_bus.publish(
                event_type.value,
                {
                    "run_id": run_id,
                    "script_path": script_path,
                    "exit_code": exit_code,
                    "duration": duration,
                    "timed_out": timed_out,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        return exec_result
    
    def _record_execution(self, result: ExecutionResult) -> None:
        """Record execution to JSONL log."""
        with open(self.execution_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(result.to_dict()) + '\n')
    
    def get_execution_history(
        self,
        script_path: Optional[str] = None,
        limit: int = 100
    ) -> List[ExecutionResult]:
        """Retrieve execution history.
        
        Args:
            script_path: Optional filter by script path
            limit: Maximum number of results
            
        Returns:
            List of ExecutionResult objects
        """
        if not self.execution_log.exists():
            return []
        
        results = []
        with open(self.execution_log, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                if script_path is None or data['script_path'] == script_path:
                    results.append(ExecutionResult(**data))
                    if len(results) >= limit:
                        break
        
        return list(reversed(results))  # Most recent first
