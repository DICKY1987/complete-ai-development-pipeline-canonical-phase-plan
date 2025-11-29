from __future__ import annotations
from typing import Protocol, Any, Optional, runtime_checkable

@runtime_checkable
class CacheManager(Protocol):
    def get(self, key: str) -> Optional[Any]:
        ...
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        ...
    
    def invalidate(self, key: str) -> None:
        ...

class CacheError(Exception):
    pass
