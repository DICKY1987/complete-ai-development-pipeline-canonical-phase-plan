"""
Base Detector Interface
All pattern detectors implement this interface
"""
DOC_ID: DOC-PAT-DETECTORS-BASE-DETECTOR-641

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass
from ..parsers.base_parser import ExecutionSession, ToolExecution


@dataclass
class DetectedPattern:
    """A detected execution pattern"""
    pattern_id: str
    pattern_type: str  # 'parallel', 'sequential', 'template'
    frequency: int  # How many times this pattern appeared
    avg_duration_seconds: float
    time_savings_percent: float | None
    tool_sequence: List[str]
    example_sessions: List[str]  # Session IDs where this pattern was found
    metadata: Dict[str, Any] | None = None


class BaseDetector(ABC):
    """Base class for all pattern detectors"""
    
    @abstractmethod
    def detect_patterns(self, sessions: List[ExecutionSession]) -> List[DetectedPattern]:
        """
        Detect patterns from execution sessions
        
        Args:
            sessions: List of execution sessions from log parsers
            
        Returns:
            List of detected patterns
        """
        pass
    
    @abstractmethod
    def get_detector_name(self) -> str:
        """Return name of this detector"""
        pass
    
    def calculate_time_savings(
        self, 
        parallel_duration: float, 
        sequential_duration: float
    ) -> float:
        """
        Calculate time savings percentage
        
        Args:
            parallel_duration: Actual duration with parallelism
            sequential_duration: Estimated duration if sequential
            
        Returns:
            Time savings as percentage (e.g., 0.60 for 60% savings)
        """
        if sequential_duration == 0:
            return 0.0
        
        savings = (sequential_duration - parallel_duration) / sequential_duration
        return max(0.0, min(1.0, savings))  # Clamp between 0 and 1
