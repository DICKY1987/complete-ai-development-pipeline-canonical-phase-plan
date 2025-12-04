"""
Adapter for PSScriptAnalyzer - PowerShell static analysis.

PSScriptAnalyzer provides best practice analysis, security scanning,
and code quality checks for PowerShell scripts.

This adapter serves dual purpose for Layer 0 (static analysis) and
Layer 3 (complexity analysis).
"""

import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List

from .base_adapter import BaseAdapter, ToolExecutionError


class PSScriptAnalyzerAdapter(BaseAdapter):
    """
    Adapter for PSScriptAnalyzer (PSSA).

    Supports both static analysis mode (Layer 0) and complexity mode (Layer 3).
    """

    def _get_tool_name(self) -> str:
        return "pwsh"

    def execute(self, target_path: str, **kwargs) -> Dict[str, Any]:
        """
        Execute PSScriptAnalyzer.

        Args:
            target_path: Path to PowerShell code to analyze
            **kwargs: Optional arguments:
                - mode: "static" (Layer 0) or "complexity" (Layer 3)
                - severity: Minimum severity (Error, Warning, Information)
                - include_rules: Specific rules to include
                - exclude_rules: Rules to exclude

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
        """Run static analysis mode (Layer 0)."""
        severity = kwargs.get("severity", "Warning")
        include_rules = kwargs.get("include_rules", [])
        exclude_rules = kwargs.get("exclude_rules", [])

        # Generate PowerShell script
        script = self._generate_static_script(
            path, severity, include_rules, exclude_rules
        )

        # Execute script
        results = self._run_pssa_script(script, path)

        # Parse results
        return self._parse_static_results(results)

    def _analyze_complexity(self, path: Path, **kwargs) -> Dict[str, Any]:
        """Run complexity analysis mode (Layer 3)."""
        # PSScriptAnalyzer doesn't provide cyclomatic complexity directly
        # We approximate using script metrics
        script = self._generate_complexity_script(path)
        results = self._run_pssa_script(script, path)
        return self._parse_complexity_results(results)

    def _generate_static_script(
        self,
        path: Path,
        severity: str,
        include_rules: List[str],
        exclude_rules: List[str],
    ) -> str:
        """Generate PowerShell script for static analysis."""
        include_str = (
            ", ".join([f"'{r}'" for r in include_rules]) if include_rules else ""
        )
        exclude_str = (
            ", ".join([f"'{r}'" for r in exclude_rules]) if exclude_rules else ""
        )

        script = f"""
        $results = Invoke-ScriptAnalyzer -Path '{path}' -Recurse -Severity {severity}
        """

        if include_rules:
            script += f" -IncludeRule @({include_str})"

        if exclude_rules:
            script += f" -ExcludeRule @({exclude_str})"

        script += """

        # Convert to custom object with metrics
        $metrics = @{
            TotalIssues = $results.Count
            BySeverity = @{
                Error = ($results | Where-Object { $_.Severity -eq 'Error' }).Count
                Warning = ($results | Where-Object { $_.Severity -eq 'Warning' }).Count
                Information = ($results | Where-Object { $_.Severity -eq 'Information' }).Count
            }
            SecurityIssues = ($results | Where-Object { $_.RuleName -like '*Security*' }).Count
            Issues = $results | Select-Object -First 100 RuleName, Severity, ScriptName, Line, Message | ForEach-Object {
                @{
                    rule = $_.RuleName
                    severity = $_.Severity.ToString()
                    file = $_.ScriptName
                    line = $_.Line
                    message = $_.Message
                }
            }
        }

        $metrics | ConvertTo-Json -Depth 5
        """

        return script

    def _generate_complexity_script(self, path: Path) -> str:
        """Generate PowerShell script for complexity analysis."""
        script = f"""
        $files = Get-ChildItem -Path '{path}' -Filter *.ps1 -Recurse

        $complexityData = @{{
            Files = @()
            TotalFunctions = 0
            HighComplexityFunctions = @()
        }}

        foreach ($file in $files) {{
            $ast = [System.Management.Automation.Language.Parser]::ParseFile(
                $file.FullName, [ref]$null, [ref]$null
            )

            $functions = $ast.FindAll({{
                $args[0] -is [System.Management.Automation.Language.FunctionDefinitionAst]
            }}, $true)

            $complexityData.TotalFunctions += $functions.Count

            foreach ($func in $functions) {{
                # Simple heuristic: count if/while/for statements as complexity
                $complexity = 1  # Base complexity

                $branches = $func.FindAll({{
                    $args[0] -is [System.Management.Automation.Language.IfStatementAst] -or
                    $args[0] -is [System.Management.Automation.Language.WhileStatementAst] -or
                    $args[0] -is [System.Management.Automation.Language.ForStatementAst] -or
                    $args[0] -is [System.Management.Automation.Language.ForEachStatementAst]
                }}, $true)

                $complexity += $branches.Count

                if ($complexity -gt 10) {{
                    $complexityData.HighComplexityFunctions += @{{
                        name = $func.Name
                        complexity = $complexity
                        file = $file.FullName
                        line = $func.Extent.StartLineNumber
                    }}
                }}
            }}
        }}

        $complexityData | ConvertTo-Json -Depth 5
        """

        return script

    def _run_pssa_script(self, script: str, cwd: Path) -> Dict[str, Any]:
        """Execute PowerShell script and return parsed results."""
        # Write script to temp file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".ps1", delete=False, encoding="utf-8"
        ) as f:
            f.write(script)
            script_path = f.name

        try:
            cmd = ["pwsh", "-NoProfile", "-File", script_path]
            result = self._run_command(cmd, cwd=cwd, timeout=180)

            if not result.stdout:
                raise ToolExecutionError("No output from PSScriptAnalyzer")

            return json.loads(result.stdout)

        finally:
            try:
                Path(script_path).unlink()
            except Exception:
                pass

    def _parse_static_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Parse static analysis results."""
        total_issues = results.get("TotalIssues", 0)
        by_severity = results.get("BySeverity", {})
        security_issues = results.get("SecurityIssues", 0)

        # Map PowerShell severity to our categories
        severity_counts = {
            "high": by_severity.get("Error", 0),
            "medium": by_severity.get("Warning", 0),
            "low": by_severity.get("Information", 0),
        }

        # Calculate code quality score
        deductions = (
            severity_counts["high"] * 10
            + severity_counts["medium"] * 4
            + severity_counts["low"] * 1
        )
        code_quality_score = max(0, 100 - deductions)

        return {
            "code_quality_score": round(code_quality_score, 2),
            "total_issues": total_issues,
            "issues_by_severity": severity_counts,
            "security_vulnerabilities": security_issues,
            "type_errors": 0,  # PSSA doesn't do type checking
            "maintainability_index": 0.0,  # Not directly provided
            "high_complexity_functions": [],  # Use complexity mode for this
            "issues": results.get("Issues", [])[:100],
            "tool_name": "psscriptanalyzer",
        }

    def _parse_complexity_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Parse complexity analysis results."""
        total_functions = results.get("TotalFunctions", 0)
        high_complexity = results.get("HighComplexityFunctions", [])

        # Calculate average complexity (approximation)
        if high_complexity:
            avg_complexity = sum(f["complexity"] for f in high_complexity) / len(
                high_complexity
            )
            max_complexity = max(f["complexity"] for f in high_complexity)
        else:
            avg_complexity = 1.0  # Default low complexity
            max_complexity = 1

        return {
            "average_complexity": round(avg_complexity, 2),
            "max_complexity": max_complexity,
            "functions_above_threshold": len(high_complexity),
            "complex_function_details": high_complexity[:20],
            "total_independent_paths": 0,  # Not available
            "tested_paths": 0,  # Not available
            "path_coverage_percent": 0.0,  # Not available
            "tool_name": "psscriptanalyzer",
        }

    def is_tool_available(self) -> bool:
        """Check if PowerShell and PSScriptAnalyzer are available."""
        try:
            import subprocess

            result = subprocess.run(
                ["pwsh", "-Command", "Get-Module -ListAvailable PSScriptAnalyzer"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return "PSScriptAnalyzer" in result.stdout
        except (FileNotFoundError, subprocess.SubprocessError):
            return False
