"""
Pipeline Plus Integration Orchestrator
End-to-end task execution coordinator
"""
DOC_ID: DOC-PAT-CORE-ENGINE-PIPELINE-PLUS-ORCHESTRATOR-396
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timezone

from modules.core_state.m010003_task_queue import TaskQueue, Task, TaskResult
from modules.core_state.m010003_audit_logger import AuditLogger
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine.patch_manager import PatchManager
from modules.core_engine.m010001_prompt_engine import PromptEngine, PromptContext
from modules.core_engine.m010001_validators import ScopeValidator, CircuitBreaker
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine.adapters import AiderAdapter, CodexAdapter, ClaudeAdapter

class PipelinePlusOrchestrator:
    """Main orchestrator for Pipeline Plus"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.task_queue = TaskQueue()
        self.audit_logger = AuditLogger()
        self.patch_manager = PatchManager()
        self.prompt_engine = PromptEngine()
        self.scope_validator = ScopeValidator()
        self.circuit_breaker = CircuitBreaker()
        self.adapters = {
            'aider': AiderAdapter(self.config.get('aider', {})),
            'codex': CodexAdapter(self.config.get('codex', {})),
            'claude': ClaudeAdapter(self.config.get('claude', {}))
        }
    
    def execute_task(self, task: Task, worktree_path: str) -> TaskResult:
        """Execute a task end-to-end"""
        self.audit_logger.log_event('task_received', task.task_id, {'source_app': task.source_app, 'mode': task.mode})
        
        # Get adapter
        adapter_name = task.source_app.lower()
        if adapter_name not in self.adapters:
            return TaskResult(task_id=task.task_id, success=False, error=f'Unknown adapter: {adapter_name}')
        
        adapter = self.adapters[adapter_name]
        
        # Execute
        result = adapter.execute_task(task, worktree_path)
        
        # Audit
        if result.success:
            self.audit_logger.log_event('completed', task.task_id, {'duration': result.duration_sec})
        else:
            self.audit_logger.log_event('failed', task.task_id, {'error': result.error_message})
        
        return TaskResult(task_id=task.task_id, success=result.success, output=result.stdout, error=result.stderr)
