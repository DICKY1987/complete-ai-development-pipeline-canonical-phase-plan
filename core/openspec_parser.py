# DOC_LINK: DOC-CORE-CORE-OPENSPEC-PARSER-046
# DOC_LINK: DOC-CORE-CORE-OPENSPEC-PARSER-023
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union

import yaml


@dataclass
class WhenThen:
    when: str
    then: str


@dataclass
class SpecItem:
    id: str
    title: str
    description: str = ""
    tags: List[str] = field(default_factory=list)
    when_then: List[WhenThen] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OpenSpecBundle:
    bundle_id: str
    items: List[SpecItem] = field(default_factory=list)
    version: str = "1.0"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "bundle-id": self.bundle_id,
            "version": self.version,
        }
        if self.metadata:
            data["metadata"] = self.metadata
        if self.items:
            data["items"] = [
                _serialize_item(item) for item in self.items
            ]
        return data

    def to_yaml(self) -> str:
        return yaml.safe_dump(
            self.to_dict(),
            sort_keys=False,
            allow_unicode=True,
        )


def _serialize_item(item: SpecItem) -> Dict[str, Any]:
    data: Dict[str, Any] = {
        "id": item.id,
        "title": item.title,
    }
    if item.description:
        data["description"] = item.description
    if item.tags:
        data["tags"] = item.tags
    if item.when_then:
        data["when-then"] = [
            {"when": wt.when, "then": wt.then} for wt in item.when_then
        ]
    if item.metadata:
        data["metadata"] = item.metadata
    return data


def _build_spec_item(raw: Dict[str, Any]) -> SpecItem:
    when_then_raw = raw.get("when-then", [])
    return SpecItem(
        id=str(raw.get("id") or raw.get("title") or "unknown"),
        title=str(raw.get("title", "")),
        description=str(raw.get("description", "")),
        tags=[
            str(tag)
            for tag in raw.get("tags", []) or []
            if tag is not None
        ],
        when_then=[
            WhenThen(when=str(entry.get("when", "")), then=str(entry.get("then", "")))
            for entry in when_then_raw
            if isinstance(entry, dict)
        ],
        metadata=dict(raw.get("metadata") or {}),
    )


def load_bundle_from_yaml(path: Union[str, Path]) -> OpenSpecBundle:
    src = Path(path)
    content = yaml.safe_load(src.read_text(encoding="utf-8")) or {}
    items_raw = content.get("items") or []
    return OpenSpecBundle(
        bundle_id=str(content.get("bundle-id") or content.get("id") or src.stem),
        version=str(content.get("version") or "1.0"),
        metadata=dict(content.get("metadata") or {}),
        items=[_build_spec_item(item) for item in items_raw if isinstance(item, dict)],
    )


def load_bundle_from_change(change_id: str, *, base_dir: Union[str, Path]) -> OpenSpecBundle:
    base = Path(base_dir)
    change_dir = base / "openspec" / "changes" / change_id
    proposal = (change_dir / "proposal.md").read_text(encoding="utf-8") if (change_dir / "proposal.md").exists() else ""
    tasks_file = change_dir / "tasks.md"
    tasks = []
    if tasks_file.exists():
        for line in tasks_file.read_text(encoding="utf-8").splitlines():
            clean_line = line.lstrip("- ").strip()
            if not clean_line:
                continue
            tasks.append(clean_line)

    items: List[SpecItem] = []
    items.append(
        SpecItem(
            id=f"CH-{change_id}",
            title=f"Change {change_id}",
            description=proposal.strip(),
        )
    )

    for idx, task_text in enumerate(tasks, start=1):
        items.append(
            SpecItem(
                id=f"T-{idx}-{change_id}",
                title=task_text,
            )
        )

    return OpenSpecBundle(
        bundle_id=f"openspec-{change_id}",
        version="1.0",
        items=items,
    )


def discover_specs(path: Union[str, Path]) -> List[OpenSpecBundle]:
    src = Path(path)
    files: List[Path] = []
    if src.is_dir():
        files.extend(sorted(src.glob("*.yaml")))
        files.extend(sorted(src.glob("*.yml")))
    elif src.is_file():
        files.append(src)
    bundles: List[OpenSpecBundle] = []
    for file in files:
        if file.exists():
            bundles.append(load_bundle_from_yaml(file))
    return bundles


def write_bundle(bundle: OpenSpecBundle, out_dir: Union[str, Path]) -> Path:
    destination = Path(out_dir)
    destination.mkdir(parents=True, exist_ok=True)
    out_path = destination / f"{bundle.bundle_id}.yaml"
    out_path.write_text(bundle.to_yaml(), encoding="utf-8")
    return out_path


def openspec_main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="OpenSpec bundle writer")
    parser.add_argument("--change-id", help="Create bundle from a change folder")
    parser.add_argument("--bundle", help="Load existing bundle YAML")
    parser.add_argument("--out", default=".", help="Output directory")
    parser.add_argument("--echo", action="store_true", help="Echo output path")
    args = parser.parse_args(argv)

    bundle: Optional[OpenSpecBundle] = None
    if args.change_id:
        bundle = load_bundle_from_change(args.change_id, base_dir=Path("."))
    elif args.bundle:
        bundle = load_bundle_from_yaml(Path(args.bundle))
    else:
        parser.error("Specify --change-id or --bundle")

    out_path = write_bundle(bundle, args.out)
    if args.echo:
        print(out_path)
    return 0


__all__ = [
    "OpenSpecBundle",
    "SpecItem",
    "WhenThen",
    "load_bundle_from_yaml",
    "load_bundle_from_change",
    "discover_specs",
    "write_bundle",
    "openspec_main",
    "main",
]

main = openspec_main

