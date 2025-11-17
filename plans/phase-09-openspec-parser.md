# Phase 09: OpenSpec parser and bundle generation

This phase delivers a minimal, working OpenSpec parser and bundle generator that
produces normalized YAML bundles suitable for downstream pipeline stages. It also
includes CLI usage, tests, and integration points with the error pipeline.

## Objectives

- Parse OpenSpec source files into a structured, validated model.
- Generate deterministic bundle YAML artifacts under `bundles/`.
- Provide a small Python module and CLI wrapper for local use and CI.
- Add tests that validate parsing, normalization, and bundle emission.
- Prepare integration hooks for the error pipeline and agents.

## Prerequisites

- Python 3.10+
- `pytest` installed locally or in CI
- Optional: `gh` GitHub CLI configured (`gh auth status` shows logged in)
- Repository layout assumptions:
  - Source code path: `src/pipeline/`
  - Spec inputs: `docs/spec/` (Markdown + front matter) and/or `bundles/*.yaml`
  - Bundle outputs: `bundles/*.yaml`

## Tasks

1. Create parser module `src/pipeline/openspec_parser.py`.
2. Implement model types and validation (lightweight, no external deps).
3. Support inputs:
   - Single file: `.yaml` or `.yml`
   - Directory scan: `docs/spec/` for Markdown specs with front matter
4. Normalize and emit bundle YAML (`bundles/<name>.yaml`).
5. Add CLI entry points for common flows.
6. Add tests in `tests/test_openspec_parser.py`.
7. Optional: create a GitHub epic via `gh issue create` for a generated bundle.

## Code snippets

Place the following file at `src/pipeline/openspec_parser.py`.

```python
# src/pipeline/openspec_parser.py
from __future__ import annotations

import dataclasses as dc
import json
import sys
import textwrap
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
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_yaml(self) -> str:
        # Minimal YAML emitter to avoid extra deps; stable ordering
        def esc(s: str) -> str:
            if any(ch in s for ch in [":", "-", "#", "\n", "\"", "'"]):
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


def _parse_simple_yaml(path: Path) -> Dict[str, Any]:
    # Tiny YAML subset parser for key: value, lists, and list of maps.
    # Replace with PyYAML if allowed; kept minimal per repo guidelines.
    import re

    data: Dict[str, Any] = {}
    stack: List[Tuple[int, Union[Dict[str, Any], List[Any]]]] = [(0, data)]
    current_key: Optional[str] = None

    def set_value(container, key, value):
        if isinstance(container, dict):
            container[key] = value
        else:
            raise ValueError("Invalid container for key assignment")

    with path.open("r", encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not line.strip() or line.strip().startswith("#"):
                continue
            indent = len(line) - len(line.lstrip(" "))
            while stack and indent < stack[-1][0]:
                stack.pop()
            container = stack[-1][1]
            if line.lstrip().startswith("- "):
                item_str = line.lstrip()[2:].strip()
                if not isinstance(container, list):
                    # Convert previous key to list
                    if isinstance(container, dict) and current_key:
                        lst: List[Any] = []
                        container[current_key] = lst
                        container = lst
                        stack.append((indent, container))
                    else:
                        raise ValueError("List item without a list context")
                if ":" in item_str:
                    # list item is a map starter
                    d: Dict[str, Any] = {}
                    container.append(d)  # type: ignore[arg-type]
                    stack.append((indent + 2, d))
                    key, val = [s.strip() for s in item_str.split(":", 1)]
                    d[key] = val if val else None
                    current_key = key
                else:
                    container.append(item_str)  # type: ignore[arg-type]
            else:
                key, val = [s.strip() for s in line.split(":", 1)]
                if val == "":
                    # container or list follows
                    d: Dict[str, Any] = {}
                    set_value(container, key, d)
                    stack.append((indent + 2, d))
                    current_key = key
                else:
                    set_value(container, key, val)
                    current_key = key
    return data


def load_bundle_from_yaml(path: Path) -> OpenSpecBundle:
    raw = _parse_simple_yaml(path)
    bundle_id = str(raw.get("bundle-id") or raw.get("bundle_id"))
    version = str(raw.get("version", "1.0"))
    metadata = dict(raw.get("metadata", {}))
    items_raw = raw.get("items", [])
    items: List[SpecItem] = []
    for r in items_raw:
        sid = str(r.get("id"))
        title = str(r.get("title"))
        desc = str(r.get("description", ""))
        tags = list(r.get("tags", []) or [])
        when_then = [WhenThen(when=str(x.get("when")), then=str(x.get("then"))) for x in (r.get("when-then") or [])]
        items.append(SpecItem(id=sid, title=title, description=desc, tags=tags, when_then=when_then))
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
```

### Optional: GitHub epic creation via `gh`

Example command to create an epic (GitHub issue) for a bundle:

```bash
gh issue create \
  --title "OpenSpec: <bundle-id>" \
  --body "Automated epic for OpenSpec bundle <bundle-id>" \
  --label epic,openspec
```

Replace `<bundle-id>` with the actual bundle id printed by the CLI.

## Tests

Create `tests/test_openspec_parser.py`:

```python
# tests/test_openspec_parser.py
from pathlib import Path
from src.pipeline.openspec_parser import load_bundle_from_yaml, write_bundle


def test_load_and_roundtrip(tmp_path: Path):
    src = tmp_path / "demo.yaml"
    src.write_text(
        (
            "bundle-id: demo-001\n"
            "version: 1.0\n"
            "items:\n"
            "  - id: S-1\n"
            "    title: Login succeeds\n"
            "    when-then:\n"
            "      - when: user submits valid credentials\n"
            "        then: session is created\n"
        ),
        encoding="utf-8",
    )
    b = load_bundle_from_yaml(src)
    assert b.bundle_id == "demo-001"
    out = write_bundle(b, tmp_path)
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "bundle-id: \"demo-001\"" in text or "bundle-id: demo-001" in text
```

Run tests:

```bash
pytest -q
```

## Integration points

- Error pipeline: consume normalized bundles from `bundles/` and enqueue units
  for `file-analyzer`, `test-runner`, and `code-analyzer` agents.
- Reference: `MOD_ERROR_PIPELINE/pipeline_engine.py` for queueing/dispatch.
- Future phases (10–11) will wire coordinator and state transitions.

## Rollback plan

- Revert changes by removing `src/pipeline/openspec_parser.py` and any generated
  files under `bundles/` created during this phase.
- If CI is impacted, pin jobs to a commit prior to this change and re-run.

