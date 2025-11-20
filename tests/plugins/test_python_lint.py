"""
Tests for Python lint plugins (ruff, pylint).
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from error.plugins.python_ruff.plugin import RuffPlugin
from error.plugins.python_pylint.plugin import PylintPlugin
from tests.plugins.conftest import (
    assert_issue_valid,
    assert_plugin_result_valid,
    create_sample_file,
    skip_if_tool_missing,
    tool_available,
)


# Sample Ruff JSON output
RUFF_SAMPLE_OUTPUT = json.dumps([
    {
        "code": "F401",
        "message": "module imported but unused",
        "filename": "test.py",
        "location": {"row": 1, "column": 1}
    },
    {
        "code": "E501",
        "message": "line too long (120 > 88 characters)",
        "filename": "test.py",
        "location": {"row": 5, "column": 89}
    }
])

# Sample Pylint JSON output
PYLINT_SAMPLE_OUTPUT = json.dumps([
    {
        "type": "error",
        "symbol": "syntax-error",
        "message": "invalid syntax",
        "path": "test.py",
        "line": 1,
        "column": 0
    },
    {
        "type": "warning",
        "symbol": "unused-import",
        "message": "Unused import sys",
        "path": "test.py",
        "line": 2,
        "column": 0
    },
    {
        "type": "convention",
        "symbol": "line-too-long",
        "message": "Line too long (100/80)",
        "path": "test.py",
        "line": 10,
        "column": 0
    }
])


class TestRuffPlugin:
    """Tests for Ruff linter plugin."""
    
    def test_plugin_has_required_attributes(self):
        """Test plugin has required class attributes."""
        plugin = RuffPlugin()
        assert plugin.plugin_id == "python_ruff"
        assert plugin.name == "Ruff Linter"
        assert hasattr(plugin, "check_tool_available")
        assert hasattr(plugin, "build_command")
        assert hasattr(plugin, "execute")
    
    def test_check_tool_available(self):
        """Test tool availability check."""
        plugin = RuffPlugin()
        result = plugin.check_tool_available()
        assert result == tool_available("ruff")
    
    def test_build_command(self, tmp_path: Path):
        """Test command building."""
        plugin = RuffPlugin()
        test_file = tmp_path / "test.py"
        test_file.write_text("import os", encoding="utf-8")
        
        cmd = plugin.build_command(test_file)
        assert isinstance(cmd, list)
        assert "ruff" in cmd
        assert "check" in cmd
        assert "--output-format" in cmd or "-f" in cmd or "json" in cmd
        assert str(test_file) in cmd
    
    def test_parse_ruff_json(self, tmp_path: Path):
        """Test parsing Ruff JSON output."""
        plugin = RuffPlugin()
        test_file = create_sample_file(tmp_path, "test.py", "import os\n")
        
        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 1  # Ruff returns 1 when issues found
            mock_proc.stdout = RUFF_SAMPLE_OUTPUT
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc
            
            result = plugin.execute(test_file)
            
            assert_plugin_result_valid(result, expected_success=True)
            assert len(result.issues) == 2
            
            # Check first issue
            issue1 = result.issues[0]
            assert_issue_valid(issue1, expected_tool="ruff")
            assert issue1.code == "F401"
            assert issue1.category == "style"
            assert issue1.severity == "warning"
            assert issue1.line == 1
            assert issue1.column == 1
            
            # Check second issue
            issue2 = result.issues[1]
            assert issue2.code == "E501"
            assert issue2.line == 5
    
    def test_success_codes(self, tmp_path: Path):
        """Test that return codes 0 and 1 are both successful."""
        plugin = RuffPlugin()
        test_file = create_sample_file(tmp_path, "test.py", "import os")
        
        with patch("subprocess.run") as mock_run:
            # Test return code 0 (no issues)
            mock_proc = MagicMock()
            mock_proc.returncode = 0
            mock_proc.stdout = "[]"
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc
            
            result = plugin.execute(test_file)
            assert result.success is True
            
            # Test return code 1 (issues found)
            mock_proc.returncode = 1
            result = plugin.execute(test_file)
            assert result.success is True
            
            # Test return code 2 (should fail)
            mock_proc.returncode = 2
            result = plugin.execute(test_file)
            assert result.success is False
    
    def test_handles_malformed_json(self, tmp_path: Path):
        """Test graceful handling of malformed JSON."""
        plugin = RuffPlugin()
        test_file = create_sample_file(tmp_path, "test.py", "import os")
        
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


class TestPylintPlugin:
    """Tests for Pylint linter plugin."""
    
    def test_plugin_has_required_attributes(self):
        """Test plugin has required class attributes."""
        plugin = PylintPlugin()
        assert plugin.plugin_id == "python_pylint"
        assert plugin.name == "Pylint"
        assert hasattr(plugin, "check_tool_available")
        assert hasattr(plugin, "build_command")
        assert hasattr(plugin, "execute")
    
    def test_check_tool_available(self):
        """Test tool availability check."""
        plugin = PylintPlugin()
        result = plugin.check_tool_available()
        assert result == tool_available("pylint")
    
    def test_parse_pylint_json(self, tmp_path: Path):
        """Test parsing Pylint JSON output with category/severity mapping."""
        plugin = PylintPlugin()
        test_file = create_sample_file(tmp_path, "test.py", "import os\n")
        
        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 4  # Pylint uses bitmask return codes
            mock_proc.stdout = PYLINT_SAMPLE_OUTPUT
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc
            
            result = plugin.execute(test_file)
            
            assert_plugin_result_valid(result, expected_success=True)
            assert len(result.issues) == 3
            
            # Check error mapping (error → syntax/error)
            error_issue = result.issues[0]
            assert_issue_valid(error_issue, expected_tool="pylint")
            assert error_issue.category == "syntax"
            assert error_issue.severity == "error"
            
            # Check warning mapping (warning → style/warning)
            warning_issue = result.issues[1]
            assert warning_issue.category == "style"
            assert warning_issue.severity == "warning"
            
            # Check convention mapping (convention → style/info)
            convention_issue = result.issues[2]
            assert convention_issue.category == "style"
            assert convention_issue.severity == "info"
    
    def test_pylint_return_code_handling(self, tmp_path: Path):
        """Test Pylint return code handling (bitmask)."""
        plugin = PylintPlugin()
        test_file = create_sample_file(tmp_path, "test.py", "import os")
        
        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.stdout = "[]"
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc
            
            # Bit 32 (usage error) should fail
            mock_proc.returncode = 32
            result = plugin.execute(test_file)
            assert result.success is False
            
            # Bits 1,2,4,8,16 (various issues) should succeed
            for code in [1, 2, 4, 8, 16]:
                mock_proc.returncode = code
                result = plugin.execute(test_file)
                assert result.success is True
            
            # Return code 0 (no issues) should succeed
            mock_proc.returncode = 0
            result = plugin.execute(test_file)
            assert result.success is True
    
    def test_handles_exception(self, tmp_path: Path):
        """Test that plugin handles exceptions gracefully."""
        plugin = PylintPlugin()
        test_file = create_sample_file(tmp_path, "test.py", "import os")
        
        with patch("subprocess.run", side_effect=Exception("Test error")):
            result = plugin.execute(test_file)
            
            assert result.success is False
            assert "Test error" in result.stderr
