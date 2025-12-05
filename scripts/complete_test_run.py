"""Complete a test run to trigger automation.

This script marks all steps as succeeded to trigger:
- Completion detection
- Auto-archival
- Auto-reporting
- Success alerts
"""
# DOC_ID: DOC-SCRIPTS-COMPLETE-TEST-RUN-014

import sys
from pathlib import Path
from datetime import datetime, UTC

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.state.db import Database


def complete_test_run(run_id: str):
    """Mark all steps as succeeded to trigger completion."""
    db_path = ".state/orchestration.db"
    db = Database(db_path)
    db.connect()
    
    cursor = db.conn.cursor()
    
    # Update all steps to succeeded
    cursor.execute("""
        UPDATE step_attempts
        SET state = 'succeeded'
        WHERE run_id = ? AND state = 'pending'
    """, (run_id,))
    
    steps_updated = cursor.rowcount
    db.conn.commit()
    
    print(f"✅ Completed test run: {run_id}")
    print(f"   Steps updated: {steps_updated}")
    print()
    print("Monitoring daemon should detect completion within 10 seconds...")
    print("Watch for:")
    print("  - Completion detection")
    print("  - Archival attempt (will skip if no artifacts)")
    print("  - Report generation")
    print("  - Success alert (console)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/complete_test_run.py <run_id>")
        sys.exit(1)
    
    run_id = sys.argv[1]
    complete_test_run(run_id)
