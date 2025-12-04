"""
SQLite-backed knowledge graph storage.

Stores nodes (modules, classes, functions) and relationships (imports, calls, inheritance).
"""

# DOC_ID: DOC-CORE-KNOWLEDGE-GRAPH-403

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from .relationships import RelationshipType


@dataclass
class NodeRecord:
    """Represents a graph node."""

    name: str
    type: str
    file: Optional[str] = None
    line: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class EdgeRecord:
    """Represents a graph edge."""

    source_id: int
    target_id: int
    type: str
    weight: float = 1.0
    frequency: int = 1
    metadata: Optional[Dict[str, Any]] = None


class KnowledgeGraph:
    """Knowledge graph backed by SQLite."""

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        if self.db_path.parent and not self.db_path.parent.exists():
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._ensure_schema()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.commit()
            self.conn.close()
            self.conn = None

    def _ensure_schema(self):
        """Create tables and indexes if they do not exist."""
        cur = self.conn.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                file TEXT,
                line INTEGER,
                metadata TEXT,
                UNIQUE(name, type)
            );

            CREATE TABLE IF NOT EXISTS edges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id INTEGER NOT NULL,
                target_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                weight REAL DEFAULT 1.0,
                frequency INTEGER DEFAULT 1,
                metadata TEXT,
                FOREIGN KEY (source_id) REFERENCES nodes(id),
                FOREIGN KEY (target_id) REFERENCES nodes(id)
            );

            CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(type);
            CREATE INDEX IF NOT EXISTS idx_edges_type ON edges(type);
            CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_id);
            CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_id);
            """
        )
        self.conn.commit()

    def _serialize_metadata(self, metadata: Optional[Dict[str, Any]]) -> Optional[str]:
        return json.dumps(metadata) if metadata else None

    def add_node(self, node: NodeRecord) -> int:
        """Insert or fetch a node and return its id."""
        cur = self.conn.cursor()
        metadata_json = self._serialize_metadata(node.metadata)
        cur.execute(
            """
            INSERT INTO nodes (name, type, file, line, metadata)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(name, type) DO UPDATE SET
                file=excluded.file,
                line=excluded.line,
                metadata=COALESCE(excluded.metadata, nodes.metadata)
            """,
            (node.name, node.type, node.file, node.line, metadata_json),
        )
        self.conn.commit()
        node_id = cur.execute(
            "SELECT id FROM nodes WHERE name=? AND type=?", (node.name, node.type)
        ).fetchone()["id"]
        return node_id

    def add_edge(self, edge: EdgeRecord) -> int:
        """Insert an edge and return its id."""
        if not RelationshipType.has_value(edge.type):
            raise ValueError(f"Unsupported relationship type: {edge.type}")

        cur = self.conn.cursor()
        metadata_json = self._serialize_metadata(edge.metadata)
        cur.execute(
            """
            INSERT INTO edges (source_id, target_id, type, weight, frequency, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                edge.source_id,
                edge.target_id,
                edge.type,
                edge.weight,
                edge.frequency,
                metadata_json,
            ),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_node(self, name: str, type: Optional[str] = None) -> Optional[sqlite3.Row]:
        """Fetch a node by name (and optional type)."""
        cur = self.conn.cursor()
        if type:
            row = cur.execute(
                "SELECT * FROM nodes WHERE name=? AND type=?", (name, type)
            ).fetchone()
        else:
            row = cur.execute("SELECT * FROM nodes WHERE name=?", (name,)).fetchone()
        return row

    def get_nodes(self, type: Optional[str] = None) -> List[sqlite3.Row]:
        """Return all nodes, optionally filtered by type."""
        cur = self.conn.cursor()
        if type:
            return cur.execute(
                "SELECT * FROM nodes WHERE type=? ORDER BY name", (type,)
            ).fetchall()
        return cur.execute("SELECT * FROM nodes ORDER BY name").fetchall()

    def get_edges(self, type: Optional[str] = None) -> List[sqlite3.Row]:
        """Return all edges, optionally filtered by type."""
        cur = self.conn.cursor()
        if type:
            return cur.execute(
                "SELECT * FROM edges WHERE type=? ORDER BY id", (type,)
            ).fetchall()
        return cur.execute("SELECT * FROM edges ORDER BY id").fetchall()

    def delete_all(self):
        """Clear all nodes and edges."""
        cur = self.conn.cursor()
        cur.execute("DELETE FROM edges")
        cur.execute("DELETE FROM nodes")
        self.conn.commit()


__all__ = ["KnowledgeGraph", "NodeRecord", "EdgeRecord"]
