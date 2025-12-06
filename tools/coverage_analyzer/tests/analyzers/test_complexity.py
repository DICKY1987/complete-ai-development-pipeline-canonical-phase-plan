"""Tests for complexity analyzer (Layer 3).

DOC_ID: DOC-TEST-ANALYZERS-TEST-COMPLEXITY-361
"""

from unittest.mock import Mock, patch

import pytest
from coverage_analyzer.adapters.base_adapter import ToolNotAvailableError
from coverage_analyzer.analyzers.complexity import ComplexityAnalyzer
from coverage_analyzer.base import AnalysisConfiguration, ComplexityMetrics


class TestComplexityAnalyzer:
    """Tests for ComplexityAnalyzer."""

    def test_initialization(self, tmp_path):
        config = AnalysisConfiguration(target_path=str(tmp_path), language="python")
        analyzer = ComplexityAnalyzer(config)
        assert analyzer.config == config

    def test_unsupported_language(self, tmp_path):
        config = AnalysisConfiguration(target_path=str(tmp_path), language="java")
        analyzer = ComplexityAnalyzer(config)

        with pytest.raises(ValueError, match="Unsupported language"):
            analyzer.analyze()

    @patch("coverage_analyzer.analyzers.complexity.get_registry")
    def test_analyze_python_no_tools(self, mock_get_registry, tmp_path):
        config = AnalysisConfiguration(target_path=str(tmp_path), language="python")

        mock_registry = Mock()
        mock_registry.is_adapter_available.return_value = False
        mock_get_registry.return_value = mock_registry

        analyzer = ComplexityAnalyzer(config)

        with pytest.raises(ToolNotAvailableError, match="Radon not available"):
            analyzer.analyze()

    @patch("coverage_analyzer.analyzers.complexity.get_registry")
    def test_analyze_python_low_complexity(self, mock_get_registry, tmp_path):
        """Test with low complexity (good code quality)."""
        config = AnalysisConfiguration(target_path=str(tmp_path), language="python")

        # Mock radon adapter with low complexity
        mock_adapter = Mock()
        mock_adapter.execute.return_value = {
            "functions_analyzed": 10,
            "total_complexity": 30,  # Avg = 3
            "max_complexity": 5,
            "maintainability_index": 85.0,
            "high_complexity_count": 0,
            "total_loc": 200,
        }

        mock_registry = Mock()
        mock_registry.is_adapter_available.return_value = True
        mock_registry.get_adapter.return_value = mock_adapter
        mock_get_registry.return_value = mock_registry

        analyzer = ComplexityAnalyzer(config)
        metrics = analyzer.analyze()

        assert isinstance(metrics, ComplexityMetrics)
        assert metrics.average_complexity == 3.0
        assert metrics.max_complexity == 5
        assert metrics.functions_above_threshold == 0
        assert metrics.tool_name == "radon"

    @patch("coverage_analyzer.analyzers.complexity.get_registry")
    def test_analyze_python_high_complexity(self, mock_get_registry, tmp_path):
        """Test with high complexity (poor code quality)."""
        config = AnalysisConfiguration(target_path=str(tmp_path), language="python")

        # Mock radon adapter with high complexity
        mock_adapter = Mock()
        mock_adapter.execute.return_value = {
            "functions_analyzed": 10,
            "total_complexity": 150,  # Avg = 15 (high!)
            "max_complexity": 25,  # Very high!
            "maintainability_index": 35.0,  # Poor!
            "high_complexity_count": 5,
            "total_loc": 500,
        }

        mock_registry = Mock()
        mock_registry.is_adapter_available.return_value = True
        mock_registry.get_adapter.return_value = mock_adapter
        mock_get_registry.return_value = mock_registry

        analyzer = ComplexityAnalyzer(config)
        metrics = analyzer.analyze()

        assert metrics.average_complexity == 15.0
        assert metrics.max_complexity == 25
        assert metrics.functions_above_threshold == 5

    @patch("coverage_analyzer.analyzers.complexity.logger")
    @patch("coverage_analyzer.analyzers.complexity.get_registry")
    def test_log_excellent_quality(self, mock_get_registry, mock_logger, tmp_path):
        """Test logging for excellent maintainability (≥80)."""
        config = AnalysisConfiguration(target_path=str(tmp_path), language="python")

        mock_adapter = Mock()
        mock_adapter.execute.return_value = {
            "functions_analyzed": 10,
            "total_complexity": 30,
            "max_complexity": 5,
            "maintainability_index": 90.0,
            "high_complexity_count": 0,
            "total_loc": 200,
        }

        mock_registry = Mock()
        mock_registry.is_adapter_available.return_value = True
        mock_registry.get_adapter.return_value = mock_adapter
        mock_get_registry.return_value = mock_registry

        analyzer = ComplexityAnalyzer(config)
        metrics = analyzer.analyze()

        # Should log excellent quality
        assert any("Excellent" in str(call) for call in mock_logger.info.call_args_list)

    @patch("coverage_analyzer.analyzers.complexity.logger")
    @patch("coverage_analyzer.analyzers.complexity.get_registry")
    def test_log_poor_quality(self, mock_get_registry, mock_logger, tmp_path):
        """Test logging for poor maintainability (<40)."""
        config = AnalysisConfiguration(target_path=str(tmp_path), language="python")

        mock_adapter = Mock()
        mock_adapter.execute.return_value = {
            "functions_analyzed": 10,
            "total_complexity": 200,
            "max_complexity": 30,
            "maintainability_index": 25.0,
            "high_complexity_count": 8,
            "total_loc": 500,
        }

        mock_registry = Mock()
        mock_registry.is_adapter_available.return_value = True
        mock_registry.get_adapter.return_value = mock_adapter
        mock_get_registry.return_value = mock_registry

        analyzer = ComplexityAnalyzer(config)
        metrics = analyzer.analyze()

        # Should log high complexity error
        assert any(
            "High complexity" in str(call) or "very high" in str(call)
            for call in mock_logger.error.call_args_list
        )

    @patch("coverage_analyzer.analyzers.complexity.get_registry")
    def test_analyze_powershell(self, mock_get_registry, tmp_path):
        """Test PowerShell complexity analysis."""
        config = AnalysisConfiguration(target_path=str(tmp_path), language="powershell")

        # Mock PSSA adapter
        mock_adapter = Mock()
        mock_adapter.execute.return_value = {
            "total_issues": 10,
            "error_count": 2,
            "warning_count": 5,
            "total_loc": 300,
        }

        mock_registry = Mock()
        mock_registry.is_adapter_available.return_value = True
        mock_registry.get_adapter.return_value = mock_adapter
        mock_get_registry.return_value = mock_registry

        analyzer = ComplexityAnalyzer(config)
        metrics = analyzer.analyze()

        assert isinstance(metrics, ComplexityMetrics)
        assert metrics.tool_name == "psscriptanalyzer"
        assert metrics.average_complexity == 1.0  # 10 issues / 10

    @patch("coverage_analyzer.analyzers.complexity.get_registry")
    def test_analyze_powershell_no_tools(self, mock_get_registry, tmp_path):
        config = AnalysisConfiguration(target_path=str(tmp_path), language="powershell")

        mock_registry = Mock()
        mock_registry.is_adapter_available.return_value = False
        mock_get_registry.return_value = mock_registry

        analyzer = ComplexityAnalyzer(config)

        with pytest.raises(
            ToolNotAvailableError, match="PSScriptAnalyzer not available"
        ):
            analyzer.analyze()

    @patch("coverage_analyzer.analyzers.complexity.get_registry")
    def test_zero_functions_analyzed(self, mock_get_registry, tmp_path):
        """Test handling of zero functions (empty project)."""
        config = AnalysisConfiguration(target_path=str(tmp_path), language="python")

        mock_adapter = Mock()
        mock_adapter.execute.return_value = {
            "functions_analyzed": 0,
            "total_complexity": 0,
            "max_complexity": 0,
            "maintainability_index": 100.0,
            "high_complexity_count": 0,
            "total_loc": 0,
        }

        mock_registry = Mock()
        mock_registry.is_adapter_available.return_value = True
        mock_registry.get_adapter.return_value = mock_adapter
        mock_get_registry.return_value = mock_registry

        analyzer = ComplexityAnalyzer(config)
        metrics = analyzer.analyze()

        # Should handle division by zero gracefully
        assert metrics.average_complexity == 0.0

    @patch("coverage_analyzer.analyzers.complexity.get_registry")
    def test_tool_execution_failure(self, mock_get_registry, tmp_path):
        """Test handling of tool execution failures."""
        config = AnalysisConfiguration(target_path=str(tmp_path), language="python")

        # Mock adapter that raises exception
        mock_adapter = Mock()
        mock_adapter.execute.side_effect = Exception("Radon crashed")

        mock_registry = Mock()
        mock_registry.is_adapter_available.return_value = True
        mock_registry.get_adapter.return_value = mock_adapter
        mock_get_registry.return_value = mock_registry

        analyzer = ComplexityAnalyzer(config)

        with pytest.raises(ToolNotAvailableError, match="Complexity analysis failed"):
            analyzer.analyze()
