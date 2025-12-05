"""Create a test run to demonstrate monitoring automation.

This script creates a simulated run in the database to test:
- Monitoring daemon detection
- Completion detection
- Auto-archival
- Auto-reporting
- Alerting
"""
# DOC_ID: DOC-SCRIPTS-TEST-RUN-CREATOR-013

import sys
import time
from pathlib import Path
from datetime import datetime, UTC

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.state.db import Database


def create_test_run():
    """Create a test run with simulated steps."""
    db_path = ".state/orchestration.db"
    db = Database(db_path)
    db.connect()
    
    # Create test run
    run_id = f"TEST-RUN-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}"
    
    cursor = db.conn.cursor()
    
    # Create runs table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            run_id TEXT PRIMARY KEY,
            project_id TEXT,
            phase_id TEXT,
            workstream_id TEXT,
            state TEXT,
            created_at TEXT,
            started_at TEXT,
            ended_at TEXT,
            metadata TEXT
        )
    """)
    
    # Create step_attempts table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS step_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT,
            step_id TEXT,
            state TEXT,
            created_at TEXT,
            FOREIGN KEY (run_id) REFERENCES runs(run_id)
        )
    """)
    
    # Create run_events table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS run_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT,
            event_type TEXT,
            severity TEXT,
            timestamp TEXT,
            data TEXT,
            FOREIGN KEY (run_id) REFERENCES runs(run_id)
        )
    """)
    
    # Insert test run
    now = datetime.now(UTC).isoformat() + "Z"
    cursor.execute("""
        INSERT INTO runs (run_id, project_id, phase_id, workstream_id, state, created_at, started_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (run_id, "test-project", "phase7", "test-workstream", "running", now, now))
    
    # Insert test steps
    for i in range(1, 6):
        cursor.execute("""
            INSERT INTO step_attempts (run_id, step_id, state, created_at)
            VALUES (?, ?, ?, ?)
        """, (run_id, f"step-{i}", "pending", now))
    
    db.conn.commit()
    
    print(f"✅ Created test run: {run_id}")
    print(f"   Database: {db_path}")
    print(f"   Steps: 5 (pending)")
    print(f"   State: running")
    print()
    print("Monitoring daemon should detect this run within 10 seconds...")
    print()
    print("To complete the run (trigger automation):")
    print(f"  python scripts/complete_test_run.py {run_id}")
    
    return run_id


if __name__ == "__main__":
    create_test_run()
