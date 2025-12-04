"""
Tests for markup/data plugins (YAML, Markdown, JSON).
"""
# DOC_ID: DOC-TEST-PLUGINS-TEST-MARKUP-DATA-144
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Try to import plugins - may fail if error shared modules not migrated
try:
    from phase6_error_recovery.modules.plugins.yaml_yamllint.src.yaml_yamllint.plugin import YamllintPlugin
    from phase6_error_recovery.modules.plugins.md_mdformat_fix.src.md_mdformat_fix.plugin import MdformatFixPlugin
    from phase6_error_recovery.modules.plugins.md_markdownlint.src.md_markdownlint.plugin import MarkdownlintPlugin
    from phase6_error_recovery.modules.plugins.json_jq.src.json_jq.plugin import JsonJqPlugin
    PLUGINS_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    PLUGINS_AVAILABLE = False
    pytestmark = pytest.mark.skip(reason="Plugin modules require error shared modules not yet migrated")
from tests.plugins.conftest import (
    assert_issue_valid,
    assert_plugin_result_valid,
    create_sample_file,
    skip_if_tool_missing,
    tool_available,
)


# Sample yamllint parsable output
YAMLLINT_SAMPLE_OUTPUT = """
test.yml:1:1: [error] syntax error: expected <block end>, but found '<scalar>' (syntax)
test.yml:5:10: [warning] line too long (120 > 80 characters) (line-length)
"""

# Sample markdownlint JSON output
MARKDOWNLINT_SAMPLE_JSON = json.dumps({
    "test.md": [
        {
            "lineNumber": 1,
            "ruleNames": ["MD041", "first-line-heading"],
            "ruleDescription": "First line in file should be a top level heading"
        },
        {
            "lineNumber": 10,
            "ruleNames": ["MD009", "no-trailing-spaces"],
            "ruleDescription": "Trailing spaces"
        }
    ]
})


class TestYamllintPlugin:
    """Tests for yamllint plugin."""
    
    def test_plugin_has_required_attributes(self):
        """Test plugin has required class attributes."""
        plugin = YamllintPlugin()
        assert plugin.plugin_id == "yaml_yamllint"
        assert plugin.name == "yamllint"
        assert hasattr(plugin, "check_tool_available")
        assert hasattr(plugin, "build_command")
        assert hasattr(plugin, "execute")
    
    def test_check_tool_available(self):
        """Test tool availability check."""
        plugin = YamllintPlugin()
        result = plugin.check_tool_available()
        assert result == tool_available("yamllint")
    
    def test_build_command(self, tmp_path: Path):
        """Test command building."""
        plugin = YamllintPlugin()
        test_file = tmp_path / "test.yml"
        test_file.write_text("key: value", encoding="utf-8")
        
        cmd = plugin.build_command(test_file)
        assert isinstance(cmd, list)
        assert "yamllint" in cmd
        assert "-f" in cmd or "--format" in cmd
        assert "parsable" in cmd
        assert str(test_file) in cmd
    
    def test_parse_yamllint_output(self, tmp_path: Path):
        """Test parsing yamllint parsable format output."""
        plugin = YamllintPlugin()
        test_file = create_sample_file(tmp_path, "test.yml", "key: value\n")
        
        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 1
            mock_proc.stdout = YAMLLINT_SAMPLE_OUTPUT
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc
            
            result = plugin.execute(test_file)
            
            assert_plugin_result_valid(result, expected_success=True)
            assert len(result.issues) == 2
            
            # First issue: syntax error → syntax category
            syntax_issue = result.issues[0]
            assert_issue_valid(syntax_issue, expected_tool="yamllint")
            assert syntax_issue.category == "syntax"
            assert syntax_issue.severity == "error"
            assert syntax_issue.line == 1
            assert syntax_issue.column == 1
            
            # Second issue: line too long → style category
            style_issue = result.issues[1]
            assert style_issue.category == "style"
            assert style_issue.severity == "warning"
            assert style_issue.line == 5
            assert style_issue.column == 10
    
    def test_success_codes(self, tmp_path: Path):
        """Test that return codes 0 and 1 are both successful."""
        plugin = YamllintPlugin()
        test_file = create_sample_file(tmp_path, "test.yml", "key: value")
        
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


class TestMdformatFixPlugin:
    """Tests for mdformat fix plugin."""
    
    def test_plugin_has_required_attributes(self):
        """Test plugin has required class attributes."""
        plugin = MdformatFixPlugin()
        assert plugin.plugin_id == "md_mdformat_fix"
        assert plugin.name == "mdformat (fix)"
        assert hasattr(plugin, "check_tool_available")
        assert hasattr(plugin, "build_command")
        assert hasattr(plugin, "execute")
    
    def test_check_tool_available(self):
        """Test tool availability check."""
        plugin = MdformatFixPlugin()
        result = plugin.check_tool_available()
        assert result == tool_available("mdformat")
    
    def test_build_command(self, tmp_path: Path):
        """Test command building."""
        plugin = MdformatFixPlugin()
        test_file = tmp_path / "test.md"
        test_file.write_text("# Title", encoding="utf-8")
        
        cmd = plugin.build_command(test_file)
        assert isinstance(cmd, list)
        assert "mdformat" in cmd
        assert str(test_file) in cmd
    
    def test_execute_no_issues_emitted(self, tmp_path: Path):
        """Test that fix plugin does not emit issues."""
        plugin = MdformatFixPlugin()
        test_file = create_sample_file(tmp_path, "test.md", "# Title\n\nContent")
        
        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 0
            mock_proc.stdout = ""
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc
            
            result = plugin.execute(test_file)
            
            assert_plugin_result_valid(result, expected_success=True)
            assert len(result.issues) == 0  # Fix plugins don't emit issues


