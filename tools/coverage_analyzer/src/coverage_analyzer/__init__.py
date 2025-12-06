"""
Coverage Analyzer - 5-Layer Progressive Test Coverage Framework

This module provides comprehensive test coverage analysis across 5 layers:

Pre-Execution (Shift-Left Security):
- Layer 0: Static Analysis (SAST) - Code quality & security
- Layer 0.5: Software Composition Analysis (SCA) - Dependency vulnerabilities

Execution (Dynamic Testing):
- Layer 1: Structural Coverage - What code was executed
- Layer 2: Mutation Testing - Whether tests verify correctness
- Layer 3: Path Coverage - All logical paths exercised

Post-Execution (Production Readiness):
- Layer 4: Operational Validation - System-level NFR testing

Usage:
    from coverage_analyzer import CoverageAnalyzer, AnalysisConfiguration

    config = AnalysisConfiguration(
        target_path="src/myproject",
        language="python",
        layers=["0", "1", "3"]
    )

    analyzer = CoverageAnalyzer(config)
    report = analyzer.analyze()
    print(f"Overall quality score: {report.overall_quality_score}")
"""
DOC_ID: DOC-SCRIPT-COVERAGE-ANALYZER-INIT-796

__version__ = "0.1.0"

from .adapters.base_adapter import (
    BaseAdapter,
    ToolExecutionError,
    ToolNotAvailableError,
)
from .base import (
    AnalysisConfiguration,
    ComplexityMetrics,
    CoverageLayer,
    CoverageReport,
    MutationMetrics,
    OperationalMetrics,
    SCAMetrics,
    Severity,
    StaticAnalysisMetrics,
    StructuralCoverageMetrics,
)
from .registry import AnalyzerRegistry, get_registry

__all__ = [
    # Data models
    "CoverageLayer",
    "Severity",
    "StaticAnalysisMetrics",
    "SCAMetrics",
    "StructuralCoverageMetrics",
    "MutationMetrics",
    "ComplexityMetrics",
    "OperationalMetrics",
    "CoverageReport",
    "AnalysisConfiguration",
    # Registry
    "AnalyzerRegistry",
    "get_registry",
    # Base classes
    "BaseAdapter",
    "ToolExecutionError",
    "ToolNotAvailableError",
]
