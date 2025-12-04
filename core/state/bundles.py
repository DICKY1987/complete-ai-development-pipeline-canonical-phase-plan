"""Workstream bundle loading and validation.

This module turns JSON workstream bundle files into validated, in-memory
structures ready for orchestration. It provides:

- Directory resolution with `PIPELINE_WORKSTREAM_DIR` override
- JSON loading for bundle files (single object or list of objects)
- Schema validation (via `jsonschema` if available; strict manual fallback)
- Dependency graph building and cycle detection
- File-scope overlap detection
- Optional DB sync of validated bundles to the `workstreams` table
"""
# DOC_ID: DOC-CORE-STATE-BUNDLES-168

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Tuple

try:
    import jsonschema  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    jsonschema = None  # type: ignore

__all__ = [
    "WorkstreamBundle",
    "BundleValidationError",
    "BundleDependencyError",
    "BundleCycleError",
    "FileScopeOverlapError",
    "get_workstream_dir",
    "load_bundle_file",
    "validate_bundle_data",
    "load_and_validate_bundles",
    "build_dependency_graph",
    "detect_cycles",
    "detect_filescope_overlaps",
    "sync_bundles_to_db",
]


# ============================
# Data structures & exceptions
# ============================


@dataclass(frozen=True)
class WorkstreamBundle:
    id: str
    openspec_change: str
    ccpm_issue: str | int
    gate: int
    files_scope: Tuple[str, ...]
    files_create: Tuple[str, ...] = field(default_factory=tuple)
    tasks: Tuple[str, ...] = field(default_factory=tuple)
    acceptance_tests: Tuple[str, ...] = field(default_factory=tuple)
    depends_on: Tuple[str, ...] = field(default_factory=tuple)
    tool: str = ""
    circuit_breaker: Mapping[str, Any] | None = None
    metadata: Mapping[str, Any] | None = None
    __source_file__: str | None = None  # for error context
    # UET Phase H additions (all optional for backward compatibility)
    parallel_ok: bool = True
    conflict_group: str | None = None
    kind: str = "impl"
    priority: str = "foreground"
    estimated_context_tokens: int | None = None
    max_cost_usd: float | None = None
    compensation_actions: Tuple[str, ...] = field(default_factory=tuple)
    test_gates: Tuple[Mapping[str, Any], ...] = field(default_factory=tuple)


class BundleValidationError(ValueError):
    pass


class BundleDependencyError(ValueError):
    pass


class BundleCycleError(ValueError):
    pass


class FileScopeOverlapError(ValueError):
    pass


# ==============
# Helper methods
# ==============


_WS_ID_RE = re.compile(r"^ws-[a-z0-9-]+$")


def _detect_repo_root(start: Optional[Path] = None) -> Path:
    base = (start or Path.cwd()).resolve()
    cur = base
    for _ in range(10):
        if (cur / ".git").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return base


def _load_schema(repo_root: Path) -> Dict[str, Any]:
    schema_path = repo_root / "schema" / "workstream.schema.json"
    if not schema_path.exists():
        raise BundleValidationError(
            f"Schema not found: {schema_path}. Ensure PH-04 added the JSON Schema."
        )
    try:
        return json.loads(schema_path.read_text(encoding="utf-8"))
    except Exception as e:  # pragma: no cover
        raise BundleValidationError(f"Failed reading schema {schema_path}: {e}")


def _ensure_str_list(value: Any, field: str, *, allow_empty: bool = True) -> Tuple[str, ...]:
    if not isinstance(value, list) or any(not isinstance(x, str) for x in value):
        raise BundleValidationError(f"Field '{field}' must be an array of strings")
    if not allow_empty and len(value) == 0:
        raise BundleValidationError(f"Field '{field}' must not be empty")
    return tuple(value)


def _normalize_path(p: str) -> str:
    # Normalize to POSIX-like with forward slashes; treat paths as relative strings.
    return p.replace("\\", "/").strip("/")


# =========================
# Public API implementation
# =========================


