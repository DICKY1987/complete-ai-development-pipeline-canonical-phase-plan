"""
Parallel Pattern Detector
Detects when multiple tools are executed in parallel
"""
# DOC_ID: DOC-PAT-DETECTORS-PARALLEL-DETECTOR-642

from typing import List, Dict
from collections import defaultdict
from .base_detector import BaseDetector, DetectedPattern
from ..parsers.base_parser import ExecutionSession, ToolExecution


class ParallelDetector(BaseDetector):
    """Detects parallel tool execution patterns"""
    
    def get_detector_name(self) -> str:
        return "parallel"
    
    def detect_patterns(self, sessions: List[ExecutionSession]) -> List[DetectedPattern]:
        """
        Detect parallel execution patterns
        
        Algorithm:
        1. Group tool executions by parent_id
        2. If group size > 1, it's a parallel pattern
        3. Count frequency of each unique parallel pattern
        4. Calculate time savings (parallel vs sequential)
        """
        # Store patterns: {tool_sequence_key: [session_ids, durations, ...]}
        pattern_data: Dict[str, Dict] = defaultdict(lambda: {
            'sessions': [],
            'parallel_durations': [],
            'sequential_durations': []
        })
        
        for session in sessions:
            parallel_groups = self._identify_parallel_groups(session)
            
            for group in parallel_groups:
                # Create pattern key from sorted tool names
                tool_names = sorted([exec.tool_name for exec in group])
                pattern_key = '|'.join(tool_names)
                
                # Calculate durations
                parallel_duration = max(exec.duration_seconds for exec in group)
                sequential_duration = sum(exec.duration_seconds for exec in group)
                
                # Store data
                pattern_data[pattern_key]['sessions'].append(session.session_id)
                pattern_data[pattern_key]['parallel_durations'].append(parallel_duration)
                pattern_data[pattern_key]['sequential_durations'].append(sequential_duration)
        
        # Convert to DetectedPattern objects
        patterns = []
        for pattern_key, data in pattern_data.items():
            if len(data['sessions']) < 3:  # Minimum 3 occurrences
                continue
            
            tool_sequence = pattern_key.split('|')
            avg_parallel = sum(data['parallel_durations']) / len(data['parallel_durations'])
            avg_sequential = sum(data['sequential_durations']) / len(data['sequential_durations'])
            
            time_savings = self.calculate_time_savings(avg_parallel, avg_sequential)
            
            pattern = DetectedPattern(
                pattern_id=f"parallel_{pattern_key.replace('|', '_')}",
                pattern_type='parallel',
                frequency=len(data['sessions']),
                avg_duration_seconds=avg_parallel,
                time_savings_percent=time_savings * 100,
                tool_sequence=tool_sequence,
                example_sessions=data['sessions'][:5],  # First 5 examples
                metadata={
                    'avg_parallel_duration': avg_parallel,
                    'avg_sequential_duration': avg_sequential,
                    'speedup_factor': avg_sequential / avg_parallel if avg_parallel > 0 else 1.0
                }
            )
            patterns.append(pattern)
        
        # Sort by frequency (most common first)
        patterns.sort(key=lambda p: p.frequency, reverse=True)
        return patterns
    
    def _identify_parallel_groups(self, session: ExecutionSession) -> List[List[ToolExecution]]:
        """
        Identify groups of tool executions that ran in parallel
        
        Returns executions grouped by parent_id with >1 execution per group
        """
        groups: Dict[str, List[ToolExecution]] = defaultdict(list)
        
        for execution in session.executions:
            parent = execution.parent_id or "root"
            groups[parent].append(execution)
        
        # Filter for groups with >1 execution (parallel)
        parallel_groups = [
            group for group in groups.values() 
            if len(group) > 1
        ]
        
        return parallel_groups
