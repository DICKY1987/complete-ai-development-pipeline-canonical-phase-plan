"""Test Deterministic Execution

Validates that scheduler, router, and orchestrator produce
deterministic, reproducible results when required.
"""

# DOC_ID: DOC-TEST-DETERMINISTIC-EXECUTION-001

import pytest

from core.engine.orchestrator import Orchestrator
from core.engine.router import TaskRouter
from core.engine.scheduler import ExecutionScheduler, Task


def test_scheduler_produces_deterministic_task_order():
    """Verify tasks with same dependencies execute in sorted order"""
    scheduler = ExecutionScheduler()

    # Add 5 tasks with no dependencies in random order
    task_ids = ["task_5", "task_2", "task_8", "task_1", "task_9"]
    for tid in task_ids:
        task = Task(tid, "test")
        scheduler.add_task(task)

    # Get ready tasks twice
    ready_1 = [t.task_id for t in scheduler.get_ready_tasks()]
    ready_2 = [t.task_id for t in scheduler.get_ready_tasks()]

    # Should be identical and sorted
    assert ready_1 == ready_2, "Task order should be deterministic"
    assert ready_1 == sorted(ready_1), "Tasks should be in sorted order"
    assert ready_1 == ["task_1", "task_2", "task_5", "task_8", "task_9"]


def test_scheduler_respects_dependencies():
    """Verify dependency resolution is deterministic"""
    scheduler = ExecutionScheduler()

    # Create tasks with dependencies
    task_1 = Task("task_1", "test", depends_on=[])
    task_2 = Task("task_2", "test", depends_on=["task_1"])
    task_3 = Task("task_3", "test", depends_on=["task_1"])
    task_4 = Task("task_4", "test", depends_on=["task_2", "task_3"])

    # Add in random order
    for task in [task_4, task_1, task_3, task_2]:
        scheduler.add_task(task)

    # First round: only task_1 should be ready
    ready_1 = scheduler.get_ready_tasks()
    assert len(ready_1) == 1
    assert ready_1[0].task_id == "task_1"

    # Complete task_1
    task_1.status = "completed"

    # Second round: task_2 and task_3 should be ready (sorted order)
    ready_2 = scheduler.get_ready_tasks()
    assert len(ready_2) == 2
    assert [t.task_id for t in ready_2] == ["task_2", "task_3"]


def test_orchestrator_generates_deterministic_ids():
    """Verify deterministic mode produces reproducible IDs"""
    orch_1 = Orchestrator(deterministic_mode=True)
    orch_2 = Orchestrator(deterministic_mode=True)

    # Create runs with same inputs
    run_1 = orch_1.create_run("proj1", "phase1")
    run_2 = orch_2.create_run("proj1", "phase1")

    # Should be identical in deterministic mode
    assert run_1 == run_2, "Deterministic mode should produce identical run IDs"
    assert run_1.startswith("DET"), "Deterministic IDs should start with DET"


def test_orchestrator_non_deterministic_differs():
    """Verify non-deterministic mode produces different IDs"""
    orch_1 = Orchestrator(deterministic_mode=False)
    orch_2 = Orchestrator(deterministic_mode=False)

    run_1 = orch_1.create_run("proj1", "phase1")
    run_2 = orch_2.create_run("proj1", "phase1")

    # Should be different (very high probability)
    assert run_1 != run_2, "Non-deterministic mode should produce unique IDs"


def test_orchestrator_timestamp_deterministic():
    """Verify deterministic mode produces fixed timestamps"""
    orch = Orchestrator(deterministic_mode=True)

    ts_1 = orch.now_iso()
    ts_2 = orch.now_iso()

    # Should be identical fixed timestamp
    assert ts_1 == ts_2
    assert ts_1 == "2024-01-01T00:00:00.000000Z"


def test_scheduler_parallel_tasks_sorted():
    """Verify parallel-eligible tasks returned in sorted order"""
    scheduler = ExecutionScheduler()

    # Add 10 tasks with no dependencies
    for i in [9, 3, 7, 1, 5, 2, 8, 4, 6, 0]:
        scheduler.add_task(Task(f"parallel_{i}", "test"))

    ready = scheduler.get_ready_tasks()

    # All should be ready (no dependencies)
    assert len(ready) == 10

    # Should be in sorted order
    task_ids = [t.task_id for t in ready]
    assert task_ids == sorted(task_ids)
    assert task_ids[0] == "parallel_0"
    assert task_ids[-1] == "parallel_9"


def test_deterministic_mode_increment_counter():
    """Verify deterministic counter increments properly"""
    orch = Orchestrator(deterministic_mode=True)

    ids = [orch.generate_ulid() for _ in range(5)]

    # Should be sequential
    assert ids == [
        "DET0000000000000000000001",
        "DET0000000000000000000002",
        "DET0000000000000000000003",
        "DET0000000000000000000004",
        "DET0000000000000000000005",
    ]


def test_scheduler_cycle_detection_deterministic():
    """Verify cycle detection works with sorted iteration"""
    scheduler = ExecutionScheduler()

    # Create circular dependency
    task_a = Task("task_a", "test", depends_on=["task_b"])
    task_b = Task("task_b", "test", depends_on=["task_a"])

    scheduler.add_task(task_a)
    scheduler.add_task(task_b)

    cycle = scheduler.detect_cycles()

    assert cycle is not None, "Should detect cycle"
    # Cycle should be deterministic (sorted)
    assert sorted(cycle) == cycle or sorted(cycle, reverse=True) == cycle
