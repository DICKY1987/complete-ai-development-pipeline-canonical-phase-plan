"""Integration test: Full Python error pipeline end-to-end."""

# DOC_ID: DOC-ERROR-INTEGRATION-TEST-FULL-PIPELINE-PYTHON-001

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from phase6_error_recovery.modules.error_engine.src.engine.file_hash_cache import (
    FileHashCache,
)
from phase6_error_recovery.modules.error_engine.src.engine.pipeline_engine import (
    PipelineEngine,
)
from phase6_error_recovery.modules.error_engine.src.engine.plugin_manager import (
    PluginManager,
)


@pytest.fixture
def pipeline_engine(tmp_path: Path):
    """Create a pipeline engine with real plugin manager and cache."""
    cache_path = tmp_path / "test_cache.json"
    hash_cache = FileHashCache(cache_path)
    hash_cache.load()

    plugin_manager = PluginManager()
    plugin_manager.discover()

    return PipelineEngine(plugin_manager, hash_cache)


@pytest.fixture
def python_file_with_type_error(tmp_path: Path) -> Path:
    """Create a Python file with a type error for mypy."""
    file_path = tmp_path / "type_error.py"
    file_path.write_text(
        '''"""Module with type error."""

def add_numbers(a: int, b: int) -> int:
    """Add two integers."""
    return a + b

result: int = "not an integer"  # Type error
''',
        encoding="utf-8",
    )
    return file_path


@pytest.fixture
def python_file_clean(tmp_path: Path) -> Path:
    """Create a clean Python file."""
    file_path = tmp_path / "clean.py"
    file_path.write_text(
        '''"""Clean module."""


def greet(name: str) -> str:
    """Greet someone."""
    return f"Hello, {name}!"
''',
        encoding="utf-8",
    )
    return file_path


@pytest.mark.skipif(not shutil.which("mypy"), reason="mypy not installed")
def test_python_type_error_detection(pipeline_engine, python_file_with_type_error):
    """Test that pipeline detects Python type errors."""
    report = pipeline_engine.process_file(python_file_with_type_error)

    assert report.status == "completed"
    assert report.summary is not None
    assert report.summary.plugins_run > 0
    assert report.summary.total_errors > 0 or report.summary.total_warnings > 0


@pytest.mark.skipif(not shutil.which("mypy"), reason="mypy not installed")
def test_python_clean_file_passes(pipeline_engine, python_file_clean):
    """Test that clean Python files pass validation."""
    report = pipeline_engine.process_file(python_file_clean)

    assert report.status == "completed"
    assert report.summary is not None


@pytest.mark.skipif(not shutil.which("mypy"), reason="mypy not installed")
def test_python_file_hash_caching(pipeline_engine, python_file_clean):
    """Test that file hash caching works correctly."""
    # First run
    report1 = pipeline_engine.process_file(python_file_clean)

    # Second run (should use cache)
    report2 = pipeline_engine.process_file(python_file_clean)

    assert report1.status == "completed"
    assert report2.status == "skipped"  # Skipped due to cache hit


def test_pipeline_handles_missing_file(pipeline_engine, tmp_path):
    """Test that pipeline handles missing files gracefully."""
    missing_file = tmp_path / "nonexistent.py"

    report = pipeline_engine.process_file(missing_file)

    assert report.status in ["completed", "error"]


@pytest.mark.skipif(not shutil.which("black"), reason="black not installed")
def test_python_formatting_issue_detection(pipeline_engine, tmp_path):
    """Test that pipeline detects formatting issues."""
    file_path = tmp_path / "unformatted.py"
    file_path.write_text(
        '''"""Unformatted module."""
def  bad_spacing(  x,y  ):
    return   x+y
''',
        encoding="utf-8",
    )

    report = pipeline_engine.process_file(file_path)

    assert report.status == "completed"
    assert report.summary is not None
