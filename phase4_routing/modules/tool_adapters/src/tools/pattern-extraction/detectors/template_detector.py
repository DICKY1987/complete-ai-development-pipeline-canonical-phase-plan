"""
Template Convergence Detector
Detects when patterns converge to reusable templates
"""
# DOC_ID: DOC-PAT-DETECTORS-TEMPLATE-DETECTOR-644

from typing import List, Dict
from collections import defaultdict
from .base_detector import BaseDetector, DetectedPattern
from ..parsers.base_parser import ExecutionSession


class TemplateDetector(BaseDetector):
    """Detects template convergence patterns"""

    def get_detector_name(self) -> str:
        return "template"

    def detect_patterns(self, sessions: List[ExecutionSession]) -> List[DetectedPattern]:
        """
        Detect template convergence patterns

        Algorithm:
        1. Group sessions by similar tool sequences
        2. If variation < 5%, extract as template
        3. Measure time improvement across uses
        """
        # Group by tool sequence signature
        sequence_groups: Dict[str, List[ExecutionSession]] = defaultdict(list)

        for session in sessions:
            tool_sequence = tuple(sorted([e.tool_name for e in session.executions]))
            signature = '|'.join(tool_sequence)
            sequence_groups[signature].append(session)

        # Find converging templates
        patterns = []
        for signature, group_sessions in sequence_groups.items():
            if len(group_sessions) < 10:  # Need at least 10 uses to detect convergence
                continue

            # Sort by time
            sorted_sessions = sorted(group_sessions, key=lambda s: s.start_time)

            # Calculate time trend (are executions getting faster?)
            durations = [(s.end_time - s.start_time).total_seconds() for s in sorted_sessions]

            # Check for convergence (last 5 are similar)
            if len(durations) >= 10:
                recent_durations = durations[-5:]
                early_durations = durations[:5]

                avg_recent = sum(recent_durations) / len(recent_durations)
                avg_early = sum(early_durations) / len(early_durations)

                # If recent executions are faster, this is a converged template
                if avg_recent < avg_early * 0.7:  # 30% or more improvement
                    time_savings = self.calculate_time_savings(avg_recent, avg_early)

                    tool_sequence = signature.split('|')

                    pattern = DetectedPattern(
                        pattern_id=f"template_{'_'.join(tool_sequence)}",
                        pattern_type='template',
                        frequency=len(group_sessions),
                        avg_duration_seconds=avg_recent,
                        time_savings_percent=time_savings * 100,
                        tool_sequence=tool_sequence,
                        example_sessions=[s.session_id for s in sorted_sessions[-5:]],
                        metadata={
                            'early_avg': avg_early,
                            'recent_avg': avg_recent,
                            'improvement': time_savings,
                            'uses_to_converge': len(group_sessions) // 2
                        }
                    )
                    patterns.append(pattern)

        # Sort by time savings
        patterns.sort(key=lambda p: p.time_savings_percent or 0, reverse=True)
        return patterns
