"""Tests for operational validation analyzer (Layer 4)."""
DOC_ID: DOC-TEST-ANALYZERS-TEST-OPERATIONAL-360

from unittest.mock import Mock, patch

import pytest
from coverage_analyzer.adapters.base_adapter import ToolNotAvailableError
from coverage_analyzer.analyzers.operational import OperationalAnalyzer
from coverage_analyzer.base import AnalysisConfiguration, OperationalMetrics


class TestOperationalAnalyzer:
    """Tests for OperationalAnalyzer."""

    @patch("coverage_analyzer.analyzers.operational.get_registry")
    def test_analyze_success(self, mock_get_registry, tmp_path):
        """Test successful operational analysis."""
        config = AnalysisConfiguration(target_path=str(tmp_path), language="python")

        # Mock Locust adapter
        mock_adapter = Mock()
        mock_adapter.execute.return_value = {
            "total_requests": 100,
            "failed_requests": 2,
            "avg_response_time": 150.5,
            "max_response_time": 350.0,
            "requests_per_second": 10.5,
        }

        mock_registry = Mock()
        mock_registry.is_adapter_available.return_value = True
        mock_registry.get_adapter.return_value = mock_adapter
        mock_get_registry.return_value = mock_registry

        analyzer = OperationalAnalyzer(config)
        metrics = analyzer.analyze(users=10, run_time="30s")

        assert isinstance(metrics, OperationalMetrics)
        assert metrics.total_requests == 100
        assert metrics.failed_requests == 2
        assert metrics.success_rate == 98.0
        assert metrics.avg_response_time_ms == 150.5
        assert metrics.concurrent_users == 10
        assert metrics.tool_name == "locust"

    @patch("coverage_analyzer.analyzers.operational.get_registry")
    def test_analyze_no_locust(self, mock_get_registry, tmp_path):
        """Test analysis when Locust not available."""
        config = AnalysisConfiguration(target_path=str(tmp_path), language="python")

        mock_registry = Mock()
        mock_registry.is_adapter_available.return_value = False
        mock_get_registry.return_value = mock_registry

        analyzer = OperationalAnalyzer(config)

        with pytest.raises(ToolNotAvailableError, match="Locust not available"):
            analyzer.analyze()

    @patch("coverage_analyzer.analyzers.operational.get_registry")
    def test_performance_score_excellent(self, mock_get_registry, tmp_path):
        """Test performance score calculation for excellent performance."""
        config = AnalysisConfiguration(target_path=str(tmp_path), language="python")

        # Mock excellent results: 100% success, 50ms avg
        mock_adapter = Mock()
        mock_adapter.execute.return_value = {
            "total_requests": 100,
            "failed_requests": 0,
            "avg_response_time": 50.0,  # <100ms = 40 points
            "max_response_time": 100.0,
            "requests_per_second": 20.0,
        }

        mock_registry = Mock()
        mock_registry.is_adapter_available.return_value = True
        mock_registry.get_adapter.return_value = mock_adapter
        mock_get_registry.return_value = mock_registry

        analyzer = OperationalAnalyzer(config)
        metrics = analyzer.analyze()

        # 100% success rate * 0.6 = 60 + 40 (response time) = 100
        assert metrics.performance_score == 100.0
        assert metrics.passed_validation is True

    @patch("coverage_analyzer.analyzers.operational.get_registry")
    def test_performance_score_good(self, mock_get_registry, tmp_path):
        """Test performance score calculation for good performance."""
        config = AnalysisConfiguration(target_path=str(tmp_path), language="python")

        # Mock good results: 95% success, 250ms avg
        mock_adapter = Mock()
        mock_adapter.execute.return_value = {
            "total_requests": 100,
            "failed_requests": 5,
            "avg_response_time": 250.0,  # 100-500ms = 30 points
            "max_response_time": 500.0,
            "requests_per_second": 10.0,
        }

        mock_registry = Mock()
        mock_registry.is_adapter_available.return_value = True
        mock_registry.get_adapter.return_value = mock_adapter
        mock_get_registry.return_value = mock_registry

        analyzer = OperationalAnalyzer(config)
        metrics = analyzer.analyze()

        # 95% * 0.6 = 57 + 30 = 87
        assert metrics.performance_score == 87.0
        assert metrics.passed_validation is True

    @patch("coverage_analyzer.analyzers.operational.get_registry")
    def test_performance_score_poor(self, mock_get_registry, tmp_path):
        """Test performance score calculation for poor performance."""
        config = AnalysisConfiguration(target_path=str(tmp_path), language="python")

        # Mock poor results: 80% success, 3000ms avg
        mock_adapter = Mock()
        mock_adapter.execute.return_value = {
            "total_requests": 100,
            "failed_requests": 20,
            "avg_response_time": 3000.0,  # >2000ms = 0 points
            "max_response_time": 5000.0,
            "requests_per_second": 2.0,
        }

        mock_registry = Mock()
        mock_registry.is_adapter_available.return_value = True
        mock_registry.get_adapter.return_value = mock_adapter
        mock_get_registry.return_value = mock_registry

        analyzer = OperationalAnalyzer(config)
        metrics = analyzer.analyze()

        # 80% * 0.6 = 48 + 0 = 48
        assert metrics.performance_score == 48.0
        assert metrics.passed_validation is False

    @patch("coverage_analyzer.analyzers.operational.get_registry")
    def test_validation_failed_low_success_rate(self, mock_get_registry, tmp_path):
        """Test validation fails with low success rate."""
        config = AnalysisConfiguration(target_path=str(tmp_path), language="python")

        mock_adapter = Mock()
        mock_adapter.execute.return_value = {
            "total_requests": 100,
            "failed_requests": 10,  # 90% success
            "avg_response_time": 100.0,  # Good response time
            "max_response_time": 200.0,
            "requests_per_second": 10.0,
        }

        mock_registry = Mock()
        mock_registry.is_adapter_available.return_value = True
        mock_registry.get_adapter.return_value = mock_adapter
        mock_get_registry.return_value = mock_registry

        analyzer = OperationalAnalyzer(config)
        metrics = analyzer.analyze()

        assert metrics.success_rate == 90.0
        assert metrics.passed_validation is False  # Need >=95%

    @patch("coverage_analyzer.analyzers.operational.get_registry")
    def test_validation_failed_slow_response(self, mock_get_registry, tmp_path):
        """Test validation fails with slow response time."""
        config = AnalysisConfiguration(target_path=str(tmp_path), language="python")

        mock_adapter = Mock()
        mock_adapter.execute.return_value = {
            "total_requests": 100,
            "failed_requests": 0,  # 100% success
            "avg_response_time": 1500.0,  # Slow
            "max_response_time": 3000.0,
            "requests_per_second": 5.0,
        }

        mock_registry = Mock()
        mock_registry.is_adapter_available.return_value = True
        mock_registry.get_adapter.return_value = mock_adapter
        mock_get_registry.return_value = mock_registry

        analyzer = OperationalAnalyzer(config)
        metrics = analyzer.analyze()

        assert metrics.avg_response_time_ms == 1500.0
        assert metrics.passed_validation is False  # Need <1000ms

    @patch("coverage_analyzer.analyzers.operational.logger")
    @patch("coverage_analyzer.analyzers.operational.get_registry")
    def test_log_excellent_performance(self, mock_get_registry, mock_logger, tmp_path):
        """Test logging for excellent performance."""
        config = AnalysisConfiguration(target_path=str(tmp_path), language="python")

        mock_adapter = Mock()
        mock_adapter.execute.return_value = {
            "total_requests": 100,
            "failed_requests": 0,
            "avg_response_time": 50.0,
            "max_response_time": 100.0,
            "requests_per_second": 20.0,
        }

        mock_registry = Mock()
        mock_registry.is_adapter_available.return_value = True
        mock_registry.get_adapter.return_value = mock_adapter
        mock_get_registry.return_value = mock_registry

        analyzer = OperationalAnalyzer(config)
        metrics = analyzer.analyze()

        # Should log excellent performance
        assert any("Excellent" in str(call) for call in mock_logger.info.call_args_list)

    @patch("coverage_analyzer.analyzers.operational.logger")
    @patch("coverage_analyzer.analyzers.operational.get_registry")
    def test_log_poor_performance(self, mock_get_registry, mock_logger, tmp_path):
        """Test logging for poor performance."""
        config = AnalysisConfiguration(target_path=str(tmp_path), language="python")

        mock_adapter = Mock()
        mock_adapter.execute.return_value = {
            "total_requests": 100,
            "failed_requests": 50,
            "avg_response_time": 3000.0,
            "max_response_time": 6000.0,
            "requests_per_second": 1.0,
        }

        mock_registry = Mock()
        mock_registry.is_adapter_available.return_value = True
        mock_registry.get_adapter.return_value = mock_adapter
        mock_get_registry.return_value = mock_registry

        analyzer = OperationalAnalyzer(config)
        metrics = analyzer.analyze()

        # Should log poor performance and warnings
        assert any("Poor" in str(call) for call in mock_logger.error.call_args_list)

    @patch("coverage_analyzer.analyzers.operational.get_registry")
    def test_custom_test_parameters(self, mock_get_registry, tmp_path):
        """Test using custom test parameters."""
        config = AnalysisConfiguration(target_path=str(tmp_path), language="python")

        mock_adapter = Mock()
        mock_adapter.execute.return_value = {
            "total_requests": 500,
            "failed_requests": 10,
            "avg_response_time": 200.0,
            "max_response_time": 400.0,
            "requests_per_second": 50.0,
        }

        mock_registry = Mock()
        mock_registry.is_adapter_available.return_value = True
        mock_registry.get_adapter.return_value = mock_adapter
        mock_get_registry.return_value = mock_registry

        analyzer = OperationalAnalyzer(config)
        metrics = analyzer.analyze(
            users=50, spawn_rate=5, run_time="1m", host="http://example.com"
        )

        # Verify adapter was called with custom params
        mock_adapter.execute.assert_called_once()
        call_kwargs = mock_adapter.execute.call_args[1]
        assert call_kwargs["users"] == 50
        assert call_kwargs["spawn_rate"] == 5
        assert call_kwargs["run_time"] == "1m"
        assert call_kwargs["host"] == "http://example.com"
