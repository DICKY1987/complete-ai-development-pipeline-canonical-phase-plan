#!/usr/bin/env python
"""Database migration CLI tool."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.db import create_migration_manager, get_db


def main():
    if len(sys.argv) < 2:
        print("Usage: python manage_db.py <command>")
        print("\nCommands:")
        print("  status   - Show migration status")
        print("  migrate  - Apply pending migrations")
        print("  rollback - Rollback last migration")
        sys.exit(1)

    command = sys.argv[1].lower()
    db = get_db()
    manager = create_migration_manager(db)

    if command == "status":
        manager.status()
    elif command == "migrate":
        manager.migrate()
    elif command == "rollback":
        if len(sys.argv) > 2:
            target = int(sys.argv[2])
            manager.rollback(target)
        else:
            manager.rollback()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
