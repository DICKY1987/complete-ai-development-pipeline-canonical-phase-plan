"""
Data Access Object for Run entities.

Reference: DOC-SSOT-STATE-MACHINES-001 §6
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from core.dao.base import BaseDAO


class RunDAO(BaseDAO):
    """DAO for runs table."""
    
    @property
    def table_name(self) -> str:
        return "runs"
    
    @property
    def id_column(self) -> str:
        return "run_id"
    
    def find_by_state(self, state: str) -> List[Dict[str, Any]]:
        """Find all runs in a given state."""
        return self.find_by(state=state)
