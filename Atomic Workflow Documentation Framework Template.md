🧭 Atomic Workflow Documentation Framework Template
1. Step Metadata Block (YAML Frontmatter or Table)

(Machine-readable metadata for versioning, traceability, and automation)
Use this as a consistent “header” for every step or document.

id: "ATW-03"                   # Unique ID
title: "Validate Phase"
phase: "Validate"
version: "1.0"
author: "System Architect"
last_updated: "2025-10-14"
related_steps: ["ATW-02", "ATW-04"]
dependencies: ["execution_plan.yaml", "codegate_pass"]
tags: ["deterministic", "QA", "rollback"]

2. Overview

A narrative summary describing what this step achieves, where it fits in the overall process, and its purpose within the workflow.

Recommended content:

Purpose and scope of this step

Relationship to previous and next steps

Core principles (e.g., determinism, reproducibility, isolation)

3. Objectives & Deterministic Guarantees

The measurable outcomes or “success criteria” that define when this step has been completed correctly.

Examples:

“All generated files have passed syntax and unit tests.”

“Each file either enters quarantine or advances deterministically.”

“Every action produces a logged event with a unique identifier.”

4. Inputs

Everything this step consumes — tangible or contextual.

Subsections (optional but consistent):

Artifacts / Files: (e.g., execution_plan.yaml, code from prior phase)

State: (e.g., worktree branches, checkpoints)

Triggers: (what initiates this step)

Tools / Systems: (software, CLIs, services)

Human Inputs: (if approvals or reviews are required)

5. Actions (Process Narrative)

The heart of the section. A structured, narrative description of what happens.
Avoid pure command lists; instead, describe what and why, optionally including pseudocode or structured bullet steps.

Recommended subsections:

Pre-checks: Validation of prerequisites.

Execution Flow: Sequential actions taken in this phase.

Parallel or Conditional Paths: Describe when actions branch or run concurrently.

Automation Hooks: How tools, scripts, or AIs are invoked.

Control & Safety Gates: What conditions allow or prevent forward movement.

(Keep Actions narrative-style — code snippets optional.)

6. Outputs

Define every artifact, log, or state change produced here.

Subsections (consistent naming):

Artifacts / Files Produced (e.g., validation_report.json, checkpoint(validate-pass))

Logs / Metrics (where logs are stored, structure, frequency)

State Changes (e.g., repo moved from dirty → validated)

Notifications or Events (GUI updates, JSON events, etc.)

7. Dependencies & Preconditions

Clarify exactly what must exist or complete successfully before this step can start.
This ensures determinism and helps parallel schedulers resolve ordering.

Examples:

“Requires prior step Execute to have produced an approved batch.”

“Git worktrees must be healthy and detached from main.”

“Local code gate watcher must be active.”

8. Postconditions / Completion Criteria

Define what must be true after successful execution — not just outputs, but verified states.

Examples:

“All workstream branches include a checkpoint(validate-pass) commit.”

“No open validation loops remain.”

“All files either passed validation or were quarantined with logs.”

9. Error Handling & Recovery Logic

Describe how failures are detected, logged, and resolved.
Emphasize deterministic rollback, isolation, and data preservation.

Include:

Known failure modes (AI timeout, Git conflict, gate fail).

Automated recovery or rollback behavior.

Human intervention triggers and escalation paths.

What data persists after failure (local saves, logs, quarantined files).

10. Logging & Observability

Describe how telemetry, events, and traceability are maintained.
Each sub-step should have structured, machine-readable log conventions.

Standardize fields:

run_id, ws_id, file_id, step, substep, loop_idx, timestamp, status, reason_code, artifact_path

Example: “Each sub-step writes one JSONL line; GUI parses this for visual timelines.”

11. Security & Access Controls (optional, common placement)

If a step interacts with sensitive data, API keys, or repositories, define:

Permissions required

Token scopes

Security validation gates (e.g., secret scans, compliance policies)

(This section appears here for consistency but can be omitted if not relevant.)

12. Integration Points (External Systems / Tools)

Define where this step interfaces with other systems — CI/CD, GitHub, monitoring dashboards, or other AI CLIs.

APIs used

Communication patterns (e.g., stdio pipes, shared files, sockets)

Data exchange formats (JSON, CSV, YAML)

13. Deliverables & Verification Tests (Step-Specific)

For steps that produce measurable results or milestones, define:

Expected deliverables (e.g., “function X implemented, doc Y generated”)

Verification method (unit tests, static checks, manual review)

Links to deliverable schemas or validation definitions

14. Risks, Constraints, and Notes

Capture anything that could limit reliability, scalability, or repeatability.
Also use this section for historical or contextual remarks that may explain design choices.

15. Related Artifacts & References

Cross-reference supporting files, prior steps, or schemas.

Example: “See ATW-05: Merge Phase for dependent commit logic.”

“Schema: /schemas/validation_event.schema.json.”

16. Revision History
Version	Date	Author	Description
1.0	2025-10-14	System Architect	Initial draft
1.1	—	—	—
🧩 Guiding Principles for Using This Framework

Sequence Consistency:

Sections 1–8 are always present and always in the same order.

Sections 9–16 are optional extensions, but if included, they appear in fixed sequence.

Injection Rules:

Custom, step-specific sections are inserted after the “Actions” section but before “Outputs” if they describe intermediate behavior.

Alternatively, append them after “Outputs” if they extend reporting or validation logic.

Example: a “Machine Learning Considerations” or “AI Behavior Notes” section could appear between Actions and Outputs.

Narrative First, Code Optional:

Prioritize clear explanations of intent, flow, and guarantees over implementation details.

When examples are useful, include them in callouts or collapsible sections (<details> blocks) to keep readability.

Machine-Readable Companion Files:

Each document can have a .meta.json file containing IDs, dependencies, and schemas, enabling automation or GUI parsing.

Scalability & Reuse:

Keep the same structure for top-level workflows (Prompt → Ship) and sub-processes (e.g., Code Gate Loop, Merge Queue).

This allows nested or linked documentation to be generated automatically.

✅ Example Partial Layout (for “Validate Phase”)

Overview

Objectives & Deterministic Guarantees

Inputs

Actions

Pre-checks

Execution Flow

Conditional Paths

Outputs

Dependencies & Preconditions

Postconditions

Error Handling

Logging & Observability

Integration Points

Deliverables & Verification Tests

Related Artifacts

Revision History

📘 Summary: Why This Structure Works
Design Goal	Solution
Consistency	Core section spine (1–8) appears in all steps.
Flexibility	Custom sections can be inserted in predefined slots.
Clarity	Narrative + metadata + output structure make documents readable.
Determinism	Inputs/Outputs/Dependencies enforce traceability.
Scalability	Works for any phase, from atomic task to macro workflow.
Tool Compatibility	Metadata can be parsed by automation, GUIs, or validation scripts.
