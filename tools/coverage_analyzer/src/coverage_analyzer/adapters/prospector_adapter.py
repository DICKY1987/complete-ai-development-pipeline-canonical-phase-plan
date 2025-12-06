"""
Adapter for Prospector - Python multi-tool static analyzer.

Prospector combines multiple tools (pylint, pyflakes, mccabe, etc.) into
a single comprehensive analysis.
"""
DOC_ID: DOC-SCRIPT-ADAPTERS-PROSPECTOR-ADAPTER-816

import json
from pathlib import Path
from typing import Any, Dict, List

from .base_adapter import BaseAdapter, ToolExecutionError


class ProspectorAdapter(BaseAdapter):
    """
    Adapter for Prospector multi-tool analyzer.

    Runs multiple analysis tools and aggregates results for Layer 0.
    """

    def _get_tool_name(self) -> str:
        return "prospector"

    def execute(self, target_path: str, **kwargs) -> Dict[str, Any]:
        """
        Execute Prospector analysis.

        Args:
            target_path: Path to Python code to analyze
            **kwargs: Optional arguments:
                - strictness: Analysis strictness (veryhigh, high, medium, low, verylow)
                - with_tools: List of tools to enable
                - without_tools: List of tools to disable

        Returns:
            Dictionary with aggregated analysis metrics
        """
        path = self.validate_target_path(target_path)

        strictness = kwargs.get("strictness", "medium")
        with_tools = kwargs.get("with_tools", [])
        without_tools = kwargs.get("without_tools", [])

        # Run Prospector
        results = self._run_prospector(path, strictness, with_tools, without_tools)

        # Parse and return metrics
        return self._parse_prospector_results(results)

    def _run_prospector(
        self,
        path: Path,
        strictness: str,
        with_tools: List[str],
        without_tools: List[str],
    ) -> Dict[str, Any]:
        """Run Prospector analyzer."""
        cmd = [
            "prospector",
            str(path),
            "--output-format",
            "json",
            "--strictness",
            strictness,
        ]

        # Add tool filters
        for tool in with_tools:
            cmd.extend(["--with-tool", tool])

        for tool in without_tools:
            cmd.extend(["--without-tool", tool])

        result = self._run_command(cmd, timeout=180)

        if not result.stdout:
            raise ToolExecutionError("No output from Prospector")

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise ToolExecutionError(f"Failed to parse Prospector output: {e}")

    def _parse_prospector_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Prospector results into StaticAnalysisMetrics format."""
        summary = results.get("summary", {})
        messages = results.get("messages", [])

        # Extract summary counts
        total_issues = summary.get("message_count", 0)

        # Count by severity
        severity_counts = {"high": 0, "medium": 0, "low": 0}
        security_issues = 0
        type_issues = 0
        complexity_issues = []

        for msg in messages:
            # Map Prospector severity to our categories
            source = msg.get("source", "")
            code = msg.get("code", "")
            location = msg.get("location", {})

            # Categorize by source and code
            if source == "pylint":
                if code.startswith("E"):  # Errors
                    severity_counts["high"] += 1
                elif code.startswith("W"):  # Warnings
                    severity_counts["medium"] += 1
                else:
                    severity_counts["low"] += 1

                # Check for security-related issues
                if any(sec in code.lower() for sec in ["sec", "sql", "eval", "exec"]):
                    security_issues += 1

                # Check for type issues
                if "type" in code.lower() or code in ["E1101", "E1103"]:
                    type_issues += 1

            elif source == "mccabe":
                # Complexity issues
                complexity_issues.append(
                    {
                        "function": location.get("function", "unknown"),
                        "file": location.get("path", ""),
                        "line": location.get("line", 0),
                    }
                )
                severity_counts["medium"] += 1

            elif source == "pep8" or source == "pycodestyle":
                severity_counts["low"] += 1

            else:
                # Default to medium
                severity_counts["medium"] += 1

        # Calculate code quality score from Prospector's summary
        # Prospector doesn't provide a direct score, so we calculate it
        deductions = (
            severity_counts["high"] * 5
            + severity_counts["medium"] * 2
            + severity_counts["low"] * 1
        )
        code_quality_score = max(0, 100 - deductions)

        return {
            "code_quality_score": round(code_quality_score, 2),
            "total_issues": total_issues,
            "issues_by_severity": severity_counts,
            "security_vulnerabilities": security_issues,
            "type_errors": type_issues,
            "maintainability_index": 0.0,  # Not directly provided
            "high_complexity_functions": [
                c["function"] for c in complexity_issues[:20]
            ],
            "messages": messages[:100],  # Keep first 100 for details
            "tool_name": "prospector",
        }
