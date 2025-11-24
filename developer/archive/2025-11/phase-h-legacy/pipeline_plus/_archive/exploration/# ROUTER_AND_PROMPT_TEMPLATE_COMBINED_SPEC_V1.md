# ROUTER_AND_PROMPT_TEMPLATE_COMBINED_SPEC_V1

> **Purpose:** Single, machine-optimized reference that merges:
>
> * `Prompt_improve.md` (router/orchestrator + routing config design)
> * `Anthropic Prompt Guide → structure XML-ish thinking.md` (prompt structure + WORKSTREAM_V1.1 template)
>
> This file is intended for **agentic AI only** (no human readers) and preserves **all information** from both sources.

---

## 0. METADATA

* `source_files`:

  * `Prompt_improve.md`
  * `Anthropic Prompt Guide → structure XML-ish thinking.md`
* `domain`:

  * Multi-CLI AI task router
  * Workstream/task model
  * Routing config (YAML)
  * Timeout & safety behavior
  * Advanced features (metrics, priority, cost/latency)
  * Prompt design principles (Anthropic-style structure)
  * Universal **WORKSTREAM_V1.1** prompt template (ASCII-sectioned)
* `primary_use_cases`:

  * Implementing a **central headless router** for Codex / Claude / Aider / Ollama-Code / Copilot.
  * Generating **structured workstream prompts** that are:

    * Tool-agnostic (works with multiple CLI AIs)
    * Explicit about role, context, constraints, classification, and output format.
  * Supporting **agentic workflows**, delegation, retries, and self-healing.

---

## 1. INTEGRATED SUMMARY (FOR AGENTIC AI)

### 1.1 Router / Orchestrator – Core Idea

* Use a **central router/orchestrator** that:

  * Accepts **tasks** from any “source” app (Codex, Claude, Copilot, etc.).
  * Selects a **“worker”/target app** (Aider, Ollama Code, Claude, etc.) based on config.
  * Runs worker apps **headless**, capturing stdout/stderr and logs.
  * Applies **timeouts, retries, and delegation** rules from config.
* Fits naturally on top of existing patterns:

  * A script like `SubmitTask.ps1` emits task JSON into `.tasks/inbox`.
  * A long-running **QueueWorker / Router** process:

    * Reads these tasks.
    * Consults `router.config.yaml`.
    * Spawns selected CLI app.
    * Tracks logs, timeouts, and routing state.

### 1.2 Core Components

1. **Task Router / Orchestrator (central brain)**

   * Long-running process (Python/Node/Go) that:

     * Watches a **task queue** (files/JSONL/SQLite/message queue).
     * For each task:

       * Reads `source_app`, `capabilities`, routing constraints.
       * Picks `target app`.
       * Executes target **headless**.
       * Streams logs to central UI + persistent logs.
       * Applies **timeout / retry / reroute** policies.

2. **Task Queue**

   * Recommend simple JSON/JSONL spooler:

     * `.tasks/inbox/*.jsonl` → new tasks.
     * `.tasks/running/*.jsonl` → active tasks.
     * `.tasks/done/*.jsonl` → completed tasks.
     * `.tasks/failed/*.jsonl` → failed/timeout tasks.
   * Each file = **one task object** (JSON/JSONL).

3. **App Adapters**

   * Per CLI app:

     * Knows how to run CLI (command template, env vars, non-interactive flags).
     * Maps generic `Task` → concrete CLI arguments.
     * (Optional) parses outputs for telemetry (e.g., tests passed/failed).
   * Implementation choices:

     * Python classes (`AiderAdapter`, `CodexAdapter`…) OR
     * Pure config: `cmd_template`, env, capability tags.

4. **Config Loader & Registry**

   * Loads `router.config.yaml`.
   * Builds:

     * **AppRegistry** = apps, roles (source/target), capabilities, timeouts.
     * **RoutingPolicy** = default/fallback rules by:

       * `source_app`
       * `capability`
       * `global` settings (delegation, max hops, default timeouts).

5. **Audit & Logging**

   * Structured JSONL logs under `.runs/`:

     * `audit.jsonl` with events: `task_received`, `routed_to_app`, `process_started`, `stdout_chunk`, `timeout`, `retry_scheduled`, `completed`, `delegation_blocked`, etc.
   * Optional metrics (see §1.6).

### 1.3 Task Model & Routing Config

#### Task Schema (Conceptual)

* **Fields (example from doc):**

  * `task_id`: ULID or similar unique id.
  * `source_app`: who submitted the task (`codex`, `claude`, etc.).
  * `requested_target`: specific requested target app or `null`.
  * `capabilities`: semantic tags (`"refactor"`, `"python"`, etc.).
  * `description`: human-readable task summary.
  * `payload`:

    * `repo_path`: path to repo.
    * `files`: list of files.
    * `extra_cli_args`: optional extra arguments.
  * `constraints`:

    * `allow_delegation` (bool).
    * `must_stay_local` (bool).
    * `max_hops` (int).
  * `timeouts`:

    * `wall_clock_sec`
    * `idle_output_sec`
  * `routing_state`:

    * `current_target`
    * `route_history` (list of hops).
  * `retry_state`:

    * `attempt`
    * `max_attempts`
  * `metadata`:

    * `priority`
    * `created_at` timestamp.

#### Routing Config (router.config.yaml)

* Top-level sections:

  * `apps`: definitions for each CLI tool.
  * `routing`: global & per-source/capability routing rules.
  * `timeouts`: global timeout defaults & behavior.
  * `logging`: log level, format, paths.
  * `metadata`: optional app scoring (cost/latency/reliability).

* **App entries** specify:

  * `roles`: `[source, target]` / `[target]` etc.
  * `cmd_template`: CLI command pattern.
  * `default_model` (if applicable).
  * `capabilities`: what each app can do (e.g., `refactor`, `tests`, `docs`).
  * `allow_delegation_in` / `allow_delegation_out`.
  * `require_local_completion` (e.g., some apps must finish local).
  * `default_timeouts`: `wall_clock_sec`, `idle_output_sec`.
  * `retry`: `max_attempts`, `strategy` (`same_target`, `fallback`, `none`).

* **Routing rules**:

  * `global`:

    * `delegation_enabled` (bool).
    * `prevent_cycles` (bool).
    * `max_hops` (int).
    * default timeouts & timeout action.
  * `by_source`:

    * per-source `allow_delegation_out`, `require_local_completion`.
    * `preferred_targets_by_capability` mapping.
  * `by_capability`:

    * `default_targets`, `fallback_targets`, `max_attempts`.

