"""Core types and data structures for pattern-driven error detection.

This module defines the foundational types used throughout the pattern
detection framework, following the principles of deterministic,
pattern-based bug detection.
"""
# DOC_ID: DOC-ERROR-PATTERNS-TYPES-055
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


class PatternCategory(str, Enum):
    """Categories of bug patterns that can be detected.
    
    Bugs cluster around patterns of incompleteness. Each category
    represents a class of issues that can be systematically detected.
    """
    BOUNDARY_VALUE = "boundary_value"
    STATE_TRANSITION = "state_transition"
    ERROR_PATH = "error_path"
    INTEGRATION_SEAM = "integration_seam"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    TEMPORAL = "temporal"
    INPUT_VALIDATION = "input_validation"
    CONCURRENCY = "concurrency"


class PatternSeverity(str, Enum):
    """Severity levels for pattern findings."""
    CRITICAL = "critical"  # Security, data loss, system crash
    MAJOR = "major"  # Functionality broken, significant UX impact
    MINOR = "minor"  # Minor functionality issues, edge cases
    INFO = "info"  # Suggestions, optimizations


@dataclass
class PatternFinding:
    """A single finding from pattern analysis.
    
    Attributes:
        pattern_category: The category of pattern this finding belongs to
        severity: How severe this finding is
        file_path: Path to the affected file
        line: Line number where the issue is located (if applicable)
        column: Column number (if applicable)
        code: Pattern code identifier (e.g., "BVA-001")
        message: Human-readable description of the finding
        suggested_fix: Recommended fix for the issue
        test_case: Test case to verify the fix
        context: Additional context about the finding
    """
    pattern_category: PatternCategory
    severity: PatternSeverity
    file_path: str
    line: Optional[int] = None
    column: Optional[int] = None
    code: str = ""
    message: str = ""
    suggested_fix: Optional[str] = None
    test_case: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PatternResult:
    """Result of running pattern analysis on a file or module.
    
    Attributes:
        file_path: Path that was analyzed
        patterns_checked: Which pattern categories were analyzed
        findings: List of pattern findings discovered
        summary: Summary statistics of the analysis
        duration_ms: Time taken to run analysis
    """
    file_path: str
    patterns_checked: List[PatternCategory] = field(default_factory=list)
    findings: List[PatternFinding] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    duration_ms: Optional[int] = None

    @property
    def has_critical(self) -> bool:
        """Check if there are any critical findings."""
        return any(f.severity == PatternSeverity.CRITICAL for f in self.findings)

    @property
    def findings_by_category(self) -> Dict[PatternCategory, List[PatternFinding]]:
        """Group findings by pattern category."""
        result: Dict[PatternCategory, List[PatternFinding]] = {}
        for finding in self.findings:
            if finding.pattern_category not in result:
                result[finding.pattern_category] = []
            result[finding.pattern_category].append(finding)
        return result

    @property
    def findings_by_severity(self) -> Dict[PatternSeverity, List[PatternFinding]]:
        """Group findings by severity."""
        result: Dict[PatternSeverity, List[PatternFinding]] = {}
        for finding in self.findings:
            if finding.severity not in result:
                result[finding.severity] = []
            result[finding.severity].append(finding)
        return result


# Boundary Value Analysis Types

@dataclass
class BoundaryTestCase:
    """A generated boundary test case.
    
    Attributes:
        parameter_name: Name of the parameter being tested
        parameter_type: Type of the parameter
        test_value: The boundary value to test
        test_category: Category of boundary test (min, max, zero, null, etc.)
        expected_behavior: What should happen with this input
    """
    parameter_name: str
    parameter_type: str
    test_value: Any
    test_category: str
    expected_behavior: str
    is_valid_input: bool = True


@dataclass 
class BoundarySpec:
    """Specification for boundary testing of a parameter.
    
    Contains the boundary values and edge cases for different types.
    """
    param_type: str
    boundaries: List[BoundaryTestCase] = field(default_factory=list)


# State Transition Types

@dataclass
class StateTransition:
    """Represents a state transition in the system.
    
    Attributes:
        from_state: Starting state
        to_state: Target state
        trigger: What causes this transition
        is_implemented: Whether this transition is handled in code
        is_valid: Whether this is a valid transition
    """
    from_state: str
    to_state: str
    trigger: str
    is_implemented: bool = False
    is_valid: bool = True
    guard_conditions: List[str] = field(default_factory=list)


