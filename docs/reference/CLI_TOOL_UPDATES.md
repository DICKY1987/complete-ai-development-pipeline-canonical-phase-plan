# CLI TOOL UPDATES

This document consolidates guidance from the conversation about configuring and controlling AI-powered CLI tools:
- **Claude Code**
- **Codex CLI** (Windows & WSL)
- **Aider**
- **GitHub Copilot CLI**

It covers:
1. A cross-tool pattern for instructions and behavior.
2. How to grant more automatic permissions (especially Copilot CLI).
3. What “sandbox-safe” means.
4. A “soft sandbox” layout using per-project clones.
5. Per-tool configuration for the soft-sandbox pattern.
6. A canonical `DEV_RULES_CORE.md` and how each tool should reference it.

---

## 1. Cross-Tool Instruction Pattern

For all tools, think in **three layers**:

1. **Global persona / rules (user-level)**
   - Applies everywhere on your machine.
   - One file or settings block per tool:
     - Claude Code → `~/.claude/CLAUDE.md` + `~/.claude/settings.json`
     - Codex → `~/.codex/AGENTS.md` + `~/.codex/config.toml`
     - Aider → `~/.aider.conf.yml` or home-level `.aider.model.settings.yml`
     - GitHub Copilot → GitHub account “custom instructions”

2. **Repo / project-level instructions**
   - Live inside each project repository:
     - Claude Code → `./CLAUDE.md` (and optionally subfolder `CLAUDE.md`)
     - Codex → `./AGENTS.md` (and optionally in subfolders)
     - Aider → `./.aider.conf.yml` + optionally project `.aider.model.settings.yml`
     - Copilot → `.github/copilot-instructions.md`

3. **Per-invocation overrides**
   - CLI flags or prompt text:
     - Claude Code → `--system-prompt`, `--append-system-prompt`, `--system-prompt-file`
     - Codex → prompt content + CLI overrides
     - Aider → `--read`, `--model`, etc.
     - Copilot CLI → prompt text, tool flags (`--allow-all-tools`, etc.)

The idea is:
- **Global files** capture your *personal* coding philosophy.
- **Per-repo files** capture *project-specific* rules (including sandbox behavior).
- **Flags** are for one-off modes, not for your long-term architecture.

---

## 2. GitHub Copilot CLI Permissions & “Full Send” Mode

By default, Copilot CLI is conservative and asks frequently for confirmation before running tools or modifying files.

### 2.1 Allow all tools

From the official options, you can run:

```bash
copilot --allow-all-tools
```

- `--allow-all-tools` = allow all tools to run automatically without confirmation (also controllable via the `COPILOT_ALLOW_ALL` environment variable).

You can also use:

- `--allow-tool [tools...]` – allow only specific tools.
- `--allow-all-paths` – disable path verification and let it operate on any path.

Example “full send” run from a trusted repo:

```bash
copilot --allow-all-tools --allow-all-paths
```

Or, safer (respect paths but auto-approve tools):

```bash
copilot --allow-all-tools
```

### 2.2 Make auto-approval the default

Set an environment variable so you don’t have to pass the flag every time.

**WSL / bash:**

```bash
# In ~/.bashrc or ~/.zshrc
export COPILOT_ALLOW_ALL=1
```

Then reload:

```bash
source ~/.bashrc
```

**PowerShell (Windows):**

For the current session:

```powershell
$env:COPILOT_ALLOW_ALL = "1"
```

To make it permanent, add this to your PowerShell profile (`notepad $PROFILE`):

```powershell
$env:COPILOT_ALLOW_ALL = "1"
```

After that, running just:

```bash
copilot
```

will behave as if `--allow-all-tools` were always set.

### 2.3 Stop the “Do you trust this folder?” prompt

When Copilot CLI asks if you trust a folder, choose:

> “Yes, and remember this folder for future sessions.”

This adds the path to its allow-list so you won’t be asked again when starting in that directory.

You can also pre-approve extra directories with:

```bash
copilot --add-dir /path/to/project --allow-all-tools
```

### 2.4 Safety warning

With `--allow-all-tools` and `COPILOT_ALLOW_ALL=1`:

- Copilot can run arbitrary commands.
- It can edit files and call git without asking every time.

This is acceptable **only** in environments you consider safe to experiment with (see the sandbox sections below).

