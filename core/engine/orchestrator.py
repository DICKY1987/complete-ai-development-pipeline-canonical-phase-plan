"""Orchestrator core loop (single workstream) for PH-05.

Implements EDIT -> STATIC -> RUNTIME sequencing for one workstream, recording
DB state transitions and step attempts. No FIX loop or retries in this phase.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
import os
from datetime import datetime
from typing import Any, Dict, List, Mapping, Optional

from core.state import db
from core.state import bundles
from core.state import worktree
from core.engine import tools
from core import prompts
from core.engine import circuit_breakers as cb

__all__ = [
    "STEP_EDIT",
    "STEP_STATIC",
    "STEP_RUNTIME",
    "StepResult",
    "run_edit_step",
    "run_static_step",
    "run_runtime_step",
    "run_workstream",
    "run_single_workstream_from_bundle",
]


# Step identifiers
STEP_EDIT = "edit"
STEP_STATIC = "static"
STEP_RUNTIME = "runtime"


@dataclass
class StepResult:
    step_name: str
    success: bool
    details: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


def _utc_now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def run_edit_step(run_id: str, ws_id: str, bundle_obj: Any, context: Mapping[str, Any]) -> StepResult:
    db.init_db()
    ws = db.get_workstream(ws_id)
    run = db.get_run(run_id)

    wt_path = worktree.create_worktree_for_ws(run_id, ws_id)
    ctx = dict(context)
    ctx.setdefault("worktree_path", wt_path)

    db.update_workstream_status(ws_id, "editing")
    db.record_event("step_start", run_id=run_id, ws_id=ws_id, payload={"step": STEP_EDIT})
    started = _utc_now()

    # Dry-run support: skip external tools
    dry_run = bool(ctx.get("dry_run") or (os.getenv("PIPELINE_DRY_RUN") == "1"))
    if dry_run:
        result_dict = {"tool": "aider", "dry_run": True}
        completed = _utc_now()
        db.record_step_attempt(run_id, ws_id, STEP_EDIT, "success", started_at=started, completed_at=completed, result=result_dict)
        db.record_event("step_end", run_id=run_id, ws_id=ws_id, payload={"step": STEP_EDIT, "success": True})
        db.update_workstream_status(ws_id, "ready_for_static")
        return StepResult(step_name=STEP_EDIT, success=True, details=result_dict)

    try:
        tr = prompts.run_aider_edit(run, ws, bundle_obj, ctx, run_id=run_id, ws_id=ws_id)
        success = bool(tr.success)
        result_dict = tr.to_dict()
    except Exception as e:  # pragma: no cover - safety
        success = False
        result_dict = {"exception": str(e)}

    completed = _utc_now()
    db.record_step_attempt(
        run_id,
        ws_id,
        STEP_EDIT,
        "success" if success else "failed",
        started_at=started,
        completed_at=completed,
        result=result_dict,
    )
    db.record_event("step_end", run_id=run_id, ws_id=ws_id, payload={"step": STEP_EDIT, "success": success})

    if success:
        db.update_workstream_status(ws_id, "ready_for_static")
        return StepResult(step_name=STEP_EDIT, success=True, details=result_dict)
    else:
        db.update_workstream_status(ws_id, "failed")
        return StepResult(step_name=STEP_EDIT, success=False, details=result_dict, error_message="edit step failed")


def run_static_step(run_id: str, ws_id: str, bundle_obj: Any, context: Mapping[str, Any]) -> StepResult:
    db.init_db()
    ctx = dict(context)
    started = _utc_now()
    db.update_workstream_status(ws_id, "static_check")
    db.record_event("step_start", run_id=run_id, ws_id=ws_id, payload={"step": STEP_STATIC})

    dry_run = bool(ctx.get("dry_run") or (os.getenv("PIPELINE_DRY_RUN") == "1"))
    tool_ids: List[str] = list(ctx.get("static_tools", []))

    if dry_run:
        completed = _utc_now()
        res = {"tools": tool_ids, "dry_run": True}
        db.record_step_attempt(run_id, ws_id, STEP_STATIC, "success", started_at=started, completed_at=completed, result=res)
        db.record_event("step_end", run_id=run_id, ws_id=ws_id, payload={"step": STEP_STATIC, "success": True})
        return StepResult(step_name=STEP_STATIC, success=True, details=res)

    # Default to a no-op static check if none configured
    success = True
    results: List[Dict[str, Any]] = []
    if tool_ids:
        for tid in tool_ids:
            tr = tools.run_tool(tid, {"repo_root": str(tools._get_repo_root())}, run_id=run_id, ws_id=ws_id)
            results.append(tr.to_dict())
            if not tr.success:
                success = False
                break

    completed = _utc_now()
    db.record_step_attempt(
        run_id,
        ws_id,
        STEP_STATIC,
        "success" if success else "failed",
        started_at=started,
        completed_at=completed,
        result={"results": results},
    )
    db.record_event("step_end", run_id=run_id, ws_id=ws_id, payload={"step": STEP_STATIC, "success": success})
    return StepResult(step_name=STEP_STATIC, success=success, details={"results": results}, error_message=None if success else "static step failed")


def run_runtime_step(run_id: str, ws_id: str, bundle_obj: Any, context: Mapping[str, Any]) -> StepResult:
    db.init_db()
    ctx = dict(context)
    started = _utc_now()
    db.update_workstream_status(ws_id, "runtime_tests")
    db.record_event("step_start", run_id=run_id, ws_id=ws_id, payload={"step": STEP_RUNTIME})

    dry_run = bool(ctx.get("dry_run") or (os.getenv("PIPELINE_DRY_RUN") == "1"))
    if dry_run:
        completed = _utc_now()
        res = {"acceptance_tests": list(getattr(bundle_obj, "acceptance_tests", [])), "dry_run": True}
        db.record_step_attempt(run_id, ws_id, STEP_RUNTIME, "success", started_at=started, completed_at=completed, result=res)
        db.record_event("step_end", run_id=run_id, ws_id=ws_id, payload={"step": STEP_RUNTIME, "success": True})
        return StepResult(step_name=STEP_RUNTIME, success=True, details=res)

    # For PH-05, run a single tool (configurable) or no-op if none
    runtime_tool = ctx.get("runtime_tool")  # e.g., "pytest"
    success = True
    result_detail: Dict[str, Any] = {}
    if runtime_tool:
        tr = tools.run_tool(runtime_tool, {"repo_root": str(tools._get_repo_root())}, run_id=run_id, ws_id=ws_id)
        result_detail = tr.to_dict()
        success = bool(tr.success)

    completed = _utc_now()
    db.record_step_attempt(
        run_id,
        ws_id,
        STEP_RUNTIME,
        "success" if success else "failed",
        started_at=started,
        completed_at=completed,
        result=result_detail,
    )
    db.record_event("step_end", run_id=run_id, ws_id=ws_id, payload={"step": STEP_RUNTIME, "success": success})
    return StepResult(step_name=STEP_RUNTIME, success=success, details=result_detail, error_message=None if success else "runtime step failed")


def _signature_from_tool_result(step: str, tr_dict: Dict[str, Any]) -> str:
    msg = str(tr_dict.get("stderr") or tr_dict.get("stdout") or "")
    return cb.compute_error_signature(step, msg)


def _diff_hash_from_tool_result(tr_dict: Dict[str, Any]) -> str:
    return cb.compute_diff_hash(tr_dict)


def run_static_with_fix(run_id: str, ws_id: str, bundle_obj: Any, context: Mapping[str, Any]) -> StepResult:
    """Run STATIC, attempt FIX retries via Aider on failure, respecting breakers."""
    cfg = cb.BreakerConfig.from_dict(cb.load_config())
    state = cb.FixLoopState()

    # Initial attempt
    res = run_static_step(run_id, ws_id, bundle_obj, context)
    state.step_attempts += 1
    if res.success:
        return res

    # Start FIX loop
    while cb.allow_fix_attempt(state, STEP_STATIC, cfg):
        # Record error signature and diff hash
        details_list = (res.details or {}).get("results", [])
        last = details_list[-1] if details_list else {}
        sig = _signature_from_tool_result(STEP_STATIC, last)
        h = _diff_hash_from_tool_result(last)
        state.signature_counts[sig] = state.signature_counts.get(sig, 0) + 1
        state.recent_diff_hashes.append(h)
        if cb.detect_oscillation(state, cfg):
            db.record_event("breaker_trip", run_id=run_id, ws_id=ws_id, payload={"reason": "oscillation", "step": STEP_STATIC})
            break

        # Record error row
        db.record_error(
            error_code="static_failure",
            signature=sig,
            message=last.get("stderr") or last.get("stdout") or "",
            run_id=run_id,
            ws_id=ws_id,
            step_name=STEP_STATIC,
            context=last,
        )

        # Attempt FIX via aider
        run_info = db.get_run(run_id)
        ws_info = db.get_workstream(ws_id)
        try:
            fix_result = prompts.run_aider_fix(run_info, ws_info, bundle_obj, errors=[last], context=context, run_id=run_id, ws_id=ws_id)
            db.record_event("fix_attempt", run_id=run_id, ws_id=ws_id, payload={"step": STEP_STATIC, "tool_result": fix_result.to_dict()})
        except Exception as e:  # pragma: no cover
            db.record_event("fix_attempt_error", run_id=run_id, ws_id=ws_id, payload={"step": STEP_STATIC, "error": str(e)})

        state.fix_attempts += 1

        # Re-run static after fix
        res = run_static_step(run_id, ws_id, bundle_obj, context)
        state.step_attempts += 1
        if res.success:
            return res

    # If we reach here, static remains failed
    return res


def run_runtime_with_fix(run_id: str, ws_id: str, bundle_obj: Any, context: Mapping[str, Any]) -> StepResult:
    cfg = cb.BreakerConfig.from_dict(cb.load_config())
    state = cb.FixLoopState()

    res = run_runtime_step(run_id, ws_id, bundle_obj, context)
    state.step_attempts += 1
    if res.success:
        return res

    while cb.allow_fix_attempt(state, STEP_RUNTIME, cfg):
        last = res.details or {}
        sig = _signature_from_tool_result(STEP_RUNTIME, last)
        h = _diff_hash_from_tool_result(last)
        state.signature_counts[sig] = state.signature_counts.get(sig, 0) + 1
        state.recent_diff_hashes.append(h)
        if cb.detect_oscillation(state, cfg):
            db.record_event("breaker_trip", run_id=run_id, ws_id=ws_id, payload={"reason": "oscillation", "step": STEP_RUNTIME})
            break

        db.record_error(
            error_code="runtime_failure",
            signature=sig,
            message=last.get("stderr") or last.get("stdout") or "",
            run_id=run_id,
            ws_id=ws_id,
            step_name=STEP_RUNTIME,
            context=last,
        )

        run_info = db.get_run(run_id)
        ws_info = db.get_workstream(ws_id)
        try:
            fix_result = prompts.run_aider_fix(run_info, ws_info, bundle_obj, errors=[last], context=context, run_id=run_id, ws_id=ws_id)
            db.record_event("fix_attempt", run_id=run_id, ws_id=ws_id, payload={"step": STEP_RUNTIME, "tool_result": fix_result.to_dict()})
        except Exception as e:  # pragma: no cover
            db.record_event("fix_attempt_error", run_id=run_id, ws_id=ws_id, payload={"step": STEP_RUNTIME, "error": str(e)})

        state.fix_attempts += 1

        res = run_runtime_step(run_id, ws_id, bundle_obj, context)
        state.step_attempts += 1
        if res.success:
            return res

    return res


def run_workstream(run_id: str, ws_id: str, bundle_obj: bundles.WorkstreamBundle, context: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    """Run EDIT -> STATIC -> RUNTIME for a single workstream and record results.

    Returns a summary dictionary suitable for JSON serialization.
    """
    ctx = dict(context or {})
    db.init_db()

    # Ensure run and workstream exist
    try:
        db.get_run(run_id)
    except Exception:
        db.create_run(run_id, status="in_progress")

    try:
        db.get_workstream(ws_id)
    except Exception:
        db.create_workstream(ws_id=ws_id, run_id=run_id, status="pending", metadata={
            "bundle_id": bundle_obj.id,
            "files_scope": list(bundle_obj.files_scope),
            "acceptance_tests": list(bundle_obj.acceptance_tests),
        })

    db.update_workstream_status(ws_id, "started")
    db.record_event("workstream_start", run_id=run_id, ws_id=ws_id, payload={"bundle_id": bundle_obj.id})

    # Optional: GitHub issue update (CCPM integration)
    def _post(step: str, final_status: Optional[str] = None) -> None:
        try:
            from src.integrations import github_sync  # type: ignore

            issue = getattr(bundle_obj, "ccpm_issue", None)
            if issue is None:
                return
            ev = github_sync.LifecycleEvent(run_id=run_id, ws_id=ws_id, step=step, final_status=final_status)
            github_sync.post_lifecycle_comment(issue, ev)
        except Exception:
            # Best-effort only; never block orchestrator
            pass

    _post("workstream_start")

    # EDIT
    _post("edit_start")
    res_edit = run_edit_step(run_id, ws_id, bundle_obj, ctx)
    _post("edit_end")
    if not res_edit.success:
        final_status = "failed"
        db.update_workstream_status(ws_id, final_status)
        db.record_event("workstream_end", run_id=run_id, ws_id=ws_id, payload={"final_status": final_status})
        _post("workstream_end", final_status)
        return {
            "run_id": run_id,
            "ws_id": ws_id,
            "final_status": final_status,
            "steps": [asdict(res_edit)],
        }

    # STATIC (with FIX loop)
    _post("static_start")
    res_static = run_static_with_fix(run_id, ws_id, bundle_obj, ctx)
    _post("static_end")
    # Post a brief static summary (best-effort)
    try:
        from src.integrations import github_sync  # type: ignore

        issue = getattr(bundle_obj, "ccpm_issue", None)
        details = res_static.details or {}
        tools = []
        if isinstance(details, dict):
            tools = list(details.get("tools", [])) or []
            if not tools and isinstance(details.get("results"), list):
                tools = [str(i) for i in range(len(details["results"]))]
        github_sync.comment(issue, f"WS {ws_id} static summary: success={res_static.success} tools={len(tools)}")
    except Exception:
        pass
    if not res_static.success:
        final_status = "failed"
        db.update_workstream_status(ws_id, final_status)
        db.record_event("workstream_end", run_id=run_id, ws_id=ws_id, payload={"final_status": final_status})
        _post("workstream_end", final_status)
        return {
            "run_id": run_id,
            "ws_id": ws_id,
            "final_status": final_status,
            "steps": [asdict(res_edit), asdict(res_static)],
        }

    # RUNTIME (with FIX loop)
    _post("runtime_start")
    res_runtime = run_runtime_with_fix(run_id, ws_id, bundle_obj, ctx)
    _post("runtime_end")
    # Post a brief runtime summary (best-effort)
    try:
        from src.integrations import github_sync  # type: ignore

        issue = getattr(bundle_obj, "ccpm_issue", None)
        details = res_runtime.details or {}
        total = passed = failed = 0
        if isinstance(details, dict) and isinstance(details.get("summary"), dict):
            s = details["summary"]
            total = int(s.get("total_tests", 0) or 0)
            passed = int(s.get("passed", 0) or 0)
            failed = int(s.get("failed", 0) or 0)
        github_sync.comment(issue, f"WS {ws_id} runtime summary: success={res_runtime.success} total={total} passed={passed} failed={failed}")
    except Exception:
        pass
    if not res_runtime.success:
        final_status = "failed"
        db.update_workstream_status(ws_id, final_status)
        db.record_event("workstream_end", run_id=run_id, ws_id=ws_id, payload={"final_status": final_status})
        _post("workstream_end", final_status)
        return {
            "run_id": run_id,
            "ws_id": ws_id,
            "final_status": final_status,
            "steps": [asdict(res_edit), asdict(res_static), asdict(res_runtime)],
        }

    # Scope validation
    ok, out_of_scope = worktree.validate_scope(ctx.get("worktree_path") or worktree.get_worktree_path(ws_id), bundle_obj.files_scope)
    if not ok:
        db.record_event("scope_violation", run_id=run_id, ws_id=ws_id, payload={"out_of_scope_files": out_of_scope})
        final_status = "failed"
        db.update_workstream_status(ws_id, final_status)
        db.record_event("workstream_end", run_id=run_id, ws_id=ws_id, payload={"final_status": final_status})
        return {
            "run_id": run_id,
            "ws_id": ws_id,
            "final_status": final_status,
            "steps": [asdict(res_edit), asdict(res_static), asdict(res_runtime)],
        }

    final_status = "done"
    db.update_workstream_status(ws_id, final_status)
    db.record_event("workstream_end", run_id=run_id, ws_id=ws_id, payload={"final_status": final_status})
    _post("workstream_end", final_status)
    return {
        "run_id": run_id,
        "ws_id": ws_id,
        "final_status": final_status,
        "steps": [asdict(res_edit), asdict(res_static), asdict(res_runtime)],
    }


def run_single_workstream_from_bundle(ws_id: str, run_id: Optional[str] = None, context: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    """Load bundles, find ws_id, and run orchestrator for one workstream."""
    items = bundles.load_and_validate_bundles()
    bundle_obj = next((b for b in items if b.id == ws_id), None)
    if bundle_obj is None:
        raise ValueError(f"Workstream '{ws_id}' not found in bundles directory")

    rid = run_id or ("run-" + datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"))
    return run_workstream(rid, ws_id, bundle_obj, context=context)
