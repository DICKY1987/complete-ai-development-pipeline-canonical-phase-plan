"""
Compatibility shim: re-export prompt engine from aider.engine

Provides compatibility wrappers for the orchestrator which expects the old signature.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import aider.engine as engine
from .tools import ToolResult, _get_repo_root

# Re-export for direct imports
TemplateRender = engine.TemplateRender


def run_aider_edit(
    run: Any,  # DB row or dict for run
    ws: Any,  # DB row or dict for workstream
    bundle_obj: Any,  # WorkstreamBundle instance
    context: Mapping[str, Any],
    run_id: str,
    ws_id: str,
    **kwargs: Any
) -> ToolResult:
    """Compatibility wrapper for orchestrator.

    Translates old signature (run, ws, bundle, context) to new signature
    (cwd, files, tasks, repo_root, ws_id).
    """
    cwd = Path(context.get("worktree_path", "."))
    files = list(bundle_obj.files_scope) if hasattr(bundle_obj, "files_scope") else []
    tasks = list(bundle_obj.tasks) if hasattr(bundle_obj, "tasks") else []
    repo_root = _get_repo_root()
    timeout = context.get("timeout_seconds", 300)

    return engine.run_aider_edit(
        cwd=cwd,
        files=files,
        tasks=tasks,
        repo_root=repo_root,
        ws_id=ws_id,
        timeout_seconds=timeout,
        **kwargs
    )


def run_aider_fix(
    run: Any,
    ws: Any,
    bundle_obj: Any,
    error_summary: str,
    error_details: str,
    context: Mapping[str, Any],
    run_id: str,
    ws_id: str,
    **kwargs: Any
) -> ToolResult:
    """Compatibility wrapper for orchestrator.

    Translates old signature to new signature.
    """
    cwd = Path(context.get("worktree_path", "."))
    files = list(bundle_obj.files_scope) if hasattr(bundle_obj, "files_scope") else []
    repo_root = _get_repo_root()
    timeout = context.get("timeout_seconds", 300)

    return engine.run_aider_fix(
        cwd=cwd,
        files=files,
        error_summary=error_summary,
        error_details=error_details,
        repo_root=repo_root,
        ws_id=ws_id,
        timeout_seconds=timeout,
        **kwargs
    )
