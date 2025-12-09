"""
Data Access Object for TestGate entities.

Reference: DOC-SSOT-STATE-MACHINES-001 §6
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from core.dao.base import BaseDAO


class TestGateDAO(BaseDAO):
    """DAO for test_gates table."""
    
    @property
    def table_name(self) -> str:
        return "test_gates"
    
    @property
    def id_column(self) -> str:
        return "gate_id"
    
    def find_by_state(self, state: str) -> List[Dict[str, Any]]:
        """Find all test_gates in a given state."""
        return self.find_by(state=state)
    
    def find_by_task(self, task_id: str) -> List[Dict[str, Any]]:
        """Find all test_gates for a task."""
        return self.find_by(task_id=task_id)
