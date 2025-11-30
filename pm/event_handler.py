"""
Event Handler - Pipeline Lifecycle Events

Handles events from the core pipeline orchestrator and:
- Updates local CCPM task status
- Optionally syncs to GitHub issues (when enabled)
- Provides event logging and tracking

This is the final integration piece that connects pipeline execution
to CCPM workflow tracking and GitHub visibility.
"""
DOC_ID: DOC-PM-PM-EVENT-HANDLER-015
DOC_ID: DOC-PM-PM-EVENT-HANDLER-009

from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import logging

from pm.models import WorkstreamEvent, EventType, Status

# Try to import GitHub sync (optional)
try:
    from modules.pm_integrations.m01001F_github_sync import comment, set_status, post_lifecycle_comment, LifecycleEvent
    HAS_GITHUB_SYNC = True
except ImportError:
    HAS_GITHUB_SYNC = False

# Try to import epic manager for status updates
try:
    from pm.epic import EpicManager
    HAS_EPIC_MANAGER = True
except ImportError:
    HAS_EPIC_MANAGER = False


logger = logging.getLogger(__name__)


class PipelineEventHandler:
    """
    Handles pipeline lifecycle events and syncs to CCPM tasks/GitHub.
    
    This is the glue between the orchestrator and PM tracking.
    """
    
    def __init__(self, enable_github: bool = None):
        """
        Initialize event handler.
        
        Args:
            enable_github: Override for GitHub sync (default: check config)
        """
        self.enable_github = enable_github
        if self.enable_github is None:
            self.enable_github = self._should_enable_github()
        
        self.epic_manager = EpicManager() if HAS_EPIC_MANAGER else None
    
    def _should_enable_github(self) -> bool:
        """Check if GitHub sync should be enabled."""
        if not HAS_GITHUB_SYNC:
            return False
        
        # Check config
        try:
            from modules.pm_integrations.m01001F_github_sync import _enabled
            return _enabled()
        except Exception:
            return False
    
    def handle(self, event: WorkstreamEvent) -> None:
        """
        Process a pipeline event.
        
        Args:
            event: Workstream event from orchestrator
        """
        try:
            # Update local task status
            self._update_task_status(event)
            
            # Sync to GitHub (if enabled and event has issue number)
            if self.enable_github:
                self._sync_to_github(event)
            
            # Log event
            self._log_event(event)
        
        except Exception as e:
            logger.error(f"Error handling event {event.event_type}: {e}")
    
    def on_workstream_start(
        self,
        ws_id: str,
        epic_name: Optional[str] = None,
        task_id: Optional[str] = None,
        **payload
    ) -> None:
        """
        Handle workstream start event.
        
        Args:
            ws_id: Workstream ID
            epic_name: Epic name (optional)
            task_id: Task ID (optional)
            **payload: Additional event data
        """
        event = WorkstreamEvent(
            event_type=EventType.WORKSTREAM_START,
            ws_id=ws_id,
            epic_name=epic_name,
            task_id=task_id,
            timestamp=datetime.utcnow(),
            payload=payload,
        )
        self.handle(event)
    
    def on_step_complete(
        self,
        ws_id: str,
        step_name: str,
        success: bool,
        epic_name: Optional[str] = None,
        task_id: Optional[str] = None,
        **payload
    ) -> None:
        """
        Handle step completion event.
        
        Args:
            ws_id: Workstream ID
            step_name: Step that completed
            success: Whether step succeeded
            epic_name: Epic name (optional)
            task_id: Task ID (optional)
            **payload: Additional data
        """
        event = WorkstreamEvent(
            event_type=EventType.STEP_COMPLETE,
            ws_id=ws_id,
            epic_name=epic_name,
            task_id=task_id,
            timestamp=datetime.utcnow(),
            payload={
                "step_name": step_name,
                "success": success,
                **payload
            },
        )
        self.handle(event)
    
    def on_workstream_complete(
        self,
        ws_id: str,
        success: bool,
        final_state: str,
        epic_name: Optional[str] = None,
        task_id: Optional[str] = None,
        **payload
    ) -> None:
        """
        Handle workstream completion event.
        
        Args:
            ws_id: Workstream ID
            success: Whether workstream succeeded
            final_state: Final pipeline state
            epic_name: Epic name (optional)
            task_id: Task ID (optional)
            **payload: Additional data
        """
        event = WorkstreamEvent(
            event_type=EventType.WORKSTREAM_COMPLETE,
            ws_id=ws_id,
            epic_name=epic_name,
            task_id=task_id,
            timestamp=datetime.utcnow(),
            payload={
                "success": success,
                "final_state": final_state,
                **payload
            },
        )
        self.handle(event)
    
    def on_workstream_blocked(
        self,
        ws_id: str,
        reason: str,
        epic_name: Optional[str] = None,
        task_id: Optional[str] = None,
        **payload
    ) -> None:
        """
        Handle workstream blocked event.
        
        Args:
            ws_id: Workstream ID
            reason: Why workstream is blocked
            epic_name: Epic name (optional)
            task_id: Task ID (optional)
            **payload: Additional data
        """
        event = WorkstreamEvent(
            event_type=EventType.WORKSTREAM_BLOCKED,
            ws_id=ws_id,
            epic_name=epic_name,
            task_id=task_id,
            timestamp=datetime.utcnow(),
            payload={
                "reason": reason,
                **payload
            },
        )
        self.handle(event)
    
    def on_workstream_failed(
        self,
        ws_id: str,
        error: str,
        epic_name: Optional[str] = None,
        task_id: Optional[str] = None,
        **payload
    ) -> None:
        """
        Handle workstream failure event.
        
        Args:
            ws_id: Workstream ID
            error: Error message
            epic_name: Epic name (optional)
            task_id: Task ID (optional)
            **payload: Additional data
        """
        event = WorkstreamEvent(
            event_type=EventType.WORKSTREAM_FAILED,
            ws_id=ws_id,
            epic_name=epic_name,
            task_id=task_id,
            timestamp=datetime.utcnow(),
            payload={
                "error": error,
                **payload
            },
        )
        self.handle(event)
    
    def _update_task_status(self, event: WorkstreamEvent) -> None:
        """Update local CCPM task status based on event."""
        if not self.epic_manager:
            return  # No epic manager available
        
        # Parse epic/task from workstream ID if not provided
        epic_name = event.epic_name
        task_id = event.task_id
        
        if not epic_name or not task_id:
            # Try to parse from ws_id (format: ws-{epic}-{task})
            parts = event.ws_id.split('-', 2)
            if len(parts) >= 3:
                epic_name = parts[1]
                task_id = parts[2]
        
        if not epic_name or not task_id:
            return  # Can't determine task
        
        # Map event type to status
        new_status = self._event_to_status(event)
        
        if new_status:
            try:
                self.epic_manager.update_task_status(epic_name, task_id, new_status)
                logger.info(f"Updated task {epic_name}/{task_id} to {new_status.value}")
            except Exception as e:
                logger.warning(f"Failed to update task status: {e}")
    
    def _event_to_status(self, event: WorkstreamEvent) -> Optional[Status]:
        """Map event to task status."""
        event_type = event.event_type
        
        if event_type == EventType.WORKSTREAM_START:
            return Status.IN_PROGRESS
        
        elif event_type == EventType.WORKSTREAM_COMPLETE:
            if event.payload.get("success"):
                return Status.COMPLETED
            else:
                return Status.BLOCKED
        
        elif event_type == EventType.WORKSTREAM_BLOCKED:
            return Status.BLOCKED
        
        elif event_type == EventType.WORKSTREAM_FAILED:
            return Status.BLOCKED
        
        # STEP_COMPLETE doesn't change task status
        return None
    
    def _sync_to_github(self, event: WorkstreamEvent) -> None:
        """Sync event to GitHub issue (if issue number available)."""
        if not HAS_GITHUB_SYNC:
            return
        
        # Get issue number from payload or load from epic
        issue_num = event.payload.get("github_issue")
        
        if not issue_num and event.epic_name and self.epic_manager:
            try:
                epic = self.epic_manager.load_epic(event.epic_name, load_tasks=False)
                issue_num = epic.github_issue
            except Exception:
                pass
        
        if not issue_num:
            return  # No GitHub issue to update
        
        # Format lifecycle event
        lifecycle_event = LifecycleEvent(
            run_id=event.payload.get("run_id", "unknown"),
            ws_id=event.ws_id,
            step=event.event_type.value,
            final_status=event.payload.get("final_state"),
        )
        
        # Post comment
        try:
            post_lifecycle_comment(issue_num, lifecycle_event)
            logger.info(f"Posted GitHub comment to issue #{issue_num}")
        except Exception as e:
            logger.warning(f"Failed to post GitHub comment: {e}")
        
        # Update labels/state on completion
        if event.event_type == EventType.WORKSTREAM_COMPLETE:
            try:
                if event.payload.get("success"):
                    set_status(issue_num, state="closed", add_labels=["completed"])
                else:
                    set_status(issue_num, add_labels=["blocked"])
            except Exception as e:
                logger.warning(f"Failed to update GitHub issue status: {e}")
    
    def _log_event(self, event: WorkstreamEvent) -> None:
        """Log event for debugging/auditing."""
        logger.info(
            f"Event: {event.event_type.value} | "
            f"WS: {event.ws_id} | "
            f"Epic: {event.epic_name or 'N/A'} | "
            f"Task: {event.task_id or 'N/A'}"
        )


