---
doc_id: DOC-LEGACY-PATCH-FILES-AS-UNIFIED-DIFF-OPTIMAL-010
---

# Patch Files as Unified Diff & Optimal Handoff Format*For Agentic AI Pipelines and Multi-CLI Workflows*



---

## 0. Purpose of This Document

This document combines and normalizes two source docs:

* **“patch files are in unified diff_format.md”**
* **“patch files are an optimal handoff format.md”**

Goal:

* Explain **what patch files are**, in unified diff format.
* Explain **how they work** (create, apply, conflict handling).
* Describe **where they are the best possible handoff artifact** between tools/agents.
* Describe **where they are *not* ideal** and what to use instead.
* Provide **concrete patterns** and **JSON structures** suitable for your orchestrator / router.
* Cover **language-aware validation** for **PowerShell** and **Python**.
* Provide a **mental model**: patch files as the backbone transport format under your higher-level workstream system.

This is written **for agentic AI tools** (Codex CLI, Aider, Claude Code, Gemini CLI, etc.) and pipeline orchestrators.

---

## 1. What Is a Patch File? (Unified Diff Format)

Most patch files are in **unified diff** format – the same format produced by commands like `git diff`.

### 1.1 Example Unified Diff

```diff
diff --git a/script.py b/script.py
index 1234567..89abcde 100644
--- a/script.py
+++ b/script.py
@@ -1,5 +1,6 @@
 def main():
-    print("Hello world")
+    print("Hello, world!")
+    print("This line was added")
```

Key points:

* `diff --git a/script.py b/script.py`
  Identifies the file being changed.

* `@@ -1,5 +1,6 @@` (hunk header)

  * Left side (`-1,5`): starting line and number of lines in the **old** file.
  * Right side (`+1,6`): starting line and number of lines in the **new** file.

* Line prefixes:

  * `-` → **removed** lines.
  * `+` → **added** lines.
  * (no prefix / space) → **context** lines that help locate the change.

### 1.2 Language Agnosticism

Unified diff is **pure text**:

* It does not know or care whether the underlying file is:

  * PowerShell (`.ps1`, `.psm1`)
  * Python (`.py`)
  * C#, TypeScript, JSON, Markdown, etc.
* This makes patch files an excellent **generic carrier of code changes** across:

  * Languages
  * Tools (Aider, Codex, Claude Code, etc.)
  * Environments (Windows, WSL, Codespaces, remote servers)

---

## 2. How Patch Files Work in Practice

### 2.1 Creating a Patch

Most commonly via **Git**:

```bash
# Compare working tree to last commit
git diff > change.patch

# Or a specific commit range
git diff OLD_COMMIT NEW_COMMIT > feature.patch
```

Notes:

* `git diff` computes deltas between two states of the repository.
* The resulting `.patch` (or `.diff`) file is a portable description of the change set.

Outside Git:

* Some tools can generate unified diffs directly, but in your pipeline, **Git is usually the main producer** of patch content, even if via wrappers.

### 2.2 Applying a Patch

Two common mechanisms:

#### a) `git apply`

```bash
git apply change.patch
```

* Uses context lines and hunk metadata to locate where changes should go.
* Fails if the file has diverged too far from the expected base (similar to merge conflicts).

#### b) `patch` Utility (classic)

```bash
patch -p1 < change.patch
```

* Same idea as `git apply`.
* Reads the patch from stdin, finds matching context, then modifies files.

### 2.3 Conflicts and Drift

If the underlying files have changed too much (e.g., new unrelated edits, merges, or refactors):

* The context in the patch no longer matches perfectly.
* `git apply` / `patch` will typically:

  * Fail and report “hunk FAILED” or similar.
  * Require human (or higher-level tool) intervention to reconcile.

This behavior is desirable:

* It **prevents silent corruption** where a patch is applied to the wrong code.
* It aligns with your desire for **deterministic**, **auditable** changes.

---

## 3. Why Patch Files Are Useful for AI & Automation

Patch files have properties that align perfectly with your pipeline goals:

### 3.1 Atomic Change Sets

* One patch file ≈ **one precise change set**.
* Easy to:

  * Store as a single artifact.
  * Log and index.
  * Associate with a workstream, run, or ULID.
  * Undo (via reverse patch or Git revert).

### 3.2 Reviewability

* A `.patch` can be inspected in isolation to see **exactly what changed**.
* No need to open the full file:

  * Great for:

    * Code reviews.
    * AI-based reviewers.
    * CI bots.

### 3.3 Reproducibility Across Environments

* Same patch can be applied on:

  * Laptop (Windows)
  * Desktop
  * WSL
  * GitHub Codespaces
  * Remote CI runners
