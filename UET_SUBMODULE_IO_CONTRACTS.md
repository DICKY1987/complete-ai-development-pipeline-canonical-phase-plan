# UET Submodule I/O Contracts v1.0

**Status**: Active
**Last Updated**: 2025-11-30
**Purpose**: Defines stable data contracts for all cross-module communication

---

## 0. Contract Principles

**Rule**: Any new helper or submodule MUST accept/return only these shapes (or documented extensions) when crossing module boundaries.

**Why**: Prevents AI from inventing arbitrary data structures and ensures deterministic, testable integration.

---

## 1. Path & Repository Contracts

### 1.1 RepoPathRefV1

Logical reference to a file/directory in the repository.

```python
RepoPathRefV1 = {
    "module_id": str,      # optional - e.g. "mod.core.state"
    "doc_id": str,         # optional - e.g. "DOC-CORE-STATE-DB-001"
    "rel_path": str,       # optional - e.g. "core/state/db.py"
    "workspace": str,      # required - "main" | "agent-1-ws-22"
}
```

**Contract**:
- Callers MUST pass logical info (module_id, doc_id, rel_path), NOT pre-joined OS paths
- At least one of `{doc_id, rel_path}` is required
- `workspace` controls which worktree/root to resolve against

### 1.2 ResolvedPathV1

Absolute, normalized file path after resolution.

```python
ResolvedPathV1 = {
    "abs_path": str,       # e.g. "C:/.../core/state/db.py"
    "rel_path": str,       # e.g. "core/state/db.py"
    "workspace": str,      # e.g. "agent-1-ws-22"
}
```

**Contract**:
- Always normalized (no `..`, consistent separators)
- Never creates directories or files – pure resolution only
- All filesystem operations MUST use this contract

---

## 2. ID & Registry Contracts

### 2.1 DocIdParseResultV1

Structured representation of a doc_id.

```python
DocIdParseResultV1 = {
    "raw": str,            # e.g. "DOC-CORE-STATE-DB-001"
    "category": str,       # e.g. "DOC"
    "domain": str,         # e.g. "CORE"
    "area": str,           # e.g. "STATE"
    "name": str,           # e.g. "DB"
    "sequence": int,       # e.g. 1
}
```

**Contracts**:
- `parse_doc_id(str) -> DocIdParseResultV1 | raises DocIdError`
- `mint_doc_id(category, domain, area, name) -> str`
- Callers NEVER string-split doc_ids themselves

### 2.2 DocRegistryEntryV1

Single entry from doc_id registry.

```python
DocRegistryEntryV1 = {
    "doc_id": str,         # e.g. "DOC-CORE-STATE-DB-001"
    "path": str,           # relative path
    "module_id": str,      # e.g. "mod.core.state"
    "status": str,         # "active" | "deprecated"
    "category": str,       # e.g. "core"
    "title": str,          # human-readable
}
```

**Contracts**:
- `get_doc(doc_id) -> DocRegistryEntryV1 | None`
- `find_docs_by_module(module_id) -> list[DocRegistryEntryV1]`
- Read-only – no mutation via this interface

---

## 3. Logging & Audit Contracts

### 3.1 LogEventV1

Universal event log entry (JSONL).

```python
LogEventV1 = {
    "timestamp": str,      # ISO 8601 UTC
    "event_type": str,     # "phase.completed" | "task.failed" | "error.detected"
    "run_id": str,         # e.g. "RUN-..."
    "ws_id": str,          # optional workstream ID
    "phase_id": str,       # optional phase ID
    "doc_ids": list[str],  # related documents
    "summary": str,        # short human-readable line
    "details": dict,       # arbitrary JSON-serializable data
}
```

**Contract**:
- `append_event(log_path: ResolvedPathV1, event: LogEventV1) -> None`
- MUST be append-only, atomic (temp file → move)
- Never throws on extra keys in `details`

---

## 4. Run & Execution Contracts

### 4.1 RunRecordV1

Database record for a single phase/workstream run.

```python
RunRecordV1 = {
    "run_id": str,         # e.g. "RUN-..."
    "ws_id": str,          # workstream ID
    "phase_id": str,       # phase ID
    "status": str,         # "queued" | "running" | "succeeded" | "failed"
    "started_at": str,     # ISO 8601
    "finished_at": str,    # ISO 8601, optional
    "meta": dict,          # additional context
}
```

**Contracts**:
- `create_run(ws_id, phase_id, context) -> RunRecordV1`
- `update_run_status(run_id, status, meta=None) -> RunRecordV1`

### 4.2 PatchRecordV1

Database record for a patch artifact.

```python
PatchRecordV1 = {
    "patch_id": str,       # e.g. "PATCH-..."
    "run_id": str,
    "ws_id": str,
    "phase_id": str,
    "files_changed": list[str],
    "hash": str,           # e.g. "sha256:..."
    "path": str,           # e.g. ".ledger/patches/..."
}
```

