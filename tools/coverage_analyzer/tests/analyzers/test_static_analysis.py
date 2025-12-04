"""Tests for static analysis analyzer (Layer 0)."""

from unittest.mock import Mock, patch

import pytest
from coverage_analyzer.adapters.base_adapter import ToolNotAvailableError
from coverage_analyzer.analyzers.static_analysis import StaticAnalysisAnalyzer
from coverage_analyzer.base import AnalysisConfiguration, StaticAnalysisMetrics


class TestStaticAnalysisAnalyzer:
    """Tests for StaticAnalysisAnalyzer."""

    def test_initialization(self, tmp_path):
        config = AnalysisConfiguration(target_path=str(tmp_path), language="python")
        analyzer = StaticAnalysisAnalyzer(config)
        assert analyzer.config == config

    def test_unsupported_language(self, tmp_path):
        config = AnalysisConfiguration(target_path=str(tmp_path), language="java")
        analyzer = StaticAnalysisAnalyzer(config)

        with pytest.raises(ValueError, match="Unsupported language"):
            analyzer.analyze()

    @patch("coverage_analyzer.analyzers.static_analysis.get_registry")
    def test_analyze_python_no_tools(self, mock_get_registry, tmp_path):
        config = AnalysisConfiguration(target_path=str(tmp_path), language="python")

        mock_registry = Mock()
        mock_registry.is_adapter_available.return_value = False
        mock_get_registry.return_value = mock_registry

        analyzer = StaticAnalysisAnalyzer(config)

        with pytest.raises(
            ToolNotAvailableError, match="No Python static analysis tools"
        ):
            analyzer.analyze()

    @patch("coverage_analyzer.analyzers.static_analysis.get_registry")
    def test_analyze_python_single_tool(self, mock_get_registry, tmp_path):
        config = AnalysisConfiguration(target_path=str(tmp_path), language="python")

        # Mock adapter
        mock_adapter = Mock()
        mock_adapter.execute.return_value = {
            "code_quality_score": 85.0,
            "total_issues": 10,
            "issues_by_severity": {"high": 2, "medium": 5, "low": 3},
            "security_vulnerabilities": 1,
            "type_errors": 0,
            "maintainability_index": 75.0,
            "high_complexity_functions": ["func1"],
            "tool_name": "prospector",
        }

        # Mock registry
        mock_registry = Mock()
        mock_registry.is_adapter_available.side_effect = (
            lambda name: name == "prospector"
        )
        mock_registry.get_adapter.return_value = mock_adapter
        mock_get_registry.return_value = mock_registry

        analyzer = StaticAnalysisAnalyzer(config)
        metrics = analyzer.analyze()

        assert isinstance(metrics, StaticAnalysisMetrics)
        assert metrics.code_quality_score == 85.0
        assert metrics.total_issues == 10
        assert metrics.tool_name == "prospector"

    @patch("coverage_analyzer.analyzers.static_analysis.get_registry")
    def test_analyze_python_multiple_tools(self, mock_get_registry, tmp_path):
        config = AnalysisConfiguration(target_path=str(tmp_path), language="python")

        # Mock adapters - return different results for different tools
        def mock_execute(target_path, **kwargs):
            tool_name = kwargs.get("tool_name", "unknown")
            if "radon" in str(mock_adapter.tool_name):
                return {
                    "code_quality_score": 90.0,
                    "total_issues": 5,
                    "issues_by_severity": {"high": 0, "medium": 2, "low": 3},
                    "security_vulnerabilities": 0,
                    "type_errors": 0,
                    "maintainability_index": 85.0,
                    "high_complexity_functions": [],
                    "tool_name": "radon",
                }
            else:
                return {
                    "code_quality_score": 80.0,
                    "total_issues": 15,
                    "issues_by_severity": {"high": 3, "medium": 7, "low": 5},
                    "security_vulnerabilities": 2,
                    "type_errors": 1,
                    "maintainability_index": 70.0,
                    "high_complexity_functions": ["func1"],
                    "tool_name": "bandit",
                }

        mock_adapter = Mock()
        mock_adapter.execute.side_effect = mock_execute

        # Mock registry - both tools available
        mock_registry = Mock()
        mock_registry.is_adapter_available.side_effect = lambda name: name in [
            "radon",
            "bandit",
        ]
        mock_registry.get_adapter.return_value = mock_adapter
        mock_get_registry.return_value = mock_registry

        analyzer = StaticAnalysisAnalyzer(config)
        metrics = analyzer.analyze()

        # Should aggregate results from both tools
        assert isinstance(metrics, StaticAnalysisMetrics)
        assert 80 <= metrics.code_quality_score <= 90  # Average
        assert "+" in metrics.tool_name  # Combined tool names

    @patch("coverage_analyzer.analyzers.static_analysis.get_registry")
    def test_analyze_powershell_success(self, mock_get_registry, tmp_path):
        config = AnalysisConfiguration(target_path=str(tmp_path), language="powershell")

        # Mock adapter
        mock_adapter = Mock()
        mock_adapter.execute.return_value = {
            "code_quality_score": 88.0,
            "total_issues": 8,
            "issues_by_severity": {"high": 1, "medium": 4, "low": 3},
            "security_vulnerabilities": 1,
            "type_errors": 0,
            "maintainability_index": 0.0,
            "high_complexity_functions": [],
            "tool_name": "psscriptanalyzer",
        }

        mock_registry = Mock()
        mock_registry.get_adapter.return_value = mock_adapter
        mock_get_registry.return_value = mock_registry

        analyzer = StaticAnalysisAnalyzer(config)
        metrics = analyzer.analyze()

        assert isinstance(metrics, StaticAnalysisMetrics)
        assert metrics.code_quality_score == 88.0
        assert metrics.tool_name == "psscriptanalyzer"

    @patch("coverage_analyzer.analyzers.static_analysis.logger")
    @patch("coverage_analyzer.analyzers.static_analysis.get_registry")
    def test_log_security_warning(self, mock_get_registry, mock_logger, tmp_path):
        config = AnalysisConfiguration(
            target_path=str(tmp_path), language="python", fail_on_critical_security=True
        )

        # Mock adapter with security vulnerabilities
        mock_adapter = Mock()
        mock_adapter.execute.return_value = {
            "code_quality_score": 70.0,
            "total_issues": 20,
            "issues_by_severity": {"high": 5, "medium": 10, "low": 5},
            "security_vulnerabilities": 3,  # Has vulnerabilities
            "type_errors": 0,
            "maintainability_index": 65.0,
            "high_complexity_functions": [],
            "tool_name": "bandit",
        }

        mock_registry = Mock()
        mock_registry.is_adapter_available.side_effect = lambda name: name == "bandit"
        mock_registry.get_adapter.return_value = mock_adapter
        mock_get_registry.return_value = mock_registry

        analyzer = StaticAnalysisAnalyzer(config)
        metrics = analyzer.analyze()

        # Should log error about security vulnerabilities
        assert mock_logger.error.called
        assert "security vulnerabilities" in str(mock_logger.error.call_args)

    def test_aggregate_empty_results(self, tmp_path):
        config = AnalysisConfiguration(target_path=str(tmp_path), language="python")

        analyzer = StaticAnalysisAnalyzer(config)
        metrics = analyzer._aggregate_results([])

        # Should return empty metrics
        assert metrics.code_quality_score == 0.0
        assert metrics.total_issues == 0
        assert metrics.tool_name == "none"
