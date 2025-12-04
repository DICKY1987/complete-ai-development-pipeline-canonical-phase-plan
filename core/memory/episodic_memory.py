"""Episodic memory storage and retrieval for autonomous agents (WS-04-03B)."""

from __future__ import annotations

import hashlib
import json
import math
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence

SchemaLoader = Callable[[], str]
Embedder = Callable[[str], List[float]]


def _normalize_vector(vector: Sequence[float]) -> List[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return [0.0 for _ in vector]
    return [value / norm for value in vector]


def _default_embedder(text: str, dimensions: int = 12) -> List[float]:
    """Deterministic bag-of-words style embedding to avoid external deps."""
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    vector = [0.0] * dimensions
    if not tokens:
        return vector

    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = digest[0] % dimensions
        vector[index] += 1.0

    return _normalize_vector(vector)


def _cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    if len(a) != len(b):
        return 0.0
    numerator = sum(x * y for x, y in zip(a, b))
    denom_a = math.sqrt(sum(x * x for x in a))
    denom_b = math.sqrt(sum(y * y for y in b))
    if denom_a == 0 or denom_b == 0:
        return 0.0
    return numerator / (denom_a * denom_b)


@dataclass
class Episode:
    id: int
    task_id: str
    task_description: str
    user_prompt: str
    files_changed: List[str]
    edit_accepted: bool
    project_conventions: List[str]
    embedding: List[float]
    metadata: Dict[str, object]
    created_at: datetime


class EpisodicMemory:
    """SQLite-backed episodic memory with lightweight semantic recall."""

    def __init__(
        self,
        db_path: str = ".worktrees/episodic_memory.db",
        schema_loader: Optional[SchemaLoader] = None,
        embedder: Optional[Embedder] = None,
    ):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._schema_loader = schema_loader
        self._embedder = embedder or _default_embedder
        self._conn: Optional[sqlite3.Connection] = None

    # Connection and schema helpers
    def connect(self) -> None:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
            self._ensure_schema()

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    def _ensure_schema(self) -> None:
        cursor = self._conn.cursor()
        schema_sql = self._load_schema_sql()
        cursor.executescript(schema_sql)
        self._conn.commit()

    def _load_schema_sql(self) -> str:
        if self._schema_loader:
            return self._schema_loader()

        schema_path = Path("schema/episodic_memory_schema.sql")
        if schema_path.exists():
            return schema_path.read_text(encoding="utf-8")

        # Inline fallback to keep module self-contained.
        return """
        CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL UNIQUE,
            task_description TEXT NOT NULL,
            user_prompt TEXT NOT NULL,
            files_changed TEXT NOT NULL,
            edit_accepted INTEGER NOT NULL,
            project_conventions TEXT NOT NULL,
            embedding TEXT NOT NULL,
            metadata TEXT,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_episodes_created_at ON episodes(created_at);
        """

    # Public API
    def record_episode(
        self,
        task_id: str,
        task_description: str,
        user_prompt: str,
        files_changed: Iterable[str],
        edit_accepted: bool,
        project_conventions: Iterable[str],
        metadata: Optional[Dict[str, object]] = None,
    ) -> int:
        """Persist a new episode with deterministic embedding."""
        self.connect()
        embedding = self._embedder(task_description)
        now = datetime.now(timezone.utc).isoformat()

        cursor = self._conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO episodes (
                task_id, task_description, user_prompt, files_changed,
                edit_accepted, project_conventions, embedding, metadata, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task_id,
                task_description,
                user_prompt,
                json.dumps(list(files_changed)),
                1 if edit_accepted else 0,
                json.dumps(list(project_conventions)),
                json.dumps(embedding),
                json.dumps(metadata or {}),
                now,
            ),
        )
        self._conn.commit()
        return cursor.lastrowid

    def get_episode(self, task_id: str) -> Optional[Episode]:
        self.connect()
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM episodes WHERE task_id = ?", (task_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_episode(row)

    def list_episodes(self, limit: int = 200) -> List[Episode]:
        self.connect()
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT * FROM episodes ORDER BY datetime(created_at) DESC LIMIT ?",
            (limit,),
        )
        rows = cursor.fetchall()
        return [self._row_to_episode(row) for row in rows]

    def recall_similar_tasks(
        self, task_description: str, top_k: int = 5, min_score: float = 0.0
    ) -> List[Dict[str, object]]:
        """Return similar episodes sorted by cosine similarity."""
        self.connect()
        query_vec = self._embedder(task_description)
        episodes = self.list_episodes(limit=500)

        scored = []
        for episode in episodes:
            score = _cosine_similarity(query_vec, episode.embedding)
            if score >= min_score:
                scored.append({"episode": episode, "score": score})

        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored[:top_k]

    def _row_to_episode(self, row: sqlite3.Row) -> Episode:
        return Episode(
            id=row["id"],
            task_id=row["task_id"],
            task_description=row["task_description"],
            user_prompt=row["user_prompt"],
            files_changed=json.loads(row["files_changed"]),
            edit_accepted=bool(row["edit_accepted"]),
            project_conventions=json.loads(row["project_conventions"]),
            embedding=json.loads(row["embedding"]),
            metadata=json.loads(row["metadata"] or "{}"),
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def __enter__(self) -> "EpisodicMemory":
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
