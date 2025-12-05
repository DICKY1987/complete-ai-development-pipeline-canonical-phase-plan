# PAT-EDIT-WORKTREE-001: Implement Changes Safely

## Purpose
Apply modifications while respecting repository scope and preserving user work.

## Steps
1. Confirm target files are within allowed scope.
2. Use minimal diffs and preserve existing style.
3. Prefer incremental saves with clear checkpoints.
4. Avoid reverting user changes; integrate with current state.

## Success Criteria
- Changes confined to approved files.
- Diffs are minimal and purposeful.
- No unrelated files touched.
