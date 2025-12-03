"""
Sequential Pattern Detector
Detects common sequential workflow patterns
"""
# DOC_ID: DOC-PAT-DETECTORS-SEQUENTIAL-DETECTOR-643

from typing import List, Dict
from collections import defaultdict, Counter
from .base_detector import BaseDetector, DetectedPattern
from ..parsers.base_parser import ExecutionSession


class SequentialDetector(BaseDetector):
    """Detects sequential workflow patterns"""
    
    def get_detector_name(self) -> str:
        return "sequential"
    
    def detect_patterns(self, sessions: List[ExecutionSession]) -> List[DetectedPattern]:
        """
        Detect sequential workflow patterns
        
        Algorithm:
        1. Extract tool sequences from each session
        2. Find common subsequences (n-grams)
        3. Count frequency of each sequence
        4. Calculate average duration
        """
        # Count sequence frequencies
        sequence_data: Dict[str, Dict] = defaultdict(lambda: {
            'sessions': [],
            'durations': []
        })
        
        for session in sessions:
            # Get tool sequence for this session
            tool_sequence = [e.tool_name for e in sorted(session.executions, key=lambda x: x.start_time)]
            
            # Extract n-grams (sequences of 2-5 tools)
            for n in range(2, 6):
                for i in range(len(tool_sequence) - n + 1):
                    ngram = tuple(tool_sequence[i:i+n])
                    pattern_key = ' → '.join(ngram)
                    
                    # Calculate duration for this sequence
                    executions_in_sequence = sorted(session.executions, key=lambda x: x.start_time)[i:i+n]
                    duration = sum(e.duration_seconds for e in executions_in_sequence)
                    
                    sequence_data[pattern_key]['sessions'].append(session.session_id)
                    sequence_data[pattern_key]['durations'].append(duration)
        
        # Convert to DetectedPattern objects
        patterns = []
        for pattern_key, data in sequence_data.items():
            if len(data['sessions']) < 5:  # Minimum 5 occurrences
                continue
            
            tool_sequence = pattern_key.split(' → ')
            avg_duration = sum(data['durations']) / len(data['durations']) if data['durations'] else 0.0
            
            pattern = DetectedPattern(
                pattern_id=f"sequential_{'_'.join(tool_sequence)}",
                pattern_type='sequential',
                frequency=len(data['sessions']),
                avg_duration_seconds=avg_duration,
                time_savings_percent=None,  # Sequential doesn't have inherent time savings
                tool_sequence=tool_sequence,
                example_sessions=data['sessions'][:5],
                metadata={
                    'sequence_length': len(tool_sequence),
                    'avg_duration': avg_duration
                }
            )
            patterns.append(pattern)
        
        # Sort by frequency
        patterns.sort(key=lambda p: p.frequency, reverse=True)
        return patterns
