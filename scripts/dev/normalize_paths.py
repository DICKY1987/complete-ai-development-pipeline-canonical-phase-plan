from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None  # type: ignore


PATH_REGEX = re.compile(r"(?P<path>(?:[A-Za-z]:\\\\|\\\\\\\\|\.|~)?(?:[\\/][^\\/\n\r\t\f\v\)\]\s]+){1,})")
MD_LINK_REGEX = re.compile(r"(\[([^\]]+)\])\(([^)]+)\)")


DEFAULT_INCLUDE = [
    "PHASE_DEV_DOCS",
    "plans",
    "Coordination Mechanisms",
]
DOC_EXTS = {".md", ".txt"}


def load_mapping(config_path: Path) -> Dict:
    if yaml is None:
        return {}
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    return data or {}


def normalize_one(path: str, canonical_table: Dict[str, str]) -> str:
    if "://" in path:
        return path  # skip URLs
    p = path.replace("\\", "/")
    if p.startswith("./"):
        p = p[2:]
    while "//" in p:
        p = p.replace("//", "/")
    # canonicalize top-level section case-insensitively
    parts = p.split("/")
    if parts and parts[0]:
        head = parts[0].lower()
        for key, target in canonical_table.items():
            if head == key.lower():
                # Replace with canonical head (strip trailing / from target)
                canon_head = target[:-1] if target.endswith('/') else target
                parts[0] = canon_head
                break
    return "/".join(parts)


def normalize_content(text: str, canonical_table: Dict[str, str]) -> Tuple[str, int]:
    changes = 0

    def repl_link(m: re.Match[str]) -> str:
        nonlocal changes
        prefix, label, url = m.group(1), m.group(2), m.group(3)
        new_url = normalize_one(url, canonical_table)
        if new_url != url:
            changes += 1
        return f"{prefix}({new_url})"

    text2 = MD_LINK_REGEX.sub(repl_link, text)

    # Also normalize standalone path-like tokens cautiously (avoid mangling code blocks)
    def repl_path(m: re.Match[str]) -> str:
        nonlocal changes
        val = m.group("path")
        new_val = normalize_one(val, canonical_table)
        if new_val != val:
            changes += 1
        return new_val

    text3 = PATH_REGEX.sub(repl_path, text2)
    return text3, changes


def iter_target_files(root: Path, includes: List[str]) -> List[Path]:
    files: List[Path] = []
    for inc in includes:
        base = (root / inc)
        if not base.exists():
            continue
        for fp in base.rglob("*"):
            if fp.is_file() and fp.suffix.lower() in DOC_EXTS:
                files.append(fp)
    return files


def build_canonical_table(cfg: Dict) -> Dict[str, str]:
    table: Dict[str, str] = {}
    sections = (cfg or {}).get("sections", [])
    for sec in sections:
        name = sec.get("name")
        root = sec.get("target-root")
        if name and root:
            table[name] = root
    # Also add explicit keys for target-root heads to stabilize canonicalization
    for sec in sections:
        root = sec.get("target-root", "")
        if root:
            head = root.strip("/").split("/")[0]
            table.setdefault(head, root)
    return table


def main() -> None:
    ap = argparse.ArgumentParser(description="Normalize path references in docs for WS-03")
    ap.add_argument("--root", default=".")
    ap.add_argument("--config", default="config/section_map.yaml")
    ap.add_argument("--sections", nargs="*", default=DEFAULT_INCLUDE,
                    help="Top-level folders to include (default: PHASE_DEV_DOCS, plans, Coordination Mechanisms)")
    ap.add_argument("--apply", action="store_true", help="Write changes (default is dry-run)")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    cfg = load_mapping(Path(args.config))
    canon = build_canonical_table(cfg)

    files = iter_target_files(root, args.sections)
    total_changes = 0
    changed_files = 0

    for fp in files:
        try:
            text = fp.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        new_text, changes = normalize_content(text, canon)
        if changes > 0:
            changed_files += 1
            total_changes += changes
            if args.apply:
                fp.write_text(new_text, encoding="utf-8")

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"WS-03 normalize ({mode})")
    print(f" Scanned files: {len(files)}")
    print(f" Files with changes: {changed_files}")
    print(f" Total replacements: {total_changes}")


if __name__ == "__main__":
    main()