* **Timeouts section**:

  * `default_wall_clock_sec`, `default_idle_output_sec`.
  * `on_timeout`:

    * `action_order`: e.g., `["retry", "fallback", "abort"]`.
    * `max_retries_total`.

* **Logging section**:

  * `level`: `debug|info|warn|error`.
  * `format`: `json|text`.
  * `log_dir`, `audit_log_path`.
  * `include_subprocess_output`, `include_task_payload`.

* **Metadata section**:

  * `app_scores` with:

    * `reliability`, `latency`, `cost` per app.

### 1.4 Execution & UX/DX

* **Headless delegation flow**:

  1. User or tool submits task (e.g., via `SubmitTask.ps1` or `taskctl submit`).
  2. Task is written to `.tasks/inbox` as JSON.
  3. Router:

     * Reads new task.
     * Resolves target app using config.
     * Spawns target CLI command:

       * e.g., `aider --yes --no-tty --model deepseek-coder src/pipeline.py`.
     * Captures logs and returns them to central console or TUI.

* **Example CLI usage** (router CLI `taskctl`):

  * Submit:

    ```bash
    taskctl submit \
      --source claude \
      --capability tests \
      --repo-path "C:/repo" \
      --description "Generate unit tests for foo.py" \
      --files foo.py \
      --allow-delegation
    ```
  * Watch tasks:

    ```bash
    taskctl watch
    ```
  * Inspect task:

    ```bash
    taskctl status <task_id> --details
    ```
  * Dry-run routing:

    ```bash
    taskctl route \
      --source codex \
      --capability refactor \
      --description "Big refactor" \
      --dry-run
    ```

### 1.5 Timeouts, Errors, Safety

* **Idle output timeout**:

  * If no stdout/stderr for `idle_output_sec`, assume stuck/waiting.
  * Router attempts graceful then hard terminate.

* **Wall clock timeout**:

  * Hard upper bound for total runtime (`wall_clock_sec`).

* **Interactive prompt detection (optional)**:

  * Inspect stdout for patterns like `?:`, `Press ENTER`, `y/n`.
  * If detected, treat as `needs_interaction`:

    * Fail or reroute according to policy.

* **Timeout/retry strategies**:

  * `retry` same target (`retry.strategy == "same_target"`).
  * `fallback` to other targets in `fallback_targets`.
  * `abort` when out of retries/fallbacks.

* **Preventing delegation loops**:

  * `route_history` (list of `(from, to, reason)` hops).
  * `prevent_cycles` flag: skip already-used targets.
  * `max_hops` global limit.
  * Per-task `allow_delegation` can be disabled after some hops.

### 1.6 Extras & Advanced Features

* **Metrics & dashboards**:

  * Emit metrics: `tasks_per_app`, `avg_runtime_sec`, `timeout_rate`, `failure_rate`.
  * Visualize via Prometheus/Grafana or simple TUI (e.g., `textual`).

* **Dry-run / simulation mode**:

  * `taskctl route --dry-run` to test routing decisions without execution.

* **Priority queues / scheduling**:

  * `metadata.priority` = `low|normal|high|urgent`.
  * Router chooses next task based on priority + age.
  * Optional concurrency limits per app: `apps[aider].concurrency_limit`.

* **Cost/latency-aware routing**:

  * Use `metadata.app_scores` to choose among multiple valid targets:

    * Highest reliability; then lowest cost; then lowest latency.

* **Rich audit logs**:

  * For each task:

    * Creator (source app/human).
    * All routing decisions + reasons.
    * Exact CLI command run (excluding secrets).
    * Exit code, durations, and partial outputs.

### 1.7 Implementation Guidance & Roadmap

* **Language recommendation**: Python.

  * CLI: `typer` or `click`.
  * Config: `pydantic` / `pydantic-settings` + `PyYAML`.
  * Process execution: `asyncio.create_subprocess_exec` or `subprocess.Popen`.
  * File watching: simple polling or `watchdog`.
  * Logging: `structlog` or `logging` with JSON formatting.
  * IDs: `ulid-py` for task IDs.

* **Phase 1 (MVP)**:

  1. Define minimal `Task` schema.
  2. Implement `router.config.yaml` with apps + basic routing.
  3. Build `taskctl`:

     * `submit`, `worker` (single-hop routing, headless execution + logs).
  4. Integrate `SubmitTask.ps1` to wrap `taskctl submit`.

* **Phase 2**:

  * Add route history + multi-hop delegation.
  * Implement idle timeout detection.
  * Add `taskctl watch` and `taskctl status`.
  * Add config toggles: `delegation_enabled`, per-app `allow_delegation_out`, `require_local_completion`.

* **Phase 3**:

  * Cost/latency/reliability scoring.
  * Priority queues & concurrency limits.
  * Metrics export and dashboard.
  * Dry-run / simulation enhancements.

* **Next-step suggestions from original text**:

  * Translate into concrete JSON task schema + first router config tailored to actual tools (Aider + Ollama + Codex + Claude Code CLI).
  * Sketch minimal `taskctl worker` prototype that plugs into existing `.tasks/inbox` + `SubmitTask.ps1`.

---

## 2. PROMPT STRUCTURE & WORKSTREAM TEMPLATE (ANTHROPIC-STYLE)

### 2.1 Key Ideas From Anthropic-Style Prompt Guide

* **Be explicit and detailed**:

  * Spell out instructions, context, and success criteria.
* **Use section tags / structure**:

  * e.g. `<instructions>`, `<context>`, `<examples>`, `<thinking>`, `<answer>` in conceptual XML.
  * For CLI universality: prefer ASCII forms like `[INSTRUCTIONS]`, `[CONTEXT]`, `[OUTPUT_FORMAT]`, `[REASONING]`.
* **Chain-of-thought**:

  * Use step-by-step reasoning when the task is complex.
  * Do **not** always force full chain-of-thought for simple tasks.
* **Few-shot examples**:

  * Use 3–5 examples when behavior is subtle or requires pattern-learning.

### 2.2 3C Pattern & Persona

* **3C = Clarity, Context, Constraints**:

  * **Clarity**: explicitly state what to do, success criteria.
  * **Context**: environment, repo, subsystem, why now.
  * **Constraints**: format, length, safety bounds, disallowed changes.