# Global event handler instance (singleton pattern)
_global_handler: Optional[PipelineEventHandler] = None


def get_event_handler(enable_github: bool = None) -> PipelineEventHandler:
    """
    Get or create global event handler instance.
    
    Args:
        enable_github: Override GitHub sync setting
    
    Returns:
        PipelineEventHandler instance
    """
    global _global_handler
    
    if _global_handler is None:
        _global_handler = PipelineEventHandler(enable_github=enable_github)
    
    return _global_handler


# Convenience functions for orchestrator integration

def emit_workstream_start(ws_id: str, **kwargs) -> None:
    """Emit workstream start event."""
    handler = get_event_handler()
    handler.on_workstream_start(ws_id, **kwargs)


def emit_step_complete(ws_id: str, step_name: str, success: bool, **kwargs) -> None:
    """Emit step completion event."""
    handler = get_event_handler()
    handler.on_step_complete(ws_id, step_name, success, **kwargs)


def emit_workstream_complete(ws_id: str, success: bool, final_state: str, **kwargs) -> None:
    """Emit workstream completion event."""
    handler = get_event_handler()
    handler.on_workstream_complete(ws_id, success, final_state, **kwargs)


def emit_workstream_blocked(ws_id: str, reason: str, **kwargs) -> None:
    """Emit workstream blocked event."""
    handler = get_event_handler()
    handler.on_workstream_blocked(ws_id, reason, **kwargs)


def emit_workstream_failed(ws_id: str, error: str, **kwargs) -> None:
    """Emit workstream failure event."""
    handler = get_event_handler()
    handler.on_workstream_failed(ws_id, error, **kwargs)


__all__ = [
    "PipelineEventHandler",
    "get_event_handler",
    "emit_workstream_start",
    "emit_step_complete",
    "emit_workstream_complete",
    "emit_workstream_blocked",
    "emit_workstream_failed",
]
