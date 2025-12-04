"""Tests for Execution Scheduler - WS-03-01C"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.engine.scheduler import ExecutionScheduler, Task, create_task_from_spec


class TestTaskCreation:
    """Test Task object creation"""

    # DOC_ID: DOC-TEST-ENGINE-TEST-SCHEDULING-177

    def test_create_task(self):
        """Test creating a task"""
        task = Task("T1", "code_edit")
        assert task.task_id == "T1"
        assert task.task_kind == "code_edit"
        assert task.status == "pending"
        assert task.depends_on == []

    def test_task_with_dependencies(self):
        """Test task with dependencies"""
        task = Task("T2", "test", depends_on=["T1"])
        assert task.depends_on == ["T1"]

    def test_task_with_metadata(self):
        """Test task with metadata"""
        task = Task("T1", "code_edit", metadata={"priority": "high"})
        assert task.metadata["priority"] == "high"

    def test_create_from_spec(self):
        """Test creating task from spec"""
        spec = {
            "id": "T1",
            "kind": "code_edit",
            "name": "Fix bug",
            "depends_on": ["T0"],
            "constraints": {"max_lines": 100},
        }

        task = create_task_from_spec(spec)
        assert task.task_id == "T1"
        assert task.task_kind == "code_edit"
        assert task.depends_on == ["T0"]
        assert task.metadata["description"] == "Fix bug"


class TestSchedulerBasics:
    """Test basic scheduler operations"""

    def test_create_scheduler(self):
        """Test creating a scheduler"""
        scheduler = ExecutionScheduler()
        assert scheduler is not None
        assert len(scheduler.tasks) == 0

    def test_add_task(self):
        """Test adding a task"""
        scheduler = ExecutionScheduler()
        task = Task("T1", "code_edit")

        scheduler.add_task(task)

        assert "T1" in scheduler.tasks
        assert scheduler.tasks["T1"] == task

    def test_add_multiple_tasks(self):
        """Test adding multiple tasks"""
        scheduler = ExecutionScheduler()
        tasks = [Task("T1", "code_edit"), Task("T2", "test"), Task("T3", "deploy")]

        scheduler.add_tasks(tasks)

        assert len(scheduler.tasks) == 3

    def test_get_task(self):
        """Test retrieving a task"""
        scheduler = ExecutionScheduler()
        task = Task("T1", "code_edit")
        scheduler.add_task(task)

        retrieved = scheduler.get_task("T1")
        assert retrieved == task

    def test_get_nonexistent_task(self):
        """Test getting nonexistent task returns None"""
        scheduler = ExecutionScheduler()
        assert scheduler.get_task("T99") is None


class TestDependencyManagement:
    """Test dependency tracking and resolution"""

    def test_simple_dependency(self):
        """Test simple linear dependency"""
        scheduler = ExecutionScheduler()

        t1 = Task("T1", "code_edit")
        t2 = Task("T2", "test", depends_on=["T1"])

        scheduler.add_tasks([t1, t2])

        assert "T1" in scheduler.dependency_graph["T2"]
        assert "T2" in scheduler.reverse_deps["T1"]

    def test_multiple_dependencies(self):
        """Test task with multiple dependencies"""
        scheduler = ExecutionScheduler()

        t1 = Task("T1", "code_edit")
        t2 = Task("T2", "code_review")
        t3 = Task("T3", "deploy", depends_on=["T1", "T2"])

        scheduler.add_tasks([t1, t2, t3])

        assert "T1" in scheduler.dependency_graph["T3"]
        assert "T2" in scheduler.dependency_graph["T3"]

    def test_get_dependent_tasks(self):
        """Test getting tasks that depend on a given task"""
        scheduler = ExecutionScheduler()

        t1 = Task("T1", "code_edit")
        t2 = Task("T2", "test", depends_on=["T1"])
        t3 = Task("T3", "deploy", depends_on=["T1"])

        scheduler.add_tasks([t1, t2, t3])

        dependents = scheduler.get_dependent_tasks("T1")
        assert "T2" in dependents
        assert "T3" in dependents


class TestReadyTasks:
    """Test identifying ready tasks"""

    def test_no_dependencies_ready_immediately(self):
        """Test tasks with no dependencies are ready"""
        scheduler = ExecutionScheduler()

        t1 = Task("T1", "code_edit")
        scheduler.add_task(t1)

        ready = scheduler.get_ready_tasks()
        assert len(ready) == 1
        assert ready[0].task_id == "T1"

    def test_dependent_task_not_ready(self):
        """Test dependent tasks are not ready initially"""
        scheduler = ExecutionScheduler()

        t1 = Task("T1", "code_edit")
        t2 = Task("T2", "test", depends_on=["T1"])

        scheduler.add_tasks([t1, t2])

        ready = scheduler.get_ready_tasks()
        assert len(ready) == 1
        assert ready[0].task_id == "T1"

    def test_dependent_task_ready_after_completion(self):
        """Test dependent task becomes ready after dependency completes"""
        scheduler = ExecutionScheduler()

        t1 = Task("T1", "code_edit")
        t2 = Task("T2", "test", depends_on=["T1"])

        scheduler.add_tasks([t1, t2])

        # Complete T1
        scheduler.mark_completed("T1")

        # Now T2 should be ready
        ready = scheduler.get_ready_tasks()
        assert len(ready) == 1
        assert ready[0].task_id == "T2"

    def test_can_execute(self):
        """Test checking if a task can execute"""
        scheduler = ExecutionScheduler()

        t1 = Task("T1", "code_edit")
        t2 = Task("T2", "test", depends_on=["T1"])

        scheduler.add_tasks([t1, t2])

        assert scheduler.can_execute("T1") is True
        assert scheduler.can_execute("T2") is False

        scheduler.mark_completed("T1")
        assert scheduler.can_execute("T2") is True

    def test_get_blocking_tasks(self):
        """Test getting tasks that block execution"""
        scheduler = ExecutionScheduler()

        t1 = Task("T1", "code_edit")
        t2 = Task("T2", "review")
        t3 = Task("T3", "deploy", depends_on=["T1", "T2"])

        scheduler.add_tasks([t1, t2, t3])

        blocking = scheduler.get_blocking_tasks("T3")
        assert "T1" in blocking
        assert "T2" in blocking

        scheduler.mark_completed("T1")
        blocking = scheduler.get_blocking_tasks("T3")
        assert "T1" not in blocking
        assert "T2" in blocking


class TestCycleDetection:
    """Test circular dependency detection"""

    def test_no_cycle(self):
        """Test detecting no cycle in valid graph"""
        scheduler = ExecutionScheduler()

        t1 = Task("T1", "code_edit")
        t2 = Task("T2", "test", depends_on=["T1"])
        t3 = Task("T3", "deploy", depends_on=["T2"])

        scheduler.add_tasks([t1, t2, t3])

        cycle = scheduler.detect_cycles()
        assert cycle is None

    def test_simple_cycle(self):
        """Test detecting simple cycle"""
        scheduler = ExecutionScheduler()

        t1 = Task("T1", "task1", depends_on=["T2"])
        t2 = Task("T2", "task2", depends_on=["T1"])

        scheduler.add_tasks([t1, t2])

        cycle = scheduler.detect_cycles()
        assert cycle is not None
        assert "T1" in cycle
        assert "T2" in cycle

    def test_complex_cycle(self):
        """Test detecting cycle in complex graph"""
        scheduler = ExecutionScheduler()

        t1 = Task("T1", "task1")
        t2 = Task("T2", "task2", depends_on=["T1"])
        t3 = Task("T3", "task3", depends_on=["T2"])
        t4 = Task("T4", "task4", depends_on=["T3", "T1"])
        t5 = Task("T5", "task5", depends_on=["T4"])
        t2_cyclic = Task("T2", "task2", depends_on=["T1", "T5"])  # Creates cycle

        scheduler.add_tasks([t1, t3, t4, t5])
        scheduler.add_task(t2_cyclic)  # Add cyclic dependency

        cycle = scheduler.detect_cycles()
        assert cycle is not None


class TestExecutionOrder:
    """Test topological ordering and execution levels"""

    def test_simple_linear_order(self):
        """Test simple linear execution order"""
        scheduler = ExecutionScheduler()

        t1 = Task("T1", "task1")
        t2 = Task("T2", "task2", depends_on=["T1"])
        t3 = Task("T3", "task3", depends_on=["T2"])

        scheduler.add_tasks([t1, t2, t3])

        order = scheduler.get_execution_order()
        assert order == [["T1"], ["T2"], ["T3"]]

    def test_parallel_execution_order(self):
        """Test parallel tasks in same level"""
        scheduler = ExecutionScheduler()

        t1 = Task("T1", "task1")
        t2 = Task("T2", "task2")
        t3 = Task("T3", "task3", depends_on=["T1", "T2"])

        scheduler.add_tasks([t1, t2, t3])

        order = scheduler.get_execution_order()
        assert len(order) == 2
        assert set(order[0]) == {"T1", "T2"}
        assert order[1] == ["T3"]

    def test_complex_execution_order(self):
        """Test complex dependency graph"""
        scheduler = ExecutionScheduler()

        t1 = Task("T1", "task1")
        t2 = Task("T2", "task2")
        t3 = Task("T3", "task3", depends_on=["T1"])
        t4 = Task("T4", "task4", depends_on=["T2"])
        t5 = Task("T5", "task5", depends_on=["T3", "T4"])

        scheduler.add_tasks([t1, t2, t3, t4, t5])

        order = scheduler.get_execution_order()
        assert len(order) == 3
        assert set(order[0]) == {"T1", "T2"}
        assert set(order[1]) == {"T3", "T4"}
        assert order[2] == ["T5"]

    def test_execution_order_with_cycle(self):
        """Test that cycles raise error"""
        scheduler = ExecutionScheduler()

        t1 = Task("T1", "task1", depends_on=["T2"])
        t2 = Task("T2", "task2", depends_on=["T1"])

        scheduler.add_tasks([t1, t2])

        with pytest.raises(ValueError, match="Circular dependency"):
            scheduler.get_execution_order()


class TestParallelBatches:
    """Test parallel batch generation"""

    def test_single_batch(self):
        """Test single batch for small workload"""
        scheduler = ExecutionScheduler()

        t1 = Task("T1", "task1")
        t2 = Task("T2", "task2")

        scheduler.add_tasks([t1, t2])

        batches = scheduler.get_parallel_batches(max_parallel=5)
        assert len(batches) == 1
        assert set(batches[0]) == {"T1", "T2"}

    def test_multiple_batches(self):
        """Test splitting into multiple batches"""
        scheduler = ExecutionScheduler()

        tasks = [Task(f"T{i}", "task") for i in range(10)]
        scheduler.add_tasks(tasks)

        batches = scheduler.get_parallel_batches(max_parallel=3)

        # Should have 4 batches (3+3+3+1)
        assert len(batches) == 4
        assert len(batches[0]) == 3
        assert len(batches[1]) == 3
        assert len(batches[2]) == 3
        assert len(batches[3]) == 1

    def test_batches_with_dependencies(self):
        """Test batches respect dependencies"""
        scheduler = ExecutionScheduler()

        t1 = Task("T1", "task1")
        t2 = Task("T2", "task2")
        t3 = Task("T3", "task3", depends_on=["T1", "T2"])

        scheduler.add_tasks([t1, t2, t3])

        batches = scheduler.get_parallel_batches(max_parallel=5)

        # T1 and T2 in first batch, T3 in second
        assert len(batches) == 2
        assert set(batches[0]) == {"T1", "T2"}
        assert batches[1] == ["T3"]


class TestTaskStatusManagement:
    """Test task status tracking"""

    def test_mark_completed(self):
        """Test marking task as completed"""
        scheduler = ExecutionScheduler()
        task = Task("T1", "task1")
        scheduler.add_task(task)

        scheduler.mark_completed("T1", result={"status": "success"})

        assert scheduler.tasks["T1"].status == "completed"
        assert scheduler.tasks["T1"].result == {"status": "success"}

    def test_mark_failed(self):
        """Test marking task as failed"""
        scheduler = ExecutionScheduler()
        task = Task("T1", "task1")
        scheduler.add_task(task)

        scheduler.mark_failed("T1", error="Execution failed")

        assert scheduler.tasks["T1"].status == "failed"
        assert scheduler.tasks["T1"].error == "Execution failed"

    def test_mark_running(self):
        """Test marking task as running"""
        scheduler = ExecutionScheduler()
        task = Task("T1", "task1")
        scheduler.add_task(task)

        scheduler.mark_running("T1")

        assert scheduler.tasks["T1"].status == "running"

    def test_get_stats(self):
        """Test getting task statistics"""
        scheduler = ExecutionScheduler()

        t1 = Task("T1", "task1")
        t2 = Task("T2", "task2")
        t3 = Task("T3", "task3")

        scheduler.add_tasks([t1, t2, t3])
        scheduler.mark_running("T1")
        scheduler.mark_completed("T2")

        stats = scheduler.get_stats()
        assert stats["total"] == 3
        assert stats["pending"] == 1
        assert stats["running"] == 1
        assert stats["completed"] == 1
        assert stats["failed"] == 0

    def test_is_complete(self):
        """Test checking if all tasks are done"""
        scheduler = ExecutionScheduler()

        t1 = Task("T1", "task1")
        t2 = Task("T2", "task2")

        scheduler.add_tasks([t1, t2])

        assert scheduler.is_complete() is False

        scheduler.mark_completed("T1")
        assert scheduler.is_complete() is False

        scheduler.mark_completed("T2")
        assert scheduler.is_complete() is True

    def test_has_failures(self):
        """Test checking for failures"""
        scheduler = ExecutionScheduler()

        t1 = Task("T1", "task1")
        t2 = Task("T2", "task2")

        scheduler.add_tasks([t1, t2])

        assert scheduler.has_failures() is False

        scheduler.mark_failed("T1", "Error")
        assert scheduler.has_failures() is True


class TestRealWorldScenarios:
    """Test realistic workstream scenarios"""

    def test_software_development_workflow(self):
        """Test typical software development task flow"""
        scheduler = ExecutionScheduler()

        # Define tasks
        tasks = [
            Task("design", "design"),
            Task("implement", "code_edit", depends_on=["design"]),
            Task("unit_test", "test", depends_on=["implement"]),
            Task("code_review", "code_review", depends_on=["implement"]),
            Task("integration_test", "test", depends_on=["unit_test", "code_review"]),
            Task("deploy", "deploy", depends_on=["integration_test"]),
        ]

        scheduler.add_tasks(tasks)

        # Check execution order
        order = scheduler.get_execution_order()

        assert order[0] == ["design"]
        assert order[1] == ["implement"]
        assert set(order[2]) == {"unit_test", "code_review"}
        assert order[3] == ["integration_test"]
        assert order[4] == ["deploy"]

    def test_parallel_feature_development(self):
        """Test parallel feature development"""
        scheduler = ExecutionScheduler()

        tasks = [
            Task("feature_a", "code_edit"),
            Task("feature_b", "code_edit"),
            Task("test_a", "test", depends_on=["feature_a"]),
            Task("test_b", "test", depends_on=["feature_b"]),
            Task("merge", "code_review", depends_on=["test_a", "test_b"]),
        ]

        scheduler.add_tasks(tasks)

        # Features can be developed in parallel
        batches = scheduler.get_parallel_batches(max_parallel=2)

        assert set(batches[0]) == {"feature_a", "feature_b"}
        assert set(batches[1]) == {"test_a", "test_b"}
        assert batches[2] == ["merge"]
