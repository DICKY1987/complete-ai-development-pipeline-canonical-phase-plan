---
doc_id: DOC-CORE-UET-CLI-TOOL-EXECUTION-SPEC-192
meta_version: "doc-meta.v1"
doc_ulid: "01JAAAAAAA0CLI0TOOLEXEC0001"
doc_type: "core_spec"
doc_layer: "framework"
title: "CLI Tool Execution Specification"
summary: "Defines how a single CLI instance (e.g. Claude Code CLI, GitHub Copilot CLI) executes tasks from multiple workstreams using queues, workers, and sandboxes."
version: "1.0.0"
status: "draft"
schema_ref: "schema/tool_execution_profile.v1.json"
created_at: "2025-11-22T00:00:00Z"
updated_at: "2025-11-22T00:00:00Z"
author_type: "mixed"
owner: "SYSTEM:AGENT_ORCHESTRATOR"
security_tier: "internal"

project_id: null
module_id: null
phase_id: null
workstream_id: null

spec_refs:
  - "PHASE_SPEC_MASTER_ULID"        # UET_PHASE_SPEC_MASTER
  - "WORKSTREAM_SPEC_ULID"          # UET_WORKSTREAM_SPEC
  - "TASK_ROUTING_SPEC_ULID"        # UET_TASK_ROUTING_SPEC
  - "COOPERATION_SPEC_ULID"         # UET_COOPERATION_SPEC
  - "KERNEL_PARALLELISM_SPEC_ULID"  # UET_EXECUTION_KERNEL_PARALLELISM_STRATEGY_SPEC_V2
  - "PATCH_MANAGEMENT_SPEC_ULID"    # UET_PATCH_MANAGEMENT_SPEC

tags:
  - "spec"
  - "tool_profile"
  - "cli"
  - "execution"
  - "multi_workstream"

patch_policy:
  patch_required: true
  require_issue_ref: true
  min_reviewers: 1

ascii_only: true
max_line_length:
  hard: 120
  soft: 100
checksum: null
last_validated_at: null
---

# CLI Tool Execution Specification

## 1. Purpose & Scope

This spec defines **how a single CLI tool instance** (e.g. `claude_code_cli`, `github_copilot_cli`) participates in the UET execution model when serving **multiple workstreams** simultaneously.

It answers:

- How work from many workstreams becomes **ToolWorkItems** for this CLI.
- How a single CLI **worker** chooses which item to process next (fairness).
- How sandboxes/working directories are mapped to **runs / workstreams**.
- How limits (concurrency, queue depth, runtime, cost) are enforced.

It does **not** redefine:

- Phase / Workstream structure (see PHASE_SPEC_MASTER, WORKSTREAM_SPEC).
- ExecutionRequest or routing (see TASK_ROUTING_SPEC).
- Run / Step / Event model (see COOPERATION_SPEC).
- Kernel scheduling and DAG semantics (see KERNEL_PARALLELISM_SPEC).

This document is a **tool-level profile spec** that plugs into those layers.

---

## 2. Key Concepts & Relationships

At the tool level we care about three core objects:

- **ToolExecutionProfile** – static configuration for a CLI tool.
- **ToolWorker** – a long-lived process that wraps a single CLI instance.
- **ToolWorkItem** – a concrete unit of work (one ExecutionRequest routed to this tool).

### 2.1 ToolExecutionProfile (per CLI tool)

Each CLI tool (Claude Code, Copilot CLI, etc.) MUST have a `ToolExecutionProfile` entry.

High-level JSON shape:

```json
{
  "tool_id": "claude_code_cli",
  "kind": "cli_tool",
  "max_workers": 1,
  "sandbox_mode": "per_workstream_worktree",
  "queue_strategy": {
    "kind": "priority_round_robin_by_workstream",
    "max_queue_depth": 256,
    "max_consecutive_from_same_workstream": 3
  },
  "limits": {
    "max_runtime_seconds": 600,
    "max_token_cost": 200000,
    "max_output_bytes": 1048576
  },
  "is_interactive_cli": true,
  "non_interactive_policy": "fail_if_prompted"
}
