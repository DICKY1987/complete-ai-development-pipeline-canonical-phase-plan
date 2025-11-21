from __future__ import annotations

from pathlib import Path

from error.engine.pipeline_engine import PipelineEngine
from error.engine.plugin_manager import PluginManager
from error.engine.file_hash_cache import FileHashCache


def test_engine_skip_on_unchanged(tmp_path: Path) -> None:
    # Prepare a file and engine with isolated cache
    f = tmp_path / "a.py"
    f.write_text("print('hi')\n", encoding="utf-8")

    cache_path = tmp_path / "cache.json"
    cache = FileHashCache(cache_path)
    cache.load()

    pm = PluginManager()
    engine = PipelineEngine(pm, cache)

    r1 = engine.process_file(f)
    assert r1.status == "completed"

    r2 = engine.process_file(f)
    assert r2.status == "skipped"

