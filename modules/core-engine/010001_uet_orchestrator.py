"""Run Orchestrator - WS-03-01A

Main orchestration logic for executing workstreams.
Manages run lifecycle, state transitions, and event emission.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from modules.core_state.010003_uet_db_adapter import Database, get_db
from modules.core_engine.010001_uet_state_machine import RunStateMachine, StepStateMachine


def generate_ulid() -> str:
    """Generate a ULID-compatible ID (using UUID for now)"""
    # TODO: Replace with actual ULID library
    return uuid.uuid4().hex.upper()[:26]


def now_iso() -> str:
    """Get current timestamp in ISO format"""
    return datetime.utcnow().isoformat() + "Z"


class Orchestrator:
    """Main orchestration engine for running workstreams"""
    
    def __init__(self, db: Optional[Database] = None):
        self.db = db or get_db()
    
    # Run lifecycle management
    
    def create_run(self, project_id: str, phase_id: str, workstream_id: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new run in pending state.
        
        Args:
            project_id: Project identifier
            phase_id: Phase being executed
            workstream_id: Optional workstream being executed
            metadata: Optional metadata dictionary
            
        Returns:
            run_id: Created run identifier
        """
        run_id = generate_ulid()
        
        run_data = {
            'run_id': run_id,
            'project_id': project_id,
            'phase_id': phase_id,
            'workstream_id': workstream_id,
            'created_at': now_iso(),
            'state': 'pending',
            'metadata': metadata or {}
        }
        
        self.db.create_run(run_data)
        
        # Emit event
        self._emit_event(run_id, 'run_created', {
            'project_id': project_id,
            'phase_id': phase_id,
            'workstream_id': workstream_id
        })
        
        return run_id
    
    def start_run(self, run_id: str) -> bool:
        """
        Transition run from pending to running.
        
        Args:
            run_id: Run to start
            
        Returns:
            True if transition succeeded, False otherwise
        """
        run = self.db.get_run(run_id)
        if not run:
            raise ValueError(f"Run not found: {run_id}")
        
        # Validate transition
        error = RunStateMachine.validate_transition(run['state'], 'running')
        if error:
            raise ValueError(error)
        
        # Update state
        self.db.update_run(run_id, {
            'state': 'running',
            'started_at': now_iso()
        })
        
        # Emit event
        self._emit_event(run_id, 'run_started', {})
        
        return True
    
    def complete_run(self, run_id: str, status: str, exit_code: int = 0,
                     error_message: Optional[str] = None) -> bool:
        """
        Complete a run with success/failure status.
        
        Args:
            run_id: Run to complete
            status: Final status ('succeeded', 'failed', 'quarantined', 'canceled')
            exit_code: Exit code (0 for success)
            error_message: Optional error message
            
        Returns:
            True if transition succeeded, False otherwise
        """
        run = self.db.get_run(run_id)
        if not run:
            raise ValueError(f"Run not found: {run_id}")
        
        # Validate transition
        error = RunStateMachine.validate_transition(run['state'], status)
        if error:
            raise ValueError(error)
        
        # Update state
        updates = {
            'state': status,
            'ended_at': now_iso(),
            'exit_code': exit_code
        }
        
        if error_message:
            updates['error_message'] = error_message
        
        self.db.update_run(run_id, updates)
        
        # Emit event
        self._emit_event(run_id, 'run_completed', {
            'status': status,
            'exit_code': exit_code
        })
        
        return True
    
    def quarantine_run(self, run_id: str, reason: str) -> bool:
        """
        Quarantine a run due to errors or safety concerns.
        
        Args:
            run_id: Run to quarantine
            reason: Reason for quarantine
            
        Returns:
            True if successful
        """
        run = self.db.get_run(run_id)
        if not run:
            raise ValueError(f"Run not found: {run_id}")
        
        # Can quarantine from running or failed state
        current_state = run['state']
        if current_state not in ['running', 'failed']:
            raise ValueError(f"Cannot quarantine run in state '{current_state}'")
        
        error = RunStateMachine.validate_transition(current_state, 'quarantined')
        if error:
            raise ValueError(error)
        
        self.db.update_run(run_id, {
            'state': 'quarantined',
            'ended_at': now_iso(),
            'error_message': reason
        })
        
        self._emit_event(run_id, 'run_quarantined', {'reason': reason})
        
        return True
    
    def cancel_run(self, run_id: str, reason: str = "Canceled by user") -> bool:
        """
        Cancel a pending or running run.
        
        Args:
            run_id: Run to cancel
            reason: Cancellation reason
            
        Returns:
            True if successful
        """
        run = self.db.get_run(run_id)
        if not run:
            raise ValueError(f"Run not found: {run_id}")
        
        error = RunStateMachine.validate_transition(run['state'], 'canceled')
        if error:
            raise ValueError(error)
        
        self.db.update_run(run_id, {
            'state': 'canceled',
            'ended_at': now_iso(),
            'error_message': reason
        })
        
        self._emit_event(run_id, 'run_canceled', {'reason': reason})
        
        return True
    
    # Step attempt management
    
    def create_step_attempt(self, run_id: str, tool_id: str, sequence: int,
                           prompt: Optional[str] = None,
                           metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a step attempt within a run.
        
        Args:
            run_id: Parent run ID
            tool_id: Tool being invoked
            sequence: Step sequence number
            prompt: Optional input prompt
            metadata: Optional metadata
            
        Returns:
            step_attempt_id: Created step attempt ID
        """
        # Verify run exists and is running
        run = self.db.get_run(run_id)
        if not run:
            raise ValueError(f"Run not found: {run_id}")
        
        if run['state'] != 'running':
            raise ValueError(f"Cannot create step for run in state '{run['state']}'")
        
        step_id = generate_ulid()
        
        step_data = {
            'step_attempt_id': step_id,
            'run_id': run_id,
            'sequence': sequence,
            'tool_id': tool_id,
            'started_at': now_iso(),
            'state': 'running',
            'metadata': metadata or {}
        }
        
        # Add prompt if provided (not in minimal schema)
        if prompt:
            step_data['input_prompt'] = prompt
        
        self.db.create_step_attempt(step_data)
        
        self._emit_event(run_id, 'step_started', {
            'step_attempt_id': step_id,
            'sequence': sequence,
            'tool_id': tool_id
        })
        
        return step_id
    
    def complete_step_attempt(self, step_attempt_id: str, status: str,
                              exit_code: int = 0, output_patch_id: Optional[str] = None,
                              error_log: Optional[str] = None) -> bool:
        """
        Complete a step attempt with status.
        
        Args:
            step_attempt_id: Step to complete
            status: Final status ('succeeded', 'failed', 'canceled')
            exit_code: Exit code
            output_patch_id: Optional patch artifact ID
            error_log: Optional error log
            
        Returns:
            True if successful
        """
        step = self.db.get_step_attempt(step_attempt_id)
        if not step:
            raise ValueError(f"Step attempt not found: {step_attempt_id}")
        
        error = StepStateMachine.validate_transition(step['state'], status)
        if error:
            raise ValueError(error)
        
        updates = {
            'state': status,
            'ended_at': now_iso(),
            'exit_code': exit_code
        }
        
        if output_patch_id:
            updates['output_patch_id'] = output_patch_id
        
        if error_log:
            updates['error_log'] = error_log
        
        self.db.update_step_attempt(step_attempt_id, updates)
        
        self._emit_event(step['run_id'], 'step_completed', {
            'step_attempt_id': step_attempt_id,
            'status': status,
            'exit_code': exit_code
        })
        
        return True
    
    # Query methods
    
    def get_run_status(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get current run status"""
        return self.db.get_run(run_id)
    
    def list_runs(self, project_id: Optional[str] = None, 
                  state: Optional[str] = None,
                  limit: int = 100) -> List[Dict[str, Any]]:
        """List runs with optional filters"""
        filters = {}
        if project_id:
            filters['project_id'] = project_id
        if state:
            filters['state'] = state
        
        return self.db.list_runs(filters, limit)
    
    def get_run_steps(self, run_id: str) -> List[Dict[str, Any]]:
        """Get all steps for a run"""
        return self.db.list_step_attempts(run_id)
    
    def get_run_events(self, run_id: str) -> List[Dict[str, Any]]:
        """Get all events for a run"""
        return self.db.list_events(run_id)
    
    # Event emission
    
    def _emit_event(self, run_id: str, event_type: str, data: Dict[str, Any]):
        """Emit a run event"""
        event_id = generate_ulid()
        
        event_data = {
            'event_id': event_id,
            'run_id': run_id,
            'timestamp': now_iso(),
            'event_type': event_type,
            'data': data
        }
        
        self.db.create_event(event_data)
