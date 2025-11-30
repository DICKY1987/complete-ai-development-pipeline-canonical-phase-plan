"""WorkstreamService Protocol - Workstream lifecycle management."""

from __future__ import annotations

from typing import Protocol, Any, runtime_checkable


@runtime_checkable
class WorkstreamService(Protocol):
    """Protocol for workstream lifecycle management."""
# DOC_ID: DOC-CORE-INTERFACES-WORKSTREAM-SERVICE-105
    
    def create(self, spec: dict[str, Any]) -> str:
        """Create new workstream, return ID."""
        ...
    
    def load(self, ws_id: str) -> dict[str, Any]:
        """Load workstream by ID."""
        ...
    
    def execute(self, ws_id: str, *, dry_run: bool = False) -> str:
        """Execute workstream, return run ID."""
        ...
    
    def get_status(self, ws_id: str) -> dict[str, Any]:
        """Get workstream status."""
        ...
    
    def list_all(self, *, status: str | None = None) -> list[dict[str, Any]]:
        """List all workstreams."""
        ...


class WorkstreamServiceError(Exception):
    """Base exception for workstream service errors."""
    pass
