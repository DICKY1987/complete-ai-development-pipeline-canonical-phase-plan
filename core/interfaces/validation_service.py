from __future__ import annotations
from typing import Protocol, Any, runtime_checkable

@runtime_checkable
class ValidationService(Protocol):
    def validate(self, data: dict[str, Any], schema: str) -> list[str]:
        ...
    
    def validate_workstream(self, ws: dict[str, Any]) -> list[str]:
        ...

class ValidationError(Exception):
    pass
