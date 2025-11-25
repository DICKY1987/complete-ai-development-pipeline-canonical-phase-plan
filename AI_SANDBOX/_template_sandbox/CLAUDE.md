# Claude Code Instructions - AI Sandbox Clone

## Context
- This repository is an **AI sandbox clone** of the main project
- All changes here are experimental and must remain git-revertible
- This clone is specifically for AI-assisted development and testing

## Primary Contract
**CRITICAL:** If `docs/DEV_RULES_CORE.md` exists in this repository:
- Treat it as the **governing rules document** for all AI tools
- Follow rules DR-1.* through DR-9.* from that file
- If any request conflicts with DEV_RULES_CORE.md, explain the conflict before proceeding

## Sandbox-Specific Rules
1. **Branch discipline**
   - Work on `ai-sandbox/claude/*` branches or clearly describe changes if on main
   - Use descriptive branch names: `ai-sandbox/claude/feature-name`

2. **Editing scope**
   - Only modify files within this repository root
   - Never traverse above the repo boundary for destructive operations
   - Treat this directory as the absolute top-level boundary

3. **Change philosophy**
   - Prefer small, atomic commits with clear messages
   - Show unified diffs when making edits
   - Explain your plan before large refactors

4. **Testing requirements**
   - When changing behavior, add or update tests
   - Run existing tests when appropriate
   - If tests aren't updated, explain why

5. **Safety**
   - This is a sandbox, but changes should still be clean and professional
   - Avoid destructive commands; if needed, explain first
   - Keep all changes readable and reviewable

## Handoff to Other Tools
When generating work for other AI tools:
- Reference `docs/DEV_RULES_CORE.md` by path
- Assume they also follow the same core rules
- Use standard formats (unified diffs, Markdown specs)

## Phase & Workstream Awareness
If phase specs exist (e.g., `PHASE_SPEC_*.md`, `WORKSTREAM_*.md`):
- Treat them as contracts for inputs, outputs, acceptance criteria
- Include phase/workstream IDs in commit messages when relevant
- Highlight conflicts with specs rather than silently ignoring them

---
End of Claude sandbox instructions
