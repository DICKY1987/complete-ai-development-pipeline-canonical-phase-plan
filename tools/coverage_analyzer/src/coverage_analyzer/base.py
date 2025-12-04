"""
Core data models for the 5-layer test coverage framework.

This module defines the fundamental data structures used across all layers:
- Layer 0: Static Analysis (SAST)
- Layer 0.5: Software Composition Analysis (SCA)
- Layer 1: Structural Coverage
- Layer 2: Mutation Testing
- Layer 3: Path Coverage
- Layer 4: Operational Validation
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class CoverageLayer(Enum):
    """Enumeration of coverage analysis layers."""

    STATIC_ANALYSIS = "0"
    SCA = "0.5"
    STRUCTURAL = "1"
    MUTATION = "2"
    PATH_COVERAGE = "3"
    OPERATIONAL = "4"


class Severity(Enum):
    """Issue severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class StaticAnalysisMetrics:
    """Layer 0 metrics - Static Analysis & Security Testing (SAST)."""

    code_quality_score: float  # 0-100
    total_issues: int
    issues_by_severity: Dict[str, int] = field(default_factory=dict)
    security_vulnerabilities: int = 0
    type_errors: int = 0
    maintainability_index: float = 0.0
    high_complexity_functions: List[str] = field(default_factory=list)
    tool_name: str = ""
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class SCAMetrics:
    """Layer 0.5 metrics - Software Composition Analysis."""

    total_dependencies: int
    vulnerable_dependencies: int
    vulnerabilities_by_severity: Dict[str, int] = field(default_factory=dict)
    cve_details: List[Dict[str, Any]] = field(default_factory=list)
    outdated_packages: int = 0
    license_issues: int = 0
    security_score: float = 100.0  # 0-100
    tool_name: str = ""
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class StructuralCoverageMetrics:
    """Layer 1 metrics - Structural Coverage (Statement + Branch)."""

    line_coverage_percent: float
    branch_coverage_percent: float
    function_coverage_percent: float
    total_lines: int
    covered_lines: int
    total_branches: int
    covered_branches: int
    total_functions: int
    covered_functions: int
    uncovered_lines: List[int] = field(default_factory=list)
    tool_name: str = ""
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class MutationMetrics:
    """Layer 2 metrics - Mutation Testing."""

    total_mutants: int
    killed_mutants: int
    survived_mutants: int
    timeout_mutants: int
    mutation_score: float  # 0-100
    surviving_mutant_locations: List[str] = field(default_factory=list)
    tool_name: str = ""
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class ComplexityMetrics:
    """Layer 3 metrics - Cyclomatic Complexity & Path Coverage."""

    average_complexity: float
    max_complexity: int
    functions_above_threshold: int  # CC > 10
    complex_function_details: List[Dict[str, Any]] = field(default_factory=list)
    total_independent_paths: int = 0
    tested_paths: int = 0
    path_coverage_percent: float = 0.0
    tool_name: str = ""
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class OperationalMetrics:
    """Layer 4 metrics - Operational Validation (Load Testing & Performance)."""

    total_requests: int
    failed_requests: int
    success_rate: float  # Percentage
    avg_response_time_ms: float
    max_response_time_ms: float
    requests_per_second: float
    concurrent_users: int
    test_duration: str  # e.g., "30s", "1m"
    performance_score: float  # 0-100
    passed_validation: bool
    tool_name: str = ""
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class CoverageReport:
    """Complete 5-layer coverage analysis report."""

    target_path: str
    language: str  # "python" or "powershell"

    # Layer metrics
    static_analysis: Optional[StaticAnalysisMetrics] = None
    sca: Optional[SCAMetrics] = None
    structural_coverage: Optional[StructuralCoverageMetrics] = None
    mutation_testing: Optional[MutationMetrics] = None
    complexity: Optional[ComplexityMetrics] = None
    operational_validation: Optional[OperationalMetrics] = None

    # Overall metrics
    overall_quality_score: float = 0.0  # 0-100 weighted average
    layers_executed: List[str] = field(default_factory=list)
    execution_duration_seconds: float = 0.0
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        self.overall_quality_score = self._calculate_quality_score()

    def _calculate_quality_score(self) -> float:
        """Calculate weighted quality score across all executed layers."""
        weights = {
            "static_analysis": 0.15,
            "sca": 0.10,
            "structural_coverage": 0.25,
            "mutation_testing": 0.20,
            "complexity": 0.15,
            "operational_validation": 0.15,
        }

        scores = {}

        if self.static_analysis:
            scores["static_analysis"] = self.static_analysis.code_quality_score

        if self.sca:
            scores["sca"] = self.sca.security_score

        if self.structural_coverage:
            scores["structural_coverage"] = (
                self.structural_coverage.line_coverage_percent * 0.5
                + self.structural_coverage.branch_coverage_percent * 0.5
            )

        if self.mutation_testing:
            scores["mutation_testing"] = self.mutation_testing.mutation_score

        if self.complexity:
            # Lower complexity is better; invert the score
            avg_cc = self.complexity.average_complexity
            complexity_score = max(0, 100 - (avg_cc - 1) * 10)
            scores["complexity"] = min(100, complexity_score)

        if self.operational_validation:
            # Use performance score directly (already 0-100)
            scores["operational_validation"] = (
                self.operational_validation.performance_score
            )

        if not scores:
            return 0.0

        # Calculate weighted average
        total_weight = sum(weights[layer] for layer in scores.keys())
        weighted_sum = sum(scores[layer] * weights[layer] for layer in scores.keys())

        return weighted_sum / total_weight if total_weight > 0 else 0.0


@dataclass
class AnalysisConfiguration:
    """Configuration for coverage analysis execution."""

    target_path: str
    language: str  # "python" or "powershell"
    layers: List[str] = field(default_factory=lambda: ["0", "0.5", "1", "2", "3", "4"])

    # Layer-specific configs
    static_analysis_tools: List[str] = field(default_factory=list)
    sca_tools: List[str] = field(default_factory=list)
    structural_tools: List[str] = field(default_factory=list)
    mutation_tools: List[str] = field(default_factory=list)
    complexity_tools: List[str] = field(default_factory=list)
    operational_tools: List[str] = field(default_factory=list)

    # Quality gate thresholds
    min_line_coverage: float = 80.0
    min_branch_coverage: float = 70.0
    min_mutation_score: float = 70.0
    max_complexity_threshold: int = 10
    fail_on_critical_security: bool = True
    fail_on_critical_cve: bool = True

    # Output settings
    output_format: str = "json"  # json, html, terminal
    output_path: Optional[str] = None
    verbose: bool = False
