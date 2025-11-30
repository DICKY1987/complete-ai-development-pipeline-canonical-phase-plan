# DOC_LINK: DOC-CORE-CACHE-MEMORY-CACHE-MANAGER-075
from __future__ import annotations
from typing import Any, Optional
import time

class MemoryCacheManager:
    def __init__(self):
        self._cache: dict[str, tuple[Any, float]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        if key not in self._cache:
            return None
        value, expiry = self._cache[key]
        if expiry < time.time():
            del self._cache[key]
            return None
        return value
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        expiry = time.time() + ttl
        self._cache[key] = (value, expiry)
    
    def invalidate(self, key: str) -> None:
        self._cache.pop(key, None)
