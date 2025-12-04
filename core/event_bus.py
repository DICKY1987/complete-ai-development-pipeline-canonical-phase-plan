"""Compatibility shim exposing the event bus interface."""

from core.events.event_bus import Event, EventBus, EventSeverity, EventType

__all__ = ["Event", "EventBus", "EventSeverity", "EventType"]
