from __future__ import annotations

import json
import re
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .openspec_parser import OpenSpecBundle, load_bundle_from_change, discover_specs, load_bundle_from_yaml
from . import bundles as ws_bundles


_PATH_TOKEN = re.compile(r"(?P<path>(?:[A-Za-z]:/)?[A-Za-z0-9_./\\-]+\.[A-Za-z0-9_]+)")


def _extract_paths_from_tasks(tasks: Iterable[str]) -> List[str]:
    paths: List[str] = []
    for t in tasks:
        for m in _PATH_TOKEN.finditer(t):
            p = m.group("path").replace("\\", "/")
            # keep only repo-relative-looking paths
            if "/" in p and not p.startswith("http"):
                paths.append(p.lstrip("/"))
    # de-dup, preserve order
    seen = set()
    out: List[str] = []
    for p in paths:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def bundle_to_workstream(
    bundle: OpenSpecBundle,
    *,
    change_id: Optional[str] = None,
    files_scope: Optional[List[str]] = None,
    tool: str = "aider",
    gate: int = 1,
    ccpm_issue: str | int = "TBD",
) -> Dict[str, Any]:
    """Map an OpenSpecBundle into a single workstream JSON object.

    This converter uses conservative defaults and allows overriding critical
    fields like files_scope/tool/gate/ccpm_issue via parameters.
    """
    cid = change_id or bundle.bundle_id.replace("openspec-", "")

    # Collect tasks from item titles that look like tasks (exclude the synthetic change item id)
    tasks: List[str] = []
    for it in bundle.items:
        # skip the synthetic change item created by openspec_parser load_bundle_from_change
        if it.id.startswith("T-") or (it.id and it.id.lower().startswith("task")):
            tasks.append(it.title.strip() or it.id)

    # acceptance criteria from when-then
    acceptance: List[str] = []
    for it in bundle.items:
        for wt in it.when_then:
            acceptance.append(f"WHEN {wt.when} THEN {wt.then}")

    inferred_scope = _extract_paths_from_tasks(tasks)
    scope = files_scope if files_scope else inferred_scope
    if not scope:
        raise ValueError(
            f"No file paths could be inferred from tasks in bundle {bundle.bundle_id}. "
            "Provide explicit --files-scope or add file paths to task descriptions."
        )

    ws: Dict[str, Any] = {
        "id": f"ws-{cid}",
        "openspec_change": cid,
        "ccpm_issue": ccpm_issue,
        "gate": int(gate),
        "files_scope": scope,
        "files_create": [],
        "tasks": tasks,
        "acceptance_tests": acceptance,
        "depends_on": [],
        "tool": tool,
        "metadata": {"source_bundle": bundle.bundle_id},
    }

    # Validate against schema via existing pipeline module to ensure compatibility
    schema = None
    try:
        # internal function pulls schema from repo
        schema = None
        ws_bundles.validate_bundle_data(ws, schema=schema)
    except Exception as e:
        # re-raise with context
        raise ValueError(f"Generated workstream failed validation: {e}") from e
    return ws


def load_bundles_from_input(
    *, change_id: Optional[str] = None, input_path: Optional[Path] = None
) -> List[OpenSpecBundle]:
    if change_id:
        return [load_bundle_from_change(change_id)]
    if input_path is None:
        raise ValueError("Either change_id or input_path is required")
    if input_path.is_file():
        return [load_bundle_from_yaml(input_path)]
    return discover_specs(input_path)

