"""Tests for core data models."""
DOC_ID: DOC-TEST-TESTS-TEST-BASE-357

from datetime import datetime

import pytest
from coverage_analyzer.base import (
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


class TestCoverageLayer:
    """Tests for CoverageLayer enum."""

    def test_layer_values(self):
        assert CoverageLayer.STATIC_ANALYSIS.value == "0"
        assert CoverageLayer.SCA.value == "0.5"
        assert CoverageLayer.STRUCTURAL.value == "1"
        assert CoverageLayer.MUTATION.value == "2"
        assert CoverageLayer.PATH_COVERAGE.value == "3"
        assert CoverageLayer.OPERATIONAL.value == "4"


class TestStaticAnalysisMetrics:
    """Tests for StaticAnalysisMetrics dataclass."""

    def test_initialization(self):
        metrics = StaticAnalysisMetrics(
            code_quality_score=85.0,
            total_issues=10,
            issues_by_severity={"high": 2, "medium": 5, "low": 3},
            tool_name="prospector",
        )

        assert metrics.code_quality_score == 85.0
        assert metrics.total_issues == 10
        assert metrics.tool_name == "prospector"
        assert isinstance(metrics.timestamp, datetime)

    def test_default_values(self):
        metrics = StaticAnalysisMetrics(
            code_quality_score=90.0, total_issues=0, tool_name="test"
        )

        assert metrics.security_vulnerabilities == 0
        assert metrics.type_errors == 0
        assert metrics.maintainability_index == 0.0
        assert metrics.high_complexity_functions == []


class TestSCAMetrics:
    """Tests for SCAMetrics dataclass."""

    def test_initialization(self):
        metrics = SCAMetrics(
            total_dependencies=50, vulnerable_dependencies=3, tool_name="safety"
        )

        assert metrics.total_dependencies == 50
        assert metrics.vulnerable_dependencies == 3
        assert metrics.security_score == 100.0
        assert isinstance(metrics.timestamp, datetime)


class TestStructuralCoverageMetrics:
    """Tests for StructuralCoverageMetrics dataclass."""

    def test_initialization(self):
        metrics = StructuralCoverageMetrics(
            line_coverage_percent=85.5,
            branch_coverage_percent=80.0,
            function_coverage_percent=90.0,
            total_lines=100,
            covered_lines=85,
            total_branches=40,
            covered_branches=32,
            total_functions=10,
            covered_functions=9,
            tool_name="coverage.py",
        )

        assert metrics.line_coverage_percent == 85.5
        assert metrics.covered_lines == 85
        assert isinstance(metrics.timestamp, datetime)


class TestMutationMetrics:
    """Tests for MutationMetrics dataclass."""

    def test_initialization(self):
        metrics = MutationMetrics(
            total_mutants=50,
            killed_mutants=40,
            survived_mutants=8,
            timeout_mutants=2,
            mutation_score=80.0,
            tool_name="mutmut",
        )

        assert metrics.total_mutants == 50
        assert metrics.mutation_score == 80.0
        assert isinstance(metrics.timestamp, datetime)


class TestComplexityMetrics:
    """Tests for ComplexityMetrics dataclass."""

    def test_initialization(self):
        metrics = ComplexityMetrics(
            average_complexity=5.2,
            max_complexity=15,
            functions_above_threshold=2,
            tool_name="radon",
        )

        assert metrics.average_complexity == 5.2
        assert metrics.max_complexity == 15
        assert isinstance(metrics.timestamp, datetime)


class TestOperationalMetrics:
    """Tests for OperationalMetrics dataclass."""

    def test_initialization(self):
        metrics = OperationalMetrics(
            total_requests=100,
            failed_requests=5,
            success_rate=95.0,
            avg_response_time_ms=150.5,
            max_response_time_ms=500.0,
            requests_per_second=10.5,
            concurrent_users=10,
            test_duration="30s",
            performance_score=85.0,
            passed_validation=True,
            tool_name="locust",
        )

        assert metrics.total_requests == 100
        assert metrics.failed_requests == 5
        assert metrics.success_rate == 95.0
        assert metrics.passed_validation is True
        assert isinstance(metrics.timestamp, datetime)


class TestCoverageReport:
    """Tests for CoverageReport dataclass."""

    def test_initialization_empty(self):
        report = CoverageReport(target_path="/path/to/project", language="python")

        assert report.target_path == "/path/to/project"
        assert report.language == "python"
        assert report.overall_quality_score == 0.0
        assert report.layers_executed == []
        assert isinstance(report.timestamp, datetime)

    def test_quality_score_calculation_single_layer(self, sample_structural_metrics):
        report = CoverageReport(
            target_path="/test",
            language="python",
            structural_coverage=sample_structural_metrics,
        )

        # Structural coverage: (85.5 + 80.0) / 2 = 82.75
        assert 82.0 < report.overall_quality_score < 83.0

    def test_quality_score_calculation_multiple_layers(
        self, sample_static_metrics, sample_structural_metrics, sample_mutation_metrics
    ):
        report = CoverageReport(
            target_path="/test",
            language="python",
            static_analysis=sample_static_metrics,
            structural_coverage=sample_structural_metrics,
            mutation_testing=sample_mutation_metrics,
        )

        # Should calculate weighted average across all 3 layers
        assert 0 < report.overall_quality_score <= 100

    def test_quality_score_all_layers(self, sample_coverage_report):
        # With all 6 layers present
        assert 0 < sample_coverage_report.overall_quality_score <= 100


class TestAnalysisConfiguration:
    """Tests for AnalysisConfiguration dataclass."""

    def test_initialization_defaults(self):
        config = AnalysisConfiguration(
            target_path="/path/to/project", language="python"
        )

        assert config.target_path == "/path/to/project"
        assert config.language == "python"
        assert config.layers == ["0", "0.5", "1", "2", "3", "4"]
        assert config.min_line_coverage == 80.0
        assert config.fail_on_critical_security is True

    def test_custom_configuration(self):
        config = AnalysisConfiguration(
            target_path="/custom/path",
            language="powershell",
            layers=["1", "3"],
            min_line_coverage=90.0,
            fail_on_critical_security=False,
            output_format="html",
        )

        assert config.language == "powershell"
        assert config.layers == ["1", "3"]
        assert config.min_line_coverage == 90.0
        assert config.fail_on_critical_security is False
        assert config.output_format == "html"
