"""
Mutation Testing Analyzer - Layer 2.

Orchestrates mutation testing to assess test suite quality by
introducing intentional bugs and verifying tests catch them.


DOC_ID: DOC-SCRIPT-ANALYZERS-MUTATION-802
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..adapters.base_adapter import ToolNotAvailableError
from ..base import AnalysisConfiguration, MutationMetrics
from ..registry import get_registry

logger = logging.getLogger(__name__)


class MutationAnalyzer:
    """
    Layer 2 analyzer for mutation testing.

    Executes mutation testing to measure test suite effectiveness by
    introducing code mutations and checking if tests detect them.
    """

    def __init__(self, config: AnalysisConfiguration):
        """
        Initialize the mutation analyzer.

        Args:
            config: Analysis configuration
        """
        self.config = config
        self.registry = get_registry()

    def analyze(self) -> MutationMetrics:
        """
        Execute mutation testing.

        Returns:
            MutationMetrics with mutation testing results

        Raises:
            ToolNotAvailableError: If no mutation testing tools are available
            ValueError: If language is not supported
        """
        language = self.config.language.lower()

        if language == "python":
            return self._analyze_python()
        elif language == "powershell":
            # PowerShell doesn't have mature mutation testing tools yet
            logger.warning(
                "Mutation testing not fully supported for PowerShell, returning empty metrics"
            )
            return MutationMetrics(
                total_mutants=0,
                killed_mutants=0,
                survived_mutants=0,
                timeout_mutants=0,
                mutation_score=0.0,
                tool_name="none",
            )
        else:
            raise ValueError(f"Unsupported language: {language}. " f"Supported: python")

    def _analyze_python(self) -> MutationMetrics:
        """Analyze Python code using mutation testing."""
        logger.info("Running Python mutation testing")

        # Try tools in order of preference
        tools_to_try = ["mutmut"]  # mutmut is most popular and reliable
        available_tools = self._get_available_tools(tools_to_try)

        if not available_tools:
            raise ToolNotAvailableError(
                "No Python mutation testing tools available. "
                "Install: pip install mutmut"
            )

        # Run the first available tool
        tool_name = available_tools[0]

        try:
            logger.info(f"Running {tool_name}")
            adapter = self.registry.get_adapter(tool_name)

            # Execute mutation testing
            result = adapter.execute(target_path=self.config.target_path)

            # Convert to metrics object
            metrics = MutationMetrics(
                total_mutants=result["total_mutants"],
                killed_mutants=result["killed_mutants"],
                survived_mutants=result["survived_mutants"],
                timeout_mutants=result.get("timeout_mutants", 0),
                mutation_score=result["mutation_score"],
                tool_name=result["tool_name"],
            )

            self._log_results(metrics)
            return metrics

        except Exception as e:
            logger.error(f"Tool {tool_name} failed: {e}")
            raise ToolNotAvailableError(f"Mutation testing failed: {e}")

    def _get_available_tools(self, tool_names: List[str]) -> List[str]:
        """Get list of available tools from registry."""
        available = []
        for name in tool_names:
            if self.registry.is_adapter_available(name):
                available.append(name)
        return available

    def _log_results(self, metrics: MutationMetrics) -> None:
        """Log mutation testing results."""
        logger.info(
            f"Mutation testing complete: "
            f"Total={metrics.total_mutants}, "
            f"Killed={metrics.killed_mutants}, "
            f"Survived={metrics.survived_mutants}, "
            f"Score={metrics.mutation_score}%, "
            f"Tool={metrics.tool_name}"
        )

        # Assess test quality based on mutation score
        if metrics.mutation_score >= 80:
            logger.info("✓ Excellent test quality (≥80% mutation score)")
        elif metrics.mutation_score >= 60:
            logger.warning("⚠ Good test quality (60-80% mutation score)")
        elif metrics.mutation_score >= 40:
            logger.warning(
                "⚠ Fair test quality (40-60% mutation score) - consider improving tests"
            )
        else:
            logger.error(
                "✗ Poor test quality (<40% mutation score) - tests need significant improvement"
            )

        # Log surviving mutants warning
        if metrics.survived_mutants > 0:
            logger.warning(
                f"{metrics.survived_mutants} mutants survived - these indicate weak test coverage"
            )

        # Log timeout mutants
        if metrics.timeout_mutants > 0:
            logger.info(
                f"{metrics.timeout_mutants} mutants timed out - may indicate infinite loops"
            )
