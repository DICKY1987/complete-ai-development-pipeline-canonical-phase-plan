"""Tests for cost tracking."""

import pytest
from modules.core_engine.m010001_cost_tracker import PRICING_TABLE, CostTracker


def test_pricing_table():
    """Test pricing table has expected models."""
    # DOC_ID: DOC-TEST-TESTS-TEST-COST-TRACKING-078
    # DOC_ID: DOC-TEST-TESTS-TEST-COST-TRACKING-039
    assert "gpt-4" in PRICING_TABLE
    assert "claude-3-sonnet" in PRICING_TABLE

    gpt4 = PRICING_TABLE["gpt-4"]
    assert gpt4.input_cost_per_1k == 0.03
    assert gpt4.output_cost_per_1k == 0.06


def test_record_usage(temp_db):
    """Test recording token usage."""
    tracker = CostTracker()

    cost = tracker.record_usage(
        run_id="run-test",
        workstream_id="ws-test",
        step_id="step-1",
        worker_id="worker-1",
        model_name="gpt-4",
        input_tokens=1000,
        output_tokens=500,
    )

    # GPT-4: $0.03 per 1k input + $0.06 per 1k output
    # 1000 input = $0.03, 500 output = $0.03
    expected_cost = 0.03 + 0.03
    assert abs(cost - expected_cost) < 0.001


def test_get_total_cost(temp_db):
    """Test getting total cost for a run."""
    tracker = CostTracker()

    # Record some usage
    tracker.record_usage(
        run_id="run-cost-test",
        workstream_id="ws-1",
        step_id="step-1",
        worker_id="worker-1",
        model_name="gpt-3.5-turbo",
        input_tokens=2000,
        output_tokens=1000,
    )

    tracker.record_usage(
        run_id="run-cost-test",
        workstream_id="ws-2",
        step_id="step-2",
        worker_id="worker-2",
        model_name="gpt-3.5-turbo",
        input_tokens=3000,
        output_tokens=1500,
    )

    total = tracker.get_total_cost("run-cost-test")
    assert total > 0
