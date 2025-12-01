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
- DR-4.3 – If tests are not updated, the tool MUST explain why (e.g. "no test harness exists for this area yet").

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
