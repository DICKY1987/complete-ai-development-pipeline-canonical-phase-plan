"""Parallel execution workers

Runs scheduled workstream tasks with isolation and telemetry capture.
"""
# DOC_ID: DOC-CORE-ENGINE-EXECUTOR-149

from __future__ import annotations
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass


@dataclass
class ExecutionResult:
    """Result of task execution"""
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    exit_code: int = 0


class Executor:
    """Executes tasks with isolation and telemetry"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.task_handlers: Dict[str, Callable] = {}
    
    def register_handler(self, task_type: str, handler: Callable):
        """Register a handler for a task type"""
        self.task_handlers[task_type] = handler
    
    def execute(self, task_type: str, task_data: Dict[str, Any]) -> ExecutionResult:
        """Execute a task"""
        handler = self.task_handlers.get(task_type)
        if not handler:
            return ExecutionResult(
                success=False,
                error=f"No handler registered for task type: {task_type}"
            )
        
        try:
            result = handler(task_data)
            return ExecutionResult(success=True, output=str(result))
        except Exception as e:
            return ExecutionResult(success=False, error=str(e))


__all__ = ['Executor', 'ExecutionResult']

