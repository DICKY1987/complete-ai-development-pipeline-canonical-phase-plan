
Here’s how I’d design a **zero-touch, fully-autonomous refactor runner** on top of what you already have.

---

## 0. What “zero touch” really means here

For this project, I’d define “zero touch” as:

* You do **one-time setup**:

  * Confirm the phase plan / workstreams.
  * Configure usage budgets for Codex / Gemini / Copilot.
  * Decide whether merges to `main` are automatic or gated.
* Then you run a **single command**:

  * `python -m pipeline.autorun --plan section_refactor --mode zero-touch`
* From that point:

  * A scheduler walks the dependency graph.
  * Each workstream runs through your orchestrator + error pipeline.
  * AI tools are chosen automatically within quotas.
  * Git branches / worktrees, tests, path indexer, etc. are all driven *without* asking you anything.

You only step in if:

* A safety rule trips (e.g., >N consecutive failures, test regressions in critical modules).
* Or you want to review / abort.

Everything else is the system’s job.

---

## 1. The architecture you need (4 layers)

You already have most of this in your repo, it just isn’t wired into a single “autorun” yet.

### Layer 1 – **Spec & Planning**

* **OpenSpec**: high-level change spec for “Section-Aware Repo Refactor + Path Abstraction,” which can generate task trees and CLI prompts for multiple assistants. ([GitHub][1])
* **CCPM**: GitHub Issues + worktrees project management system used by Claude Code, which is already designed for *parallel agent execution on worktrees*. ([GitHub][2])
* **Internal workstreams**: your JSON/YAML workstream bundle schema (ws-01..ws-N), dependency graph, files_scope, test commands.

Together, this gives you a **complete machine-readable “what needs to be done”**.

### Layer 2 – **State Machine & Orchestrator**

* Your Python orchestrator + error state machine:

  * EDIT → STATIC → RUNTIME phases.
  * FIX loops / escalation (Aider → Codex → Claude/Gemini).
  * SQLite / JSONL state for “run”, “workstream”, and “error” tables.

This is the **brain** that executes one workstream at a time in a controlled way.

### Layer 3 – **AI Tool Drivers**

* Aider driver (local, no quota).
* Codex driver (CLI, with FS/network flags).
* Gemini driver (CLI or API wrapper).
* Copilot driver (if you decide to use it programmatically).
* Claude Code / CCPM driver (optional, to delegate whole workstreams to Claude Code agents if you want). ([Claude Code][3])

Each driver exposes a common API:

```python
run_step(tool_name, repo_root, worktree_path, step_spec) -> StepResult
```

### Layer 4 – **Scheduler / Autorun**

A long-running `autorun.py` that:

* Reads the phase plan + workstreams.
* Solves dependencies.
* Chooses the next runnable workstream.
* Assigns tools under quota + risk policies.
* Calls the orchestrator.
* Updates state.
* Repeats until all workstreams are **DONE** or a **circuit-breaker** trips.

---

## 2. Step 0 – Encode the project as a machine plan

You’re already partway here with your “dependency-aware path” and Section-Aware workstream documents.

You want a **tool-neutral** workstream record that looks roughly like:

```json
{
  "id": "WS-03-core-refactor",
  "phase": "PH-03",
  "section": "core",
  "depends_on": ["WS-01-path-index", "WS-02-section-map"],
  "files_scope": [
    "src/core/**",
    "tests/core/**"
  ],
  "test_commands": [
    "pytest tests/core -q",
    "python scripts/paths_index_cli.py check --section core"
  ],
  "risk_level": "high",
  "preferred_tools": ["aider"],
  "fallback_tools": ["codex", "gemini"],
  "max_attempts": 5
}
```

Then:

* **OpenSpec**: define a change (e.g., `OS-REF-SECTION`), and use OpenSpec’s CLI to generate or verify the task list and ensure your workstreams map cleanly to the spec. ([GitHub][1])
* **CCPM**: create matching GitHub Issues (one per workstream) so pm/Claude Code can see and manipulate the same tasks if you want to pull them into Claude Code’s project view. ([GitHub][2])

