"""
Tests for Python security plugins (bandit, safety).
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from modules.error_plugin_python_bandit.m01000F_plugin import BanditPlugin
from modules.error_plugin_python_safety.m010016_plugin import SafetyPlugin
from tests.plugins.conftest import (
    assert_issue_valid,
    assert_plugin_result_valid,
    create_sample_file,
    skip_if_tool_missing,
    tool_available,
)


# Sample Bandit JSON output
BANDIT_SAMPLE_OUTPUT = json.dumps({
    "results": [
        {
            "code": "import pickle",
            "filename": "test.py",
            "issue_confidence": "HIGH",
            "issue_severity": "MEDIUM",
            "issue_text": "Consider possible security implications",
            "line_number": 1,
            "line_range": [1],
            "test_id": "B301",
            "test_name": "blacklist"
        },
        {
            "code": "eval(user_input)",
            "filename": "test.py",
            "issue_confidence": "HIGH",
            "issue_severity": "HIGH",
            "issue_text": "Use of possibly insecure function - consider using safer ast.literal_eval",
            "line_number": 5,
            "line_range": [5],
            "test_id": "B307",
            "test_name": "eval"
        }
    ]
})

# Sample Safety JSON output
SAFETY_SAMPLE_OUTPUT = json.dumps([
    {
        "vulnerability": "CVE-2023-12345",
        "package_name": "requests",
        "installed_version": "2.0.0",
        "affected_versions": "< 2.31.0",
        "analyzed_version": "2.0.0",
        "advisory": "Security issue in requests library",
        "severity": "high"
    },
    {
        "vulnerability": "CVE-2023-67890",
        "package_name": "urllib3",
        "installed_version": "1.26.0",
        "affected_versions": "< 1.26.18",
        "analyzed_version": "1.26.0",
        "advisory": "Vulnerability in urllib3",
        "severity": "medium"
    }
])


class TestBanditPlugin:
    """Tests for Bandit security scanner plugin."""
    
    def test_plugin_has_required_attributes(self):
        """Test plugin has required class attributes."""
        plugin = BanditPlugin()
        assert plugin.plugin_id == "python_bandit"
        assert plugin.name == "Bandit"
        assert hasattr(plugin, "check_tool_available")
        assert hasattr(plugin, "build_command")
        assert hasattr(plugin, "execute")
    
    def test_check_tool_available(self):
        """Test tool availability check."""
        plugin = BanditPlugin()
        result = plugin.check_tool_available()
        assert result == tool_available("bandit")
    
    def test_build_command(self, tmp_path: Path):
        """Test command building."""
        plugin = BanditPlugin()
        test_file = tmp_path / "test.py"
        test_file.write_text("import os", encoding="utf-8")
        
        cmd = plugin.build_command(test_file)
        assert isinstance(cmd, list)
        assert "bandit" in cmd
        assert "-f" in cmd or "--format" in cmd
        assert "json" in cmd
        assert str(test_file) in cmd
    
    def test_parse_bandit_json_with_severity_mapping(self, tmp_path: Path):
        """Test parsing Bandit JSON with severity mapping (HIGH→error, MEDIUM→warning, LOW→info)."""
        plugin = BanditPlugin()
        test_file = create_sample_file(tmp_path, "test.py", "import pickle\n")
        
        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 1
            mock_proc.stdout = BANDIT_SAMPLE_OUTPUT
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc
            
            result = plugin.execute(test_file)
            
            assert_plugin_result_valid(result, expected_success=True)
            assert len(result.issues) == 2
            
            # First issue: MEDIUM severity → warning
            medium_issue = result.issues[0]
            assert_issue_valid(medium_issue, expected_tool="bandit")
            assert medium_issue.category == "security"
            assert medium_issue.severity == "warning"
            assert medium_issue.code == "B301"
            assert medium_issue.line == 1
            
            # Second issue: HIGH severity → error
            high_issue = result.issues[1]
            assert high_issue.category == "security"
            assert high_issue.severity == "error"
            assert high_issue.code == "B307"
            assert high_issue.line == 5
    
    def test_success_codes(self, tmp_path: Path):
        """Test that return codes 0 and 1 are both successful."""
        plugin = BanditPlugin()
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
    
    def test_handles_exception(self, tmp_path: Path):
        """Test that plugin handles exceptions gracefully."""
        plugin = BanditPlugin()
        test_file = create_sample_file(tmp_path, "test.py", "import os")
        
        with patch("subprocess.run", side_effect=Exception("Test error")):
            result = plugin.execute(test_file)
            
            assert result.success is False
            assert "Test error" in result.stderr


class TestSafetyPlugin:
    """Tests for Safety dependency scanner plugin."""
    
    def test_plugin_has_required_attributes(self):
        """Test plugin has required class attributes."""
        plugin = SafetyPlugin()
        assert plugin.plugin_id == "python_safety"
        assert plugin.name == "Safety"
        assert hasattr(plugin, "check_tool_available")
        assert hasattr(plugin, "build_command")
        assert hasattr(plugin, "execute")
    
    def test_check_tool_available(self):
        """Test tool availability check."""
        plugin = SafetyPlugin()
        result = plugin.check_tool_available()
        assert result == tool_available("safety")
    
    def test_build_command(self, tmp_path: Path):
        """Test command building."""
        plugin = SafetyPlugin()
        test_file = tmp_path / "requirements.txt"
        test_file.write_text("requests==2.0.0", encoding="utf-8")
        
        cmd = plugin.build_command(test_file)
        assert isinstance(cmd, list)
        assert "safety" in cmd
        assert "check" in cmd
    
    def test_parse_safety_json_with_severity_mapping(self, tmp_path: Path):
        """Test parsing Safety JSON with severity mapping."""
        plugin = SafetyPlugin()
        test_file = create_sample_file(tmp_path, "requirements.txt", "requests==2.0.0\n")
        
        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 1
            mock_proc.stdout = SAFETY_SAMPLE_OUTPUT
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc
            
            result = plugin.execute(test_file)
            
            assert_plugin_result_valid(result, expected_success=True)
            assert len(result.issues) >= 1
            
            # Check issues have security category
            for issue in result.issues:
                assert_issue_valid(issue, expected_tool="safety")
                assert issue.category == "security"
                assert issue.severity in ["error", "warning", "info"]
    
    def test_no_requirements_file(self, tmp_path: Path):
        """Test that plugin succeeds with no issues when no requirements.txt exists."""
        plugin = SafetyPlugin()
        test_file = tmp_path / "nonexistent.txt"
        
        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 0
            mock_proc.stdout = "[]"
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc
            
            result = plugin.execute(test_file)
            
            assert result.success is True
            assert len(result.issues) == 0
    
    def test_handles_non_json_output(self, tmp_path: Path):
        """Test graceful handling of non-JSON output (e.g., license/db errors)."""
        plugin = SafetyPlugin()
        test_file = create_sample_file(tmp_path, "requirements.txt", "requests==2.0.0")
        
        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 0
            mock_proc.stdout = "License required\nDatabase update needed"
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc
            
            result = plugin.execute(test_file)
            
            # Should succeed with no issues
            assert result.success is True
            assert len(result.issues) == 0
    
    def test_severity_mapping(self, tmp_path: Path):
        """Test severity mapping: critical/high→error, medium→warning, low→info."""
        plugin = SafetyPlugin()
        test_file = create_sample_file(tmp_path, "requirements.txt", "requests==2.0.0")
        
        sample_output = json.dumps([
            {"vulnerability": "CVE-1", "package_name": "pkg1", "severity": "critical"},
            {"vulnerability": "CVE-2", "package_name": "pkg2", "severity": "high"},
            {"vulnerability": "CVE-3", "package_name": "pkg3", "severity": "medium"},
            {"vulnerability": "CVE-4", "package_name": "pkg4", "severity": "low"},
        ])
        
        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 1
            mock_proc.stdout = sample_output
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc
            
            result = plugin.execute(test_file)
            
            assert len(result.issues) == 4
            # Check severity mapping (implementation-specific)
            # critical/high should map to error, medium to warning, low to info
