"""
Resolver for SPEC_MGMT_V1.

Resolves:
- spec://VOLUME/SECTION[#p-N]
- specid://<ID>

Uses docs/.index/suite-index.yaml and sidecars to resolve to file and (optionally) line ranges.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:
    raise SystemExit("Missing PyYAML. Install with `pip install pyyaml`.")


def load_suite_index(path: str = "docs/.index/suite-index.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_sidecar(md_path: str) -> dict:
    sc_path = md_path + ".sidecar.yaml"
    with open(sc_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_spec_uri(uri: str, index: dict) -> dict:
    if uri.startswith("specid://"):
        target_id = uri[len("specid://") :]
        for vol in index.get("suite", {}).get("volumes", []):
            for sec in vol.get("sections", []):
                if sec.get("id") == target_id:
                    return {
                        "type": "section",
                        "id": sec["id"],
                        "file": sec["file"],
                        "volume_key": vol["key"],
                        "section_key": sec["key"],
                        "title": sec["title"],
                    }
                for para in sec.get("paragraphs", []):
                    if para.get("id") == target_id:
                        sc = load_sidecar(sec["file"])
                        for p in sc.get("paragraphs", []):
                            if p.get("id") == target_id:
                                return {
                                    "type": "paragraph",
                                    "id": p.get("id"),
                                    "file": sec["file"],
                                    "start_line": p.get("start_line"),
                                    "end_line": p.get("end_line"),
                                    "anchor": p.get("anchor"),
                                    "volume_key": vol["key"],
                                    "section_key": sec["key"],
                                    "title": sec["title"],
                                }
        raise KeyError(f"No object found with id {target_id}")

    if uri.startswith("spec://"):
        body = uri[len("spec://") :]
        anchor = None
        if "#" in body:
            body, anchor = body.split("#", 1)
        parts = body.split("/", 1)
        if len(parts) != 2:
            raise ValueError("Invalid spec:// URI; expected spec://VOLUME/SECTION")
        vol_key, sec_key = parts
        for vol in index.get("suite", {}).get("volumes", []):
            if vol.get("key") == vol_key:
                for sec in vol.get("sections", []):
                    if sec.get("key") == sec_key:
                        if not anchor:
                            return {
                                "type": "section",
                                "id": sec["id"],
                                "file": sec["file"],
                                "volume_key": vol["key"],
                                "section_key": sec["key"],
                                "title": sec["title"],
                            }
                        sc = load_sidecar(sec["file"])
                        for p in sc.get("paragraphs", []):
                            if p.get("anchor") == anchor:
                                return {
                                    "type": "paragraph",
                                    "id": p.get("id"),
                                    "file": sec["file"],
                                    "start_line": p.get("start_line"),
                                    "end_line": p.get("end_line"),
                                    "anchor": p.get("anchor"),
                                    "volume_key": vol["key"],
                                    "section_key": sec["key"],
                                    "title": sec["title"],
                                }
                        raise KeyError(f"Anchor {anchor} not found in section {sec_key}")
        raise KeyError(f"No matching section {sec_key} in volume {vol_key}")

    raise ValueError("Unsupported URI scheme; use spec:// or specid://")


def main() -> None:
    ap = argparse.ArgumentParser(description="Resolve specification URIs to file locations")
    ap.add_argument("uri", help="spec:// or specid:// URI")
    args = ap.parse_args()
    index = load_suite_index()
    result = resolve_spec_uri(args.uri, index)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

