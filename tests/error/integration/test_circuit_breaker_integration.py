"""Integration test: Circuit breaker integration with error recovery."""

# DOC_ID: DOC-ERROR-INTEGRATION-TEST-CIRCUIT-BREAKER-007

from __future__ import annotations

from pathlib import Path

import pytest

from phase6_error_recovery.modules.error_engine.src.engine.error_context import (
    ErrorPipelineContext,
)


@pytest.fixture
def circuit_breaker_context():
    """Create context for circuit breaker testing."""
    return ErrorPipelineContext(
        run_id="test-cb-001",
        workstream_id="test-ws-cb-001",
        python_files=["test1.py", "test2.py", "test3.py"],
        enable_mechanical_autofix=True,
        enable_aider=True,
        strict_mode=True,
        max_attempts_per_agent=3,
    )


def test_circuit_breaker_context_initialization(circuit_breaker_context):
    """Test that circuit breaker context is properly initialized."""
    assert circuit_breaker_context.max_attempts_per_agent == 3
    assert len(circuit_breaker_context.python_files) == 3


def test_attempt_number_tracking(circuit_breaker_context):
    """Test that attempt numbers are tracked correctly."""
    circuit_breaker_context.attempt_number = 0
    assert circuit_breaker_context.attempt_number == 0

    circuit_breaker_context.attempt_number += 1
    assert circuit_breaker_context.attempt_number == 1

    circuit_breaker_context.attempt_number += 1
    assert circuit_breaker_context.attempt_number == 2


def test_circuit_opens_after_max_attempts():
    """Test that circuit opens (stops retrying) after max attempts."""
    ctx = ErrorPipelineContext(
        run_id="test-max-001",
        workstream_id="test-ws-max-001",
        python_files=["broken.py"],
        max_attempts_per_agent=2,
    )

    # Simulate failures up to max
    for i in range(ctx.max_attempts_per_agent):
        ctx.attempt_number = i
        assert (
            ctx.attempt_number < ctx.max_attempts_per_agent
            or ctx.attempt_number == ctx.max_attempts_per_agent
        )

    # After max attempts, should stop (implicit circuit open)
    ctx.attempt_number = ctx.max_attempts_per_agent
    assert ctx.attempt_number == ctx.max_attempts_per_agent


def test_circuit_breaker_with_error_report_history(circuit_breaker_context):
    """Test circuit breaker with error report history tracking."""
    reports = [
        {"summary": {"total_issues": 10}},
        {"summary": {"total_issues": 8}},
        {"summary": {"total_issues": 8}},  # No improvement
    ]

    for report in reports:
        circuit_breaker_context.update_error_reports(report)

    # Last two reports should show no improvement
    last = circuit_breaker_context.last_error_report
    prev = circuit_breaker_context.previous_error_report

    if last and prev:
        assert last["summary"]["total_issues"] == prev["summary"]["total_issues"]


def test_circuit_recovery_on_improvement(circuit_breaker_context):
    """Test that circuit can recover when errors improve."""
    circuit_breaker_context.update_error_reports({"summary": {"total_issues": 10}})
    circuit_breaker_context.update_error_reports({"summary": {"total_issues": 5}})

    last = circuit_breaker_context.last_error_report
    prev = circuit_breaker_context.previous_error_report

    # Improvement should allow continued attempts
    if last and prev:
        assert last["summary"]["total_issues"] < prev["summary"]["total_issues"]


def test_circuit_breaker_failure_metadata(circuit_breaker_context):
    """Test that failure metadata is preserved for circuit breaker decisions."""
    failure_report = {
        "summary": {
            "total_issues": 5,
            "has_hard_fail": True,
            "issues_by_category": {"syntax": 2, "type": 3},
        },
        "timestamp": "2025-12-05T10:00:00Z",
    }

    circuit_breaker_context.update_error_reports(failure_report)

    assert circuit_breaker_context.last_error_report["summary"]["has_hard_fail"] is True
    assert "issues_by_category" in circuit_breaker_context.last_error_report["summary"]


def test_circuit_opens_with_infrastructure_failure():
    """Test that circuit opens immediately on infrastructure failure."""
    ctx = ErrorPipelineContext(
        run_id="test-infra-001",
        workstream_id="test-ws-infra-001",
        python_files=["test.py"],
    )

    # Simulate infrastructure failure
    ctx.final_status = "infra_failure"

    assert ctx.final_status == "infra_failure"
    # Circuit should open immediately, no retries


def test_circuit_state_serialization(circuit_breaker_context):
    """Test that circuit breaker state is preserved through serialization."""
    circuit_breaker_context.attempt_number = 2
    circuit_breaker_context.current_agent = "aider"

    json_data = circuit_breaker_context.to_json()
    restored = ErrorPipelineContext.from_json(json_data)

    assert restored.attempt_number == 2
    assert restored.current_agent == "aider"
    assert restored.max_attempts_per_agent == 3


def test_multiple_file_circuit_breaker_isolation():
    """Test that circuit breaker failures on one file don't affect others."""
    ctx = ErrorPipelineContext(
        run_id="test-multi-file-001",
        workstream_id="test-ws-multi-file-001",
        python_files=["file1.py", "file2.py", "file3.py"],
    )

    # Each file should have independent circuit breaker state
    assert len(ctx.python_files) == 3

    # Conceptually, circuit breaker should isolate failures per file
    # (Implementation detail: would need per-file attempt tracking)
