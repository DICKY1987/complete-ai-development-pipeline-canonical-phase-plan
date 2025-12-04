# START <TestKey>
# TestType: Unit
# TargetModule: phase6_error_recovery/modules/error_engine/src/engine/error_state_machine.py
# TargetFunction: advance_state
# Purpose: Exercise deterministic state transitions across success, escalation, and terminal branches
# OptimizationPattern: Fixture-Based
# CoverageGoalAchieved: 100% True
# END <TestKey>

from __future__ import annotations

from phase6_error_recovery.modules.error_engine.src.engine import (
    error_state_machine as sm,
)
from phase6_error_recovery.modules.error_engine.src.engine.error_context import (
    ErrorPipelineContext,
)


def _ctx(state: str, **kwargs) -> ErrorPipelineContext:
    ctx = ErrorPipelineContext(run_id="r", workstream_id="w", **kwargs)
    ctx.current_state = state
    return ctx


def test_init_sets_baseline():
    ctx = _ctx(sm.S_INIT)
    sm.advance_state(ctx)
    assert ctx.current_state == sm.S0_BASELINE_CHECK
    assert ctx.attempt_number == 0
    assert ctx.current_agent == "none"
    assert ctx.mechanical_fix_applied is False


def test_baseline_success_and_mechanical_flow():
    # Success path when no issues
    ctx = _ctx(sm.S0_BASELINE_CHECK, last_error_report={"summary": {"total_issues": 0}})
    sm.advance_state(ctx)
    assert ctx.current_state == sm.S_SUCCESS
    assert ctx.final_status == "success"

    # Mechanical autofix path when issues remain
    ctx = _ctx(
        sm.S0_BASELINE_CHECK,
        last_error_report={"summary": {"total_issues": 2, "has_hard_fail": True}},
        enable_mechanical_autofix=True,
    )
    sm.advance_state(ctx)
    assert ctx.current_state == sm.S0_MECHANICAL_AUTOFIX

    sm.advance_state(ctx)
    assert ctx.current_state == sm.S0_MECHANICAL_RECHECK
    assert ctx.mechanical_fix_applied is True


def test_recheck_allows_success_when_not_strict():
    ctx = _ctx(
        sm.S0_MECHANICAL_RECHECK,
        last_error_report={"summary": {"total_issues": 3, "has_hard_fail": False}},
        strict_mode=False,
    )
    sm.advance_state(ctx)
    assert ctx.current_state == sm.S_SUCCESS
    assert ctx.final_status == "success"


def test_escalation_chain_and_quarantine():
    ctx = _ctx(
        sm.S0_MECHANICAL_RECHECK,
        last_error_report={"summary": {"total_issues": 1, "has_hard_fail": True}},
        enable_mechanical_autofix=True,
        enable_aider=True,
        enable_codex=True,
        enable_claude=False,
    )
    sm.advance_state(ctx)
    assert ctx.current_state == sm.S1_AIDER_FIX
    assert ctx.attempt_number == 1
    assert ctx.current_agent == "aider"

    ctx.current_state = sm.S1_AIDER_RECHECK
    ctx.last_error_report = {"summary": {"total_issues": 1, "has_hard_fail": True}}
    sm.advance_state(ctx)
    assert ctx.current_state == sm.S2_CODEX_FIX
    assert ctx.attempt_number == 2
    assert ctx.current_agent == "codex"

    ctx.current_state = sm.S2_CODEX_RECHECK
    ctx.last_error_report = {"summary": {"total_issues": 1, "has_hard_fail": True}}
    sm.advance_state(ctx)
    assert ctx.current_state == sm.S4_QUARANTINE


def test_claude_recheck_quarantine_and_terminal_noop():
    ctx = _ctx(
        sm.S3_CLAUDE_RECHECK,
        last_error_report={"summary": {"total_issues": 1, "has_hard_fail": True}},
    )
    sm.advance_state(ctx)
    assert ctx.current_state == sm.S4_QUARANTINE

    ctx.current_state = sm.S_SUCCESS
    sm.advance_state(ctx)
    assert ctx.current_state == sm.S_SUCCESS


def test_baseline_escalates_without_mechanical():
    ctx = _ctx(
        sm.S0_BASELINE_CHECK,
        last_error_report={"summary": {"total_issues": 5, "has_hard_fail": True}},
        enable_mechanical_autofix=False,
        enable_aider=True,
        enable_codex=False,
        enable_claude=False,
    )
    sm.advance_state(ctx)
    assert ctx.current_state == sm.S1_AIDER_FIX


def test_rechecks_promote_to_claude():
    ctx = _ctx(
        sm.S1_AIDER_RECHECK,
        last_error_report={"summary": {"total_issues": 1, "has_hard_fail": True}},
        enable_codex=False,
        enable_claude=True,
    )
    sm.advance_state(ctx)
    assert ctx.current_state == sm.S3_CLAUDE_FIX
    assert ctx.attempt_number == 3
    assert ctx.current_agent == "claude"

    ctx.current_state = sm.S2_CODEX_RECHECK
    ctx.last_error_report = {"summary": {"total_issues": 1, "has_hard_fail": True}}
    sm.advance_state(ctx)
    assert ctx.current_state == sm.S3_CLAUDE_FIX
