from __future__ import annotations

import dataclasses as dc
import json
import sys
from dataclasses import field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


@dc.dataclass
class WhenThen:
    when: str
    then: str


@dc.dataclass
class SpecItem:
    id: str
    title: str
    description: str = ""
    tags: List[str] = field(default_factory=list)
    when_then: List[WhenThen] = field(default_factory=list)


@dc.dataclass
class OpenSpecBundle:
    bundle_id: str
    items: List[SpecItem]
    version: str = "1.0"
    metadata: Dict[str, Any] = dc.field(default_factory=dict)

    def to_yaml(self) -> str:
        # Minimal YAML emitter to avoid extra dependencies; stable ordering
        def esc(s: str) -> str:
            if any(ch in s for ch in [":", "-", "#", "\n", '"', "'"]):
                return json.dumps(s)
            return s

        lines: List[str] = []
        lines.append(f"bundle-id: {esc(self.bundle_id)}")
        lines.append(f"version: {esc(self.version)}")
        if self.metadata:
            lines.append("metadata:")
            for k in sorted(self.metadata.keys()):
                v = self.metadata[k]
                lines.append(f"  {k}: {esc(str(v))}")
        lines.append("items:")
        for it in self.items:
            lines.append("  - id: " + esc(it.id))
            lines.append("    title: " + esc(it.title))
            if it.description:
                desc = it.description.strip().replace("\n", "\\n")
                lines.append("    description: " + esc(desc))
            if it.tags:
                lines.append("    tags:")
                for t in it.tags:
                    lines.append("      - " + esc(t))
            if it.when_then:
                lines.append("    when-then:")
                for wt in it.when_then:
                    lines.append("      - when: " + esc(wt.when))
                    lines.append("        then: " + esc(wt.then))
        return "\n".join(lines) + "\n"


def load_bundle_from_yaml(path: Path) -> OpenSpecBundle:
    # Specialized, minimal parser for the expected bundle shape.
    bundle_id: Optional[str] = None
    version: str = "1.0"
    metadata: Dict[str, Any] = {}
    items: List[SpecItem] = []

    in_items = False
    in_when_then = False
    current_item: Optional[Dict[str, Any]] = None

    lines = path.read_text(encoding="utf-8").splitlines()
    for raw in lines:
        line = raw.rstrip("\n")
        if not line.strip() or line.strip().startswith("#"):
            continue
        if not in_items:
            if line.startswith("bundle-id:") or line.startswith("bundle_id:"):
                bundle_id = line.split(":", 1)[1].strip().strip('"')
                continue
            if line.startswith("version:"):
                version = line.split(":", 1)[1].strip().strip('"')
                continue
            if line.startswith("metadata:"):
                # Simple metadata parsing of immediate k:v pairs
                in_metadata = True
                continue
            if line.startswith("items:"):
                in_items = True
                continue
            # ignore other top-level keys for now
            continue
        # in items
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        if stripped.startswith("- "):
            # start of new item, may include inline key:value
            if current_item is not None:
                # finalize previous
                it = SpecItem(
                    id=str(current_item.get("id", "")),
                    title=str(current_item.get("title", "")),
                    description=str(current_item.get("description", "")),
                    tags=list(current_item.get("tags", []) or []),
                    when_then=[WhenThen(when=w[0], then=w[1]) for w in current_item.get("when_then", [])],
                )
                items.append(it)
            current_item = {"when_then": []}
            in_when_then = False
            # inline key: value on same line
            inline = stripped[2:].strip()
            if ":" in inline:
                k, v = [s.strip() for s in inline.split(":", 1)]
                if k == "id":
                    current_item["id"] = v.strip('"')
                else:
                    current_item[k] = v.strip('"')
            continue
        # handle nested fields for current_item
        if current_item is None:
            continue
        key_val = stripped.split(":", 1)
        if len(key_val) == 2:
            k = key_val[0].strip()
            v = key_val[1].strip()
            if k == "when-then":
                in_when_then = True
                continue
            if k == "tags":
                # subsequent lines expected as list items; skip here
                current_item.setdefault("tags", [])
                continue
            # simple scalar
            current_item[k] = v.strip('"')
            continue
        # list items under when-then or tags
        if stripped.startswith("-") and in_when_then:
            # expect forms: - when: X / then: Y possibly on next indented line
            rest = stripped[1:].strip()
            # optional prefix 'when:' on same line
            if rest.startswith("when:"):
                when_txt = rest.split(":", 1)[1].strip().strip('"')
                # next lines may contain 'then:'; handled in future iterations
                current_item.setdefault("_pending_when", when_txt)
                continue
        if stripped.startswith("then:") and in_when_then:
            then_txt = stripped.split(":", 1)[1].strip().strip('"')
            when_txt = current_item.pop("_pending_when", "")
            current_item.setdefault("when_then", []).append((when_txt, then_txt))
            continue
        if stripped.startswith("-") and "tags" in current_item and not in_when_then:
            tag_val = stripped[1:].strip().strip('"')
            current_item.setdefault("tags", []).append(tag_val)
            continue

    # finalize last item
    if in_items and current_item is not None:
        it = SpecItem(
            id=str(current_item.get("id", "")),
            title=str(current_item.get("title", "")),
            description=str(current_item.get("description", "")),
            tags=list(current_item.get("tags", []) or []),
            when_then=[WhenThen(when=w[0], then=w[1]) for w in current_item.get("when_then", [])],
        )
        items.append(it)

    if bundle_id is None:
        raise ValueError("bundle-id is required")
    return OpenSpecBundle(bundle_id=bundle_id, items=items, version=version, metadata=metadata)


def discover_specs(input_path: Path) -> List[OpenSpecBundle]:
    if input_path.is_file() and input_path.suffix in {".yaml", ".yml"}:
        return [load_bundle_from_yaml(input_path)]
    bundles: List[OpenSpecBundle] = []
    if input_path.is_dir():
        for p in sorted(input_path.rglob("*.yml")) + sorted(input_path.rglob("*.yaml")):
            bundles.append(load_bundle_from_yaml(p))
    return bundles


def write_bundle(bundle: OpenSpecBundle, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{bundle.bundle_id}.yaml"
    out_path.write_text(bundle.to_yaml(), encoding="utf-8")
    return out_path


def main(argv: List[str]) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="OpenSpec parser and bundle generator")
    ap.add_argument("input", type=str, help="Path to .yaml bundle or directory with bundles")
    ap.add_argument("--out", type=str, default="bundles", help="Output bundles directory")
    ap.add_argument("--echo", action="store_true", help="Echo normalized YAML to stdout")
    args = ap.parse_args(argv)

    input_path = Path(args.input)
    out_dir = Path(args.out)
    bundles = discover_specs(input_path)
    if not bundles:
        print("No bundles found", file=sys.stderr)
        return 2
    last: Optional[Path] = None
    for b in bundles:
        last = write_bundle(b, out_dir)
        if args.echo:
            sys.stdout.write(b.to_yaml())
    if last:
        print(str(last))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
