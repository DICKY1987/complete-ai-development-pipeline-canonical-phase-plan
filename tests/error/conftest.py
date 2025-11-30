"""Shared pytest fixtures for error pipeline tests."""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure repository root is in path for imports
# tests/error/conftest.py -> parents[2] = repo root
_conftest_path = Path(__file__).resolve()
_repo_root = _conftest_path.parents[2]

# Handle spaces in path by using forward slashes
_repo_root_str = str(_repo_root).replace('\\', '/')
if _repo_root_str not in sys.path:
    sys.path.insert(0, str(_repo_root))

from typing import Dict, Any

import pytest

from modules.error_engine.m010004_plugin_manager import PluginManager
from modules.error_engine.m010004_file_hash_cache import FileHashCache
from modules.error_engine.m010004_error_context import ErrorPipelineContext


@pytest.fixture
def temp_cache(tmp_path: Path) -> FileHashCache:
    """Create a temporary file hash cache for testing."""
# DOC_ID: DOC-ERROR-ERROR-CONFTEST-078
    cache_path = tmp_path / "test_cache.json"
    cache = FileHashCache(cache_path)
    cache.load()
    return cache


@pytest.fixture
def mock_plugin_manager() -> PluginManager:
    """Create a mock plugin manager with test plugins."""
    pm = PluginManager()
    return pm


@pytest.fixture
def error_context() -> ErrorPipelineContext:
    """Create a standard error context for tests."""
    return ErrorPipelineContext(
        run_id="test-run-001",
        workstream_id="test-ws-001",
        python_files=["test.py"],
        powershell_files=[],
        enable_mechanical_autofix=True,
        enable_aider=False,
        enable_codex=False,
        enable_claude=False,
        strict_mode=True,
    )


@pytest.fixture
def sample_error_report() -> Dict[str, Any]:
    """Sample error report for testing."""
    return {
        "attempt_number": 0,
        "ai_agent": "none",
        "run_id": "test-run-001",
        "workstream_id": "test-ws-001",
        "issues": [
            {
                "tool": "ruff",
                "path": "test.py",
                "line": 10,
                "column": 5,
                "code": "E501",
                "category": "style",
                "severity": "warning",
                "message": "Line too long"
            }
        ],
        "summary": {
            "total_issues": 1,
            "issues_by_tool": {"ruff": 1},
            "issues_by_category": {"style": 1},
            "has_hard_fail": False,
            "style_only": True,
            "total_errors": 0,
            "total_warnings": 1,
        }
    }


@pytest.fixture
def valid_python_file(tmp_path: Path) -> Path:
    """Create a valid Python file for testing."""
    file_path = tmp_path / "valid.py"
    file_path.write_text(
        '"""Valid Python module."""\n\n\ndef hello() -> str:\n    """Say hello."""\n    return "Hello, World!"\n',
        encoding="utf-8"
    )
    return file_path


@pytest.fixture
def broken_python_file(tmp_path: Path) -> Path:
    """Create a Python file with errors for testing."""
    file_path = tmp_path / "broken.py"
    file_path.write_text(
        '# Missing docstring\ndef bad_function(x,y,z):  # Too many args\n    return x+y+z\n',
        encoding="utf-8"
    )
    return file_path
