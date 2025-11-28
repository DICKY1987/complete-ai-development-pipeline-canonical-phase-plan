from __future__ import annotations

import ast
import json
import os
import re
import sqlite3
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Tuple

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional dependency checked at runtime
    yaml = None  # type: ignore


# Simple, conservative path-like pattern. We avoid matching URLs and single words.
PATH_REGEX = re.compile(
    r"(?P<path>(?:[A-Za-z]:\\\\|\\\\\\\\|\.|~)?(?:[\\/][^\\/\n\r\t\f\v]+){1,})"
)


SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".venv",
    "venv",
    "node_modules",
    "build",
    "dist",
    "logs",
    "state",
}


CODE_EXTS = {".py", ".ps1", ".psm1", ".sh", ".bat", ".cmd"}
CONFIG_EXTS = {".yml", ".yaml", ".json", ".ini", ".cfg", ".toml"}
DOC_EXTS = {".md", ".txt"}


TRACKED_PATTERNS = [
    # High-signal repo sections
    "src/",
    "tests/",
    "docs/",
    "tools/",
    "scripts/",
    "config/",
    "schema/",
    "openspec/",
    "workstreams/",
    "PHASE_DEV_DOCS",
    "MOD_ERROR_PIPELINE",
    "gui",
    "sandbox_repos/",
]


@dataclass
class Occurrence:
    file_path: str
    line_no: int
    kind: str
    value: str
    pattern: Optional[str]
    ext: str
    context: Optional[str] = None


