"""StateStore Protocol - Abstraction for state management.

This module defines the StateStore protocol for centralizing all state operations
(workstreams, executions, jobs, errors) with unified DB/filesystem hiding.

Example:
    >>> from core.state.sqlite_store import SQLiteStateStore
    >>> store = SQLiteStateStore()
    >>> ws = store.get_workstream('ws-test-001')
    >>> print(ws['id'])
    ws-test-001
"""
# DOC_ID: DOC-CORE-INTERFACES-STATE-STORE-102

from __future__ import annotations

from typing import Protocol, Optional, Any, runtime_checkable
from datetime import datetime


@runtime_checkable
class StateStore(Protocol):
    """Protocol for state management operations.
    
    This abstraction centralizes all state operations, providing:
    - Workstream CRUD operations
    - Execution tracking
    - Job status management
    - Error recording
    - Event logging
    
    Implementations can use different backends (SQLite, Postgres, etc.)
    without changing consumer code.
    """
    
    def get_workstream(self, ws_id: str) -> Optional[dict[str, Any]]:
        """Retrieve a workstream by ID.
        
        Args:
            ws_id: Workstream identifier
            
        Returns:
            Workstream dict with metadata, or None if not found
            
        Example:
            >>> ws = store.get_workstream('ws-test')
            >>> print(ws['status'])
            pending
        """
        ...
    
    def save_workstream(self, workstream: dict[str, Any]) -> None:
        """Save or update a workstream.
        
        Args:
            workstream: Workstream dict with at least 'id' field
            
        Raises:
            ValueError: If workstream missing required fields
            
        Example:
            >>> store.save_workstream({
            ...     'id': 'ws-new',
            ...     'status': 'pending',
            ...     'tasks': ['Task 1']
            ... })
        """
        ...
    
    def list_workstreams(
        self,
        *,
        status: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """List workstreams with optional filtering.
        
        Args:
            status: Filter by status (pending, running, done, failed)
            run_id: Filter by run ID
            
        Returns:
            List of workstream dicts
            
        Example:
            >>> running = store.list_workstreams(status='running')
            >>> print(len(running))
            3
        """
        ...
    
    def record_execution(
        self,
        execution: dict[str, Any],
    ) -> str:
        """Record a job execution.
        
        Args:
            execution: Execution dict with run_id, ws_id, status, etc.
            
        Returns:
            Execution ID
            
        Example:
            >>> exec_id = store.record_execution({
            ...     'run_id': 'run-001',
            ...     'ws_id': 'ws-test',
            ...     'status': 'running',
            ...     'started_at': datetime.now()
            ... })
        """
        ...
    
    def list_executions(
        self,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        """List executions with optional filtering.
        
        Args:
            filters: Dict of filter criteria (status, run_id, ws_id, etc.)
            
        Returns:
            List of execution dicts
            
        Example:
            >>> execs = store.list_executions({'status': 'running'})
            >>> for e in execs:
            ...     print(e['ws_id'], e['started_at'])
        """
        ...
    
    def update_execution_status(
        self,
        exec_id: str,
        status: str,
        *,
        completed_at: Optional[datetime] = None,
        exit_code: Optional[int] = None,
    ) -> None:
        """Update execution status.
        
        Args:
            exec_id: Execution identifier
            status: New status (running, done, failed)
            completed_at: Completion timestamp
            exit_code: Process exit code
        """
        ...
    
    def record_event(
        self,
        event_type: str,
        payload: dict[str, Any],
    ) -> None:
        """Record a pipeline event.
        
        Args:
            event_type: Event type (job.started, job.completed, etc.)
            payload: Event data
            
        Example:
            >>> store.record_event('job.completed', {
            ...     'job_id': 'job-001',
            ...     'exit_code': 0,
            ...     'duration_s': 12.5
            ... })
        """
        ...


class StateStoreError(Exception):
    """Base exception for state store errors."""
    pass


class WorkstreamNotFoundError(StateStoreError):
    """Raised when workstream is not found."""
    
    def __init__(self, ws_id: str):
        self.ws_id = ws_id
        super().__init__(f"Workstream not found: {ws_id}")


class ExecutionNotFoundError(StateStoreError):
    """Raised when execution is not found."""
    
    def __init__(self, exec_id: str):
        self.exec_id = exec_id
        super().__init__(f"Execution not found: {exec_id}")
