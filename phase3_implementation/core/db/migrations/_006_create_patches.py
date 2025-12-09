"""
Migration 006: Create patches table.

Reference: DOC-SSOT-STATE-MACHINES-001 §6.5
"""

def up(conn):
    """Create patches table with foreign key to tasks."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS patches (
            patch_id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL,
            state TEXT NOT NULL,
            file_path TEXT,
            patch_format TEXT,
            scope TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            applied_at TEXT,
            verified_at TEXT,
            metadata TEXT,
            
            FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE CASCADE,
            CHECK (state IN ('PENDING', 'VALIDATING', 'QUARANTINED', 'STAGED', 
                           'APPLIED', 'VERIFIED', 'ROLLED_BACK', 'SUPERSEDED', 
                           'EXPIRED', 'BLOCKED')),
            CHECK (patch_format IN ('unified_diff', 'context_diff', 'git_patch', 'inline'))
        )
    """)
    
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_patches_task_id 
        ON patches(task_id)
    """)
    
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_patches_state 
        ON patches(state)
    """)
    
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_patches_file_path 
        ON patches(file_path)
    """)


def down(conn):
    """Drop patches table."""
    conn.execute("DROP TABLE IF EXISTS patches")
