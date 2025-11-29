from __future__ import annotations
import uuid
from typing import Any, Callable
from collections import defaultdict

class SimpleEventBus:
    def __init__(self):
        self._subscribers: dict[str, dict[str, Callable]] = defaultdict(dict)
    
    def emit(self, event_type: str, payload: dict[str, Any]) -> None:
        for handler in self._subscribers[event_type].values():
            try:
                handler(payload)
            except Exception:
                pass
    
    def subscribe(self, event_type: str, handler: Callable[[dict[str, Any]], None]) -> str:
        sub_id = str(uuid.uuid4())
        self._subscribers[event_type][sub_id] = handler
        return sub_id
    
    def unsubscribe(self, subscription_id: str) -> None:
        for event_subs in self._subscribers.values():
            if subscription_id in event_subs:
                del event_subs[subscription_id]
                return
