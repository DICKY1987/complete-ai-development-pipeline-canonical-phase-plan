"""
Common test fixtures and utilities for plugin testing.
"""
DOC_ID: DOC-TEST-PLUGINS-CONFTEST-140
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_subprocess_success():
    """Mock successful subprocess run."""
    mock = MagicMock()
    mock.returncode = 0
    mock.stdout = ""
    mock.stderr = ""
    return mock


@pytest.fixture
def mock_subprocess_with_issues():
    """Mock subprocess run with issues found."""
    mock = MagicMock()
    mock.returncode = 1
    mock.stdout = ""
    mock.stderr = ""
    return mock


def tool_available(tool_name: str) -> bool:
    """Check if a tool is available on the system."""
    return shutil.which(tool_name) is not None


def skip_if_tool_missing(tool_name: str):
    """Pytest marker to skip test if tool is not installed."""
    return pytest.mark.skipif(
        not tool_available(tool_name),
        reason=f"{tool_name} not installed"
    )


def create_sample_file(tmp_path: Path, filename: str, content: str) -> Path:
    """Create a sample file for testing."""
    file_path = tmp_path / filename
    file_path.write_text(content, encoding="utf-8")
    return file_path


def assert_plugin_result_valid(result, expected_success: bool = True):
    """Assert that a PluginResult has expected structure."""
    assert hasattr(result, "plugin_id")
    assert hasattr(result, "success")
    assert hasattr(result, "issues")
    assert hasattr(result, "stdout")
    assert hasattr(result, "stderr")
    assert hasattr(result, "returncode")
    assert result.success == expected_success
    assert isinstance(result.issues, list)


def assert_issue_valid(issue, expected_tool: str = None):
    """Assert that a PluginIssue has expected structure."""
    assert hasattr(issue, "tool")
    assert hasattr(issue, "path")
    assert hasattr(issue, "category")
    assert hasattr(issue, "severity")
    assert hasattr(issue, "message")
    
    if expected_tool:
        assert issue.tool == expected_tool
    
    # Category should be one of the allowed values
    if issue.category:
        assert issue.category in ["syntax", "style", "type", "security", "test_failure"]
    
    # Severity should be one of the allowed values
    if issue.severity:
        assert issue.severity in ["error", "warning", "info"]
