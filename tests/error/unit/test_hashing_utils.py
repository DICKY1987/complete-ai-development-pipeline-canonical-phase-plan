# START <TestKey>
# TestType: Unit
# TargetModule: phase6_error_recovery/modules/error_engine/src/shared/utils/hashing.py
# TargetFunction: sha256_file
# Purpose: Verify deterministic hashing across single and multi-chunk reads
# OptimizationPattern: Fixture-Based
# CoverageGoalAchieved: 100% True
# END <TestKey>

from __future__ import annotations

import hashlib

from phase6_error_recovery.modules.error_engine.src.shared.utils.hashing import (
    sha256_file,
)


def test_sha256_file_small(tmp_path):
    target = tmp_path / "small.txt"
    target.write_text("hello world", encoding="utf-8")

    expected = hashlib.sha256(target.read_bytes()).hexdigest()

    assert sha256_file(target) == expected


def test_sha256_file_multiple_chunks(tmp_path):
    # Force multiple 1MB reads to exercise the chunked iterator.
    target = tmp_path / "large.bin"
    target.write_bytes(b"a" * (1024 * 1024 + 7))

    expected = hashlib.sha256(target.read_bytes()).hexdigest()

    assert sha256_file(target) == expected
