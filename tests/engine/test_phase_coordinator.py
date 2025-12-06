"""Tests for Phase Coordinator - Full automation pipeline.

DOC_ID: DOC-ENGINE-ENGINE-TEST-PHASE-COORDINATOR-004
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from core.engine.orchestrator import Orchestrator
from core.engine.phase_coordinator import (PhaseCoordinator,
                                           PhaseCoordinatorConfig)
from core.engine.router import TaskRouter
from core.engine.scheduler import ExecutionScheduler, Task
from core.engine.state_file_manager import StateFileManager
from core.events.event_bus import EventBus, EventType
from core.state.db import Database


@pytest.fixture
def test_db(tmp_path):
    """Create a test database with schema initialized."""
    db_path = tmp_path / "test.db"
    db = Database(db_path)
    return db


@pytest.fixture
def mock_orchestrator(test_db):
    """Create a mock orchestrator."""
    orch = Orchestrator(db=test_db)
    return orch


@pytest.fixture
def mock_router(tmp_path):
    """Create a mock router."""
    config_path = tmp_path / "router_config.json"
    config_path.write_text('{"apps": {}, "routing": {"rules": []}, "defaults": {}}')

    mock = Mock(spec=TaskRouter)
    mock.route_task.return_value = "aider"
    mock.decision_log = []
    mock.get_tool_config.return_value = {"command": "aider"}
    return mock


@pytest.fixture
def scheduler():
    """Create a real scheduler."""
    return ExecutionScheduler()


@pytest.fixture
def state_manager(tmp_path):
    """Create a state manager with temp directory."""
    return StateFileManager(output_dir=tmp_path / ".state")


@pytest.fixture
def event_bus(test_db):
    """Create an event bus with initialized database."""
    return EventBus(db_path=str(test_db.db_path))


@pytest.fixture
def coordinator(mock_orchestrator, mock_router, scheduler, state_manager, event_bus):
    """Create a phase coordinator."""
    config = PhaseCoordinatorConfig(
        routing_enabled=True,
        execution_enabled=True,
        error_recovery_enabled=False,  # Disable for basic tests
    )
    return PhaseCoordinator(
        orchestrator=mock_orchestrator,
        router=mock_router,
        scheduler=scheduler,
        config=config,
        state_manager=state_manager,
        event_bus=event_bus,
    )


def test_phase_coordinator_creation(coordinator):
    """Test that coordinator is created successfully."""
    assert coordinator is not None
    assert coordinator.config.routing_enabled
    assert coordinator.config.execution_enabled


def test_routing_phase(coordinator, scheduler, mock_orchestrator):
    """Test Phase 4: Routing."""
    # Create a run first
    run_id = mock_orchestrator.create_run(
        project_id="test-project", phase_id="test-phase"
    )

    tasks = [
        Task(task_id="task-001", task_kind="code_edit", metadata={}),
        Task(task_id="task-002", task_kind="analysis", metadata={}),
    ]

    results = coordinator._run_routing_phase(run_id, tasks)

    assert results["decisions_count"] == 0  # Mock router has empty decision log
    assert "decisions_file" in results
    assert "assignments_file" in results

    # Verify tasks were assigned tools
    assert tasks[0].selected_tool == "aider"
    assert tasks[1].selected_tool == "aider"


def test_execution_phase(coordinator, scheduler, mock_orchestrator):
    """Test Phase 5: Execution."""
    run_id = mock_orchestrator.create_run(
        project_id="test-project", phase_id="test-phase"
    )

    task = Task(task_id="task-001", task_kind="code_edit", metadata={})
    task.selected_tool = "aider"
    tasks = [task]

    # Mock executor behavior
    with patch.object(coordinator.executor, "execute_task") as mock_execute:
        from core.engine.executor import AdapterResult

        mock_execute.return_value = AdapterResult(
            exit_code=0, output_patch_id="patch-001"
        )

        results = coordinator._run_execution_phase(run_id, tasks)

    assert results["total"] == 1
    assert results["succeeded"] == 1
    assert results["failed"] == 0
    assert "results_file" in results


def test_full_pipeline_success(coordinator, scheduler, mock_orchestrator):
    """Test full pipeline execution with success."""
    run_id = mock_orchestrator.create_run(
        project_id="test-project", phase_id="test-phase"
    )

    tasks = [
        Task(task_id="task-001", task_kind="code_edit", metadata={}),
    ]

    with patch.object(coordinator.executor, "execute_task") as mock_execute:
        from core.engine.executor import AdapterResult

        mock_execute.return_value = AdapterResult(exit_code=0)

        results = coordinator.run_full_pipeline(run_id, tasks)

    assert results["success"]
    assert results["total_tasks"] == 1
    assert "routing_results" in results
    assert "execution_results" in results
    assert results["duration_seconds"] > 0


def test_full_pipeline_with_failure(coordinator, scheduler, mock_orchestrator):
    """Test full pipeline with task failure."""
    run_id = mock_orchestrator.create_run(
        project_id="test-project", phase_id="test-phase"
    )

    tasks = [
        Task(task_id="task-001", task_kind="code_edit", metadata={}),
    ]

    with patch.object(coordinator.executor, "execute_task") as mock_execute:
        from core.engine.executor import AdapterResult

        mock_execute.return_value = AdapterResult(exit_code=1, error_log="Test error")

        results = coordinator.run_full_pipeline(run_id, tasks)

    assert results["success"]
    assert results["total_tasks"] == 1
    assert results["execution_results"]["failed"] == 1


def test_event_emission(coordinator, event_bus, scheduler, mock_orchestrator):
    """Test that events are emitted during pipeline execution."""
    run_id = mock_orchestrator.create_run(
        project_id="test-project", phase_id="test-phase"
    )

    emitted_events = []

    def capture_event(event):
        emitted_events.append(event)

    event_bus.subscribe(EventType.ROUTING_COMPLETE, capture_event)

    tasks = [
        Task(task_id="task-001", task_kind="code_edit", metadata={}),
    ]

    coordinator._run_routing_phase(run_id, tasks)

    # Event should be emitted
    assert len(emitted_events) > 0


def test_config_defaults():
    """Test default configuration values."""
    config = PhaseCoordinatorConfig()

    assert config.routing_enabled
    assert config.execution_enabled
    assert config.error_recovery_enabled
    assert config.max_retries == 2
    assert config.agents == ["aider", "codex", "claude"]
    assert config.fallback_agent == "aider"


def test_error_recovery_disabled(coordinator, scheduler, mock_orchestrator):
    """Test pipeline with error recovery disabled."""
    run_id = mock_orchestrator.create_run(
        project_id="test-project", phase_id="test-phase"
    )

    tasks = [
        Task(task_id="task-001", task_kind="code_edit", metadata={}),
    ]

    with patch.object(coordinator.executor, "execute_task") as mock_execute:
        from core.engine.executor import AdapterResult

        mock_execute.return_value = AdapterResult(exit_code=1, error_log="Test error")

        results = coordinator.run_full_pipeline(run_id, tasks)

    # Recovery should not run (disabled in fixture)
    assert "recovery_results" not in results or results["recovery_results"] == {}


def test_state_file_export(
    coordinator, scheduler, state_manager, tmp_path, mock_orchestrator
):
    """Test that state files are exported."""
    run_id = mock_orchestrator.create_run(
        project_id="test-project", phase_id="test-phase"
    )

    tasks = [
        Task(task_id="task-001", task_kind="code_edit", metadata={}),
    ]

    with patch.object(coordinator.executor, "execute_task") as mock_execute:
        from core.engine.executor import AdapterResult

        mock_execute.return_value = AdapterResult(exit_code=0)

        coordinator.run_full_pipeline(run_id, tasks)

    state_dir = tmp_path / ".state"
    assert state_dir.exists()

    # Check for state files
    assert (state_dir / "routing_decisions.json").exists()
    assert (state_dir / "adapter_assignments.json").exists()
    assert (state_dir / "execution_results.json").exists()


def test_coordinator_factory():
    """Test coordinator factory function."""
    import tempfile
    from pathlib import Path

    from core.engine.phase_coordinator import create_phase_coordinator
    from core.state.db import Database

    with tempfile.TemporaryDirectory() as tmp:
        db = Database(Path(tmp) / "test.db")
        orchestrator = Orchestrator(db=db)

        tmp_path = Path(tmp)
        config_path = tmp_path / "router_config.json"
        config_path.write_text('{"apps": {}, "routing": {"rules": []}, "defaults": {}}')

        router = TaskRouter(str(config_path))
        scheduler = ExecutionScheduler()

        coordinator = create_phase_coordinator(
            orchestrator=orchestrator,
            router=router,
            scheduler=scheduler,
        )

        assert coordinator is not None
        assert isinstance(coordinator, PhaseCoordinator)
