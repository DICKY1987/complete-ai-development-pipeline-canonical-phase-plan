"""
Integration tests for DAO layer.

Tests all CRUD operations and database constraints.
"""

import pytest
import os
from datetime import datetime, timezone

from core.dao.run_dao import RunDAO
from core.dao.workstream_dao import WorkstreamDAO
from core.dao.task_dao import TaskDAO
from core.dao.worker_dao import WorkerDAO
from core.dao.patch_dao import PatchDAO
from core.dao.test_gate_dao import TestGateDAO
from core.dao.circuit_breaker_dao import CircuitBreakerDAO
from core.db.migration_manager import MigrationManager


@pytest.fixture
def test_db_path(tmp_path):
    """Create a temporary test database."""
    import importlib
    from pathlib import Path
    from core.db.connection import DatabaseConnection
    
    db_path = str(tmp_path / "test.db")
    db_conn = DatabaseConnection(db_path)
    manager = MigrationManager(db_conn)
    
    # Discover and register migrations (skip _001 from Phase 2)
    migrations_dir = Path(__file__).parent.parent.parent / "core" / "db" / "migrations"
    for migration_file in sorted(migrations_dir.glob("_*.py")):
        if migration_file.stem == "__init__" or migration_file.stem.startswith("_001"):
            continue
        
        # Import migration module
        module_name = f"core.db.migrations.{migration_file.stem}"
        module = importlib.import_module(module_name)
        
        # Extract version from filename (_002_name.py -> 2)
        version = int(migration_file.stem.split('_')[1])
        name = migration_file.stem
        
        manager.register(version, name, module.up, module.down)
    
    # Run migrations
    manager.migrate()
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)


class TestRunDAO:
    """Test Run DAO operations."""
    
    def test_create_and_get(self, test_db_path):
        dao = RunDAO(test_db_path)
        
        run = {
            'run_id': 'run-001',
            'state': 'INITIALIZING',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'metadata': {'version': '1.0'},
            'progress_percentage': 0.0
        }
        
        run_id = dao.create(run)
        assert run_id == 'run-001'
        
        retrieved = dao.get('run-001')
        assert retrieved is not None
        assert retrieved['state'] == 'INITIALIZING'
        assert retrieved['metadata'] == {'version': '1.0'}
    
    def test_update(self, test_db_path):
        dao = RunDAO(test_db_path)
        
        run = {
            'run_id': 'run-002',
            'state': 'INITIALIZING',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        dao.create(run)
        success = dao.update('run-002', {'state': 'RUNNING', 'progress_percentage': 50.0})
        
        assert success
        updated = dao.get('run-002')
        assert updated['state'] == 'RUNNING'
        assert updated['progress_percentage'] == 50.0
    
    def test_find_by_state(self, test_db_path):
        dao = RunDAO(test_db_path)
        
        for i in range(3):
            dao.create({
                'run_id': f'run-{i}',
                'state': 'RUNNING' if i < 2 else 'COMPLETED',
                'created_at': datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            })
        
        running = dao.find_by_state('RUNNING')
        assert len(running) == 2


class TestWorkstreamDAO:
    """Test Workstream DAO operations."""
    
    def test_create_with_foreign_key(self, test_db_path):
        run_dao = RunDAO(test_db_path)
        ws_dao = WorkstreamDAO(test_db_path)
        
        # Create parent run
        run_dao.create({
            'run_id': 'run-001',
            'state': 'RUNNING',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        })
        
        # Create workstream
        ws = {
            'workstream_id': 'ws-001',
            'run_id': 'run-001',
            'state': 'PENDING',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        ws_id = ws_dao.create(ws)
        assert ws_id == 'ws-001'
        
        retrieved = ws_dao.get('ws-001')
        assert retrieved['run_id'] == 'run-001'
    
    def test_find_by_run(self, test_db_path):
        run_dao = RunDAO(test_db_path)
        ws_dao = WorkstreamDAO(test_db_path)
        
        run_dao.create({
            'run_id': 'run-001',
            'state': 'RUNNING',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        })
        
        for i in range(3):
            ws_dao.create({
                'workstream_id': f'ws-{i}',
                'run_id': 'run-001',
                'state': 'PENDING',
                'created_at': datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            })
        
        workstreams = ws_dao.find_by_run('run-001')
        assert len(workstreams) == 3


class TestTaskDAO:
    """Test Task DAO operations."""
    
    def test_create_with_dependencies(self, test_db_path):
        run_dao = RunDAO(test_db_path)
        ws_dao = WorkstreamDAO(test_db_path)
        task_dao = TaskDAO(test_db_path)
        worker_dao = WorkerDAO(test_db_path)
        
        # Create hierarchy
        run_dao.create({
            'run_id': 'run-001',
            'state': 'RUNNING',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        })
        
        ws_dao.create({
            'workstream_id': 'ws-001',
            'run_id': 'run-001',
            'state': 'RUNNING',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        })
        
        worker_dao.create({
            'worker_id': 'worker-001',
            'state': 'IDLE',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        })
        
        task = {
            'task_id': 'task-001',
            'workstream_id': 'ws-001',
            'worker_id': 'worker-001',
            'state': 'QUEUED',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'retry_count': 0,
            'max_retries': 3
        }
        
        task_id = task_dao.create(task)
        assert task_id == 'task-001'
        
        retrieved = task_dao.get('task-001')
        assert retrieved['workstream_id'] == 'ws-001'
        assert retrieved['worker_id'] == 'worker-001'


class TestCircuitBreakerDAO:
    """Test CircuitBreaker DAO operations."""
    
    def test_get_by_tool_name(self, test_db_path):
        dao = CircuitBreakerDAO(test_db_path)
        
        breaker = {
            'breaker_id': 'breaker-001',
            'tool_name': 'pytest',
            'state': 'CLOSED',
            'failure_count': 0,
            'failure_threshold': 5,
            'cooldown_seconds': 60,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        dao.create(breaker)
        
        retrieved = dao.get_by_tool('pytest')
        assert retrieved is not None
        assert retrieved['breaker_id'] == 'breaker-001'
        assert retrieved['state'] == 'CLOSED'


class TestDAOConstraints:
    """Test database constraints."""
    
    def test_foreign_key_cascade_delete(self, test_db_path):
        """Test that deleting a run cascades to workstreams."""
        run_dao = RunDAO(test_db_path)
        ws_dao = WorkstreamDAO(test_db_path)
        
        run_dao.create({
            'run_id': 'run-001',
            'state': 'RUNNING',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        })
        
        ws_dao.create({
            'workstream_id': 'ws-001',
            'run_id': 'run-001',
            'state': 'PENDING',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        })
        
        # Delete run should cascade to workstream
        run_dao.delete('run-001')
        
        assert ws_dao.get('ws-001') is None
    
    def test_count_operations(self, test_db_path):
        dao = RunDAO(test_db_path)
        
        for i in range(5):
            dao.create({
                'run_id': f'run-{i}',
                'state': 'RUNNING' if i < 3 else 'COMPLETED',
                'created_at': datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            })
        
        total = dao.count()
        assert total == 5
        
        running = dao.count(state='RUNNING')
        assert running == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
