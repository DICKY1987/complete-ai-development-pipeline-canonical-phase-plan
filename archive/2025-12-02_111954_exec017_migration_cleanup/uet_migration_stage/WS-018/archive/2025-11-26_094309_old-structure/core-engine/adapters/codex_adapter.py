"""Codex Tool Adapter"""
from typing import Dict, Any, List, Optional
from pathlib import Path
from .base import ToolAdapter, ExecutionResult

class CodexAdapter(ToolAdapter):
    def build_command(self, task: Dict[str, Any], prompt_file: Optional[Path] = None) -> List[str]:
        command = ['gh', 'copilot', 'suggest']
        if prompt_file and prompt_file.exists():
            prompt_text = prompt_file.read_text(encoding='utf-8')
            command.extend(['-t', 'shell', prompt_text])
        else:
            payload = task.get('payload', {})
            description = payload.get('description', 'Execute task')
            command.extend(['-t', 'shell', description])
        return command
    
    def execute(self, command: List[str], cwd: str, timeout: int = 600) -> ExecutionResult:
        return self._run_subprocess(command, cwd, timeout)
# DOC_LINK: DOC-PAT-ADAPTERS-CODEX-ADAPTER-684
