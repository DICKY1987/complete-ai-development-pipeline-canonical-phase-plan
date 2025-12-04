---
doc_id: DOC-GUIDE-ARCHITECTURE-BOUNDARIES-921
---


---

## 1. Top-level layout split GUI vs Engine vs Specs

Use a very clear, boring structure:

```text
/engine/                     # Terminal/TUI + orchestrator layer
  orchestrator/
    orchestrator.py
    job_queue.py
    job_state_store.py
  adapters/
    aider_adapter.py
    codex_adapter.py
    tests_adapter.py
    git_adapter.py

/gui/                        # GUI shell layer
  panels/
    file_pipeline_radar/
      file_pipeline_radar.panel.json
      file_pipeline_radar.spec.md
      file_pipeline_radar_view.py
    quarantine_center/
      quarantine_center.panel.json
      quarantine_center.spec.md
      quarantine_center_view.py
    run_overview_strip/
      run_overview_strip.panel.json
      run_overview_strip.spec.md
      run_overview_strip_view.py

/specs/                      # Shared declarative specs (AI lives here)
  jobs/
    job.schema.json
    aider_job.example.json
    codex_job.example.json
  engine/
    engine_api.md
  gui/
    panel.schema.json
    panel_spec_template.md
```

**Rule for AI:**

> **GUI code never directly calls tools like Aider/Codex.**
> It only talks to `/engine/orchestrator.py` and reads state from `/engine/job_state_store.py` (or SQLite, etc.).

This gives you the hybrid style “for free” because the separation is enforced by directory and file-type.

---

## 2. Standard “job” format (the engine contract)

Every tool run (Aider, Codex, tests, etc.) should be defined by a **job JSON** that the orchestrator understands.

### 2.1. Job file structure

`/schema/jobs/job.schema.json` (simplified idea):

```jsonc
{
  "$id": "job.schema.json",
  "type": "object",
  "required": ["job_id", "workstream_id", "tool", "command", "env", "paths"],
  "properties": {
    "job_id":        { "type": "string" },
    "workstream_id": { "type": "string" },
    "tool":          { "type": "string" }, // "aider" | "codex" | "tests" | ...
    "command": {
      "type": "object",
      "required": ["exe", "args"],
      "properties": {
        "exe":  { "type": "string" },
        "args": { "type": "array", "items": { "type": "string" } }
      }
    },
    "env": {
      "type": "object",
      "additionalProperties": { "type": "string" }
    },
    "paths": {
      "type": "object",
      "properties": {
        "repo_root":    { "type": "string" },
        "working_dir":  { "type": "string" },
        "log_file":     { "type": "string" },
        "error_report": { "type": "string" }
      }
    },
    "metadata": {
      "type": "object",
      "description": "Extra tool-specific settings, e.g. message-file for Aider."
    }
  }
}
```

An **Aider job example** (`/schema/jobs/aider_job.example.json`):

```jsonc
{
  "job_id": "job-2025-11-18-001",
  "workstream_id": "ws-PH07",
  "tool": "aider",
  "command": {
    "exe": "aider",
    "args": ["--message-file", "PHASE_DEV_DOCS/AIDER_INSTRUCTIONS_PH07.txt"]
  },
  "env": {
    "OLLAMA_API_BASE": "http://127.0.0.1:11434",
    "OPENAI_API_KEY": "",
    "GIT_EDITOR": "true"
  },
  "paths": {
    "repo_root": "C:/Users/richg/ALL_AI/Complete AI Development Pipeline – Canonical Phase Plan",
    "working_dir": "C:/Users/richg/ALL_AI/Complete AI Development Pipeline – Canonical Phase Plan",
    "log_file": "logs/ws-PH07/job-2025-11-18-001.log",
    "error_report": "logs/ws-PH07/job-2025-11-18-001.error.json"
  },
  "metadata": {
    "retry_policy": "escalate_to_codex_on_error",
    "timeout_seconds": 600
  }
}
```

### 2.2. Orchestrator CLI contract

Create **one canonical entrypoint**:

```bash
python -m engine.orchestrator run-job --job-file path/to/job.json
```

Or in PowerShell:

```powershell
python .\engine\orchestrator\orchestrator.py run-job --job-file path\to\job.json
```

That’s all the GUI ever invokes.

**AI rule:**

