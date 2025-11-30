"""Pattern-driven error detection framework.

This module provides systematic pattern-based bug detection to address
the "80/20 problem" - finding edge cases, integration points, and
emergent behaviors that hide in the final 20% of development.

Pattern Categories:
- Boundary Value Analysis: Systematic input boundary testing
- State Transition Gap: Missing state transition detection
- Error Path Coverage: Systematic error handling validation
- Integration Seam Analysis: Integration point failure detection
- Resource Exhaustion: Resource leak pattern detection
- Temporal Bug Patterns: Time-based bug detection

Usage:
    from error.patterns import PatternAnalyzer, PatternCategory
    
    analyzer = PatternAnalyzer()
    results = analyzer.analyze_module("path/to/module.py")
"""
DOC_ID: DOC-ERROR-PATTERNS-INIT-056

from .types import (
    PatternCategory,
    PatternSeverity,
    PatternFinding,
    PatternResult,
    BoundaryTestCase,
    StateTransition,
    IntegrationSeam,
)
from .pattern_analyzer import PatternAnalyzer

__all__ = [
    "PatternCategory",
    "PatternSeverity",
    "PatternFinding",
    "PatternResult",
    "BoundaryTestCase",
    "StateTransition",
    "IntegrationSeam",
    "PatternAnalyzer",
]
