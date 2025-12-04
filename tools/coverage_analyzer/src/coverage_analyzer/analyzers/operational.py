"""
Operational Validation Analyzer - Layer 4.

Tests system behavior under operational conditions:
- Load testing and performance metrics
- Stress testing and failure modes
- Operational health indicators
"""

import logging
from typing import Any, Dict

from coverage_analyzer.adapters.base_adapter import ToolNotAvailableError
from coverage_analyzer.base import AnalysisConfiguration, OperationalMetrics
from coverage_analyzer.registry import get_registry

logger = logging.getLogger(__name__)


class OperationalAnalyzer:
    """Layer 4: Operational Validation Analysis."""

    def __init__(self, config: AnalysisConfiguration):
        """
        Initialize operational analyzer.

        Args:
            config: Analysis configuration
        """
        self.config = config
        self.registry = get_registry()

    def analyze(
        self,
        users: int = 10,
        spawn_rate: int = 2,
        run_time: str = "30s",
        host: str = "http://localhost:8000",
        **kwargs,
    ) -> OperationalMetrics:
        """
        Run operational validation analysis.

        Args:
            users: Number of concurrent users to simulate
            spawn_rate: User spawn rate (users per second)
            run_time: Test duration (e.g., "30s", "1m")
            host: Target host URL
            **kwargs: Additional test parameters

        Returns:
            OperationalMetrics with load test results

        Raises:
            ToolNotAvailableError: If required tools not available
        """
        logger.info(f"Starting operational validation: users={users}, time={run_time}")

        # Currently only supports load testing via Locust
        # Future: Add performance profiling, chaos testing, etc.
        metrics = self._analyze_load_performance(
            users=users, spawn_rate=spawn_rate, run_time=run_time, host=host, **kwargs
        )

        self._log_results(metrics)
        return metrics

    def _analyze_load_performance(
        self,
        users: int,
        spawn_rate: int,
        run_time: str,
        host: str,
        **kwargs,
    ) -> OperationalMetrics:
        """Run load testing using Locust."""
        if not self.registry.is_adapter_available("locust"):
            raise ToolNotAvailableError(
                "Locust not available. Install: pip install locust"
            )

        try:
            logger.info("Running Locust load testing")
            adapter = self.registry.get_adapter("locust")

            # Execute load tests
            result = adapter.execute(
                target_path=self.config.target_path,
                users=users,
                spawn_rate=spawn_rate,
                run_time=run_time,
                host=host,
                **kwargs,
            )

            # Convert to OperationalMetrics
            metrics = self._extract_metrics_from_locust(result, users, run_time)

            return metrics

        except Exception as e:
            logger.error(f"Load testing failed: {e}")
            raise ToolNotAvailableError(f"Load testing failed: {e}")

    def _extract_metrics_from_locust(
        self, result: Dict[str, Any], users: int, run_time: str
    ) -> OperationalMetrics:
        """Extract operational metrics from Locust results."""
        total_requests = result.get("total_requests", 0)
        failed_requests = result.get("failed_requests", 0)
        avg_response_time = result.get("avg_response_time", 0.0)
        requests_per_second = result.get("requests_per_second", 0.0)

        # Calculate success rate
        success_rate = 0.0
        if total_requests > 0:
            success_rate = ((total_requests - failed_requests) / total_requests) * 100

        # Calculate performance score (0-100)
        # Based on response time and success rate
        performance_score = self._calculate_performance_score(
            avg_response_time, success_rate
        )

        # Determine if system passed operational validation
        passed = success_rate >= 95.0 and avg_response_time < 1000.0

        return OperationalMetrics(
            total_requests=total_requests,
            failed_requests=failed_requests,
            success_rate=round(success_rate, 2),
            avg_response_time_ms=round(avg_response_time, 2),
            max_response_time_ms=round(result.get("max_response_time", 0.0), 2),
            requests_per_second=round(requests_per_second, 2),
            concurrent_users=users,
            test_duration=run_time,
            performance_score=round(performance_score, 2),
            passed_validation=passed,
            tool_name="locust",
        )

    def _calculate_performance_score(
        self, avg_response_time: float, success_rate: float
    ) -> float:
        """
        Calculate overall performance score (0-100).

        Factors:
        - Success rate (60% weight)
        - Response time (40% weight)

        Args:
            avg_response_time: Average response time in ms
            success_rate: Success rate percentage

        Returns:
            Performance score (0-100)
        """
        # Success rate component (60% weight)
        success_component = success_rate * 0.6

        # Response time component (40% weight)
        # Excellent: <100ms = 40, Good: <500ms = 30, Fair: <1000ms = 20
        if avg_response_time < 100:
            time_component = 40.0
        elif avg_response_time < 500:
            time_component = 30.0
        elif avg_response_time < 1000:
            time_component = 20.0
        elif avg_response_time < 2000:
            time_component = 10.0
        else:
            time_component = 0.0

        return success_component + time_component

    def _log_results(self, metrics: OperationalMetrics) -> None:
        """Log operational validation results."""
        logger.info(
            f"Operational validation complete: "
            f"Requests={metrics.total_requests}, "
            f"SuccessRate={metrics.success_rate}%, "
            f"AvgResponseTime={metrics.avg_response_time_ms}ms, "
            f"Score={metrics.performance_score}, "
            f"Tool={metrics.tool_name}"
        )

        # Performance assessment
        if metrics.performance_score >= 90:
            logger.info("✓ Excellent operational performance (score ≥90)")
        elif metrics.performance_score >= 70:
            logger.info("✓ Good operational performance (score 70-90)")
        elif metrics.performance_score >= 50:
            logger.warning("⚠ Fair operational performance (score 50-70)")
        else:
            logger.error("✗ Poor operational performance (score <50)")

        # Validation result
        if metrics.passed_validation:
            logger.info(
                "✓ System passed operational validation "
                "(≥95% success, <1000ms avg response)"
            )
        else:
            logger.warning(
                "⚠ System failed operational validation "
                "(requires ≥95% success AND <1000ms avg response)"
            )

        # Specific warnings
        if metrics.success_rate < 95.0:
            logger.warning(f"Low success rate: {metrics.success_rate}% (target: ≥95%)")

        if metrics.avg_response_time_ms > 1000.0:
            logger.warning(
                f"Slow response time: {metrics.avg_response_time_ms}ms (target: <1000ms)"
            )

        if metrics.max_response_time_ms > 5000.0:
            logger.error(
                f"Very slow max response: {metrics.max_response_time_ms}ms (>5s)"
            )
