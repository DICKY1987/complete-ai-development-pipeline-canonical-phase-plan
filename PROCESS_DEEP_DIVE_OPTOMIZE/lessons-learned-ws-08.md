# WS-08 lessons learned

WS-08 refactored the prompt/aider subsystem by moving prompt building and
templating from `src/pipeline/` to `aider/` with a thin compatibility layer.
This document captures key risks, fixes, and patterns to carry forward.

## Refactoring risks and mitigations

- Template drift: mismatched variable names between code and templates caused
  missing context. Mitigation: centralized `build_*_prompt()` functions and a
  single templates directory at `aider/templates/prompts/`.
- Signature changes: the orchestrator expected the old `run_aider_*` signatures.
  Mitigation: a compatibility shim in `src/pipeline/prompts.py` that translates
  to the new `aider.engine` APIs.
- Windows console/Unicode: Aider invocations on Windows can hit encoding quirks.
  Mitigation: set `PYTHONIOENCODING=utf-8` and avoid non-ASCII in command-line
  message arguments by using `--message-file`.
- Dry-run gaps: Dry-run skips tool execution, so prompt files are not written.
  Mitigation: unit/integration tests directly exercise prompt rendering.

## Fixed regressions (root causes)

- Template naming mismatch: ensure templates use `repo_root` (not `repo_path`).
- Function signature compatibility: wrapper maps old orchestration signature to
  new engine call sites.
- Context key mismatch: use `worktree_path` consistently across engine and
  templates.
- Template variable defaults: guard against empty lists (`files_scope`,
  `files_create`, `acceptance_tests`) to avoid rendering gaps.

## Compatibility patterns

- Keep `aider/engine.py` as the source of truth for prompt rendering and tool
  execution parameters; re-export via `core/prompts.py` and shim via
  `src/pipeline/prompts.py`.
- Maintain prompt templates in `aider/templates/prompts/` with simple, stable
  variables and avoid logic in templates.

## Template best practices

- Keep prompts deterministic; avoid timestamps in acceptance criteria.
- Render all context explicitly (ids, repo paths, file scopes, tests, gate).
- Ensure lists render even when empty (or provide safe defaults).

## Next steps

- Leave WS-10 deferred until a manual implementation is completed or an ADR
  authorizes dependency relaxation.
- Add optional unit tests around `build_edit_prompt` and `build_fix_prompt` to
  guard against future drift.

