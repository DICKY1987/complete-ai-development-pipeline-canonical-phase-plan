"""Tests for Layer 0 static analysis adapters.

DOC_ID: DOC-TEST-ADAPTERS-TEST-STATIC-ANALYSIS-ADAPTERS-368
"""

import json
from unittest.mock import Mock, patch

import pytest
from coverage_analyzer.adapters.bandit_adapter import BanditAdapter
from coverage_analyzer.adapters.base_adapter import ToolExecutionError
from coverage_analyzer.adapters.mypy_adapter import MypyAdapter
from coverage_analyzer.adapters.prospector_adapter import ProspectorAdapter
from coverage_analyzer.adapters.pssa_adapter import PSScriptAnalyzerAdapter
from coverage_analyzer.adapters.radon_adapter import RadonAdapter


class TestRadonAdapter:
    """Tests for RadonAdapter."""

    def test_initialization(self):
        adapter = RadonAdapter()
        assert adapter.tool_name == "radon"

    def test_get_tool_name(self):
        adapter = RadonAdapter()
        assert adapter._get_tool_name() == "radon"

    def test_invalid_mode(self, tmp_path):
        adapter = RadonAdapter()
        with pytest.raises(ValueError, match="Invalid mode"):
            adapter.execute(str(tmp_path), mode="invalid")

    @patch("coverage_analyzer.adapters.radon_adapter.RadonAdapter._run_command")
    def test_static_mode_success(self, mock_run_command, tmp_path):
        adapter = RadonAdapter()

        # Mock command results
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({"module.py": {"mi": 75.5, "rank": "A"}})
        mock_run_command.return_value = mock_result

        result = adapter.execute(str(tmp_path), mode="static")

        assert "code_quality_score" in result
        assert "maintainability_index" in result
        assert result["tool_name"] == "radon"

    @patch("coverage_analyzer.adapters.radon_adapter.RadonAdapter._run_command")
    def test_complexity_mode_success(self, mock_run_command, tmp_path):
        adapter = RadonAdapter()

        # Mock CC results
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(
            {
                "module.py": [
                    {"name": "func1", "complexity": 5},
                    {"name": "func2", "complexity": 12},
                ]
            }
        )
        mock_run_command.return_value = mock_result

        result = adapter.execute(str(tmp_path), mode="complexity")

        assert "average_complexity" in result
        assert "max_complexity" in result
        assert "functions_above_threshold" in result
        assert result["tool_name"] == "radon"


class TestBanditAdapter:
    """Tests for BanditAdapter."""

    def test_initialization(self):
        adapter = BanditAdapter()
        assert adapter.tool_name == "bandit"

    @patch("coverage_analyzer.adapters.bandit_adapter.BanditAdapter._run_command")
    def test_execute_success(self, mock_run_command, tmp_path):
        adapter = BanditAdapter()

        bandit_output = {
            "metrics": {},
            "results": [
                {
                    "issue_severity": "HIGH",
                    "issue_text": "SQL injection",
                    "line_number": 42,
                },
                {
                    "issue_severity": "MEDIUM",
                    "issue_text": "Weak crypto",
                    "line_number": 67,
                },
            ],
        }

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(bandit_output)
        mock_run_command.return_value = mock_result

        result = adapter.execute(str(tmp_path))

        assert result["total_issues"] == 2
        assert result["security_vulnerabilities"] == 2  # HIGH + MEDIUM
        assert result["issues_by_severity"]["high"] == 1
        assert result["tool_name"] == "bandit"

    @patch("coverage_analyzer.adapters.bandit_adapter.BanditAdapter._run_command")
    def test_no_issues_perfect_score(self, mock_run_command, tmp_path):
        adapter = BanditAdapter()

        bandit_output = {"metrics": {}, "results": []}

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(bandit_output)
        mock_run_command.return_value = mock_result

        result = adapter.execute(str(tmp_path))

        assert result["code_quality_score"] == 100.0
        assert result["total_issues"] == 0