> When AI wants to run a tool, it:
>
> 1. Writes a job JSON file using `job.schema.json`.
> 2. Spawns `orchestrator run-job --job-file ...`.
> 3. Watches the job status via state store (file or DB) and logs.

---

## 3. Adapter scripts: thin wrappers around tools

Each CLI tool gets an adapter in `/engine/adapters/`.

The **only job** of an adapter is to:

* Read a job JSON (or receive a Python dict).
* Build the right command line.
* Spawn the process in a pseudo-terminal.
* Stream logs + write exit code and error JSON.

### 3.1. Standard header for adapter scripts

At the top of every `*_adapter.py`:

```python
"""
ADAPTER_ROLE: terminal_tool_adapter
TOOL: aider
VERSION: 0.1.0

RESPONSIBILITY:
- Accept a job dict (from orchestrator).
- Build the aider CLI command.
- Run it in a PTY.
- Stream logs to job['paths']['log_file'].
- Return a JobResult object (exit_code, error_report_path, duration_s).
"""
```

This header makes it easy for an AI to understand *what this file is supposed to do*.

### 3.2. Adapter function signature (for all tools)

```python
# engine/adapters/aider_adapter.py

from typing import Dict, Any
from engine.types import JobResult  # define once in engine/types.py

def run_aider_job(job: Dict[str, Any]) -> JobResult:
    """
    Run Aider for this job.
    Required job keys:
      - command.exe
      - command.args
      - env
      - paths.repo_root
      - paths.log_file
      - paths.error_report
    """
    ...
```

Codex adapter uses the same idea:

```python
# engine/adapters/codex_adapter.py

def run_codex_job(job: Dict[str, Any]) -> JobResult:
    ...
```

Then `orchestrator.py` only needs a **simple mapping**:

```python
TOOL_RUNNERS = {
    "aider": run_aider_job,
    "codex": run_codex_job,
    "tests": run_tests_job
}
```

---

## 4. Orchestrator script: single source of truth for job lifecycle

`/engine/orchestrator/orchestrator.py` should own:

* Job status transitions (queued → running → completed → failed → quarantined).
* Calls into adapters.
* Writes to **state store** (SQLite, JSON, whatever you already use).

### 4.1. Orchestrator header

```python
"""
ADAPTER_ROLE: job_orchestrator
VERSION: 0.1.0

RESPONSIBILITY:
- Accept jobs from CLI (run-job) or GUI via state store.
- Dispatch jobs to the correct tool adapter.
- Capture logs, exit code, and error info.
- Update job and workstream status in the state store.
"""
```

### 4.2. CLI pattern

Skeleton:

```python
import json
import argparse
from engine.adapters import aider_adapter, codex_adapter
from engine.state_store import JobStateStore

TOOL_RUNNERS = {
    "aider": aider_adapter.run_aider_job,
    "codex": codex_adapter.run_codex_job,
    # ...
}

def run_job(job_file: str):
    with open(job_file, "r", encoding="utf-8") as f:
        job = json.load(f)

    store = JobStateStore()
    store.mark_running(job["job_id"])

    runner = TOOL_RUNNERS[job["tool"]]
    result = runner(job)

    store.update_from_result(job, result)

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")

    run_job_parser = sub.add_parser("run-job")
    run_job_parser.add_argument("--job-file", required=True)

    args = parser.parse_args()
    if args.cmd == "run-job":
        run_job(args.job_file)

if __name__ == "__main__":
    main()
```

You don’t have to write this now — but **every AI that touches orchestrator** should work toward this shape.

---

## 5. GUI mods: same pattern for every small panel

Use the **panel JSON + spec.md** pattern we discussed and explicitly align it with the hybrid engine.

### 5.1. Panel manifest (per GUI mod)

`/gui/panels/file_pipeline_radar/file_pipeline_radar.panel.json`:

```jsonc
{
  "panel_id": "file_pipeline_radar",
  "title": "File Pipeline Radar",
  "version": "0.1.0",
  "status": "draft",

  "ui": {
    "region": "main",
    "size_hint": "md",
    "order": 30
  },

  "tech": {
    "framework": "pyqt6",
    "entry_file": "file_pipeline_radar_view.py",
    "entry_symbol": "FilePipelineRadarPanel"
  },

  "data_sources": [
    {
      "service": "job_state_store",
      "methods": ["list_jobs", "get_job", "list_workstreams_for_run"]
    }
  ],

  "engine_api": {
    "run_job_cli": "python -m engine.orchestrator run-job --job-file {job_file}"
  },

  "events": {
    "subscribes": ["run.selected"],
    "publishes": ["job.selected", "file.selected"]
  }
}
```

