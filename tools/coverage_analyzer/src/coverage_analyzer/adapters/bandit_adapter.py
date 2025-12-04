"""
Adapter for Bandit - Python security vulnerability scanner.

Bandit analyzes Python code for common security issues.
"""

import json
from pathlib import Path
from typing import Any, Dict

from .base_adapter import BaseAdapter, ToolExecutionError


class BanditAdapter(BaseAdapter):
    """
    Adapter for Bandit security scanner.

    Scans Python code for security vulnerabilities and generates
    metrics for Layer 0 (static analysis).
    """

    def _get_tool_name(self) -> str:
        return "bandit"

    def execute(self, target_path: str, **kwargs) -> Dict[str, Any]:
        """
        Execute Bandit security scan.

        Args:
            target_path: Path to Python code to analyze
            **kwargs: Optional arguments:
                - confidence_level: Minimum confidence (LOW, MEDIUM, HIGH)
                - severity_level: Minimum severity (LOW, MEDIUM, HIGH)
                - skip_tests: Skip test files (default: True)

        Returns:
            Dictionary with security metrics
        """
        path = self.validate_target_path(target_path)

        confidence = kwargs.get("confidence_level", "LOW")
        severity = kwargs.get("severity_level", "LOW")
        skip_tests = kwargs.get("skip_tests", True)

        # Run Bandit
        results = self._run_bandit(path, confidence, severity, skip_tests)

        # Parse and return metrics
        return self._parse_bandit_results(results)

    def _run_bandit(
        self, path: Path, confidence: str, severity: str, skip_tests: bool
    ) -> Dict[str, Any]:
        """Run Bandit security scanner."""
        cmd = [
            "bandit",
            "-r",  # Recursive
            str(path),
            "-f",
            "json",  # JSON output
            "-ll",  # Report all severity levels (overridden by severity filter)
        ]

        # Add confidence level
        if confidence == "MEDIUM":
            cmd.append("-i")
        elif confidence == "HIGH":
            cmd.extend(["-i", "-i"])

        # Skip test files
        if skip_tests:
            cmd.extend(["--skip", "B101"])  # Skip assert statements in tests

        result = self._run_command(cmd, timeout=120)

        # Bandit returns non-zero if issues found, but that's expected
        if not result.stdout:
            raise ToolExecutionError("No output from Bandit")

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise ToolExecutionError(f"Failed to parse Bandit output: {e}")

    def _parse_bandit_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Bandit results into StaticAnalysisMetrics format."""
        metrics_data = results.get("metrics", {})
        issues = results.get("results", [])

        # Count issues by severity
        severity_counts = {"high": 0, "medium": 0, "low": 0}
        security_vulnerabilities = 0

        for issue in issues:
            severity = issue.get("issue_severity", "LOW").lower()
            if severity in severity_counts:
                severity_counts[severity] += 1

            # Count as security vulnerability if MEDIUM or HIGH
            if severity in ["medium", "high"]:
                security_vulnerabilities += 1

        total_issues = len(issues)

        # Calculate code quality score
        # Perfect score (100) if no issues
        # Deduct points based on severity
        deductions = (
            severity_counts["high"] * 15
            + severity_counts["medium"] * 8
            + severity_counts["low"] * 3
        )
        code_quality_score = max(0, 100 - deductions)

        # Get lines of code scanned
        total_lines = sum(
            file_metrics.get("SLOC", 0)
            for file_metrics in metrics_data.values()
            if isinstance(file_metrics, dict)
        )

        return {
            "code_quality_score": round(code_quality_score, 2),
            "total_issues": total_issues,
            "issues_by_severity": severity_counts,
            "security_vulnerabilities": security_vulnerabilities,
            "type_errors": 0,  # Bandit doesn't check types
            "maintainability_index": 0.0,  # Not applicable
            "high_complexity_functions": [],  # Not applicable
            "total_lines_scanned": total_lines,
            "issues": issues[:50],  # Keep first 50 for details
            "tool_name": "bandit",
        }
