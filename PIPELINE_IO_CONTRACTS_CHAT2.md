Nice, this is exactly the right question to be asking *before* you let more AI loose in the repo.

Think of it as: you’ve mostly nailed **“big-module I/O”** (planning ↔ engine ↔ error ↔ persistence).
Now you need **“library-level I/O contracts”** so that *submodules/helpers/utilities* stay stable and safe to call.

Below is a concrete list of the contracts I’d nail down and freeze.

---

## 0. Meta-rule: each helper must have a **clear public surface**

For every shared module (`modules/error_shared`, future `modules/path_shared`, `modules/id_shared`, etc.), define:

* A single **“public API” section** in the doc:

  * `Public types`: DTOs / dict shapes it accepts/returns
  * `Public functions`: signatures + behavior guarantees
* Everything else is “internal – no external callers”.

You don’t need to over-type Python, but you **do** need consistent shapes.

---

## 1. Path / Repo / Worktree helpers

**Why:** you’re about to have a lot of code that needs to go from `doc_id` / `module_id` / logical paths → real files in main/worktrees. If those callers hand each other raw strings, AI will break things.

### 1.1 Input: logical references

Define a small struct (even if it’s just a dict convention):

```python
RepoPathRefV1 = {
  "module_id": "mod.core.state",     # optional
  "doc_id": "DOC-CORE-STATE-DB-001", # optional
  "rel_path": "core/state/db.py",    # optional
  "workspace": "main" | "agent-1-ws-22",
}
```

**Contract:**

* Callers **must** pass *logical* info (module_id, doc_id, rel_path), not pre-joined OS paths.
* At least one of `{doc_id, rel_path}` is required.
* `workspace` controls which worktree/root you resolve against.

### 1.2 Output: resolved paths

Your path helper guarantees:

```python
ResolvedPathV1 = {
  "abs_path": "C:/.../complete-ai.../core/state/db.py",
  "rel_path": "core/state/db.py",
  "workspace": "agent-1-ws-22",
}
```

* Always normalized (no `..`, consistent separators).
* Never creates directories or files – **pure resolution only**.

All submodules that “touch the filesystem” should depend on *this* contract, not re-invent path logic.

---

## 2. ID / Registry helpers (doc_id, module_id, pattern_id)

Right now, a lot of logic *assumes* doc/module IDs exist and are valid. You want that encoded into helpers.

### 2.1 ID parsing / formatting

Define, for all callers:

```python
DocIdParseResultV1 = {
  "raw": "DOC-CORE-STATE-DB-001",
  "category": "DOC",
  "domain": "CORE",
  "area": "STATE",
  "name": "DB",
  "sequence": 1,
}
```

**Contracts:**

* `parse_doc_id(str) -> DocIdParseResultV1 | raises DocIdError`
* `mint_doc_id(category, domain, area, name) -> str`
* `lookup_doc_path(doc_id) -> ResolvedPathV1`

Callers **never** muck with `DOC-...` by string-splitting themselves.

### 2.2 Registry query helpers

Have “read-only” registry helpers:

```python
DocRegistryEntryV1 = {
  "doc_id": "DOC-CORE-STATE-DB-001",
  "path": "core/state/db.py",
  "module_id": "mod.core.state",
  "status": "active" | "deprecated",
}
```

Contract:

* `get_doc(doc_id)` → entry or `None`
* `find_docs_by_module(module_id)` → list[entry]
* No write/mutation here – that’s for dedicated tooling.

---

## 3. JSONL / audit / logging helpers

You already have `jsonl_manager` in `error_shared`. This is one of the most important internal contracts.

### 3.1 Input: log event payload

Define once, use everywhere:

```python
LogEventV1 = {
  "timestamp": "2025-11-30T01:23:45Z",
  "event_type": "phase.completed" | "task.failed" | "error.detected" | ...,
  "run_id": "RUN-...",
  "ws_id": "WS-...",
  "phase_id": "PH-...",
  "doc_ids": ["DOC-..."],
  "summary": "Short human-readable line",
  "details": {...},  # arbitrary JSON-serializable dict
}
```

Helper contract:

* `append_event(log_path: ResolvedPathV1, event: LogEventV1) -> None`
* Must be **append-only**, atomic (temp file → move), and never throw on “extra keys”.

All helpers/submodules that write JSONL should **only** use this helper.

---

## 4. Run DB / patch ledger helpers

You don’t want every script crafting its own SQL for `uet_runs`, `step_attempts`, etc.

### 4.1 Run lifecycle helper

Define:

```python
RunRecordV1 = {
  "run_id": "RUN-...",
  "ws_id": "WS-...",
  "phase_id": "PH-...",
  "status": "queued" | "running" | "succeeded" | "failed",
  "started_at": "...",
  "finished_at": "...",
  "meta": {...},
}
```

Helper contracts:

* `create_run(ws_id, phase_id, context) -> RunRecordV1`
* `update_run_status(run_id, status, meta=None) -> RunRecordV1`
* `record_step_attempt(run_id, step_payload: ExecutionRequestV1, result: ExecutionResultV1)`

### 4.2 Patch descriptor helper

```python
PatchRecordV1 = {
  "patch_id": "PATCH-...",
  "run_id": "RUN-...",
  "ws_id": "WS-...",
  "phase_id": "PH-...",
  "files_changed": ["core/state/db.py"],
  "hash": "sha256:...",
  "path": ".ledger/patches/WS-...-RUN-....patch",
}
```