* As long as the **base files match**, the patch yields identical changes.

This matches your need for **deterministic, cross-environment** behavior.

### 3.4 Safety with AI Tools

Instead of allowing an AI tool to overwrite files directly, use a **two-step** pattern:

1. **AI generates patch** (diff) describing the desired changes.
2. **Orchestrator**:

   * Validates the patch.
   * Runs tests and static checks.
   * Applies the patch if safe.
   * Records audit metadata and commits via Git.

Benefits:

* Every automatic change is **explicitly recorded**.
* You can **reject** suspect patches before they touch the repo.
* Easy to integrate circuit breakers and error signatures.

### 3.5 Version-Control Friendly

Git fundamentally stores changes as **deltas**:

* Patch files align with how Git thinks internally.
* Email-based workflows often send `.patch` files directly.
* They naturally map to:

  * Commits.
  * Branches.
  * Workstreams in your pipeline.

---

## 4. When Patch-Based Editing Is a Great Idea

Think of patch files as the **preferred transport format** for **automated, cross-tool, and cross-environment** changes.

### 4.1 Automated Changes from AI Tools or Scripts

Pattern:

1. A tool (Aider, Codex, Claude, etc.) **proposes** a change as a unified diff.

2. The orchestrator:

   * Saves that diff as a `.patch` file under a ledger path, e.g.:

     ```text
     .ledger/patches/YYYYMMDD-HHMM-<ULID>.patch
     ```

   * Optionally runs a dry-run `git apply --check`.

   * Runs language-aware tests and linters.

   * If everything passes:

     * `git apply`
     * `git commit -m "AI: <summary> [<ULID>]"`

3. If checks fail:

   * Patch is **quarantined** for manual or automated fix loops.

Why this is excellent:

* Fully **auditable**.
* Easy to revert or re-evaluate later.
* Clean boundary between **proposal** (patch) and **acceptance** (apply+commit).

### 4.2 Multi-Machine or Multi-Agent Workflows

Use patches as a **portable contract** between agents and machines.

Examples:

* **Agent A (Codex)** on Laptop:

  * Generates `ws-10.patch` covering a refactor.
* **Agent B (Aider)** or a validator on WSL:

  * Receives that patch.
  * Applies it in an isolated worktree.
  * Runs tests/linters.
  * Returns a structured result.

Benefits:

* Avoids re-running the entire refactor on another machine or with another tool.
* Guarantees that the **same edit set** is applied everywhere.

### 4.3 Guard Rails Around “Completed” Workstreams

For your **workstream-based pipeline**, some areas are “done” or “locked”:

* Before applying any patch, the orchestrator:

  * Inspects the patch to see which files and lines it modifies.
  * Cross-references a registry of:

    * **Locked workstreams**
    * **Frozen modules**
    * **Protected files or directories**

If the patch attempts to modify locked areas:

* The orchestrator **rejects** or **quarantines** it.
* This is much easier with patches than with raw file overwrites, because:

  * The patch describes **exactly** what changes and where.

### 4.4 Edit → Validate / Review Chains (Source Edits, Target Validates)

Pattern:

1. **CLI app A** (e.g., Aider, Codex, Claude):

   * Produces a **unified diff** instead of directly editing the repo.
2. Router creates a **patch-style task** for **CLI app B**:

   * B is responsible for **validating** the change:

     * Applying patch in a temporary branch or worktree.
     * Running tests/linters.
     * Reporting pass/fail and diagnostics.

Why patch is optimal:

* B doesn’t re-decide *what* to change.
* B only decides **“Is this change safe/correct?”**
* Easy to store patch + validation results as artifacts.

### 4.5 Multi-Agent “Edit → Review → Merge” Flows

Pattern:

1. Aider produces patch `ws-10.patch` for a refactor.

2. Router sends this patch to Claude CLI with an instruction:

   > “Review this patch for correctness, style, and potential bugs.
   > Do not rewrite; just point out issues and suggest fixes.”

3. If issues are found:

   * Either revise the patch (generate a new patch).
   * Or spawn a new follow-up workstream.

Here, the patch is the **boundary artifact**:

* Agent A edits.
* Agent B reviews.
* No risk that the reviewer silently edits unrelated areas without being tracked.

### 4.6 Cross-Environment Delegation

Instead of:

> “Run the refactor again in environment X”

Do:

> “Apply this *already generated* patch in environment X and validate.”

That avoids:

* Tool/model differences across environments.
* “Drift” between codebases if regenerations differ.

---

## 5. When Patch-Based Editing Is *Not* Ideal

Patch files are powerful, but they are **not** the universal answer for every kind of task.

### 5.1 High-Level Design / Analysis Tasks

