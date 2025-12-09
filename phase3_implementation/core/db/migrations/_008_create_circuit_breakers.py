"""
Migration 008: Create circuit_breakers table.

Reference: DOC-SSOT-STATE-MACHINES-001 §6.8
"""

def up(conn):
    """Create circuit_breakers table."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS circuit_breakers (
            breaker_id TEXT PRIMARY KEY,
            tool_name TEXT NOT NULL UNIQUE,
            state TEXT NOT NULL,
            failure_count INTEGER DEFAULT 0,
            failure_threshold INTEGER DEFAULT 5,
            last_failure_at TEXT,
            cooldown_seconds INTEGER DEFAULT 60,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            metadata TEXT,
            
            CHECK (state IN ('CLOSED', 'OPEN', 'HALF_OPEN')),
            CHECK (failure_count >= 0),
            CHECK (failure_threshold > 0),
            CHECK (cooldown_seconds > 0)
        )
    """)
    
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_circuit_breakers_tool_name 
        ON circuit_breakers(tool_name)
    """)
    
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_circuit_breakers_state 
        ON circuit_breakers(state)
    """)


def down(conn):
    """Drop circuit_breakers table."""
    conn.execute("DROP TABLE IF EXISTS circuit_breakers")
