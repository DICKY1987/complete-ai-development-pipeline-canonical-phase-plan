"""
Tests for cross-cutting plugins (codespell, semgrep, gitleaks).
"""

# DOC_ID: DOC-TEST-PLUGINS-TEST-CROSS-CUTTING-142
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Try to import plugins - may fail if error shared modules not migrated
try:
    from phase6_error_recovery.modules.plugins.codespell.src.codespell.plugin import (
        CodespellPlugin,
    )
    from phase6_error_recovery.modules.plugins.semgrep.src.semgrep.plugin import (
        SemgrepPlugin,
    )
    from phase6_error_recovery.modules.plugins.gitleaks.src.gitleaks.plugin import (
        GitleaksPlugin,
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


# Sample codespell output
CODESPELL_SAMPLE_OUTPUT = """
test.txt:1: teh ==> the
test.txt:5: recieve ==> receive
"""

# Sample Semgrep JSON output
SEMGREP_SAMPLE_OUTPUT = json.dumps(
    {
        "results": [
            {
                "path": "test.py",
                "start": {"line": 10, "col": 5},
                "check_id": "python.lang.security.audit.dangerous-exec",
                "extra": {"message": "Detected the use of exec()", "severity": "ERROR"},
            },
            {
                "path": "test.py",
                "start": {"line": 20, "col": 1},
                "check_id": "python.lang.security.audit.weak-crypto",
                "extra": {
                    "message": "Use of weak cryptographic hash",
                    "severity": "WARNING",
                },
            },
        ]
    }
)

# Sample Gitleaks JSON output
GITLEAKS_SAMPLE_OUTPUT = json.dumps(
    [
        {
            "File": "test.py",
            "StartLine": 15,
            "RuleID": "generic-api-key",
            "Description": "Detected a Generic API Key",
        },
        {
            "File": "test.py",
            "StartLine": 25,
            "RuleID": "aws-access-token",
            "Description": "AWS Access Token",
        },
    ]
)


class TestCodespellPlugin:
    """Tests for codespell spelling checker plugin."""

    def test_plugin_has_required_attributes(self):
        """Test plugin has required class attributes."""
        plugin = CodespellPlugin()
        assert plugin.plugin_id == "codespell"
        assert plugin.name == "codespell"
        assert hasattr(plugin, "check_tool_available")
        assert hasattr(plugin, "build_command")
        assert hasattr(plugin, "execute")

    def test_check_tool_available(self):
        """Test tool availability check."""
        plugin = CodespellPlugin()
        result = plugin.check_tool_available()
        assert result == tool_available("codespell")

    def test_build_command(self, tmp_path: Path):
        """Test command building."""
        plugin = CodespellPlugin()
        test_file = tmp_path / "test.txt"
        test_file.write_text("This is a test", encoding="utf-8")

        cmd = plugin.build_command(test_file)
        assert isinstance(cmd, list)
        assert "codespell" in cmd
        assert str(test_file) in cmd

    def test_parse_codespell_output(self, tmp_path: Path):
        """Test parsing codespell output."""
        plugin = CodespellPlugin()
        test_file = create_sample_file(tmp_path, "test.txt", "This is teh test\n")

        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 1
            mock_proc.stdout = CODESPELL_SAMPLE_OUTPUT
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc

            result = plugin.execute(test_file)

            assert_plugin_result_valid(result, expected_success=True)
            assert len(result.issues) == 2

            # All issues should be style/warning
            for issue in result.issues:
                assert_issue_valid(issue, expected_tool="codespell")
                assert issue.category == "style"
                assert issue.severity == "warning"

            # Check specific issue details
            assert result.issues[0].line == 1
            assert "teh" in result.issues[0].message
            assert result.issues[1].line == 5

    def test_success_codes(self, tmp_path: Path):
        """Test that return codes 0 and 1 are both successful."""
        plugin = CodespellPlugin()
        test_file = create_sample_file(tmp_path, "test.txt", "correct spelling")

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


class TestSemgrepPlugin:
    """Tests for Semgrep security scanner plugin."""

    def test_plugin_has_required_attributes(self):
        """Test plugin has required class attributes."""
        plugin = SemgrepPlugin()
        assert plugin.plugin_id == "semgrep"
        assert plugin.name == "Semgrep"
        assert hasattr(plugin, "check_tool_available")
        assert hasattr(plugin, "build_command")
        assert hasattr(plugin, "execute")

    def test_check_tool_available(self):
        """Test tool availability check."""
        plugin = SemgrepPlugin()
        result = plugin.check_tool_available()
        assert result == tool_available("semgrep")

    def test_build_command(self, tmp_path: Path):
        """Test command building."""
        plugin = SemgrepPlugin()
        test_file = tmp_path / "test.py"
        test_file.write_text("import os", encoding="utf-8")

        cmd = plugin.build_command(test_file)
        assert isinstance(cmd, list)
        assert "semgrep" in cmd
        assert "--json" in cmd
        assert "--quiet" in cmd
        assert "--config" in cmd
        assert "auto" in cmd

    def test_parse_semgrep_json_with_severity_mapping(self, tmp_path: Path):
        """Test parsing Semgrep JSON with severity mapping (ERROR→error, WARNING→warning, INFO→info)."""
        plugin = SemgrepPlugin()
        test_file = create_sample_file(tmp_path, "test.py", "exec(user_input)\n")

        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 1
            mock_proc.stdout = SEMGREP_SAMPLE_OUTPUT
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc

            result = plugin.execute(test_file)

            assert_plugin_result_valid(result, expected_success=True)
            assert len(result.issues) == 2

            # First issue: ERROR → error
            error_issue = result.issues[0]
            assert_issue_valid(error_issue, expected_tool="semgrep")
            assert error_issue.category == "security"
            assert error_issue.severity == "error"
            assert error_issue.line == 10
            assert error_issue.column == 5

            # Second issue: WARNING → warning
            warning_issue = result.issues[1]
            assert warning_issue.category == "security"
            assert warning_issue.severity == "warning"
            assert warning_issue.line == 20

    def test_success_codes(self, tmp_path: Path):
        """Test that return codes 0 and 1 are both successful."""
        plugin = SemgrepPlugin()
        test_file = create_sample_file(tmp_path, "test.py", "import os")

        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.stdout = json.dumps({"results": []})
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

    def test_timeout_enforcement(self, tmp_path: Path):
        """Test that timeout is set to 180 seconds."""
        plugin = SemgrepPlugin()
        test_file = create_sample_file(tmp_path, "test.py", "import os")

        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 0
            mock_proc.stdout = json.dumps({"results": []})
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc

            plugin.execute(test_file)

            # Check timeout parameter
            call_kwargs = mock_run.call_args.kwargs
            assert "timeout" in call_kwargs
            assert call_kwargs["timeout"] == 180


class TestGitleaksPlugin:
    """Tests for Gitleaks secret detection plugin."""

    def test_plugin_has_required_attributes(self):
        """Test plugin has required class attributes."""
        plugin = GitleaksPlugin()
        assert plugin.plugin_id == "gitleaks"
        assert plugin.name == "Gitleaks"
        assert hasattr(plugin, "check_tool_available")
        assert hasattr(plugin, "build_command")
        assert hasattr(plugin, "execute")

    def test_check_tool_available(self):
        """Test tool availability check."""
        plugin = GitleaksPlugin()
        result = plugin.check_tool_available()
        assert result == tool_available("gitleaks")

    def test_build_command(self, tmp_path: Path):
        """Test command building."""
        plugin = GitleaksPlugin()
        test_file = tmp_path / "test.py"
        test_file.write_text("API_KEY = 'secret'", encoding="utf-8")

        cmd = plugin.build_command(test_file)
        assert isinstance(cmd, list)
        assert "gitleaks" in cmd
        assert "detect" in cmd
        assert "--no-git" in cmd
        assert "--no-banner" in cmd
        assert "--report-format" in cmd
        assert "json" in cmd

    def test_parse_gitleaks_json_filters_to_target_file(self, tmp_path: Path):
        """Test parsing Gitleaks JSON and filtering to target file only."""
        plugin = GitleaksPlugin()
        test_file = create_sample_file(tmp_path, "test.py", "API_KEY = 'secret'\n")

        # Create Gitleaks output with multiple files
        gitleaks_output = json.dumps(
            [
                {
                    "File": "test.py",
                    "StartLine": 15,
                    "RuleID": "generic-api-key",
                    "Description": "Detected a Generic API Key",
                },
                {
                    "File": "other.py",  # Should be filtered out
                    "StartLine": 10,
                    "RuleID": "aws-key",
                    "Description": "AWS Key",
                },
            ]
        )

        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 1
            mock_proc.stdout = gitleaks_output
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc

            result = plugin.execute(test_file)

            assert_plugin_result_valid(result, expected_success=True)
            # Should only include issues from test.py
            assert len(result.issues) == 1

            issue = result.issues[0]
            assert_issue_valid(issue, expected_tool="gitleaks")
            assert issue.category == "security"
            assert issue.severity == "error"
            assert issue.line == 15
            assert "test.py" in issue.path

    def test_success_codes(self, tmp_path: Path):
        """Test that return codes 0 and 1 are both successful."""
        plugin = GitleaksPlugin()
        test_file = create_sample_file(tmp_path, "test.py", "import os")

        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.stdout = "[]"
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc

            # Return code 0 (no secrets)
            mock_proc.returncode = 0
            result = plugin.execute(test_file)
            assert result.success is True

            # Return code 1 (secrets found)
            mock_proc.returncode = 1
            result = plugin.execute(test_file)
            assert result.success is True

    def test_timeout_enforcement(self, tmp_path: Path):
        """Test that timeout is set to 180 seconds."""
        plugin = GitleaksPlugin()
        test_file = create_sample_file(tmp_path, "test.py", "import os")

        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 0
            mock_proc.stdout = "[]"
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc

            plugin.execute(test_file)

            # Check timeout parameter
            call_kwargs = mock_run.call_args.kwargs
            assert "timeout" in call_kwargs
            assert call_kwargs["timeout"] == 180
