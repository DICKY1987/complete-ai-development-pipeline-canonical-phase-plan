"""
Structural Coverage Analyzer - Layer 1.

Orchestrates structural coverage analysis (statement + branch coverage)
for both Python and PowerShell code.
"""
DOC_ID: DOC-SCRIPT-ANALYZERS-STRUCTURAL-800

import logging
from pathlib import Path
from typing import Optional

from ..adapters.base_adapter import ToolNotAvailableError
from ..base import AnalysisConfiguration, StructuralCoverageMetrics
from ..registry import get_registry

logger = logging.getLogger(__name__)


class StructuralCoverageAnalyzer:
    """
    Layer 1 analyzer for structural code coverage.

    Executes statement and branch coverage analysis using language-specific
    tools (coverage.py for Python, Pester for PowerShell).
    """

    def __init__(self, config: AnalysisConfiguration):
        """
        Initialize the structural coverage analyzer.

        Args:
            config: Analysis configuration
        """
        self.config = config
        self.registry = get_registry()

    def analyze(self) -> StructuralCoverageMetrics:
        """
        Execute structural coverage analysis.

        Returns:
            StructuralCoverageMetrics with coverage data

        Raises:
            ToolNotAvailableError: If required coverage tool is not available
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

    def _analyze_python(self) -> StructuralCoverageMetrics:
        """Analyze Python code coverage using coverage.py."""
        logger.info("Running Python structural coverage analysis")

        try:
            adapter = self.registry.get_adapter("coverage.py")
        except KeyError:
            raise ToolNotAvailableError(
                "coverage.py adapter not registered. "
                "Run: registry.register('coverage.py', CoveragePyAdapter, '1')"
            )

        # Execute coverage analysis
        result = adapter.execute(
            target_path=self.config.target_path,
            test_command=(
                self.config.structural_tools[0]
                if self.config.structural_tools
                else "pytest"
            ),
        )

        # Convert to metrics object
        metrics = StructuralCoverageMetrics(
            line_coverage_percent=result["line_coverage_percent"],
            branch_coverage_percent=result["branch_coverage_percent"],
            function_coverage_percent=result["function_coverage_percent"],
            total_lines=result["total_lines"],
            covered_lines=result["covered_lines"],
            total_branches=result["total_branches"],
            covered_branches=result["covered_branches"],
            total_functions=result["total_functions"],
            covered_functions=result["covered_functions"],
            uncovered_lines=result["uncovered_lines"],
            tool_name=result["tool_name"],
        )

        self._log_results(metrics)
        return metrics

    def _analyze_powershell(self) -> StructuralCoverageMetrics:
        """Analyze PowerShell code coverage using Pester."""
        logger.info("Running PowerShell structural coverage analysis")

        try:
            adapter = self.registry.get_adapter("pester")
        except KeyError:
            raise ToolNotAvailableError(
                "pester adapter not registered. "
                "Run: registry.register('pester', PesterAdapter, '1')"
            )

        # Execute coverage analysis
        result = adapter.execute(target_path=self.config.target_path)

        # Convert to metrics object
        metrics = StructuralCoverageMetrics(
            line_coverage_percent=result["line_coverage_percent"],
            branch_coverage_percent=result["branch_coverage_percent"],
            function_coverage_percent=result["function_coverage_percent"],
            total_lines=result["total_lines"],
            covered_lines=result["covered_lines"],
            total_branches=result["total_branches"],
            covered_branches=result["covered_branches"],
            total_functions=result["total_functions"],
            covered_functions=result["covered_functions"],
            uncovered_lines=result["uncovered_lines"],
            tool_name=result["tool_name"],
        )

        self._log_results(metrics)
        return metrics

    def _log_results(self, metrics: StructuralCoverageMetrics) -> None:
        """Log coverage analysis results."""
        logger.info(
            f"Coverage analysis complete: "
            f"Line={metrics.line_coverage_percent}%, "
            f"Branch={metrics.branch_coverage_percent}%, "
            f"Tool={metrics.tool_name}"
        )

        # Check against thresholds
        if metrics.line_coverage_percent < self.config.min_line_coverage:
            logger.warning(
                f"Line coverage ({metrics.line_coverage_percent}%) "
                f"below threshold ({self.config.min_line_coverage}%)"
            )

        if metrics.branch_coverage_percent < self.config.min_branch_coverage:
            logger.warning(
                f"Branch coverage ({metrics.branch_coverage_percent}%) "
                f"below threshold ({self.config.min_branch_coverage}%)"
            )
