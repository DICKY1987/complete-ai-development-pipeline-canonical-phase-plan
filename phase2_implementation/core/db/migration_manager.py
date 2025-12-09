"""
Database migration system.

Implements versioned database migrations for schema changes.
Tracks applied migrations and supports rollback.

Reference: DOC-SSOT-STATE-MACHINES-001 §6
"""

from typing import List, Callable
from datetime import datetime, timezone

from .connection import DatabaseConnection


class Migration:
    """
    Single database migration.

    Contains upgrade and downgrade functions for schema changes.
    """

    def __init__(
        self, version: int, name: str, upgrade_func: Callable, downgrade_func: Callable
    ):
        """
        Initialize migration.

        Args:
            version: Migration version number
            name: Migration name/description
            upgrade_func: Function to apply migration
            downgrade_func: Function to rollback migration
        """
        self.version = version
        self.name = name
        self.upgrade = upgrade_func
        self.downgrade = downgrade_func

    def __repr__(self):
        return f"Migration(v{self.version}: {self.name})"


class MigrationManager:
    """
    Database migration manager.

    Tracks and applies versioned schema migrations.
    """

    def __init__(self, db: DatabaseConnection):
        """
        Initialize migration manager.

        Args:
            db: Database connection
        """
        self.db = db
        self.migrations: List[Migration] = []
        self._ensure_migrations_table()

    def _ensure_migrations_table(self):
        """Create migrations tracking table if not exists."""
        self.db.execute_script(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                applied_at TEXT NOT NULL,
                checksum TEXT
            );
        """
        )

    def register(self, version: int, name: str, upgrade: Callable, downgrade: Callable):
        """
        Register a migration.

        Args:
            version: Migration version number
            name: Migration name
            upgrade: Upgrade function
            downgrade: Downgrade function
        """
        migration = Migration(version, name, upgrade, downgrade)
        self.migrations.append(migration)
        self.migrations.sort(key=lambda m: m.version)

    def get_current_version(self) -> int:
        """
        Get current database schema version.

        Returns:
            Current version number (0 if no migrations applied)
        """
        result = self.db.fetchone(
            "SELECT MAX(version) as version FROM schema_migrations"
        )
        return result["version"] if result["version"] is not None else 0

    def get_pending_migrations(self) -> List[Migration]:
        """
        Get migrations not yet applied.

        Returns:
            List of pending migrations
        """
        current_version = self.get_current_version()
        return [m for m in self.migrations if m.version > current_version]

    def migrate(self, target_version: int = None):
        """
        Apply pending migrations up to target version.

        Args:
            target_version: Target version (None = latest)
        """
        pending = self.get_pending_migrations()

        if target_version is not None:
            pending = [m for m in pending if m.version <= target_version]

        if not pending:
            print("No pending migrations.")
            return

        print(f"Applying {len(pending)} migration(s)...")

        for migration in pending:
            print(f"  → {migration}")

            with self.db.transaction() as conn:
                # Apply migration
                migration.upgrade(conn)

                # Record in migrations table
                conn.execute(
                    """INSERT INTO schema_migrations (version, name, applied_at)
                       VALUES (?, ?, ?)""",
                    (
                        migration.version,
                        migration.name,
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )

            print(f"    ✓ Applied v{migration.version}")

        print(f"Migration complete. Current version: {self.get_current_version()}")

    def rollback(self, target_version: int = None):
        """
        Rollback migrations to target version.

        Args:
            target_version: Target version to rollback to (None = rollback one)
        """
        current_version = self.get_current_version()

        if target_version is None:
            target_version = current_version - 1

        if target_version >= current_version:
            print("Nothing to rollback.")
            return

        # Get migrations to rollback (in reverse order)
        to_rollback = [
            m
            for m in reversed(self.migrations)
            if target_version < m.version <= current_version
        ]

        print(f"Rolling back {len(to_rollback)} migration(s)...")

        for migration in to_rollback:
            print(f"  ← {migration}")

            with self.db.transaction() as conn:
                # Rollback migration
                migration.downgrade(conn)

                # Remove from migrations table
                conn.execute(
                    "DELETE FROM schema_migrations WHERE version = ?",
                    (migration.version,),
                )

            print(f"    ✓ Rolled back v{migration.version}")

        print(f"Rollback complete. Current version: {self.get_current_version()}")

    def status(self):
        """Print migration status."""
        current_version = self.get_current_version()
        pending = self.get_pending_migrations()

        print(f"Current schema version: {current_version}")
        print(
            f"Latest available version: {max([m.version for m in self.migrations], default=0)}"
        )
        print(f"Pending migrations: {len(pending)}")

        if pending:
            print("\nPending:")
            for m in pending:
                print(f"  - v{m.version}: {m.name}")

        # Show applied migrations
        applied = self.db.fetchall(
            "SELECT * FROM schema_migrations ORDER BY version DESC LIMIT 5"
        )

        if applied:
            print("\nRecent migrations:")
            for row in applied:
                print(
                    f"  ✓ v{row['version']}: {row['name']} ({row['applied_at'][:10]})"
                )


def create_migration_manager(db: DatabaseConnection = None) -> MigrationManager:
    """
    Create migration manager with registered migrations.

    Args:
        db: Database connection (uses global if None)

    Returns:
        Configured migration manager
    """
    if db is None:
        from .connection import get_db

        db = get_db()

    manager = MigrationManager(db)

    # Import and register all migrations
    from .migrations import register_migrations

    register_migrations(manager)

    return manager