This is your **single source of truth** for the refactor.

---

## 3. Step 1 – Bootstrap run: indexes, registries, baselines

Before doing *any* AI editing, your autorun should:

1. **Run the Hardcoded Path Indexer** workstream (WS-01):

   * Scan repo.
   * Populate `refactor_paths.db` and write `reports/paths-baseline.json`.
2. **Build or validate the Path Registry**:

   * Load `config/path_index.yaml`.
   * Validate that every key corresponds to a real path today.
3. **Run baseline tests**:

   * `pytest -q` (or whatever you have).
   * Basic static analyzers.
4. Snapshots:

   * Tag / branch (`git tag prerefactor-baseline`).
   * Snapshot of path index and registry so you can diff later.

You can wrap this in a single “bootstrap” workstream that **must** succeed before anything else runs.

---

## 4. Step 2 – Autonomous Scheduler & State Machine

This is the heart of “zero touch”.

### 4.1. Scheduler logic (high level)

Pseudocode:

```python
def pick_next_workstream(state, workstreams, quotas):
    # Exclude completed or permanently failed workstreams
    pending = [ws for ws in workstreams if state.status(ws.id) in ("PENDING", "BLOCKED")]

    # Respect dependencies
    runnable = [
        ws for ws in pending
        if all(state.status(dep) == "DONE" for dep in ws.depends_on)
    ]

    # Prioritize by phase + risk + section ordering
    runnable.sort(key=priority_key)

    for ws in runnable:
        tool = choose_tool_for_ws(ws, quotas)
        if tool:
            return ws, tool

    return None, None
```

The scheduler:

* Consults **dependencies** (your Section-Aware plan).
* Consults **quotas** (see §5).
* Chooses the best next `(workstream, tool)` pair.

### 4.2. Orchestrator loop

For each chosen workstream:

```python
def run_workstream_autonomous(ws, tool):
    # 1. Create isolated git worktree/branch
    wt_path = create_worktree(ws.id)

    # 2. Call orchestrator: EDIT → STATIC → RUNTIME with the chosen tool
    result = orchestrator.run(ws, tool, wt_path)

    # 3. Update state
    update_state(ws.id, result)

    # 4. If success → merge back (or mark ready-to-merge)
    if result.success:
        merge_worktree(ws.id)
    else:
        maybe_escalate_or_fail(ws, result)
```

The orchestrator:

* Uses the **Aider-optimized workstream file** (or Codex/Gemini prompt view) as instructions.
* Enforces `files_scope` and section rules.
* Runs tests & path checks.
* On failure, triggers your error pipeline (Aider → Codex → Claude/Gemini) automatically, within quotas.

No user interaction required.

---

## 5. Step 3 – AI Tool drivers + quota rules

### 5.1. One driver interface

Define a driver per tool:

```python
class AiderDriver:
    name = "aider"
    def run_step(self, ws, step, wt_path): ...

class CodexDriver:
    name = "codex"
    def run_step(self, ws, step, wt_path): ...

class GeminiDriver:
    name = "gemini"
    def run_step(self, ws, step, wt_path): ...
```

Each driver:

* Accepts a single **step** of the workstream’s operations sequence.
* Knows how to:

  * Build its prompt from the tool-neutral spec + Aider-style instructions.
  * Invoke the CLI / API.
  * Return a `StepResult` with:

    * `success`, `files_changed`, `logs`, `usage` (tokens/calls).

### 5.2. Quota-aware tool selection

Have a `quotas` config, e.g.:

```yaml
tool_budgets:
  codex:
    max_calls_per_day: 40
    max_tokens_per_day: 200000
  gemini:
    max_calls_per_day: 30
  copilot:
    enabled: false
  aider:
    max_calls_per_day: null  # unlimited
```

And a policy like:

* Default tool per workstream = Aider (safe, local).
* For high-risk or spec-critical workstreams:

  * First attempt with Aider.
  * If Aider hits N failures, escalate to Codex (if quota left).
  * If Codex also fails N times, escalate to Gemini or mark `NEEDS_REVIEW`.

