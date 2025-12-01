---
doc_id: DOC-AIM-FULL-STACK-OF-APPS-TOOLS-THIS-PIPELINE-088
---

Here’s the full stack of apps/tools this pipeline expects, organized by **“must have vs nice-to-have”** and by ecosystem.

I’m only listing things that actually show up in the spec + phase plan (plus the obvious runtimes they depend on), not random extras.

---

## 1. Core platform & runtimes (required)

These are the foundations everything else sits on:

* **Windows 10/11**

  * Assumed host OS.

* **PowerShell 7 (pwsh)**

  * Used for:

    * Task scripts (e.g., `scripts/*.ps1`, diagnostics).
    * Running PSScriptAnalyzer & Pester.
    * Optional older PowerShell-based version of the pipeline (the spec includes PS functions like `Invoke-EditStep`, `Invoke-StaticPipeline`, etc.).

* **Python 3.12+**

  * Primary language for the orchestrator and CLI.
  * Used for:

    * `src/pipeline/*.py` (DB, orchestrator, tools adapter, scheduler, etc.).
    * Running tests (`pytest`).
    * CLI helpers (e.g., `scripts/init_db.py`, `scripts/generate_spec_index.py`).

* **Git CLI**

  * Used for:

    * Worktrees (`git worktree`).
    * Branching and committing changes made by Aider.
    * Pushing branches for PR creation.

* **SQLite**

  * DB engine behind the state layer.
  * In the Python-first design, this is just the **standard library `sqlite3`** module plus a `.db` file under `state/`.
  * In the original PowerShell-spec, there are calls like `Invoke-SqliteQuery`, but in the current phase plan, Python is the source of truth.

---

## 2. Python dev & validation tooling

These are the Python tools explicitly called out in the phase plan:

* **pytest** (required for dev)

  * Test framework for:

    * DB layer (PH-02).
    * `tools.py` adapter (PH-03).
    * Future orchestrator/scheduler behavior.

* **Ruff** (recommended)

  * Fast Python linter.
  * Listed in PH-00 as one of the core quality tools for the repo.

* **Black** (recommended)

  * Code formatter.
  * Used to keep all pipeline Python code consistent.

* **Mypy** (recommended)

  * Static type checker.
  * Helps keep the orchestrator/state layer API safe as it grows.

> These four are the ones explicitly mentioned in the phase plan:
> `Python: Ruff, Black, Mypy, pytest` (PH-00).

You can treat **pytest** as “must-have for development” and the others as **strongly recommended** for quality gates.

---

## 3. PowerShell tools & modules

Used primarily in the STATIC and TEST stages for PowerShell code:

* **PSScriptAnalyzer** (required for PS code quality)

  * PowerShell module.
  * Command used: `Invoke-ScriptAnalyzer`
  * Purpose:

    * Static analysis and style/best-practice checks on PowerShell scripts.
  * Appears in both spec and phase plan as a core static check tool.

* **Pester** (required for PS tests)

  * PowerShell testing framework.
  * Command used: `Invoke-Pester`
  * Purpose:

    * Run PowerShell tests as part of the STATIC / RUNTIME pipeline stages.
  * Used where workstreams include PowerShell code or PS-based acceptance tests.

---

## 4. AI editing & prompt-driven tooling

The editor/AI that actually edits code inside worktrees:

* **Aider CLI** (required for the EDIT/FIX steps)

  * Tool ID: `"aider"` / `"aider-editor"` in the spec/tool profiles.
  * Role:

    * Main AI “editor” used for:

      * `EDIT` step: apply planned changes for a workstream.
      * `FIX` step: respond to static/runtime test failures with targeted fixes.
  * Uses environment variables such as:

    * `AIDER_NO_AUTO_COMMITS=1` (required per Aider contract).
  * PH-03.5 is entirely about **Aider integration contract + prompt template system** built on top of the generic `run_tool()` adapter from PH-03.

> Behind Aider you’ll also need an LLM provider (OpenAI / Anthropic / etc.) and API keys, but those are **credentials**, not separate “apps” in this phase plan.

---

## 5. Integration & DevOps tooling

Used to connect pipeline output to your broader dev workflow:

* **GitHub CLI (`gh`)**

  * Used in the spec to:

    * Create PRs: `gh pr create …`
    * Comment on pm/GitHub issues: `gh issue comment $ws.ccpm_issue …`
  * Tied to PH-08 (“Integrations (OpenSpec, CCPM, GitHub)”) for:

    * Branch & PR automation.
    * Posting status / comments back to your issue tracker.

* **OpenSpec (spec + optional CLI/library)**

  * Not a specific binary in the spec, but functionally you need:

    * An **OpenSpec change definition** per workstream.
    * Optionally an OpenSpec CLI or Python library if you want:

      * Automatic workstream generation.
      * Automatic status updates back into OpenSpec/CCPM.
  * The pipeline references:

    * `openspec_change`
    * `gate`
    * `tasks` from OpenSpec.

* **CCPM / Issue tracker**

  * Represented by `ccpm_issue` in the workstream schema.
  * In practice, the plan uses **GitHub issues** plus `gh` to comment, rather than a separate CCPM app.
  * You may still have a separate CCPM system, but at pipeline level it just needs:

    * An issue identifier.
    * The ability to post updates (via GitHub / API).

---

## 6. Optional / extension tools mentioned in the spec

The spec explicitly calls out a few “other tools” that are **not required**, but that you can plug into the STATIC or quality stages via the `tool_profiles` system:

* **yamllint**

  * YAML linter.
  * Suggested in spec as an example extra static checker.

* **codespell**

  * Spelling checker for source/docs.

* **gitleaks**

  * Secret/scanning tool for git repos.

These are examples of tools that can be wired through `config/tool_profiles.json` and invoked via `run_tool()` just like PSScriptAnalyzer or pytest.

---

## 7. Task / helper tooling (optional but supported)

The plan allows either Python task runners or pure CLI/PowerShell:

* **Invoke (Python package `invoke`)**

  * Optional.
  * Used for dev tasks like:

    * `invoke db.init`
    * `invoke diagnostics`
  * If you don’t use Invoke, you can just call Python modules directly (`python -m pipeline.db init`) or use PowerShell scripts.

* **PowerShell helper scripts**

  * Things like:

    * `pwsh scripts/Show-PipelineRun.ps1`
  * These are scripts you’ll write as part of the runbook/diagnostics layers, not standalone external apps.

---

## Quick recap by category

**Absolutely core to the pipeline’s design**

* Windows
* PowerShell 7
* Python 3.12+
* Git
* SQLite (via Python `sqlite3`)
* pytest
* PSScriptAnalyzer
* Pester
* Aider CLI
* GitHub CLI (`gh`)

**Strongly recommended dev quality tools**

* Ruff
* Black
* Mypy

**Optional / pluggable**

* yamllint
* codespell
* gitleaks
* Python `invoke`
* Any additional CLI you wire into `tool_profiles.json` (security scanners, linters, formatters, etc.)
* OpenSpec/CCPM-specific CLIs or libraries, if you want deeper automation there.

If you want, next I can turn this into a **checklist script** (PowerShell) that verifies each tool is installed, prints versions/paths, and writes a little “pipeline readiness report” you can run anytime.

