from __future__ import annotations

"""Executor integration smoke tests for Phase 5 execution."""
# DOC_ID: DOC-TEST-ENGINE-EXECUTOR-FLOW-300

import json
import time
from pathlib import Path
from typing import Dict

import pytest

from core.engine.executor import AdapterResult, Executor
from core.engine.orchestrator import Orchestrator
from core.engine.process_spawner import ProcessSpawner
from core.engine.router import TaskRouter
from core.engine.scheduler import ExecutionScheduler, Task
from core.engine.test_gate import GateCriteria, TestGate, TestResults
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

    def adapter(task_obj: Task, tool_id: str, _: Dict[str, Any]) -> AdapterResult:
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

    def adapter(_: Task, __: str, ___: Dict[str, Any]) -> AdapterResult:
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
        orch, router, scheduler, adapter_runner=lambda *args: AdapterResult()
    )
    summary = executor.run(run_id)

    assert summary["state"] == "failed"
    assert scheduler.has_failures() is True


def _write_gate_migration(root: Path) -> None:
    """Create a minimal migration file for TestGate to load."""
    schema_dir = root / "schema" / "migrations"
    schema_dir.mkdir(parents=True, exist_ok=True)
    migration = schema_dir / "004_add_test_gates_table.sql"
    migration.write_text(
        """
        CREATE TABLE IF NOT EXISTS test_gates (
            gate_id TEXT PRIMARY KEY,
            name TEXT,
            gate_type TEXT,
            state TEXT,
            project_id TEXT,
            execution_request_id TEXT,
            criteria TEXT,
            execution TEXT,
            results TEXT,
            decision TEXT,
            created_at TEXT,
            updated_at TEXT,
            metadata TEXT
        );
        """
    )


def test_executor_with_test_gate_integration(tmp_path, monkeypatch):
    """Executor can drive a real TestGate pass decision."""
    _write_gate_migration(tmp_path)
    monkeypatch.chdir(tmp_path)

    db = _make_db(tmp_path)
    gate_manager = TestGate(db)
    gate_id = "01HQGATEEXEC00000000000001"
    gate_manager.create_gate(
        gate_id,
        name="Unit Tests",
        gate_type="unit_tests",
        criteria=GateCriteria(min_coverage=80.0),
    )

    orch = Orchestrator(db)
    router = StubRouter()
    scheduler = ExecutionScheduler()
    scheduler.add_task(Task("T1", "code_edit"))
    run_id = orch.create_run("PRJ-1", "PH-05")

    def adapter(_: Task, __: str, ___: Dict[str, Any]) -> AdapterResult:
        return AdapterResult(exit_code=0, metadata={"coverage": 90.0})

    def gate_callback(run_id: str, task: Task, result: AdapterResult) -> bool:
        gate_manager.start_gate(gate_id, command="pytest")
        results = TestResults(
            total_tests=1,
            passed_tests=1,
            failed_tests=0,
            coverage_percent=result.metadata.get("coverage"),
        )
        gate_manager.complete_gate(gate_id, results, exit_code=result.exit_code)
        return gate_manager.get_gate(gate_id)["decision"]["passed"]

    executor = Executor(orch, router, scheduler, adapter, gate_callback=gate_callback)
    summary = executor.run(run_id)

    gate = gate_manager.get_gate(gate_id)
    assert summary["state"] == "succeeded"
    assert gate["state"] == "passed"


def test_executor_gate_callback_can_fail_task(tmp_path):
    """Gate callback returning False forces failure even if adapter succeeds."""
    db = _make_db(tmp_path)
    orch = Orchestrator(db)
    router = StubRouter()
    scheduler = ExecutionScheduler()
    scheduler.add_task(Task("T1", "code_edit"))

    run_id = orch.create_run("PRJ-1", "PH-05")

    def adapter(_: Task, __: str, ___: Dict[str, Any]) -> AdapterResult:
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
        _: Task, __: str, ___: Dict[str, Any]
    ) -> AdapterResult:  # pragma: no cover - exercised via exception path
        raise RuntimeError("adapter boom")

    executor = Executor(orch, router, scheduler, adapter)
    summary = executor.run(run_id)

    assert summary["state"] == "failed"
    step = db.list_step_attempts(run_id)[0]
    assert step["state"] == "failed"
    assert step["exit_code"] == 1
    assert "adapter boom" in step["error_log"]


def test_executor_runs_with_subprocess_adapter(tmp_path, monkeypatch):
    """Executor uses SubprocessAdapter when no adapter_runner is provided."""
    router_config = {
        "version": "1.0.0",
        "apps": {
            "echoer": {
                "kind": "tool",
                "command": "python -c \"print('ok')\"",
                "capabilities": {"task_kinds": ["code_edit"]},
                "limits": {"timeout_seconds": 10},
            }
        },
        "routing": {"rules": []},
    }
    config_path = tmp_path / "router.json"
    config_path.write_text(json.dumps(router_config))
    router = TaskRouter(str(config_path))

    db = _make_db(tmp_path)
    orch = Orchestrator(db)
    scheduler = ExecutionScheduler()
    scheduler.add_task(Task("T1", "code_edit", metadata={"description": "echo"}))
    run_id = orch.create_run("PRJ-1", "PH-05")

    executor = Executor(orch, router, scheduler)
    summary = executor.run(run_id)

    step = db.list_step_attempts(run_id)[0]
    assert summary["state"] == "succeeded"
    assert step["state"] == "succeeded"
    assert step["exit_code"] == 0


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