def get_workstream_dir() -> Path:
    """Resolve the directory to load workstream bundles from.

    Priority:
    1) PIPELINE_WORKSTREAM_DIR environment variable
    2) <repo_root>/workstreams
    """
    override = os.getenv("PIPELINE_WORKSTREAM_DIR")
    if override:
        p = Path(override).expanduser().resolve()
    else:
        repo_root = _detect_repo_root()
        p = (repo_root / "workstreams").resolve()
    if not p.exists() or not p.is_dir():
        raise FileNotFoundError(f"Workstream directory not found: {p}")
    return p


def load_bundle_file(path: Path) -> Dict[str, Any] | List[Dict[str, Any]]:
    """Load JSON content from a file.

    Supports a single bundle object or a list of bundles.
    """
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise BundleValidationError(f"Invalid JSON in {path}: {e}")
    if isinstance(data, dict):
        return data
    if isinstance(data, list):
        if not all(isinstance(x, dict) for x in data):
            raise BundleValidationError(
                f"Top-level array in {path} must contain objects only"
            )
        return data  # type: ignore[return-value]
    raise BundleValidationError(f"Top-level JSON must be object or array in {path}")


def validate_bundle_data(data: Dict[str, Any], *, schema: Optional[Dict[str, Any]] = None, source_file: Optional[Path] = None) -> WorkstreamBundle:
    """Validate a single bundle dict against the workstream schema.

    If `jsonschema` is installed, use it; otherwise, enforce equivalent checks
    manually (required fields, types, patterns, and strict unknown-field policy).
    Returns a normalized `WorkstreamBundle`.
    """
    repo_root = _detect_repo_root()
    if schema is None:
        schema = _load_schema(repo_root)

    # Strict unknown field policy by default
    allowed_fields = set(schema.get("properties", {}).keys())
    unknown = [k for k in data.keys() if k not in allowed_fields]
    if not schema.get("additionalProperties", True) and unknown:
        raise BundleValidationError(
            f"Unknown field(s) in bundle {data.get('id', '<no-id>')}: {', '.join(sorted(unknown))}"
        )

    if jsonschema is not None:  # pragma: no branch
        try:
            jsonschema.validate(instance=data, schema=schema)  # type: ignore
        except Exception as e:
            location = f" ({source_file})" if source_file else ""
            raise BundleValidationError(
                f"Schema validation failed for id={data.get('id','<no-id>')}{location}: {e}"
            )
    else:
        # Manual enforcement (subset sufficient for this project)
        required = set(schema.get("required", []))
        missing = [k for k in required if k not in data]
        if missing:
            raise BundleValidationError(
                f"Missing required field(s) for id={data.get('id','<no-id>')}: {', '.join(sorted(missing))}"
            )
        # Types and constraints
        ws_id = data.get("id")
        if not isinstance(ws_id, str) or not _WS_ID_RE.match(ws_id):
            raise BundleValidationError("Field 'id' must match ^ws-[a-z0-9-]+$")
        if not isinstance(data.get("openspec_change"), str):
            raise BundleValidationError("Field 'openspec_change' must be a string")
        ccpm_issue = data.get("ccpm_issue")
        if not (isinstance(ccpm_issue, (str, int))):
            raise BundleValidationError("Field 'ccpm_issue' must be string or integer")
        gate = data.get("gate")
        if not (isinstance(gate, int) and gate >= 1):
            raise BundleValidationError("Field 'gate' must be an integer >= 1")
        files_scope = _ensure_str_list(data.get("files_scope"), "files_scope", allow_empty=False)
        files_create = _ensure_str_list(data.get("files_create", []), "files_create")
        tasks = _ensure_str_list(data.get("tasks"), "tasks")
        acceptance_tests = _ensure_str_list(data.get("acceptance_tests", []), "acceptance_tests")
        depends_on = _ensure_str_list(data.get("depends_on", []), "depends_on")
        tool = data.get("tool")
        if not isinstance(tool, str) or not tool:
            raise BundleValidationError("Field 'tool' must be a non-empty string")
        circuit_breaker = data.get("circuit_breaker")
        if circuit_breaker is not None and not isinstance(circuit_breaker, dict):
            raise BundleValidationError("Field 'circuit_breaker' must be an object if present")
        metadata = data.get("metadata")
        if metadata is not None and not isinstance(metadata, dict):
            raise BundleValidationError("Field 'metadata' must be an object if present")

        # Build WorkstreamBundle (normalized paths)
        return WorkstreamBundle(
            id=ws_id,
            openspec_change=data["openspec_change"],
            ccpm_issue=ccpm_issue,  # type: ignore[arg-type]
            gate=gate,
            files_scope=tuple(_normalize_path(p) for p in files_scope),
            files_create=tuple(_normalize_path(p) for p in files_create),
            tasks=tasks,
            acceptance_tests=acceptance_tests,
            depends_on=depends_on,
            tool=tool,
            circuit_breaker=circuit_breaker,
            metadata=metadata,
            __source_file__=str(source_file) if source_file else None,
            # UET fields (optional, with defaults)
            parallel_ok=data.get("parallel_ok", True),
            conflict_group=data.get("conflict_group"),
            kind=data.get("kind", "impl"),
            priority=data.get("priority", "foreground"),
            estimated_context_tokens=data.get("estimated_context_tokens"),
            max_cost_usd=data.get("max_cost_usd"),
            compensation_actions=tuple(data.get("compensation_actions", [])),
            test_gates=tuple(data.get("test_gates", [])),
        )

    # When jsonschema validated successfully, still normalize into dataclass
    return WorkstreamBundle(
        id=data["id"],
        openspec_change=data["openspec_change"],
        ccpm_issue=data["ccpm_issue"],
        gate=data["gate"],
        files_scope=tuple(_normalize_path(p) for p in data.get("files_scope", [])),
        files_create=tuple(_normalize_path(p) for p in data.get("files_create", [])),
        tasks=tuple(data.get("tasks", [])),
        acceptance_tests=tuple(data.get("acceptance_tests", [])),
        depends_on=tuple(data.get("depends_on", [])),
        tool=data.get("tool", ""),
        circuit_breaker=data.get("circuit_breaker"),
        metadata=data.get("metadata"),
        __source_file__=str(source_file) if source_file else None,
        # UET fields (optional, with defaults)
        parallel_ok=data.get("parallel_ok", True),
        conflict_group=data.get("conflict_group"),
        kind=data.get("kind", "impl"),
        priority=data.get("priority", "foreground"),
        estimated_context_tokens=data.get("estimated_context_tokens"),
        max_cost_usd=data.get("max_cost_usd"),
        compensation_actions=tuple(data.get("compensation_actions", [])),
        test_gates=tuple(data.get("test_gates", [])),
    )


