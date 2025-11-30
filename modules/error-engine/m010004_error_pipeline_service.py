"""Error Pipeline Service - High-level orchestration of error detection and fixing.

This module coordinates the state machine, agent adapters, and validation pipeline
to provide automated error remediation.
"""
DOC_ID: DOC-PAT-ERROR-ENGINE-M010004-ERROR-PIPELINE-545
from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from .m010004_agent_adapters import AgentInvocation, AgentResult, get_agent_adapter
from .m010004_error_context import ErrorPipelineContext
from .m010004_error_state_machine import advance_state
from error.shared.utils.time import utc_now_iso


def tick(ctx: ErrorPipelineContext) -> ErrorPipelineContext:
    """Advance the error pipeline by one step."""
    advance_state(ctx)
    return ctx


@dataclass
class StageSummary:
    stage: str
    total: int
    ok: int
    failed: int
    units: List[str]


def execute_fix_state(ctx: ErrorPipelineContext, files: List[str]) -> AgentResult:
    """Execute fix based on current state.
    
    Args:
        ctx: Error pipeline context
        files: List of files to fix
        
    Returns:
        AgentResult from the invoked agent
    """
    # Map state to agent
    agent_map = {
        "S1_AIDER_FIX": "aider",
        "S2_CODEX_FIX": "codex",
        "S3_CLAUDE_FIX": "claude",
    }
    
    agent_name = agent_map.get(ctx.current_state)
    if not agent_name:
        # Not a fix state or mechanical fix
        raise ValueError(f"Cannot execute fix for state: {ctx.current_state}")
    
    # Get adapter
    adapter = get_agent_adapter(agent_name)
    
    # Create invocation
    invocation = AgentInvocation(
        agent_name=agent_name,
        files=files,
        error_report=ctx.last_error_report or {},
        timeout_seconds=300,
    )
    
    # Invoke agent
    result = adapter.invoke(invocation)
    
    # Record attempt in context
    ctx.record_ai_attempt({
        "agent": agent_name,
        "attempt": ctx.attempt_number,
        "state": ctx.current_state,
        "success": result.success,
        "files_modified": result.files_modified,
        "duration_ms": result.duration_ms,
        "timestamp": utc_now_iso(),
        "error_message": result.error_message,
    })
    
    return result


def run_error_pipeline_with_fixes(
    ctx: ErrorPipelineContext,
    validation_func: callable,
) -> Dict[str, Any]:
    """Run the complete error pipeline with AI-assisted fixing.
    
    This is the main entry point that orchestrates:
    1. Initial validation
    2. State machine progression
    3. AI agent invocation for fixes
    4. Re-validation after fixes
    
    Args:
        ctx: Error pipeline context
        validation_func: Function that validates files and returns error report
        
    Returns:
        Final error report with summary
    """
    files = ctx.python_files + ctx.powershell_files
    
    # Run initial validation (S0_BASELINE_CHECK)
    if ctx.current_state == "S_INIT":
        advance_state(ctx)  # S_INIT → S0_BASELINE_CHECK
    
    # Baseline check
    if ctx.current_state == "S0_BASELINE_CHECK":
        report = validation_func(files)
        ctx.update_error_reports(report)
        advance_state(ctx)
        
        # If success, return immediately
        if ctx.current_state == "S_SUCCESS":
            return ctx.last_error_report
    
    # Iterate through fix states until success or quarantine
    max_iterations = 10  # Safety limit
    iteration = 0
    
    while iteration < max_iterations and ctx.current_state not in ("S_SUCCESS", "S4_QUARANTINE"):
        iteration += 1
        
        # Check if current state is a fix state
        if ctx.current_state in ("S0_MECHANICAL_AUTOFIX", "S1_AIDER_FIX", "S2_CODEX_FIX", "S3_CLAUDE_FIX"):
            if ctx.current_state == "S0_MECHANICAL_AUTOFIX":
                # Mechanical fixes - apply auto-fix plugins
                # This would call the pipeline with fix plugins only
                # For now, mark as applied and advance
                ctx.mechanical_fix_applied = True
                advance_state(ctx)  # → S0_MECHANICAL_RECHECK
            else:
                # AI agent fix
                try:
                    result = execute_fix_state(ctx, files)
                    # Advance to recheck state
                    advance_state(ctx)
                except Exception as e:
                    # Agent invocation failed - record and advance to recheck anyway
                    ctx.record_ai_attempt({
                        "agent": ctx.current_agent,
                        "attempt": ctx.attempt_number,
                        "success": False,
                        "error": str(e),
                        "timestamp": utc_now_iso(),
                    })
                    advance_state(ctx)
        
        # Check if current state is a recheck state
        if ctx.current_state in ("S0_MECHANICAL_RECHECK", "S1_AIDER_RECHECK", "S2_CODEX_RECHECK", "S3_CLAUDE_RECHECK"):
            # Re-validate
            report = validation_func(files)
            ctx.update_error_reports(report)
            advance_state(ctx)
        
        # If in other states, just advance (safety)
        if ctx.current_state not in ("S_SUCCESS", "S4_QUARANTINE"):
            if ctx.current_state.endswith("_FIX") or ctx.current_state.endswith("_RECHECK"):
                pass  # Already handled above
            else:
                advance_state(ctx)
    
    # Return final report
    final_report = ctx.last_error_report or {}
    final_report["final_state"] = ctx.current_state
    final_report["final_status"] = ctx.final_status
    final_report["ai_attempts"] = ctx.ai_attempts
    final_report["mechanical_fix_applied"] = ctx.mechanical_fix_applied
    
    return final_report


