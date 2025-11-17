# Phase 13: Advanced features (spec validation, auto-archive)

Extend the pipeline with a spec validation plugin (parsing WHEN/THEN clauses),
auto-archiving on `S_SUCCESS`, simple dashboard hooks, and a path to expand
multi-language plugins.

## Objectives

- Implement a spec validation plugin that parses WHEN/THEN and enforces shape.
- Add auto-archive behavior on final success.
- Provide a minimal dashboard integration point.
- Propose structure for multi-language plugin support.

## Prerequisites

- Phase 09 bundle format and `WhenThen` structures.
- Phase 11 pipeline integration entry point.

## Tasks

1. Create `src/plugins/spec_validator.py` parsing WHEN/THEN.
2. Add adapter hook in the pipeline to invoke validator pre-test.
3. Implement auto-archive utility and wire on `S_SUCCESS`.
4. Document dashboard metrics and a simple reporter.
5. Outline multi-language plugin expansion.

## Code snippets

Place at `src/plugins/spec_validator.py`.

```python
# src/plugins/spec_validator.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


@dataclass
class ValidationIssue:
    unit_id: str
    severity: str  # info|warn|error
    message: str


def parse_when_then(text: str) -> Tuple[str, str]:
    # Format: "WHEN <...> THEN <...>"; tolerant of case and spacing.
    s = text.strip()
    up = s.upper()
    if "WHEN " in up and " THEN " in up:
        w = up.index("WHEN ")
        t = up.index(" THEN ")
        when = s[w + 5 : t].strip()
        then = s[t + 6 :].strip()
        return when, then
    # fallback: return as-is if not strictly matched
    return s, ""


def validate(unit_id: str, clauses: List[str]) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    if not clauses:
        issues.append(ValidationIssue(unit_id, "warn", "No WHEN/THEN clauses"))
        return issues
    for raw in clauses:
        when, then = parse_when_then(raw)
        if not when or not then:
            issues.append(ValidationIssue(unit_id, "error", f"Malformed clause: {raw}"))
    return issues
```

Add a tiny auto-archive helper at `src/pipeline/archive.py`.

```python
# src/pipeline/archive.py
from __future__ import annotations

import shutil
from pathlib import Path


def auto_archive(path: Path, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    out = dest_dir / (path.name + ".zip")
    if out.exists():
        out.unlink()
    shutil.make_archive(str(out.with_suffix("")), "zip", path)
    return out
```

Wire the validator and archive in `src/pipeline/error_pipeline_service.py`
(insertions shown conceptually; adapt to real file once created):

```python
# Pseudocode for integration points
from src.plugins.spec_validator import validate as validate_spec
from src.pipeline.archive import auto_archive

def run_pipeline(units, max_workers=4):
    # Pre: validate specs (no-op if units are file paths)
    validation_issues = []
    for u in units:
        issues = validate_spec(u, ["WHEN user logs in THEN session exists"])  # replace with real clauses
        validation_issues.extend(issues)

    result = {"validation": [i.__dict__ for i in validation_issues]}

    # ... run stages as in Phase 11 ...
    out = {"state": "S_SUCCESS", **result}  # example

    # Auto-archive on success
    if out["state"] == "S_SUCCESS":
        auto_archive(Path("bundles"), Path("archives"))
    return out
```

## Tests

Create `tests/test_spec_validator.py`:

```python
# tests/test_spec_validator.py
from src.plugins.spec_validator import parse_when_then, validate


def test_parse_when_then():
    w, t = parse_when_then("WHEN A THEN B")
    assert w == "A" and t == "B"


def test_validate_flags_malformed():
    issues = validate("U1", ["WHEN only_when"])
    assert any(i.severity == "error" for i in issues)
```

## Dashboard integration

- Minimal approach: write JSON summary files per run under `artifacts/` and
  point a static dashboard (e.g., a local HTML) to poll and render them.
- Suggested fields: run id, timestamps, stage summaries, failed units.

## Multi-language plugin expansion

- Standardize the plugin envelope (stdin JSON in, stdout JSON out).
- Add simple adapters for Node.js and Shell to conform to the envelope.
- Coordinate via the existing `agent_coordinator` interface.

## Rollback plan

- Remove `src/plugins/spec_validator.py`, `src/pipeline/archive.py`, and any
  references added to the pipeline service.
- Delete generated archives under `archives/` if created.

