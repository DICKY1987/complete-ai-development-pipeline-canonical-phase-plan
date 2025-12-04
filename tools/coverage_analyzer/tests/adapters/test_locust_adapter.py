"""Tests for Locust adapter (Layer 4 - Operational Validation)."""

import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from coverage_analyzer.adapters.base_adapter import ToolNotAvailableError
from coverage_analyzer.adapters.locust_adapter import LocustAdapter


class TestLocustAdapter:
    """Tests for LocustAdapter."""

    def test_initialization(self):
        """Test adapter initialization."""
        adapter = LocustAdapter()
        assert adapter.tool_name == "locust"

    @patch("subprocess.run")
    def test_is_available_true(self, mock_run):
        """Test is_available when Locust is installed."""
        mock_run.return_value = Mock(returncode=0, stdout="Locust 2.15.0\n")

        adapter = LocustAdapter()
        assert adapter.is_available() is True

    @patch("subprocess.run")
    def test_is_available_false(self, mock_run):
        """Test is_available when Locust is not installed."""
        mock_run.side_effect = FileNotFoundError()

        adapter = LocustAdapter()
        assert adapter.is_available() is False

    @patch("subprocess.run")
    def test_is_available_timeout(self, mock_run):
        """Test is_available when command times out."""
        mock_run.side_effect = subprocess.TimeoutExpired("locust", 5)

        adapter = LocustAdapter()
        assert adapter.is_available() is False

    @patch("subprocess.run")
    def test_execute_success(self, mock_run, tmp_path):
        """Test successful load test execution."""
        # Mock version check
        mock_run.side_effect = [
            Mock(returncode=0, stdout="Locust 2.15.0\n"),  # is_available
            Mock(  # execute
                returncode=0,
                stdout="100 requests completed\nMedian response time: 50ms\n",
                stderr="",
            ),
        ]

        adapter = LocustAdapter()
        result = adapter.execute(
            target_path=str(tmp_path), users=10, spawn_rate=2, run_time="10s"
        )

        assert isinstance(result, dict)
        assert "total_requests" in result
        assert "tool_name" in result
        assert result["tool_name"] == "locust"

    @patch("subprocess.run")
    def test_execute_not_available(self, mock_run):
        """Test execute when Locust not available."""
        mock_run.side_effect = FileNotFoundError()

        adapter = LocustAdapter()
        with pytest.raises(ToolNotAvailableError, match="Locust not available"):
            adapter.execute()

    @patch("subprocess.run")
    def test_execute_timeout(self, mock_run, tmp_path):
        """Test execute with timeout."""
        mock_run.side_effect = [
            Mock(returncode=0, stdout="Locust 2.15.0\n"),  # is_available
            subprocess.TimeoutExpired("locust", 300),  # execute times out
        ]

        adapter = LocustAdapter()
        with pytest.raises(ToolNotAvailableError, match="timed out"):
            adapter.execute(target_path=str(tmp_path))

    def test_find_locustfile_explicit(self, tmp_path):
        """Test finding locustfile when path explicitly provided."""
        locustfile = tmp_path / "my_locustfile.py"
        locustfile.write_text("# locustfile")

        adapter = LocustAdapter()
        found = adapter._find_locustfile(str(tmp_path), str(locustfile))

        assert found == locustfile

    def test_find_locustfile_auto_root(self, tmp_path):
        """Test auto-detecting locustfile in root."""
        locustfile = tmp_path / "locustfile.py"
        locustfile.write_text("# locustfile")

        adapter = LocustAdapter()
        found = adapter._find_locustfile(str(tmp_path), None)

        assert found == locustfile

    def test_find_locustfile_auto_tests(self, tmp_path):
        """Test auto-detecting locustfile in tests directory."""
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        locustfile = tests_dir / "locustfile.py"
        locustfile.write_text("# locustfile")

        adapter = LocustAdapter()
        found = adapter._find_locustfile(str(tmp_path), None)

        assert found == locustfile

    def test_find_locustfile_not_found(self, tmp_path):
        """Test when locustfile not found."""
        adapter = LocustAdapter()
        found = adapter._find_locustfile(str(tmp_path), None)

        assert found is None

    def test_create_minimal_locustfile(self, tmp_path):
        """Test creating minimal locustfile."""
        adapter = LocustAdapter()
        locustfile = adapter._create_minimal_locustfile(str(tmp_path))

        assert locustfile.exists()
        assert "HttpUser" in locustfile.read_text()
        assert "task" in locustfile.read_text()

    def test_parse_locust_output_from_stdout(self):
        """Test parsing Locust output from stdout."""
        stdout = """
        Type     Name    # Requests    # Fails    Median    Average    Min    Max
        GET      /          100           2        50         55        10     200
        """
        stderr = ""

        adapter = LocustAdapter()
        metrics = adapter._parse_locust_output(stdout, stderr, None)

        assert metrics["tool_name"] == "locust"
        assert isinstance(metrics["total_requests"], int)
        assert isinstance(metrics["failed_requests"], int)

    def test_parse_csv_stats(self, tmp_path):
        """Test parsing CSV statistics file."""
        csv_content = """Type,Name,Request Count,Failure Count,Median Response Time,Average Response Time,Min Response Time,Max Response Time,Average Content Size,Requests/s,Failures/s,50%,66%,75%,80%,90%,95%,98%,99%,99.9%,99.99%,100%
Aggregated,Aggregated,100,5,50,55.5,10,200,1024,10.5,0.5,50,60,70,80,100,150,180,190,199,200,200
"""
        csv_file = tmp_path / "locust_stats_stats.csv"
        csv_file.write_text(csv_content)

        adapter = LocustAdapter()
        metrics = adapter._parse_csv_stats(csv_file)

        assert metrics["total_requests"] == 100
        assert metrics["failed_requests"] == 5
        assert metrics["avg_response_time"] == 55.5
        assert metrics["requests_per_second"] == 10.5

    @patch("subprocess.run")
    def test_execute_with_custom_params(self, mock_run, tmp_path):
        """Test execute with custom parameters."""
        mock_run.side_effect = [
            Mock(returncode=0, stdout="Locust 2.15.0\n"),  # is_available
            Mock(returncode=0, stdout="", stderr=""),  # execute
        ]

        adapter = LocustAdapter()
        result = adapter.execute(
            target_path=str(tmp_path),
            users=50,
            spawn_rate=5,
            run_time="1m",
            host="http://example.com",
        )

        # Verify command was called with correct params
        call_args = mock_run.call_args_list[1][0][0]
        assert "--users" in call_args
        assert "50" in call_args
        assert "--spawn-rate" in call_args
        assert "5" in call_args
        assert "--run-time" in call_args
        assert "1m" in call_args
        assert "--host" in call_args
        assert "http://example.com" in call_args
