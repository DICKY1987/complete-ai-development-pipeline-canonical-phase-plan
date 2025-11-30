"""
Renderer for specifications.

Primary mode (SPEC_MGMT_V1 compatibility):
- Reads docs/.index/suite-index.yaml and concatenates sections into a single Markdown stream.

OpenSpec fallback mode:
- If suite-index is not present, renders all `openspec/specs/**/spec.md` files
  in deterministic order into a single Markdown stream with headings.
"""
DOC_ID: DOC-PAT-TOOLS-RENDERER-968

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

try:
    import yaml  # type: ignore
except ImportError:
    raise SystemExit("Missing PyYAML. Install with `pip install pyyaml`.")


def load_suite_index(path: str = "docs/.index/suite-index.yaml") -> dict | None:
    p = Path(path)
    if not p.exists():
        return None
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def read_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def render_spec(index: dict) -> str:
    lines = []
    suite = index.get("suite", {})
    title = suite.get("title", "Specification")
    lines.append(f"# {title}\n")
    version = suite.get("version")
    eff = suite.get("effective_date")
    meta = []
    if version:
        meta.append(f"Version {version}")
    if eff:
        meta.append(f"Effective {eff}")
    if meta:
        lines.append(f"_({', '.join(meta)})_\n\n")
    for vol in suite.get("volumes", []):
        vkey = vol.get("key")
        vtitle = vol.get("title")
        lines.append(f"\n## {vkey} {vtitle}\n")
        for sec in vol.get("sections", []):
            skey = sec.get("key")
            stitle = sec.get("title")
            lines.append(f"\n### {vkey}/{skey} {stitle}\n")
            content = read_file(sec["file"]) 
            lines.append(content.rstrip() + "\n")
    return "\n".join(lines)


def render_openspec_specs(root: Path = Path("openspec/specs")) -> str:
    """Render all OpenSpec spec.md files into a single Markdown stream.

    Orders by directory then filename, and inserts section headings based on the
    immediate directory name and file path.
    """
    if not root.exists():
        return "# Specification\n\n_No OpenSpec specs found._\n"
    files: List[Path] = sorted(root.rglob("spec.md"))
    if not files:
        return "# Specification\n\n_No OpenSpec specs found._\n"
    out: List[str] = ["# Specification\n"]
    for p in files:
        # Heading derived from directory structure
        rel = p.relative_to(root)
        section = rel.parts[0]
        out.append(f"\n## {section}\n")
        out.append(p.read_text(encoding="utf-8").rstrip() + "\n")
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description="Render the specification into a single Markdown file")
    ap.add_argument("--output", "-o", help="Path to write rendered Markdown")
    args = ap.parse_args()
    index = load_suite_index()
    if index is not None:
        output = render_spec(index)
    else:
        output = render_openspec_specs()
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
