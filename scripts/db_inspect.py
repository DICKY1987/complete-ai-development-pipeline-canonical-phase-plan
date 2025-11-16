#!/usr/bin/env python3
"""Inspect basic database information.

Prints the list of tables and counts for quick verification.

Usage:
  python scripts/db_inspect.py [--db PATH]
"""

from __future__ import annotations

import argparse
import sqlite3
from typing import Iterable

from src.pipeline import db as pipeline_db


def iter_tables(conn: sqlite3.Connection) -> Iterable[str]:
    cur = conn.cursor()
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    )
    for (name,) in cur.fetchall():
        yield name
    cur.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect pipeline DB")
    parser.add_argument("--db", dest="db_path", help="Path to DB file")
    args = parser.parse_args(argv)

    conn = pipeline_db.get_connection(db_path=args.db_path)
    try:
        print("Tables:")
        for t in iter_tables(conn):
            cur = conn.execute(f"SELECT COUNT(*) FROM {t}")
            (count,) = cur.fetchone()
            print(f"  - {t}: {count}")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

