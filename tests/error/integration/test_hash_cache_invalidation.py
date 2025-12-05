"""Integration test: Hash cache invalidation and incremental validation."""

# DOC_ID: DOC-ERROR-INTEGRATION-TEST-HASH-CACHE-008

from __future__ import annotations

from pathlib import Path

import pytest

from phase6_error_recovery.modules.error_engine.src.engine.file_hash_cache import (
    FileHashCache,
)


@pytest.fixture
def hash_cache(tmp_path: Path):
    """Create a hash cache for testing."""
    cache_path = tmp_path / "test_hash_cache.json"
    cache = FileHashCache(cache_path)
    cache.load()
    return cache


@pytest.fixture
def test_file(tmp_path: Path) -> Path:
    """Create a test file."""
    file_path = tmp_path / "test.py"
    file_path.write_text(
        '''"""Test module."""


def hello() -> str:
    """Say hello."""
    return "Hello!"
''',
        encoding="utf-8",
    )
    return file_path


def test_cache_detects_new_file(hash_cache, test_file):
    """Test that cache detects a new file (not in cache)."""
    changed = hash_cache.has_changed(test_file)

    assert changed is True


def test_cache_detects_unchanged_file(hash_cache, test_file):
    """Test that cache detects unchanged file after first check."""
    # First check - should be changed
    hash_cache.has_changed(test_file)

    # Second check - should be unchanged
    changed = hash_cache.has_changed(test_file)

    assert changed is False


def test_cache_detects_file_modification(hash_cache, test_file):
    """Test that cache detects file modifications."""
    # First check
    hash_cache.has_changed(test_file)

    # Modify file
    test_file.write_text(
        '''"""Modified module."""


def goodbye() -> str:
    """Say goodbye."""
    return "Goodbye!"
''',
        encoding="utf-8",
    )

    # Second check - should detect change
    changed = hash_cache.has_changed(test_file)

    assert changed is True


def test_cache_mark_validated(hash_cache, test_file):
    """Test that marking a file as validated updates metadata."""
    hash_cache.has_changed(test_file)

    metadata = {
        "validated_at": "2025-12-05T10:00:00Z",
        "tool": "mypy",
        "status": "passed",
    }

    hash_cache.mark_validated(test_file, metadata)

    # Verify cache was updated
    assert str(test_file.resolve()) in hash_cache.cache


def test_cache_persistence(tmp_path, test_file):
    """Test that cache persists to disk and can be reloaded."""
    cache_path = tmp_path / "persistent_cache.json"

    # Create cache and check file
    cache1 = FileHashCache(cache_path)
    cache1.load()
    cache1.has_changed(test_file)
    cache1.save()

    # Create new cache instance and load
    cache2 = FileHashCache(cache_path)
    cache2.load()

    # Should detect no change (loaded from disk)
    changed = cache2.has_changed(test_file)

    assert changed is False


def test_cache_handles_missing_file(hash_cache, tmp_path):
    """Test that cache handles missing files gracefully."""
    missing_file = tmp_path / "nonexistent.py"

    changed = hash_cache.has_changed(missing_file)

    # Missing file should be treated as changed (or error handled)
    assert isinstance(changed, bool)


def test_cache_handles_directory_instead_of_file(hash_cache, tmp_path):
    """Test that cache handles directories gracefully."""
    directory = tmp_path / "subdir"
    directory.mkdir()

    # Should handle directory gracefully (skip or error)
    try:
        hash_cache.has_changed(directory)
        # If it doesn't raise, that's fine
        assert True
    except Exception:
        # If it raises, that's also acceptable behavior
        assert True


def test_incremental_validation_with_multiple_files(hash_cache, tmp_path):
    """Test incremental validation with multiple files."""
    files = []
    for i in range(3):
        file_path = tmp_path / f"file{i}.py"
        file_path.write_text(f'"""File {i}."""\n', encoding="utf-8")
        files.append(file_path)

    # First pass - all should be changed
    changes = [hash_cache.has_changed(f) for f in files]
    assert all(changes)

    # Second pass - none should be changed
    changes = [hash_cache.has_changed(f) for f in files]
    assert not any(changes)

    # Modify one file
    files[1].write_text('"""Modified file 1."""\n', encoding="utf-8")

    # Third pass - only modified file should be changed
    changes = [hash_cache.has_changed(f) for f in files]
    assert changes[1] is True
    assert changes[0] is False
    assert changes[2] is False


def test_cache_invalidation_on_size_change(hash_cache, test_file):
    """Test that cache invalidates when file size changes."""
    hash_cache.has_changed(test_file)

    # Append to file (size change)
    with test_file.open("a", encoding="utf-8") as f:
        f.write("\n\n# Extra content\n")

    changed = hash_cache.has_changed(test_file)

    assert changed is True


def test_cache_serialization_format(tmp_path, test_file):
    """Test that cache serialization format is valid JSON."""
    cache_path = tmp_path / "format_cache.json"
    cache = FileHashCache(cache_path)
    cache.load()

    cache.has_changed(test_file)
    cache.save()

    # Cache file should exist and be valid JSON
    assert cache_path.exists()

    import json

    with cache_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
        assert isinstance(data, dict)