def load_and_validate_bundles(workstream_dir: Optional[Path] = None) -> List[WorkstreamBundle]:
    """Load and validate all bundles from the specified or default workstream directory.

    - Supports per-file single object or list-of-objects format.
    - Enforces unique ids.
    - Enforces valid depends_on references.
    - Detects and raises on cycles.
    - Returns list sorted by id for determinism.
    """
    if workstream_dir is None:
        ws_dir = get_workstream_dir()
    else:
        ws_dir = workstream_dir

    repo_root = _detect_repo_root()
    schema = _load_schema(repo_root)

    bundles: List[WorkstreamBundle] = []
    for path in sorted(ws_dir.glob("*.json")):
        payload = load_bundle_file(path)
        items: List[Dict[str, Any]]
        if isinstance(payload, list):
            items = payload
        else:
            items = [payload]
        for obj in items:
            b = validate_bundle_data(obj, schema=schema, source_file=path)
            bundles.append(b)

    # Unique ids
    seen: Dict[str, str] = {}
    for b in bundles:
        if b.id in seen:
            raise BundleValidationError(
                f"Duplicate bundle id '{b.id}' in {b.__source_file__} and {seen[b.id]}"
            )
        seen[b.id] = b.__source_file__ or "<unknown>"

    # Dependency references
    ids = {b.id for b in bundles}
    missing_refs: Dict[str, List[str]] = {}
    for b in bundles:
        missing = [d for d in b.depends_on if d not in ids]
        if missing:
            missing_refs[b.id] = missing
    if missing_refs:
        details = "; ".join(f"{k} -> {', '.join(v)}" for k, v in sorted(missing_refs.items()))
        raise BundleDependencyError(f"Missing dependency references: {details}")

    # Cycles
    graph, _ = build_dependency_graph(bundles)
    cycles = detect_cycles(graph)
    if cycles:
        formatted = "; ".join(" -> ".join(c) for c in cycles)
        raise BundleCycleError(f"Dependency cycle(s) detected: {formatted}")

    return sorted(bundles, key=lambda b: b.id)


