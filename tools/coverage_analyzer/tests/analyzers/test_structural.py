"""Tests for structural coverage analyzer."""

from unittest.mock import Mock, patch

import pytest
from coverage_analyzer.adapters.base_adapter import ToolNotAvailableError
from coverage_analyzer.analyzers.structural import StructuralCoverageAnalyzer
from coverage_analyzer.base import AnalysisConfiguration, StructuralCoverageMetrics
from coverage_analyzer.registry import get_registry


class TestStructuralCoverageAnalyzer:
    """Tests for StructuralCoverageAnalyzer class."""

    def test_initialization(self, mock_coverage_config):
        """Test analyzer initialization."""
        analyzer = StructuralCoverageAnalyzer(mock_coverage_config)
        assert analyzer.config == mock_coverage_config
        assert analyzer.registry is not None

    def test_analyze_unsupported_language(self, tmp_path):
        """Test analysis with unsupported language."""
        config = AnalysisConfiguration(
            target_path=str(tmp_path), language="java"  # Not supported
        )

        analyzer = StructuralCoverageAnalyzer(config)

        with pytest.raises(ValueError, match="Unsupported language"):
            analyzer.analyze()

    @patch("coverage_analyzer.analyzers.structural.get_registry")
    def test_analyze_python_adapter_not_registered(self, mock_get_registry, tmp_path):
        """Test Python analysis when adapter is not registered."""
        config = AnalysisConfiguration(target_path=str(tmp_path), language="python")

        # Mock registry without coverage.py adapter
        mock_registry = Mock()
        mock_registry.get_adapter.side_effect = KeyError("Not registered")
        mock_get_registry.return_value = mock_registry

        analyzer = StructuralCoverageAnalyzer(config)

        with pytest.raises(
            ToolNotAvailableError, match="coverage.py adapter not registered"
        ):
            analyzer.analyze()

    @patch("coverage_analyzer.analyzers.structural.get_registry")
    def test_analyze_python_success(
        self, mock_get_registry, sample_python_project, sample_structural_metrics
    ):
        """Test successful Python coverage analysis."""
        config = AnalysisConfiguration(
            target_path=str(sample_python_project), language="python"
        )

        # Mock adapter
        mock_adapter = Mock()
        mock_adapter.execute.return_value = {
            "line_coverage_percent": 85.5,
            "branch_coverage_percent": 80.0,
            "function_coverage_percent": 90.0,
            "total_lines": 100,
            "covered_lines": 85,
            "total_branches": 40,
            "covered_branches": 32,
            "total_functions": 10,
            "covered_functions": 9,
            "uncovered_lines": [15, 27, 38],
            "tool_name": "coverage.py",
        }

        # Mock registry
        mock_registry = Mock()
        mock_registry.get_adapter.return_value = mock_adapter
        mock_get_registry.return_value = mock_registry

        analyzer = StructuralCoverageAnalyzer(config)
        metrics = analyzer.analyze()

        # Verify
        assert isinstance(metrics, StructuralCoverageMetrics)
        assert metrics.line_coverage_percent == 85.5
        assert metrics.branch_coverage_percent == 80.0
        assert metrics.tool_name == "coverage.py"

        # Verify adapter was called correctly
        mock_adapter.execute.assert_called_once()
        call_args = mock_adapter.execute.call_args
        assert call_args[1]["target_path"] == str(sample_python_project)

    @patch("coverage_analyzer.analyzers.structural.get_registry")
    def test_analyze_powershell_success(self, mock_get_registry, tmp_path):
        """Test successful PowerShell coverage analysis."""
        config = AnalysisConfiguration(target_path=str(tmp_path), language="powershell")

        # Mock adapter
        mock_adapter = Mock()
        mock_adapter.execute.return_value = {
            "line_coverage_percent": 75.0,
            "branch_coverage_percent": 75.0,
            "function_coverage_percent": 0.0,
            "total_lines": 200,
            "covered_lines": 150,
            "total_branches": 0,
            "covered_branches": 0,
            "total_functions": 0,
            "covered_functions": 0,
            "uncovered_lines": [10, 20, 30],
            "tool_name": "pester",
        }

        # Mock registry
        mock_registry = Mock()
        mock_registry.get_adapter.return_value = mock_adapter
        mock_get_registry.return_value = mock_registry

        analyzer = StructuralCoverageAnalyzer(config)
        metrics = analyzer.analyze()

        # Verify
        assert isinstance(metrics, StructuralCoverageMetrics)
        assert metrics.line_coverage_percent == 75.0
        assert metrics.tool_name == "pester"

    @patch("coverage_analyzer.analyzers.structural.logger")
    @patch("coverage_analyzer.analyzers.structural.get_registry")
    def test_log_results_below_threshold(
        self, mock_get_registry, mock_logger, tmp_path
    ):
        """Test warning logs when coverage is below thresholds."""
        config = AnalysisConfiguration(
            target_path=str(tmp_path),
            language="python",
            min_line_coverage=90.0,
            min_branch_coverage=85.0,
        )

        # Mock adapter with low coverage
        mock_adapter = Mock()
        mock_adapter.execute.return_value = {
            "line_coverage_percent": 70.0,  # Below threshold
            "branch_coverage_percent": 60.0,  # Below threshold
            "function_coverage_percent": 0.0,
            "total_lines": 100,
            "covered_lines": 70,
            "total_branches": 50,
            "covered_branches": 30,
            "total_functions": 0,
            "covered_functions": 0,
            "uncovered_lines": [],
            "tool_name": "coverage.py",
        }

        mock_registry = Mock()
        mock_registry.get_adapter.return_value = mock_adapter
        mock_get_registry.return_value = mock_registry

        analyzer = StructuralCoverageAnalyzer(config)
        metrics = analyzer.analyze()

        # Verify warnings were logged
        assert mock_logger.warning.call_count == 2  # Line and branch coverage warnings
