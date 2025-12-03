"""
Guard validator for SPEC_MGMT_V1.

Validates that suite-index.yaml, sidecars, and files are consistent.
"""
# DOC_ID: DOC-PAT-TOOLS-GUARD-965

from __future__ import annotations

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


def validate_suite(index_path: Path = Path("docs/.index/suite-index.yaml")) -> list[str]:
    errors: list[str] = []
    index = yaml.safe_load(index_path.read_text(encoding="utf-8"))
    suite = index.get("suite", {})

    seen_ids: set[str] = set()
    for vol in suite.get("volumes", []):
        keys_in_vol = set()
        for sec in vol.get("sections", []):
            sid = sec.get("id")
            if sid in seen_ids:
                errors.append(f"Duplicate section id {sid}")
            seen_ids.add(sid)
            skey = sec.get("key")
            if skey in keys_in_vol:
                errors.append(f"Duplicate section key {skey} in volume {vol.get('key')}")
            keys_in_vol.add(skey)
            for para in sec.get("paragraphs", []):
                pid = para.get("id")
                if not pid:
                    errors.append(f"Missing paragraph id in {vol.get('key')}/{skey} {para.get('anchor')}")
                elif pid in seen_ids:
                    errors.append(f"Duplicate paragraph id {pid}")
                else:
                    seen_ids.add(pid)

    for vol in suite.get("volumes", []):
        for sec in vol.get("sections", []):
            fpath = Path(sec.get("file"))
            if not fpath.exists():
                errors.append(f"Missing file {fpath}")
                continue
            content = fpath.read_text(encoding="utf-8")
            file_hash = compute_hash(content.encode("utf-8"))
            if sec.get("mfid") != file_hash:
                errors.append(f"MFID mismatch for {fpath}")
            sc_path = fpath.with_suffix(fpath.suffix + ".sidecar.yaml")
            if not sc_path.exists():
                errors.append(f"Missing sidecar for {fpath}")
                continue
            sc = yaml.safe_load(sc_path.read_text(encoding="utf-8"))
            if sc.get("mfid") != file_hash:
                errors.append(f"Sidecar MFID mismatch for {fpath}")
            sc_paras = sc.get("paragraphs", [])
            computed = compute_paragraphs(content)
            if len(sc_paras) != len(computed):
                errors.append(f"Paragraph count mismatch for {fpath}")
            for idx, (start, end, text) in enumerate(computed, start=1):
                anchor = f"p-{idx}"
                side = next((x for x in sc_paras if x.get("anchor") == anchor), None)
                if not side:
                    errors.append(f"Missing sidecar entry {anchor} in {fpath}")
                    continue
                if side.get("start_line") != start or side.get("end_line") != end:
                    errors.append(f"Line range mismatch for {fpath} {anchor}")
                ph = compute_hash(text.encode("utf-8"))
                if side.get("mfid") != ph:
                    errors.append(f"Paragraph MFID mismatch for {fpath} {anchor}")
                idx_para = next((x for x in sec.get("paragraphs", []) if x.get("anchor") == anchor), None)
                if not idx_para:
                    errors.append(f"Index missing paragraph {anchor} for {fpath}")
                else:
                    if idx_para.get("mfid") != side.get("mfid"):
                        errors.append(f"Index MFID mismatch for {fpath} {anchor}")
                    if idx_para.get("id") != side.get("id"):
                        errors.append(f"Index id mismatch for {fpath} {anchor}")
    return errors


def main() -> None:
    errs = validate_suite()
    if errs:
        for e in errs:
            print(e)
        raise SystemExit(1)
    print("Specification is valid.")


if __name__ == "__main__":
    main()

