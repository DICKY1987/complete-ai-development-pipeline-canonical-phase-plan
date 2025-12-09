"""
Migration registry.

Registers all database migrations in order.
"""

from . import _001_create_state_transitions as migration_001


def register_migrations(manager):
    """
    Register all migrations with the manager.
    
    Args:
        manager: MigrationManager instance
    """
    # Migration 001: State transitions audit table
    manager.register(
        version=1,
        name="create_state_transitions",
        upgrade=migration_001.upgrade,
        downgrade=migration_001.downgrade
    )
    
    # Future migrations will be registered here
    # manager.register(version=2, ...)
