"""Tests for the main pattern analyzer."""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to Python path for imports
_test_file = Path(__file__).resolve()
_repo_root = _test_file.parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

import tempfile

import pytest
from error.patterns import (
    PatternAnalyzer,
    PatternCategory,
    PatternFinding,
    PatternResult,
    PatternSeverity,
)
from error.patterns.pattern_analyzer import (
    DEFAULT_CHECKLIST,
    analyze_module,
    generate_gap_report,
)


class TestPatternAnalyzer:
    """Test the main PatternAnalyzer class."""

    # DOC_ID: DOC-TEST-PATTERN-TESTS-TEST-PATTERN-ANALYZER-132

    def test_init_default_categories(self):
        """Initialize with default categories."""
        analyzer = PatternAnalyzer()

        assert len(analyzer._categories) > 0
        assert PatternCategory.BOUNDARY_VALUE in analyzer._categories
        assert PatternCategory.ERROR_PATH in analyzer._categories

    def test_init_custom_categories(self):
        """Initialize with custom categories."""
        analyzer = PatternAnalyzer(categories=[PatternCategory.BOUNDARY_VALUE])

        assert len(analyzer._categories) == 1
        assert PatternCategory.BOUNDARY_VALUE in analyzer._categories

    def test_init_severity_threshold(self):
        """Initialize with severity threshold."""
        analyzer = PatternAnalyzer(severity_threshold=PatternSeverity.MAJOR)

        assert analyzer._severity_threshold == PatternSeverity.MAJOR


class TestAnalyzeFile:
    """Test file analysis."""

    def test_analyze_file_returns_result(self):
        """Analyze file returns PatternResult."""
        code = """
def process(x):
    return x * 2
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()

            analyzer = PatternAnalyzer()
            result = analyzer.analyze_file(Path(f.name))

            assert isinstance(result, PatternResult)
            assert result.file_path == f.name
            assert result.duration_ms is not None

    def test_analyze_file_with_specific_categories(self):
        """Analyze file with specific categories."""
        code = """
