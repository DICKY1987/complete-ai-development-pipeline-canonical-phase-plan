"""Decision Registry - Track all system decisions

Records and queries decisions made by the orchestration system.
Supports filtering by category, run_id, and time range.
"""

# DOC_ID: DOC-PATTERNS-DECISION-REGISTRY-001

import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class Decision:
    """Represents a decision made by the system"""

    decision_id: str
    timestamp: str
    category: str  # routing, scheduling, retry, circuit_breaker
    context: Dict[str, Any]
    options: List[str]
    selected_option: str
    rationale: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class DecisionRegistry:
    """SQLite-backed registry for system decisions"""

    def __init__(self, storage_path: str = ".state/decisions.db"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(self.storage_path))
        self.db.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        """Initialize database schema"""
        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS decisions (
                decision_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                category TEXT NOT NULL,
                context TEXT NOT NULL,  -- JSON
                options TEXT NOT NULL,  -- JSON array
                selected_option TEXT NOT NULL,
                rationale TEXT NOT NULL,
                metadata TEXT NOT NULL,  -- JSON
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create indices for common queries
        self.db.execute(
            "CREATE INDEX IF NOT EXISTS idx_category ON decisions(category)"
        )
        self.db.execute(
            "CREATE INDEX IF NOT EXISTS idx_timestamp ON decisions(timestamp)"
        )
        self.db.execute(
            "CREATE INDEX IF NOT EXISTS idx_created_at ON decisions(created_at)"
        )

        self.db.commit()

    def log_decision(self, decision: Decision) -> None:
        """
        Record a decision.

        Args:
            decision: Decision to record
        """
        import json

        self.db.execute(
            """
            INSERT INTO decisions (
                decision_id, timestamp, category, context,
                options, selected_option, rationale, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                decision.decision_id,
                decision.timestamp,
                decision.category,
                json.dumps(decision.context),
                json.dumps(decision.options),
                decision.selected_option,
                decision.rationale,
                json.dumps(decision.metadata),
            ),
        )
        self.db.commit()

    def query_decisions(
        self,
        category: Optional[str] = None,
        since: Optional[str] = None,
        run_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Decision]:
        """
        Query decision history.

        Args:
            category: Filter by decision category
            since: Filter by timestamp (ISO 8601)
            run_id: Filter by run_id (from metadata)
            limit: Maximum number of results

        Returns:
            List of matching decisions
        """
        import json

        query = "SELECT * FROM decisions WHERE 1=1"
        params: List[Any] = []

        if category:
            query += " AND category = ?"
            params.append(category)

        if since:
            query += " AND timestamp >= ?"
            params.append(since)

        if run_id:
            # Search in metadata JSON
            query += " AND json_extract(metadata, '$.run_id') = ?"
            params.append(run_id)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        rows = self.db.execute(query, params).fetchall()

        decisions = []
        for row in rows:
            decisions.append(
                Decision(
                    decision_id=row["decision_id"],
                    timestamp=row["timestamp"],
                    category=row["category"],
                    context=json.loads(row["context"]),
                    options=json.loads(row["options"]),
                    selected_option=row["selected_option"],
                    rationale=row["rationale"],
                    metadata=json.loads(row["metadata"]),
                )
            )

        return decisions

    def get_decision_stats(self) -> Dict[str, Any]:
        """
        Get decision statistics.

        Returns:
            Dictionary with decision counts by category
        """
        stats = {}

        # Total decisions
        row = self.db.execute("SELECT COUNT(*) as count FROM decisions").fetchone()
        stats["total"] = row["count"]

        # By category
        rows = self.db.execute(
            "SELECT category, COUNT(*) as count FROM decisions GROUP BY category"
        ).fetchall()
        stats["by_category"] = {row["category"]: row["count"] for row in rows}

        # Recent decisions (last 24 hours)
        now = datetime.now(timezone.utc).isoformat()
        recent_since = (
            datetime.now(timezone.utc).replace(hour=0, minute=0, second=0).isoformat()
        )
        row = self.db.execute(
            "SELECT COUNT(*) as count FROM decisions WHERE timestamp >= ?",
            (recent_since,),
        ).fetchone()
        stats["last_24h"] = row["count"]

        return stats

    def close(self):
        """Close database connection"""
        if self.db:
            self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
