"""Unit tests for error state machine."""
from __future__ import annotations

import pytest

from modules.error_engine.m010004_error_state_machine import (
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
    S4_QUARANTINE,
    S_SUCCESS,
)
from modules.error_engine.m010004_error_context import ErrorPipelineContext


class TestStateTransitions:
    """Test state machine transitions."""
DOC_ID: DOC-ERROR-UNIT-TEST-STATE-MACHINE-083
    
    def test_init_to_baseline(self):
        """Test S_INIT → S0_BASELINE_CHECK."""
        ctx = ErrorPipelineContext(
            run_id="test-001",
            workstream_id="ws-001",
            current_state=S_INIT,
        )
        
        advance_state(ctx)
        
        assert ctx.current_state == S0_BASELINE_CHECK
        assert ctx.attempt_number == 0
        assert ctx.current_agent == "none"
    
    def test_baseline_no_issues_to_success(self):
        """Test S0_BASELINE_CHECK → S_SUCCESS (no issues)."""
        ctx = ErrorPipelineContext(
            run_id="test-001",
            workstream_id="ws-001",
            current_state=S0_BASELINE_CHECK,
            last_error_report={"summary": {"total_issues": 0}},
        )
        
        advance_state(ctx)
        
        assert ctx.current_state == S_SUCCESS
        assert ctx.final_status == "success"
    
    def test_baseline_with_issues_to_mechanical(self):
        """Test S0_BASELINE_CHECK → S0_MECHANICAL_AUTOFIX (issues found)."""
        ctx = ErrorPipelineContext(
            run_id="test-001",
            workstream_id="ws-001",
            current_state=S0_BASELINE_CHECK,
            enable_mechanical_autofix=True,
            last_error_report={"summary": {"total_issues": 5, "has_hard_fail": False}},
        )
        
        advance_state(ctx)
        
        assert ctx.current_state == S0_MECHANICAL_AUTOFIX
    
    def test_mechanical_fix_to_recheck(self):
        """Test S0_MECHANICAL_AUTOFIX → S0_MECHANICAL_RECHECK."""
        ctx = ErrorPipelineContext(
            run_id="test-001",
            workstream_id="ws-001",
            current_state=S0_MECHANICAL_AUTOFIX,
        )
        
        advance_state(ctx)
        
        assert ctx.current_state == S0_MECHANICAL_RECHECK
        assert ctx.mechanical_fix_applied is True