@dataclass
class StateDiagram:
    """State diagram for analyzing state transitions.
    
    Attributes:
        name: Name of the state machine
        states: All valid states
        transitions: Implemented transitions
        initial_state: Starting state
        terminal_states: End states
    """
    name: str
    states: Set[str] = field(default_factory=set)
    transitions: List[StateTransition] = field(default_factory=list)
    initial_state: Optional[str] = None
    terminal_states: Set[str] = field(default_factory=set)

    def get_missing_transitions(self) -> List[StateTransition]:
        """Find state transitions that are possible but not implemented."""
        implemented = {(t.from_state, t.to_state) for t in self.transitions}
        missing = []
        for from_state in self.states:
            for to_state in self.states:
                if from_state != to_state and (from_state, to_state) not in implemented:
                    missing.append(StateTransition(
                        from_state=from_state,
                        to_state=to_state,
                        trigger="unknown",
                        is_implemented=False,
                    ))
        return missing


# Integration Seam Types

@dataclass
class IntegrationSeam:
    """An integration point that could be a failure source.
    
    Attributes:
        name: Name of the integration point
        seam_type: Type of integration (api, database, file, external_service)
        location: Where in code this integration exists
        checks: What failure handling has been verified
    """
    name: str
    seam_type: str  # "api", "database", "file", "external_service", "network"
    location: str
    checks: Dict[str, bool] = field(default_factory=dict)

    @property
    def missing_checks(self) -> List[str]:
        """Return list of missing failure handling checks."""
        required_checks = [
            "network_failure_handling",
            "timeout_handling",
            "retry_logic",
            "circuit_breaker",
            "data_validation",
            "version_mismatch_handling",
        ]
        return [check for check in required_checks if not self.checks.get(check, False)]


# Resource Pattern Types

@dataclass
class ResourcePattern:
    """Pattern for detecting resource management issues.
    
    Attributes:
        resource_type: Type of resource (file, connection, memory, thread)
        pattern_name: Name of the pattern being checked
        file_path: File where pattern was found
        line: Line number
        is_leak: Whether this represents a potential leak
    """
    resource_type: str
    pattern_name: str
    file_path: str
    line: int
    is_leak: bool
    context: str = ""


# Temporal Pattern Types

@dataclass
class TemporalPattern:
    """Pattern for time-based bug detection.
    
    Attributes:
        pattern_type: Type of temporal issue (timezone, dst, leap_year, etc.)
        file_path: File where pattern was found
        line: Line number
        issue_description: What temporal bug could occur
    """
    pattern_type: str
    file_path: str
    line: int
    issue_description: str
    affected_dates: List[str] = field(default_factory=list)


# Error Path Types

@dataclass
class ErrorPathCheck:
    """A check for error path coverage.
    
    Attributes:
        check_type: Type of error check
        function_name: Function being checked
        file_path: File path
        is_covered: Whether this error path is handled
        missing_handling: What error handling is missing
    """
    check_type: str  # "dependency_unavailable", "null_return", "timeout", "exception", "malformed_data", "concurrent_access"
    function_name: str
    file_path: str
    line: Optional[int] = None
    is_covered: bool = False
    missing_handling: Optional[str] = None


# Checklist Types

@dataclass
class ChecklistItem:
    """A single item in a validation checklist.
    
    Attributes:
        category: Checklist category (input_validation, error_handling, etc.)
        item: The check item description
        is_checked: Whether this item passes
        evidence: What was found (or not found)
    """
    category: str
    item: str
    is_checked: bool = False
    evidence: Optional[str] = None


@dataclass
class ModuleChecklist:
    """Complete validation checklist for a module.
    
    Contains all checklist items organized by category, following
    the reusable testing patterns approach.
    """
    module_path: str
    items: List[ChecklistItem] = field(default_factory=list)

    def get_by_category(self, category: str) -> List[ChecklistItem]:
        """Get all items for a specific category."""
        return [item for item in self.items if item.category == category]

    @property
    def passing_count(self) -> int:
        """Count of passing items."""
        return sum(1 for item in self.items if item.is_checked)

    @property
    def total_count(self) -> int:
        """Total count of items."""
        return len(self.items)

    @property
    def pass_rate(self) -> float:
        """Percentage of items passing."""
        if self.total_count == 0:
            return 100.0
        return (self.passing_count / self.total_count) * 100