* **Persona**:

  * Very effective to set a role:

    * e.g. `ROLE: Senior {language}/{domain} engineer and careful refactoring assistant.`
* **Implication**:

  * Make **3C + Persona** first-class fields in prompt format:

    * `ROLE: ...`
    * `[OBJECTIVE]` or `OBJECTIVE: ...`
    * `[CONTEXT]`
    * `[CONSTRAINTS]`

### 2.3 Agentic AI References (Classification & Self-Healing)

* Concepts pulled from PRR / agentic references:

  * Task analysis block with **classification**:

    * Complexity, domain, quality tier, time constraint.
  * Explicit **output spec + validation gates**:

    * Contract for what “done” means.
  * Self-healing loops:

    * `max_iterations`, `confidence_threshold`, error detection & validation.
  * Separation into phases:

    * Intake/analysis → Plan/reasoning → Execution → Validation/self-critique.

* **Implications for template**:

  * Add **classification mini-block**:

    * `COMPLEXITY: simple|moderate|complex|enterprise`
    * `QUALITY_TIER: standard|production`
    * `domain: code|docs|analysis`
  * Add **VALIDATION** section:

    * Checklist of what to verify before final answer.
  * Add `SELF_CHECK` knob:

    * e.g. `SELF_CHECK: yes|no` plus a brief description.

### 2.4 Concrete Improvements to the Universal Workstream Template

1. **Explicit persona (ROLE)**:

   * Add `ROLE: ...` at top to define behavior and domain.

2. **First-class 3C sections**:

   * `[OBJECTIVE]`: 1–3 explicit sentences.
   * `[CONTEXT]`: ~3–7 lines with key project data.
   * `[CONSTRAINTS]`: bullet list for must / must-not rules.

3. **Classification block**:

   * Unified `CLASSIFICATION` line:

     ```text
     CLASSIFICATION: complexity={simple|moderate|complex|enterprise}; quality={standard|production}; domain={code|docs|analysis}
     ```
   * Router can use this for:

     * Scheduling
     * Timeouts
   * Model can use this to:

     * Decide amount of reasoning and caution.

4. **Output spec as contract**:

   * Add `[OUTPUT_FORMAT]` section with:

     * Primary format (`markdown`, `plain_text`, `json`).
     * Required sections & order:

       * e.g., `CHANGES_SUMMARY`, `IMPLEMENTATION_NOTES`, `RISK_CHECKS`, `NEXT_STEPS`.

5. **Reasoning mode & self-check**:

   * Add `[REASONING_MODE]`:

     * `Mode: step_by_step|concise`
     * If `step_by_step`, list plan steps before answer.
   * Add `[VALIDATION]`:

     * Checklist verifying constraints, syntax, tests, etc.
     * Behavior on ambiguity:

       * Output `CLARIFICATION_NEEDED: ...` only.

6. **Examples as optional**:

   * `[EXAMPLE_TASKS]`:

     * Usually empty.
     * Optionally 1–2 short good/bad microexamples.

### 2.5 Revised Slim ASCII Universal Workstream Template (WORKSTREAM_V1.1)

The doc defines a **canonical, ASCII-only template** suitable as universal workstream prompt for Aider / Codex / Claude / Copilot / Gemini / Ollama-Code.

Full template:

```text
=== WORKSTREAM_V1.1 ===

[HEADER]
WORKSTREAM_ID: {{workstream_id}}
CALLING_APP: {{source_app}}        # e.g. codex-cli, claude-code, aider, etc.
TARGET_APP: {{target_app}}        # e.g. aider, codex-cli, claude-code
REPO_ROOT: {{repo_path}}
ENTRY_FILES: {{primary_files_or_globs}}

ROLE: {{persona_line}}            # e.g. "Senior Python engineer and careful refactoring assistant."

CLASSIFICATION: complexity={{simple|moderate|complex|enterprise}}; quality={{standard|production}}; domain={{code|docs|analysis}}

[OBJECTIVE]
{{1–3 sentences, explicit & measurable goal}}

[CONTEXT]
- Project: {{project_name_or_subsystem}}
- Current state: {{short description of what exists today}}
- Why this workstream: {{reason / triggering event}}
- Relevant architecture/constraints: {{e.g. hexagonal, feature-flagged, no breaking changes}}
- Related tickets/links: {{optional}}

[CONSTRAINTS]
- Must:
  - {{bullet 1 – hard requirements}}
  - {{bullet 2}}
- Must NOT:
  - {{bullet 1 – prohibited behaviors (e.g., no new external deps)}}
  - {{bullet 2}}
- Safety:
  - Prefer minimal, well-scoped changes
  - Preserve existing behavior unless explicitly requested

[TASK_BREAKDOWN]
- Main task type: {{refactor|implement_feature|write_tests|analysis|docs}}
- Suggested steps:
  1) {{step 1}}
  2) {{step 2}}
  3) {{step 3}}
- Focus areas:
  - {{specific files/functions/modules}}

[REASONING_MODE]
- Mode: {{step_by_step|concise}}
- If step_by_step: briefly outline your plan, then apply it.

[OUTPUT_FORMAT]
- Primary format: {{markdown|plain_text|json}}
- Required sections in the final answer:
  1) CHANGES_SUMMARY
  2) IMPLEMENTATION_NOTES
  3) RISK_CHECKS
  4) NEXT_STEPS (if any)
- If code is shown, include only the minimal necessary snippets or unified diffs.

[VALIDATION]
- Before final answer, self-check that:
  - [ ] All constraints in [CONSTRAINTS] are satisfied.
  - [ ] The proposed changes are consistent with the [OBJECTIVE].
  - [ ] No obvious syntax or structural errors are present.
- If you detect blocking ambiguity, STOP and output only:
  "CLARIFICATION_NEEDED: {{your concise questions}}"

[EXAMPLE_TASKS]   # optional; usually empty
- Example_good:
  - Objective: "Refactor function X to remove duplication with Y while keeping behavior identical."
  - Constraints: "No new deps, keep public API unchanged."
- Example_bad:
  - "Rewrite the whole module from scratch" (too broad, violates minimal change principle).

[EXECUTION_NOTES_FOR_ROUTER]
- Preferred timeout_seconds: {{default_for_this_class}}
- Retry_on_failure: {{true|false}}
- Escalation_hint: if this tool cannot complete due to limits, recommend a follow-up workstream for {{more_powerful_app}}

=== END_WORKSTREAM_V1.1 ===
```

