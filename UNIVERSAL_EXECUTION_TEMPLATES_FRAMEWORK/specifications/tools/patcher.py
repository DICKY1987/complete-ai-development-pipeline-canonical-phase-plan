"""
Paragraph patcher for SPEC_MGMT_V1.

Replaces a paragraph by id, updates the sidecar and suite index.
"""
DOC_ID: DOC-PAT-TOOLS-PATCHER-967

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:
    raise SystemExit("Missing PyYAML. Install with `pip install pyyaml`.")


def compute_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compute_paragraphs(text: str):
    paras = []
    lines = text.splitlines()
    start = None
    buf = []
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


def load_suite_index(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def save_suite_index(data: dict, path: Path) -> None:
    path.write_text(yaml.dump(data, sort_keys=False), encoding="utf-8")


def load_sidecar(md_path: Path) -> dict:
    sc_path = md_path.with_suffix(md_path.suffix + ".sidecar.yaml")
    return yaml.safe_load(sc_path.read_text(encoding="utf-8"))


def save_sidecar(sc: dict, md_path: Path) -> None:
    sc_path = md_path.with_suffix(md_path.suffix + ".sidecar.yaml")
    sc_path.write_text(yaml.dump(sc, sort_keys=False), encoding="utf-8")


def replace_paragraph(md_path: Path, start_line: int, end_line: int, replacement_lines: list[str]) -> None:
    lines = md_path.read_text(encoding="utf-8").splitlines(keepends=True)
    start_idx = start_line - 1
    end_idx = end_line - 1
    new_lines = lines[:start_idx] + [l + "\n" for l in replacement_lines] + lines[end_idx + 1 :]
    md_path.write_text("".join(new_lines), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Patch a specification paragraph by id")
    ap.add_argument("--id", required=True, help="Paragraph ID to replace")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--text", help="Inline replacement text")
    g.add_argument("--file", help="Path to file with replacement text")
    args = ap.parse_args()

    spec_id = args.id
    if args.text is not None:
        replacement_text = args.text
    else:
        p = Path(args.file)
        if not p.exists():
            raise SystemExit(f"Replacement file {p} does not exist")
        replacement_text = p.read_text(encoding="utf-8")

    index_path = Path("docs/.index/suite-index.yaml")
    index_data = load_suite_index(index_path)
    suite = index_data.get("suite", {})

    found = None
    for vol in suite.get("volumes", []):
        for sec in vol.get("sections", []):
            for para in sec.get("paragraphs", []):
                if para.get("id") == spec_id:
                    found = (vol, sec, para)
                    break
            if found:
                break
        if found:
            break
    if not found:
        raise SystemExit(f"Paragraph id {spec_id} not found in index")

    vol, sec, para = found
    md_path = Path(sec["file"])
    sc = load_sidecar(md_path)
    p_entry = next((p for p in sc.get("paragraphs", []) if p.get("id") == spec_id), None)
    if not p_entry:
        raise SystemExit(f"Paragraph id {spec_id} not found in sidecar")

    start_line = p_entry["start_line"]
    end_line = p_entry["end_line"]
    replace_paragraph(md_path, start_line, end_line, replacement_text.splitlines())

    # recompute paragraphs and update sidecar
    updated = md_path.read_text(encoding="utf-8")
    paragraphs = compute_paragraphs(updated)
    old_entries = {(p["anchor"], p["start_line"], p["end_line"]): p["id"] for p in sc.get("paragraphs", [])}
    new_entries = []
    for idx, (start, end, ptxt) in enumerate(paragraphs, start=1):
        anchor = f"p-{idx}"
        pid = old_entries.get((anchor, start, end)) or next((v for (a, _, _), v in old_entries.items() if a == anchor), p_entry["id"] if anchor == p_entry["anchor"] else para["id"])
        new_entries.append({
            "anchor": anchor,
            "start_line": start,
            "end_line": end,
            "mfid": compute_hash(ptxt.encode("utf-8")),
            "id": pid,
        })

    file_hash = compute_hash(updated.encode("utf-8"))
    new_sc = {**sc, "mfid": file_hash, "paragraphs": new_entries}
    save_sidecar(new_sc, md_path)

    # update index section
    sec["mfid"] = file_hash
    sec["paragraphs"] = [{"id": p["id"], "anchor": p["anchor"], "mfid": p["mfid"]} for p in new_entries]
    save_suite_index(index_data, index_path)
    print(f"Patched paragraph {spec_id} in {md_path}")


if __name__ == "__main__":
    main()

