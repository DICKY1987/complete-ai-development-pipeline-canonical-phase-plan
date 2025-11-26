from __future__ import annotations

from pathlib import Path

from modules.error_engine.m010004_file_hash_cache import FileHashCache


def test_file_hash_cache_roundtrip(tmp_path: Path) -> None:
    cache_path = tmp_path / "cache.json"
    f = tmp_path / "f.txt"
    f.write_text("hello", encoding="utf-8")

    cache = FileHashCache(cache_path)
    cache.load()

    # First time should be seen as changed
    assert cache.has_changed(f) is True
    cache.mark_validated(f, had_errors=False)
    cache.save()

    # Reload and verify unchanged
    cache2 = FileHashCache(cache_path)
    cache2.load()
    assert cache2.has_changed(f) is False

    # Modify file -> changed
    f.write_text("hello world", encoding="utf-8")
    assert cache2.has_changed(f) is True