def build_dependency_graph(bundles: Sequence[WorkstreamBundle]) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """Build adjacency (children) and reverse (parents) graphs.

    - children[id] = list of nodes that depend on id
    - parents[id] = list of nodes that id depends on (prereqs)
    """
    children: Dict[str, List[str]] = {b.id: [] for b in bundles}
    parents: Dict[str, List[str]] = {b.id: list(b.depends_on) for b in bundles}

    # For each dependency edge A(depends on B): add child edge B -> A
    for b in bundles:
        for p in b.depends_on:
            if p in children:
                children[p].append(b.id)
    # Deterministic ordering
    for k in children:
        children[k].sort()
    for k in parents:
        parents[k].sort()
    return children, parents


def detect_cycles(graph: Mapping[str, List[str]]) -> List[List[str]]:
    """Detect cycles in a directed graph using DFS.

    Returns a list of cycles; each is a list of node ids in order.
    """
    visited: Dict[str, int] = {}
    stack: List[str] = []
    cycles: List[List[str]] = []

    def dfs(node: str) -> None:
        state = visited.get(node, 0)
        if state == 1:
            # Found a back-edge; extract cycle from stack
            if node in stack:
                idx = stack.index(node)
                cycles.append(stack[idx:] + [node])
            return
        if state == 2:
            return
        visited[node] = 1
        stack.append(node)
        for nxt in graph.get(node, []):
            dfs(nxt)
        stack.pop()
        visited[node] = 2

    for n in sorted(graph.keys()):
        if visited.get(n, 0) == 0:
            dfs(n)

    # Normalize cycle representation (start at lowest id)
    norm_cycles: List[List[str]] = []
    for cyc in cycles:
        if len(cyc) >= 2 and cyc[0] == cyc[-1]:
            body = cyc[:-1]
        else:
            body = cyc
        if not body:
            continue
        # rotate to smallest lexicographic start
        min_idx = min(range(len(body)), key=lambda i: body[i])
        ordered = body[min_idx:] + body[:min_idx]
        norm_cycles.append(ordered)
    # Deduplicate
    seen: set[Tuple[str, ...]] = set()
    unique: List[List[str]] = []
    for c in norm_cycles:
        t = tuple(c)
        if t not in seen:
            seen.add(t)
            unique.append(c)
    return unique


def detect_filescope_overlaps(bundles: Sequence[WorkstreamBundle]) -> Dict[str, List[str]]:
    """Return mapping file_path -> [workstream ids] for overlaps (>1 owner)."""
    owners: Dict[str, List[str]] = {}
    for b in bundles:
        for f in b.files_scope:
            key = _normalize_path(f)
            owners.setdefault(key, []).append(b.id)
    return {k: sorted(v) for k, v in owners.items() if len(v) > 1}


def sync_bundles_to_db(run_id: str, bundles: Sequence[WorkstreamBundle]) -> None:
    """Insert validated bundles into the DB as workstreams for a run.

    - Sets status to "pending".
    - Stores depends_on as JSON in the `depends_on` TEXT column.
    - Stores metadata (if provided) in `metadata_json`.
    """
    from . import db  # local import to avoid hard dependency at import time

    # Ensure DB exists
    db.init_db()

    for b in bundles:
        try:
            db.create_workstream(
                ws_id=b.id,
                run_id=run_id,
                status="pending",
                depends_on=json.dumps(list(b.depends_on)) if b.depends_on else None,
                metadata={
                    "openspec_change": b.openspec_change,
                    "ccpm_issue": b.ccpm_issue,
                    "gate": b.gate,
                    "files_scope": list(b.files_scope),
                    "files_create": list(b.files_create),
                    "tasks": list(b.tasks),
                    "acceptance_tests": list(b.acceptance_tests),
                    "tool": b.tool,
                    "circuit_breaker": b.circuit_breaker,
                    "metadata": b.metadata,
                },
            )
        except Exception as e:  # pragma: no cover - DB errors exercised elsewhere
            raise BundleDependencyError(f"Failed to sync workstream {b.id} to DB: {e}")

