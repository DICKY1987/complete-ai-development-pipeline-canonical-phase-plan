"""
Migration 005: Create workers table.

Reference: DOC-SSOT-STATE-MACHINES-001 §6.4
"""

def up(conn):
    """Create workers table."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS workers (
            worker_id TEXT PRIMARY KEY,
            state TEXT NOT NULL,
            last_heartbeat TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            metadata TEXT,
            
            CHECK (state IN ('IDLE', 'BUSY', 'UNHEALTHY', 'DEAD', 'STOPPED'))
        )
    """)
    
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_workers_state 
        ON workers(state)
    """)
    
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_workers_last_heartbeat 
        ON workers(last_heartbeat DESC)
    """)


def down(conn):
    """Drop workers table."""
    conn.execute("DROP TABLE IF EXISTS workers")
