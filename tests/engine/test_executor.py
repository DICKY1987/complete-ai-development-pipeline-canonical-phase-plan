from __future__ import annotations

"""Executor integration smoke tests for Phase 5 execution."""
# DOC_ID: DOC-TEST-ENGINE-EXECUTOR-FLOW-300

import time
from pathlib import Path

from core.engine.executor import AdapterResult, Executor
from core.engine.orchestrator import Orchestrator
from core.engine.process_spawner import ProcessSpawner
from core.engine.scheduler import ExecutionScheduler, Task
from core.state.db import Database


class StubRouter:
    """Simple router stub used for executor tests."""

    def __init__(self, tool_id: str | None = "aider"):
        self.tool_id = tool_id

    def route_task(self, task_kind: str, **_: str) -> str | None:
        return self.tool_id


def _make_db(tmp_path: Path) -> Database:
    db = Database(str(tmp_path / "executor.db"))
    db.connect()
    return db


def test_executor_runs_task_and_updates_state(tmp_path):
    """Happy path: task routed, adapter succeeds, run completes."""
    db = _make_db(tmp_path)
    orch = Orchestrator(db)
    router = StubRouter()
    scheduler = ExecutionScheduler()

    task = Task("T1", "code_edit", metadata={"description": "Fix bug"})
    scheduler.add_task(task)

    run_id = orch.create_run("PRJ-1", "PH-05")

    def adapter(task_obj: Task, tool_id: str) -> AdapterResult:
        assert tool_id == "aider"
        return AdapterResult(exit_code=0, output_patch_id=f"{task_obj.task_id}-patch")

    gate_calls = []

    def gate_callback(run: str, task_obj: Task, result: AdapterResult) -> bool:
        gate_calls.append((run, task_obj.task_id, result.output_patch_id))
        return True

    executor = Executor(orch, router, scheduler, adapter, gate_callback)
    summary = executor.run(run_id)

    assert summary["state"] == "succeeded"
    run = orch.get_run_status(run_id)
    assert run["state"] == "succeeded"

    steps = db.list_step_attempts(run_id)
    assert len(steps) == 1
    assert steps[0]["state"] == "succeeded"
    assert steps[0]["output_patch_id"] == "T1-patch"
    assert gate_calls == [(run_id, "T1", "T1-patch")]


def test_executor_marks_failure_when_adapter_fails(tmp_path):
    """Adapter non-zero exit marks step and run as failed."""
    db = _make_db(tmp_path)
    orch = Orchestrator(db)
    router = StubRouter()
    scheduler = ExecutionScheduler()
    scheduler.add_task(Task("T1", "code_edit"))

    run_id = orch.create_run("PRJ-1", "PH-05")

    def adapter(_: Task, __: str) -> AdapterResult:
        return AdapterResult(exit_code=9, error_log="boom")

    executor = Executor(orch, router, scheduler, adapter)
    summary = executor.run(run_id)

    assert summary["state"] == "failed"
    step = db.list_step_attempts(run_id)[0]
    assert step["state"] == "failed"
    assert step["exit_code"] == 9
    assert step["error_log"] == "boom"


def test_executor_handles_missing_route(tmp_path):
    """If router cannot pick a tool the task is failed."""
    db = _make_db(tmp_path)
    orch = Orchestrator(db)
    router = StubRouter(tool_id=None)
    scheduler = ExecutionScheduler()
    scheduler.add_task(Task("T1", "code_edit"))

    run_id = orch.create_run("PRJ-1", "PH-05")

    executor = Executor(
        orch, router, scheduler, adapter_runner=lambda *_: AdapterResult()
    )
    summary = executor.run(run_id)

    assert summary["state"] == "failed"
    assert scheduler.has_failures() is True


def test_executor_gate_callback_can_fail_task(tmp_path):
    """Gate callback returning False forces failure even if adapter succeeds."""
    db = _make_db(tmp_path)
    orch = Orchestrator(db)
    router = StubRouter()
    scheduler = ExecutionScheduler()
    scheduler.add_task(Task("T1", "code_edit"))

    run_id = orch.create_run("PRJ-1", "PH-05")

    def adapter(_: Task, __: str) -> AdapterResult:
        return AdapterResult(exit_code=0)

    def gate_callback(_: str, __: Task, ___: AdapterResult) -> bool:
        return False

    executor = Executor(orch, router, scheduler, adapter, gate_callback=gate_callback)
    summary = executor.run(run_id)

    assert summary["state"] == "failed"
    step = db.list_step_attempts(run_id)[0]
    assert step["state"] == "failed"
    assert step["exit_code"] == 1


def test_executor_handles_adapter_exception(tmp_path):
    """Adapter exceptions are caught and mark step/task as failed."""
    db = _make_db(tmp_path)
    orch = Orchestrator(db)
    router = StubRouter()
    scheduler = ExecutionScheduler()
    scheduler.add_task(Task("T1", "code_edit"))

    run_id = orch.create_run("PRJ-1", "PH-05")

    def adapter(
        _: Task, __: str
    ) -> AdapterResult:  # pragma: no cover - exercised via exception path
        raise RuntimeError("adapter boom")

    executor = Executor(orch, router, scheduler, adapter)
    summary = executor.run(run_id)

    assert summary["state"] == "failed"
    step = db.list_step_attempts(run_id)[0]
    assert step["state"] == "failed"
    assert step["exit_code"] == 1
    assert "adapter boom" in step["error_log"]


def test_process_spawner_lifecycle(tmp_path):
    """ProcessSpawner spawns and terminates worker processes."""
    spawner = ProcessSpawner(base_sandbox_dir=tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    worker = spawner.spawn_worker_process(
        worker_id="worker-1",
        adapter_type="aider",
        repo_root=repo_root,
        env_overrides={"CUSTOM": "1"},
    )

    assert spawner.is_alive("worker-1") is True
    assert worker.env["UET_WORKER_ID"] == "worker-1"
    assert Path(worker.env["REPO_ROOT"]) == repo_root
    assert worker.sandbox_path.exists()

    spawner.terminate_worker_process("worker-1")

    # Give the OS a brief moment to reap the process
    time.sleep(0.05)
    assert spawner.is_alive("worker-1") is False
