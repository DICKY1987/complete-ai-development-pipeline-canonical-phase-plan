

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
