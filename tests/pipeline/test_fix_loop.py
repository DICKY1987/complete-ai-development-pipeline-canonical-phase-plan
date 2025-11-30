# DOC_LINK: DOC-TEST-PIPELINE-TEST-FIX-LOOP-136
import os
from types import SimpleNamespace

import pytest

from modules.core_state import m010003_db
from core import orchestrator


@pytest.fixture(autouse=True)
def init_db_tmp(tmp_path, monkeypatch):
    # Point DB to a temp location for isolation
    db_path = tmp_path / "state.db"
    monkeypatch.setenv("PIPELINE_DB_PATH", str(db_path))
    db.init_db()
    yield


@pytest.fixture
def bundle_ws():
    return SimpleNamespace(
        id="ws-fix",
        openspec_change="OS-FIX",
        ccpm_issue=1,
        gate=1,
        files_scope=("src/app.py",),
        files_create=("src/app.py",),
        tasks=("do thing",),
        acceptance_tests=("pytest -q",),
        depends_on=(),
        tool="aider",
        circuit_breaker=None,
        metadata=None,
    )


def test_static_fix_succeeds(monkeypatch, bundle_ws):
    # Simulate: first static fails, then after fix it succeeds
    calls = {"static": 0, "fix": 0}

    # Make EDIT succeed
    monkeypatch.setattr(
        "src.pipeline.prompts.run_aider_edit",
        lambda run, ws, b, ctx, run_id=None, ws_id=None: __import__("types").SimpleNamespace(to_dict=lambda: {"ok": True}, success=True),
    )

    def fake_static(run_id, ws_id, b, ctx):
        calls["static"] += 1
        ok = calls["static"] >= 2
        details = {"results": [{"tool_id": "pytest", "stdout": "", "stderr": "E", "success": ok}]}
        return orchestrator.StepResult(orchestrator.STEP_STATIC, ok, details)

    monkeypatch.setattr("src.pipeline.orchestrator.run_static_step", fake_static)
    monkeypatch.setattr(
        "src.pipeline.prompts.run_aider_fix",
        lambda run, ws, b, errors, context, run_id=None, ws_id=None: __import__("types").SimpleNamespace(to_dict=lambda: {"ok": True}),
    )

    res = orchestrator.run_workstream("run-fix-1", bundle_ws.id, bundle_ws, context={})
    assert res["final_status"] == "done"


def test_runtime_fix_exhausts(monkeypatch, bundle_ws):
    # Simulate: runtime always fails; breaker stops further attempts
    calls = {"runtime": 0}

    def fake_runtime(run_id, ws_id, b, ctx):
        calls["runtime"] += 1
        details = {"stdout": "", "stderr": "FAIL", "success": False}
        return orchestrator.StepResult(orchestrator.STEP_RUNTIME, False, details)

    # Make edit/static succeed quickly
    monkeypatch.setattr(
        "src.pipeline.prompts.run_aider_edit",
        lambda run, ws, b, ctx, run_id=None, ws_id=None: __import__("types").SimpleNamespace(to_dict=lambda: {"ok": True}, success=True),
    )
    monkeypatch.setattr("src.pipeline.orchestrator.run_static_step", lambda *a, **k: orchestrator.StepResult(orchestrator.STEP_STATIC, True, {}))
    monkeypatch.setattr("src.pipeline.orchestrator.run_runtime_step", fake_runtime)

    res = orchestrator.run_workstream("run-fix-2", bundle_ws.id, bundle_ws, context={})
    assert res["final_status"] == "failed"
    # Should not loop indefinitely; at most defaults allow 2 fix attempts after first
    assert calls["runtime"] <= 3

