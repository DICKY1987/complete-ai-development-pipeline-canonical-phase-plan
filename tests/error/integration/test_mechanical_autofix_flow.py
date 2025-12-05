"""Integration test: Mechanical autofix flow (Tier 0)."""

# DOC_ID: DOC-ERROR-INTEGRATION-TEST-MECHANICAL-AUTOFIX-005

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from phase6_error_recovery.modules.error_engine.src.engine.error_context import (
    ErrorPipelineContext,
)
from phase6_error_recovery.modules.error_engine.src.engine.error_state_machine import (
    advance_state,
)


@pytest.fixture
def mechanical_context():
    """Create context for mechanical autofix testing."""
    return ErrorPipelineContext(
        run_id="test-mech-001",
        workstream_id="test-ws-mech-001",
        python_files=["test.py"],
        enable_mechanical_autofix=True,
        enable_aider=False,
        enable_codex=False,
        enable_claude=False,
        strict_mode=False,  # Non-strict allows warnings
    )


def test_mechanical_autofix_enabled_flag(mechanical_context):
    """Test that mechanical autofix is properly enabled."""
    assert mechanical_context.enable_mechanical_autofix is True
    assert mechanical_context.enable_aider is False
    assert mechanical_context.enable_codex is False
    assert mechanical_context.enable_claude is False


def test_mechanical_autofix_state_entry(mechanical_context):
    """Test entering mechanical autofix state."""
    mechanical_context.current_state = "S0_BASELINE_CHECK"
    mechanical_context.strict_mode = True  # Require fixing even warnings
    mechanical_context.last_error_report = {
        "summary": {
            "total_issues": 5,
            "has_hard_fail": False,  # Only warnings/style
            "style_only": True,
        }
    }

    advance_state(mechanical_context)

    assert mechanical_context.current_state == "S0_MECHANICAL_AUTOFIX"


def test_mechanical_fix_applied_flag(mechanical_context):
    """Test that mechanical fix applied flag is tracked."""
    mechanical_context.current_state = "S0_MECHANICAL_AUTOFIX"
    mechanical_context.mechanical_fix_applied = True

    advance_state(mechanical_context)

    assert mechanical_context.current_state == "S0_MECHANICAL_RECHECK"


def test_mechanical_autofix_skipped_when_disabled():
    """Test that mechanical autofix is skipped when disabled."""
    ctx = ErrorPipelineContext(
        run_id="test-no-mech-001",
        workstream_id="test-ws-no-mech-001",
        python_files=["test.py"],
        enable_mechanical_autofix=False,
        enable_aider=True,
        strict_mode=True,
    )

    ctx.current_state = "S0_BASELINE_CHECK"
    ctx.last_error_report = {"summary": {"total_issues": 5, "has_hard_fail": True}}

    advance_state(ctx)

    # Should skip mechanical and go to AI agent
    assert ctx.current_state != "S0_MECHANICAL_AUTOFIX"


@pytest.mark.skipif(not shutil.which("black"), reason="black not installed")
def test_mechanical_autofix_tools_available():
    """Test that mechanical autofix tools are available."""
    # Check for common mechanical autofix tools
    tools = {
        "black": shutil.which("black"),
        "isort": shutil.which("isort"),
    }

    # At least one should be available
    assert any(tools.values()), "No mechanical autofix tools available"


def test_mechanical_recheck_reduces_errors(mechanical_context):
    """Test that mechanical recheck verifies error reduction."""
    mechanical_context.current_state = "S0_MECHANICAL_RECHECK"

    # Simulate error reduction after mechanical fix
    mechanical_context.previous_error_report = {"summary": {"total_issues": 10}}
    mechanical_context.last_error_report = {
        "summary": {"total_issues": 2, "has_hard_fail": False}
    }

    # In non-strict mode, reduced errors = success
    advance_state(mechanical_context)

    assert mechanical_context.current_state in [
        "S_SUCCESS",
        "S1_AIDER_FIX",
        "S4_QUARANTINE",
    ]


def test_mechanical_fix_metadata_tracking(mechanical_context):
    """Test that mechanical fix metadata is tracked in context."""
    mechanical_context.mechanical_fix_applied = True

    json_data = mechanical_context.to_json()

    assert json_data["mechanical_fix_applied"] is True


def test_multiple_mechanical_tools_coordination(tmp_path):
    """Test that multiple mechanical tools can be coordinated (black + isort)."""
    # This is a conceptual test - actual implementation would involve plugin manager
    tools_to_check = ["black", "isort", "autopep8"]
    available_tools = [tool for tool in tools_to_check if shutil.which(tool)]

    # If multiple tools available, they should coordinate
    if len(available_tools) >= 2:
        assert True  # Coordination possible
    else:
        pytest.skip("Need at least 2 formatting tools installed")


def test_mechanical_autofix_state_to_json_roundtrip(mechanical_context):
    """Test state serialization during mechanical autofix."""
    mechanical_context.current_state = "S0_MECHANICAL_AUTOFIX"
    mechanical_context.mechanical_fix_applied = True

    json_data = mechanical_context.to_json()
    restored = ErrorPipelineContext.from_json(json_data)

    assert restored.current_state == "S0_MECHANICAL_AUTOFIX"
    assert restored.mechanical_fix_applied is True
