"""Tests for run monitor - WS-03-03B"""

import sys
from pathlib import Path

import pytest

# Add framework root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.engine.monitoring import RunMonitor


class TestRunMonitor:
    """Test RunMonitor functionality"""

    # DOC_ID: DOC-TEST-MONITORING-TEST-RUN-MONITOR-182

    def test_create_monitor(self):
        """Test creating a run monitor"""
        monitor = RunMonitor(":memory:")

        assert monitor.db is not None

    def test_get_summary_empty(self):
        """Test getting summary with no runs"""
        monitor = RunMonitor(":memory:")

        summary = monitor.get_summary()

        assert summary["total_runs"] == 0
        assert summary["active_runs"] == 0

    def test_list_active_runs_empty(self):
        """Test listing active runs when none exist"""
        monitor = RunMonitor(":memory:")

        active = monitor.list_active_runs()

        assert active == []

    def test_get_metrics_for_run(self, tmp_path):
        """Test getting metrics for a specific run"""
        from datetime import datetime

        db_path = tmp_path / "test.db"
        monitor = RunMonitor(str(db_path))

        # Create a run with simple test ID
        run_id = "01234567890123456789012345"
        monitor.db.create_run(
            {
                "run_id": run_id,
                "project_id": "test-project",
                "phase_id": "PH-01",
                "workstream_id": "WS-01",
                "created_at": datetime.utcnow().isoformat() + "Z",
                "state": "running",
            }
        )

        # Get metrics
        metrics = monitor.get_run_metrics(run_id)

        assert metrics is not None
        assert metrics.run_id == run_id
        assert metrics.status == "running"
        assert metrics.total_steps == 0

    def test_metrics_to_dict(self, tmp_path):
        """Test converting metrics to dict"""
        from datetime import datetime

        db_path = tmp_path / "test.db"
        monitor = RunMonitor(str(db_path))

        run_id = "01234567890123456789012346"
        monitor.db.create_run(
            {
                "run_id": run_id,
                "project_id": "test-project",
                "phase_id": "PH-01",
                "created_at": datetime.utcnow().isoformat() + "Z",
            }
        )

        metrics = monitor.get_run_metrics(run_id)
        d = metrics.to_dict()

        assert d["run_id"] == run_id
        assert d["status"] == "pending"
        assert "created_at" in d
