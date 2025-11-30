"""
Base Parser Interface
All log parsers implement this interface
"""
DOC_ID: DOC-PAT-PARSERS-BASE-PARSER-648

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ToolExecution:
    """Single tool execution event"""
    tool_name: str
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    parent_id: str | None
    execution_id: str
    success: bool
    error_message: str | None = None
    metadata: Dict[str, Any] | None = None


@dataclass
class ExecutionSession:
    """Collection of tool executions in a session"""
    session_id: str
    start_time: datetime
    end_time: datetime
    executions: List[ToolExecution]
    metadata: Dict[str, Any] | None = None


class BaseParser(ABC):
    """Base class for all log parsers"""
    
    @abstractmethod
    def parse_logs(self, log_path: str) -> List[ExecutionSession]:
        """
        Parse logs from given path and return execution sessions
        
        Args:
            log_path: Path to log file or directory
            
        Returns:
            List of execution sessions extracted from logs
        """
        pass
    
    @abstractmethod
    def get_parser_name(self) -> str:
        """Return name of this parser (e.g., 'claude_code', 'copilot')"""
        pass
    
    def extract_tool_sequences(self, session: ExecutionSession) -> List[List[str]]:
        """
        Extract sequences of tool calls from a session
        
        Returns:
            List of tool sequences (e.g., [['grep', 'view', 'edit'], ['create', 'powershell']])
        """
        sequences = []
        current_sequence = []
        
        for execution in sorted(session.executions, key=lambda e: e.start_time):
            if current_sequence and execution.parent_id is None:
                # New top-level execution, start new sequence
                if current_sequence:
                    sequences.append(current_sequence)
                current_sequence = [execution.tool_name]
            else:
                current_sequence.append(execution.tool_name)
        
        if current_sequence:
            sequences.append(current_sequence)
        
        return sequences
    
    def identify_parallel_executions(self, session: ExecutionSession) -> List[List[ToolExecution]]:
        """
        Identify groups of tool executions that ran in parallel
        
        Returns:
            List of parallel execution groups
        """
        # Group by parent_id
        groups: Dict[str, List[ToolExecution]] = {}
        
        for execution in session.executions:
            parent = execution.parent_id or "root"
            if parent not in groups:
                groups[parent] = []
            groups[parent].append(execution)
        
        # Filter for groups with >1 execution (parallel)
        parallel_groups = [
            group for group in groups.values() 
            if len(group) > 1
        ]
        
        return parallel_groups
