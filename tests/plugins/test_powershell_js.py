"""
Tests for PowerShell and JavaScript/TypeScript plugins.
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.plugins.powershell_pssa.plugin import PSScriptAnalyzerPlugin
from src.plugins.js_prettier_fix.plugin import PrettierFixPlugin
from src.plugins.js_eslint.plugin import ESLintPlugin
from tests.plugins.conftest import (
    assert_issue_valid,
    assert_plugin_result_valid,
    create_sample_file,
    skip_if_tool_missing,
    tool_available,
)


# Sample PSScriptAnalyzer JSON output
PSSA_SAMPLE_OUTPUT = json.dumps([
    {
        "RuleName": "PSAvoidUsingCmdletAliases",
        "Severity": "Warning",
        "Message": "Avoid using cmdlet aliases",
        "Line": 3,
        "Column": 1,
        "ScriptPath": "test.ps1"
    },
    {
        "RuleName": "ParseError",
        "Severity": "Error",
        "Message": "Missing closing brace",
        "Line": 10,
        "Column": 5,
        "ScriptPath": "test.ps1"
    }
])

# Sample ESLint JSON output
ESLINT_SAMPLE_OUTPUT = json.dumps([
    {
        "filePath": "test.js",
        "messages": [
            {
                "ruleId": "no-unused-vars",
                "severity": 2,
                "message": "variable is defined but never used",
                "line": 1,
                "column": 7
            },
            {
                "ruleId": "semi",
                "severity": 1,
                "message": "Missing semicolon",
                "line": 5,
                "column": 10
            }
        ]
    }
])


class TestPSScriptAnalyzerPlugin:
    """Tests for PSScriptAnalyzer plugin."""
    
    def test_plugin_has_required_attributes(self):
        """Test plugin has required class attributes."""
        plugin = PSScriptAnalyzerPlugin()
        assert plugin.plugin_id == "powershell_pssa"
        assert plugin.name == "PSScriptAnalyzer"
        assert hasattr(plugin, "check_tool_available")
        assert hasattr(plugin, "build_command")
        assert hasattr(plugin, "execute")
    
    def test_check_tool_available(self):
        """Test tool availability check."""
        plugin = PSScriptAnalyzerPlugin()
        result = plugin.check_tool_available()
        assert result == tool_available("pwsh")
    
    def test_build_command(self, tmp_path: Path):
        """Test command building."""
        plugin = PSScriptAnalyzerPlugin()
        test_file = tmp_path / "test.ps1"
        test_file.write_text("Write-Host 'hello'", encoding="utf-8")
        
        cmd = plugin.build_command(test_file)
        assert isinstance(cmd, list)
        assert "pwsh" in cmd
        assert "-NoProfile" in cmd
        assert "-Command" in cmd
    
    def test_parse_pssa_json_with_severity_mapping(self, tmp_path: Path):
        """Test parsing PSScriptAnalyzer JSON with severity mapping."""
        plugin = PSScriptAnalyzerPlugin()
        test_file = create_sample_file(tmp_path, "test.ps1", "Write-Host 'test'\n")
        
        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 0
            mock_proc.stdout = PSSA_SAMPLE_OUTPUT
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc
            
            result = plugin.execute(test_file)
            
            assert_plugin_result_valid(result, expected_success=True)
            assert len(result.issues) == 2
            
            # First issue: Warning → warning
            warning_issue = result.issues[0]
            assert_issue_valid(warning_issue, expected_tool="PSScriptAnalyzer")
            assert warning_issue.category == "style"
            assert warning_issue.severity == "warning"
            assert warning_issue.code == "PSAvoidUsingCmdletAliases"
            
            # Second issue: ParseError → syntax/error
            error_issue = result.issues[1]
            assert error_issue.category == "syntax"
            assert error_issue.severity == "error"
            assert "ParseError" in error_issue.code
    
    def test_handles_single_object_json(self, tmp_path: Path):
        """Test handling of single JSON object (not array)."""
        plugin = PSScriptAnalyzerPlugin()
        test_file = create_sample_file(tmp_path, "test.ps1", "Write-Host 'test'")
        
        single_object = json.dumps({
            "RuleName": "PSAvoidUsingCmdletAliases",
            "Severity": "Warning",
            "Message": "Test message",
            "Line": 1,
            "Column": 1,
            "ScriptPath": "test.ps1"
        })
        
        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 0
            mock_proc.stdout = single_object
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc
            
            result = plugin.execute(test_file)
            
            assert result.success is True
            assert len(result.issues) == 1


class TestPrettierFixPlugin:
    """Tests for Prettier fix plugin."""
    
    def test_plugin_has_required_attributes(self):
        """Test plugin has required class attributes."""
        plugin = PrettierFixPlugin()
        assert plugin.plugin_id == "js_prettier_fix"
        assert plugin.name == "Prettier Formatter (fix)"
        assert hasattr(plugin, "check_tool_available")
        assert hasattr(plugin, "build_command")
        assert hasattr(plugin, "execute")
    
    def test_check_tool_available(self):
        """Test tool availability check."""
        plugin = PrettierFixPlugin()
        result = plugin.check_tool_available()
        assert result == tool_available("prettier")
    
    def test_build_command(self, tmp_path: Path):
        """Test command building."""
        plugin = PrettierFixPlugin()
        test_file = tmp_path / "test.js"
        test_file.write_text("const x=1", encoding="utf-8")
        
        cmd = plugin.build_command(test_file)
        assert isinstance(cmd, list)
        assert "prettier" in cmd
        assert "--write" in cmd
        assert str(test_file) in cmd
    
    def test_execute_no_issues_emitted(self, tmp_path: Path):
        """Test that fix plugin does not emit issues."""
        plugin = PrettierFixPlugin()
        test_file = create_sample_file(tmp_path, "test.js", "const x=1;")
        
        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 0
            mock_proc.stdout = ""
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc
            
            result = plugin.execute(test_file)
            
            assert_plugin_result_valid(result, expected_success=True)
            assert len(result.issues) == 0  # Fix plugins don't emit issues


class TestESLintPlugin:
    """Tests for ESLint linter plugin."""
    
    def test_plugin_has_required_attributes(self):
        """Test plugin has required class attributes."""
        plugin = ESLintPlugin()
        assert plugin.plugin_id == "js_eslint"
        assert plugin.name == "ESLint"
        assert hasattr(plugin, "check_tool_available")
        assert hasattr(plugin, "build_command")
        assert hasattr(plugin, "execute")
    
    def test_check_tool_available(self):
        """Test tool availability check."""
        plugin = ESLintPlugin()
        result = plugin.check_tool_available()
        assert result == tool_available("eslint")
    
    def test_build_command(self, tmp_path: Path):
        """Test command building."""
        plugin = ESLintPlugin()
        test_file = tmp_path / "test.js"
        test_file.write_text("const x = 1", encoding="utf-8")
        
        cmd = plugin.build_command(test_file)
        assert isinstance(cmd, list)
        assert "eslint" in cmd
        assert "-f" in cmd or "--format" in cmd
        assert "json" in cmd
        assert str(test_file) in cmd
    
    def test_parse_eslint_json_with_severity_mapping(self, tmp_path: Path):
        """Test parsing ESLint JSON with severity mapping (2→error, 1→warning)."""
        plugin = ESLintPlugin()
        test_file = create_sample_file(tmp_path, "test.js", "const x = 1\n")
        
        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 1
            mock_proc.stdout = ESLINT_SAMPLE_OUTPUT
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc
            
            result = plugin.execute(test_file)
            
            assert_plugin_result_valid(result, expected_success=True)
            assert len(result.issues) == 2
            
            # First issue: severity 2 → error
            error_issue = result.issues[0]
            assert_issue_valid(error_issue, expected_tool="eslint")
            assert error_issue.category == "style"
            assert error_issue.severity == "error"
            assert error_issue.code == "no-unused-vars"
            assert error_issue.line == 1
            assert error_issue.column == 7
            
            # Second issue: severity 1 → warning
            warning_issue = result.issues[1]
            assert warning_issue.category == "style"
            assert warning_issue.severity == "warning"
            assert warning_issue.code == "semi"
    
    def test_success_codes(self, tmp_path: Path):
        """Test that return codes 0 and 1 are both successful."""
        plugin = ESLintPlugin()
        test_file = create_sample_file(tmp_path, "test.js", "const x = 1;")
        
        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.stdout = "[]"
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
