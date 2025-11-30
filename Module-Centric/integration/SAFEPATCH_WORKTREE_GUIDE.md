---
doc_id: DOC-GUIDE-SAFEPATCH-WORKTREE-GUIDE-1453
---

# SafePatch Worktree Guide

Using git worktrees safely with module-centric boundaries.

## Scope
- One worktree per module (or small module set) to isolate changes and reduce conflicts.

## Steps
1) Create worktree for a module:
   `git worktree add .worktrees/<module_id> -b feature/<module_id>`
2) Limit edits to `modules/<module_id>/` and related docs/tests.
3) Run module-scoped validation: manifests, DAG refresh, imports, tests.
4) Commit in the worktree; merge back to main.

## Benefits
- Minimizes cross-module churn and merge conflicts.
- Keeps SafePatch boundaries aligned with module directories.

## Tips
- Avoid editing multiple modules in one worktree unless tightly coupled.
- After merging, remove worktree: `git worktree remove .worktrees/<module_id>`
