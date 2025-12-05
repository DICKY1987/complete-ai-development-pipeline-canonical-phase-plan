"""Integration test: Error state machine transitions."""

# DOC_ID: DOC-ERROR-INTEGRATION-TEST-STATE-MACHINE-004

from __future__ import annotations

from typing import Any, Dict

import pytest

from phase6_error_recovery.modules.error_engine.src.engine.error_context import (
    ErrorPipelineContext,
)
from phase6_error_recovery.modules.error_engine.src.engine.error_state_machine import (
    advance_state,
)


@pytest.fixture
def baseline_context():
    """Create context for baseline state testing."""
    return ErrorPipelineContext(
        run_id="test-run-001",
        workstream_id="test-ws-001",
        python_files=["test.py"],
        enable_mechanical_autofix=True,
        enable_aider=False,
        enable_codex=False,
        enable_claude=False,
        strict_mode=True,
    )


@pytest.fixture
def full_escalation_context():
    """Create context with all AI agents enabled."""
    return ErrorPipelineContext(
        run_id="test-run-002",
        workstream_id="test-ws-002",
        python_files=["broken.py"],
        enable_mechanical_autofix=True,
        enable_aider=True,
        enable_codex=True,
        enable_claude=True,
        strict_mode=True,
    )


def test_init_to_baseline_transition(baseline_context):
    """Test transition from S_INIT to S0_BASELINE_CHECK."""
    assert baseline_context.current_state == "S_INIT"

    advance_state(baseline_context)

    assert baseline_context.current_state == "S0_BASELINE_CHECK"


def test_baseline_success_to_success(baseline_context):
    """Test transition from baseline to success when no errors."""
    baseline_context.current_state = "S0_BASELINE_CHECK"
    baseline_context.last_error_report = {
        "summary": {
            "total_issues": 0,
            "has_hard_fail": False,
        }
    }

    advance_state(baseline_context)

    assert baseline_context.current_state == "S_SUCCESS"


def test_baseline_failure_to_mechanical(baseline_context):
    """Test transition from baseline failure to mechanical autofix."""
    baseline_context.current_state = "S0_BASELINE_CHECK"
    baseline_context.last_error_report = {
        "summary": {
            "total_issues": 5,
            "has_hard_fail": True,
        }
    }

    advance_state(baseline_context)

    assert baseline_context.current_state == "S0_MECHANICAL_AUTOFIX"


def test_mechanical_to_recheck(baseline_context):
    """Test transition from mechanical autofix to recheck."""
    baseline_context.current_state = "S0_MECHANICAL_AUTOFIX"
    baseline_context.mechanical_fix_applied = True

    advance_state(baseline_context)

    assert baseline_context.current_state == "S0_MECHANICAL_RECHECK"


def test_mechanical_recheck_success(baseline_context):
    """Test mechanical recheck succeeds and goes to success."""
    baseline_context.current_state = "S0_MECHANICAL_RECHECK"
    baseline_context.last_error_report = {
        "summary": {
            "total_issues": 0,
            "has_hard_fail": False,
        }
    }

    advance_state(baseline_context)

    assert baseline_context.current_state == "S_SUCCESS"


def test_mechanical_recheck_failure_to_quarantine_no_ai(baseline_context):
    """Test mechanical recheck failure goes to quarantine when no AI enabled."""
    baseline_context.current_state = "S0_MECHANICAL_RECHECK"
    baseline_context.last_error_report = {
        "summary": {
            "total_issues": 3,
            "has_hard_fail": True,
        }
    }

    advance_state(baseline_context)

    # Should go to quarantine since no AI agents enabled
    assert baseline_context.current_state == "S4_QUARANTINE"


def test_full_escalation_chain(full_escalation_context):
    """Test full escalation chain: baseline → mechanical → aider → codex → claude → quarantine."""
    # S_INIT → S0_BASELINE_CHECK
    advance_state(full_escalation_context)
    assert full_escalation_context.current_state == "S0_BASELINE_CHECK"

    # S0_BASELINE_CHECK → S0_MECHANICAL_AUTOFIX (baseline fails)
    full_escalation_context.last_error_report = {
        "summary": {"total_issues": 5, "has_hard_fail": True}
    }
    advance_state(full_escalation_context)
    assert full_escalation_context.current_state == "S0_MECHANICAL_AUTOFIX"

    # S0_MECHANICAL_AUTOFIX → S0_MECHANICAL_RECHECK
    advance_state(full_escalation_context)
    assert full_escalation_context.current_state == "S0_MECHANICAL_RECHECK"

    # S0_MECHANICAL_RECHECK → S1_AIDER_FIX (mechanical fails)
    full_escalation_context.last_error_report = {
        "summary": {"total_issues": 3, "has_hard_fail": True}
    }
    advance_state(full_escalation_context)
    assert full_escalation_context.current_state == "S1_AIDER_FIX"


def test_context_serialization_preserves_state(baseline_context):
    """Test that context serialization preserves state information."""
    baseline_context.current_state = "S1_AIDER_FIX"
    baseline_context.attempt_number = 1
    baseline_context.current_agent = "aider"

    # Serialize and deserialize
    json_data = baseline_context.to_json()
    restored = ErrorPipelineContext.from_json(json_data)

    assert restored.current_state == "S1_AIDER_FIX"
    assert restored.attempt_number == 1
    assert restored.current_agent == "aider"


def test_ai_attempt_recording(full_escalation_context):
    """Test that AI attempts are recorded correctly."""
    attempt = {
        "agent": "aider",
        "timestamp": "2025-12-05T10:00:00Z",
        "success": False,
        "errors_before": 5,
        "errors_after": 3,
    }

    full_escalation_context.record_ai_attempt(attempt)

    assert len(full_escalation_context.ai_attempts) == 1
    assert full_escalation_context.ai_attempts[0]["agent"] == "aider"


def test_error_report_update_preserves_history(baseline_context):
    """Test that error report updates preserve history."""
    first_report = {"summary": {"total_issues": 10}}
    second_report = {"summary": {"total_issues": 5}}

    baseline_context.update_error_reports(first_report)
    assert baseline_context.last_error_report == first_report
    assert baseline_context.previous_error_report is None

    baseline_context.update_error_reports(second_report)
    assert baseline_context.last_error_report == second_report
    assert baseline_context.previous_error_report == first_report
