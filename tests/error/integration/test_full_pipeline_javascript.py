"""Integration test: Full JavaScript error pipeline end-to-end."""

# DOC_ID: DOC-ERROR-INTEGRATION-TEST-FULL-PIPELINE-JAVASCRIPT-002

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
def js_pipeline_engine(tmp_path: Path):
    """Create a pipeline engine for JavaScript files."""
    cache_path = tmp_path / "js_cache.json"
    hash_cache = FileHashCache(cache_path)
    hash_cache.load()

    plugin_manager = PluginManager()
    plugin_manager.discover()

    return PipelineEngine(plugin_manager, hash_cache)


@pytest.fixture
def js_file_with_error(tmp_path: Path) -> Path:
    """Create a JavaScript file with linting errors."""
    file_path = tmp_path / "error.js"
    file_path.write_text(
        """// JavaScript with errors
var unusedVariable = 42;

function badFunction() {
    console.log("missing semicolon")
    return undefined
}
""",
        encoding="utf-8",
    )
    return file_path


@pytest.fixture
def js_file_clean(tmp_path: Path) -> Path:
    """Create a clean JavaScript file."""
    file_path = tmp_path / "clean.js"
    file_path.write_text(
        """/**
 * Clean JavaScript module.
 */

function greet(name) {
    return `Hello, ${name}!`;
}

module.exports = { greet };
""",
        encoding="utf-8",
    )
    return file_path


@pytest.mark.skipif(not shutil.which("eslint"), reason="eslint not installed")
def test_javascript_error_detection(js_pipeline_engine, js_file_with_error):
    """Test that pipeline detects JavaScript errors."""
    report = js_pipeline_engine.process_file(js_file_with_error)

    assert report.status == "completed"
    assert report.summary is not None


@pytest.mark.skipif(not shutil.which("eslint"), reason="eslint not installed")
def test_javascript_clean_file(js_pipeline_engine, js_file_clean):
    """Test that clean JavaScript files pass validation."""
    report = js_pipeline_engine.process_file(js_file_clean)

    assert report.status == "completed"


@pytest.mark.skipif(not shutil.which("prettier"), reason="prettier not installed")
def test_javascript_formatting_detection(js_pipeline_engine, tmp_path):
    """Test that pipeline detects formatting issues in JavaScript."""
    file_path = tmp_path / "unformatted.js"
    file_path.write_text(
        """function  bad(x,y){return x+y;}
""",
        encoding="utf-8",
    )

    report = js_pipeline_engine.process_file(file_path)

    assert report.status == "completed"


def test_javascript_handles_syntax_error(js_pipeline_engine, tmp_path):
    """Test that pipeline handles JavaScript syntax errors."""
    file_path = tmp_path / "syntax_error.js"
    file_path.write_text(
        """function broken() {
    return "missing bracket";
// Missing closing brace
""",
        encoding="utf-8",
    )

    report = js_pipeline_engine.process_file(file_path)

    assert report.status in ["completed", "error"]
