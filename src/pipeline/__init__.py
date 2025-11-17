"""Pipeline Module - Core orchestration and workflow execution.

This module provides the core orchestration logic for the AI development pipeline,
including workstream execution, tool integration, and state management.

Public API:
    - run_workstream: Execute a single workstream (EDIT → STATIC → RUNTIME)
    - run_single_workstream_from_bundle: Load and execute a workstream by ID
    - load_and_validate_bundles: Load and validate all workstream bundles
    - WorkstreamBundle: Workstream bundle data structure
    - run_tool: Execute external tool via adapter layer
    - ToolResult: Standardized tool execution result
"""

from __future__ import annotations

from .orchestrator import run_workstream, run_single_workstream_from_bundle
from .bundles import load_and_validate_bundles, WorkstreamBundle
from .tools import run_tool, ToolResult

__all__ = [
    # Orchestration
    "run_workstream",
    "run_single_workstream_from_bundle",
    # Bundle management
    "load_and_validate_bundles",
    "WorkstreamBundle",
    # Tool execution
    "run_tool",
    "ToolResult",
]

