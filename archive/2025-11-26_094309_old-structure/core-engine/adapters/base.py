"""
Base Tool Adapter for Pipeline Plus
Abstract interface for tool-specific execution
"""
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from pathlib import Path


@dataclass
class ExecutionResult:
    """Result of tool execution"""
    success: bool
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    duration_sec: float = 0.0
    timed_out: bool = False
    error_message: Optional[str] = None
    artifacts: Dict[str, Any] = field(default_factory=dict)


class ToolAdapter(ABC):
    """Abstract base class for tool adapters"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.name = self.__class__.__name__.replace('Adapter', '').lower()
    
    @abstractmethod
    def build_command(self, task: Dict[str, Any], prompt_file: Optional[Path] = None) -> List[str]:
        pass
    
    @abstractmethod
    def execute(self, command: List[str], cwd: str, timeout: int = 600) -> ExecutionResult:
        pass
    
    def execute_task(self, task: Dict[str, Any], worktree_path: str, prompt_file: Optional[Path] = None, timeout: Optional[int] = None) -> ExecutionResult:
        command = self.build_command(task, prompt_file)
        if timeout is None:
            timeout = task.get('timeouts', {}).get('wall_clock_sec', 600)
        return self.execute(command, worktree_path, timeout)
    
    def _run_subprocess(self, command: List[str], cwd: str, timeout: int, env: Optional[Dict[str, str]] = None) -> ExecutionResult:
        import time, os
        start_time = time.time()
        process_env = os.environ.copy()
        if env:
            process_env.update(env)
        process_env['PYTHONIOENCODING'] = 'utf-8'
        try:
            result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, encoding='utf-8', timeout=timeout, env=process_env)
            duration = time.time() - start_time
            return ExecutionResult(success=result.returncode == 0, exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr, duration_sec=duration, timed_out=False)
        except subprocess.TimeoutExpired as e:
            duration = time.time() - start_time
            return ExecutionResult(success=False, exit_code=-1, stdout=e.stdout.decode('utf-8') if e.stdout else '', stderr=e.stderr.decode('utf-8') if e.stderr else '', duration_sec=duration, timed_out=True, error_message=f"Command timed out after {timeout}s")
        except Exception as e:
            duration = time.time() - start_time
            return ExecutionResult(success=False, exit_code=-1, duration_sec=duration, error_message=str(e))
    
    def get_default_timeout(self) -> int:
        return self.config.get('timeout', 600)
    
    def get_model_name(self) -> Optional[str]:
        return self.config.get('model')
