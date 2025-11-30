# DOC_LINK: DOC-CORE-WORKSTREAMS-WORKSTREAM-SERVICE-IMPL-115
from __future__ import annotations
import uuid
from typing import Any
from core.interfaces.state_store import StateStore

class WorkstreamServiceImpl:
    def __init__(self, state_store: StateStore):
        self.state = state_store
    
    def create(self, spec: dict[str, Any]) -> str:
        ws_id = f"ws-{uuid.uuid4().hex[:8]}"
        workstream = {'id': ws_id, 'status': 'pending', **spec}
        self.state.save_workstream(workstream)
        return ws_id
    
    def load(self, ws_id: str) -> dict[str, Any]:
        ws = self.state.get_workstream(ws_id)
        if not ws:
            raise ValueError(f"Workstream not found: {ws_id}")
        return ws
    
    def execute(self, ws_id: str, *, dry_run: bool = False) -> str:
        run_id = f"run-{uuid.uuid4().hex[:8]}"
        ws = self.load(ws_id)
        ws['status'] = 'running' if not dry_run else 'dry_run'
        ws['run_id'] = run_id
        self.state.save_workstream(ws)
        return run_id
    
    def get_status(self, ws_id: str) -> dict[str, Any]:
        ws = self.load(ws_id)
        return {'id': ws['id'], 'status': ws.get('status', 'unknown'), 'run_id': ws.get('run_id')}
    
    def list_all(self, *, status: str | None = None) -> list[dict[str, Any]]:
        return self.state.list_workstreams(status=status)
