"""
Tests for Python type checker plugins (mypy, pyright).
"""

# DOC_ID: DOC-TEST-PLUGINS-TEST-PYTHON-TYPE-149
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Try to import plugins - may fail if error shared modules not migrated
try:
    from phase6_error_recovery.modules.plugins.python_mypy.src.python_mypy.plugin import (
        MypyPlugin,
    )
    from phase6_error_recovery.modules.plugins.python_pyright.src.python_pyright.plugin import (
        PyrightPlugin,
    )

    PLUGINS_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    PLUGINS_AVAILABLE = False
    pytestmark = pytest.mark.skip(
        reason="Plugin modules require error shared modules not yet migrated"
    )
from tests.plugins.conftest import (
    assert_issue_valid,
    assert_plugin_result_valid,
    create_sample_file,
    skip_if_tool_missing,
    tool_available,
)

# Sample mypy JSON output
MYPY_SAMPLE_OUTPUT = """
{"file": "test.py", "line": 5, "column": 10, "severity": "error", "message": "Incompatible types in assignment", "code": "assignment"}
{"file": "test.py", "line": 10, "column": 1, "severity": "note", "message": "Note: type was inferred", "code": null}
"""

# Sample Pyright JSON output
PYRIGHT_SAMPLE_OUTPUT = json.dumps(
    {
        "generalDiagnostics": [
            {
                "file": "test.py",
                "severity": "error",
                "message": "Type 'int' is not assignable to type 'str'",
                "range": {
                    "start": {"line": 4, "character": 8},
                    "end": {"line": 4, "character": 10},
                },
                "rule": "reportGeneralTypeIssues",
            },
            {
                "file": "test.py",
                "severity": "warning",
                "message": "Import 'typing' is not accessed",
                "range": {
                    "start": {"line": 0, "character": 0},
                    "end": {"line": 0, "character": 13},
                },
                "rule": "reportUnusedImport",
            },
        ],
        "summary": {"errorCount": 1, "warningCount": 1},
    }
)


class TestMypyPlugin:
    """Tests for mypy type checker plugin."""

    def test_plugin_has_required_attributes(self):
        """Test plugin has required class attributes."""
        plugin = MypyPlugin()
        assert plugin.plugin_id == "python_mypy"
        assert plugin.name == "mypy"
        assert hasattr(plugin, "check_tool_available")
        assert hasattr(plugin, "build_command")
        assert hasattr(plugin, "execute")

    def test_check_tool_available(self):
        """Test tool availability check."""
        plugin = MypyPlugin()
        result = plugin.check_tool_available()
        assert result == tool_available("mypy")

    def test_build_command(self, tmp_path: Path):
        """Test command building."""
        plugin = MypyPlugin()
        test_file = tmp_path / "test.py"
        test_file.write_text("x: int = 'hello'", encoding="utf-8")

        cmd = plugin.build_command(test_file)
        assert isinstance(cmd, list)
        assert "mypy" in cmd
        assert str(test_file) in cmd

    def test_parse_mypy_json(self, tmp_path: Path):
        """Test parsing mypy JSONL output."""
        plugin = MypyPlugin()
        test_file = create_sample_file(tmp_path, "test.py", "x: int = 'hello'\n")

        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 1  # mypy returns 1 when issues found
            mock_proc.stdout = MYPY_SAMPLE_OUTPUT
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc

            result = plugin.execute(test_file)

            assert_plugin_result_valid(result, expected_success=True)
            assert len(result.issues) >= 1

            # Check first issue
            issue = result.issues[0]
            assert_issue_valid(issue, expected_tool="mypy")
            assert issue.category == "type"
            assert issue.severity == "error"
            assert issue.line == 5
            assert issue.column == 10
            assert "assignment" in (issue.code or "")

    def test_success_codes(self, tmp_path: Path):
        """Test that return codes 0 and 1 are both successful."""
        plugin = MypyPlugin()
        test_file = create_sample_file(tmp_path, "test.py", "x: int = 5")

        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.stdout = ""
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc

            # Return code 0 (no issues)
            mock_proc.returncode = 0
            result = plugin.execute(test_file)
            assert result.success is True

            # Return code 1 (issues found)
            mock_proc.returncode = 1
            result = plugin.execute(test_file)
            assert result.success is True

            # Other return codes should fail
            mock_proc.returncode = 2
            result = plugin.execute(test_file)
            assert result.success is False

    def test_handles_malformed_json(self, tmp_path: Path):
        """Test graceful handling of malformed JSONL."""
        plugin = MypyPlugin()
        test_file = create_sample_file(tmp_path, "test.py", "x = 5")

        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 0
            mock_proc.stdout = "not valid json\n{incomplete"
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc

            result = plugin.execute(test_file)

            # Should succeed but with no issues parsed
            assert result.success is True
            assert len(result.issues) == 0


