from __future__ import annotations
from typing import Any
from core.interfaces.state_store import StateStore

class StateDataProvider:
    def __init__(self, state_store: StateStore):
        self.state = state_store
    
    def get_workstreams(self) -> list[dict[str, Any]]:
        return self.state.list_workstreams()
    
    def get_executions(self, ws_id: str) -> list[dict[str, Any]]:
        return self.state.list_executions(ws_id)
    
    def get_metrics(self) -> dict[str, Any]:
        ws_list = self.get_workstreams()
        return {
            'total_workstreams': len(ws_list),
            'by_status': self._count_by_status(ws_list)
        }
    
    def _count_by_status(self, ws_list: list) -> dict[str, int]:
        counts = {}
        for ws in ws_list:
            status = ws.get('status', 'unknown')
            counts[status] = counts.get(status, 0) + 1
        return counts