def process(x):
    return x * 2
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()

            analyzer = PatternAnalyzer()
            result = analyzer.analyze_file(
                Path(f.name), categories=[PatternCategory.BOUNDARY_VALUE]
            )

            assert PatternCategory.BOUNDARY_VALUE in result.patterns_checked
            assert len(result.patterns_checked) == 1

    def test_analyze_file_filters_by_severity(self):
        """Findings are filtered by severity threshold."""
        code = """
def process(x):
    return x * 2
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()

            # Analyzer with CRITICAL threshold should have fewer findings
            analyzer_critical = PatternAnalyzer(
                severity_threshold=PatternSeverity.CRITICAL
            )
            result_critical = analyzer_critical.analyze_file(Path(f.name))

            analyzer_info = PatternAnalyzer(severity_threshold=PatternSeverity.INFO)
            result_info = analyzer_info.analyze_file(Path(f.name))

            # Critical should have <= findings than INFO
            assert len(result_critical.findings) <= len(result_info.findings)


class TestPatternResult:
    """Test PatternResult functionality."""

    def test_has_critical_true(self):
        """has_critical returns True when critical findings exist."""
        result = PatternResult(
            file_path="test.py",
            findings=[
                PatternFinding(
                    pattern_category=PatternCategory.ERROR_PATH,
                    severity=PatternSeverity.CRITICAL,
                    file_path="test.py",
                    message="Critical issue",
                ),
            ],
        )

        assert result.has_critical is True

    def test_has_critical_false(self):
        """has_critical returns False when no critical findings."""
        result = PatternResult(
            file_path="test.py",
            findings=[
                PatternFinding(
                    pattern_category=PatternCategory.BOUNDARY_VALUE,
                    severity=PatternSeverity.MINOR,
                    file_path="test.py",
                    message="Minor issue",
                ),
            ],
        )

        assert result.has_critical is False

    def test_findings_by_category(self):
        """Group findings by category."""
        result = PatternResult(
            file_path="test.py",
            findings=[
                PatternFinding(
                    pattern_category=PatternCategory.BOUNDARY_VALUE,
                    severity=PatternSeverity.MINOR,
                    file_path="test.py",
                    message="Boundary issue",
                ),
                PatternFinding(
                    pattern_category=PatternCategory.ERROR_PATH,
                    severity=PatternSeverity.MAJOR,
                    file_path="test.py",
                    message="Error path issue",
                ),
                PatternFinding(
                    pattern_category=PatternCategory.BOUNDARY_VALUE,
                    severity=PatternSeverity.MINOR,
                    file_path="test.py",
                    message="Another boundary",
                ),
            ],
        )

        by_category = result.findings_by_category

        assert PatternCategory.BOUNDARY_VALUE in by_category
        assert PatternCategory.ERROR_PATH in by_category
        assert len(by_category[PatternCategory.BOUNDARY_VALUE]) == 2
        assert len(by_category[PatternCategory.ERROR_PATH]) == 1

    def test_findings_by_severity(self):
        """Group findings by severity."""
        result = PatternResult(
            file_path="test.py",
            findings=[
                PatternFinding(
                    pattern_category=PatternCategory.ERROR_PATH,
                    severity=PatternSeverity.CRITICAL,
                    file_path="test.py",
                    message="Critical",
                ),
                PatternFinding(
                    pattern_category=PatternCategory.BOUNDARY_VALUE,
                    severity=PatternSeverity.MINOR,
                    file_path="test.py",
                    message="Minor 1",
                ),
                PatternFinding(
                    pattern_category=PatternCategory.BOUNDARY_VALUE,
                    severity=PatternSeverity.MINOR,
                    file_path="test.py",
                    message="Minor 2",
                ),
            ],
        )

        by_severity = result.findings_by_severity

        assert PatternSeverity.CRITICAL in by_severity
        assert PatternSeverity.MINOR in by_severity
        assert len(by_severity[PatternSeverity.CRITICAL]) == 1
        assert len(by_severity[PatternSeverity.MINOR]) == 2


class TestGenerateChecklist:
    """Test checklist generation."""

    def test_generate_checklist_has_items(self):
        """Generated checklist has items."""
        code = """
def process(x):
    return x * 2
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()

            analyzer = PatternAnalyzer()
            checklist = analyzer.generate_checklist(Path(f.name))

            assert checklist.module_path == f.name
            assert len(checklist.items) > 0

    def test_checklist_categories_match_default(self):
        """Checklist categories match default categories."""
        code = """
def process(x):
    return x * 2
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()

            analyzer = PatternAnalyzer()
            checklist = analyzer.generate_checklist(Path(f.name))

            categories = set(item.category for item in checklist.items)
            expected = set(DEFAULT_CHECKLIST.keys())

            assert categories == expected

    def test_checklist_pass_rate(self):
        """Checklist computes pass rate."""
        code = """
def process(x):
    return x * 2
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()

            analyzer = PatternAnalyzer()
            checklist = analyzer.generate_checklist(Path(f.name))

            assert checklist.pass_rate >= 0
            assert checklist.pass_rate <= 100


class TestGenerateTestMatrix:
    """Test test matrix generation."""

    def test_generate_matrix_structure(self):
        """Generated matrix has correct structure."""
        code = """
def process(x):
    return x * 2
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()

            analyzer = PatternAnalyzer()
            matrix = analyzer.generate_test_matrix(Path(f.name))

            assert "file" in matrix
            assert "total_findings" in matrix
            assert "categories" in matrix


class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    def test_analyze_module_function(self):
        """analyze_module convenience function works."""
        code = """
def process(x):
    return x * 2
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()

            result = analyze_module(Path(f.name))

            assert isinstance(result, PatternResult)

    def test_generate_gap_report_function(self):
        """generate_gap_report convenience function works."""
        code = """
def process(x):
    return x * 2
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()

            report = generate_gap_report(Path(f.name))

            assert isinstance(report, str)
            assert "# Pattern Analysis Gap Report" in report
            assert "Summary" in report
