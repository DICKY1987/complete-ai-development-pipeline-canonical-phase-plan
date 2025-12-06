"""
Complexity Analyzer - Layer 3.

Orchestrates complexity analysis to measure code maintainability,
cyclomatic complexity, and cognitive complexity.
"""
DOC_ID: DOC-SCRIPT-ANALYZERS-COMPLEXITY-805

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..adapters.base_adapter import ToolNotAvailableError
from ..base import AnalysisConfiguration, ComplexityMetrics
from ..registry import get_registry

logger = logging.getLogger(__name__)


class ComplexityAnalyzer:
    """
    Layer 3 analyzer for code complexity.

    Executes complexity analysis to measure code maintainability
    using cyclomatic complexity, cognitive complexity, and
    maintainability index metrics.
    """

    def __init__(self, config: AnalysisConfiguration):
        """
        Initialize the complexity analyzer.

        Args:
            config: Analysis configuration
        """
        self.config = config
        self.registry = get_registry()

    def analyze(self) -> ComplexityMetrics:
        """
        Execute complexity analysis.

        Returns:
            ComplexityMetrics with complexity analysis results

        Raises:
            ToolNotAvailableError: If no complexity tools are available
            ValueError: If language is not supported
        """
        language = self.config.language.lower()

        if language == "python":
            return self._analyze_python()
        elif language == "powershell":
            return self._analyze_powershell()
        else:
            raise ValueError(
                f"Unsupported language: {language}. " f"Supported: python, powershell"
            )

    def _analyze_python(self) -> ComplexityMetrics:
        """Analyze Python code using complexity tools."""
        logger.info("Running Python complexity analysis")

        # Radon is the primary tool for Python complexity
        if not self.registry.is_adapter_available("radon"):
            raise ToolNotAvailableError(
                "Radon not available. Install: pip install radon"
            )

        try:
            logger.info("Running radon complexity analysis")
            adapter = self.registry.get_adapter("radon")

            # Execute complexity analysis
            result = adapter.execute(target_path=self.config.target_path)

            # Extract complexity data from radon results
            metrics = self._extract_complexity_from_radon(result)

            self._log_results(metrics)
            return metrics

        except Exception as e:
            logger.error(f"Radon failed: {e}")
            raise ToolNotAvailableError(f"Complexity analysis failed: {e}")

    def _analyze_powershell(self) -> ComplexityMetrics:
        """Analyze PowerShell code using complexity tools."""
        logger.info("Running PowerShell complexity analysis")

        # PSScriptAnalyzer provides some complexity metrics
        if not self.registry.is_adapter_available("psscriptanalyzer"):
            raise ToolNotAvailableError(
                "PSScriptAnalyzer not available. Install from PowerShell Gallery"
            )

        try:
            logger.info("Running PSScriptAnalyzer complexity analysis")
            adapter = self.registry.get_adapter("psscriptanalyzer")

            # Execute complexity analysis
            result = adapter.execute(target_path=self.config.target_path)

            # Extract complexity data from PSSA results
            metrics = self._extract_complexity_from_pssa(result)

            self._log_results(metrics)
            return metrics

        except Exception as e:
            logger.error(f"PSScriptAnalyzer failed: {e}")
            raise ToolNotAvailableError(f"Complexity analysis failed: {e}")

    def _extract_complexity_from_radon(
        self, result: Dict[str, Any]
    ) -> ComplexityMetrics:
        """Extract complexity metrics from radon output."""
        # Radon provides complexity in its results
        # Average over all functions/modules

        functions_analyzed = result.get("functions_analyzed", 0)
        total_complexity = result.get("total_complexity", 0)
        max_complexity = result.get("max_complexity", 0)
        maintainability_index = result.get("maintainability_index", 100.0)

        # Calculate averages
        avg_complexity = (
            total_complexity / functions_analyzed if functions_analyzed > 0 else 0.0
        )

        # High complexity functions (>10 is generally considered high)
        high_complexity_count = result.get("high_complexity_count", 0)

        return ComplexityMetrics(
            average_complexity=round(avg_complexity, 2),
            max_complexity=max_complexity,
            functions_above_threshold=high_complexity_count,
            total_independent_paths=functions_analyzed,
            tool_name="radon",
        )

    def _extract_complexity_from_pssa(
        self, result: Dict[str, Any]
    ) -> ComplexityMetrics:
        """Extract complexity metrics from PSScriptAnalyzer output."""
        # PSSA doesn't provide as detailed complexity metrics as radon
        # We estimate based on issue counts and severity

        total_issues = result.get("total_issues", 0)
        error_count = result.get("error_count", 0)
        warning_count = result.get("warning_count", 0)

        # Estimate maintainability index based on issues
        # Start at 100, subtract points for issues
        maintainability_index = 100.0
        maintainability_index -= error_count * 5  # Errors are serious
        maintainability_index -= warning_count * 2  # Warnings less so
        maintainability_index = max(0.0, maintainability_index)

        # Estimate complexity based on issues
        # This is a rough approximation
        estimated_complexity = total_issues / 10.0 if total_issues > 0 else 1.0

        return ComplexityMetrics(
            average_complexity=round(estimated_complexity, 2),
            max_complexity=int(estimated_complexity * 2),
            functions_above_threshold=error_count,
            total_independent_paths=max(1, total_issues // 2),
            tool_name="psscriptanalyzer",
        )

    def _log_results(self, metrics: ComplexityMetrics) -> None:
        """Log complexity analysis results."""
        logger.info(
            f"Complexity analysis complete: "
            f"AvgComplexity={metrics.average_complexity}, "
            f"MaxComplexity={metrics.max_complexity}, "
            f"HighComplexityFunctions={metrics.functions_above_threshold}, "
            f"Tool={metrics.tool_name}"
        )

        # Assess code quality based on metrics
        if metrics.average_complexity <= 5:
            logger.info("✓ Excellent complexity (avg ≤5)")
        elif metrics.average_complexity <= 10:
            logger.warning("⚠ Good complexity (avg 5-10)")
        elif metrics.average_complexity <= 15:
            logger.warning("⚠ Fair complexity (avg 10-15) - consider refactoring")
        else:
            logger.error("✗ High complexity (avg >15) - urgent refactoring needed")

        # Warn about high complexity
        if metrics.average_complexity > 10:
            logger.warning(
                f"Average complexity ({metrics.average_complexity}) is high (>10)"
            )

        if metrics.max_complexity > 20:
            logger.error(
                f"Max complexity ({metrics.max_complexity}) is very high (>20) - "
                f"refactor the most complex functions"
            )

        if metrics.functions_above_threshold > 0:
            logger.warning(
                f"{metrics.functions_above_threshold} functions have high complexity (>10)"
            )