### 2.6 Why the Template Is Universal and Agent-Friendly

* **Pure ASCII**:

  * No XML or JSON required for base parsing.
* **Sectioned**:

  * `[CONTEXT]`, `[CONSTRAINTS]`, `[OUTPUT_FORMAT]`, etc.
  * Easy for router/agents to parse via regex on section headers.
* **Supports router + prompt design**:

  * `CLASSIFICATION` and `[EXECUTION_NOTES_FOR_ROUTER]` can be parsed into task registry and scheduler.
  * Clear separation of:

    * Meta (`[HEADER]`).
    * Task semantics (`[OBJECTIVE]`, `[CONTEXT]`, `[TASK_BREAKDOWN]`).
    * Execution & validation (`[REASONING_MODE]`, `[VALIDATION]`).
    * Router hints (`[EXECUTION_NOTES_FOR_ROUTER]`).

### 2.7 Direct Answer (Preserved From Source)

* The Anthropic-style guide and agentic references:

  * **Do** strengthen the prompt template.
  * Validate the approach of:

    * Explicit role/persona and 3C (clarity, context, constraints).
    * Adding classification + output contracts + validation hooks.
    * Adding reasoning + self-check layer that works well with error pipeline and agentic design.

---

## 3. FULL SOURCE: Prompt_improve.md

> **Note:** This section reproduces the entire original `Prompt_improve.md` content to guarantee no information loss. It is already reasonably structured for both human and machine; the integrated summary above provides a higher-level view.

---

1. **High-level architecture**
2. **Task model & routing config (with YAML example)**
3. **Execution & UX/DX (what you type / what you see)**
4. **Timeouts, errors, and safety**
5. **Extra features you probably want**
6. **Implementation guidance & roadmap**

---

## 1. High-Level Architecture

### 1.1 Core idea

Use a **central router/orchestrator** that:

* Accepts tasks from any “source” app (Codex, Claude, Copilot, etc.)
* Decides which “worker” app should actually execute the task (Aider, Ollama Code, Claude, etc.)
* Runs worker apps **headless** and streams their output back into one centralized interface.
* Uses a **config file** for:

  * Which apps exist and how to run them
  * Which capabilities they offer (refactor/tests/analysis/etc.)
  * Delegation rules, timeouts, retries

This fits neatly on top of what you already have:

* **SubmitTask.ps1** (or similar) → writes a JSON task into `.tasks/inbox`.
* **QueueWorker / Router** → reads those tasks, consults config, spawns the correct CLI app, tracks logs, timeouts, delegation.

### 1.2 Components

**1. Task Router / Orchestrator (central brain)**
A long-running process (Python/Node/Go) that:

* Watches a queue (JSONL files / SQLite / message queue).
* For each task:

  * Reads `source`, `capabilities`, and options (allow_delegation, must_stay_local, etc.).
  * Picks a target app using the routing config.
  * Executes the target app headless.
  * Streams logs into one place.
  * Handles timeout/ retry/ reroute according to config.

**2. Task Queue**

You can keep your existing **JSONL spooler** pattern:

* `.tasks/inbox/*.jsonl` → new tasks
* `.tasks/running/*.jsonl` → currently executing tasks
* `.tasks/done/*.jsonl` → completed
* `.tasks/failed/*.jsonl` → failed / timeout

Each file is a **single task JSON** (or JSONL if you like).

**3. App Adapters**

Each CLI app gets a small adapter:

* Knows *how* to run the CLI:

  * Command template (e.g., `aider --yes --no-tty --model {model} {extra_args}`)
  * Environment variables (API keys, OLLAMA_API_BASE, etc.)
  * Non-interactive flags.
* Translates a generic `Task` → concrete CLI arguments for that app.
* (Optional) parses output for richer telemetry (e.g., “tests passed/failed”).

You can implement adapters as:

* Python classes (e.g., `AiderAdapter`, `CodexAdapter`).
* Or a table in config with `cmd_template` and some adapter hints.

**4. Config Loader & Registry**

A module that:

* Loads `router.config.yaml`.
* Builds an in-memory **AppRegistry**:

  * Which apps exist, roles (source/target), capabilities, timeouts.
* Builds a **RoutingPolicy** object from config:

  * Default rules by capability.
  * Overrides by source app.
  * Delegation toggles.

**5. Audit & Logging**

* JSONL structured logs: `.runs/audit.jsonl`
* Each entry: `{timestamp, task_id, event, app, data...}`
  Example events: `task_received`, `routed_to_app`, `process_started`, `stdout_chunk`, `timeout`, `retry_scheduled`, `completed`, `delegation_blocked`, etc.

---

## 2. Task Model & Routing Config

### 2.1 Task schema (conceptual)

A single task object (JSON) might look like:

```jsonc
{
  "task_id": "01J2XYZR5HA1Q5J9341ZWZ8NRY",
  "source_app": "codex",
  "requested_target": null,
  "capabilities": ["refactor", "python"],
  "description": "Refactor src/pipeline.py for clarity and add docstrings.",
  "payload": {
    "repo_path": "C:/Users/richg/ALL_AI/Complete AI Development Pipeline – Canonical Phase Plan",
    "files": ["src/pipeline.py"],
    "extra_cli_args": []
  },
  "constraints": {
    "allow_delegation": true,
    "must_stay_local": false,
    "max_hops": 3
  },
  "timeouts": {
    "wall_clock_sec": 900,
    "idle_output_sec": 120
  },
  "routing_state": {
    "current_target": null,
    "route_history": []
  },
  "retry_state": {
    "attempt": 0,
    "max_attempts": 2
  },
  "metadata": {
    "priority": "normal",
    "created_at": "2025-11-19T18:00:00Z"
  }
}
```

Your existing `SubmitTask.ps1` can be extended to emit something like this.

---

### 2.2 Example YAML config

Below is a **sample `router.config.yaml`** that covers:

* Apps registry (with capabilities, delegation flags, timeouts)
* Routing rules (by source and capability)
* Global delegation / timeout behavior
* Logging and extensibility