---

## 3. “Sandbox-Safe” – What It Actually Means

**“Sandbox-safe”** means:

> You allow tools to act more autonomously *inside a controlled environment* where mistakes are affordable and reversible.

Characteristics of a good sandbox:

1. Everything is under **git**, so you can inspect diffs and roll back with `git reset --hard`.
2. You can afford to **delete the entire directory** if needed.
3. There are no irreplaceable secrets or data.
4. Tools are restricted to the sandbox paths (no access to random parts of your filesystem).

### 3.1 Sandbox examples

1. **Soft sandbox (recommended)** – extra clone or git worktree per project:
   - Main repo: your “serious” working copy.
   - Sandbox clone: AI playground where tools can run with fewer prompts.

2. **Harder sandbox** – separate WSL instance or VM:
   - Clone repos there, let AI tools run more freely.
   - Move good changes back via git (push from sandbox, pull into main).

3. **Direct-mount sandbox** – shared folders:
   - Tools run in WSL or container but operate on a mounted Windows repo.
   - Path boundaries and config must still restrict destructive operations.

### 3.2 How sandbox interacts with local dirs and GitHub

The sandbox **doesn’t need to touch your main working copy directly**:

1. You clone the GitHub repo **into the sandbox**.
2. AI tools make changes there.
3. When satisfied:
   - `git commit` and `git push` from sandbox to GitHub.
4. In your main working copy:
   - `git fetch` and `git merge` (or open PRs and merge).

Git/GitHub become the **bridge** between sandbox and primary working copies.

---

## 4. Soft Sandbox Layout (Per-Project)

You want one sandbox **per project**, not per tool.

### 4.1 Recommended layout

**Windows:**

```text
# Main working copies
C:\Users\richg\ALL_AI\pipeline_plus
C:\Users\richg\ALL_AI\error_pipeline
C:\Users\richg\ALL_AI\file_alchemist

# AI sandbox clones
C:\Users\richg\AI_SANDBOX\pipeline_plus_sandbox
C:\Users\richg\AI_SANDBOX\error_pipeline_sandbox
C:\Users\richg\AI_SANDBOX\file_alchemist_sandbox
```

**WSL:**

```text
~/projects/pipeline_plus
~/ai-sandbox/pipeline_plus_sandbox

~/projects/error_pipeline
~/ai-sandbox/error_pipeline_sandbox
```

Inside each `*_sandbox` clone you keep the per-tool instruction/config files:

- `CLAUDE.md` – Claude Code project rules.
- `AGENTS.md` – Codex project rules.
- `.aider.conf.yml` – Aider config and behavior.
- `.github/copilot-instructions.md` – Copilot repo instructions.

All CLI tools share the **same sandbox clone per project**.

---

## 5. Per-Tool Soft Sandbox Solutions

Below: how each tool should be configured to operate in the soft-sandbox pattern.

### 5.1 Claude Code

**Run location:**

```bash
cd "$AI_SANDBOX_ROOT/pipeline_plus_sandbox"
claude
```

**Config file:** `~/.claude/settings.json`

Minimal example:

```json
{
  "model": "claude-3-5-sonnet"
}
```

**Instruction doc:** `CLAUDE.md` in each repo (sandbox & main)

Example `CLAUDE.md` for sandbox:

```md
# Claude Instructions – AI Sandbox Clone

Context:
- This repo is an AI sandbox clone of the main project.
- All edits here are experimental and must be committed on ai-sandbox/* branches.

Primary contract:
- If `docs/DEV_RULES_CORE.md` exists, treat it as the governing rules document.
- If any request conflicts with that file, explain the conflict before proceeding.

Rules:
- Only edit files inside this repo.
- Prefer small, atomic changes with clear explanations.
- When changing behavior, add or update tests where possible.
- Use unified diffs for edits whenever possible.

Safety:
- Explain destructive commands before you run them.
- Never modify files outside the repository root.
```

### 5.2 Aider

**Run location:**

```bash
cd "$AI_SANDBOX_ROOT/pipeline_plus_sandbox"
aider
```

**Config file:** `.aider.conf.yml` in repo root

Example for sandbox:

