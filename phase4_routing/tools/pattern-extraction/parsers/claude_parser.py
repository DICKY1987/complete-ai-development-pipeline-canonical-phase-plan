"""
Claude Code Log Parser
Parses Claude Code debug logs and history.jsonl
"""
# DOC_ID: DOC-PAT-PARSERS-CLAUDE-PARSER-649

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from .base_parser import BaseParser, ToolExecution, ExecutionSession


class ClaudeParser(BaseParser):
    """Parser for Claude Code debug logs and history"""
    
    def get_parser_name(self) -> str:
        return "claude_code"
    
    def parse_logs(self, log_path: str) -> List[ExecutionSession]:
        """Parse Claude Code logs"""
        log_path = Path(log_path)
        sessions = []
        
        if log_path.is_file() and log_path.suffix == '.jsonl':
            # Parse history.jsonl
            sessions.extend(self._parse_history_jsonl(log_path))
        elif log_path.is_dir():
            # Parse all files in debug directory
            for file in log_path.glob("*.txt"):
                session = self._parse_debug_log(file)
                if session:
                    sessions.append(session)
            
            # Also check for history.jsonl
            history_file = log_path.parent / "history.jsonl"
            if history_file.exists():
                sessions.extend(self._parse_history_jsonl(history_file))
        
        return sessions
    
    def _parse_history_jsonl(self, file_path: Path) -> List[ExecutionSession]:
        """Parse Claude Code history.jsonl file"""
        sessions = []
        current_session_id = None
        current_executions = []
        session_start = None
        session_end = None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue
                    
                    try:
                        event = json.loads(line)
                        timestamp = datetime.fromisoformat(event.get('timestamp', '').replace('Z', '+00:00'))
                        
                        if session_start is None or timestamp < session_start:
                            session_start = timestamp
                        if session_end is None or timestamp > session_end:
                            session_end = timestamp
                        
                        # Extract tool calls from messages
                        if event.get('type') == 'assistant' and 'tool_use' in event.get('content', []):
                            for item in event['content']:
                                if item.get('type') == 'tool_use':
                                    execution = ToolExecution(
                                        tool_name=item.get('name', 'unknown'),
                                        start_time=timestamp,
                                        end_time=timestamp,
                                        duration_seconds=0.0,
                                        parent_id=event.get('parent_id'),
                                        execution_id=item.get('id', str(timestamp.timestamp())),
                                        success=True,
                                        metadata=item
                                    )
                                    current_executions.append(execution)
                    
                    except (json.JSONDecodeError, ValueError):
                        continue
            
            if current_executions:
                sessions.append(ExecutionSession(
                    session_id=file_path.stem,
                    start_time=session_start or datetime.now(),
                    end_time=session_end or datetime.now(),
                    executions=current_executions,
                    metadata={'source_file': str(file_path)}
                ))
        
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
        
        return sessions
    
    def _parse_debug_log(self, file_path: Path) -> ExecutionSession | None:
        """Parse a Claude Code debug log text file"""
        executions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Extract tool calls from debug logs
                # Look for patterns like "tool: view", "tool: edit", etc.
                import re
                tool_pattern = r'tool:\s*(\w+)'
                timestamp_pattern = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})'
                
                matches = re.finditer(tool_pattern, content)
                for match in matches:
                    tool_name = match.group(1)
                    
                    # Try to find nearby timestamp
                    search_start = max(0, match.start() - 200)
                    search_text = content[search_start:match.start()]
                    time_match = re.search(timestamp_pattern, search_text)
                    
                    timestamp = datetime.now()
                    if time_match:
                        try:
                            timestamp = datetime.fromisoformat(time_match.group(1))
                        except ValueError:
                            pass
                    
                    execution = ToolExecution(
                        tool_name=tool_name,
                        start_time=timestamp,
                        end_time=timestamp,
                        duration_seconds=0.0,
                        parent_id=None,
                        execution_id=f"{tool_name}_{timestamp.timestamp()}",
                        success=True
                    )
                    executions.append(execution)
            
            if not executions:
                return None
            
            return ExecutionSession(
                session_id=file_path.stem,
                start_time=min(e.start_time for e in executions),
                end_time=max(e.end_time for e in executions),
                executions=executions,
                metadata={'source_file': str(file_path)}
            )
        
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None
