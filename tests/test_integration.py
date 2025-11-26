"""Integration tests for Pipeline Plus"""
import pytest
from pathlib import Path
from modules.core_engine.m010001_pipeline_plus_orchestrator import PipelinePlusOrchestrator
from modules.core_state.m010003_task_queue import Task, TaskPayload

@pytest.fixture
def orchestrator():
    return PipelinePlusOrchestrator()

def test_orchestrator_initialization(orchestrator):
    assert orchestrator.task_queue is not None
    assert orchestrator.audit_logger is not None
    assert orchestrator.patch_manager is not None
    assert orchestrator.prompt_engine is not None
    assert orchestrator.scope_validator is not None
    assert orchestrator.circuit_breaker is not None
    assert len(orchestrator.adapters) == 3

def test_orchestrator_has_all_adapters(orchestrator):
    assert 'aider' in orchestrator.adapters
    assert 'codex' in orchestrator.adapters
    assert 'claude' in orchestrator.adapters

def test_orchestrator_adapter_configuration():
    config = {'aider': {'model': 'gpt-4'}, 'codex': {'timeout': 300}}
    orch = PipelinePlusOrchestrator(config)
    assert orch.adapters['aider'].config == {'model': 'gpt-4'}
    assert orch.adapters['codex'].config == {'timeout': 300}

def test_execute_task_unknown_adapter(orchestrator, tmp_path):
    task = Task(task_id='test-1', source_app='unknown', mode='prompt', capabilities=[], payload=TaskPayload(repo_path=str(tmp_path)))
    result = orchestrator.execute_task(task, str(tmp_path))
    assert result.success is False
    assert 'Unknown adapter' in result.error

def test_components_integration(orchestrator):
    # Verify all components are properly initialized
    assert orchestrator.task_queue.inbox.exists()
    assert orchestrator.patch_manager.ledger_path.exists()
    assert orchestrator.prompt_engine.template_dir.exists()

def test_orchestrator_default_config():
    orch = PipelinePlusOrchestrator()
    assert orch.config == {}
    assert all(adapter.config == {} for adapter in orch.adapters.values())

def test_task_queue_integration(orchestrator):
    task = Task(task_id=Task.generate_id(), source_app='aider', mode='prompt', capabilities=['refactor'], payload=TaskPayload(repo_path='/test'))
    task_id = orchestrator.task_queue.enqueue(task)
    assert task_id == task.task_id
    status = orchestrator.task_queue.get_status(task_id)
    assert status.state == 'inbox'

def test_audit_logger_integration(orchestrator):
    orchestrator.audit_logger.log_event('test_event', 'task-1', {'test': 'data'})
    events = orchestrator.audit_logger.query_events()
    assert len(events) >= 1

def test_scope_validator_integration(orchestrator):
    bundle = {'files_scope': ['test.py'], 'files_create': []}
    result = orchestrator.scope_validator.validate_patch_scope(['test.py'], bundle)
    assert result.valid is True

def test_circuit_breaker_integration(orchestrator):
    trip = orchestrator.circuit_breaker.should_stop('run-1', 'ws-1', 'edit', 2)
    assert trip is None  # Within limits

def test_all_pipeline_components_present(orchestrator):
    # Phase 1A: Task Queue
    assert hasattr(orchestrator, 'task_queue')
    # Phase 1B: Audit & Telemetry
    assert hasattr(orchestrator, 'audit_logger')
    # Phase 2: Patch Management
    assert hasattr(orchestrator, 'patch_manager')
    # Phase 3: Prompt Engine
    assert hasattr(orchestrator, 'prompt_engine')
    # Phase 4: Validators & Circuit Breakers
    assert hasattr(orchestrator, 'scope_validator')
    assert hasattr(orchestrator, 'circuit_breaker')
    # Phase 5: Adapters
    assert hasattr(orchestrator, 'adapters')
