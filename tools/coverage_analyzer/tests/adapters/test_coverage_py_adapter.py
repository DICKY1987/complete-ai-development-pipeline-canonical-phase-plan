"""Tests for coverage.py adapter."""

import json
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from coverage_analyzer.adapters.base_adapter import ToolExecutionError
from coverage_analyzer.adapters.coverage_py_adapter import CoveragePyAdapter


class TestCoveragePyAdapter:
    """Tests for CoveragePyAdapter class."""

    def test_initialization(self):
        adapter = CoveragePyAdapter()
        assert adapter.tool_name == "coverage"

    def test_get_tool_name(self):
        adapter = CoveragePyAdapter()
        assert adapter._get_tool_name() == "coverage"

    @patch(
        "coverage_analyzer.adapters.coverage_py_adapter.CoveragePyAdapter._run_command"
    )
    @patch("coverage_analyzer.adapters.coverage_py_adapter.Path.exists")
    @patch("builtins.open")
    def test_execute_success(
        self,
        mock_open,
        mock_exists,
        mock_run_command,
        sample_python_project,
        mock_coverage_py_output,
    ):
        """Test successful coverage.py execution."""
        adapter = CoveragePyAdapter()

        # Mock file system
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(
            mock_coverage_py_output
        )

        # Mock command execution
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run_command.return_value = mock_result

        # Execute
        result = adapter.execute(str(sample_python_project))

        # Verify
        assert "line_coverage_percent" in result
        assert "branch_coverage_percent" in result
        assert result["tool_name"] == "coverage.py"
        assert isinstance(result["total_lines"], int)

    def test_execute_invalid_path(self):
        """Test execution with invalid path."""
        adapter = CoveragePyAdapter()

        with pytest.raises(ValueError, match="does not exist"):
            adapter.execute("/nonexistent/path")

    @patch(
        "coverage_analyzer.adapters.coverage_py_adapter.CoveragePyAdapter._run_command"
    )
    def test_generate_json_report_failure(
        self, mock_run_command, sample_python_project
    ):
        """Test failure to generate JSON report."""
        adapter = CoveragePyAdapter()

        # Mock failed command
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Coverage data not found"
        mock_run_command.return_value = mock_result

        with pytest.raises(ToolExecutionError, match="Failed to generate"):
            adapter._generate_json_report(sample_python_project)

    def test_parse_coverage_report(self, mock_coverage_py_output):
        """Test parsing of coverage.py JSON output."""
        adapter = CoveragePyAdapter()

        result = adapter._parse_coverage_report(mock_coverage_py_output)

        assert result["line_coverage_percent"] == 90.0
        assert result["total_lines"] == 50
        assert result["covered_lines"] == 45
        assert "files" in result
        assert result["tool_name"] == "coverage.py"

    def test_parse_coverage_report_no_branches(self):
        """Test parsing when no branches exist."""
        adapter = CoveragePyAdapter()

        report_data = {
            "totals": {
                "num_statements": 100,
                "covered_lines": 90,
                "percent_covered": 90.0,
                "num_branches": 0,
                "covered_branches": 0,
            },
            "files": {},
        }

        result = adapter._parse_coverage_report(report_data)

        # Should have 100% branch coverage when no branches exist
        assert result["branch_coverage_percent"] == 100.0

    def test_cleanup_coverage_files(self, tmp_path):
        """Test cleanup of temporary coverage files."""
        adapter = CoveragePyAdapter()

        # Create dummy files
        (tmp_path / ".coverage").touch()
        (tmp_path / "coverage.json").touch()

        adapter._cleanup_coverage_files(tmp_path)

        # Files should be removed
        assert not (tmp_path / ".coverage").exists()
        assert not (tmp_path / "coverage.json").exists()