**Contract**:
- `record_patch(patch_path, run_context, files_changed) -> PatchRecordV1`

---

## 5. Pattern & Execution Contracts

### 5.1 PatternRefV1

Reference to a specific pattern.

```python
PatternRefV1 = {
    "pattern_id": str,     # e.g. "PAT-EXEC-ATOMIC-CREATE-001"
    "version": str,        # e.g. "1.2.0"
}
```

### 5.2 PatternDefinitionV1

Full pattern specification.

```python
PatternDefinitionV1 = {
    "pattern_id": str,
    "description": str,
    "operation_kind": str, # e.g. "EXEC-ATOMIC-CREATE"
    "inputs_schema": dict,
    "outputs_schema": dict,
    "executor_ref": str,   # e.g. "python:patterns.exec.atomic_create.run"
}
```

**Contracts**:
- `get_pattern(pattern_id) -> PatternDefinitionV1`
- `find_patterns(operation_kind, file_type, tool) -> list[PatternDefinitionV1]`

### 5.3 ExecutionRequestV1

Request to execute a task/pattern.

```python
ExecutionRequestV1 = {
    "operation_kind": str, # e.g. "EXEC-ATOMIC-CREATE"
    "workspace": str,      # workspace identifier
    "file_scope": dict,    # create/modify/read_only files
    "context": dict,       # ws/phase/module info
    "inputs": dict,        # pattern-specific inputs
}
```

### 5.4 ExecutionResultV1

Result of task/pattern execution.

```python
ExecutionResultV1 = {
    "success": bool,
    "stdout": str,
    "stderr": str,
    "files_touched": list[str],
    "patch_path": str,     # optional
    "error": dict,         # optional ErrorEventV1
}
```

**Contract**:
- `run_pattern(pattern_ref: PatternRefV1, request: ExecutionRequestV1) -> ExecutionResultV1`
- All executors MUST implement this signature
- NEVER raises unhandled exceptions – errors go in `error` field

---

## 6. Error & Diagnostic Contracts

### 6.1 ErrorEventV1

Structured error event.

```python
ErrorEventV1 = {
    "error_id": str,       # e.g. "ERR-..."
    "kind": str,           # "execution_failure" | "validation_failure" | "pattern_mismatch"
    "message": str,        # short description
    "details": dict,       # stack trace, exit code, etc.
    "ws_id": str,
    "phase_id": str,
    "run_id": str,
}
```

**Contracts**:
- `build_error(kind, message, details, context) -> ErrorEventV1`
- `log_error(error: ErrorEventV1) -> None`
- Error plugins receive ONLY `ErrorEventV1` + optionally `ExecutionRequestV1`/`ExecutionResultV1`

---

## 7. Git & Worktree Contracts

### 7.1 GitWorkspaceRefV1

Reference to a git workspace.

```python
GitWorkspaceRefV1 = {
    "workspace": str,      # "main" | "agent-1-ws-22"
    "root_path": str,      # absolute path
}
```

### 7.2 GitStatusV1

Status of a git workspace.

```python
GitStatusV1 = {
    "workspace": str,
    "dirty_files": list[str],
    "ahead_by": int,
    "behind_by": int,
}
```

**Contracts**:
- `get_workspace_status(workspace) -> GitStatusV1`
- `ensure_clean_workspace(workspace, allow_untracked=False) -> None | raises`
- `create_worktree_for_ws(ws_id) -> GitWorkspaceRefV1`

---

## 8. Tool Runner Contracts

### 8.1 ToolRunRequestV1

Request to run external tool.

```python
ToolRunRequestV1 = {
    "cmd": list[str],      # e.g. ["python", "-m", "pytest", "-q"]
    "cwd": str,            # working directory
    "env": dict,           # merged over defaults
    "timeout_seconds": int,
}
```

### 8.2 ToolRunResultV1

Result of tool execution.

```python
ToolRunResultV1 = {
    "exit_code": int,
    "stdout": str,
    "stderr": str,
    "duration_seconds": float,
}
```

**Contract**:
- `run_tool(request: ToolRunRequestV1) -> ToolRunResultV1`
- On timeout: `exit_code` non-zero + `stderr` describes it
- NEVER raises exceptions – all errors in result

---

## 9. Enforcement

### 9.1 Validation

All submodules implementing these contracts MUST:
1. Accept/return ONLY these shapes at public boundaries
2. Include type hints matching these contracts
3. Include tests verifying contract compliance

### 9.2 CI Integration

- Pre-commit hooks check for contract violations
- Contract schema validation in test suite
- Documentation MUST reference contract version (e.g. "uses ExecutionRequestV1")

---

## 10. Extension Guidelines

To extend a contract:
1. Create new version (e.g. `ExecutionRequestV2`)
2. Document migration path
3. Support both versions during transition period
4. Deprecate old version with timeline
5. Update all consumers before removing old version

**Never** modify existing versioned contracts in-place.