Examples:

* “Analyse this module and propose a new architecture.”
* “Write a test plan for this subsystem.”

Issues with forcing a patch here:

* The main result is **semantics and planning**, not edits.
* The target tool needs:

  * Context, design intent, and requirements.
  * Not an existing diff.

Better approach:

* Use a **workstream prompt + file scope**:

  * Provide:

    * Repo path.
    * Key files to inspect.
    * Tasks/goals.
  * Allow the tool to produce:

    * Design docs.
    * Commentary.
    * A later patch as a **separate step** (if needed).

### 5.2 Large, Exploratory Refactors

For big restructures and reorganizations:

* Patches can become:

  * Very large and noisy.
  * Harder for humans and models to reason about.
  * More fragile when combined with other ongoing changes.

Often better to:

* Let tools:

  * Load the relevant files.
  * Plan in terms of new structure.
  * Apply changes directly to a worktree.
* Then, capture the **diff back to main** as a patch (for logging / review), but don’t insist on patch-only editing mid-flow.

### 5.3 Tools Whose Role Is to *Generate* Changes (Not Just Validate)

When a second tool is meant to perform **its own edits**, not just validate or review:

* Handing it a pre-made patch can be redundant or misleading.
* Better to:

  * Provide instructions (prompt) + file scope.
  * Let it produce its own edits/patch at the end.

### 5.4 Interactive, Local Human Development

For manual work in IDEs (VS Code, PyCharm, etc.):

* Best workflow is usually:

  * Edit the file.
  * Run tests.
  * `git diff` → review.
  * `git commit`.

Patches still exist conceptually as the **diff**, but:

* You don’t need to hand-edit patch files.
* You naturally rely on Git to manage the changes.

### 5.5 Files That Change Constantly

Examples:

* Autogenerated files.
* Lockfiles.
* Logs, volatile metadata.

Patches on these can be:

* Noisy and brittle.
* High risk of conflicts and low value.

Strategy:

* Exclude these from **patch-based workflows** where possible.
* Or treat them with separate rules (regenerate rather than patch).

---

## 6. PowerShell & Python: Language-Aware Validation Around Patches

Patch files themselves are **language-agnostic**, but your pipeline doesn’t have to be.

### 6.1 PowerShell

After applying a patch that touches PowerShell files (`.ps1`, `.psm1`, etc.):

Recommended checks:

* **Script metadata / basic sanity** (when applicable):

  ```powershell
  # Example if using script metadata
  Test-ScriptFileInfo -Path .\scripts\MyScript.ps1
  ```

* **Static analysis with PSScriptAnalyzer**:

  ```powershell
  Invoke-ScriptAnalyzer -Path .\scripts -Recurse -Severity Warning
  ```

* **Tests with Pester (where relevant)**:

  ```powershell
  Invoke-Pester -PassThru
  ```

Integrate these as tools in your **tool profiles** and call them in the **STATIC** step of your pipeline.

### 6.2 Python

After applying patches touching `.py` files:

Recommended checks:

* **Syntax / bytecode compilation**:

  ```bash
  python -m compileall src
  # or
  python -m py_compile path/to/changed_file.py
  ```

* **Linters and format checks**:

  ```bash
  ruff check src scripts
  black --check src scripts
  ```

* **Unit tests** (full or targeted):

  ```bash
  pytest -q
  # Or subset: pytest -q -k "<pattern>"
  ```

Combined with patch-based edits, this yields:

* A clear **what changed** (patch).
* A clear **is it valid?** (language-aware validation).

---

## 7. Integrating Patches Into Your Task Routing Model

Use patch files **selectively** as part of your **task payload model**.

### 7.1 Task Mode / Payload Type

Extend your task schema with a `mode` (or `payload_type`) field:

Suggested values:

* `"prompt"`

  * Tool receives:

    * Instructions.
    * Repo path and file scope.
  * Tool performs **edits itself**, usually in a worktree.
* `"patch_review"`

  * Tool receives:

    * A generated patch file.
    * A review objective.
  * Tool performs:

    * **Analysis** and commentary only (no edits).
* `"patch_apply_validate"`

  * Tool receives:

    * A patch.
    * Instructions to apply it in a sandbox.
  * Tool:

    * Applies patch in temp branch/worktree.
    * Runs tests/linters.
    * Returns pass/fail with diagnostics.

#### Example: Patch Review Task Payload

```jsonc
{
  "task_id": "01J2EXAMPLEULID",
  "source_app": "aider",
  "mode": "patch_review",
  "repo_path": "C:/repo",
  "patch_file": ".tasks/patches/ws-10.patch",
  "objective": "Review this patch for correctness, style, and potential bugs.",
  "constraints": {
    "allow_delegation": false
  }
}
```

