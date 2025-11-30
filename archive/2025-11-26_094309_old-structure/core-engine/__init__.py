"""Core Orchestration Engine

Workstream orchestration, scheduling, execution, and tool integration.

This module coordinates workstream execution with retry logic, circuit breakers,
and recovery strategies. It integrates with external AI coding tools via adapters.

Public API:
    Orchestration:
        - orchestrator.run_workstream() - Execute single workstream
        - orchestrator.execute_workstreams_parallel() - Parallel execution
        - orchestrator.run_edit_step()
        - orchestrator.run_static_with_fix()
        - orchestrator.run_runtime_with_fix()
    
    Scheduling:
        - scheduler.build_execution_plan() - Dependency resolution and waves
    
    Tool Integration:
        - tools.run_tool() - Execute tool with profile
        - tools.load_tool_profiles()
        - adapters.get_adapter() - Get tool adapter
        - adapters.BaseAdapter - Adapter interface
    
    Circuit Breakers:
        - circuit_breakers.FixLoopState
        - circuit_breakers.allow_fix_attempt()
        - circuit_breakers.detect_oscillation()
    
    Recovery:
        - recovery_manager.RecoveryManager
        - recovery.attempt_recovery()

Usage:
    from modules.core_engine.m010001_orchestrator import run_workstream
    from modules.core_engine.m010001_scheduler import build_execution_plan
    
    plan = build_execution_plan(bundles)
    result = run_workstream(run_id, ws_id, bundle)

For details, see:
    - core/engine/README.md
    - core/engine/dependencies.yaml
    - core/engine/adapters/README.md
"""
DOC_ID: DOC-PAT-CORE-ENGINE-INIT-405

__all__ = [
    "orchestrator",
    "scheduler",
    "executor",
    "tools",
    "circuit_breakers",
    "recovery",
    "recovery_manager",
    "aim_integration",
    "adapters",
    "metrics",
    "cost_tracker",
]
