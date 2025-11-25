# GitHub Copilot Instructions - AI Sandbox Clone

## Context
This repository is an **AI sandbox clone** designed for AI-assisted development and experimentation.
All changes must remain git-tracked and reversible.

## Primary Contract
**CRITICAL:** The file `docs/DEV_RULES_CORE.md` contains the **canonical development rules** for this repository.

When generating suggestions or executing commands:
- Read and apply rules DR-1.* through DR-9.* from `docs/DEV_RULES_CORE.md`
- If any suggestion conflicts with those rules, explain the conflict
- Treat DEV_RULES_CORE.md as authoritative for all AI tools

## Behavioral Guidelines

### 1. Editing Philosophy
- Make **small, atomic changes** (DR-3.1)
- Explain changes briefly before applying (DR-3.2)
- Preserve existing formatting and style (DR-3.3)
- Show unified diffs when possible

### 2. Testing Requirements
- Add or update tests when changing behavior (DR-4.1)
- Detect and use existing test frameworks (DR-4.2)
- Explain if tests aren't updated (DR-4.3)

### 3. File Boundaries
- Only modify files within this repository (DR-2.1)
- Treat repo root as absolute boundary (DR-2.3)
- Never traverse above this directory for destructive operations

### 4. Git & Branching
- Work on `ai-sandbox/copilot/*` branches when appropriate (DR-6.1)
- Write short, descriptive commit messages (DR-6.2)
- Never force-push or rewrite history (DR-6.3)

### 5. Safety & Secrets
- Never generate real secrets (DR-7.1)
- Use placeholders: `YOUR_API_KEY_HERE`
- Explain destructive commands before execution (DR-7.3)
- Scope all operations to this repository

### 6. Code Style
- Use clear, idiomatic code (DR-8.1)
- Add concise comments only where needed (DR-8.2)
- Avoid obvious or redundant comments
- Keep public interfaces stable when possible (DR-8.3)

### 7. Tool Interoperability
- Assume multiple AI tools work on this repo (DR-9.1)
- Use standard formats for outputs (DR-9.2)
- Reference `docs/DEV_RULES_CORE.md` when generating instructions (DR-9.3)

## Phase & Workstream Awareness
If phase specification files exist (e.g., `PHASE_SPEC_*.md`, `WORKSTREAM_*.md`):
- Treat them as binding contracts (DR-5.1)
- Include phase/workstream IDs in commit messages (DR-5.2)
- Highlight conflicts with specs rather than ignoring them (DR-5.3)

## Sandbox Environment
This clone is specifically for:
- Experimental AI-assisted development
- Testing new features before merging to main
- Rapid iteration with AI tools
- Safe, reversible changes

All operations should maintain:
- Professional code quality
- Clear git history
- Readable, reviewable changes
- Compatibility with other AI tools

---
End of Copilot instructions
