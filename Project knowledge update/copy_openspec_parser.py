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


def _read_change_tasks(change_dir: Path) -> List[str]:
    tasks_path = change_dir / "tasks.md"
    if not tasks_path.exists():
        return []
    lines = tasks_path.read_text(encoding="utf-8").splitlines()
    tasks: List[str] = []
    for line in lines:
        s = line.strip()
        if s.startswith("- [") or s.startswith("-"):
            # strip checkbox markers if present
            s2 = s.lstrip("- ")
            if s2.startswith("[ ") or s2.startswith("[x") or s2.startswith("[X"):
                # remove leading [ ] or [x] token
                rb = s2.find("]")
                if rb != -1:
                    s2 = s2[rb + 1 :].strip()
            tasks.append(s2)
    return tasks


def _read_change_title(change_dir: Path) -> str:
    prop = change_dir / "proposal.md"
    if not prop.exists():
        return change_dir.name
    text = prop.read_text(encoding="utf-8")
    # Try YAML frontmatter title first
    title = ""
    if text.startswith("---"):
        lines = text.splitlines()
        for i in range(1, min(len(lines), 50)):
            l = lines[i].strip()
            if l == "---":
                break
            if l.lower().startswith("title:"):
                title = l.split(":", 1)[1].strip().strip('"')
                break
    if not title:
        # Fallback to first Markdown heading
        for line in text.splitlines():
            if line.lstrip().startswith("#"):
                title = line.lstrip("# ").strip()
                if title:
                    break
    return title or change_dir.name


def load_bundle_from_change(change_id: str, base_dir: Optional[Path] = None) -> OpenSpecBundle:
    """Create an OpenSpecBundle from an OpenSpec change directory.

    Expects structure: openspec/changes/<change-id>/{proposal.md,tasks.md}
    """
    root = (base_dir or Path.cwd()).resolve()
    change_dir = root / "openspec" / "changes" / change_id
    if not change_dir.exists():
        raise FileNotFoundError(f"OpenSpec change not found: {change_dir}")

    title = _read_change_title(change_dir)
    tasks = _read_change_tasks(change_dir)

    items: List[SpecItem] = []
    # Make a single high-level item for the change plus task-tagged items
    items.append(SpecItem(id=f"CH-{change_id}", title=title, description=""))
    for idx, t in enumerate(tasks, start=1):
        items.append(SpecItem(id=f"T-{idx}", title=t))

    return OpenSpecBundle(bundle_id=f"openspec-{change_id}", items=items)


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
    src = ap.add_mutually_exclusive_group(required=False)
    src.add_argument("input", nargs="?", default=None, help="Path to bundle file or directory")
    src.add_argument("--change-id", dest="change_id", help="OpenSpec change id under openspec/changes/")
    ap.add_argument("--out", type=str, default="bundles", help="Output bundles directory")
    ap.add_argument("--echo", action="store_true", help="Echo normalized YAML to stdout")
    ap.add_argument("--generate-bundle", action="store_true", help="Generate bundle YAML to --out")
    ap.add_argument("--create-epic", action="store_true", help="Stub: print epic payload for pm/GitHub")
    args = ap.parse_args(argv)

    out_dir = Path(args.out)

    built_bundles: List[OpenSpecBundle] = []
    if args.change_id:
        built_bundles = [load_bundle_from_change(args.change_id)]
    elif args.input:
        input_path = Path(args.input)
        built_bundles = discover_specs(input_path)
    else:
        print("Either --change-id or input path is required", file=sys.stderr)
        return 2

    if not built_bundles:
        print("No bundles found", file=sys.stderr)
        return 2

    last_out: Optional[Path] = None
    for b in built_bundles:
        if args.generate-bundle or args.input:
            last_out = write_bundle(b, out_dir)
        if args.echo:
            sys.stdout.write(b.to_yaml())
        if args.create_epic:
            payload = {
                "title": f"[OpenSpec] {b.bundle_id}",
                "labels": ["openspec", "epic"],
                "body": f"Auto-generated from {b.bundle_id}. Items: {len(b.items)}",
            }
            print(json.dumps(payload, indent=2))

    if last_out:
        print(str(last_out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