```yaml
# .aider.conf.yml – AI sandbox clone

model: anthropic/claude-3-7-sonnet-20250219  # or your preferred model
auto-commits: true
branch: ai-sandbox/aider

# Automatically load the core rules document
read:
  - docs/DEV_RULES_CORE.md
```

### 5.3 GitHub Copilot & Copilot CLI

**Run location:**

```bash
cd "$AI_SANDBOX_ROOT/pipeline_plus_sandbox"
copilot --allow-all-tools    # if you trust the sandbox
```

**Repo instructions file:** `.github/copilot-instructions.md`

Example content:

```md
# Copilot Instructions – AI Sandbox Clone

Primary contract:
- This repository uses `docs/DEV_RULES_CORE.md` as the canonical development rules.
- Apply rules DR-1.* through DR-9.* from that document when generating suggestions.

Behavior:
- Keep changes small, atomic, and test-aware.
- Only modify files inside this repository.
- Prefer adding or updating tests for behavior changes.
- Never generate or commit real secrets; use placeholders like `YOUR_API_KEY_HERE`.

Sandbox:
- This is an AI sandbox clone; experimental changes are allowed, but must remain readable and revertible.
```

**Environment for fewer prompts:**

```bash
# WSL (~/.bashrc)
export COPILOT_ALLOW_ALL=1
```

### 5.4 Codex CLI (WSL)

**Run location:**

```bash
cd "$AI_SANDBOX_ROOT/pipeline_plus_sandbox"
codex
```

**Config file:** `~/.codex/config.toml`

Example:

```toml
# Codex config – WSL

model = "gpt-5.1-codex"
sandbox_mode = "workspace-write"
```

**Instruction doc:** `AGENTS.md` in repo root

Example `AGENTS.md`:

```md
# Codex Instructions – AI Sandbox Clone

Primary contract:
- Treat `docs/DEV_RULES_CORE.md` as the governing development rules for this repository.

Behavior:
- Read and follow rules DR-1.* through DR-9.* in `DEV_RULES_CORE.md`.
- Keep edits within this git repo only.
- Prefer small, atomic changes and explain your plan before large refactors.
- Update or propose tests when changing behavior.
- Avoid destructive commands outside the project; if needed inside, explain them first.

Sandbox:
- This is an AI sandbox clone; work may be experimental but should still produce clear commits and readable diffs.
```

### 5.5 Codex CLI (Windows)

**Run location:**

```powershell
cd C:\Users\richg\AI_SANDBOX\pipeline_plus_sandbox
codex
```

**Config file:** `C:\Users\richg\.codex\config.toml`

Example:

```toml
# Codex config – Windows

model = "gpt-5.1-codex"
sandbox_mode = "workspace-write"
```

---

## 6. Canonical `DEV_RULES_CORE.md`

Place this file at:

> `docs/DEV_RULES_CORE.md`

