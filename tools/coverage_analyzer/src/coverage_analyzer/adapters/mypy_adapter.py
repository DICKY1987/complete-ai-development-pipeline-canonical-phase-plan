"""
Adapter for mypy - Python static type checker.

mypy validates type hints and detects type-related errors.
"""
DOC_ID: DOC-SCRIPT-ADAPTERS-MYPY-ADAPTER-807

import json
import re
from pathlib import Path
from typing import Any, Dict, List

from .base_adapter import BaseAdapter, ToolExecutionError


class MypyAdapter(BaseAdapter):
    """
    Adapter for mypy type checker.

    Analyzes Python code for type errors and generates metrics
    for Layer 0 (static analysis).
    """

    def _get_tool_name(self) -> str:
        return "mypy"

    def execute(self, target_path: str, **kwargs) -> Dict[str, Any]:
        """
        Execute mypy type checking.

        Args:
            target_path: Path to Python code to analyze
            **kwargs: Optional arguments:
                - strict: Use strict mode (default: False)
                - ignore_missing_imports: Ignore missing import errors (default: True)

        Returns:
            Dictionary with type checking metrics
        """
        path = self.validate_target_path(target_path)

        strict = kwargs.get("strict", False)
        ignore_missing = kwargs.get("ignore_missing_imports", True)

        # Run mypy
        output = self._run_mypy(path, strict, ignore_missing)

        # Parse and return metrics
        return self._parse_mypy_results(output)

    def _run_mypy(self, path: Path, strict: bool, ignore_missing: bool) -> str:
        """Run mypy type checker."""
        cmd = [
            "mypy",
            str(path),
            "--show-column-numbers",
            "--no-error-summary",  # We'll parse errors ourselves
        ]

        if strict:
            cmd.append("--strict")

        if ignore_missing:
            cmd.append("--ignore-missing-imports")

        result = self._run_command(cmd, timeout=120)

        # mypy returns non-zero if type errors found
        # Return stdout regardless of exit code
        return result.stdout + result.stderr

    def _parse_mypy_results(self, output: str) -> Dict[str, Any]:
        """Parse mypy output into StaticAnalysisMetrics format."""
        # Parse error lines
        # Format: path/file.py:line:col: error: message
        error_pattern = re.compile(
            r"^(.+?):(\d+):(\d+): (error|warning|note): (.+)$", re.MULTILINE
        )

        errors = []
        warnings = []
        notes = []

        for match in error_pattern.finditer(output):
            file_path, line, col, severity, message = match.groups()

            error_info = {
                "file": file_path,
                "line": int(line),
                "column": int(col),
                "severity": severity,
                "message": message,
            }

            if severity == "error":
                errors.append(error_info)
            elif severity == "warning":
                warnings.append(error_info)
            else:
                notes.append(error_info)

        type_errors = len(errors)
        total_issues = type_errors + len(warnings)

        # Calculate code quality score
        # Perfect score (100) if no errors
        # Deduct 10 points per error, 3 per warning
        deductions = type_errors * 10 + len(warnings) * 3
        code_quality_score = max(0, 100 - deductions)

        return {
            "code_quality_score": round(code_quality_score, 2),
            "total_issues": total_issues,
            "issues_by_severity": {
                "high": type_errors,  # Treat type errors as high severity
                "medium": len(warnings),
                "low": len(notes),
            },
            "security_vulnerabilities": 0,  # mypy doesn't detect security issues
            "type_errors": type_errors,
            "maintainability_index": 0.0,  # Not applicable
            "high_complexity_functions": [],  # Not applicable
            "errors": errors[:50],  # Keep first 50 for details
            "warnings": warnings[:50],
            "tool_name": "mypy",
        }
