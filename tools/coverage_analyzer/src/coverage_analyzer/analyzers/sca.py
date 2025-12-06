"""
Software Composition Analysis (SCA) Analyzer - Layer 0.5.

Orchestrates dependency security scanning to identify vulnerabilities
in third-party libraries and packages.
"""
DOC_ID: DOC-SCRIPT-ANALYZERS-SCA-803

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..adapters.base_adapter import ToolNotAvailableError
from ..base import AnalysisConfiguration, SCAMetrics
from ..registry import get_registry

logger = logging.getLogger(__name__)


class SCAAnalyzer:
    """
    Layer 0.5 analyzer for Software Composition Analysis.

    Scans project dependencies for known security vulnerabilities using
    CVE databases and security advisories.
    """

    def __init__(self, config: AnalysisConfiguration):
        """
        Initialize the SCA analyzer.

        Args:
            config: Analysis configuration
        """
        self.config = config
        self.registry = get_registry()

    def analyze(self) -> SCAMetrics:
        """
        Execute SCA analysis.

        Returns:
            SCAMetrics with vulnerability data

        Raises:
            ToolNotAvailableError: If no SCA tools are available
            ValueError: If language is not supported
        """
        language = self.config.language.lower()

        if language == "python":
            return self._analyze_python()
        elif language == "powershell":
            # PowerShell doesn't have mature SCA tooling yet
            logger.warning(
                "SCA not fully supported for PowerShell, returning empty metrics"
            )
            return SCAMetrics(
                total_dependencies=0,
                vulnerable_dependencies=0,
                security_score=100.0,
                tool_name="none",
            )
        else:
            raise ValueError(f"Unsupported language: {language}. " f"Supported: python")

    def _analyze_python(self) -> SCAMetrics:
        """Analyze Python dependencies using SCA tools."""
        logger.info("Running Python SCA analysis")

        # Try tools in order of preference
        tools_to_try = ["pip-audit", "safety"]
        available_tools = self._get_available_tools(tools_to_try)

        if not available_tools:
            raise ToolNotAvailableError(
                "No Python SCA tools available. "
                "Install: pip install pip-audit safety"
            )

        # Run the first available tool
        # (Running multiple SCA tools often duplicates findings)
        tool_name = available_tools[0]

        try:
            logger.info(f"Running {tool_name}")
            adapter = self.registry.get_adapter(tool_name)
            result = adapter.execute(target_path=self.config.target_path)

            # Convert to metrics object
            vulnerabilities_by_severity = {
                "critical": result.get("critical_vulnerabilities", 0),
                "high": result.get("high_vulnerabilities", 0),
                "medium": result.get("medium_vulnerabilities", 0),
                "low": result.get("low_vulnerabilities", 0),
            }

            metrics = SCAMetrics(
                total_dependencies=result["total_dependencies"],
                vulnerable_dependencies=result["vulnerable_dependencies"],
                vulnerabilities_by_severity=vulnerabilities_by_severity,
                cve_details=result.get("vulnerabilities", []),
                security_score=result["security_score"],
                tool_name=result["tool_name"],
            )

            self._log_results(metrics)
            return metrics

        except Exception as e:
            logger.error(f"Tool {tool_name} failed: {e}")
            raise ToolNotAvailableError(f"SCA scan failed: {e}")

    def _get_available_tools(self, tool_names: List[str]) -> List[str]:
        """Get list of available tools from registry."""
        available = []
        for name in tool_names:
            if self.registry.is_adapter_available(name):
                available.append(name)
        return available

    def _log_results(self, metrics: SCAMetrics) -> None:
        """Log SCA results."""
        logger.info(
            f"SCA complete: "
            f"Dependencies={metrics.total_dependencies}, "
            f"Vulnerable={metrics.vulnerable_dependencies}, "
            f"Score={metrics.security_score}, "
            f"Tool={metrics.tool_name}"
        )

        # Log warnings for vulnerabilities
        if metrics.vulnerabilities_by_severity.get("critical", 0) > 0:
            logger.error(
                f"Found {metrics.vulnerabilities_by_severity.get("critical", 0)} CRITICAL vulnerabilities!"
            )

        if metrics.vulnerabilities_by_severity.get("high", 0) > 0:
            logger.warning(
                f"Found {metrics.vulnerabilities_by_severity.get("high", 0)} HIGH severity vulnerabilities"
            )

        if metrics.vulnerable_dependencies > 0:
            logger.warning(
                f"{metrics.vulnerable_dependencies} packages have known vulnerabilities"
            )

        # Check fail_on_critical_security
        if self.config.fail_on_critical_security:
            total_critical = metrics.vulnerabilities_by_severity.get(
                "critical", 0
            ) + metrics.vulnerabilities_by_severity.get("high", 0)
            if total_critical > 0:
                logger.error(
                    f"Failing due to {total_critical} critical/high vulnerabilities "
                    f"(fail_on_critical_security=True)"
                )