```yaml
# router.config.yaml

apps:
  aider:
    roles: [source, target]          # can submit and receive tasks
    cmd_template: >
      aider --yes --no-tty --model {model} {extra_args}
    default_model: deepseek-coder
    capabilities:
      - refactor
      - tests
      - docs
    allow_delegation_in: true
    allow_delegation_out: true
    require_local_completion: false
    default_timeouts:
      wall_clock_sec: 900
      idle_output_sec: 120
    retry:
      max_attempts: 1
      strategy: "same_target"

  codex:
    roles: [source, target]
    cmd_template: >
      codex --non-interactive {extra_args}
    capabilities:
      - refactor
      - scaffolding
      - analysis
    allow_delegation_in: true
    allow_delegation_out: true
    require_local_completion: false
    default_timeouts:
      wall_clock_sec: 600
      idle_output_sec: 90
    retry:
      max_attempts: 0
      strategy: "none"

  claude:
    roles: [source, target]
    cmd_template: >
      claude --repo {repo_path} {extra_args}
    capabilities:
      - analysis
      - tests
      - docs
    allow_delegation_in: true
    allow_delegation_out: true
    require_local_completion: false
    default_timeouts:
      wall_clock_sec: 1200
      idle_output_sec: 180
    retry:
      max_attempts: 1
      strategy: "fallback"

  copilot:
    roles: [source, target]
    cmd_template: >
      copilot-cli run {extra_args}
    capabilities:
      - refactor
      - suggestions
    allow_delegation_in: true
    allow_delegation_out: false     # e.g., only runs what it gets, no further delegation
    require_local_completion: true
    default_timeouts:
      wall_clock_sec: 600
      idle_output_sec: 120
    retry:
      max_attempts: 0
      strategy: "none"

  ollama_code:
    roles: [target]
    cmd_template: >
      ollama-code --model {model} {extra_args}
    default_model: deepseek-coder
    capabilities:
      - refactor
      - bulk-edits
    allow_delegation_in: true
    allow_delegation_out: false
    require_local_completion: true
    default_timeouts:
      wall_clock_sec: 900
      idle_output_sec: 120
    retry:
      max_attempts: 1
      strategy: "same_target"

routing:
  global:
    delegation_enabled: true
    prevent_cycles: true
    max_hops: 3
    default_wall_clock_sec: 900
    default_idle_output_sec: 120
    default_timeout_action: "fallback"   # abort | retry | fallback

  # Per-source overrides
  by_source:
    codex:
      allow_delegation_out: true
      require_local_completion: false
      preferred_targets_by_capability:
        refactor: [aider, ollama_code]
        tests: [claude]
        analysis: [claude, codex]

    claude:
      allow_delegation_out: true
      preferred_targets_by_capability:
        refactor: [aider]
        tests: [claude]
        docs: [claude]

    aider:
      allow_delegation_out: true
      preferred_targets_by_capability:
        bulk-edits: [ollama_code]

  # Capability-level defaults (used when no source-specific rule)
  by_capability:
    refactor:
      default_targets: [aider, codex]
      fallback_targets: [claude]
      max_attempts: 2
    tests:
      default_targets: [claude]
      fallback_targets: [aider]
    analysis:
      default_targets: [claude, codex]
      fallback_targets: []
    docs:
      default_targets: [claude, aider]
      fallback_targets: []

timeouts:
  # Global behavior if not overridden at app or task level
  default_wall_clock_sec: 900
  default_idle_output_sec: 120
  on_timeout:
    # What to do when a timeout hits
    action_order: ["retry", "fallback", "abort"]
    max_retries_total: 2

logging:
  level: info            # debug | info | warn | error
  format: json           # json | text
  log_dir: ".runs/logs"
  audit_log_path: ".runs/audit.jsonl"
  include_subprocess_output: true
  include_task_payload: false   # for privacy; can be toggled

# Future extensibility
metadata:
  # Optional hints router can use later (cost/latency/reliability)
  app_scores:
    aider:
      reliability: 0.9
      latency: 0.4
      cost: 0.1
    codex:
      reliability: 0.8
      latency: 0.6
      cost: 0.2
    claude:
      reliability: 0.95
      latency: 0.5
      cost: 0.3
```

### 2.3 How the router uses config at runtime

For each task:

1. **Identify source + capabilities**

   * Use `task.source_app` and `task.capabilities` (or infer from tags like `task.description`, file types, etc.).

2. **Check delegation toggles**

   * If `routing.global.delegation_enabled` is `false` → run on `source_app` only.
   * If the task has `constraints.allow_delegation == false` → no delegation for this task.
   * If `source_app` has `require_local_completion == true` in config → always run locally, no delegation.

3. **Build candidate target list**

   * From `routing.by_source[source].preferred_targets_by_capability[capability]` if exists.
   * Else from `routing.by_capability[capability].default_targets`.
   * Filter to apps where:

     * `roles` includes `target`
     * `allow_delegation_in == true`
     * Not already in `task.routing_state.route_history` (to prevent loops if configured).

4. **Pick best target**

   * Usually: first candidate.
   * Can later use `metadata.app_scores` (reliability/cost/latency) to pick.

5. **Merge timeouts**

   * Start from `apps[target].default_timeouts`.
   * Override with `task.timeouts` if set.
   * Override with `routing.timeout` defaults if needed.

6. **Execute & monitor**

   * Spawn CLI using `apps[target].cmd_template`.
   * Stream stdout/stderr to logs and to the main UI.
   * Apply idle and wall_clock timeouts.

7. **On completion/timeout/error**

   * Update `routing_state.route_history` with `(source → target)` hop.
   * If success → mark `done`, log audit entries.
   * If failure/timeout → follow `timeouts.on_timeout.action_order`:

     * Try `retry` (if under `max_retries`).
     * Then `fallback` (choose next target from `fallback_targets`).
     * Then `abort` (mark failed, stop routing).

---

## 3. Execution & UX / DX

### 3.1 Headless delegation in practice

Assume you have a CLI tool called `taskctl` (part of the router) and your existing PowerShell script `SubmitTask.ps1` wraps it.

#### Example: Codex delegates a refactor to Aider

User runs Codex CLI like usual, but uses a helper to submit a delegatable task:

```powershell
pwsh -File scripts/SubmitTask.ps1 `
  -Tool router `
  -Args @(
    "submit",
    "--source", "codex",
    "--capability", "refactor",
    "--repo-path", "C:/Users/richg/ALL_AI/Complete AI Development Pipeline – Canonical Phase Plan",
    "--files", "src/pipeline.py",
    "--description", "Refactor pipeline for clarity and add docstrings",
    "--allow-delegation"
  )
```