Notice: **GUI knows orchestrator CLI, not Aider/Codex**.

### 5.2. Panel spec (Hybrid Markdown)

`/gui/panels/file_pipeline_radar/file_pipeline_radar.spec.md`:

```markdown
---
doc_key: gui.file_pipeline_radar.v1
kind: gui_panel_spec
panel_id: file_pipeline_radar
semver: 0.1.0
status: draft
framework: pyqt6
region: main
order: 30
---

# SUMMARY
Visual board showing where each workstream and file is in the pipeline:
waiting, running, fixing, quarantined, or passed.

# DATA_DEPENDENCIES
- job_state_store.list_jobs(run_id)
- job_state_store.list_workstreams_for_run(run_id)

# ENGINE_INTERACTION
- To start a job, this panel creates a job JSON using schema/jobs/job.schema.json
  and calls engine.orchestrator via:
  python -m engine.orchestrator run-job --job-file <path>

# LAYOUT
- Top: Run selector + summary badges.
- Middle: Kanban view (columns = Waiting, Running, Fixing, Quarantine, Done).
- Bottom: Log preview for selected job (read-only).

# EVENTS
- Subscribes:
  - run.selected { run_id }
- Publishes:
  - job.selected { job_id, workstream_id }
  - file.selected { file_path, workstream_id }

# RULES
- Never call Aider/Codex directly.
- Only start jobs via the orchestrator CLI.
- All job JSON files must validate against job.schema.json.
```

AI can follow this template to create *any* new GUI mod.

---

## 6. How to “modify scripts to match” this hybrid style

When AI updates **existing** scripts, give it these instructions (you can paste this as a prompt snippet later):

1. **Classify each script by role**
   Add a header docstring at the top:

   * `ADAPTER_ROLE: terminal_tool_adapter` (for tool wrappers)
   * `ADAPTER_ROLE: job_orchestrator` (for orchestrator)
   * `ADAPTER_ROLE: gui_panel` (for GUI code)
   * `ADAPTER_ROLE: state_store` (for persistent state)

2. **Move direct tool-invocations into adapters**

   * Any `subprocess.run(["aider", ...])` or `codex ...` in random scripts → moved into `/engine/adapters/<tool>_adapter.py`.
   * Call sites now build a **job JSON** and invoke the orchestrator.

3. **Make all long-running actions job-based**

   * No script should “inline” a big chain like Aider → tests → Codex.
     Instead:

     * Create individual job files for each stage.
     * Orchestrator coordinates them (pipeline/queue logic).

4. **Standardize logs**

   * Tools write logs to the `job["paths"]["log_file"]`.
   * Use a simple line-based format; you can add JSONL later if needed.

5. **Standardize error reports**

   * If something fails, adapters write a small JSON to `job["paths"]["error_report"]`:

     ```jsonc
     {
       "job_id": "job-2025-11-18-001",
       "tool": "aider",
       "exit_code": 1,
       "summary": "Tests failed",
       "details": ["Test foo_bar failed", "See log for stack trace"]
     }
     ```

   * The orchestrator reads this and updates job/workstream status (including “quarantine”).

6. **Ensure GUI code never imports adapters directly**

   * GUI only uses:

     * `job_state_store` (to read status)
     * `engine.orchestrator` CLI (to start jobs)

---

## 7. How you actually use this as the human

You don’t need to touch code — you just:

1. Create a new folder under `/gui/panels/<panel_id>/`.

2. Fill in:

   * `<panel_id>.panel.json` (manifest).
   * `<panel_id>.spec.md` (layout & behavior).

3. Tell the AI:

   > “Implement `<panel_id>_view.py` for this panel, following its `.panel.json` and `.spec.md`, and only use `engine.orchestrator` via the job schema for running tools.”

4. For engine-side changes, tell AI:

   > “Refactor existing scripts into `engine/orchestrator` + `engine/adapters` using the job schema in `/schema/jobs/job.schema.json` and the ADAPTER_ROLE headers.”

Everything else falls out of that pattern.

---

