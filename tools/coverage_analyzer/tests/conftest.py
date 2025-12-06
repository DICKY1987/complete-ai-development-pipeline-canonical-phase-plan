"""
Test fixtures for coverage analyzer tests.

Provides shared fixtures for mocking tool outputs, sample projects,
and test configurations.
"""
DOC_ID: DOC-TEST-TESTS-CONFTEST-356

from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pytest
from coverage_analyzer.base import (
    AnalysisConfiguration,
    ComplexityMetrics,
    CoverageReport,
    MutationMetrics,
    OperationalMetrics,
    SCAMetrics,
    StaticAnalysisMetrics,
    StructuralCoverageMetrics,
)


@pytest.fixture
def sample_python_project(tmp_path: Path) -> Path:
    """Create a minimal Python project for testing."""
    project_dir = tmp_path / "sample_project"
    project_dir.mkdir()

    # Create a simple module
    module_file = project_dir / "calculator.py"
    module_file.write_text(
        """
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
"""
    )

    # Create a test file
    test_file = project_dir / "test_calculator.py"
    test_file.write_text(
        """
from calculator import add, subtract, divide
import pytest

def test_add():
    assert add(2, 3) == 5

def test_subtract():
    assert subtract(5, 3) == 2

def test_divide():
    assert divide(10, 2) == 5

def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(10, 0)
"""
    )

    return project_dir


@pytest.fixture
def mock_coverage_config(tmp_path: Path) -> AnalysisConfiguration:
    """Create a test configuration."""
    return AnalysisConfiguration(
        target_path=str(tmp_path),
        language="python",
        layers=["1"],  # Just structural coverage for basic tests
        min_line_coverage=80.0,
        output_format="json",
        verbose=False,
    )


@pytest.fixture
def mock_static_analysis_output() -> Dict[str, Any]:
    """Mock Prospector JSON output."""
    return {
        "summary": {
            "message_count": 5,
            "error_count": 0,
            "warning_count": 3,
            "info_count": 2,
        },
        "messages": [
            {
                "source": "pylint",
                "code": "C0111",
                "message": "Missing docstring",
                "location": {"path": "module.py", "line": 1},
            }
        ],
    }


@pytest.fixture
def mock_bandit_output() -> Dict[str, Any]:
    """Mock Bandit security scan output."""
    return {
        "results": [
            {
                "issue_severity": "HIGH",
                "issue_confidence": "HIGH",
                "issue_text": "Possible SQL injection",
                "line_number": 42,
                "filename": "database.py",
            }
        ],
        "metrics": {"SEVERITY.HIGH": 1, "SEVERITY.MEDIUM": 2, "SEVERITY.LOW": 3},
    }


@pytest.fixture
def mock_safety_output() -> str:
    """Mock Safety CLI output."""
    return """
+-------------------------------------------------+
| Safety Report                                   |
+-------------------------------------------------+
| package: requests                               |
| installed: 2.25.0                               |
| affected: <2.31.0                               |
| ID: 51668                                       |
+-------------------------------------------------+
"""


@pytest.fixture
def mock_coverage_py_output() -> Dict[str, Any]:
    """Mock coverage.py JSON output."""
    return {
        "meta": {"version": "7.0.0"},
        "files": {
            "module.py": {
                "summary": {
                    "covered_lines": 45,
                    "num_statements": 50,
                    "percent_covered": 90.0,
                    "missing_lines": 5,
                    "excluded_lines": 0,
                }
            }
        },
        "totals": {"covered_lines": 45, "num_statements": 50, "percent_covered": 90.0},
    }


@pytest.fixture
def mock_mutmut_output() -> str:
    """Mock mutmut CLI output."""
    return """
- Total mutants: 50
- Killed: 40
- Survived: 8
- Timeout: 2
- Mutation score: 80.0%
"""


@pytest.fixture
def sample_static_metrics() -> StaticAnalysisMetrics:
    """Create sample static analysis metrics."""
    return StaticAnalysisMetrics(
        code_quality_score=85.0,
        total_issues=10,
        issues_by_severity={"high": 1, "medium": 3, "low": 6},
        security_vulnerabilities=1,
        type_errors=2,
        maintainability_index=75.0,
        high_complexity_functions=["complex_function"],
        tool_name="prospector",
    )


@pytest.fixture
def sample_sca_metrics() -> SCAMetrics:
    """Create sample SCA metrics."""
    return SCAMetrics(
        total_dependencies=25,
        vulnerable_dependencies=2,
        vulnerabilities_by_severity={"high": 1, "medium": 1},
        cve_details=[
            {"cve": "CVE-2023-12345", "severity": "high", "package": "requests"}
        ],
        outdated_packages=5,
        license_issues=0,
        security_score=92.0,
        tool_name="safety",
    )


@pytest.fixture
def sample_structural_metrics() -> StructuralCoverageMetrics:
    """Create sample structural coverage metrics."""
    return StructuralCoverageMetrics(
        line_coverage_percent=85.5,
        branch_coverage_percent=80.0,
        function_coverage_percent=90.0,
        total_lines=100,
        covered_lines=85,
        total_branches=40,
        covered_branches=32,
        total_functions=10,
        covered_functions=9,
        uncovered_lines=[15, 27, 38],
        tool_name="coverage.py",
    )


@pytest.fixture
def sample_mutation_metrics() -> MutationMetrics:
    """Create sample mutation testing metrics."""
    return MutationMetrics(
        total_mutants=50,
        killed_mutants=40,
        survived_mutants=8,
        timeout_mutants=2,
        mutation_score=80.0,
        surviving_mutant_locations=["module.py:42", "module.py:67"],
        tool_name="mutmut",
    )


@pytest.fixture
def sample_complexity_metrics() -> ComplexityMetrics:
    """Create sample complexity metrics."""
    return ComplexityMetrics(
        average_complexity=5.2,
        max_complexity=15,
        functions_above_threshold=2,
        complex_function_details=[
            {"name": "complex_func", "complexity": 15, "file": "module.py"}
        ],
        total_independent_paths=50,
        tested_paths=45,
        path_coverage_percent=90.0,
        tool_name="radon",
    )


@pytest.fixture
def sample_operational_metrics() -> OperationalMetrics:
    """Create sample operational validation metrics."""
    return OperationalMetrics(
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


@pytest.fixture
def sample_coverage_report(
    sample_static_metrics,
    sample_sca_metrics,
    sample_structural_metrics,
    sample_mutation_metrics,
    sample_complexity_metrics,
    sample_operational_metrics,
) -> CoverageReport:
    """Create a complete sample coverage report."""
    return CoverageReport(
        target_path="/path/to/project",
        language="python",
        static_analysis=sample_static_metrics,
        sca=sample_sca_metrics,
        structural_coverage=sample_structural_metrics,
        mutation_testing=sample_mutation_metrics,
        complexity=sample_complexity_metrics,
        operational_validation=sample_operational_metrics,
        layers_executed=["0", "0.5", "1", "2", "3", "4"],
        execution_duration_seconds=245.7,
    )
