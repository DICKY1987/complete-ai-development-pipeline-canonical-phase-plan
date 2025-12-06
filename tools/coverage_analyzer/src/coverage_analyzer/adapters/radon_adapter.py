"""
Adapter for Radon - Python complexity and maintainability analysis.

Radon provides cyclomatic complexity, maintainability index, and raw metrics.
This adapter serves dual purpose for Layer 0 (static analysis) and Layer 3
(complexity/path coverage).
"""
DOC_ID: DOC-SCRIPT-ADAPTERS-RADON-ADAPTER-809

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_adapter import BaseAdapter, ToolExecutionError


class RadonAdapter(BaseAdapter):
    """
    Adapter for Radon code metrics tool.

    Supports both static analysis mode (Layer 0) and complexity mode (Layer 3).
    """

    def _get_tool_name(self) -> str:
        return "radon"

    def execute(self, target_path: str, **kwargs) -> Dict[str, Any]:
        """
        Execute Radon analysis.

        Args:
            target_path: Path to Python code to analyze
            **kwargs: Optional arguments:
                - mode: "static" (Layer 0) or "complexity" (Layer 3)
                - min_rank: Minimum grade to report (A-F)
                - show_complexity: Include complexity in static mode

        Returns:
            Dictionary with metrics based on mode
        """
        path = self.validate_target_path(target_path)
        mode = kwargs.get("mode", "static")

        if mode == "static":
            return self._analyze_static(path, **kwargs)
        elif mode == "complexity":
            return self._analyze_complexity(path, **kwargs)
        else:
            raise ValueError(f"Invalid mode: {mode}. Use 'static' or 'complexity'")

    def _analyze_static(self, path: Path, **kwargs) -> Dict[str, Any]:
        """
        Run static analysis mode (Layer 0).

        Focuses on code quality and maintainability metrics.
        """
        # Get maintainability index
        mi_results = self._run_maintainability_index(path)

        # Get raw metrics
        raw_results = self._run_raw_metrics(path)

        # Get complexity for high-complexity function detection
        cc_results = self._run_cyclomatic_complexity(path)

        # Parse and combine results
        return self._parse_static_results(mi_results, raw_results, cc_results)

    def _analyze_complexity(self, path: Path, **kwargs) -> Dict[str, Any]:
        """
        Run complexity analysis mode (Layer 3).

        Focuses on cyclomatic complexity and path coverage metrics.
        """
        cc_results = self._run_cyclomatic_complexity(path)
        return self._parse_complexity_results(cc_results)

    def _run_maintainability_index(self, path: Path) -> List[Dict]:
        """Run radon mi (maintainability index)."""
        cmd = ["radon", "mi", str(path), "-s", "-j"]
        result = self._run_command(cmd, timeout=60)

        if result.returncode != 0:
            raise ToolExecutionError(f"Radon MI failed: {result.stderr}")

        try:
            return json.loads(result.stdout) if result.stdout else {}
        except json.JSONDecodeError:
            raise ToolExecutionError("Failed to parse Radon MI output")

    def _run_raw_metrics(self, path: Path) -> Dict[str, Any]:
        """Run radon raw (lines of code metrics)."""
        cmd = ["radon", "raw", str(path), "-s", "-j"]
        result = self._run_command(cmd, timeout=60)

        if result.returncode != 0:
            raise ToolExecutionError(f"Radon raw failed: {result.stderr}")

        try:
            return json.loads(result.stdout) if result.stdout else {}
        except json.JSONDecodeError:
            raise ToolExecutionError("Failed to parse Radon raw output")

    def _run_cyclomatic_complexity(self, path: Path) -> Dict[str, Any]:
        """Run radon cc (cyclomatic complexity)."""
        cmd = ["radon", "cc", str(path), "-s", "-j", "-a"]
        result = self._run_command(cmd, timeout=60)

        if result.returncode != 0:
            raise ToolExecutionError(f"Radon CC failed: {result.stderr}")

        try:
            return json.loads(result.stdout) if result.stdout else {}
        except json.JSONDecodeError:
            raise ToolExecutionError("Failed to parse Radon CC output")

    def _parse_static_results(
        self, mi_results: Dict, raw_results: Dict, cc_results: Dict
    ) -> Dict[str, Any]:
        """Parse results for Layer 0 (static analysis)."""
        # Calculate average maintainability index
        mi_scores = []
        for file_path, data in mi_results.items():
            if isinstance(data, dict) and "mi" in data:
                mi_scores.append(data["mi"])

        avg_mi = sum(mi_scores) / len(mi_scores) if mi_scores else 0.0

        # Count high complexity functions
        high_complexity_functions = []
        total_complexity = 0
        function_count = 0

        for file_path, functions in cc_results.items():
            if isinstance(functions, list):
                for func in functions:
                    complexity = func.get("complexity", 0)
                    total_complexity += complexity
                    function_count += 1

                    if complexity > 10:  # High complexity threshold
                        high_complexity_functions.append(
                            {
                                "name": func.get("name", "unknown"),
                                "complexity": complexity,
                                "file": file_path,
                            }
                        )

        avg_complexity = total_complexity / function_count if function_count > 0 else 0

        # Calculate code quality score (0-100)
        # Based on maintainability index (0-100 scale)
        code_quality_score = avg_mi

        # Count issues (functions with complexity > 10 or MI < 10)
        total_issues = len(high_complexity_functions)
        for file_path, data in mi_results.items():
            if isinstance(data, dict) and data.get("mi", 100) < 10:
                total_issues += 1

        return {
            "code_quality_score": round(code_quality_score, 2),
            "total_issues": total_issues,
            "issues_by_severity": {
                "high": len(
                    [f for f in high_complexity_functions if f["complexity"] > 15]
                ),
                "medium": len(
                    [f for f in high_complexity_functions if 10 < f["complexity"] <= 15]
                ),
                "low": 0,
            },
            "security_vulnerabilities": 0,  # Radon doesn't detect security issues
            "type_errors": 0,  # Radon doesn't do type checking
            "maintainability_index": round(avg_mi, 2),
            "high_complexity_functions": [
                f["name"] for f in high_complexity_functions[:20]
            ],
            "tool_name": "radon",
        }

    def _parse_complexity_results(self, cc_results: Dict) -> Dict[str, Any]:
        """Parse results for Layer 3 (complexity analysis)."""
        total_complexity = 0
        max_complexity = 0
        function_count = 0
        high_complexity_functions = []

        for file_path, functions in cc_results.items():
            if isinstance(functions, list):
                for func in functions:
                    complexity = func.get("complexity", 0)
                    total_complexity += complexity
                    function_count += 1
                    max_complexity = max(max_complexity, complexity)

                    if complexity > 10:
                        high_complexity_functions.append(
                            {
                                "name": func.get("name", "unknown"),
                                "complexity": complexity,
                                "file": file_path,
                                "lineno": func.get("lineno", 0),
                            }
                        )

        avg_complexity = total_complexity / function_count if function_count > 0 else 0

        return {
            "average_complexity": round(avg_complexity, 2),
            "max_complexity": max_complexity,
            "functions_above_threshold": len(high_complexity_functions),
            "complex_function_details": high_complexity_functions[:20],
            "total_independent_paths": total_complexity,  # Approximation
            "tested_paths": 0,  # Not available without test data
            "path_coverage_percent": 0.0,  # Not available without test data
            "tool_name": "radon",
        }
