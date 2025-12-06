"""Tests for mutation testing adapter (Layer 2)."""
DOC_ID: DOC-TEST-ADAPTERS-TEST-MUTATION-ADAPTER-367

from unittest.mock import Mock, patch

import pytest
from coverage_analyzer.adapters.base_adapter import ToolExecutionError
from coverage_analyzer.adapters.mutmut_adapter import MutmutAdapter


class TestMutmutAdapter:
    """Tests for MutmutAdapter."""

    def test_initialization(self):
        adapter = MutmutAdapter()
        assert adapter.tool_name == "mutmut"

    def test_get_tool_name(self):
        adapter = MutmutAdapter()
        assert adapter._get_tool_name() == "mutmut"

    @patch("coverage_analyzer.adapters.mutmut_adapter.MutmutAdapter._run_command")
    def test_execute_success(self, mock_run_command, tmp_path):
        adapter = MutmutAdapter()

        # Mock run command
        run_result = Mock()
        run_result.returncode = 0
        run_result.stdout = ""

        # Mock results command
        results_result = Mock()
        results_result.returncode = 0
        results_result.stdout = (
            "Killed: 45, Survived: 5, Timeout: 2, Suspicious: 1, Skipped: 0"
        )

        # Mock junitxml command
        junit_result = Mock()
        junit_result.returncode = 0
        junit_result.stdout = "<xml>...</xml>"

        mock_run_command.side_effect = [run_result, results_result, junit_result]

        result = adapter.execute(str(tmp_path))

        assert result["total_mutants"] == 53  # 45 + 5 + 2 + 1
        assert result["killed_mutants"] == 45
        assert result["survived_mutants"] == 5
        assert result["timeout_mutants"] == 2
        assert result["suspicious_mutants"] == 1
        assert result["mutation_score"] > 0
        assert result["tool_name"] == "mutmut"

    @patch("coverage_analyzer.adapters.mutmut_adapter.MutmutAdapter._run_command")
    def test_high_mutation_score(self, mock_run_command, tmp_path):
        """Test with high mutation score (good test quality)."""
        adapter = MutmutAdapter()

        run_result = Mock()
        run_result.returncode = 0
        run_result.stdout = ""

        # 95% killed (excellent)
        results_result = Mock()
        results_result.returncode = 0
        results_result.stdout = (
            "Killed: 95, Survived: 5, Timeout: 0, Suspicious: 0, Skipped: 0"
        )

        junit_result = Mock()
        junit_result.returncode = 0
        junit_result.stdout = ""

        mock_run_command.side_effect = [run_result, results_result, junit_result]

        result = adapter.execute(str(tmp_path))

        assert result["mutation_score"] == 95.0
        assert result["test_effectiveness"] == 95.0

    @patch("coverage_analyzer.adapters.mutmut_adapter.MutmutAdapter._run_command")
    def test_low_mutation_score(self, mock_run_command, tmp_path):
        """Test with low mutation score (poor test quality)."""
        adapter = MutmutAdapter()

        run_result = Mock()
        run_result.returncode = 0
        run_result.stdout = ""

        # Only 30% killed (poor)
        results_result = Mock()
        results_result.returncode = 0
        results_result.stdout = (
            "Killed: 30, Survived: 70, Timeout: 0, Suspicious: 0, Skipped: 0"
        )

        junit_result = Mock()
        junit_result.returncode = 0
        junit_result.stdout = ""

        mock_run_command.side_effect = [run_result, results_result, junit_result]

        result = adapter.execute(str(tmp_path))

        assert result["mutation_score"] == 30.0
        assert result["survived_mutants"] == 70

    def test_extract_count(self):
        """Test regex extraction of counts."""
        adapter = MutmutAdapter()

        text = "Killed: 45, Survived: 5, Timeout: 2"

        assert adapter._extract_count(text, r"Killed[:\s]+(\d+)") == 45
        assert adapter._extract_count(text, r"Survived[:\s]+(\d+)") == 5
        assert adapter._extract_count(text, r"Timeout[:\s]+(\d+)") == 2
        assert adapter._extract_count(text, r"NotFound[:\s]+(\d+)") == 0

    def test_extract_count_case_insensitive(self):
        """Test case-insensitive extraction."""
        adapter = MutmutAdapter()

        text = "KILLED: 100"
        assert adapter._extract_count(text, r"killed[:\s]+(\d+)") == 100

    @patch("coverage_analyzer.adapters.mutmut_adapter.MutmutAdapter._run_command")
    def test_clean_cache(self, mock_run_command):
        """Test cache cleaning."""
        adapter = MutmutAdapter()

        mock_result = Mock()
        mock_result.returncode = 0
        mock_run_command.return_value = mock_result

        adapter.clean_cache()

        mock_run_command.assert_called_once()
        assert "clean-cache" in str(mock_run_command.call_args)

    @patch("coverage_analyzer.adapters.mutmut_adapter.MutmutAdapter._run_command")
    def test_clean_cache_ignores_errors(self, mock_run_command):
        """Test that cache cleaning ignores errors."""
        adapter = MutmutAdapter()

        mock_run_command.side_effect = Exception("Cache clean failed")

        # Should not raise
        adapter.clean_cache()

    @patch("coverage_analyzer.adapters.mutmut_adapter.MutmutAdapter._run_command")
    def test_with_skipped_mutants(self, mock_run_command, tmp_path):
        """Test handling of skipped mutants."""
        adapter = MutmutAdapter()

        run_result = Mock()
        run_result.returncode = 0
        run_result.stdout = ""

        # Some mutants skipped
        results_result = Mock()
        results_result.returncode = 0
        results_result.stdout = (
            "Killed: 80, Survived: 10, Timeout: 5, Suspicious: 0, Skipped: 5"
        )

        junit_result = Mock()
        junit_result.returncode = 0
        junit_result.stdout = ""

        mock_run_command.side_effect = [run_result, results_result, junit_result]

        result = adapter.execute(str(tmp_path))

        # Mutation score should exclude skipped and timeout
        # Actual: 80 / (80 + 10 - skipped) or similar
        assert result["skipped_mutants"] == 5
        assert 88 <= result["mutation_score"] <= 95

    def test_parse_empty_results(self):
        """Test parsing when no mutants found."""
        adapter = MutmutAdapter()

        results = {"summary": "", "junit_xml": "", "exit_code": 0}
        parsed = adapter._parse_mutmut_results(results)

        assert parsed["total_mutants"] == 0
        assert parsed["mutation_score"] == 0.0
