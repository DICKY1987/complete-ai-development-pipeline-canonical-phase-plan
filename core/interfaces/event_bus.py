"""EventBus Protocol - Abstraction for event pub/sub system."""

from __future__ import annotations

from typing import Protocol, Any, Callable, runtime_checkable


@runtime_checkable
class EventBus(Protocol):
    """Protocol for event publishing and subscription.
    
    Features:
    - Publish events to subscribers
    - Subscribe to event types
    - Unsubscribe from events
    - Async event delivery support
    """
# DOC_ID: DOC-CORE-INTERFACES-EVENT-BUS-096
    
    def emit(self, event_type: str, payload: dict[str, Any]) -> None:
        """Emit an event to all subscribers.
        
        Args:
            event_type: Type of event (e.g., 'job.started')
            payload: Event data
        """
        ...
    
    def subscribe(
        self,
        event_type: str,
        handler: Callable[[dict[str, Any]], None],
    ) -> str:
        """Subscribe to events of a specific type.
        
        Args:
            event_type: Event type to subscribe to
            handler: Callback function for events
            
        Returns:
            Subscription ID for unsubscribing
        """
        ...
    
    def unsubscribe(self, subscription_id: str) -> None:
        """Unsubscribe from events.
        
        Args:
            subscription_id: ID returned from subscribe()
        """
        ...


class EventBusError(Exception):
    """Base exception for event bus errors."""
    pass
