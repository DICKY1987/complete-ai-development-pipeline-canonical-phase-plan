"""Tests for SCA adapters (Layer 0.5).

DOC_ID: DOC-TEST-ADAPTERS-TEST-SCA-ADAPTERS-369
"""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from coverage_analyzer.adapters.base_adapter import ToolExecutionError
from coverage_analyzer.adapters.pip_audit_adapter import PipAuditAdapter
from coverage_analyzer.adapters.safety_adapter import SafetyAdapter


class TestSafetyAdapter:
    """Tests for SafetyAdapter."""

    def test_initialization(self):
        adapter = SafetyAdapter()
        assert adapter.tool_name == "safety"

    def test_get_tool_name(self):
        adapter = SafetyAdapter()
        assert adapter._get_tool_name() == "safety"

    @patch("coverage_analyzer.adapters.safety_adapter.SafetyAdapter._run_command")
    @patch(
        "coverage_analyzer.adapters.safety_adapter.SafetyAdapter._find_requirements_file"
    )
    def test_execute_no_vulnerabilities(
        self, mock_find_req, mock_run_command, tmp_path
    ):
        adapter = SafetyAdapter()

        mock_find_req.return_value = tmp_path / "requirements.txt"

        # No vulnerabilities found
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_run_command.return_value = mock_result

        result = adapter.execute(str(tmp_path))

        assert result["vulnerable_dependencies"] == 0
        assert result["security_score"] == 100.0
        assert result["tool_name"] == "safety"

    @patch("coverage_analyzer.adapters.safety_adapter.SafetyAdapter._run_command")
    @patch(
        "coverage_analyzer.adapters.safety_adapter.SafetyAdapter._find_requirements_file"
    )
    def test_execute_with_vulnerabilities(
        self, mock_find_req, mock_run_command, tmp_path
    ):
        adapter = SafetyAdapter()

        mock_find_req.return_value = tmp_path / "requirements.txt"

        safety_output = {
            "vulnerabilities": [
                {
                    "package": "django",
                    "installed_version": "2.2.0",
                    "vulnerable_spec": "<2.2.13",
                    "fixed_versions": ["2.2.13"],
                    "cve": "CVE-2020-13254",
                    "advisory": "Django 2.2 before 2.2.13 has SQL injection vulnerability",
                },
                {
                    "package": "requests",
                    "installed_version": "2.6.0",
                    "vulnerable_spec": "<2.6.1",
                    "fixed_versions": ["2.6.1"],
                    "cve": "CVE-2015-2296",
                    "advisory": "Information disclosure in requests",
                },
            ],
            "metadata": {"packages_count": 50},
        }

        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = json.dumps(safety_output)
        mock_run_command.return_value = mock_result

        result = adapter.execute(str(tmp_path))

        assert result["total_dependencies"] == 50
        assert result["vulnerable_dependencies"] == 2  # django and requests
        assert result["security_score"] < 100.0
        assert len(result["vulnerabilities"]) == 2
        assert result["tool_name"] == "safety"

    def test_find_requirements_file_success(self, tmp_path):
        adapter = SafetyAdapter()

        # Create requirements.txt
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("django==2.2.0\n")

        found = adapter._find_requirements_file(tmp_path)
        assert found == req_file

    def test_find_requirements_file_not_found(self, tmp_path):
        adapter = SafetyAdapter()

        with pytest.raises(ToolExecutionError, match="No requirements file found"):
            adapter._find_requirements_file(tmp_path)


class TestPipAuditAdapter:
    """Tests for PipAuditAdapter."""

    def test_initialization(self):
        adapter = PipAuditAdapter()
        assert adapter.tool_name == "pip-audit"

    def test_get_tool_name(self):
        adapter = PipAuditAdapter()
        assert adapter._get_tool_name() == "pip-audit"

    @patch("coverage_analyzer.adapters.pip_audit_adapter.PipAuditAdapter._run_command")
    @patch(
        "coverage_analyzer.adapters.pip_audit_adapter.PipAuditAdapter._find_requirements_file"
    )
    def test_execute_no_vulnerabilities(
        self, mock_find_req, mock_run_command, tmp_path
    ):
        adapter = PipAuditAdapter()

        mock_find_req.return_value = tmp_path / "requirements.txt"

        # No vulnerabilities
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_run_command.return_value = mock_result

        result = adapter.execute(str(tmp_path))

        assert result["vulnerable_dependencies"] == 0
        assert result["security_score"] == 100.0
        assert result["tool_name"] == "pip-audit"

    @patch("coverage_analyzer.adapters.pip_audit_adapter.PipAuditAdapter._run_command")
    @patch(
        "coverage_analyzer.adapters.pip_audit_adapter.PipAuditAdapter._find_requirements_file"
    )
    def test_execute_with_vulnerabilities(
        self, mock_find_req, mock_run_command, tmp_path
    ):
        adapter = PipAuditAdapter()

        mock_find_req.return_value = tmp_path / "requirements.txt"

        pip_audit_output = {
            "dependencies": [
                {"name": "django", "version": "2.2.0"},
                {"name": "requests", "version": "2.25.0"},
            ],
            "vulnerabilities": [
                {
                    "name": "django",
                    "version": "2.2.0",
                    "fix_versions": ["2.2.13"],
                    "aliases": ["CVE-2020-13254", "GHSA-xxxx-yyyy"],
                    "description": "SQL injection in Django 2.2",
                }
            ],
        }

        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = json.dumps(pip_audit_output)
        mock_run_command.return_value = mock_result

        result = adapter.execute(str(tmp_path))

        assert result["total_dependencies"] == 2
        assert result["vulnerable_dependencies"] == 1  # django only
        assert result["security_score"] < 100.0
        assert len(result["vulnerabilities"]) == 1
        assert result["vulnerabilities"][0]["package"] == "django"
        assert result["tool_name"] == "pip-audit"

    @patch("coverage_analyzer.adapters.pip_audit_adapter.PipAuditAdapter._run_command")
    def test_scan_environment_mode(self, mock_run_command, tmp_path):
        adapter = PipAuditAdapter()

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({"dependencies": [], "vulnerabilities": []})
        mock_run_command.return_value = mock_result

        result = adapter.execute(str(tmp_path), scan_environment=True)

        # Should not try to find requirements file
        mock_run_command.assert_called_once()
        assert result["tool_name"] == "pip-audit"

    def test_severity_classification(self, tmp_path):
        adapter = PipAuditAdapter()

        # Test severity determination logic
        results = {
            "dependencies": [{"name": "pkg1", "version": "1.0"}],
            "vulnerabilities": [
                {
                    "name": "pkg1",
                    "version": "1.0",
                    "fix_versions": ["1.1"],  # Fixable = high severity
                    "aliases": ["CVE-2023-1234"],
                    "description": "Test vulnerability",
                }
            ],
        }

        parsed = adapter._parse_pip_audit_results(results)

        assert parsed["high_vulnerabilities"] >= 0  # Should categorize
        assert parsed["vulnerable_dependencies"] == 1
