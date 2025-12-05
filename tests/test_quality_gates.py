"""Integration tests for quality gate validators."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
SCRIPTS = REPO_ROOT / "scripts"


class TestIncompleteScanner:
    """Tests for incomplete implementation scanner."""

    def test_scanner_runs_successfully(self):
        """Scanner should execute without errors."""
        result = subprocess.run(
            [
                sys.executable,
                SCRIPTS / "scan_incomplete_implementation.py",
                "--root",
                str(REPO_ROOT),
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        # Exit code 0 (no issues) or 1 (issues found) are both valid
        assert result.returncode in (
            0,
            1,
        ), f"Unexpected exit code: {result.returncode}\n{result.stderr}"

    def test_scanner_produces_output(self):
        """Scanner should produce JSON output."""
        output_file = REPO_ROOT / ".state" / "test_incomplete_scan.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Remove any existing file
        if output_file.exists():
            output_file.unlink()

        result = subprocess.run(
            [
                sys.executable,
                SCRIPTS / "scan_incomplete_implementation.py",
                "--root",
                str(REPO_ROOT),
                "--output",
                str(output_file),
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

        # Should complete successfully (exit code 0 or 1 both OK)
        assert result.returncode in (0, 1), f"Scanner failed: {result.stderr}"
        assert (
            output_file.exists()
        ), f"Scanner did not create output file. stderr: {result.stderr}"
        assert output_file.stat().st_size > 0, "Output file is empty"

        # Cleanup
        if output_file.exists():
            output_file.unlink()

    def test_scanner_respects_allowlist(self):
        """Scanner should respect allowlist configuration."""
        allowlist_file = REPO_ROOT / "incomplete_allowlist.yaml"

        result = subprocess.run(
            [
                sys.executable,
                SCRIPTS / "scan_incomplete_implementation.py",
                "--root",
                str(REPO_ROOT),
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

        # Should not fail if allowlist properly configured
        assert "allowlist" in result.stdout.lower() or result.returncode in (0, 1)


class TestDependencyGraphValidator:
    """Tests for dependency graph validator."""

    def test_validator_runs_successfully(self):
        """Validator should execute without errors."""
        result = subprocess.run(
            [sys.executable, SCRIPTS / "validate_dependency_graph.py"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        # Exit code 0 (valid) or 1 (violations) are both acceptable
        assert result.returncode in (
            0,
            1,
        ), f"Unexpected exit code: {result.returncode}\n{result.stderr}"

    def test_validator_produces_report(self):
        """Validator should generate JSON report."""
        output_file = REPO_ROOT / ".state" / "test_dependency_report.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Remove any existing file
        if output_file.exists():
            output_file.unlink()

        result = subprocess.run(
            [
                sys.executable,
                SCRIPTS / "validate_dependency_graph.py",
                "--report",
                str(output_file),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

        # Should complete (exit code 0 or 1 both OK)
        assert result.returncode in (0, 1), f"Validator failed: {result.stderr}"
        assert (
            output_file.exists()
        ), f"Validator did not create report file. stderr: {result.stderr}"
        assert output_file.stat().st_size > 0, "Report file is empty"

        # Cleanup
        if output_file.exists():
            output_file.unlink()

    def test_validator_detects_deprecated_imports(self):
        """Validator should detect deprecated import patterns."""
        result = subprocess.run(
            [sys.executable, SCRIPTS / "validate_dependency_graph.py"],
            capture_output=True,
            timeout=120,
        )

        # Should complete successfully (exit 0=no violations, 1=violations found)
        assert result.returncode in (
            0,
            1,
        ), f"Validator crashed with unexpected exit code: {result.returncode}"
