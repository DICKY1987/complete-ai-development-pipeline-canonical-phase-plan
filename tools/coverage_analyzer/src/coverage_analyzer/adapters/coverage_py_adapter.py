"""
Adapter for coverage.py - Python structural coverage analysis.

Wraps coverage.py to provide statement, branch, and function coverage metrics.
"""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from .base_adapter import BaseAdapter, ToolExecutionError


class CoveragePyAdapter(BaseAdapter):
    """
    Adapter for coverage.py tool.

    Executes coverage.py to analyze Python code coverage and returns
    structured metrics compatible with StructuralCoverageMetrics.
    """

    def _get_tool_name(self) -> str:
        return "coverage"

    def execute(self, target_path: str, **kwargs) -> Dict[str, Any]:
        """
        Execute coverage.py and return parsed results.

        Args:
            target_path: Path to Python code to analyze
            **kwargs: Optional arguments:
                - test_command: Command to run tests (default: "pytest")
                - source_dirs: List of source directories to measure
                - omit_patterns: Patterns to omit from coverage

        Returns:
            Dictionary with coverage metrics:
                - line_coverage_percent: float
                - branch_coverage_percent: float
                - function_coverage_percent: float
                - total_lines: int
                - covered_lines: int
                - total_branches: int
                - covered_branches: int
                - uncovered_lines: List[int]
                - files: Dict[str, Any] - per-file coverage data

        Raises:
            ToolExecutionError: If coverage.py execution fails
        """
        path = self.validate_target_path(target_path)

        test_command = kwargs.get("test_command", "pytest")
        source_dirs = kwargs.get("source_dirs", [str(path)])
        omit_patterns = kwargs.get("omit_patterns", [])

        # Create temporary coverage config
        coverage_config = self._create_coverage_config(source_dirs, omit_patterns)

        try:
            # Step 1: Run tests with coverage
            self._run_coverage(test_command, path, coverage_config)

            # Step 2: Generate JSON report
            report_data = self._generate_json_report(path)

            # Step 3: Parse and return metrics
            return self._parse_coverage_report(report_data)

        finally:
            # Cleanup
            self._cleanup_coverage_files(path)

    def _create_coverage_config(
        self, source_dirs: list, omit_patterns: list
    ) -> Optional[str]:
        """Create a temporary .coveragerc configuration."""
        # For simplicity, return None and use command-line args
        # In production, could write a temp config file
        return None

    def _run_coverage(
        self, test_command: str, cwd: Path, config: Optional[str]
    ) -> None:
        """Run tests with coverage measurement."""
        # Build coverage command
        cmd = ["coverage", "run", "--branch", "-m"]
        cmd.extend(test_command.split())

        result = self._run_command(cmd, cwd=cwd, timeout=300)

        if result.returncode != 0:
            # Tests may have failed, but coverage data might still be valid
            # Log warning but continue
            pass

    def _generate_json_report(self, cwd: Path) -> Dict[str, Any]:
        """Generate JSON coverage report."""
        cmd = ["coverage", "json", "-o", "coverage.json"]

        result = self._run_command(cmd, cwd=cwd)

        if result.returncode != 0:
            raise ToolExecutionError(
                f"Failed to generate coverage report: {result.stderr}"
            )

        # Read the JSON report
        report_file = cwd / "coverage.json"
        if not report_file.exists():
            raise ToolExecutionError("Coverage JSON report not generated")

        with open(report_file, "r") as f:
            return json.load(f)

    def _parse_coverage_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse coverage.py JSON report into our metrics format."""
        totals = report_data.get("totals", {})
        files_data = report_data.get("files", {})

        # Calculate metrics
        total_statements = totals.get("num_statements", 0)
        covered_lines = totals.get("covered_lines", 0)
        missing_lines = totals.get("missing_lines", 0)

        # Branch coverage
        total_branches = totals.get("num_branches", 0)
        covered_branches = totals.get("covered_branches", 0)

        # Line coverage percentage
        line_coverage = totals.get("percent_covered", 0.0)

        # Branch coverage percentage
        if total_branches > 0:
            branch_coverage = (covered_branches / total_branches) * 100
        else:
            branch_coverage = 100.0  # No branches means 100% branch coverage

        # Function coverage (approximate from files)
        total_functions = 0
        covered_functions = 0
        all_uncovered_lines = []

        for file_path, file_data in files_data.items():
            summary = file_data.get("summary", {})
            missing = summary.get("missing_lines", [])
            if isinstance(missing, list):
                all_uncovered_lines.extend(missing)

            # Estimate functions (coverage.py doesn't track this directly)
            # For now, use a heuristic or set to 0

        return {
            "line_coverage_percent": round(line_coverage, 2),
            "branch_coverage_percent": round(branch_coverage, 2),
            "function_coverage_percent": 0.0,  # Not directly available
            "total_lines": total_statements,
            "covered_lines": covered_lines,
            "total_branches": total_branches,
            "covered_branches": covered_branches,
            "total_functions": total_functions,
            "covered_functions": covered_functions,
            "uncovered_lines": all_uncovered_lines[:100],  # Limit to first 100
            "files": files_data,
            "tool_name": "coverage.py",
        }

    def _cleanup_coverage_files(self, cwd: Path) -> None:
        """Remove temporary coverage files."""
        coverage_files = [".coverage", "coverage.json"]
        for file in coverage_files:
            file_path = cwd / file
            if file_path.exists():
                try:
                    file_path.unlink()
                except Exception:
                    pass  # Ignore cleanup errors