Helper:

* `record_patch(patch_path: ResolvedPathV1, run_context, files_changed) -> PatchRecordV1`

Execution submodules (like a Python executor, MQL executor, etc.) should **only** interact with DB via these helpers.

---

## 5. Pattern / template helpers

This is the glue between raw execution helpers and the pattern registry.

### 5.1 Pattern lookup

Define:

```python
PatternRefV1 = {
  "pattern_id": "PAT-EXEC-ATOMIC-CREATE-001",
  "version": "1.2.0",
}

PatternDefinitionV1 = {
  "pattern_id": "...",
  "description": "...",
  "operation_kind": "EXEC-ATOMIC-CREATE",
  "inputs_schema": {...},
  "outputs_schema": {...},
  "executor_ref": "python:patterns.exec.atomic_create.run",
}
```

Helpers:

* `get_pattern(pattern_id) -> PatternDefinitionV1`
* `find_patterns(operation_kind, file_type, tool) -> list[PatternDefinitionV1]`

### 5.2 Pattern execution wrapper

Central contract:

```python
ExecutionRequestV1 = {
  "operation_kind": "EXEC-ATOMIC-CREATE",
  "workspace": "agent-1-ws-22",
  "file_scope": {...},
  "context": {...},      # ws/phase/module info
  "inputs": {...},       # pattern-specific inputs
}

ExecutionResultV1 = {
  "success": True/False,
  "stdout": "...",
  "stderr": "...",
  "files_touched": [...],
  "patch_path": "....patch" | None,
  "error": None | ErrorEventV1,
}
```

Pattern helper:

* `run_pattern(pattern_ref: PatternRefV1, request: ExecutionRequestV1) -> ExecutionResultV1`

Every submodule that “does work” (e.g. Python file modifier, tests runner) should implement this contract so the orchestrator + pattern automation can treat them uniformly.

---

## 6. Error / diagnostic helpers

You already have `error_shared` with types/time/hashing/jsonl/env/security. Lock the **error event** shape.

```python
ErrorEventV1 = {
  "error_id": "ERR-...",
  "kind": "execution_failure" | "validation_failure" | "pattern_mismatch" | ...,
  "message": "Short description",
  "details": {...},  # stack trace, exit code, etc.
  "ws_id": "WS-...",
  "phase_id": "PH-...",
  "run_id": "RUN-...",
}
```

Contracts:

* `build_error(kind, message, details, context) -> ErrorEventV1`
* `log_error(error: ErrorEventV1) -> None` (via JSONL + DB)
* Error plugins always receive **only** `ErrorEventV1` + maybe `ExecutionRequestV1`/`ExecutionResultV1`.

---

## 7. Git / worktree helpers

Given your worktree + ID system, this is critical.

### 7.1 Git action contracts

Helpers like:

```python
GitWorkspaceRefV1 = {
  "workspace": "main" | "agent-1-ws-22",
  "root_path": "...",
}

GitStatusV1 = {
  "workspace": "...",
  "dirty_files": [...],
  "ahead_by": 0,
  "behind_by": 1,
}
```

Contracts:

* `get_workspace_status(workspace) -> GitStatusV1`
* `ensure_clean_workspace(workspace, allow_untracked=False) -> None | raises`
* `create_worktree_for_ws(ws_id) -> GitWorkspaceRefV1`

All submodules needing git info call *these*, not `subprocess.run("git ...")` directly.

---

## 8. CLI / tool runner helpers

Every helper that shells out to `pytest`, `ruff`, `mypy`, etc. should go through a single “tool runner” contract:

```python
ToolRunRequestV1 = {
  "cmd": ["python", "-m", "pytest", "-q"],
  "cwd": "core/",
  "env": {...},      # merged over defaults
  "timeout_seconds": 300,
}

ToolRunResultV1 = {
  "exit_code": 0,
  "stdout": "...",
  "stderr": "...",
  "duration_seconds": 12.34,
}
```

Contract:

* `run_tool(request: ToolRunRequestV1) -> ToolRunResultV1`
* On timeout, `exit_code` non-zero + `stderr` describes it – **no exceptions up the stack**.

---

## 9. How to turn this into something concrete

If you want this captured for your AI CLIs, the next artifact to create is something like:

> `UET_SUBMODULE_IO_CONTRACTS.md` *or* `AI_LIB_IO_CONTRACTS.yaml`

With sections:

1. `RepoPathRefV1` / `ResolvedPathV1`
2. `DocIdParseResultV1` / `DocRegistryEntryV1`
3. `LogEventV1`
4. `RunRecordV1` / `StepAttemptV1` / `PatchRecordV1`
5. `PatternRefV1` / `PatternDefinitionV1` / `ExecutionRequestV1` / `ExecutionResultV1`
6. `ErrorEventV1`
7. `GitWorkspaceRefV1` / `GitStatusV1`
8. `ToolRunRequestV1` / `ToolRunResultV1`

Then add a simple rule:

> **Any new helper or submodule MUST accept/return only these shapes (or documented extensions) when crossing module boundaries.**

If you’d like, I can draft that `UET_SUBMODULE_IO_CONTRACTS.md` in your usual hybrid-spec style so your CLI can generate or verify helpers against it.
