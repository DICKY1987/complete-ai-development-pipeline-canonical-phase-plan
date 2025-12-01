# DOC_LINK: DOC-CORE-INTERFACES-FILE-OPERATIONS-097
from __future__ import annotations
from typing import Protocol, runtime_checkable
from pathlib import Path

@runtime_checkable
class FileOperations(Protocol):
    def read(self, path: Path) -> str:
        ...
    
    def write(self, path: Path, content: str) -> None:
        ...
    
    def patch(self, path: Path, old: str, new: str) -> None:
        ...
    
    def exists(self, path: Path) -> bool:
        ...

class FileOperationsError(Exception):
    pass
