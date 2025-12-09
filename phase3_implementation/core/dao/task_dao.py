"""
Data Access Object for Task entities.

Reference: DOC-SSOT-STATE-MACHINES-001 §6
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from core.dao.base import BaseDAO


class TaskDAO(BaseDAO):
    """DAO for tasks table."""
    
    @property
    def table_name(self) -> str:
        return "tasks"
    
    @property
    def id_column(self) -> str:
        return "task_id"
    
    def find_by_state(self, state: str) -> List[Dict[str, Any]]:
        """Find all tasks in a given state."""
        return self.find_by(state=state)
    
    def find_by_workstream(self, workstream_id: str) -> List[Dict[str, Any]]:
        """Find all tasks for a workstream."""
        return self.find_by(workstream_id=workstream_id)
    
    def find_by_worker(self, worker_id: str) -> List[Dict[str, Any]]:
        """Find all tasks assigned to a worker."""
        return self.find_by(worker_id=worker_id)
