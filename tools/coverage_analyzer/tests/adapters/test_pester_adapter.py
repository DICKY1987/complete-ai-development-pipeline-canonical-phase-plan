"""Tests for Pester adapter."""
DOC_ID: DOC-TEST-ADAPTERS-TEST-PESTER-ADAPTER-365

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from coverage_analyzer.adapters.base_adapter import ToolExecutionError
from coverage_analyzer.adapters.pester_adapter import PesterAdapter


class TestPesterAdapter:
    """Tests for PesterAdapter class."""

    def test_initialization(self):
        adapter = PesterAdapter()
        assert adapter.tool_name == "pwsh"

    def test_get_tool_name(self):
        adapter = PesterAdapter()
        assert adapter._get_tool_name() == "pwsh"

    def test_generate_pester_script(self):
        """Test Pester script generation."""
        adapter = PesterAdapter()

        script = adapter._generate_pester_script(
            test_path="./tests", code_coverage_paths=["./src/*.ps1"]
        )

        assert "New-PesterConfiguration" in script
        assert "CodeCoverage.Enabled = $true" in script
        assert "./tests" in script
        assert "./src/*.ps1" in script
        assert "ConvertTo-Json" in script

    @patch("coverage_analyzer.adapters.pester_adapter.PesterAdapter._run_command")
    @patch("coverage_analyzer.adapters.pester_adapter.Path.unlink")
    def test_run_pester_success(self, mock_unlink, mock_run_command, tmp_path):
        """Test successful Pester execution."""
        adapter = PesterAdapter()

        # Mock Pester output
        pester_output = {
            "TotalCount": 100,
            "CoveredCount": 85,
            "MissedCount": 15,
            "CoveragePercent": 85.0,
            "MissedCommands": [
                {"File": "test.ps1", "Line": 10, "Command": "Write-Host"}
            ],
            "Files": {},
        }

        # Mock command result
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(pester_output)
        mock_result.stderr = ""
        mock_run_command.return_value = mock_result

        # Execute
        result = adapter._run_pester("script content", tmp_path)

        # Verify
        assert result["TotalCount"] == 100
        assert result["CoveredCount"] == 85
        assert result["CoveragePercent"] == 85.0

    @patch("coverage_analyzer.adapters.pester_adapter.PesterAdapter._run_command")
    def test_run_pester_no_output(self, mock_run_command, tmp_path):
        """Test Pester execution with no output."""
        adapter = PesterAdapter()

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_run_command.return_value = mock_result

        with pytest.raises(ToolExecutionError, match="No output from Pester"):
            adapter._run_pester("script", tmp_path)

    def test_parse_pester_coverage(self):
        """Test parsing of Pester coverage data."""
        adapter = PesterAdapter()

        coverage_data = {
            "TotalCount": 100,
            "CoveredCount": 85,
            "MissedCount": 15,
            "CoveragePercent": 85.0,
            "MissedCommands": [
                {"File": "module.ps1", "Line": 42, "Command": "Write-Host"},
                {"File": "module.ps1", "Line": 67, "Command": "Write-Error"},
            ],
            "Files": {
                "module.ps1": {
                    "TotalCommands": 100,
                    "CoveredCommands": 85,
                    "MissedCommands": 15,
                    "MissedLines": [42, 67],
                }
            },
        }

        result = adapter._parse_pester_coverage(coverage_data)

        assert result["line_coverage_percent"] == 85.0
        assert result["branch_coverage_percent"] == 85.0  # Approximation
        assert result["total_lines"] == 100
        assert result["covered_lines"] == 85
        assert 42 in result["uncovered_lines"]
        assert 67 in result["uncovered_lines"]
        assert result["tool_name"] == "pester"

    def test_parse_pester_coverage_empty(self):
        """Test parsing with no coverage data."""
        adapter = PesterAdapter()

        coverage_data = {
            "TotalCount": 0,
            "CoveredCount": 0,
            "CoveragePercent": 0.0,
            "MissedCommands": [],
            "Files": {},
        }

        result = adapter._parse_pester_coverage(coverage_data)

        assert result["line_coverage_percent"] == 0.0
        assert result["total_lines"] == 0
        assert result["uncovered_lines"] == []

    @patch("subprocess.run")
    def test_is_tool_available_true(self, mock_run):
        """Test tool availability check when Pester is installed."""
        adapter = PesterAdapter()

        mock_result = Mock()
        mock_result.stdout = "Pester 5.3.1"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        assert adapter.is_tool_available() is True

    @patch("subprocess.run")
    def test_is_tool_available_false(self, mock_run):
        """Test tool availability check when Pester is not installed."""
        adapter = PesterAdapter()

        mock_result = Mock()
        mock_result.stdout = ""
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        assert adapter.is_tool_available() is False

    @patch("subprocess.run")
    def test_is_tool_available_error(self, mock_run):
        """Test tool availability check when PowerShell is not available."""
        adapter = PesterAdapter()

        mock_run.side_effect = FileNotFoundError()

        assert adapter.is_tool_available() is False