class HardcodedPathIndexer:
    def __init__(self, root: Path, db_path: Path):
        self.root = root.resolve()
        self.db_path = db_path.resolve()
        self.conn: Optional[sqlite3.Connection] = None

    # -------- DB management --------
    def connect(self) -> None:
        if self.conn is None:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.execute("PRAGMA synchronous=NORMAL;")
            self._init_schema()

    def close(self) -> None:
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def _init_schema(self) -> None:
        assert self.conn is not None
        cur = self.conn.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT
            );

            CREATE TABLE IF NOT EXISTS files (
                file_path TEXT PRIMARY KEY,
                ext TEXT,
                size INTEGER,
                mtime REAL,
                scanned_at REAL
            );

            CREATE TABLE IF NOT EXISTS occurrences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT,
                line_no INTEGER,
                kind TEXT,
                pattern TEXT,
                value TEXT,
                context TEXT,
                ext TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_occ_kind ON occurrences(kind);
            CREATE INDEX IF NOT EXISTS idx_occ_pattern ON occurrences(pattern);
            CREATE INDEX IF NOT EXISTS idx_occ_file ON occurrences(file_path);
            """
        )
        self.conn.commit()

    def reset(self) -> None:
        if self.db_path.exists():
            self.db_path.unlink()
        self.connect()

    # -------- Scanning --------
    def scan(self, include_hidden: bool = False) -> Tuple[int, int]:
        self.connect()
        assert self.conn is not None

        files = list(self._iter_files(include_hidden=include_hidden))
        files.sort()
        now = time.time()
        inserted_files = 0
        inserted_occ = 0

        cur = self.conn.cursor()
        for fp in files:
            try:
                stat = fp.stat()
                cur.execute(
                    "REPLACE INTO files(file_path, ext, size, mtime, scanned_at) VALUES (?,?,?,?,?)",
                    (
                        str(fp.relative_to(self.root)),
                        fp.suffix.lower(),
                        stat.st_size,
                        stat.st_mtime,
                        now,
                    ),
                )
                inserted_files += 1

                occurrences = list(self._scan_file(fp))
                for occ in occurrences:
                    cur.execute(
                        "INSERT INTO occurrences(file_path, line_no, kind, pattern, value, context, ext) VALUES (?,?,?,?,?,?,?)",
                        (
                            occ.file_path,
                            occ.line_no,
                            occ.kind,
                            occ.pattern,
                            occ.value,
                            occ.context,
                            occ.ext,
                        ),
                    )
                inserted_occ += len(occurrences)
            except Exception:
                # Best-effort scanning; continue on errors
                continue

        self.conn.commit()
        return inserted_files, inserted_occ

    def _iter_files(self, include_hidden: bool = False) -> Iterator[Path]:
        for dirpath, dirnames, filenames in os.walk(self.root):
            rel = Path(dirpath).resolve().relative_to(self.root)
            # mutate dirnames to prune traversal
            pruned: List[str] = []
            for d in list(dirnames):
                if d in SKIP_DIRS:
                    pruned.append(d)
                elif not include_hidden and d.startswith('.'):
                    pruned.append(d)
            for d in pruned:
                dirnames.remove(d)

            for name in filenames:
                if not include_hidden and name.startswith('.'):  # skip hidden files
                    continue
                fp = Path(dirpath) / name
                # Skip the DB itself
                if fp.resolve() == self.db_path:
                    continue
                yield fp

    # -------- File scanners --------
    def _scan_file(self, fp: Path) -> Iterator[Occurrence]:
        rel_path = str(fp.resolve().relative_to(self.root))
        ext = fp.suffix.lower()
        try:
            text = fp.read_text(encoding="utf-8", errors="replace")
        except Exception:
            # Binary or unreadable
            return iter(())

        if ext == ".py":
            yield from self._scan_python(fp, text)
            # Also pick up literal paths in strings
            for ln, line in enumerate(text.splitlines(), start=1):
                for m in PATH_REGEX.finditer(line):
                    val = m.group("path")
                    if self._looks_like_path(val):
                        yield self._occ(rel_path, ln, "fs_literal", val, ext, line)
            return

        if ext in {".ps1", ".psm1", ".sh", ".bat", ".cmd"}:
            for ln, line in enumerate(text.splitlines(), start=1):
                for m in PATH_REGEX.finditer(line):
                    val = m.group("path")
                    if self._looks_like_path(val):
                        yield self._occ(rel_path, ln, "code_path", val, ext, line)
            return

        if ext in {".yml", ".yaml"} and yaml is not None:
            # Structured parse
            try:
                data = list(yaml.safe_load_all(text))
            except Exception:
                data = []
            for ln, line in enumerate(text.splitlines(), start=1):
                for m in PATH_REGEX.finditer(line):
                    val = m.group("path")
                    if self._looks_like_path(val):
                        yield self._occ(rel_path, ln, "config_path", val, ext, line)
            # Inspect values in structured data
            for doc in data:
                for path_val in self._iter_string_values(doc):
                    if self._looks_like_path(path_val):
                        yield self._occ(rel_path, 0, "config_path", path_val, ext, None)
            return

        if ext == ".json":
            try:
                data = json.loads(text)
            except Exception:
                data = None
            for ln, line in enumerate(text.splitlines(), start=1):
                for m in PATH_REGEX.finditer(line):
                    val = m.group("path")
                    if self._looks_like_path(val):
                        yield self._occ(rel_path, ln, "config_path", val, ext, line)
            if data is not None:
                for path_val in self._iter_string_values(data):
                    if self._looks_like_path(path_val):
                        yield self._occ(rel_path, 0, "config_path", path_val, ext, None)
            return

        if ext in DOC_EXTS or ext in CONFIG_EXTS:
            # Generic text search
            for ln, line in enumerate(text.splitlines(), start=1):
                for m in PATH_REGEX.finditer(line):
                    val = m.group("path")
                    if self._looks_like_path(val):
                        yield self._occ(rel_path, ln, "doc_link" if ext in DOC_EXTS else "config_path", val, ext, line)
            return

        # Fallback: no-op
        return iter(())

    def _scan_python(self, fp: Path, text: str) -> Iterator[Occurrence]:
        rel_path = str(fp.resolve().relative_to(self.root))
        try:
            tree = ast.parse(text)
        except Exception:
            return iter(())

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name
                    yield self._occ(rel_path, getattr(node, 'lineno', 0), "code_import", mod, ".py", None)
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                yield self._occ(rel_path, getattr(node, 'lineno', 0), "code_import", mod, ".py", None)

        return iter(())

    # -------- Helpers --------
    def _occ(self, file_path: str, line_no: int, kind: str, value: str, ext: str, context_line: Optional[str]) -> Occurrence:
        pattern = self._classify_pattern(value)
        return Occurrence(
            file_path=file_path,
            line_no=line_no,
            kind=kind,
            value=value.strip(),
            pattern=pattern,
            ext=ext,
            context=(context_line.strip() if context_line is not None else None),
        )

    def _classify_pattern(self, value: str) -> Optional[str]:
        low = value.replace("\\", "/").lower()
        for pat in TRACKED_PATTERNS:
            if pat.lower() in low:
                return pat
        # Derive top-level if possible, e.g., "src/..." => "src/"
        parts = [p for p in low.split('/') if p]
        if parts:
            return parts[0] + "/"
        return None

    def _looks_like_path(self, value: str) -> bool:
        v = value.strip()
        if "://" in v:  # likely URL
            return False
        # Require at least one separator and 2+ segments
        sep_count = v.count('/') + v.count('\\')
        return sep_count >= 1 and any(seg for seg in re.split(r"[\\/]", v) if seg)

    def _iter_string_values(self, obj) -> Iterator[str]:
        if obj is None:
            return
        if isinstance(obj, str):
            yield obj
        elif isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(k, str) and self._looks_like_path(k):
                    yield k
                yield from self._iter_string_values(v)
        elif isinstance(obj, (list, tuple, set)):
            for it in obj:
                yield from self._iter_string_values(it)


def scan_repository(root: Path, db_path: Path, reset: bool = False, include_hidden: bool = False) -> Tuple[int, int]:
    indexer = HardcodedPathIndexer(root, db_path)
    if reset:
        indexer.reset()
    else:
        indexer.connect()
    try:
        return indexer.scan(include_hidden=include_hidden)
    finally:
        indexer.close()


__all__ = [
    "HardcodedPathIndexer",
    "scan_repository",
    "Occurrence",
]

