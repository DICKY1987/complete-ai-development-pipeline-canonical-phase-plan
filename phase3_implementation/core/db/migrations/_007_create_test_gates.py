"""
Migration 007: Create test_gates table.

Reference: DOC-SSOT-STATE-MACHINES-001 §6.6
"""

def up(conn):
    """Create test_gates table with foreign key to tasks."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS test_gates (
            gate_id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL,
            state TEXT NOT NULL,
            test_suite TEXT,
            timeout_seconds INTEGER DEFAULT 600,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            started_at TEXT,
            completed_at TEXT,
            test_results TEXT,
            metadata TEXT,
            
            FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE CASCADE,
            CHECK (state IN ('PENDING', 'RUNNING', 'PASSED', 'FAILED', 'BLOCKED')),
            CHECK (timeout_seconds > 0)
        )
    """)
    
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_test_gates_task_id 
        ON test_gates(task_id)
    """)
    
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_test_gates_state 
        ON test_gates(state)
    """)


def down(conn):
    """Drop test_gates table."""
    conn.execute("DROP TABLE IF EXISTS test_gates")