Behind the scenes:

1. `SubmitTask.ps1` writes a fully-formed `task.json` into `.tasks/inbox/`.

2. The router (already running) detects the new task, loads it.

3. Using config, it decides: `source=codex`, `capability=refactor` → primary target `aider`.

4. Router starts `aider` using:

   ```bash
   aider --yes --no-tty --model deepseek-coder src/pipeline.py
   ```

5. Router simultaneously:

   * Captures `stdout/stderr` from Aider.
   * Writes them to `.runs/logs/task-01J2XYZR5H.log`.
   * Streams key lines back to a main TUI or plain console, e.g.:

   ```text
   [TASK 01J2XYZR5H] Source=codex Capabilities=[refactor,python]
   [ROUTER] Routing to target app: aider (timeout=900s, idle_timeout=120s)
   [aider] Adding file: src/pipeline.py
   [aider] Proposed changes:
   [aider] - Added docstrings to Pipeline class
   [aider] - Simplified error handling
   [aider] Applying changes...
   [aider] Done. No tests to run.
   [ROUTER] Task 01J2XYZR5H completed with status=success (duration=42s)
   ```

User only needs to look at **one interface**; they don’t have to open Aider separately.

### 3.2 CLI flows for the user

A couple of user-facing commands (for your router CLI):

```bash
# Submit a task directly
taskctl submit \
  --source claude \
  --capability tests \
  --repo-path "C:/repo" \
  --description "Generate unit tests for foo.py" \
  --files foo.py \
  --allow-delegation

# Watch tasks
taskctl watch   # tails logs for active tasks

# Inspect a specific task
taskctl status 01J2XYZR5H --details

# Dry-run routing (no execution, just show which app would get it)
taskctl route \
  --source codex \
  --capability refactor \
  --description "Big refactor" \
  --dry-run
```

---

## 4. Timeouts, Errors, Safety

### 4.1 Detecting “stuck” tasks

**Basic, robust signals:**

1. **Idle output timeout**

   * No stdout/stderr from subprocess for `idle_output_sec` → consider it stuck or waiting for input.
   * Router can:

     * Send a gentle terminate (`SIGTERM` / process.kill or `taskkill /PID` on Windows).
     * If no exit, send hard kill.

2. **Wall clock timeout**

   * Hard upper bound: total runtime exceeds `wall_clock_sec`.
   * Same behavior: terminate, then act according to config.

3. **Interactive prompt detection (optional)**

   * Router can inspect stdout for common prompt patterns:

     * `?:`, `Press ENTER`, `y/n`, etc.
   * If seen, treat as “stuck awaiting user input” → mark task as `needs_interaction` and either:

     * Fail fast, or
     * Attempt reroute to an app that’s better at headless mode.

### 4.2 Strategies for timeouts & retries

Based on `timeouts.on_timeout` and per-app `retry` config:

* **Retry same target**

  * If `retry.strategy == "same_target"`, increment attempt and rerun with same app.
  * Example: small network blip.

* **Fallback target**

  * If primary fails, choose next in `fallback_targets`.
  * Example: `ollama_code` fails → fallback to `aider`.

* **Abort**

  * When out of retries or no fallbacks left:

    * Mark `task.status = "failed_timeout"`.
    * Log full context into audit log.
    * Optionally emit a follow-up task for “postmortem analysis”.

### 4.3 Preventing delegation loops / runaways

Mechanisms:

1. **Route history**

   * `task.routing_state.route_history` is an ordered list of `{from, to, reason}` hops.
   * Before delegating, router checks:

     * If proposed `target` already in history and `routing.global.prevent_cycles == true`, skip that target.

2. **Global hop limit**

   * `routing.global.max_hops` (e.g., 3).
   * If `route_history.length >= max_hops`, block further delegation, mark as failed or partial.

3. **Per-task flag**

   * `constraints.allow_delegation` can be switched off permanently after one or two hops using policy (e.g., “once escalated to Claude, no further delegation”).

---

## 5. Things You Haven’t Mentioned (But Will Want)

Here are some high-leverage extras.

### 5.1 Metrics & dashboards

* Emit metrics to Prometheus or a simple JSON file:

  * tasks_per_app
  * avg_runtime_sec per app/capability
  * timeout_rate
  * failure_rate per routing path (e.g., codex→aider vs claude→aider)
* Then:

  * Use Grafana or a simple TUI dashboard to spot problematic tools or configs.

### 5.2 Dry-run / simulation mode

* `taskctl route --dry-run`:

  * Uses config and a synthetic task to show:

    * Which app would run.
    * Timeouts.
    * Fallback plan if it fails.
* Great for:

  * Testing config changes before you trust them.
  * Teaching future-you how routing behaves.

### 5.3 Priority queues / scheduling

* Extend tasks with `metadata.priority` (`low`, `normal`, `high`, `urgent`).
* Router picks next task using:

  * Priority + age (to avoid starvation).
* Optionally:

  * Concurrency limits per app (`apps[aider].concurrency_limit: 2`).

### 5.4 Cost / latency-aware routing

* Use `metadata.app_scores` (cost/latency/reliability) from config.
* Routing heuristic could be:

  * Prefer highest **reliability**, then lowest **cost**, then lowest **latency**.
* This becomes powerful when you mix local tools (0 cost, slower) with cloud tools (costly but faster/stronger).

### 5.5 Rich audit logs

* For each task, keep an audit trail:

  * Who created it (source app + optional human).
  * Each routing decision + reason.
  * Exact CLI command run (minus secrets).
  * Exit code, durations, partial outputs.
* This makes debugging and post-mortem analysis much easier, especially when multiple agents are involved.

---

## 6. Implementation Guidance & Roadmap

### 6.1 Tech recommendations

Given your stack and preferences, I’d suggest:

**Language:** Python

* **CLI:** `typer` or `click`
* **Config:** `pydantic` or `pydantic-settings` + `PyYAML`
* **Process execution:** `asyncio.create_subprocess_exec` or `subprocess.Popen` with nonblocking read.
* **File watching for queue:** simple polling loop, or `watchdog` if you want event-based.
* **Logging:** `structlog` or standard `logging` with JSON formatter; write to `.runs/audit.jsonl`.
* **IDs:** `ulid-py` for ULID task IDs.

