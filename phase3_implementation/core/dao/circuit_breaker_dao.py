"""
Data Access Object for CircuitBreaker entities.

Reference: DOC-SSOT-STATE-MACHINES-001 §6
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from core.dao.base import BaseDAO


class CircuitBreakerDAO(BaseDAO):
    """DAO for circuit_breakers table."""
    
    @property
    def table_name(self) -> str:
        return "circuit_breakers"
    
    @property
    def id_column(self) -> str:
        return "breaker_id"
    
    def find_by_state(self, state: str) -> List[Dict[str, Any]]:
        """Find all circuit_breakers in a given state."""
        return self.find_by(state=state)
    
    def get_by_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get circuit breaker by tool name."""
        results = self.find_by(tool_name=tool_name)
        return results[0] if results else None
