"""
Adapter for pip-audit - Official Python security vulnerability scanner.

pip-audit is the official PyPA tool for scanning Python packages for known
vulnerabilities using the OSV database.


DOC_ID: DOC-SCRIPT-ADAPTERS-PIP-AUDIT-ADAPTER-810
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from .base_adapter import BaseAdapter, ToolExecutionError


class PipAuditAdapter(BaseAdapter):
    """
    Adapter for pip-audit vulnerability scanner.

    pip-audit is the official PyPA (Python Packaging Authority) tool for
    auditing Python environments and requirements files.
    """

    def _get_tool_name(self) -> str:
        return "pip-audit"

    def execute(self, target_path: str, **kwargs) -> Dict[str, Any]:
        """
        Execute pip-audit vulnerability scan.

        Args:
            target_path: Path to Python project
            **kwargs: Optional arguments:
                - requirements_file: Path to requirements file
                - scan_environment: Scan installed packages (default: False)
                - ignore_vulns: List of vulnerability IDs to ignore

        Returns:
            Dictionary with SCA metrics

        Raises:
            ToolExecutionError: If pip-audit execution fails
        """
        path = self.validate_target_path(target_path)

        requirements_file = kwargs.get("requirements_file")
        scan_environment = kwargs.get("scan_environment", False)
        ignore_vulns = kwargs.get("ignore_vulns", [])

        # Find requirements file if scanning file
        if not scan_environment and not requirements_file:
            requirements_file = self._find_requirements_file(path)

        # Run pip-audit
        results = self._run_pip_audit(requirements_file, scan_environment, ignore_vulns)

        # Parse and return metrics
        return self._parse_pip_audit_results(results)

    def _find_requirements_file(self, path: Path) -> Path:
        """Find requirements file in project."""
        candidates = [
            path / "requirements.txt",
            path / "requirements" / "base.txt",
            path / "requirements" / "production.txt",
            path / "pyproject.toml",
        ]

        for candidate in candidates:
            if candidate.exists():
                return candidate

        raise ToolExecutionError(f"No requirements file found in {path}")

    def _run_pip_audit(
        self,
        requirements_file: Path = None,
        scan_environment: bool = False,
        ignore_vulns: List[str] = None,
    ) -> Dict[str, Any]:
        """Run pip-audit scanner."""
        cmd = ["pip-audit", "--format", "json"]

        if scan_environment:
            # Scan currently installed packages
            pass  # Default behavior
        elif requirements_file:
            cmd.extend(["-r", str(requirements_file)])

        # Add ignore list
        if ignore_vulns:
            for vuln_id in ignore_vulns:
                cmd.extend(["--ignore-vuln", vuln_id])

        result = self._run_command(cmd, timeout=180)

        # pip-audit returns non-zero if vulnerabilities found
        if not result.stdout:
            # No vulnerabilities
            return {"dependencies": [], "vulnerabilities": []}

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise ToolExecutionError(f"Failed to parse pip-audit output: {e}")

    def _parse_pip_audit_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Parse pip-audit results into SCAMetrics format."""
        dependencies = results.get("dependencies", [])
        vulnerabilities = results.get("vulnerabilities", [])

        # Count vulnerable packages
        vulnerable_packages = set()

        vulnerability_details = []
        critical_count = 0
        high_count = 0
        medium_count = 0
        low_count = 0

        for vuln in vulnerabilities:
            package_name = vuln.get("name", "unknown")
            vulnerable_packages.add(package_name)

            # pip-audit provides severity via aliases field or CVSS score
            aliases = vuln.get("aliases", [])

            # Determine severity from CVE/GHSA data
            # pip-audit uses OSV format which may include severity
            severity = "medium"  # Default

            # Check for GHSA (GitHub Security Advisory) which includes severity
            for alias in aliases:
                if "GHSA" in alias or "CVE" in alias:
                    # For now, use heuristic based on fix availability
                    if vuln.get("fix_versions"):
                        severity = "high"  # Fixable = high priority
                    else:
                        severity = "medium"  # No fix = still concerning

            # Count by severity
            if severity == "critical":
                critical_count += 1
            elif severity == "high":
                high_count += 1
            elif severity == "medium":
                medium_count += 1
            else:
                low_count += 1

            vulnerability_details.append(
                {
                    "package": package_name,
                    "installed_version": vuln.get("version", "unknown"),
                    "vulnerable_spec": "",  # Not provided by pip-audit
                    "fixed_versions": vuln.get("fix_versions", []),
                    "cve": ", ".join(aliases),
                    "severity": severity,
                    "advisory": vuln.get("description", "")[:200],
                }
            )

        total_deps = len(dependencies) if dependencies else len(vulnerable_packages) * 2

        # Calculate security score
        deductions = (
            critical_count * 25 + high_count * 15 + medium_count * 8 + low_count * 3
        )
        security_score = max(0, 100 - deductions)

        return {
            "total_dependencies": total_deps,
            "vulnerable_dependencies": len(vulnerable_packages),
            "vulnerabilities": vulnerability_details[:50],
            "security_score": round(security_score, 2),
            "critical_vulnerabilities": critical_count,
            "high_vulnerabilities": high_count,
            "medium_vulnerabilities": medium_count,
            "low_vulnerabilities": low_count,
            "tool_name": "pip-audit",
        }
