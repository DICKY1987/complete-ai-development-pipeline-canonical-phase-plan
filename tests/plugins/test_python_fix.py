"""
Tests for Python fix plugins (isort, black).
"""

# DOC_ID: DOC-TEST-PLUGINS-TEST-PYTHON-FIX-146
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Try to import plugins - may fail if error shared modules not migrated
try:
    from phase6_error_recovery.modules.plugins.python_black_fix.src.python_black_fix.plugin import (
        BlackFixPlugin,
    )
    from phase6_error_recovery.modules.plugins.python_isort_fix.src.python_isort_fix.plugin import (
        IsortFixPlugin,
    )

    PLUGINS_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    PLUGINS_AVAILABLE = False
    pytestmark = pytest.mark.skip(
        reason="Plugin modules require error shared modules not yet migrated"
    )
from tests.plugins.conftest import (
    assert_plugin_result_valid,
    create_sample_file,
    skip_if_tool_missing,
    tool_available,
)

# Sample Python code with unsorted imports
UNSORTED_IMPORTS = """
import sys
import os
from pathlib import Path
import json
from typing import Dict
"""

SORTED_IMPORTS = """
import json
import os
import sys
from pathlib import Path
from typing import Dict
"""

POORLY_FORMATTED = """
def hello(  ):
    x=1+2
    return x
"""

WELL_FORMATTED = """
def hello():
    x = 1 + 2
    return x
"""


class TestIsortFixPlugin:
    """Tests for isort fix plugin."""

    def test_plugin_has_required_attributes(self):
        """Test plugin has required class attributes."""
        plugin = IsortFixPlugin()
        assert plugin.plugin_id == "python_isort_fix"
        assert plugin.name == "isort (fix)"
        assert hasattr(plugin, "check_tool_available")
        assert hasattr(plugin, "build_command")
        assert hasattr(plugin, "execute")

    def test_check_tool_available(self):
        """Test tool availability check."""
        plugin = IsortFixPlugin()
        # Should return True if isort is installed, False otherwise
        result = plugin.check_tool_available()
        assert result == tool_available("isort")

    def test_build_command(self, tmp_path: Path):
        """Test command building."""
        plugin = IsortFixPlugin()
        test_file = tmp_path / "test.py"
        test_file.write_text("import os", encoding="utf-8")

        cmd = plugin.build_command(test_file)
        assert isinstance(cmd, list)
        assert "isort" in cmd
        assert str(test_file) in cmd

    @skip_if_tool_missing("isort")
    def test_execute_sorts_imports(self, tmp_path: Path):
        """Test that plugin executes and sorts imports (live test)."""
        plugin = IsortFixPlugin()
        test_file = create_sample_file(tmp_path, "test.py", UNSORTED_IMPORTS)

        result = plugin.execute(test_file)

        assert_plugin_result_valid(result, expected_success=True)
        assert result.plugin_id == "python_isort_fix"
        assert len(result.issues) == 0  # Fix plugins don't emit issues

    def test_execute_with_mock(self, tmp_path: Path):
        """Test execute with mocked subprocess (unit test)."""
        plugin = IsortFixPlugin()
        test_file = create_sample_file(tmp_path, "test.py", UNSORTED_IMPORTS)

        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 0
            mock_proc.stdout = ""
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc

            result = plugin.execute(test_file)

            assert_plugin_result_valid(result, expected_success=True)
            assert len(result.issues) == 0
            assert mock_run.called

    def test_execute_handles_exception(self, tmp_path: Path):
        """Test that plugin handles exceptions gracefully."""
        plugin = IsortFixPlugin()
        test_file = create_sample_file(tmp_path, "test.py", "import os")

        with patch("subprocess.run", side_effect=Exception("Test error")):
            result = plugin.execute(test_file)

            assert result.success is False
            assert "Test error" in result.stderr


class TestBlackFixPlugin:
    """Tests for black fix plugin."""

    def test_plugin_has_required_attributes(self):
        """Test plugin has required class attributes."""
        plugin = BlackFixPlugin()
        assert plugin.plugin_id == "python_black_fix"
        assert plugin.name == "Black Formatter (fix)"
        assert hasattr(plugin, "check_tool_available")
        assert hasattr(plugin, "build_command")
        assert hasattr(plugin, "execute")

    def test_check_tool_available(self):
        """Test tool availability check."""
        plugin = BlackFixPlugin()
        result = plugin.check_tool_available()
        assert result == tool_available("black")

    def test_build_command(self, tmp_path: Path):
        """Test command building."""
        plugin = BlackFixPlugin()
        test_file = tmp_path / "test.py"
        test_file.write_text("def f():pass", encoding="utf-8")

        cmd = plugin.build_command(test_file)
        assert isinstance(cmd, list)
        assert "black" in cmd
        assert str(test_file) in cmd

    @skip_if_tool_missing("black")
    def test_execute_formats_code(self, tmp_path: Path):
        """Test that plugin executes and formats code (live test)."""
        plugin = BlackFixPlugin()
        test_file = create_sample_file(tmp_path, "test.py", POORLY_FORMATTED)

        result = plugin.execute(test_file)

        assert_plugin_result_valid(result, expected_success=True)
        assert result.plugin_id == "python_black_fix"
        assert len(result.issues) == 0  # Fix plugins don't emit issues

    def test_execute_with_mock(self, tmp_path: Path):
        """Test execute with mocked subprocess (unit test)."""
        plugin = BlackFixPlugin()
        test_file = create_sample_file(tmp_path, "test.py", POORLY_FORMATTED)

        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 0
            mock_proc.stdout = ""
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc

            result = plugin.execute(test_file)

            assert_plugin_result_valid(result, expected_success=True)
            assert len(result.issues) == 0
            assert mock_run.called

    def test_execute_handles_exception(self, tmp_path: Path):
        """Test that plugin handles exceptions gracefully."""
        plugin = BlackFixPlugin()
        test_file = create_sample_file(tmp_path, "test.py", "def f():pass")

        with patch("subprocess.run", side_effect=Exception("Test error")):
            result = plugin.execute(test_file)

            assert result.success is False
            assert "Test error" in result.stderr

    def test_execute_with_timeout(self, tmp_path: Path):
        """Test that timeout is enforced."""
        plugin = BlackFixPlugin()
        test_file = create_sample_file(tmp_path, "test.py", "def f():pass")

        with patch("subprocess.run") as mock_run:
            # Verify timeout parameter is passed
            mock_proc = MagicMock()
            mock_proc.returncode = 0
            mock_proc.stdout = ""
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc

            plugin.execute(test_file)

            # Check that subprocess.run was called with timeout
            call_kwargs = mock_run.call_args.kwargs
            assert "timeout" in call_kwargs
            assert call_kwargs["timeout"] == 120