class TestPyrightPlugin:
    """Tests for Pyright type checker plugin."""

    def test_plugin_has_required_attributes(self):
        """Test plugin has required class attributes."""
        plugin = PyrightPlugin()
        assert plugin.plugin_id == "python_pyright"
        assert plugin.name == "Pyright"
        assert hasattr(plugin, "check_tool_available")
        assert hasattr(plugin, "build_command")
        assert hasattr(plugin, "execute")

    def test_check_tool_available(self):
        """Test tool availability check."""
        plugin = PyrightPlugin()
        result = plugin.check_tool_available()
        assert result == tool_available("pyright")

    def test_build_command(self, tmp_path: Path):
        """Test command building."""
        plugin = PyrightPlugin()
        test_file = tmp_path / "test.py"
        test_file.write_text("x: int = 'hello'", encoding="utf-8")

        cmd = plugin.build_command(test_file)
        assert isinstance(cmd, list)
        assert "pyright" in cmd
        assert "--outputjson" in cmd
        assert str(test_file) in cmd

    def test_parse_pyright_json(self, tmp_path: Path):
        """Test parsing Pyright JSON output with 0-based to 1-based conversion."""
        plugin = PyrightPlugin()
        test_file = create_sample_file(tmp_path, "test.py", "x: int = 'hello'\n")

        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 1
            mock_proc.stdout = PYRIGHT_SAMPLE_OUTPUT
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc

            result = plugin.execute(test_file)

            assert_plugin_result_valid(result, expected_success=True)
            assert len(result.issues) == 2

            # Check first issue (error)
            error_issue = result.issues[0]
            assert_issue_valid(error_issue, expected_tool="pyright")
            assert error_issue.category == "type"
            assert error_issue.severity == "error"
            # Pyright uses 0-based positions, should be converted to 1-based
            assert error_issue.line == 5  # 4 + 1
            assert error_issue.column == 9  # 8 + 1

            # Check second issue (warning)
            warning_issue = result.issues[1]
            assert warning_issue.severity == "warning"
            assert warning_issue.line == 1  # 0 + 1
            assert warning_issue.column == 1  # 0 + 1

    def test_success_codes(self, tmp_path: Path):
        """Test that return codes 0 and 1 are both successful."""
        plugin = PyrightPlugin()
        test_file = create_sample_file(tmp_path, "test.py", "x: int = 5")

        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.stdout = json.dumps({"generalDiagnostics": []})
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc

            # Return code 0 (no issues)
            mock_proc.returncode = 0
            result = plugin.execute(test_file)
            assert result.success is True

            # Return code 1 (issues found)
            mock_proc.returncode = 1
            result = plugin.execute(test_file)
            assert result.success is True

            # Other return codes should fail
            mock_proc.returncode = 2
            result = plugin.execute(test_file)
            assert result.success is False

    def test_handles_malformed_json(self, tmp_path: Path):
        """Test graceful handling of malformed JSON."""
        plugin = PyrightPlugin()
        test_file = create_sample_file(tmp_path, "test.py", "x = 5")

        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 0
            mock_proc.stdout = "not valid json"
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc

            result = plugin.execute(test_file)

            # Should succeed but with no issues parsed
            assert result.success is True
            assert len(result.issues) == 0
