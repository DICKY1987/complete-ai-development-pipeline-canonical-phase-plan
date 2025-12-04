"""
Spec Indexer for multi-document versioning (SPEC_MGMT_V1).

Responsibilities:
- Walk a source tree of Markdown files.
- Ensure each has a .sidecar.yaml combining document and paragraph metadata.
- Validate sidecars against schema/sidecar_metadata.schema.yaml.
- Build docs/index.json (document metadata) and docs/.index/suite-index.yaml.

CLI:
  python tools/spec_indexer/indexer.py \
    --source <path> \
    --output docs/index.json \
    --suite-index-out docs/.index/suite-index.yaml \
    [--validate-only]

Defaults:
- source: "docs/source" if exists; otherwise fallback to
  "Multi-Document Versioning Automation final_spec_docs/docs/source".
"""
# DOC_ID: DOC-PAT-TOOLS-INDEXER-966

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    import yaml  # type: ignore
except Exception:
    raise SystemExit("Missing PyYAML. Install with `pip install pyyaml`.")

try:
    from jsonschema import Draft202012Validator  # type: ignore
except Exception:
    raise SystemExit("Missing jsonschema. Install with `pip install jsonschema`." )


def compute_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def write_yaml(obj: Any, p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        yaml.dump(obj, f, sort_keys=False)


def compute_paragraphs(text: str) -> List[Tuple[int, int, str]]:
    paras: List[Tuple[int, int, str]] = []
    lines = text.splitlines()
    start = None
    buf: List[str] = []
    for i, line in enumerate(lines, start=1):
        if not line.strip():
            if start is not None:
                paras.append((start, i - 1, "\n".join(buf)))
                start = None
                buf = []
            continue
        if start is None:
            start = i
        buf.append(line)
    if start is not None:
        paras.append((start, len(lines), "\n".join(buf)))
    return paras


def first_heading(text: str) -> str | None:
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("# "):
            return s[2:].strip()
    return None


def stable_id(seed: str) -> str:
    # Deterministic 26-char id from sha256
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:26].upper()


def ensure_sidecar(md_path: Path, schema: dict) -> dict:
    """Create or augment .sidecar.yaml for the given markdown file.

    Adds required document metadata fields if missing. Ensures paragraph entries
    exist with anchors, ranges, mfids and stable ids.
    """
    text = read_text(md_path)
    file_hash = compute_hash(text.encode("utf-8"))
    sc_path = md_path.with_suffix(md_path.suffix + ".sidecar.yaml")
    existing: Dict[str, Any] = {}
    if sc_path.exists():
        try:
            existing = yaml.safe_load(read_text(sc_path)) or {}
        except Exception:
            existing = {}

    # Build paragraphs
    paras = compute_paragraphs(text)
    sc_paras: List[Dict[str, Any]] = []
    # Map old anchors->id to preserve when present
    old_paras = { (p.get("anchor"), p.get("start_line"), p.get("end_line")): p.get("id")
                  for p in existing.get("paragraphs", []) }
    for idx, (start, end, ptext) in enumerate(paras, start=1):
        anchor = f"p-{idx}"
        key = (anchor, start, end)
        pid = old_paras.get(key)
        if not pid:
            pid = stable_id(f"{md_path.as_posix()}::{anchor}")
        sc_paras.append({
            "anchor": anchor,
            "start_line": start,
            "end_line": end,
            "mfid": compute_hash(ptext.encode("utf-8")),
            "id": pid,
        })

    # Document metadata defaults
    rel_path = md_path.as_posix()
    category = md_path.parent.name
    section_key = md_path.stem
    document_id = f"{category}/{section_key}"
    title = existing.get("title") or first_heading(text) or section_key.replace("-", " ")
    now_iso = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    sidecar: Dict[str, Any] = {
        **existing,
        "document_id": existing.get("document_id", document_id),
        "title": title,
        "version": existing.get("version", "0.1.0"),
        "category": existing.get("category", category),
        "last_updated": now_iso,
        "authors": existing.get("authors", []),
        "tags": existing.get("tags", []),
        "depends_on": existing.get("depends_on", []),
        "status": existing.get("status", "draft"),
        "checksum": compute_hash(text.encode("utf-8")),
        # Paragraph tracking
        "file": rel_path,
        "mfid": file_hash,
        "paragraphs": sc_paras,
    }

    # Validate
    Draft202012Validator(schema).validate(sidecar)

    # Write back
    write_yaml(sidecar, sc_path)
    return sidecar