```md
---
doc_id: DEV_RULES_CORE
version: 1.0.0
status: active
applies_to:
  - all_tools
  - all_repos
  - all_sandboxes
---

# Development Rules – Core Canon

> This document is the **single source of truth** for how AI coding tools must behave in this repository.
> All tools (Claude Code, Codex, Aider, GitHub Copilot CLI, etc.) MUST follow these rules.

## 1. Scope & Hierarchy

- DR-1.1 – This document applies to:
  - Main repo working copies
  - AI sandbox clones (e.g. `*_sandbox`)
  - All AI coding tools and agents operating in this repo
- DR-1.2 – If any other instructions conflict with this file, **this file wins** unless explicitly overridden in a project-specific spec.
- DR-1.3 – If a phase/workstream spec file defines stricter rules, tools MUST obey the stricter rule.

## 2. Sandbox & File Boundaries

- DR-2.1 – Do **not** read, write, move, or delete files outside the current git repo directory.
- DR-2.2 – Treat sandbox clones (e.g. `*_sandbox`) as **authoritative workspaces** for automated edits.
- DR-2.3 – When running file or shell commands, assume the repo root is the top-level boundary; never traverse above it for destructive operations.

## 3. Editing & Patch Rules

- DR-3.1 – Prefer **small, atomic changes** over large refactors.
- DR-3.2 – When changing code, tools SHOULD:
  - Explain the intended change briefly.
  - Apply the minimal diff needed.
  - Show or emit a unified diff when possible.
- DR-3.3 – When editing existing files, preserve:
  - Existing formatting and style where practical.
  - Existing comments and documentation unless they are clearly wrong.
- DR-3.4 – When large refactors are unavoidable, break them into **ordered steps** and commit/propose them in multiple smaller chunks.

## 4. Testing Requirements

- DR-4.1 – Any change that alters behavior SHOULD be accompanied by:
  - New tests, or
  - Updates to existing tests.
- DR-4.2 – When a test framework is detected (e.g. `pytest`, `unittest`, `Pester`, `jest`, etc.), tools SHOULD:
  - Add or update tests in the matching framework.
  - Suggest or run the appropriate test command.
- DR-4.3 – If tests are not updated, the tool MUST explain why (e.g. “no test harness exists for this area yet”).

## 5. Phase & Workstream Awareness (If Present)

> This section only applies if phase/workstream specs exist (e.g. `PHASE_SPEC_*.md`, `WORKSTREAM_*.md`).

- DR-5.1 – When a phase or workstream is referenced, tools MUST treat the corresponding spec file(s) as the **contract** for:
  - Inputs
  - Outputs
  - Acceptance criteria
- DR-5.2 – Tools SHOULD align edits and commits with the active phase/workstream ID (e.g. include `PH-XXX` / `WS-YYY` in commit messages or summaries).
- DR-5.3 – If a requested change conflicts with a phase/workstream spec, tools MUST:
  - Highlight the conflict, and
  - Ask for clarification instead of silently ignoring the spec.

## 6. Git, Branching & Commits

- DR-6.1 – In sandbox clones, tools SHOULD:
  - Work on dedicated branches (e.g. `ai-sandbox/<tool>/<topic>`), or
  - Clearly describe the changes if committing directly to the default branch.
- DR-6.2 – Commit messages SHOULD:
  - Be short but descriptive.
  - Reference relevant phase/workstream IDs if known.
- DR-6.3 – Tools MUST NOT rewrite git history (e.g. `git push --force`) unless explicitly instructed.

## 7. Safety & Secrets

- DR-7.1 – Never invent or commit real secrets (API keys, passwords, tokens). Use clear placeholders like `YOUR_API_KEY_HERE`.
- DR-7.2 – Tools MUST NOT read from obvious secret locations (e.g. `.env` files, `secrets/` directories) unless explicitly asked.
- DR-7.3 – Destructive commands (`rm -rf`, mass renames, bulk deletions) MUST:
  - Be clearly explained first.
  - Be scoped to the current repo.
  - Only be executed when explicitly confirmed (or when the calling environment is documented as disposable).

## 8. Code Style & Documentation

- DR-8.1 – Prefer clear, idiomatic code in the primary language of the repo.
- DR-8.2 – When adding non-trivial logic, tools SHOULD:
  - Add concise comments **only where needed**.
  - Avoid redundant or obvious comments.
- DR-8.3 – Keep public/function interfaces stable when possible; if changed, clearly explain the impact.

## 9. Tool Interoperability

- DR-9.1 – Assume multiple AI tools may work on this repo; do not rely on tool-specific artifacts that break others.
- DR-9.2 – Prefer handoff formats that are easy to consume across tools (e.g. unified diffs, small Markdown specs).
- DR-9.3 – When generating instructions for other tools, reference this file by path (`docs/DEV_RULES_CORE.md`) and assume they also follow these rules.

---
End of DEV_RULES_CORE
```

---

## 7. Summary

This file brings together the key ideas from the conversation:

- Use **per-project sandbox clones** where AI tools can act more freely.
- Encode your global coding philosophy and guardrails in **`DEV_RULES_CORE.md`**.
- Have each tool’s instruction/config system **point at that file**:
  - Claude Code → `CLAUDE.md`
  - Codex → `AGENTS.md`
  - Aider → `.aider.conf.yml` with `read: docs/DEV_RULES_CORE.md`
  - Copilot → `.github/copilot-instructions.md`
- Use tool configs (`settings.json`, `config.toml`, `.aider.conf.yml`, env vars) to control *power & defaults* (models, sandboxing, auto-approval).
- Use instruction docs to control *behavior & style* (atomic changes, tests, phase awareness, safety).

You can now feed this single document to any “agentic AI” to understand and enforce your CLI tool behavior strategy.