This keeps it portable across Windows/WSL and fits neatly into your existing PowerShell world.

### 6.2 MVP (Phase 1)

Goal: **Single-hop routing with headless execution and logs**

1. **Define Task schema**

   * Minimal fields: `task_id`, `source_app`, `capabilities`, `description`, `payload.repo_path`, `payload.files`, `constraints.allow_delegation`.

2. **Implement `router.config.yaml` with apps + basic routing**

   * Aider, Codex, Claude entries.
   * Simple `routing.by_source` and `routing.by_capability`.

3. **Build `taskctl` CLI**

   * `taskctl submit` → writes JSON into `.tasks/inbox`.
   * `taskctl worker` → long-running loop:

     * Read tasks from `.tasks/inbox`.
     * Route to single target (no delegation chaining yet).
     * Run CLI app headless with timeouts.
     * Write logs and move task to `.tasks/done` / `.tasks/failed`.

4. **Integrate with your existing `SubmitTask.ps1`**

   * Wrap `taskctl submit` so your Codex/Claude flows don’t change much.

### 6.3 Iteration 2 (Phase 2)

Goal: **Delegation, retries, better UX**

1. **Add route history + multi-hop delegation**

   * Implement `route_history` and `max_hops`.
   * Enable fallback targets on failure/timeout.

2. **Idle output detection**

   * Nonblocking read from subprocess.
   * Timer that resets on each stdout/stderr chunk.
   * Timeout = kill + retry/fallback.

3. **`taskctl watch` & `taskctl status`**

   * Show live progress per task.
   * Summaries of last N tasks (who handled what, how long, result).

4. **Configuration toggles**

   * `delegation_enabled` global.
   * per-app `allow_delegation_out`, `require_local_completion`.

### 6.4 Iteration 3 (Phase 3)

Goal: **Advanced features & intelligence**

1. **Cost/latency/reliability scoring**

   * Use `metadata.app_scores` to choose best target among several.

2. **Priority queues + concurrency limits**

   * Per-app concurrency (avoid overloading Aider/DeepSeek).
   * Priority scheduler (`urgent` tasks jump the line).

3. **Metrics & dashboard**

   * Export metrics to Prometheus or just write a compact metrics JSON.
   * Optional TUI dashboard using `textual` to view tasks and app stats.

4. **Dry-run / simulation mode**

   * `taskctl route --dry-run` to visualize routing without actually running CLIs.

---

If you’d like, next step I can:

* Translate this into a **concrete JSON task schema** + **first `router.config.yaml`** tailored to your exact tools (Aider+Ollama+Codex+Claude Code CLI).
* Or sketch a **minimal Python `taskctl worker` prototype** that plugs into your existing `.tasks/inbox` + `SubmitTask.ps1` pattern.

---

## 4. FULL SOURCE: Anthropic Prompt Guide → structure XML-ish thinking.md

> **Note:** This section reproduces the entire original `Anthropic Prompt Guide → structure XML-ish thinking.md` content for completeness.

---

````markdown
---

## 1. What the attached references add

### a) Anthropic Prompt Guide → structure, XML-ish thinking, examples

Key ideas:

* Be explicit and detailed; spell out instructions, context, and success criteria.
* Use **tags/sections** (`<instructions>`, `<context>`, `<examples>`, `<thinking>`, `<answer>`) to separate concerns and make the response parseable/consistent.
* Use chain-of-thought / “think step-by-step” where complexity is high, NOT necessarily on every task.
* Provide 3–5 examples when behavior is subtle.

**Implication for your template:**
We *don’t* want full XML (for CLI universality), but we *do* want very clear, consistent sections that mirror those tags in plain ASCII (`[INSTRUCTIONS]`, `[CONTEXT]`, `[OUTPUT_FORMAT]`, `[REASONING]`).

---

### b) “High-Quality Prompts” & “Core of a Good Prompt” → 3C pattern & persona

They hammer the same triad repeatedly: **Clarity, Context, Constraints**.

* Clarity/specificity: say exactly what to do.
* Context: who is this for, why, what environment.
* Constraints: what to include / exclude, format, length, etc.
* Persona / role (“You are a senior X…”) is *very* effective.
* Few-shot and chain-of-thought are advanced knobs, not mandatory, but really help for tricky tasks.

**Implication for your template:**
We should make **3C + Persona** *first-class fields*:

* `ROLE:` or `[ROLE]`
* `OBJECTIVE:` (clarity)
* `[CONTEXT]`
* `[CONSTRAINTS]`

---

### c) Agentic AI refs (PRR prompt ref + agentic reference) → self-healing & workflow semantics

These two are overkill for a single prompt, but they give nice patterns for:

* Task analysis block with **classification** (complexity, domain, quality tier, time constraint).
* Explicit **output spec** and **validation gates** – contract for what “done” means.
* Self-healing loops with `max_iterations`, `confidence_threshold`, error detection & validation.
* Separation between:

  * Intake / analysis
  * Plan / reasoning
  * Execution
  * Validation / self-critique

**Implication for your template:**

* Add a tiny **classification mini-block** that routers and tools can use:

  * `COMPLEXITY: simple|moderate|complex|enterprise`
  * `QUALITY_TIER: standard|production`
* Add a **VALIDATION** section: what the tool should check before declaring success.
* Add an optional **SELF_REVIEW** line like: `SELF_CHECK: yes|no` with a one-liner of what to verify.

---

## 2. Concrete improvements to your universal workstream template

Your current “slim ASCII v1” template is already good on:

* having one canonical structure
* separating meta vs task vs context
* being pure text (universal for Aider, Codex, Claude, Copilot, Ollama Code, etc.)

What these docs suggest we add (still slim, still ASCII):

### (1) Make persona explicit

Add a **ROLE** field at the top:

