from __future__ import annotations

from typing import Callable, Dict, Any

from .error_context import ErrorPipelineContext
from .error_state_machine import (
    advance_state,
    S_INIT,
    S0_BASELINE_CHECK,
    S0_MECHANICAL_AUTOFIX,
    S0_MECHANICAL_RECHECK,
    S1_AIDER_FIX,
    S1_AIDER_RECHECK,
    S2_CODEX_FIX,
    S2_CODEX_RECHECK,
    S3_CLAUDE_FIX,
    S3_CLAUDE_RECHECK,
    S_SUCCESS,
    S4_QUARANTINE,
)
from . import db
from .error_engine import run_error_pipeline


def tick(ctx: ErrorPipelineContext) -> ErrorPipelineContext:
    """Advance the pipeline by one step, performing side effects when needed.

    Returns the updated context.
    """
    # First, advance out of S_INIT into baseline
    if ctx.current_state == S_INIT:
        advance_state(ctx)
        db.save_error_context(ctx)
        return ctx

    if ctx.current_state == S0_BASELINE_CHECK:
        report = run_error_pipeline(ctx.python_files, ctx.powershell_files, ctx)
        ctx.update_error_reports(report)
        db.record_error_report(ctx, report, step_name="error_pipeline_baseline")
        advance_state(ctx)
        db.save_error_context(ctx)
        return ctx

    if ctx.current_state == S0_MECHANICAL_AUTOFIX:
        # Perform mechanical autofix: run the pipeline with fix-capable plugins (e.g., black)
        report = run_error_pipeline(ctx.python_files, ctx.powershell_files, ctx)
        ctx.update_error_reports(report)
        # Update working set to the newly produced outputs so recheck analyzes fixed files
        outs = report.get("outputs", [])
        new_py = [o["output"] for o in outs if o.get("output", "").endswith(".py")]
        if new_py:
            ctx.python_files = new_py
        db.record_error_report(ctx, report, step_name="mechanical_autofix")
        advance_state(ctx)
        db.save_error_context(ctx)
        return ctx

    if ctx.current_state == S0_MECHANICAL_RECHECK:
        report = run_error_pipeline(ctx.python_files, ctx.powershell_files, ctx)
        ctx.update_error_reports(report)
        db.record_error_report(ctx, report, step_name="error_pipeline_recheck")
        advance_state(ctx)
        db.save_error_context(ctx)
        return ctx

    if ctx.current_state == S1_AIDER_FIX:
        ctx.record_ai_attempt({
            "attempt_number": ctx.attempt_number,
            "agent": "aider",
            "input_error_report_id": f"error_report_attempt_{ctx.attempt_number-1}.json",
            "changed_files": [],
            "notes": "Placeholder Aider fix not implemented; proceed to recheck.",
        })
        advance_state(ctx)
        db.save_error_context(ctx)
        return ctx

    if ctx.current_state == S1_AIDER_RECHECK:
        report = run_error_pipeline(ctx.python_files, ctx.powershell_files, ctx)
        ctx.update_error_reports(report)
        db.record_error_report(ctx, report, step_name="error_pipeline_recheck")
        advance_state(ctx)
        db.save_error_context(ctx)
        return ctx

    if ctx.current_state == S2_CODEX_FIX:
        ctx.record_ai_attempt({
            "attempt_number": ctx.attempt_number,
            "agent": "codex",
            "input_error_report_id": f"error_report_attempt_{ctx.attempt_number-1}.json",
            "changed_files": [],
            "notes": "Placeholder Codex fix not implemented; proceed to recheck.",
        })
        advance_state(ctx)
        db.save_error_context(ctx)
        return ctx

    if ctx.current_state == S2_CODEX_RECHECK:
        report = run_error_pipeline(ctx.python_files, ctx.powershell_files, ctx)
        ctx.update_error_reports(report)
        db.record_error_report(ctx, report, step_name="error_pipeline_recheck")
        advance_state(ctx)
        db.save_error_context(ctx)
        return ctx

    if ctx.current_state == S3_CLAUDE_FIX:
        ctx.record_ai_attempt({
            "attempt_number": ctx.attempt_number,
            "agent": "claude",
            "input_error_report_id": f"error_report_attempt_{ctx.attempt_number-1}.json",
            "changed_files": [],
            "notes": "Placeholder Claude fix not implemented; proceed to recheck.",
        })
        advance_state(ctx)
        db.save_error_context(ctx)
        return ctx

    if ctx.current_state == S3_CLAUDE_RECHECK:
        report = run_error_pipeline(ctx.python_files, ctx.powershell_files, ctx)
        ctx.update_error_reports(report)
        db.record_error_report(ctx, report, step_name="error_pipeline_recheck")
        advance_state(ctx)
        db.save_error_context(ctx)
        return ctx

    # Terminal or quarantine: no-op
    db.save_error_context(ctx)
    return ctx
