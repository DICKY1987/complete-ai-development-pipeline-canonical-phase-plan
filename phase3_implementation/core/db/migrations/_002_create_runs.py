"""
Migration 002: Create runs table.

Reference: DOC-SSOT-STATE-MACHINES-001 §6.1
"""

def up(conn):
    """Create runs table with proper schema."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            run_id TEXT PRIMARY KEY,
            state TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            completed_at TEXT,
            metadata TEXT,
            progress_percentage REAL DEFAULT 0.0,
            
            CHECK (state IN ('INITIALIZING', 'RUNNING', 'PAUSED', 'COMPLETED', 'FAILED')),
            CHECK (progress_percentage >= 0.0 AND progress_percentage <= 100.0)
        )
    """)
    
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_runs_state 
        ON runs(state)
    """)
    
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_runs_created_at 
        ON runs(created_at DESC)
    """)


def down(conn):
    """Drop runs table."""
    conn.execute("DROP TABLE IF EXISTS runs")
