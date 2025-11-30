#!/usr/bin/env python
# DOC_LINK: DOC-SCRIPT-DEV-PATHS-RESOLVE-CLI-269
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Ensure 'src' is importable when running from repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from path_registry import resolve_path, list_paths  # type: ignore


def cmd_resolve(args: argparse.Namespace) -> int:
    try:
        p = resolve_path(args.key)
        print(p)
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 2


def cmd_list(args: argparse.Namespace) -> int:
    data = list_paths(args.section)
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        for k, v in sorted(data.items()):
            print(f"{k} -> {v}")
    return 0


def cmd_debug(args: argparse.Namespace) -> int:
    # Print full metadata for the key
    from src.path_registry import _load_registry_raw, _flatten_paths  # type: ignore

    tree = _load_registry_raw()
    flat = _flatten_paths(tree)
    meta: dict[str, Any] | None = flat.get(args.key)  # type: ignore[assignment]
    if meta is None:
        print(f"unknown key: {args.key}", file=sys.stderr)
        return 2
    print(json.dumps(meta, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="paths-resolve",
        description="Resolve logical keys to repo-relative paths",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    p_res = sub.add_parser("resolve", help="Resolve a single key")
    p_res.add_argument("key")
    p_res.set_defaults(func=cmd_resolve)

    p_list = sub.add_parser("list", help="List all keys (optionally by section)")
    p_list.add_argument("--section", default=None)
    p_list.add_argument("--json", action="store_true")
    p_list.set_defaults(func=cmd_list)

    p_dbg = sub.add_parser("debug", help="Show metadata for a key")
    p_dbg.add_argument("key")
    p_dbg.set_defaults(func=cmd_debug)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(bool(args.func(args)))


if __name__ == "__main__":
    raise SystemExit(main())
