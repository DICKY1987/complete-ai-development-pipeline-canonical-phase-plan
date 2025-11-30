# DOC_LINK: DOC-CORE-CORE-OPENSPEC-CONVERT-045
# DOC_LINK: DOC-CORE-CORE-OPENSPEC-CONVERT-022
from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Sequence

from core.openspec_parser import OpenSpecBundle


def bundle_to_workstream(
    bundle: OpenSpecBundle,
    *,
    change_id: str,
    files_scope: Sequence[str],
    tool: str,
    gate: int,
    ccpm_issue: str | int,
    metadata: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    tasks = [
        item.title or item.id
        for item in bundle.items
        if not item.id.startswith("CH-")
    ]
    if not tasks:
        tasks = ["auto-generated"]

    return {
        "id": f"ws-{change_id}",
        "openspec_change": change_id,
        "ccpm_issue": ccpm_issue,
        "gate": gate,
        "files_scope": list(files_scope),
        "files_create": [],
        "tasks": tasks,
        "acceptance_tests": [],
        "depends_on": [],
        "tool": tool,
        "metadata": dict(metadata or bundle.metadata),
    }


__all__ = ["bundle_to_workstream"]

