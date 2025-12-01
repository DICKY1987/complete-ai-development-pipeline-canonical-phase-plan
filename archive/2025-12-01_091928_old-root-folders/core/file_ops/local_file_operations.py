# DOC_LINK: DOC-CORE-FILE-OPS-LOCAL-FILE-OPERATIONS-089
from __future__ import annotations
from pathlib import Path

class LocalFileOperations:
    def read(self, path: Path) -> str:
        return path.read_text(encoding='utf-8')
    
    def write(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
    
    def patch(self, path: Path, old: str, new: str) -> None:
        content = self.read(path)
        if old not in content:
            raise ValueError(f"Pattern not found: {old}")
        self.write(path, content.replace(old, new, 1))
    
    def exists(self, path: Path) -> bool:
        return path.exists()
