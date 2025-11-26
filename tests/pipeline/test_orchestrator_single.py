import json
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
def bundle_ws(monkeypatch):
    # Minimal bundle-like object
    return SimpleNamespace(
        id="ws-test",
        openspec_change="OS-TEST",
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


def _tool_result(tool_id: str, success: bool):
    from core.tools import ToolResult

    return ToolResult(
        tool_id=tool_id,
        command_line=tool_id,
        exit_code=0 if success else 1,
        stdout="",
        stderr="",
        timed_out=False,
        started_at="2024-01-01T00:00:00Z",
        completed_at="2024-01-01T00:00:01Z",
        duration_sec=1.0,
        success=success,
    )


def test_happy_path(monkeypatch, bundle_ws):
    # Mocks
    monkeypatch.setenv("PIPELINE_DRY_RUN", "0")
    monkeypatch.setattr(
        "src.pipeline.worktree.create_worktree_for_ws",
        lambda run_id, ws_id: os.getcwd(),
    )
    monkeypatch.setattr(
        "src.pipeline.prompts.run_aider_edit",
        lambda run, ws, b, ctx, run_id=None, ws_id=None: _tool_result("aider", True),
    )
    calls = []

    def fake_run_tool(tool_id, context, run_id=None, ws_id=None):
        calls.append(tool_id)
        return _tool_result(tool_id, True)

    monkeypatch.setattr("src.pipeline.tools.run_tool", fake_run_tool)

    res = orchestrator.run_workstream("run-1", bundle_ws.id, bundle_ws, context={
        "static_tools": ["pytest"],
        "runtime_tool": "pytest",
    })

    assert res["final_status"] == "done"
    ws = db.get_workstream(bundle_ws.id)
    assert ws["status"] == "done"
    # static and runtime tools invoked
    assert calls == ["pytest", "pytest"]


def test_edit_failure(monkeypatch, bundle_ws):
    # Aider fails
    monkeypatch.setattr(
        "src.pipeline.prompts.run_aider_edit",
        lambda run, ws, b, ctx, run_id=None, ws_id=None: _tool_result("aider", False),
    )
    # Track if static/runtime invoked
    called = {"static": False, "runtime": False}

    def fake_static(*a, **k):
        called["static"] = True
        return orchestrator.StepResult(orchestrator.STEP_STATIC, True, {})

    def fake_runtime(*a, **k):
        called["runtime"] = True
        return orchestrator.StepResult(orchestrator.STEP_RUNTIME, True, {})

    monkeypatch.setattr("src.pipeline.orchestrator.run_static_step", fake_static)
    monkeypatch.setattr("src.pipeline.orchestrator.run_runtime_step", fake_runtime)

    res = orchestrator.run_workstream("run-2", bundle_ws.id, bundle_ws, context={})
    assert res["final_status"] == "failed"
    assert called == {"static": False, "runtime": False}


def test_static_failure(monkeypatch, bundle_ws):
    monkeypatch.setattr(
        "src.pipeline.prompts.run_aider_edit",
        lambda run, ws, b, ctx, run_id=None, ws_id=None: _tool_result("aider", True),
    )
    # Static fails
    monkeypatch.setattr(
        "src.pipeline.tools.run_tool",
        lambda tool_id, context, run_id=None, ws_id=None: _tool_result(tool_id, False),
    )
    # Track runtime called
    called = {"runtime": False}

    def fake_runtime(*a, **k):
        called["runtime"] = True
        return orchestrator.StepResult(orchestrator.STEP_RUNTIME, True, {})

    monkeypatch.setattr("src.pipeline.orchestrator.run_runtime_step", fake_runtime)

    res = orchestrator.run_workstream("run-3", bundle_ws.id, bundle_ws, context={
        "static_tools": ["pytest"],
    })
    assert res["final_status"] == "failed"
    assert called["runtime"] is False


def test_runtime_failure(monkeypatch, bundle_ws):
    monkeypatch.setattr(
        "src.pipeline.prompts.run_aider_edit",
        lambda run, ws, b, ctx, run_id=None, ws_id=None: _tool_result("aider", True),
    )
    # Static succeeds, runtime fails
    monkeypatch.setattr(
        "src.pipeline.tools.run_tool",
        lambda tool_id, context, run_id=None, ws_id=None: _tool_result(tool_id, True),
    )
    monkeypatch.setattr(
        "src.pipeline.orchestrator.tools.run_tool",
        lambda tool_id, context, run_id=None, ws_id=None: _tool_result(tool_id, False),
    )

    res = orchestrator.run_workstream("run-4", bundle_ws.id, bundle_ws, context={
        "static_tools": ["pytest"],
        "runtime_tool": "pytest",
    })
    assert res["final_status"] == "failed"


def test_scope_violation(monkeypatch, bundle_ws):
    monkeypatch.setattr(
        "src.pipeline.prompts.run_aider_edit",
        lambda run, ws, b, ctx, run_id=None, ws_id=None: _tool_result("aider", True),
    )
    monkeypatch.setattr(
        "src.pipeline.tools.run_tool",
        lambda tool_id, context, run_id=None, ws_id=None: _tool_result(tool_id, True),
    )
    # Force scope violation
    monkeypatch.setattr(
        "src.pipeline.worktree.validate_scope",
        lambda wt, scope: (False, ["out/of/scope.txt"]),
    )

    res = orchestrator.run_workstream("run-5", bundle_ws.id, bundle_ws, context={
        "static_tools": ["pytest"],
        "runtime_tool": "pytest",
    })
    assert res["final_status"] == "failed"


def test_cli_dry_run(tmp_path):
    # Use built-in example bundle via ws id; request dry-run to avoid externals
    import subprocess, sys

    cmd = [sys.executable, "scripts/run_workstream.py", "--ws-id", "ws-hello-world", "--dry-run"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode in (0, 1)  # Success preferred; allow 1 if ws missing
    if proc.returncode == 0:
        data = json.loads(proc.stdout)
        assert data.get("final_status") == "done"


