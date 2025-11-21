You handle this in two layers:

1. **“Don’t ask” in the first place (per-tool headless contract)**
2. **Treat any remaining prompt as a *failure mode* that the orchestrator detects, kills, and retries or escalates**

I’ll walk through both in the context of your existing Game Board / task-queue setup.

---

## 1. Per-tool “headless contract” (prevention)

For every CLI tool in the pipeline, you want a **single adapter** whose job is:

> “Given a Task, run this tool in a way that *never* pauses for input.”

That adapter should *always* be the only way the orchestrator invokes the CLI.

In your world, that’s exactly what the **ToolRegistry / router.config.yaml / adapters** are for: one place to encode “non-interactive” flags and env vars per tool. 

Concrete patterns:

* Always include non-interactive flags where they exist:

  * `--yes`, `--assume-yes`, `--non-interactive`, `--force`, `--no-tty`, etc.
* Set CI-ish env vars to suppress wizards:

  * e.g. `GIT_TERMINAL_PROMPT=0`, `PIP_YES=1`, language-specific “CI=true” envs, etc.
* Move any **“first run”** questions into config files that your pipeline writes up front.

In your config, this lives naturally in the `apps.*.cmd_template` and per-app defaults:

```yaml
apps:
  aider:
    cmd_template: >
      aider --yes --no-tty --model {model} {extra_args}
    default_timeouts:
      wall_clock_sec: 900
      idle_output_sec: 120
```

The key rule is:

> **No tool is ever called directly.** It’s always called through a small adapter that guarantees headless mode.

If you add a new tool and forget to give it a non-interactive config, the orchestrator should treat that as **misconfiguration**, not a runtime surprise.

---

## 2. Detecting “hidden prompts” with idle timeouts

Even with good config, some tools *will* occasionally block (new versions, new features, unexpected error paths). You can’t fully prevent that, so you treat it as a **known failure mode**:

> “If a process stops producing output for too long, assume it’s stuck or waiting for input. Kill it, log it, and retry or escalate.”

You already have the right knobs in your design:

* Per-app timeouts (`wall_clock_sec`, `idle_output_sec`) in `router.config.yaml` 
* Background workers that log to `.runs/` and track tasks (`.tasks/inbox`, `/running`, `/done`, `/failed`) 

The pattern:

1. **Start the tool in the background**, logging stdout/stderr to a file or streaming pipe.
2. **Monitor activity**:

   * track last time you saw any output (or last write time on the log file).
3. If `now - last_output_time > idle_output_sec`:

   * assume “interactive prompt / hung”.
   * kill the process.
   * mark the attempt as `INTERACTIVE_TIMEOUT`.
   * record error signature in your `errors` / `events` tables.
4. Decide what to do next (retry, reroute, or fail) based on your **retry policy / circuit breaker**.

This is exactly the style of control you already sketched for your router and error pipeline. 

---

## 3. Automatic restart without the user

Once you treat “prompting for input” as a *kind of failure*, the restart logic becomes just another circuit-breaker path.

You already have:

* A task object with `retry_state.attempt` and `max_attempts`. 
* A queue design where tasks move `.tasks/inbox → running → done/failed` and can be re-enqueued. 

So:

1. **On interactive timeout:**

   * mark the attempt as failed with reason `interactive_prompt` (or similar).
   * increment `retry_state.attempt`.

2. **If attempts < max_attempts:**

   * adjust the task slightly:

     * e.g., set `constraints.force_noninteractive = true`
     * or add extra args to the task payload (like `--force`).
   * re-enqueue the task back into `.tasks/inbox`.

3. **If attempts >= max_attempts:**

   * mark task as `failed`.
   * emit a clear, machine-readable error entry in `.runs/audit.jsonl` saying:

     * “Tool appears to require interactive confirmation. Manual intervention needed.”

Because the **restart decision** is made by the orchestrator, not the user, this is fully headless.

---

## 4. Optional: making “no prompts” part of the spec

You can even push this requirement up into the **phase / workstream spec** layer (Game Board Protocol):

* In your phase/workstream spec, add a field like:

```yaml
tooling:
  must_be_headless: true
  allowed_interactive: []
```

* If a tool ever exits with `INTERACTIVE_TIMEOUT` for a phase that has `must_be_headless: true`, the orchestrator **must not** auto-escalate to “ask the user”—instead, it either:

  * retries with stricter flags, or
  * fails the phase and logs a spec violation.

That keeps everything aligned with your “GROUND TRUTH via CLI + strict rules” approach. 

---

## 5. Summary pattern you can implement

**High-level contract for your pipeline:**

1. **Per-tool adapters**:

   * Always run with non-interactive flags and CI-style env vars.
2. **Watchdog**:

   * Enforce wall-clock and idle-output timeouts.
3. **Classification**:

   * Treat “stopped to ask user something” as `INTERACTIVE_TIMEOUT` → a known error type.
4. **Restart logic**:

   * Retry a limited number of times with adjusted flags / other tool.
   * If still stuck, fail the task and log clearly.
5. **Spec layer**:

   * Workstreams/phases declare `must_be_headless: true`.
   * Any interactive behavior is a spec violation, not a user prompt.

