# DOC_LINK: DOC-CORE-INTERFACES-DATA-PROVIDER-095
from __future__ import annotations
from typing import Protocol, Any, runtime_checkable

@runtime_checkable
class DataProvider(Protocol):
    def get_workstreams(self) -> list[dict[str, Any]]:
        ...
    
    def get_executions(self, ws_id: str) -> list[dict[str, Any]]:
        ...
    
    def get_metrics(self) -> dict[str, Any]:
        ...

class DataProviderError(Exception):
    pass
