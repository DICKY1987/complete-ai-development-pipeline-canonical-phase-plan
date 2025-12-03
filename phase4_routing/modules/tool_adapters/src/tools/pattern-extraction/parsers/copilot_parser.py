"""
GitHub Copilot CLI Log Parser
Parses session-state JSONL files from ~/.copilot/session-state/
"""
# DOC_ID: DOC-PAT-PARSERS-COPILOT-PARSER-650

import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from .base_parser import BaseParser, ToolExecution, ExecutionSession


class CopilotParser(BaseParser):
    """Parser for GitHub Copilot CLI session logs"""
    
    def get_parser_name(self) -> str:
        return "copilot"
    
    def parse_logs(self, log_path: str) -> List[ExecutionSession]:
        """
        Parse Copilot session-state JSONL files
        
        Format:
        {"type":"tool_call","tool":"view","timestamp":"2025-11-23T...","..."}
        {"type":"tool_result","tool":"view","duration_ms":123,"..."}
        """
        log_dir = Path(log_path)
        sessions = []
        
        if log_dir.is_file():
            session = self._parse_session_file(log_dir)
            if session:
                sessions.append(session)
        else:
            # Parse all JSONL files in directory
            for jsonl_file in log_dir.glob("*.jsonl"):
                session = self._parse_session_file(jsonl_file)
                if session:
                    sessions.append(session)
        
        return sessions
    
    def _parse_session_file(self, file_path: Path) -> ExecutionSession | None:
        """Parse a single session JSONL file"""
        executions = []
        session_start = None
        session_end = None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_no, line in enumerate(f, 1):
                    if not line.strip():
                        continue
                    
                    try:
                        event = json.loads(line)
                        
                        # Track session boundaries
                        timestamp = self._parse_timestamp(event.get('timestamp', ''))
                        if timestamp:
                            if session_start is None or timestamp < session_start:
                                session_start = timestamp
                            if session_end is None or timestamp > session_end:
                                session_end = timestamp
                        
                        # Extract tool executions
                        if event.get('type') == 'tool_result':
                            execution = self._parse_tool_execution(event)
                            if execution:
                                executions.append(execution)
                    
                    except json.JSONDecodeError:
                        # Skip malformed lines
                        continue
            
            if not executions:
                return None
            
            return ExecutionSession(
                session_id=file_path.stem,
                start_time=session_start or datetime.now(),
                end_time=session_end or datetime.now(),
                executions=executions,
                metadata={'source_file': str(file_path)}
            )
        
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None
    
    def _parse_tool_execution(self, event: Dict[str, Any]) -> ToolExecution | None:
        """Parse a tool execution from tool_result event"""
        tool_name = event.get('tool', 'unknown')
        duration_ms = event.get('duration_ms', 0)
        timestamp = self._parse_timestamp(event.get('timestamp', ''))
        
        if not timestamp:
            return None
        
        # Calculate start/end times
        duration_seconds = duration_ms / 1000.0
        end_time = timestamp
        start_time = datetime.fromtimestamp(end_time.timestamp() - duration_seconds)
        
        return ToolExecution(
            tool_name=tool_name,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration_seconds,
            parent_id=event.get('parent_id'),
            execution_id=event.get('execution_id', f"{tool_name}_{timestamp.timestamp()}"),
            success=event.get('exit_code', 0) == 0,
            error_message=event.get('error'),
            metadata=event
        )
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime | None:
        """Parse ISO 8601 timestamp"""
        if not timestamp_str:
            return None
        
        try:
            # Handle various ISO formats
            # 2025-11-23T22:08:41.044Z
            # 2025-11-23T22:08:41+00:00
            timestamp_str = timestamp_str.replace('Z', '+00:00')
            return datetime.fromisoformat(timestamp_str)
        except ValueError:
            return None
