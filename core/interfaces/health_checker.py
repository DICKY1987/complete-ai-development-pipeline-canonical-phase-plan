# DOC_LINK: DOC-CORE-INTERFACES-HEALTH-CHECKER-098
from __future__ import annotations
from typing import Protocol, runtime_checkable

@runtime_checkable
class HealthChecker(Protocol):
    def check(self) -> dict[str, str]:
        ...
    
    def is_healthy(self) -> bool:
        ...

class HealthCheckError(Exception):
    pass