So “zero touch” doesn’t mean “blindly use the same tool”; it means “the escalation logic is also automated.”

---

## 6. Step 4 – Safety rails: tests, path index, Git

Because you’re letting this run unattended, the guardrails matter more than the AI.

### 6.1. Path index / registry as hard gate

In both STATIC and RUNTIME phases, include checks like:

* **No new forbidden patterns**:

  * Run the indexer again after edits.
  * Compare with `paths-baseline.json`.
  * Fail if:

    * New matches appear for deprecated patterns.
    * Existing matches are changed to obviously wrong paths.
* **Registry validity**:

  * Ensure `path_index.yaml` still resolves, and that renamed sections match the Section map.

If a workstream fails these checks:

* Mark it as `FAILED_INVALID_PATHS`.
* Either:

  * Try a FIX workstream that uses a “path-fix” sub-agent, or
  * Escalate to a higher-powered model once within quota.

### 6.2. Git strategy

For zero touch, I’d use **worktrees per workstream**, very similar to CCPM’s default pattern of using Git worktrees for parallel Claude Code tasks. ([GitHub][2])

Per workstream:

* `git worktree add ../wt-WS-03 WS-03-core-refactor`
* All AI edits happen in the worktree.
* On success:

  * `git checkout main`
  * `git merge --no-ff WS-03-core-refactor` (or queue for batch merge).
* On failure:

  * Drop the worktree.
  * Keep a branch + logs for later forensics.

This gives you a **clean, inspectable history** even if everything runs while you sleep.

---

## 7. Step 5 – “One command” entrypoint

Finally, expose everything through a single CLI, e.g. `pipeline_autorun.py`:

```bash
python -m src.pipeline.autorun \
  --plan section_refactor \
  --mode zero-touch \
  --max-runtime-hours 12 \
  --stop-on-critical-fail
```

Internally, `autorun`:

1. Loads phase plan + workstreams from JSON/YAML/OpenSpec.
2. Connects to the state DB (or creates it).
3. Runs the bootstrap workstream (indexes, registry, baseline tests).
4. Enters the scheduler loop:

   * Pick next `(ws, tool)` under constraints.
   * Run via orchestrator.
   * Update state & quotas.
5. Exits when:

   * All workstreams are `DONE`, or
   * A **circuit breaker** trips (e.g., 5 critical test regressions in a row, or quota exhaustion).

You can optionally wrap this in:

* A Python **Invoke task** (`inv autorun.refactor`) or
* A PowerShell **Invoke-Build task** (`Task Run-Refactor { python -m ... }`)

so it’s easy to run from your normal workflows.

---

## 8. Where OpenSpec, CCPM, Claude Code help (optionally)

You don’t *need* them to get zero-touch, but they can give you better ergonomics:

* **OpenSpec**: define the overall “Section-Aware refactor” as a spec; use OpenSpec CLI to:

  * Generate the initial set of workstreams (tasks).
  * Validate that every change is traceable to a spec item. ([GitHub][1])
* **CCPM**: use CCPM to:

  * Mirror workstream status to GitHub Issues.
  * Use Claude Code as an *additional agent* running on specific worktrees, especially to handle hairy workstreams where its subagents/skills are a better fit. ([GitHub][2])
* **Claude Code**: for the nastiest workstreams, you can spawn a Claude Code session attached to the relevant worktree and give it the same machine-readable workstream instructions; it can chain subagents to analyze & fix code while your orchestrator just treats it as another driver. ([Claude Code][3])

But the **core zero-touch behaviour** still lives in your own `autorun` + orchestrator.

---

## 9. How close to “fully autonomous” is realistic?

If you implement it like this, you can absolutely:

* Start it with one command at night.
* Have it:

  * Run dozens of workstreams.
  * Use Aider heavily, and selectively burn Codex/Gemini on tricky cases.
  * Keep Git history and tests clean.
  * Leave you with a report and a refactored repo in the morning.

I’d still recommend at least:

* A **final manual review** of:

  * Git history (merge commits per workstream).
  * Final path index diff.
  * Final test results.

But that’s a “verify and sign off” step, not part of the main loop.

---


