"""Pattern telemetry database extensions.

Adds methods to core/state/db.py for logging pattern executions and metrics.
"""
# DOC_ID: DOC-CORE-STATE-PATTERN-TELEMETRY-DB-173

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class PatternTelemetryDB:
    """Pattern telemetry database operations."""

    def __init__(self, db_connection):
        self.db = db_connection

    def log_execution(
        self,
        operation_kind: str,
        pattern_id: Optional[str],
        file_types: List[str],
        tools_used: List[str],
        input_signature: str,
        output_signature: str,
        success: bool,
        time_taken_seconds: int,
        context: Optional[Dict] = None
    ) -> int:
        """Log a pattern execution."""
        cursor = self.db.execute(
            """
            INSERT INTO execution_logs
            (operation_kind, pattern_id, file_types, tools_used,
             input_signature, output_signature, success, time_taken_seconds, context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                operation_kind,
                pattern_id,
                json.dumps(file_types),
                json.dumps(tools_used),
                input_signature,
                output_signature,
                success,
                time_taken_seconds,
                json.dumps(context or {})
            )
        )
        self.db.commit()

        # Update pattern metrics
        if pattern_id:
            self._update_pattern_metrics(pattern_id, success, time_taken_seconds)

        return cursor.lastrowid

    def _update_pattern_metrics(self, pattern_id: str, success: bool, time_seconds: int):
        """Update aggregate pattern metrics."""
        # Get current metrics
        row = self.db.execute(
            "SELECT total_uses, success_count, failure_count, avg_execution_seconds FROM pattern_metrics WHERE pattern_id = ?",
            (pattern_id,)
        ).fetchone()

        if row:
            total_uses = row[0] + 1
            success_count = row[1] + (1 if success else 0)
            failure_count = row[2] + (0 if success else 1)
            avg_exec = (row[3] * row[0] + time_seconds) / total_uses

            self.db.execute(
                """
                UPDATE pattern_metrics
                SET total_uses = ?, success_count = ?, failure_count = ?,
                    avg_execution_seconds = ?, last_used = ?, updated_at = ?
                WHERE pattern_id = ?
                """,
                (total_uses, success_count, failure_count, avg_exec,
                 datetime.now(), datetime.now(), pattern_id)
            )
        else:
            # First use
            self.db.execute(
                """
                INSERT INTO pattern_metrics
                (pattern_id, version, total_uses, success_count, failure_count, avg_execution_seconds, last_used)
                VALUES (?, '1.0.0', 1, ?, ?, ?, ?)
                """,
                (pattern_id, 1 if success else 0, 0 if success else 1, time_seconds, datetime.now())
            )

        self.db.commit()

    def get_pattern_metrics(self, pattern_id: str) -> Optional[Dict]:
        """Get metrics for a pattern."""
        row = self.db.execute(
            "SELECT * FROM pattern_metrics WHERE pattern_id = ?",
            (pattern_id,)
        ).fetchone()

        if not row:
            return None

        return {
            'pattern_id': row[0],
            'version': row[1],
            'total_uses': row[2],
            'success_count': row[3],
            'failure_count': row[4],
            'total_time_saved_minutes': row[5],
            'avg_execution_seconds': row[6],
            'last_used': row[7],
            'confidence_score': row[8]
        }

    def get_recent_executions(self, pattern_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get recent executions, optionally filtered by pattern."""
        if pattern_id:
            rows = self.db.execute(
                "SELECT * FROM execution_logs WHERE pattern_id = ? ORDER BY timestamp DESC LIMIT ?",
                (pattern_id, limit)
            ).fetchall()
        else:
            rows = self.db.execute(
                "SELECT * FROM execution_logs ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            ).fetchall()

        return [
            {
                'id': row[0],
                'timestamp': row[1],
                'operation_kind': row[2],
                'pattern_id': row[3],
                'file_types': json.loads(row[4]) if row[4] else [],
                'tools_used': json.loads(row[5]) if row[5] else [],
                'input_signature': row[6],
                'output_signature': row[7],
                'success': bool(row[8]),
                'time_taken_seconds': row[9],
                'context': json.loads(row[11]) if row[11] else {}
            }
            for row in rows
        ]

    def record_pattern_candidate(
        self,
        signature: str,
        example_executions: List[int],
        confidence: float,
        auto_generated_spec: str
    ) -> int:
        """Record an auto-detected pattern candidate."""
        cursor = self.db.execute(
            """
            INSERT INTO pattern_candidates
            (signature, example_executions, confidence, auto_generated_spec)
            VALUES (?, ?, ?, ?)
            """,
            (signature, json.dumps(example_executions), confidence, auto_generated_spec)
        )
        self.db.commit()
        return cursor.lastrowid

    def record_anti_pattern(
        self,
        anti_pattern_id: str,
        name: str,
        description: str,
        affected_patterns: List[str],
        failure_signature: str,
        recommendation: str
    ):
        """Record an anti-pattern."""
        self.db.execute(
            """
            INSERT OR REPLACE INTO anti_patterns
            (id, name, description, affected_patterns, failure_signature, recommendation)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (anti_pattern_id, name, description, json.dumps(affected_patterns), failure_signature, recommendation)
        )
        self.db.commit()

    def record_error_pattern(
        self,
        error_type: str,
        error_signature: str,
        file_types: List[str],
        resolution_steps: List[str],
        success: bool
    ):
        """Record an error resolution for learning."""
        # Check if pattern exists
        row = self.db.execute(
            "SELECT id, occurrences, successful_resolutions, failed_resolutions FROM error_patterns WHERE error_signature = ?",
            (error_signature,)
        ).fetchone()

        if row:
            occurrences = row[1] + 1
            successful = row[2] + (1 if success else 0)
            failed = row[3] + (0 if success else 1)
            success_rate = successful / occurrences
            auto_apply = success_rate >= 0.9

            self.db.execute(
                """
                UPDATE error_patterns
                SET occurrences = ?, successful_resolutions = ?, failed_resolutions = ?,
                    success_rate = ?, auto_apply = ?, updated_at = ?
                WHERE id = ?
                """,
                (occurrences, successful, failed, success_rate, auto_apply, datetime.now(), row[0])
            )
        else:
            self.db.execute(
                """
                INSERT INTO error_patterns
                (error_type, error_signature, file_types, resolution_steps,
                 successful_resolutions, failed_resolutions, success_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    error_type, error_signature, json.dumps(file_types),
                    json.dumps(resolution_steps),
                    1 if success else 0,
                    0 if success else 1,
                    1.0 if success else 0.0
                )
            )

        self.db.commit()