def build_indices(source: Path, sidecars: List[dict], output_json: Path, suite_out: Path) -> None:
    # docs/index.json (flat metadata list)
    index = [{
        "document_id": sc["document_id"],
        "title": sc["title"],
        "version": sc["version"],
        "category": sc["category"],
        "last_updated": sc["last_updated"],
        "authors": sc.get("authors", []),
        "tags": sc.get("tags", []),
        "depends_on": sc.get("depends_on", []),
        "status": sc.get("status", "draft"),
        "checksum": sc.get("checksum"),
        "file": sc["file"],
        "mfid": sc["mfid"],
    } for sc in sidecars]
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(index, indent=2), encoding="utf-8")

    # suite-index.yaml (ordered volumes/sections)
    # Build hierarchy: category (dir) -> sections sorted by stem
    volumes: Dict[str, Dict[str, Any]] = {}
    for sc in sidecars:
        vol_key = sc["category"]
        vol = volumes.setdefault(vol_key, {"key": vol_key, "title": vol_key, "sections": []})
        vol["sections"].append({
            "key": Path(sc["file"]).stem,
            "title": sc["title"],
            "file": sc["file"],
            "id": stable_id(sc["document_id"]),
            "mfid": sc["mfid"],
            "paragraphs": [{"id": p["id"], "anchor": p["anchor"], "mfid": p["mfid"]} for p in sc.get("paragraphs", [])],
        })
    # sort sections by natural order of key (prefix numbers)
    for vol in volumes.values():
        vol["sections"].sort(key=lambda s: s["key"])

    suite = {
        "suite": {
            "title": "AI Development Pipeline Spec Suite",
            "version": "0.1.0",
            "effective_date": dt.date.today().isoformat(),
            "volumes": [volumes[k] for k in sorted(volumes.keys())],
        }
    }
    write_yaml(suite, suite_out)


def detect_orphans(source: Path) -> Dict[str, List[str]]:
    missing_sidecars: List[str] = []
    orphan_sidecars: List[str] = []
    md_files = [p for p in source.rglob("*.md")]
    sc_files = [p for p in source.rglob("*.md.sidecar.yaml")]
    sc_map = {p: p for p in sc_files}
    md_map = {p.with_suffix(p.suffix + ".sidecar.yaml"): p for p in md_files}
    for md in md_files:
        sc = md.with_suffix(md.suffix + ".sidecar.yaml")
        if not sc.exists():
            missing_sidecars.append(md.as_posix())
    for sc in sc_files:
        if sc not in md_map:
            orphan_sidecars.append(sc.as_posix())
    return {"missing_sidecars": missing_sidecars, "orphan_sidecars": orphan_sidecars}


def resolve_default_source() -> Path:
    primary = Path("docs/source")
    if primary.exists():
        return primary
    alt = Path("Multi-Document Versioning Automation final_spec_docs/docs/source")
    if alt.exists():
        return alt
    raise SystemExit("No source found. Create docs/source or provide --source.")


def main() -> None:
    ap = argparse.ArgumentParser(description="Spec indexer and sidecar validator")
    ap.add_argument("--source", default=None, help="Path to the docs source root")
    ap.add_argument("--output", default="docs/index.json", help="Path for index.json output")
    ap.add_argument("--suite-index-out", default="docs/.index/suite-index.yaml", help="Path for suite index YAML")
    ap.add_argument("--validate-only", action="store_true", help="Only validate existing sidecars")
    args = ap.parse_args()

    source = Path(args.source) if args.source else resolve_default_source()
    output_json = Path(args.output)
    suite_out = Path(args.suite_index_out)

    schema_path = Path("schema/sidecar_metadata.schema.yaml")
    if not schema_path.exists():
        raise SystemExit("Missing schema/sidecar_metadata.schema.yaml")
    schema = yaml.safe_load(schema_path.read_text(encoding="utf-8"))

    sidecars: List[dict] = []
    for md in sorted(source.rglob("*.md")):
        # Skip sidecar files themselves
        if md.name.endswith(".sidecar.yaml"):
            continue
        if args.validate_only and not md.with_suffix(md.suffix + ".sidecar.yaml").exists():
            print(f"Missing sidecar for {md}")
            continue
        sc = ensure_sidecar(md, schema) if not args.validate_only else yaml.safe_load(read_text(md.with_suffix(md.suffix + ".sidecar.yaml")))
        # Validate existing in validate-only mode
        if args.validate_only:
            Draft202012Validator(schema).validate(sc)
        sidecars.append(sc)

    build_indices(source, sidecars, output_json, suite_out)

    orphans = detect_orphans(source)
    if orphans["missing_sidecars"] or orphans["orphan_sidecars"]:
        print(json.dumps(orphans, indent=2))


if __name__ == "__main__":
    main()