```text
ROLE: Senior {language}/{domain} engineer and careful refactoring assistant.
````

This is cheap and helps *every* model immediately shift into the right mode.

---

### (2) Bake in the “3 Cs”

Instead of burying them, we give each its own section:

* `[OBJECTIVE]` – short, single sentence of what success is.
* `[CONTEXT]` – 3–7 lines: repo, subsystem, why now, constraints.
* `[CONSTRAINTS]` – bullets: what to obey / avoid (no breaking tests, no new deps, etc.).

---

### (3) Small classification block for router + models

Borrowing from PRR’s `<classification>` section, compress to one line:

```text
CLASSIFICATION: complexity={simple|moderate|complex|enterprise}; quality={standard|production}; domain={code|docs|analysis}
```

* Routers can use this for scheduling / timeouts.
* Models can use it to scale their effort (e.g., more reasoning for `complex+production`).

---

### (4) Output spec as a contract

Add a strict `[OUTPUT_FORMAT]` section:

* specify **format** (markdown, plain text, JSON)
* specify **sections** that must be present (e.g. `CHANGES_SUMMARY`, `PATCH_EXPLANATION`, `NOTES`)

Example:

```text
[OUTPUT_FORMAT]
- Primary format: markdown
- Required sections (in order):
  1) CHANGES_SUMMARY (bullet list)
  2) IMPLEMENTATION_NOTES (short prose)
  3) RISK_CHECKS (bullets)
```

---

### (5) Reasoning + self-check knobs, but still minimal

Instead of heavy XML, just:

```text
[REASONING_MODE]
- For this task: {step_by_step|concise}
- If step_by_step: list key steps before presenting final answer.
```

And a tiny validation:

```text
[VALIDATION]
- Before final answer, verify:
  - [ ] All constraints honoured
  - [ ] No syntax errors in changed files
  - [ ] Tests referenced in this prompt still pass conceptually
```

This lines up well with your self-healing error pipeline pattern and the agentic references.

---

### (6) Keep examples optional + lightweight

All the docs like 3–5 examples, but examples are token-heavy.

Recommendation:

* Add an optional `[EXAMPLE_TASKS]` section that’s usually either:

  * empty, or
  * 1–2 **very short** “good vs bad” micro examples.

That way you keep “slim by default” but have a place to inject few-shot when it really matters.

---

## 3. Revised “SLIM ASCII V1.1” universal workstream template

Your current “slim ASCII v1” template is already good on:

* having one canonical structure
* separating meta vs task vs context
* being pure text (universal for Aider, Codex, Claude, Copilot, Ollama Code, etc.)

What these docs suggest we add (still slim, still ASCII):

Here’s a **drop-in upgraded version** that applies everything above but stays:

* ASCII only
* single canonical structure
* safe for *any* AI CLI tool that just consumes text

You can literally have `render_workstream_prompt.py` emit this:

```text
=== WORKSTREAM_V1.1 ===

[HEADER]
WORKSTREAM_ID: {{workstream_id}}
CALLING_APP: {{source_app}}        # e.g. codex-cli, claude-code, aider, etc.
TARGET_APP: {{target_app}}        # e.g. aider, codex-cli, claude-code
REPO_ROOT: {{repo_path}}
ENTRY_FILES: {{primary_files_or_globs}}

ROLE: {{persona_line}}            # e.g. "Senior Python engineer and careful refactoring assistant."

CLASSIFICATION: complexity={{simple|moderate|complex|enterprise}}; quality={{standard|production}}; domain={{code|docs|analysis}}

[OBJECTIVE]
{{1–3 sentences, explicit & measurable goal}}

[CONTEXT]
- Project: {{project_name_or_subsystem}}
- Current state: {{short description of what exists today}}
- Why this workstream: {{reason / triggering event}}
- Relevant architecture/constraints: {{e.g. hexagonal, feature-flagged, no breaking changes}}
- Related tickets/links: {{optional}}

[CONSTRAINTS]
- Must:
  - {{bullet 1 – hard requirements}}
  - {{bullet 2}}
- Must NOT:
  - {{bullet 1 – prohibited behaviors (e.g., no new external deps)}}
  - {{bullet 2}}
- Safety:
  - Prefer minimal, well-scoped changes
  - Preserve existing behavior unless explicitly requested

[TASK_BREAKDOWN]
- Main task type: {{refactor|implement_feature|write_tests|analysis|docs}}
- Suggested steps:
  1) {{step 1}}
  2) {{step 2}}
  3) {{step 3}}
- Focus areas:
  - {{specific files/functions/modules}}

[REASONING_MODE]
- Mode: {{step_by_step|concise}}
- If step_by_step: briefly outline your plan, then apply it.

[OUTPUT_FORMAT]
- Primary format: {{markdown|plain_text|json}}
- Required sections in the final answer:
  1) CHANGES_SUMMARY
  2) IMPLEMENTATION_NOTES
  3) RISK_CHECKS
  4) NEXT_STEPS (if any)
- If code is shown, include only the minimal necessary snippets or unified diffs.

[VALIDATION]
- Before final answer, self-check that:
  - [ ] All constraints in [CONSTRAINTS] are satisfied.
  - [ ] The proposed changes are consistent with the [OBJECTIVE].
  - [ ] No obvious syntax or structural errors are present.
- If you detect blocking ambiguity, STOP and output only:
  "CLARIFICATION_NEEDED: {{your concise questions}}"

[EXAMPLE_TASKS]   # optional; usually empty
- Example_good:
  - Objective: "Refactor function X to remove duplication with Y while keeping behavior identical."
  - Constraints: "No new deps, keep public API unchanged."
- Example_bad:
  - "Rewrite the whole module from scratch" (too broad, violates minimal change principle).

[EXECUTION_NOTES_FOR_ROUTER]
- Preferred timeout_seconds: {{default_for_this_class}}
- Retry_on_failure: {{true|false}}
- Escalation_hint: if this tool cannot complete due to limits, recommend a follow-up workstream for {{more_powerful_app}}

=== END_WORKSTREAM_V1.1 ===
```

### Why this is still “universal”

* It’s **pure ASCII**: no XML, no JSON that any particular CLI has to parse.
* For Codex / Claude / Gemini / Copilot / Aider, it’s just a well-structured prompt with clearly labeled sections.
* For your router and logging layer, it’s *machine-friendly*:

  * you can regex the bracketed sections (`^\[CONTEXT\]` etc.)
  * you can parse `CLASSIFICATION:` and `EXECUTION_NOTES_FOR_ROUTER` into your task registry.

---

## 4. Direct answer to your question

> **Do these files offer information that can strengthen the prompt template?**

Yes, very much so. They validate your overall approach and push you to:

* Make **role/persona and 3C (clarity, context, constraints)** explicit.
* Add **classification + output contracts + validation hooks**, giving both the model and your router better guidance.
* Add a skinny but powerful **reasoning + self-check** layer that plays nicely with your error pipeline and agentic design.

```

---

**End of combined spec.**
```
