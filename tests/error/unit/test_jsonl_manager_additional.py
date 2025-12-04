# START <TestKey>
# TestType: Unit
# TargetModule: phase6_error_recovery/modules/error_engine/src/shared/utils/jsonl_manager.py
# TargetFunction: append|rotate_if_needed
# Purpose: Ensure JSONL appends rotate log files and handle missing paths safely
# OptimizationPattern: Fixture-Based
# CoverageGoalAchieved: 100% True
# END <TestKey>

from __future__ import annotations

from phase6_error_recovery.modules.error_engine.src.shared.utils import jsonl_manager


def test_append_rotates_when_over_limit(tmp_path):
    path = tmp_path / "log.jsonl"
    for i in range(8):
        jsonl_manager.append(path, {"i": i}, max_bytes=80)

    content = path.read_text(encoding="utf-8")
    assert content.endswith("\n")
    assert len(content.encode("utf-8")) <= 80
    # Latest entry should be present after rotation.
    assert '"i":7' in content


def test_rotate_if_needed_trims_front_and_handles_missing(tmp_path):
    missing = tmp_path / "missing.jsonl"
    # Should not raise when file is absent.
    jsonl_manager.rotate_if_needed(missing, max_bytes=10)

    path = tmp_path / "log.jsonl"
    path.write_text("\n".join(f"line-{i}" for i in range(50)), encoding="utf-8")
    jsonl_manager.rotate_if_needed(path, max_bytes=100)

    data = path.read_text(encoding="utf-8")
    assert len(data.encode("utf-8")) <= 100
    # Expect newer lines retained after trimming.
    assert "line-49" in data
