# START <TestKey>
# TestType: Unit
# TargetModule: phase6_error_recovery/modules/error_engine/src/shared/utils/time.py
# TargetFunction: utc_now_iso|new_run_id
# Purpose: Cover deterministic timestamp formatting and ULID fallback behavior
# OptimizationPattern: Fixture-Based
# CoverageGoalAchieved: 100% True
# END <TestKey>

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

from phase6_error_recovery.modules.error_engine.src.shared.utils import (
    time as time_utils,
)


def test_utc_now_iso_uses_utc(monkeypatch):
    fixed = datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    monkeypatch.setattr(
        time_utils, "datetime", SimpleNamespace(now=lambda tz=None: fixed)
    )

    assert time_utils.utc_now_iso() == "2024-01-02T03:04:05+00:00".replace(
        "+00:00", "Z"
    )


def test_new_run_id_prefers_ulid_and_falls_back(monkeypatch):
    monkeypatch.setattr(time_utils, "ulid", SimpleNamespace(new=lambda: "ULID-VALUE"))
    assert time_utils.new_run_id() == "ULID-VALUE"

    class BrokenDatetime:
        @staticmethod
        def now(tz=None):
            return datetime(2023, 5, 6, 7, 8, 9, tzinfo=timezone.utc)

        @staticmethod
        def strftime(*args, **kwargs):
            return datetime.strftime(*args, **kwargs)

    monkeypatch.setattr(
        time_utils,
        "ulid",
        SimpleNamespace(new=lambda: (_ for _ in ()).throw(RuntimeError("boom"))),
    )
    monkeypatch.setattr(time_utils, "datetime", BrokenDatetime)

    assert time_utils.new_run_id() == "20230506T070809Z"
