"""Claude Tool Adapter"""
from typing import Dict, Any, List, Optional
from pathlib import Path
from .base import ToolAdapter, ExecutionResult

class ClaudeAdapter(ToolAdapter):
    def build_command(self, task: Dict[str, Any], prompt_file: Optional[Path] = None) -> List[str]:
        mode = task.get('mode', 'prompt')
        if mode == 'prompt':
            return self._build_prompt_command(task, prompt_file)
        elif mode == 'review':
            return self._build_review_command(task)
        else:
            raise ValueError(f'Unsupported mode: {mode}')
    
    def _build_prompt_command(self, task: Dict[str, Any], prompt_file: Optional[Path]) -> List[str]:
        command = ['claude']
        model = self.get_model_name() or 'claude-3-sonnet'
        command.extend(['--model', model])
        payload = task.get('payload', {})
        for file in payload.get('files', []):
            command.extend(['--file', file])
        if prompt_file and prompt_file.exists():
            command.extend(['--prompt-file', str(prompt_file)])
        elif 'description' in payload:
            command.extend(['--prompt', payload['description']])
        return command
    
    def _build_review_command(self, task: Dict[str, Any]) -> List[str]:
        command = ['claude', 'review']
        payload = task.get('payload', {})
        for file in payload.get('files', []):
            command.append(file)
        return command
    
    def execute(self, command: List[str], cwd: str, timeout: int = 600) -> ExecutionResult:
        return self._run_subprocess(command, cwd, timeout)
