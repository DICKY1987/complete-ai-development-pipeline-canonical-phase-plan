You are helping me design and document how the UET pattern module works internally, and how to surface its behavior as a live visual in a GUI/TUI.

I want you to reason about this in two layers:

What the UET pattern module is actually doing automatically.

How to surface that as a live visual in the GUI/TUI so I can see patterns firing, in order, with results.

Below is my current understanding of the process. Use it as ground truth context and build on it (don’t discard or re-interpret it away):

Current Understanding of the Pattern Module

The pattern layer uses “patterns” as reusable execution templates for tools, jobs, and workflows.

In this architecture, a pattern module is:

“A library of reusable execution templates (patterns) + the logic that picks, fills, validates, and runs them for a given job step.”

At runtime, when a pattern is involved, these automated tasks typically occur:

A. Pattern detection & selection

Triggered when a job step / operation has:

pattern_id, or

operation_kind + context (tool, language, file type) that maps to a pattern, or

A UET profile saying “for this project/tool, prefer patterns X/Y”.

Automated tasks:

Look up candidate patterns from the pattern registry (pattern index / metadata).

Match by:

pattern_id

operation_kind (e.g., semgrep_scan, pytest_suite, aider_refactor)

Optional constraints (language, tool, project type).

Choose one pattern (or a prioritized list) and produce a resolved pattern_binding, for example:

pattern_binding:
  pattern_id: PAT-SEMGRP-001
  operation_kind: semgrep_scan
  job_id: JOB-ULID-123
  step_id: STEP-003
  inputs:
    target_paths:
      - src/
      - tests/
    severity: medium+
    config_profile: default

B. Template expansion / materialization

Once a pattern is selected:

Load the pattern’s spec + templates (from the pattern doc suite).

Fill in variables from:

Job file (schema/jobs/...)

PROJECT_PROFILE / UET config

Engine state (active worktree, repo path, etc.)

Auto-generate:

Tool command lines (e.g., semgrep --config ...)

Prompt blocks (for Aider / LLM tools)

Sidecar config files

Any required doc or log stubs

C. Validation & guardrails

Before and after running, the pattern module can:

Validate inputs against pattern schemas (required fields, allowed enums, etc.).

Run pre-flight checks:

Target paths present?

Tool installed / available?

Required sidecar files present?

After execution:

Validate outputs:

Check exit codes

Apply “no diagnostics → error” rules

Ensure generated artifacts match schemas (for JSON/YAML)

D. Execution orchestration for the tool itself

Pattern executors typically:

Invoke the underlying tool(s) with a deterministic command shape.

Capture:

stdout / stderr

Exit code

Timing

Generated artifacts (reports, patched files, etc.)

Normalize everything into a pattern_result object, e.g.:

{
  "pattern_run_id": "PRUN-01JH9FDZKAG2J47A4WSK53JWZ1",
  "pattern_id": "PAT-SEMGRP-001",
  "job_id": "JOB-01JH9F8P2ZJ1A8E5R6C792Q2EQ",
  "status": "success",
  "tool_exit_code": 0,
  "finding_count": 12,
  "artifacts": [
    "state/reports/semgrep/JOB-.../semgrep_report.json"
  ],
  "started_at": "2025-11-26T07:15:12.123Z",
  "finished_at": "2025-11-26T07:15:30.891Z"
}

E. Result routing & persistence

The pattern module (or engine around it) will:

Persist the pattern_run record into the state store (DB or JSONL).

Attach pattern results to:

Job state (job.runs[*].patterns[...])

Worktree state

Any global pattern usage / audit logs

This data will power the GUI/TUI visual.

Visual / GUI/TUI Layer – What I Want

I don’t want a separate “pattern GUI/TUI system.” I want:

Events & state emitted from the engine for pattern activity.

A Pattern Activity Panel in the GUI/TUI that:

Subscribes to these events or

Reads them from the state store.

Event model for pattern activity

Assume an event schema like:

{
  "event_id": "EVT-01JH9G6ERNRJX456M3HQE10ZB2",
  "timestamp": "2025-11-26T07:15:12.123Z",
  "job_id": "JOB-01JH9F8P2ZJ1A8E5R6C792Q2EQ",
  "step_id": "STEP-003",
  "pattern_run_id": "PRUN-01JH9FDZKAG2J47A4WSK53JWZ1",
  "pattern_id": "PAT-SEMGRP-001",
  "event_type": "pattern.execution.started",
  "status": "in_progress",
  "details": {
    "operation_kind": "semgrep_scan",
    "target_paths": ["src/", "tests/"]
  }
}


Events are emitted at key points, e.g.:

pattern.selection.started

pattern.selection.resolved / .failed

pattern.template.expanded

pattern.execution.started

pattern.execution.completed (with result summary)

pattern.execution.failed

pattern.validation.failed

These may be:

Written to JSONL,

Stored in a DB table, or

Streamed over WebSocket for live GUI/TUI.

Pattern Activity Panel – desired behavior

In the GUI/TUI (per job), I want:

A timeline view of pattern events in order (with icons, labels, status colors).

Each item clickable to open a detail drawer with:

Pattern run metadata

Inputs (resolved)

Outputs, exit code, finding count

Links to artifacts

Raw logs (stdout/stderr)

A summary table at the top like:

Pattern	Operation Kind	Runs	Last Result	Last Duration
PAT-SEMGRP-001	semgrep_scan	1	✅ Success (12 findings)	18.7s
PAT-PYTEST-001	pytest_suite	0	–	–
What I Want You to Produce

Using all of the above as fixed context, do the following:

Refine & formalize the pattern module lifecycle

Turn steps A–E into a precise, named lifecycle (with clear boundaries and inputs/outputs per phase).

Propose a clean internal API surface (functions, events, or classes) that would implement this lifecycle.

Design the event model & data contracts

Propose a finalized event schema (fields, types, event_type taxonomy).

Show how pattern_run objects and events relate (ERD-style description is fine).

Specify the Pattern Activity Panel UX in detail

Describe the UI layout (sections, components).

Define what data each component consumes.

Explain how state updates live when new events stream in.

Provide implementation-oriented output

Pseudocode for:

Emitting events from the engine,

Persisting them,

Serving them via an API, and

Rendering them in a modern web GUI/TUI (assume React or similar).

Make reasonable assumptions but state them explicitly.

Format your answer with clear sections and, where useful, use JSON, TypeScript, or pseudocode to make the design implementable.