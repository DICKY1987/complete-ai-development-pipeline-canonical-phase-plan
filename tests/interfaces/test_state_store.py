"""Tests for StateStore protocol and SQLiteStateStore implementation."""

import pytest
from pathlib import Path
from datetime import datetime
import tempfile

from core.interfaces.state_store import (
    StateStore,
    WorkstreamNotFoundError,
    ExecutionNotFoundError,
)
from core.state.sqlite_store import SQLiteStateStore


class TestStateStoreProtocol:
    """Test StateStore protocol compliance."""
DOC_ID: DOC-TEST-INTERFACES-TEST-STATE-STORE-124
    
    def test_sqlite_store_implements_protocol(self):
        """SQLiteStateStore implements StateStore protocol."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = SQLiteStateStore(Path(tmpdir) / "test.db")
            assert isinstance(store, StateStore)


class TestSQLiteStateStore:
    """Test SQLiteStateStore implementation."""
    
    @pytest.fixture
    def store(self):
        """Create temporary SQLiteStateStore for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield SQLiteStateStore(Path(tmpdir) / "test.db")
    
    def test_save_and_get_workstream(self, store):
        """Save and retrieve workstream."""
        ws = {
            'id': 'ws-test',
            'status': 'pending',
            'tasks': ['Task 1', 'Task 2']
        }
        
        store.save_workstream(ws)
        retrieved = store.get_workstream('ws-test')
        
        assert retrieved is not None
        assert retrieved['id'] == 'ws-test'
        assert retrieved['status'] == 'pending'
        assert retrieved['tasks'] == ['Task 1', 'Task 2']
    
    def test_get_nonexistent_workstream_returns_none(self, store):
        """Getting nonexistent workstream returns None."""
        result = store.get_workstream('nonexistent')
        assert result is None
    
    def test_update_workstream(self, store):
        """Update existing workstream."""
        store.save_workstream({'id': 'ws-test', 'status': 'pending'})
        store.save_workstream({'id': 'ws-test', 'status': 'running'})
        
        ws = store.get_workstream('ws-test')
        assert ws['status'] == 'running'
    
    def test_list_workstreams(self, store):
        """List all workstreams."""
        store.save_workstream({'id': 'ws-1', 'status': 'pending'})
        store.save_workstream({'id': 'ws-2', 'status': 'running'})
        store.save_workstream({'id': 'ws-3', 'status': 'done'})
        
        all_ws = store.list_workstreams()
        assert len(all_ws) == 3
    
    def test_list_workstreams_filtered_by_status(self, store):
        """Filter workstreams by status."""
        store.save_workstream({'id': 'ws-1', 'status': 'pending'})
        store.save_workstream({'id': 'ws-2', 'status': 'running'})
        store.save_workstream({'id': 'ws-3', 'status': 'running'})
        
        running = store.list_workstreams(status='running')
        assert len(running) == 2
        assert all(w['status'] == 'running' for w in running)
    
    def test_record_execution(self, store):
        """Record job execution."""
        exec_id = store.record_execution({
            'run_id': 'run-001',
            'ws_id': 'ws-test',
            'status': 'running',
            'tool': 'codex'
        })
        
        assert exec_id is not None
        assert len(exec_id) > 0
    
    def test_list_executions(self, store):
        """List all executions."""
        store.record_execution({
            'run_id': 'run-001',
            'ws_id': 'ws-1',
            'status': 'running'
        })
        store.record_execution({
            'run_id': 'run-001',
            'ws_id': 'ws-2',
            'status': 'done'
        })
        
        execs = store.list_executions()
        assert len(execs) == 2
    
    def test_list_executions_filtered(self, store):
        """Filter executions by criteria."""
        store.record_execution({
            'run_id': 'run-001',
            'ws_id': 'ws-1',
            'status': 'running'
        })
        store.record_execution({
            'run_id': 'run-001',
            'ws_id': 'ws-2',
            'status': 'done'
        })
        store.record_execution({
            'run_id': 'run-002',
            'ws_id': 'ws-3',
            'status': 'running'
        })
        
        run_001 = store.list_executions({'run_id': 'run-001'})
        assert len(run_001) == 2
        
        running = store.list_executions({'status': 'running'})
        assert len(running) == 2
    
    def test_update_execution_status(self, store):
        """Update execution status."""
        exec_id = store.record_execution({
            'run_id': 'run-001',
            'ws_id': 'ws-test',
            'status': 'running'
        })
        
        store.update_execution_status(
            exec_id,
            'done',
            completed_at=datetime.now(),
            exit_code=0
        )
        
        execs = store.list_executions({'status': 'done'})
        assert len(execs) == 1
        assert execs[0]['exit_code'] == 0
    
    def test_update_nonexistent_execution_raises(self, store):
        """Updating nonexistent execution raises error."""
        with pytest.raises(ExecutionNotFoundError):
            store.update_execution_status('nonexistent', 'done')
    
    def test_record_event(self, store):
        """Record pipeline event."""
        # Should not raise
        store.record_event('job.completed', {
            'job_id': 'job-001',
            'exit_code': 0,
            'duration_s': 12.5
        })
    
    def test_save_workstream_without_id_raises(self, store):
        """Saving workstream without ID raises error."""
        with pytest.raises(ValueError):
            store.save_workstream({'status': 'pending'})


class TestStateStoreEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.fixture
    def store(self):
        """Create temporary SQLiteStateStore for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield SQLiteStateStore(Path(tmpdir) / "test.db")
    
    def test_complex_data_serialization(self, store):
        """Complex data types serialize correctly."""
        ws = {
            'id': 'ws-test',
            'status': 'pending',
            'tasks': ['Task 1', 'Task 2'],
            'metadata': {
                'priority': 'high',
                'tags': ['important', 'urgent']
            },
            'numbers': [1, 2, 3, 4, 5]
        }
        
        store.save_workstream(ws)
        retrieved = store.get_workstream('ws-test')
        
        assert retrieved['tasks'] == ws['tasks']
        assert retrieved['metadata'] == ws['metadata']
        assert retrieved['numbers'] == ws['numbers']
    
    def test_empty_filters(self, store):
        """Empty filters return all results."""
        store.record_execution({'run_id': 'run-001', 'ws_id': 'ws-1', 'status': 'done'})
        store.record_execution({'run_id': 'run-002', 'ws_id': 'ws-2', 'status': 'done'})
        
        all_execs = store.list_executions({})
        assert len(all_execs) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