class TestMypyAdapter:
    """Tests for MypyAdapter."""

    def test_initialization(self):
        adapter = MypyAdapter()
        assert adapter.tool_name == "mypy"

    @patch("coverage_analyzer.adapters.mypy_adapter.MypyAdapter._run_command")
    def test_parse_errors(self, mock_run_command, tmp_path):
        adapter = MypyAdapter()

        mypy_output = """module.py:10:5: error: Incompatible types
module.py:15:10: warning: Unused variable
module.py:20:1: note: See documentation
"""

        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = mypy_output
        mock_result.stderr = ""
        mock_run_command.return_value = mock_result

        result = adapter.execute(str(tmp_path))

        assert result["type_errors"] == 1
        assert result["issues_by_severity"]["high"] == 1  # error
        assert result["issues_by_severity"]["medium"] == 1  # warning
        assert result["tool_name"] == "mypy"

    @patch("coverage_analyzer.adapters.mypy_adapter.MypyAdapter._run_command")
    def test_no_errors_perfect_score(self, mock_run_command, tmp_path):
        adapter = MypyAdapter()

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run_command.return_value = mock_result

        result = adapter.execute(str(tmp_path))

        assert result["code_quality_score"] == 100.0
        assert result["type_errors"] == 0


class TestProspectorAdapter:
    """Tests for ProspectorAdapter."""

    def test_initialization(self):
        adapter = ProspectorAdapter()
        assert adapter.tool_name == "prospector"

    @patch(
        "coverage_analyzer.adapters.prospector_adapter.ProspectorAdapter._run_command"
    )
    def test_execute_success(self, mock_run_command, tmp_path):
        adapter = ProspectorAdapter()

        prospector_output = {
            "summary": {"message_count": 5},
            "messages": [
                {"source": "pylint", "code": "E1101", "location": {}},
                {"source": "pylint", "code": "W0612", "location": {}},
                {"source": "mccabe", "code": "MC0001", "location": {}},
            ],
        }

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(prospector_output)
        mock_run_command.return_value = mock_result

        result = adapter.execute(str(tmp_path))

        assert result["total_issues"] == 5
        assert result["tool_name"] == "prospector"
        assert "code_quality_score" in result


class TestPSScriptAnalyzerAdapter:
    """Tests for PSScriptAnalyzerAdapter."""

    def test_initialization(self):
        adapter = PSScriptAnalyzerAdapter()
        assert adapter.tool_name == "pwsh"

    def test_invalid_mode(self, tmp_path):
        adapter = PSScriptAnalyzerAdapter()
        with pytest.raises(ValueError, match="Invalid mode"):
            adapter.execute(str(tmp_path), mode="invalid")

    @patch(
        "coverage_analyzer.adapters.pssa_adapter.PSScriptAnalyzerAdapter._run_command"
    )
    @patch("coverage_analyzer.adapters.pssa_adapter.Path.unlink")
    def test_static_mode_success(self, mock_unlink, mock_run_command, tmp_path):
        adapter = PSScriptAnalyzerAdapter()

        pssa_output = {
            "TotalIssues": 10,
            "BySeverity": {"Error": 2, "Warning": 5, "Information": 3},
            "SecurityIssues": 1,
            "Issues": [],
        }

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(pssa_output)
        mock_run_command.return_value = mock_result

        result = adapter.execute(str(tmp_path), mode="static")

        assert result["total_issues"] == 10
        assert result["security_vulnerabilities"] == 1
        assert result["issues_by_severity"]["high"] == 2
        assert result["tool_name"] == "psscriptanalyzer"

    @patch(
        "coverage_analyzer.adapters.pssa_adapter.PSScriptAnalyzerAdapter._run_command"
    )
    @patch("coverage_analyzer.adapters.pssa_adapter.Path.unlink")
    def test_complexity_mode_success(self, mock_unlink, mock_run_command, tmp_path):
        adapter = PSScriptAnalyzerAdapter()

        pssa_output = {
            "TotalFunctions": 15,
            "HighComplexityFunctions": [
                {"name": "Test-Function", "complexity": 12, "file": "module.ps1"}
            ],
        }

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(pssa_output)
        mock_run_command.return_value = mock_result

        result = adapter.execute(str(tmp_path), mode="complexity")

        assert result["functions_above_threshold"] == 1
        assert result["tool_name"] == "psscriptanalyzer"

    @patch("subprocess.run")
    def test_is_tool_available_true(self, mock_run):
        adapter = PSScriptAnalyzerAdapter()

        mock_result = Mock()
        mock_result.stdout = "PSScriptAnalyzer 1.20.0"
        mock_run.return_value = mock_result

        assert adapter.is_tool_available() is True

    @patch("subprocess.run")
    def test_is_tool_available_false(self, mock_run):
        adapter = PSScriptAnalyzerAdapter()

        mock_result = Mock()
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        assert adapter.is_tool_available() is False
