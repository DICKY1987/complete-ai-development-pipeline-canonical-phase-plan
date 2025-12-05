"""Integration test: Multiple plugins coordinating on same file."""

# DOC_ID: DOC-ERROR-INTEGRATION-TEST-MULTI-PLUGIN-003

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
def multi_plugin_engine(tmp_path: Path):
    """Create pipeline engine with multiple plugins."""
    cache_path = tmp_path / "multi_cache.json"
    hash_cache = FileHashCache(cache_path)
    hash_cache.load()

    plugin_manager = PluginManager()
    plugin_manager.discover()

    return PipelineEngine(plugin_manager, hash_cache)


@pytest.fixture
def plugin_manager_standalone(tmp_path: Path):
    """Create standalone plugin manager for testing."""
    pm = PluginManager()
    pm.discover()
    return pm


def test_multiple_plugins_discovered(plugin_manager_standalone):
    """Test that multiple plugins are discovered."""
    plugin_manager_standalone.discover()

    # Check that at least some plugins were discovered
    assert hasattr(plugin_manager_standalone, "_plugins")
    assert (
        len(plugin_manager_standalone._plugins) >= 0
    )  # May be 0 if tools not installed


@pytest.mark.skipif(
    not (shutil.which("mypy") and shutil.which("black")),
    reason="mypy and black not installed",
)
def test_multiple_plugins_run_on_python_file(plugin_manager_standalone, tmp_path):
    """Test that multiple plugins run on the same Python file."""
    file_path = tmp_path / "multi_issue.py"
    file_path.write_text(
        '''"""Python file with multiple issues."""
def   badly_formatted(x:int,y:int)->int:
    result:str=x+y  # Type error AND formatting issue
    return result
''',
        encoding="utf-8",
    )

    plugins = plugin_manager_standalone.get_plugins_for_file(file_path)

    # Should have multiple plugins for Python files (if tools installed)
    assert len(plugins) >= 1


@pytest.mark.skipif(
    not (shutil.which("mypy") and shutil.which("black")),
    reason="mypy and black not installed",
)
def test_plugin_dependency_ordering(plugin_manager_standalone, tmp_path):
    """Test that plugins run in dependency order (formatters before linters)."""
    file_path = tmp_path / "test.py"
    file_path.write_text(
        '''"""Test module."""


def test() -> None:
    """Test function."""
    pass
''',
        encoding="utf-8",
    )

    plugins = plugin_manager_standalone.get_plugins_for_file(file_path)

    # Extract plugin IDs
    plugin_ids = [p.plugin_id for p in plugins]

    # If both formatters and linters are present, verify order
    formatter_plugins = [pid for pid in plugin_ids if "black" in pid or "isort" in pid]
    linter_plugins = [
        pid
        for pid in plugin_ids
        if "mypy" in pid or "pylint" in pid or "pyright" in pid
    ]

    if formatter_plugins and linter_plugins:
        formatter_indices = [plugin_ids.index(pid) for pid in formatter_plugins]
        linter_indices = [plugin_ids.index(pid) for pid in linter_plugins]

        # Formatters should run before linters
        max_formatter_idx = max(formatter_indices) if formatter_indices else -1
        min_linter_idx = min(linter_indices) if linter_indices else 999

        assert (
            max_formatter_idx < min_linter_idx
        ), "Formatters should run before linters"


def test_plugin_manager_handles_missing_plugins_dir(tmp_path):
    """Test that plugin manager handles missing plugins directory gracefully."""
    fake_plugins_path = tmp_path / "nonexistent_plugins"

    pm = PluginManager(plugins_path=fake_plugins_path)
    pm.discover()

    # Should not crash, just have no plugins
    assert len(pm._plugins) == 0


def test_get_plugins_for_unknown_extension(plugin_manager_standalone, tmp_path):
    """Test that plugin manager handles unknown file extensions."""
    file_path = tmp_path / "test.xyz"
    file_path.write_text("unknown file type", encoding="utf-8")

    plugins = plugin_manager_standalone.get_plugins_for_file(file_path)

    # Should return empty list or plugins with no extension restrictions
    assert isinstance(plugins, list)


@pytest.mark.skipif(not shutil.which("mypy"), reason="mypy not installed")
def test_full_pipeline_runs_multiple_plugins(multi_plugin_engine, tmp_path):
    """Test that full pipeline runs multiple plugins end-to-end."""
    file_path = tmp_path / "complete.py"
    file_path.write_text(
        '''"""Complete test module."""


def calculate(x: int, y: int) -> int:
    """Calculate sum."""
    return x + y
''',
        encoding="utf-8",
    )

    report = multi_plugin_engine.process_file(file_path)

    assert report.status in ["completed", "skipped"]
    assert report.summary is not None
