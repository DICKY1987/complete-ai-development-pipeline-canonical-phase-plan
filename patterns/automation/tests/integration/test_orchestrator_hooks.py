#!/usr/bin/env python3
"""Integration tests for orchestrator hooks."""
# DOC_ID: DOC-PAT-TESTS-ORCHESTRATOR-HOOKS-003

import json
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path

import pytest


class TestOrchestratorHooks:
    """Test pattern automation orchestrator hooks."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        db = sqlite3.connect(db_path)
        db.executescript(
            """
            CREATE TABLE execution_logs (
                id INTEGER PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                operation_kind TEXT,
                file_types TEXT,
                tools_used TEXT,
                input_signature TEXT,
                output_signature TEXT,
                success BOOLEAN,
                time_taken_seconds REAL,
                context TEXT
            );

            CREATE TABLE pattern_candidates (
                id INTEGER PRIMARY KEY,
                pattern_id TEXT UNIQUE,
                signature TEXT,
                confidence REAL
            );
        """
        )
        db.commit()
        db.close()

        yield db_path

        Path(db_path).unlink(missing_ok=True)

    @pytest.fixture
    def hooks(self, temp_db):
        """Create hooks instance with temp database."""
        import sys

        patterns_dir = Path(__file__).resolve().parents[3]
        sys.path.insert(0, str(patterns_dir))

        from automation.integration.orchestrator_hooks import PatternAutomationHooks

        return PatternAutomationHooks(db_path=temp_db, enabled=True)

    def test_hooks_initialization(self, hooks, temp_db):
        """Test hooks initialize correctly."""
        assert hooks.db_path == temp_db
        assert hooks.enabled is True

    def test_task_complete_success(self, hooks, temp_db):
        """Test on_task_complete logs successful execution."""
        task_spec = {
            "operation_kind": "file_creation",
            "name": "create_test",
            "inputs": {"filename": "test.txt"},
        }

        result = {"success": True, "outputs": {"file_created": "test.txt"}}

        context = hooks.on_task_start(task_spec)
        hooks.on_task_complete(task_spec, result, context)

        db = sqlite3.connect(temp_db)
        cursor = db.cursor()

        count = cursor.execute("SELECT COUNT(*) FROM execution_logs").fetchone()[0]
        assert count == 1

        row = cursor.execute(
            "SELECT operation_kind, success FROM execution_logs"
        ).fetchone()
        assert row[0] == "file_creation"
        assert row[1] == 1

        db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
