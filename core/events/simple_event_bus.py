"""In-memory event bus used for lightweight pub/sub and tests.

DOC_ID: DOC-CORE-EVENTS-SIMPLE-EVENT-BUS-848
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union

from core.events.event_bus import Event, EventBus, EventType


class SimpleEventBus(EventBus):
    """Simple pub/sub without persistence."""

    def __init__(self):
        super().__init__(db_path=None)

    def emit(
        self,
        event: Union[Event, EventType, str],
        payload: Optional[Dict[str, Any]] = None,
        **metadata: Any,
    ) -> str:
        evt = self._coerce_event(
            event,
            payload=payload,
            timestamp=metadata.pop("timestamp", None) or datetime.now(timezone.utc),
            **metadata,
        )
        key = self._event_type_value(evt.event_type)
        for etype in (key, "*"):
            for _, handler in self._subscribers.get(etype, []):
                try:
                    handler(evt.payload or {})
                except Exception:
                    continue
        return evt.run_id or ""
