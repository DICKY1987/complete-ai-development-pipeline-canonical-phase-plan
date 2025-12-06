"""
Adapter for Safety - Python dependency vulnerability scanner.

Safety checks Python dependencies against a database of known security
vulnerabilities from PyUp.io.


DOC_ID: DOC-SCRIPT-ADAPTERS-SAFETY-ADAPTER-811
"""

import json
from pathlib import Path
from typing import Any, Dict

from .base_adapter import BaseAdapter, ToolExecutionError


class SafetyAdapter(BaseAdapter):
    """
    Adapter for Safety dependency scanner.

    Scans Python dependencies for known vulnerabilities using the Safety
    database (CVE, PyUp advisories).
    """

    def _get_tool_name(self) -> str:
        return "safety"

    def execute(self, target_path: str, **kwargs) -> Dict[str, Any]:
        """
        Execute Safety vulnerability scan.

        Args:
            target_path: Path to Python project (containing requirements.txt or pyproject.toml)
            **kwargs: Optional arguments:
                - requirements_file: Path to requirements file (default: auto-detect)
                - ignore_ids: List of vulnerability IDs to ignore
                - audit_and_monitor: Enable audit mode (default: False)

        Returns:
            Dictionary with SCA metrics:
                - total_dependencies: int
                - vulnerable_dependencies: int
                - vulnerabilities: List[Dict]
                - security_score: float (0-100)

        Raises:
            ToolExecutionError: If Safety execution fails
        """
        path = self.validate_target_path(target_path)

        requirements_file = kwargs.get("requirements_file")
        ignore_ids = kwargs.get("ignore_ids", [])

        # Find requirements file if not specified
        if not requirements_file:
            requirements_file = self._find_requirements_file(path)

        # Run Safety
        results = self._run_safety(requirements_file, ignore_ids)

        # Parse and return metrics
        return self._parse_safety_results(results)

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

        raise ToolExecutionError(
            f"No requirements file found in {path}. "
            "Tried: requirements.txt, pyproject.toml"
        )

    def _run_safety(self, requirements_file: Path, ignore_ids: list) -> Dict[str, Any]:
        """Run Safety vulnerability scanner."""
        cmd = [
            "safety",
            "check",
            "--file",
            str(requirements_file),
            "--json",
            "--output",
            "json",
        ]

        # Add ignore list
        for vuln_id in ignore_ids:
            cmd.extend(["--ignore", str(vuln_id)])

        result = self._run_command(cmd, timeout=120)

        # Safety returns non-zero if vulnerabilities found
        if not result.stdout:
            # No vulnerabilities found
            return {"vulnerabilities": [], "metadata": {}}

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise ToolExecutionError(f"Failed to parse Safety output: {e}")

    def _parse_safety_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Safety results into SCAMetrics format."""
        vulnerabilities = results.get("vulnerabilities", [])

        # Count unique vulnerable packages
        vulnerable_packages = set()
        all_packages = set()

        vulnerability_details = []
        critical_count = 0
        high_count = 0
        medium_count = 0
        low_count = 0

        for vuln in vulnerabilities:
            package_name = vuln.get("package", "unknown")
            vulnerable_packages.add(package_name)

            # Categorize by severity (Safety doesn't provide severity directly)
            # Use CVE scoring or advisory text heuristics
            cve = vuln.get("cve", "")
            advisory = vuln.get("advisory", "")

            # Simple heuristic: check for severity keywords
            if any(
                word in advisory.lower()
                for word in ["critical", "remote code execution", "rce"]
            ):
                severity = "critical"
                critical_count += 1
            elif any(
                word in advisory.lower()
                for word in ["high", "sql injection", "authentication bypass"]
            ):
                severity = "high"
                high_count += 1
            elif any(
                word in advisory.lower()
                for word in ["medium", "moderate", "information disclosure"]
            ):
                severity = "medium"
                medium_count += 1
            else:
                severity = "low"
                low_count += 1

            vulnerability_details.append(
                {
                    "package": package_name,
                    "installed_version": vuln.get("installed_version", "unknown"),
                    "vulnerable_spec": vuln.get("vulnerable_spec", ""),
                    "fixed_versions": vuln.get("fixed_versions", []),
                    "cve": cve,
                    "severity": severity,
                    "advisory": advisory[:200],  # Truncate long advisories
                }
            )

        # Estimate total dependencies from metadata if available
        total_deps = results.get("metadata", {}).get(
            "packages_count", len(vulnerable_packages)
        )
        if total_deps == 0:
            total_deps = len(vulnerable_packages) * 2  # Rough estimate

        # Calculate security score
        # Perfect score (100) if no vulnerabilities
        # Deduct points based on severity
        deductions = (
            critical_count * 25 + high_count * 15 + medium_count * 8 + low_count * 3
        )
        security_score = max(0, 100 - deductions)

        return {
            "total_dependencies": total_deps,
            "vulnerable_dependencies": len(vulnerable_packages),
            "vulnerabilities": vulnerability_details[:50],  # Limit to first 50
            "security_score": round(security_score, 2),
            "critical_vulnerabilities": critical_count,
            "high_vulnerabilities": high_count,
            "medium_vulnerabilities": medium_count,
            "low_vulnerabilities": low_count,
            "tool_name": "safety",
        }