class TestMarkdownlintPlugin:
    """Tests for markdownlint-cli plugin."""
    
    def test_plugin_has_required_attributes(self):
        """Test plugin has required class attributes."""
        plugin = MarkdownlintPlugin()
        assert plugin.plugin_id == "md_markdownlint"
        assert plugin.name == "markdownlint-cli"
        assert hasattr(plugin, "check_tool_available")
        assert hasattr(plugin, "build_command")
        assert hasattr(plugin, "execute")
    
    def test_check_tool_available(self):
        """Test tool availability check."""
        plugin = MarkdownlintPlugin()
        result = plugin.check_tool_available()
        assert result == tool_available("markdownlint")
    
    def test_build_command(self, tmp_path: Path):
        """Test command building."""
        plugin = MarkdownlintPlugin()
        test_file = tmp_path / "test.md"
        test_file.write_text("# Title", encoding="utf-8")
        
        cmd = plugin.build_command(test_file)
        assert isinstance(cmd, list)
        assert "markdownlint" in cmd
        assert "-j" in cmd or "--json" in cmd
        assert str(test_file) in cmd
    
    def test_parse_markdownlint_json(self, tmp_path: Path):
        """Test parsing markdownlint JSON output."""
        plugin = MarkdownlintPlugin()
        test_file = create_sample_file(tmp_path, "test.md", "# Title\n")
        
        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 1
            mock_proc.stdout = MARKDOWNLINT_SAMPLE_JSON
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc
            
            result = plugin.execute(test_file)
            
            assert_plugin_result_valid(result, expected_success=True)
            assert len(result.issues) == 2
            
            # All issues should be style/warning
            for issue in result.issues:
                assert_issue_valid(issue, expected_tool="markdownlint")
                assert issue.category == "style"
                assert issue.severity == "warning"
            
            # Check specific issue details
            assert result.issues[0].line == 1
            assert "MD041" in result.issues[0].code
    
    def test_parse_text_format_fallback(self, tmp_path: Path):
        """Test fallback to text format parsing."""
        plugin = MarkdownlintPlugin()
        test_file = create_sample_file(tmp_path, "test.md", "# Title")
        
        text_output = "test.md:1:1 MD041 First line should be heading"
        
        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 1
            mock_proc.stdout = text_output
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc
            
            result = plugin.execute(test_file)
            
            # Should handle text format
            assert result.success is True


class TestJsonJqPlugin:
    """Tests for jq JSON syntax validator plugin."""
    
    def test_plugin_has_required_attributes(self):
        """Test plugin has required class attributes."""
        plugin = JsonJqPlugin()
        assert plugin.plugin_id == "json_jq"
        assert plugin.name == "jq (JSON syntax)"
        assert hasattr(plugin, "check_tool_available")
        assert hasattr(plugin, "build_command")
        assert hasattr(plugin, "execute")
    
    def test_check_tool_available(self):
        """Test tool availability check."""
        plugin = JsonJqPlugin()
        result = plugin.check_tool_available()
        assert result == tool_available("jq")
    
    def test_build_command(self, tmp_path: Path):
        """Test command building."""
        plugin = JsonJqPlugin()
        test_file = tmp_path / "test.json"
        test_file.write_text('{"key": "value"}', encoding="utf-8")
        
        cmd = plugin.build_command(test_file)
        assert isinstance(cmd, list)
        assert "jq" in cmd
        assert "empty" in cmd
        assert str(test_file) in cmd
    
    def test_valid_json(self, tmp_path: Path):
        """Test that valid JSON produces no issues."""
        plugin = JsonJqPlugin()
        test_file = create_sample_file(tmp_path, "test.json", '{"key": "value"}')
        
        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 0
            mock_proc.stdout = ""
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc
            
            result = plugin.execute(test_file)
            
            assert_plugin_result_valid(result, expected_success=True)
            assert len(result.issues) == 0
    
    def test_invalid_json(self, tmp_path: Path):
        """Test that invalid JSON creates a single syntax error issue."""
        plugin = JsonJqPlugin()
        test_file = create_sample_file(tmp_path, "test.json", '{"key": invalid}')
        
        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 1
            mock_proc.stdout = ""
            mock_proc.stderr = "parse error: Invalid numeric literal"
            mock_run.return_value = mock_proc
            
            result = plugin.execute(test_file)
            
            assert result.success is False
            assert len(result.issues) == 1
            
            issue = result.issues[0]
            assert_issue_valid(issue, expected_tool="jq")
            assert issue.category == "syntax"
            assert issue.severity == "error"
            assert "parse error" in issue.message
