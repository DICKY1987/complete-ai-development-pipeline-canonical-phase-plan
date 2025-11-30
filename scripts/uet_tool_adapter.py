"""
UET Tool Adapter
Wraps existing engine adapters for UET orchestrator
"""
DOC_ID: DOC-SCRIPT-SCRIPTS-UET-TOOL-ADAPTER-239
DOC_ID: DOC-SCRIPT-SCRIPTS-UET-TOOL-ADAPTER-176

import logging
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class ToolAdapter:
    """Adapter for executing tools within UET framework."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.tool_config = config.get('tools', {})
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task using appropriate tool adapter.
        
        Args:
            task: Task dictionary with metadata
        
        Returns:
            Result dictionary with success, output, error
        """
        metadata = task.get('metadata', {})
        tool = metadata.get('tool', 'aider')
        task_id = task.get('task_id', 'unknown')
        
        logger.info(f"Executing task {task_id} with tool: {tool}")
        
        # Build job dict for adapter
        job_dict = self._build_job_dict(task)
        
        try:
            # Import and execute appropriate adapter
            result = self._execute_adapter(tool, job_dict)
            
            logger.info(f"Task {task_id} completed: {result.get('success', False)}")
            
            return {
                'success': result.get('success', False),
                'exit_code': result.get('exit_code', 0),
                'output': result.get('stdout', ''),
                'error': result.get('stderr', ''),
                'duration': result.get('duration_s', 0.0),
                'patch_file': result.get('error_report_path', '')
            }
        
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'exit_code': -1
            }
    
    def _execute_adapter(self, tool: str, job_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the appropriate tool adapter."""
        try:
            if tool == 'aider':
                from engine.adapters.aider_adapter import run_aider_job
                return run_aider_job(job_dict)
            elif tool == 'codex':
                from engine.adapters.codex_adapter import run_codex_job
                return run_codex_job(job_dict)
            elif tool == 'git':
                from engine.adapters.git_adapter import run_git_job
                return run_git_job(job_dict)
            elif tool == 'tests':
                from engine.adapters.tests_adapter import run_tests_job
                return run_tests_job(job_dict)
            else:
                return {
                    'success': False,
                    'error': f"Unknown tool: {tool}",
                    'exit_code': -1
                }
        except ImportError as e:
            logger.error(f"Failed to import adapter for {tool}: {e}")
            return {
                'success': False,
                'error': f"Adapter not found for tool: {tool}",
                'exit_code': -1
            }
    
    def _build_job_dict(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Build job dictionary for existing adapters."""
        metadata = task.get('metadata', {})
        
        return {
            'job_id': task.get('task_id'),
            'workstream_id': task.get('task_id'),
            'tool': metadata.get('tool', 'aider'),
            'files': metadata.get('files', []),
            'instructions': '\n'.join(metadata.get('tasks', [])),
            'config': self.tool_config.get(metadata.get('tool', 'aider'), {})
        }
    
    def get_tool_for_file(self, file_path: str) -> str:
        """
        Determine which tool to use for a file based on routing rules.
        
        Args:
            file_path: Path to file
        
        Returns:
            Tool name
        """
        routing = self.config.get('adapters', {}).get('routing', [])
        
        # Sort by priority (descending)
        routing = sorted(routing, key=lambda r: r.get('priority', 0), reverse=True)
        
        # Match pattern
        for rule in routing:
            pattern = rule.get('pattern', '')
            if self._matches_pattern(file_path, pattern):
                return rule.get('tool', 'aider')
        
        # Default
        return self.config.get('execution', {}).get('default_tool', 'aider')
    
    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if file matches pattern."""
        from fnmatch import fnmatch
        return fnmatch(file_path, pattern)


if __name__ == "__main__":
    # Test adapter
    logging.basicConfig(level=logging.INFO)
    
    config = {
        'tools': {
            'aider': {'model': 'gpt-4'}
        },
        'adapters': {
            'routing': [
                {'pattern': '*.py', 'tool': 'aider', 'priority': 10}
            ]
        },
        'execution': {
            'default_tool': 'aider'
        }
    }
    
    adapter = ToolAdapter(config)
    
    # Test routing
    tool = adapter.get_tool_for_file('test.py')
    print(f"Tool for test.py: {tool}")
