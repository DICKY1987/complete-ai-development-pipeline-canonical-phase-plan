"""
Static Analysis Analyzer - Layer 0.

Orchestrates static code analysis (SAST) using multiple tools
before any test execution.


DOC_ID: DOC-SCRIPT-ANALYZERS-STATIC-ANALYSIS-801
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..adapters.base_adapter import ToolNotAvailableError
from ..base import AnalysisConfiguration, StaticAnalysisMetrics
from ..registry import get_registry

logger = logging.getLogger(__name__)


class StaticAnalysisAnalyzer:
    """
    Layer 0 analyzer for static code analysis and security testing (SAST).

    Executes pre-execution analysis using language-specific tools to identify
    code quality issues, security vulnerabilities, and maintainability concerns.
    """

    def __init__(self, config: AnalysisConfiguration):
        """
        Initialize the static analysis analyzer.

        Args:
            config: Analysis configuration
        """
        self.config = config
        self.registry = get_registry()

    def analyze(self) -> StaticAnalysisMetrics:
        """
        Execute static analysis.

        Returns:
            StaticAnalysisMetrics with aggregated results

        Raises:
            ToolNotAvailableError: If no static analysis tools are available
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

    def _analyze_python(self) -> StaticAnalysisMetrics:
        """Analyze Python code using multiple static analysis tools."""
        logger.info("Running Python static analysis")

        # Try tools in order of preference
        tools_to_try = ["prospector", "radon", "bandit", "mypy"]
        available_tools = self._get_available_tools(tools_to_try)

        if not available_tools:
            raise ToolNotAvailableError(
                "No Python static analysis tools available. "
                "Install: pip install prospector radon bandit mypy"
            )

        # Run available tools and aggregate results
        results = []
        for tool_name in available_tools:
            try:
                logger.info(f"Running {tool_name}")
                adapter = self.registry.get_adapter(tool_name)
                result = adapter.execute(
                    target_path=self.config.target_path,
                    mode="static",  # For dual-use adapters like radon
                )
                results.append(result)
            except Exception as e:
                logger.warning(f"Tool {tool_name} failed: {e}")
                continue

        # Aggregate results
        metrics = self._aggregate_results(results)
        self._log_results(metrics)

        return metrics

    def _analyze_powershell(self) -> StaticAnalysisMetrics:
        """Analyze PowerShell code using PSScriptAnalyzer."""
        logger.info("Running PowerShell static analysis")

        try:
            adapter = self.registry.get_adapter("psscriptanalyzer")
        except KeyError:
            raise ToolNotAvailableError(
                "PSScriptAnalyzer adapter not registered. "
                "Install: Install-Module -Name PSScriptAnalyzer"
            )

        # Execute analysis
        result = adapter.execute(
            target_path=self.config.target_path, mode="static", severity="Warning"
        )

        # Convert to metrics object
        metrics = StaticAnalysisMetrics(
            code_quality_score=result["code_quality_score"],
            total_issues=result["total_issues"],
            issues_by_severity=result["issues_by_severity"],
            security_vulnerabilities=result["security_vulnerabilities"],
            type_errors=result["type_errors"],
            maintainability_index=result["maintainability_index"],
            high_complexity_functions=result["high_complexity_functions"],
            tool_name=result["tool_name"],
        )

        self._log_results(metrics)
        return metrics

    def _get_available_tools(self, tool_names: List[str]) -> List[str]:
        """Get list of available tools from registry."""
        available = []
        for name in tool_names:
            if self.registry.is_adapter_available(name):
                available.append(name)
        return available

    def _aggregate_results(self, results: List[Dict]) -> StaticAnalysisMetrics:
        """Aggregate results from multiple tools."""
        if not results:
            # Return empty metrics if no results
            return StaticAnalysisMetrics(
                code_quality_score=0.0,
                total_issues=0,
                issues_by_severity={"high": 0, "medium": 0, "low": 0},
                tool_name="none",
            )

        # Use first result as base
        base = results[0]

        # For multiple results, take weighted average
        if len(results) > 1:
            total_score = sum(r.get("code_quality_score", 0) for r in results)
            avg_score = total_score / len(results)

            # Aggregate issue counts
            total_issues = sum(r.get("total_issues", 0) for r in results)

            # Merge severity counts
            merged_severity = {"high": 0, "medium": 0, "low": 0}
            for r in results:
                for severity, count in r.get("issues_by_severity", {}).items():
                    merged_severity[severity] = merged_severity.get(severity, 0) + count

            # Merge security vulnerabilities
            security_vulns = max(r.get("security_vulnerabilities", 0) for r in results)

            # Merge type errors
            type_errors = max(r.get("type_errors", 0) for r in results)

            # Get best maintainability index
            mi_values = [
                r.get("maintainability_index", 0)
                for r in results
                if r.get("maintainability_index", 0) > 0
            ]
            maintainability_index = (
                sum(mi_values) / len(mi_values) if mi_values else 0.0
            )

            # Merge high complexity functions
            high_complexity = []
            for r in results:
                high_complexity.extend(r.get("high_complexity_functions", []))
            high_complexity = list(set(high_complexity))[:20]  # Dedupe and limit

            tool_names = "+".join([r.get("tool_name", "unknown") for r in results])

        else:
            # Single result
            avg_score = base.get("code_quality_score", 0)
            total_issues = base.get("total_issues", 0)
            merged_severity = base.get("issues_by_severity", {})
            security_vulns = base.get("security_vulnerabilities", 0)
            type_errors = base.get("type_errors", 0)
            maintainability_index = base.get("maintainability_index", 0.0)
            high_complexity = base.get("high_complexity_functions", [])
            tool_names = base.get("tool_name", "unknown")

        return StaticAnalysisMetrics(
            code_quality_score=round(avg_score, 2),
            total_issues=total_issues,
            issues_by_severity=merged_severity,
            security_vulnerabilities=security_vulns,
            type_errors=type_errors,
            maintainability_index=round(maintainability_index, 2),
            high_complexity_functions=high_complexity,
            tool_name=tool_names,
        )

    def _log_results(self, metrics: StaticAnalysisMetrics) -> None:
        """Log static analysis results."""
        logger.info(
            f"Static analysis complete: "
            f"Score={metrics.code_quality_score}, "
            f"Issues={metrics.total_issues}, "
            f"Security={metrics.security_vulnerabilities}, "
            f"Tool={metrics.tool_name}"
        )

        # Check for critical issues
        if (
            self.config.fail_on_critical_security
            and metrics.security_vulnerabilities > 0
        ):
            logger.error(
                f"Found {metrics.security_vulnerabilities} security vulnerabilities "
                f"(fail_on_critical_security=True)"
            )

        high_severity = metrics.issues_by_severity.get("high", 0)
        if high_severity > 0:
            logger.warning(f"Found {high_severity} high-severity issues")
