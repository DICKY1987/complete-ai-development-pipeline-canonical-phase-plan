"""
Data Access Object for Worker entities.

Reference: DOC-SSOT-STATE-MACHINES-001 §6
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from core.dao.base import BaseDAO


class WorkerDAO(BaseDAO):
    """DAO for workers table."""
    
    @property
    def table_name(self) -> str:
        return "workers"
    
    @property
    def id_column(self) -> str:
        return "worker_id"
    
    def find_by_state(self, state: str) -> List[Dict[str, Any]]:
        """Find all workers in a given state."""
        return self.find_by(state=state)
