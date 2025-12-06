"""
Adapter for mutmut - Python mutation testing tool.

mutmut generates mutants (code variations) and runs tests to verify
if the tests catch the mutations.
"""
DOC_ID: DOC-SCRIPT-ADAPTERS-MUTMUT-ADAPTER-814

import json
import re
from pathlib import Path
from typing import Any, Dict

from .base_adapter import BaseAdapter, ToolExecutionError


class MutmutAdapter(BaseAdapter):
    """
    Adapter for mutmut mutation testing tool.

    mutmut applies mutations to code and checks if tests detect them.
    Higher mutation scores indicate better test quality.
    """

    def _get_tool_name(self) -> str:
        return "mutmut"

    def execute(self, target_path: str, **kwargs) -> Dict[str, Any]:
        """
        Execute mutmut mutation testing.

        Args:
            target_path: Path to Python code to test
            **kwargs: Optional arguments:
                - test_command: Command to run tests (default: pytest)
                - paths_to_mutate: Specific paths to mutate
                - runner: Test runner (pytest, unittest, etc.)

        Returns:
            Dictionary with mutation metrics:
                - total_mutants: int
                - killed_mutants: int
                - survived_mutants: int
                - timeout_mutants: int
                - suspicious_mutants: int
                - mutation_score: float (0-100)

        Raises:
            ToolExecutionError: If mutmut execution fails
        """
        path = self.validate_target_path(target_path)

        test_command = kwargs.get("test_command", "pytest -x")
        paths_to_mutate = kwargs.get("paths_to_mutate", str(path))

        # Run mutmut
        results = self._run_mutmut(paths_to_mutate, test_command)

        # Parse and return metrics
        return self._parse_mutmut_results(results)

    def _run_mutmut(self, paths: str, test_command: str) -> Dict[str, Any]:
        """Run mutmut mutation testing."""
        # First, run mutmut to generate and test mutations
        # This can take a long time, so we use a high timeout
        cmd = [
            "mutmut",
            "run",
            "--paths-to-mutate",
            paths,
            "--runner",
            test_command,
            "--no-progress",  # Disable progress bar for clean output
        ]

        # Run mutation testing
        result = self._run_command(cmd, timeout=600, check=False)

        # Get results summary
        summary_cmd = ["mutmut", "results"]
        summary_result = self._run_command(summary_cmd, timeout=30)

        # Get JSON results if available
        json_cmd = ["mutmut", "junitxml"]
        try:
            json_result = self._run_command(json_cmd, timeout=30, check=False)
            junit_xml = json_result.stdout
        except Exception:
            junit_xml = ""

        return {
            "summary": summary_result.stdout,
            "junit_xml": junit_xml,
            "exit_code": result.returncode,
        }

    def _parse_mutmut_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Parse mutmut results into MutationMetrics format."""
        summary = results.get("summary", "")

        # Parse summary text
        # Example: "Killed: 45, Survived: 5, Timeout: 2, Suspicious: 1"
        killed = self._extract_count(summary, r"Killed[:\s]+(\d+)")
        survived = self._extract_count(summary, r"Survived[:\s]+(\d+)")
        timeout = self._extract_count(summary, r"Timeout[:\s]+(\d+)")
        suspicious = self._extract_count(summary, r"Suspicious[:\s]+(\d+)")
        skipped = self._extract_count(summary, r"Skipped[:\s]+(\d+)")

        total = killed + survived + timeout + suspicious

        # Calculate mutation score
        # Mutation score = killed / (total - skipped - timeout)
        testable = total - skipped - timeout
        if testable > 0:
            mutation_score = (killed / testable) * 100
        else:
            mutation_score = 0.0

        # Effective mutants are those that were actually testable
        effective_mutants = killed + survived

        return {
            "total_mutants": total,
            "killed_mutants": killed,
            "survived_mutants": survived,
            "timeout_mutants": timeout,
            "suspicious_mutants": suspicious,
            "skipped_mutants": skipped,
            "mutation_score": round(mutation_score, 2),
            "effective_mutants": effective_mutants,
            "test_effectiveness": round(
                (killed / effective_mutants * 100) if effective_mutants > 0 else 0.0, 2
            ),
            "tool_name": "mutmut",
        }

    def _extract_count(self, text: str, pattern: str) -> int:
        """Extract count from text using regex pattern."""
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 0

    def clean_cache(self) -> None:
        """Clean mutmut cache (.mutmut-cache)."""
        try:
            cmd = ["mutmut", "clean-cache"]
            self._run_command(cmd, timeout=10)
        except Exception:
            pass  # Ignore cleanup errors
