---
doc_id: DOC-GUIDE-AGENTS-1111
---

# Codex CLI Instructions - AI Sandbox Clone (Windows)

## Context
- This is an **AI sandbox clone** for experimental development
- All changes are git-tracked and reversible
- This environment is specifically designed for AI-assisted development

## Primary Contract
**CRITICAL:** The file `docs\DEV_RULES_CORE.md` is the **governing rules document** for all AI tools.
- Read and follow rules DR-1.* through DR-9.* from that file
- If any request conflicts with DEV_RULES_CORE.md, explain the conflict before proceeding
- These rules apply to ALL tools working in this repository

## Workspace Configuration
For this sandbox clone, you may use:
```
workspace_mode = "workspace-write"
```

## Sandbox-Specific Behavior
1. **Editing scope**
   - Only modify files within this git repository
   - Treat the repo root as the absolute boundary
   - Never traverse above this directory

2. **Branch discipline**
   - Work on `ai-sandbox/codex/*` branches
   - Use descriptive branch names
   - Commit frequently with clear messages

3. **Change philosophy**
   - Prefer small, atomic commits
   - Explain plans before large refactors
   - Show unified diffs
   - Keep changes readable

4. **Testing**
   - Add or update tests when changing behavior
   - Run existing tests when appropriate
   - Explain if tests aren't updated

5. **Safety**
   - Maintain professional quality
   - Avoid destructive commands
   - Keep changes git-revertible

## Windows-Specific Notes
- Use backslash path separators: `docs\DEV_RULES_CORE.md`
- Respect Windows file attributes
- Be aware of case-insensitive file system

## Phase & Workstream Awareness
If phase specs exist:
- Treat them as contracts
- Include IDs in commits
- Highlight conflicts

## Tool Interoperability
- Assume multiple AI tools may work here
- Reference `docs\DEV_RULES_CORE.md`
- Use standard formats

---
End of Codex sandbox instructions (Windows)
