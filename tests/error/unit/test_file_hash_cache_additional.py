# DOC_LINK: DOC-ERROR-UNIT-TEST-FILE-HASH-CACHE-ADDITIONAL-152
# START <TestKey>
# TestType: Unit
# TargetModule: phase6_error_recovery/modules/error_engine/src/engine/file_hash_cache.py
# TargetFunction: FileHashCache.load|has_changed|mark_validated
# Purpose: Ensure cache loading, change detection, and validation bookkeeping handle edge cases
# OptimizationPattern: Fixture-Based
# CoverageGoalAchieved: 100% True
# END <TestKey>

from __future__ import annotations

import importlib
import json
import sys
import types
from pathlib import Path

import pytest

from phase6_error_recovery.modules.error_engine.src.shared.utils import (
    hashing,
)
from phase6_error_recovery.modules.error_engine.src.shared.utils import (
    time as time_utils,
)


def _alias_hash_cache_namespace(monkeypatch):
    root_mod = types.ModuleType("UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK")
    error_mod = types.ModuleType("UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error")
    shared_mod = types.ModuleType(
        "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.shared"
    )
    utils_mod = types.ModuleType(
        "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.shared.utils"
    )

    root_mod.error = error_mod
    error_mod.shared = shared_mod
    shared_mod.utils = utils_mod
    utils_mod.hashing = hashing
    utils_mod.time = time_utils

    monkeypatch.setitem(
        sys.modules, "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK", root_mod
    )
    monkeypatch.setitem(
        sys.modules, "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error", error_mod
    )
    monkeypatch.setitem(
        sys.modules, "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.shared", shared_mod
    )
    monkeypatch.setitem(
        sys.modules,
        "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.shared.utils",
        utils_mod,
    )
    monkeypatch.setitem(
        sys.modules,
        "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.shared.utils.hashing",
        hashing,
    )
    monkeypatch.setitem(
        sys.modules,
        "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.shared.utils.time",
        time_utils,
    )


@pytest.fixture
def file_hash_cache_module(monkeypatch):
    _alias_hash_cache_namespace(monkeypatch)
    import phase6_error_recovery.modules.error_engine.src.engine.file_hash_cache as fhc

    return importlib.reload(fhc)


def test_load_handles_missing_and_corrupt(tmp_path, file_hash_cache_module):
    cache_path = tmp_path / "cache.json"
    cache = file_hash_cache_module.FileHashCache(cache_path)

    cache.load()
    assert cache.cache == {}

    cache_path.write_text("{invalid", encoding="utf-8")
    cache.load()
    assert cache.cache == {}


def test_has_changed_updates_cache_and_detects_match(
    monkeypatch, tmp_path, file_hash_cache_module
):
    cache_path = tmp_path / "cache.json"
    cache = file_hash_cache_module.FileHashCache(cache_path)
    file_path = tmp_path / "file.txt"
    file_path.write_text("content", encoding="utf-8")

    monkeypatch.setattr(file_hash_cache_module, "sha256_file", lambda _: "hash1")
    monkeypatch.setattr(file_hash_cache_module, "utc_now_iso", lambda: "stamp1")

    assert cache.has_changed(file_path) is True
    key = str(file_path.resolve())
    assert cache.cache[key]["hash"] == "hash1"
    assert cache.cache[key]["last_validated"] == "stamp1"

    # No change when hash matches cache
    monkeypatch.setattr(file_hash_cache_module, "sha256_file", lambda _: "hash1")
    assert cache.has_changed(file_path) is False

    # Detect change when hash differs
    monkeypatch.setattr(file_hash_cache_module, "sha256_file", lambda _: "hash2")
    monkeypatch.setattr(file_hash_cache_module, "utc_now_iso", lambda: "stamp2")
    assert cache.has_changed(file_path) is True
    assert cache.cache[key]["hash"] == "hash2"
    assert cache.cache[key]["last_validated"] == "stamp2"

    # Missing file treated as changed
    missing_path = tmp_path / "missing.txt"
    assert cache.has_changed(missing_path) is True


def test_mark_validated_records_metadata(monkeypatch, tmp_path, file_hash_cache_module):
    cache = file_hash_cache_module.FileHashCache(tmp_path / "cache.json")
    file_path = tmp_path / "file.txt"
    file_path.write_text("data", encoding="utf-8")

    monkeypatch.setattr(file_hash_cache_module, "sha256_file", lambda _: "hash3")
    monkeypatch.setattr(file_hash_cache_module, "utc_now_iso", lambda: "stamp3")

    cache.mark_validated(file_path, had_errors=True)

    key = str(file_path.resolve())
    assert cache.cache[key]["hash"] == "hash3"
    assert cache.cache[key]["last_validated"] == "stamp3"
    assert cache.cache[key]["had_errors"] is True
