#!/usr/bin/env python3
"""Initialize the pipeline database.

Usage:
  python scripts/init_db.py [--db PATH] [--schema PATH]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.core_state import m010003_db as pipeline_db


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Initialize pipeline database")
    parser.add_argument("--db", dest="db_path", help="Path to DB file")
    parser.add_argument(
        "--schema", dest="schema_path", help="Path to schema.sql (optional)"
    )
    args = parser.parse_args(argv)

    pipeline_db.init_db(db_path=args.db_path, schema_path=args.schema_path)
    dbp = Path(args.db_path) if args.db_path else None
    if not dbp:
        # Resolve default to show user the actual path
        from modules.core_state.m010003_db import _resolve_db_path  # type: ignore

        dbp = _resolve_db_path(None)
    print(f"Initialized database at: {dbp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
