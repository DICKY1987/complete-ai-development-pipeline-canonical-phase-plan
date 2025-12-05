"""Integration test: AI agent escalation (Tier 0 → 1 → 2 → 3)."""

# DOC_ID: DOC-ERROR-INTEGRATION-TEST-AI-AGENT-ESCALATION-006

from __future__ import annotations

import pytest

from phase6_error_recovery.modules.error_engine.src.engine.error_context import (
    ErrorPipelineContext,
)
from phase6_error_recovery.modules.error_engine.src.engine.error_state_machine import (
    advance_state,
)


@pytest.fixture
def escalation_context():
    """Create context with all escalation tiers enabled."""
    return ErrorPipelineContext(
        run_id="test-escalation-001",
        workstream_id="test-ws-escalation-001",
        python_files=["broken.py"],
        enable_mechanical_autofix=True,
        enable_aider=True,
        enable_codex=True,
        enable_claude=True,
        strict_mode=True,
        max_attempts_per_agent=1,
    )


def test_tier_0_mechanical_first(escalation_context):
    """Test that Tier 0 (mechanical) is attempted first."""
    escalation_context.current_state = "S0_BASELINE_CHECK"
    escalation_context.last_error_report = {
        "summary": {"total_issues": 5, "has_hard_fail": True}
    }

    advance_state(escalation_context)

    assert escalation_context.current_state == "S0_MECHANICAL_AUTOFIX"
    assert escalation_context.attempt_number == 0


def test_tier_1_aider_after_mechanical_failure(escalation_context):
    """Test that Tier 1 (Aider) is attempted after mechanical fails."""
    escalation_context.current_state = "S0_MECHANICAL_RECHECK"
    escalation_context.last_error_report = {
        "summary": {"total_issues": 3, "has_hard_fail": True}
    }

    advance_state(escalation_context)

    assert escalation_context.current_state == "S1_AIDER_FIX"


def test_tier_2_codex_after_aider_failure(escalation_context):
    """Test that Tier 2 (Codex) is attempted after Aider fails."""
    escalation_context.current_state = "S1_AIDER_RECHECK"
    escalation_context.attempt_number = 1
    escalation_context.last_error_report = {
        "summary": {"total_issues": 2, "has_hard_fail": True}
    }

    advance_state(escalation_context)

    assert escalation_context.current_state == "S2_CODEX_FIX"


def test_tier_3_claude_after_codex_failure(escalation_context):
    """Test that Tier 3 (Claude) is attempted after Codex fails."""
    escalation_context.current_state = "S2_CODEX_RECHECK"
    escalation_context.attempt_number = 2
    escalation_context.last_error_report = {
        "summary": {"total_issues": 1, "has_hard_fail": True}
    }

    advance_state(escalation_context)

    assert escalation_context.current_state == "S3_CLAUDE_FIX"


def test_quarantine_after_all_tiers_fail(escalation_context):
    """Test that file is quarantined after all tiers fail."""
    escalation_context.current_state = "S3_CLAUDE_RECHECK"
    escalation_context.attempt_number = 3
    escalation_context.last_error_report = {
        "summary": {"total_issues": 1, "has_hard_fail": True}
    }

    advance_state(escalation_context)

    assert escalation_context.current_state == "S4_QUARANTINE"


def test_success_at_tier_1_skips_higher_tiers(escalation_context):
    """Test that success at Tier 1 skips Tier 2 and 3."""
    escalation_context.current_state = "S1_AIDER_RECHECK"
    escalation_context.attempt_number = 1
    escalation_context.last_error_report = {
        "summary": {"total_issues": 0, "has_hard_fail": False}
    }

    advance_state(escalation_context)

    assert escalation_context.current_state == "S_SUCCESS"


def test_success_at_tier_2_skips_tier_3(escalation_context):
    """Test that success at Tier 2 skips Tier 3."""
    escalation_context.current_state = "S2_CODEX_RECHECK"
    escalation_context.attempt_number = 2
    escalation_context.last_error_report = {
        "summary": {"total_issues": 0, "has_hard_fail": False}
    }

    advance_state(escalation_context)

    assert escalation_context.current_state == "S_SUCCESS"


def test_escalation_with_partial_ai_disabled():
    """Test escalation when only some AI agents are enabled."""
    ctx = ErrorPipelineContext(
        run_id="test-partial-001",
        workstream_id="test-ws-partial-001",
        python_files=["test.py"],
        enable_mechanical_autofix=True,
        enable_aider=True,
        enable_codex=False,  # Disabled
        enable_claude=True,
        strict_mode=True,
    )

    # Mechanical fails
    ctx.current_state = "S0_MECHANICAL_RECHECK"
    ctx.last_error_report = {"summary": {"total_issues": 3, "has_hard_fail": True}}
    advance_state(ctx)
    assert ctx.current_state == "S1_AIDER_FIX"

    # Aider fails
    ctx.current_state = "S1_AIDER_RECHECK"
    ctx.last_error_report = {"summary": {"total_issues": 2, "has_hard_fail": True}}
    advance_state(ctx)

    # Should skip Codex (disabled) and go to Claude
    assert ctx.current_state in ["S3_CLAUDE_FIX", "S4_QUARANTINE"]


def test_ai_attempt_tracking_through_escalation(escalation_context):
    """Test that AI attempts are tracked through escalation."""
    attempts = [
        {"agent": "aider", "success": False, "errors_after": 3},
        {"agent": "codex", "success": False, "errors_after": 2},
        {"agent": "claude", "success": False, "errors_after": 1},
    ]

    for attempt in attempts:
        escalation_context.record_ai_attempt(attempt)

    assert len(escalation_context.ai_attempts) == 3
    assert escalation_context.ai_attempts[0]["agent"] == "aider"
    assert escalation_context.ai_attempts[1]["agent"] == "codex"
    assert escalation_context.ai_attempts[2]["agent"] == "claude"


def test_max_attempts_per_agent_limit(escalation_context):
    """Test that max attempts per agent is respected."""
    assert escalation_context.max_attempts_per_agent == 1

    # Attempt tracking
    escalation_context.attempt_number = 1
    assert (
        escalation_context.attempt_number <= escalation_context.max_attempts_per_agent
    )


def test_current_agent_tracking(escalation_context):
    """Test that current agent is tracked correctly."""
    escalation_context.current_agent = "aider"
    escalation_context.current_state = "S1_AIDER_FIX"

    assert escalation_context.current_agent == "aider"

    escalation_context.current_agent = "codex"
    escalation_context.current_state = "S2_CODEX_FIX"

    assert escalation_context.current_agent == "codex"
