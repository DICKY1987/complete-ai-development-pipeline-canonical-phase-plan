"""
Database migration: Create state_transitions audit table.

Implements the state transitions audit table per SSOT §6.7.
This table records all state transitions for audit trail.

Reference: DOC-SSOT-STATE-MACHINES-001 §6.7
"""


def upgrade(conn):
    """
    Create state_transitions audit table.

    Per SSOT §6.7, this table records all state transitions
    for any entity type in the system.
    """
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS state_transitions (
            transition_id INTEGER PRIMARY KEY AUTOINCREMENT,

            -- Entity identification
            entity_type TEXT NOT NULL CHECK(entity_type IN (
                'run', 'workstream', 'task', 'worker',
                'patch_ledger', 'test_gate', 'circuit_breaker'
            )),
            entity_id TEXT NOT NULL,

            -- State transition
            from_state TEXT NOT NULL,
            to_state TEXT NOT NULL,

            -- Metadata
            trigger TEXT,
            reason TEXT,
            metadata TEXT,  -- JSON

            -- Operator (NULL for automatic, username for manual)
            operator TEXT,

            -- Timestamp
            transitioned_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

            -- Indexes for common queries
            CHECK (transitioned_at IS NOT NULL)
        );

        -- Index for entity queries
        CREATE INDEX IF NOT EXISTS idx_transitions_entity
        ON state_transitions(entity_type, entity_id);

        -- Index for time-based queries
        CREATE INDEX IF NOT EXISTS idx_transitions_time
        ON state_transitions(transitioned_at);

        -- Index for operator queries (manual overrides)
        CREATE INDEX IF NOT EXISTS idx_transitions_operator
        ON state_transitions(operator)
        WHERE operator IS NOT NULL;
    """
    )


def downgrade(conn):
    """Drop state_transitions table."""
    conn.executescript(
        """
        DROP INDEX IF EXISTS idx_transitions_operator;
        DROP INDEX IF EXISTS idx_transitions_time;
        DROP INDEX IF EXISTS idx_transitions_entity;
        DROP TABLE IF EXISTS state_transitions;
    """
    )
