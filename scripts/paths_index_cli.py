from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from tools.hardcoded_path_indexer import scan_repository


def _open_db(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    return conn


def cmd_scan(args: argparse.Namespace) -> None:
    root = Path(args.root).resolve()
    db = Path(args.db).resolve()
    files, occ = scan_repository(root, db, reset=args.reset, include_hidden=args.include_hidden)
    print(f"Scanned files: {files}")
    print(f"Occurrences inserted: {occ}")


def _query(conn: sqlite3.Connection, sql: str, params: Tuple[Any, ...] = ()) -> List[Tuple[Any, ...]]:
    cur = conn.cursor()
    cur.execute(sql, params)
    return list(cur.fetchall())


def cmd_report(args: argparse.Namespace) -> None:
    db = Path(args.db).resolve()
    conn = _open_db(db)
    try:
        where = []
        params: List[Any] = []
        if args.kind:
            where.append("kind = ?")
            params.append(args.kind)
        if args.pattern:
            where.append("pattern = ?")
            params.append(args.pattern)
        if args.file:
            where.append("file_path = ?")
            params.append(args.file)
        sql = "SELECT file_path, line_no, kind, pattern, value FROM occurrences"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY file_path, line_no"
        if args.limit:
            sql += f" LIMIT {int(args.limit)}"
        rows = _query(conn, sql, tuple(params))
    finally:
        conn.close()

    for r in rows:
        f, ln, k, p, v = r
        pdisp = p if p is not None else "-"
        print(f"{f}:{ln}\t{k}\t{pdisp}\t{v}")


def cmd_summary(args: argparse.Namespace) -> None:
    db = Path(args.db).resolve()
    conn = _open_db(db)
    try:
        by_kind = _query(conn, "SELECT kind, COUNT(*) FROM occurrences GROUP BY kind ORDER BY COUNT(*) DESC")
        by_pattern = _query(conn, "SELECT COALESCE(pattern,'-') as pat, COUNT(*) FROM occurrences GROUP BY pat ORDER BY COUNT(*) DESC LIMIT 50")
        files = _query(conn, "SELECT COUNT(*) FROM files")
    finally:
        conn.close()

    print("Files scanned:\t", files[0][0] if files else 0)
    print("\nBy kind:")
    for k, c in by_kind:
        print(f"  {k}: {c}")
    print("\nTop patterns:")
    for p, c in by_pattern:
        print(f"  {p}: {c}")


def cmd_export(args: argparse.Namespace) -> None:
    db = Path(args.db).resolve()
    conn = _open_db(db)
    try:
        rows = _query(
            conn,
            "SELECT file_path, line_no, kind, pattern, value, context, ext FROM occurrences ORDER BY file_path, line_no",
        )
    finally:
        conn.close()

    out = Path(args.out)
    if args.format == "json":
        data = [
            {
                "file_path": r[0],
                "line_no": r[1],
                "kind": r[2],
                "pattern": r[3],
                "value": r[4],
                "context": r[5],
                "ext": r[6],
            }
            for r in rows
        ]
        out.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"Exported {len(data)} rows to {out}")
    elif args.format == "csv":
        with out.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["file_path", "line_no", "kind", "pattern", "value", "context", "ext"])
            for r in rows:
                w.writerow(r)
        print(f"Exported {len(rows)} rows to {out}")
    else:
        raise SystemExit("Unsupported format (use json or csv)")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="paths_index_cli", description="Hardcoded path indexer CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    s_scan = sub.add_parser("scan", help="Scan repository and persist to SQLite")
    s_scan.add_argument("--root", default=".", help="Repository root (default: .)")
    s_scan.add_argument("--db", default="refactor_paths.db", help="SQLite db path (default: refactor_paths.db)")
    s_scan.add_argument("--reset", action="store_true", help="Reset database before scanning")
    s_scan.add_argument("--include-hidden", action="store_true", help="Include hidden files and folders")
    s_scan.set_defaults(func=cmd_scan)

    s_rep = sub.add_parser("report", help="Print occurrences filtered by criteria")
    s_rep.add_argument("--db", default="refactor_paths.db")
    s_rep.add_argument("--kind")
    s_rep.add_argument("--pattern")
    s_rep.add_argument("--file")
    s_rep.add_argument("--limit", type=int)
    s_rep.set_defaults(func=cmd_report)

    s_sum = sub.add_parser("summary", help="Show aggregate counts by kind and pattern")
    s_sum.add_argument("--db", default="refactor_paths.db")
    s_sum.set_defaults(func=cmd_summary)

    s_exp = sub.add_parser("export", help="Export all occurrences to JSON/CSV")
    s_exp.add_argument("--db", default="refactor_paths.db")
    s_exp.add_argument("--format", choices=["json", "csv"], default="json")
    s_exp.add_argument("--out", required=True)
    s_exp.set_defaults(func=cmd_export)

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
