"""
Compatibility shim: re-export prompt engine from aider.engine

Provides compatibility wrappers for the orchestrator which expects the old signature.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
import os
from datetime import datetime

import aider.engine as engine
from core.engine.tools import ToolResult, _get_repo_root

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
    (cwd, files, tasks, repo_root, ws_id, ...).
    """
    cwd = Path(context.get("worktree_path", "."))
    files = list(getattr(bundle_obj, 'files_scope', []))
    files_create = list(getattr(bundle_obj, 'files_create', []))
    tasks = list(getattr(bundle_obj, 'tasks', []))
    acceptance_tests = list(getattr(bundle_obj, 'acceptance_tests', []))
    repo_root = _get_repo_root()
    timeout = context.get("timeout_seconds", 300)

    # Extract metadata from bundle
    openspec_change = getattr(bundle_obj, "openspec_change", "")
    ccpm_issue = getattr(bundle_obj, "ccpm_issue", "")
    gate = getattr(bundle_obj, "gate", "")

    # Session override: disable external Aider and let Codex edit
    if os.getenv("PIPELINE_DISABLE_AIDER") == "1":
        now = datetime.utcnow().isoformat() + "Z"
        return ToolResult(
            tool_id="codex",
            command_line="codex-session (aider disabled)",
            exit_code=0,
            stdout="Aider disabled via PIPELINE_DISABLE_AIDER=1; edits handled by Codex",
            stderr="",
            timed_out=False,
            started_at=now,
            completed_at=now,
            duration_sec=0.0,
            success=True,
        )

    return engine.run_aider_edit(
        cwd=cwd,
        files=files,
        tasks=tasks,
        repo_root=repo_root,
        ws_id=ws_id,
        run_id=run_id,
        files_create=files_create,
        acceptance_tests=acceptance_tests,
        openspec_change=openspec_change,
        ccpm_issue=ccpm_issue,
        gate=gate,
        timeout_seconds=timeout,
        **kwargs
    )


def run_aider_fix(
    run: Any,
    ws: Any,
    bundle_obj: Any,
    errors: list[dict[str, Any]] | list[Any] | None = None,
    context: Mapping[str, Any] | None = None,
    run_id: str = "",
    ws_id: str = "",
    **kwargs: Any
) -> ToolResult:
    """Compatibility wrapper for orchestrator fix loop.

    Translates old signature to new signature.
    """
    context = context or {}
    cwd = Path(context.get("worktree_path", "."))
    files = list(getattr(bundle_obj, 'files_scope', []))
    files_create = list(getattr(bundle_obj, 'files_create', []))
    repo_root = _get_repo_root()
    timeout = context.get("timeout_seconds", 300)

    # Extract metadata from bundle (consistent with run_aider_edit)
    openspec_change = getattr(bundle_obj, "openspec_change", "")
    ccpm_issue = getattr(bundle_obj, "ccpm_issue", "")
    gate = getattr(bundle_obj, "gate", "")

    # Session override: disable external Aider fix attempts
    if os.getenv("PIPELINE_DISABLE_AIDER") == "1":
        now = datetime.utcnow().isoformat() + "Z"
        return ToolResult(
            tool_id="codex",
            command_line="codex-session fix (aider disabled)",
            exit_code=0,
            stdout="Aider fix disabled via PIPELINE_DISABLE_AIDER=1; manual follow-up required",
            stderr="",
            timed_out=False,
            started_at=now,
            completed_at=now,
            duration_sec=0.0,
            success=True,
        )

    # Collate error summary/details if provided
    error_summary = ""
    error_details = ""
    if errors:
        try:
            last = errors[-1] if isinstance(errors, list) else {}
            error_summary = str(getattr(last, 'summary', '') or last.get('summary') or '')
            error_details = str(getattr(last, 'stderr', '') or last.get('stderr') or getattr(last, 'stdout', '') or last.get('stdout') or '')
        except Exception:
            error_summary = ""
            error_details = ""

    return engine.run_aider_fix(
        cwd=cwd,
        files=files,
        error_summary=error_summary,
        error_details=error_details,
        repo_root=repo_root,
        ws_id=ws_id,
        run_id=run_id,
        files_create=files_create,
        openspec_change=openspec_change,
        ccpm_issue=ccpm_issue,
        gate=gate,
        timeout_seconds=timeout,
        **kwargs
    )
