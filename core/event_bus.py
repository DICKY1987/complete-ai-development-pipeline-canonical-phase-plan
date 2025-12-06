"""Compatibility shim exposing the event bus interface."""
DOC_ID: DOC-CORE-CORE-EVENT-BUS-772

from core.events.event_bus import Event, EventBus, EventSeverity, EventType

__all__ = ["Event", "EventBus", "EventSeverity", "EventType"]
