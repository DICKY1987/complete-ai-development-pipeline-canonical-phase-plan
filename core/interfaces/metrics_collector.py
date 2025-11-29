from __future__ import annotations
from typing import Protocol, runtime_checkable

@runtime_checkable
class MetricsCollector(Protocol):
    def increment(self, metric: str, value: int = 1) -> None:
        ...
    
    def gauge(self, metric: str, value: float) -> None:
        ...
    
    def timing(self, metric: str, duration_ms: float) -> None:
        ...

class MetricsError(Exception):
    pass
