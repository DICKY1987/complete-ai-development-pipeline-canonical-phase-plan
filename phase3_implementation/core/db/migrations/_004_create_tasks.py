"""
Migration 004: Create tasks table.

Reference: DOC-SSOT-STATE-MACHINES-001 §6.3
"""

def up(conn):
    """Create tasks table with foreign keys."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            workstream_id TEXT NOT NULL,
            state TEXT NOT NULL,
            worker_id TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            queued_at TEXT,
            started_at TEXT,
            completed_at TEXT,
            retry_count INTEGER DEFAULT 0,
            max_retries INTEGER DEFAULT 3,
            metadata TEXT,
            
            FOREIGN KEY (workstream_id) REFERENCES workstreams(workstream_id) ON DELETE CASCADE,
            FOREIGN KEY (worker_id) REFERENCES workers(worker_id) ON DELETE SET NULL,
            CHECK (state IN ('PENDING', 'QUEUED', 'VALIDATING', 'RUNNING', 
                           'COMPLETED', 'FAILED', 'BLOCKED', 'CANCELLED', 'RETRYING')),
            CHECK (retry_count >= 0),
            CHECK (max_retries >= 0)
        )
    """)
    
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_workstream_id 
        ON tasks(workstream_id)
    """)
    
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_worker_id 
        ON tasks(worker_id)
    """)
    
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_state 
        ON tasks(state)
    """)
    
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_created_at 
        ON tasks(created_at DESC)
    """)


def down(conn):
    """Drop tasks table."""
    conn.execute("DROP TABLE IF EXISTS tasks")
