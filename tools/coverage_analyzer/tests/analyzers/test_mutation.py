"""Tests for mutation testing analyzer (Layer 2)."""

from unittest.mock import Mock, patch

import pytest
from coverage_analyzer.adapters.base_adapter import ToolNotAvailableError
from coverage_analyzer.analyzers.mutation import MutationAnalyzer
from coverage_analyzer.base import AnalysisConfiguration, MutationMetrics


class TestMutationAnalyzer:
    """Tests for MutationAnalyzer."""

    def test_initialization(self, tmp_path):
        config = AnalysisConfiguration(target_path=str(tmp_path), language="python")
        analyzer = MutationAnalyzer(config)
        assert analyzer.config == config

    def test_unsupported_language(self, tmp_path):
        config = AnalysisConfiguration(target_path=str(tmp_path), language="java")
        analyzer = MutationAnalyzer(config)

        with pytest.raises(ValueError, match="Unsupported language"):
            analyzer.analyze()

    def test_powershell_returns_empty_metrics(self, tmp_path):
        """PowerShell mutation testing not fully supported yet."""
        config = AnalysisConfiguration(target_path=str(tmp_path), language="powershell")
        analyzer = MutationAnalyzer(config)

        metrics = analyzer.analyze()

        assert isinstance(metrics, MutationMetrics)
        assert metrics.total_mutants == 0
        assert metrics.mutation_score == 0.0
        assert metrics.tool_name == "none"

    @patch("coverage_analyzer.analyzers.mutation.get_registry")
    def test_analyze_python_no_tools(self, mock_get_registry, tmp_path):
        config = AnalysisConfiguration(target_path=str(tmp_path), language="python")

        mock_registry = Mock()
        mock_registry.is_adapter_available.return_value = False
        mock_get_registry.return_value = mock_registry

        analyzer = MutationAnalyzer(config)

        with pytest.raises(
            ToolNotAvailableError, match="No Python mutation testing tools"
        ):
            analyzer.analyze()

    @patch("coverage_analyzer.analyzers.mutation.get_registry")
    def test_analyze_python_high_score(self, mock_get_registry, tmp_path):
        """Test with high mutation score (excellent test quality)."""
        config = AnalysisConfiguration(target_path=str(tmp_path), language="python")

        # Mock adapter with high mutation score
        mock_adapter = Mock()
        mock_adapter.execute.return_value = {
            "total_mutants": 100,
            "killed_mutants": 85,
            "survived_mutants": 15,
            "timeout_mutants": 0,
            "suspicious_mutants": 0,
            "mutation_score": 85.0,
            "tool_name": "mutmut",
        }

        mock_registry = Mock()
        mock_registry.is_adapter_available.side_effect = lambda name: name == "mutmut"
        mock_registry.get_adapter.return_value = mock_adapter
        mock_get_registry.return_value = mock_registry

        analyzer = MutationAnalyzer(config)
        metrics = analyzer.analyze()

        assert isinstance(metrics, MutationMetrics)
        assert metrics.total_mutants == 100
        assert metrics.killed_mutants == 85
        assert metrics.mutation_score == 85.0
        assert metrics.tool_name == "mutmut"

    @patch("coverage_analyzer.analyzers.mutation.logger")
    @patch("coverage_analyzer.analyzers.mutation.get_registry")
    def test_log_excellent_quality(self, mock_get_registry, mock_logger, tmp_path):
        """Test logging for excellent test quality (≥80%)."""
        config = AnalysisConfiguration(target_path=str(tmp_path), language="python")

        mock_adapter = Mock()
        mock_adapter.execute.return_value = {
            "total_mutants": 100,
            "killed_mutants": 90,
            "survived_mutants": 10,
            "timeout_mutants": 0,
            "suspicious_mutants": 0,
            "mutation_score": 90.0,
            "tool_name": "mutmut",
        }

        mock_registry = Mock()
        mock_registry.is_adapter_available.side_effect = lambda name: name == "mutmut"
        mock_registry.get_adapter.return_value = mock_adapter
        mock_get_registry.return_value = mock_registry

        analyzer = MutationAnalyzer(config)
        metrics = analyzer.analyze()

        # Should log excellent quality
        assert any("Excellent" in str(call) for call in mock_logger.info.call_args_list)

    @patch("coverage_analyzer.analyzers.mutation.logger")
    @patch("coverage_analyzer.analyzers.mutation.get_registry")
    def test_log_poor_quality(self, mock_get_registry, mock_logger, tmp_path):
        """Test logging for poor test quality (<40%)."""
        config = AnalysisConfiguration(target_path=str(tmp_path), language="python")

        mock_adapter = Mock()
        mock_adapter.execute.return_value = {
            "total_mutants": 100,
            "killed_mutants": 30,
            "survived_mutants": 70,
            "timeout_mutants": 0,
            "suspicious_mutants": 0,
            "mutation_score": 30.0,
            "tool_name": "mutmut",
        }

        mock_registry = Mock()
        mock_registry.is_adapter_available.side_effect = lambda name: name == "mutmut"
        mock_registry.get_adapter.return_value = mock_adapter
        mock_get_registry.return_value = mock_registry

        analyzer = MutationAnalyzer(config)
        metrics = analyzer.analyze()

        # Should log poor quality
        assert any("Poor" in str(call) for call in mock_logger.error.call_args_list)

    @patch("coverage_analyzer.analyzers.mutation.logger")
    @patch("coverage_analyzer.analyzers.mutation.get_registry")
    def test_log_surviving_mutants_warning(
        self, mock_get_registry, mock_logger, tmp_path
    ):
        """Test warning about surviving mutants."""
        config = AnalysisConfiguration(target_path=str(tmp_path), language="python")

        mock_adapter = Mock()
        mock_adapter.execute.return_value = {
            "total_mutants": 50,
            "killed_mutants": 30,
            "survived_mutants": 20,  # Significant survivors
            "timeout_mutants": 0,
            "suspicious_mutants": 0,
            "mutation_score": 60.0,
            "tool_name": "mutmut",
        }

        mock_registry = Mock()
        mock_registry.is_adapter_available.side_effect = lambda name: name == "mutmut"
        mock_registry.get_adapter.return_value = mock_adapter
        mock_get_registry.return_value = mock_registry

        analyzer = MutationAnalyzer(config)
        metrics = analyzer.analyze()

        # Should warn about surviving mutants
        assert any(
            "survived" in str(call).lower()
            for call in mock_logger.warning.call_args_list
        )

    @patch("coverage_analyzer.analyzers.mutation.get_registry")
    def test_tool_execution_failure(self, mock_get_registry, tmp_path):
        """Test handling of tool execution failures."""
        config = AnalysisConfiguration(target_path=str(tmp_path), language="python")

        # Mock adapter that raises exception
        mock_adapter = Mock()
        mock_adapter.execute.side_effect = Exception("Mutation testing failed")

        mock_registry = Mock()
        mock_registry.is_adapter_available.side_effect = lambda name: name == "mutmut"
        mock_registry.get_adapter.return_value = mock_adapter
        mock_get_registry.return_value = mock_registry

        analyzer = MutationAnalyzer(config)

        with pytest.raises(ToolNotAvailableError, match="Mutation testing failed"):
            analyzer.analyze()