### 7.2 Recommended Policy: Where to Use Which Mode

A good default:

* **Creation / Edit phases** (Aider, Codex, Claude Code):

  * Use `mode: "prompt"`.
  * Tools operate directly over files in an isolated worktree.
  * At the end, capture a diff as a patch for audit and downstream steps.

* **Review / Validate / CI phases**:

  * Use `mode: "patch_review"` or `mode: "patch_apply_validate"`.
  * Tools focus on:

    * Reviewing patches.
    * Applying patches and running tests.
    * Reporting back.

This keeps:

* **Editing flows** flexible and tool-optimized.
* **Handoff and validation** deterministic and patch-based.

---

## 8. Recommended Pipeline & Mental Model

### 8.1 Git as Source of Truth

Always treat **Git** as the canonical state store for:

* PowerShell, Python, and other code.
* Documents, specs, scripts.
* Workstream inputs (unless stored elsewhere intentionally).

### 8.2 Every AI/Tool Edit as a Patch Proposal

For automated edits:

1. Tool runs in a **worktree** or local clone.
2. After it finishes:

   * Compute `git diff` against the parent branch.
   * Save diff to a patch file (with ULID/time-based naming).
3. Pipeline records metadata:

   * Workstream ID.
   * Tool name/model.
   * Timestamp.
   * Status.

### 8.3 Orchestrator Responsibilities

For each patch:

1. **Dry-run**:

   * `git apply --check patch.patch` to ensure it applies cleanly.
2. **Language-aware checks**:

   * Run relevant checks based on file types changed:

     * PowerShell: PSScriptAnalyzer, Pester.
     * Python: compile, ruff, black, pytest.
3. **Guard rails & scope checks**:

   * Ensure patch touches **only** files within the workstream’s `files_scope` and `files_create`.
   * Reject patches that touch locked or out-of-scope areas.
4. **Apply & commit** (on success):

   * `git apply patch.patch`
   * `git commit -m "AI: <short description> [<ULID>]"`

On failure:

* Patch is quarantined for manual or automated fix flows.
* No changes are applied to the main branch.

### 8.4 Integration with Error Pipelines & Circuit Breakers

For repeated failures in STATIC or RUNTIME steps:

* Record:

  * Error signatures derived from tool output.
  * Diff hashes derived from patch or final tool result.
* Detect:

  * Oscillation (same error repeating across attempted fixes).
  * Threshold breaches (too many attempts).
* Trip circuit breakers when needed:

  * Mark workstream as failed.
  * Stop further automated patch application.

Patch artifacts + error signatures give you:

* Clear cause-effect linkage between:

  * **Change set** (patch).
  * **Observed failures** (lint/test/runtime errors).

---

## 9. Summary & Decision Guide

### 9.1 When to Prefer Patch Files

Use **patch-based handoffs** when you want:

* Deterministic, portable change sets:

  * **Edit → validate/review** transitions between tools.
* Cross-environment consistency:

  * Same patch applied on laptop, WSL, remote CI, etc.
* Safe operations on “completed” or “locked” code:

  * Ability to inspect and block out-of-scope changes.
* Rich audit logs and rollback options:

  * Store patch per workstream/run in a ledger.

In these cases, **unified diff patches are arguably the optimal transfer format** between CLI apps and automated agents.

### 9.2 When Not to Over-Rely on Patches

Do **not** force patch files as the primary representation when:

* Performing high-level design, analysis, or planning.
* Doing huge exploratory refactors or reorganizations.
* Using tools whose role is to **generate** changes rather than just validate them.
* Human developers are working interactively in their IDEs.
* The files in question are volatile (logs, lockfiles, generated artifacts).

Use:

* **Workstream prompts + repo path + file scopes** for planning and primary editing.
* **Patches** for:

  * Auditing.
  * Cross-tool validation.
  * Cross-environment application.
  * Guard rails around completed workstreams.

### 9.3 Direct Answer to “Is This the Best Approach?”

* Patch files are an **excellent mechanism** and in many cases the **best** handoff artifact for:

  * Edit → validate/review flows.
  * Multi-machine task delegation.
  * Guard-railed edits to locked workstreams.
  * Auditable, rollback-friendly AI changes.

* They are **not** a replacement for:

  * High-level semantic tasks.
  * All interactive development.
  * All large-scale design efforts.

Instead:

* Treat unified diff **patch files** as the **backbone transport format** under your higher-level **workstream and task routing system**, especially for **automated, cross-tool, and cross-environment** edits.

This combined model gives you:

* Determinism.
* Traceability.
* Safety.
* Flexibility across AI tools and platforms.
