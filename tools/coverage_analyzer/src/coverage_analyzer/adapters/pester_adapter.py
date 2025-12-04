"""
Adapter for Pester - PowerShell structural coverage analysis.

Wraps Pester's code coverage functionality to provide coverage metrics
for PowerShell scripts.
"""

import json
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, Optional

from .base_adapter import BaseAdapter, ToolExecutionError


class PesterAdapter(BaseAdapter):
    """
    Adapter for Pester PowerShell testing framework.

    Executes Pester with code coverage enabled and returns structured
    metrics compatible with StructuralCoverageMetrics.
    """

    def _get_tool_name(self) -> str:
        return "pwsh"  # PowerShell Core

    def execute(self, target_path: str, **kwargs) -> Dict[str, Any]:
        """
        Execute Pester with code coverage and return parsed results.

        Args:
            target_path: Path to PowerShell code to analyze
            **kwargs: Optional arguments:
                - test_path: Path to test files (default: target_path/tests)
                - code_coverage_path: Specific files to measure

        Returns:
            Dictionary with coverage metrics (same format as coverage.py adapter)

        Raises:
            ToolExecutionError: If Pester execution fails
        """
        path = self.validate_target_path(target_path)

        test_path = kwargs.get("test_path", path / "tests")
        code_coverage_path = kwargs.get("code_coverage_path", [str(path / "*.ps1")])

        # Generate Pester script
        pester_script = self._generate_pester_script(
            test_path=str(test_path), code_coverage_paths=code_coverage_path
        )

        try:
            # Execute Pester with coverage
            coverage_data = self._run_pester(pester_script, path)

            # Parse and return metrics
            return self._parse_pester_coverage(coverage_data)

        except Exception as e:
            raise ToolExecutionError(f"Pester execution failed: {e}")

    def _generate_pester_script(self, test_path: str, code_coverage_paths: list) -> str:
        """Generate PowerShell script to run Pester with coverage."""
        # Convert paths to PowerShell array syntax
        coverage_paths_str = ", ".join([f"'{p}'" for p in code_coverage_paths])

        script = f"""
        $config = New-PesterConfiguration
        $config.Run.Path = '{test_path}'
        $config.CodeCoverage.Enabled = $true
        $config.CodeCoverage.Path = @({coverage_paths_str})
        $config.Output.Verbosity = 'Detailed'

        $result = Invoke-Pester -Configuration $config

        # Output coverage data as JSON
        $coverageData = @{{
            TotalCount = $result.CodeCoverage.CommandsAnalyzedCount
            CoveredCount = $result.CodeCoverage.CommandsExecutedCount
            MissedCount = $result.CodeCoverage.CommandsMissedCount
            CoveragePercent = $result.CodeCoverage.CoveragePercent
            MissedCommands = $result.CodeCoverage.MissedCommands | Select-Object -First 100 File, Line, Command
            Files = @{{}}
        }}

        # Group by file
        $result.CodeCoverage.AnalyzedFiles | ForEach-Object {{
            $file = $_
            $fileMissed = $result.CodeCoverage.MissedCommands | Where-Object {{ $_.File -eq $file }}
            $fileHit = $result.CodeCoverage.HitCommands | Where-Object {{ $_.File -eq $file }}

            $coverageData.Files[$file] = @{{
                TotalCommands = ($fileMissed.Count + $fileHit.Count)
                CoveredCommands = $fileHit.Count
                MissedCommands = $fileMissed.Count
                MissedLines = ($fileMissed | ForEach-Object {{ $_.Line }})
            }}
        }}

        $coverageData | ConvertTo-Json -Depth 5
        """

        return script

    def _run_pester(self, script: str, cwd: Path) -> Dict[str, Any]:
        """Execute Pester script and capture coverage data."""
        # Write script to temp file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".ps1", delete=False, encoding="utf-8"
        ) as f:
            f.write(script)
            script_path = f.name

        try:
            # Run PowerShell script
            cmd = ["pwsh", "-NoProfile", "-File", script_path]
            result = self._run_command(cmd, cwd=cwd, timeout=300)

            if not result.stdout:
                raise ToolExecutionError("No output from Pester")

            # Parse JSON output
            coverage_data = json.loads(result.stdout)
            return coverage_data

        finally:
            # Cleanup temp script
            try:
                Path(script_path).unlink()
            except Exception:
                pass

    def _parse_pester_coverage(self, coverage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Pester coverage data into our metrics format."""
        total_commands = coverage_data.get("TotalCount", 0)
        covered_commands = coverage_data.get("CoveredCount", 0)
        coverage_percent = coverage_data.get("CoveragePercent", 0.0)

        # PowerShell doesn't have branch coverage, so we approximate
        # with command coverage
        missed_commands = coverage_data.get("MissedCommands", [])
        uncovered_lines = [cmd.get("Line", 0) for cmd in missed_commands]

        files_data = coverage_data.get("Files", {})

        return {
            "line_coverage_percent": round(coverage_percent, 2),
            "branch_coverage_percent": round(coverage_percent, 2),  # Approximation
            "function_coverage_percent": 0.0,  # Not tracked by Pester
            "total_lines": total_commands,
            "covered_lines": covered_commands,
            "total_branches": 0,  # Not tracked by Pester
            "covered_branches": 0,
            "total_functions": 0,
            "covered_functions": 0,
            "uncovered_lines": uncovered_lines[:100],
            "files": files_data,
            "tool_name": "pester",
        }

    def is_tool_available(self) -> bool:
        """Check if PowerShell and Pester are available."""
        try:
            # Check PowerShell
            result = subprocess.run(
                ["pwsh", "-Command", "Get-Module -ListAvailable Pester"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return "Pester" in result.stdout
        except (FileNotFoundError, subprocess.SubprocessError):
            return False
