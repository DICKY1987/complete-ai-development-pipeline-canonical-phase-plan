"""Aider Tool Adapter"""
from typing import Dict, Any, List, Optional
from pathlib import Path
from .base import ToolAdapter, ExecutionResult

class AiderAdapter(ToolAdapter):
    def build_command(self, task: Dict[str, Any], prompt_file: Optional[Path] = None) -> List[str]:
        mode = task.get('mode', 'prompt')
        if mode == 'prompt':
            return self._build_prompt_command(task, prompt_file)
        elif mode == 'patch_apply_validate':
            payload = task.get('payload', {})
            patch_file = payload.get('patch_file')
            if not patch_file:
                raise ValueError('patch_file required')
            return ['git', 'apply', str(patch_file)]
        else:
            raise ValueError(f'Unsupported mode: {mode}')
    
    def _build_prompt_command(self, task: Dict[str, Any], prompt_file: Optional[Path]) -> List[str]:
        command = ['aider', '--no-auto-commits', '--yes']
        model = self.get_model_name()
        if model:
            command.extend(['--model', model])
        payload = task.get('payload', {})
        for file in payload.get('files', []):
            command.append(file)
        if prompt_file:
            command.extend(['--message-file', str(prompt_file)])
        elif 'description' in payload:
            command.extend(['--message', payload['description']])
        return command
    
    def execute(self, command: List[str], cwd: str, timeout: int = 600) -> ExecutionResult:
        return self._run_subprocess(command, cwd, timeout, {'PYTHONIOENCODING': 'utf-8'})
# DOC_LINK: DOC-PAT-ADAPTERS-AIDER-ADAPTER-681
