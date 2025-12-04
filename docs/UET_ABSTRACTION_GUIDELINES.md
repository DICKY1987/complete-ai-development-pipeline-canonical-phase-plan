---
doc_id: DOC-GUIDE-UET-ABSTRACTION-GUIDELINES-1002
---

# UET Abstraction Guidelines

**Status**: Active
**Last Updated**: 2025-11-30
**Purpose**: Defines when and how to use abstraction in the AI Development Pipeline

---

## 0. Core Principle

> **The contracts ARE your abstractions.**

Abstraction in this system means:
- **Stable data contracts** (see `UET_SUBMODULE_IO_CONTRACTS.md`)
- **Small helper APIs** that enforce those contracts
- **NOT** large class hierarchies or over-engineered frameworks

---

## 1. When Abstraction is Essential

### 1.1 Between Orchestrator and Workers/Tools

**Requirement**: Orchestrator speaks ONLY in `ExecutionRequestV1` / `ExecutionResultV1`.

**Why**: This lets you swap worker internals (new tool, new pattern) with zero orchestrator changes.

**Example**:
```python
# Good: Orchestrator doesn't care about implementation
def run_phase(phase_spec):
    request = build_execution_request(phase_spec)
    result = execute_pattern(request)  # Contract-based call
    return result

# Bad: Orchestrator coupled to specific tool
def run_phase(phase_spec):
    if phase_spec.language == "python":
        return run_python_script(...)  # Tight coupling
    elif phase_spec.language == "powershell":
        return run_ps_script(...)
```

### 1.2 Between Business Logic and Environment (OS, Git, DB)

**Requirement**: Business code NEVER calls environment APIs directly.

**Why**: Lets you change underlying infrastructure without touching business logic.

**Example**:
```python
# Good: Abstracted environment interaction
status = get_workspace_status(workspace)
if status.dirty_files:
    raise WorkspaceNotCleanError()

# Bad: Direct subprocess calls
result = subprocess.run(["git", "status", "--porcelain"])
if result.stdout:  # Brittle, hard to test
    raise WorkspaceNotCleanError()
```

**Protected Boundaries**:
- Git operations → `GitWorkspaceRefV1`, `GitStatusV1`
- Database operations → `RunRecordV1`, `PatchRecordV1`
- File operations → `RepoPathRefV1`, `ResolvedPathV1`
- Logging → `LogEventV1`

### 1.3 Between Patterns and Raw Scripts

**Requirement**: Pattern executors don't care HOW a file is edited.

**Why**: Internals (script, AST transform, LLM) can change without touching orchestrator.

**Example**:
```python
# Good: Pattern-based abstraction
result = run_pattern(
    PatternRefV1(pattern_id="PAT-EXEC-ATOMIC-CREATE-001"),
    ExecutionRequestV1(...)
)

# Bad: Direct tool coupling
subprocess.run(["python", "scripts/create_file.py", ...])
```

### 1.4 Between Error Detection and Everything Else

**Requirement**: Error plugins only know about `ErrorEventV1`.

**Why**: Decouples error detection from error production.

**Example**:
```python
# Good: Contract-based error handling
def handle_error(error: ErrorEventV1):
    if error.kind == "execution_failure":
        suggest_fixes(error)

# Bad: Tightly coupled to execution internals
def handle_pytest_failure(pytest_result):  # Knows too much
    if pytest_result.exit_code == 1:
        ...
```

---

## 2. When NOT to Add Abstraction

### 2.1 Tiny Leaf Helpers

**Don't abstract**: Simple utility functions that don't cross module boundaries.

**Example**:
```python
# Fine - internal helper, no abstraction needed
def _normalize_path(p: Path) -> str:
    return str(p.resolve()).replace("\\", "/")
```

### 2.2 One-Off Scripts

**Don't abstract**: Scripts that:
- Read from stdin
- Touch a couple of files
- Are NOT called by other modules

**Example**:
```bash
# Fine - standalone script
python scripts/cleanup_temp_files.py
```

### 2.3 Internal Module Implementation

**Don't abstract**: Code inside a module where everything is tightly coupled and not used elsewhere.

**Example**:
```python
# Inside doc_id_assigner.py - all internal, no abstraction needed
def _parse_file(path):
    ...

def _extract_id(content):
    ...

def _validate_id(doc_id):
    ...
```

**Key**: At the module BOUNDARY, enforce contracts. Inside, do whatever is convenient.

---

## 3. Simple Mental Rule

**Decision Tree**:

```
Is this code called by another module, agent, or process?
├─ YES → Give it a stable abstract contract
└─ NO → Keep it concrete, internal
```

**In this stack**:

✅ **Abstract** (use contracts):
- Orchestrator ↔ executors
- Executors ↔ pattern engine
- Pattern engine ↔ DB/logs
- Business logic ↔ git/worktrees
- Business logic ↔ filesystem

❌ **Don't over-abstract**:
- Internal helpers within a single module
- One-off scripts
- Temporary/experimental code

---

## 4. Enforcement Rules

### 4.1 Module Boundary Contract

**Rule**: All cross-module calls MUST use the `*V1` contracts from `UET_SUBMODULE_IO_CONTRACTS.md`.

**Enforcement**:
- Pre-commit hooks reject arbitrary dict/string passing
- CI validates contract compliance
- Code review checklist includes contract verification

### 4.2 Public vs Internal API

**Rule**: Each shared module MUST declare:
- **Public Types**: DTOs / dict shapes it accepts/returns
- **Public Functions**: Signatures + behavior guarantees
- **Internal Functions**: Marked with `_` prefix, not for external use

**Example**:
```python
# modules/path_shared/__init__.py

# PUBLIC API - stable contract
def resolve_path(ref: RepoPathRefV1) -> ResolvedPathV1:
    """Public contract - never change signature"""
    return _internal_resolve(ref)

# INTERNAL - can change freely
def _internal_resolve(ref):
    ...
```

### 4.3 Evolution Without Breaking Changes

**Rule**: Internals can evolve freely as long as public contracts stay stable.

**Example**:
```python
# Version 1
def resolve_path(ref: RepoPathRefV1) -> ResolvedPathV1:
    # Uses simple path joining
    ...

# Version 2 - internal change, contract unchanged
def resolve_path(ref: RepoPathRefV1) -> ResolvedPathV1:
    # Now uses doc_id registry lookup
    # Contract unchanged - callers unaffected
    ...
```

---

## 5. Common Anti-Patterns

### 5.1 ❌ Passing Arbitrary Dicts Across Modules

```python
# Bad
result = executor.run({"workspace": "main", "files": [...]})

# Good
result = executor.run(ExecutionRequestV1(workspace="main", ...))
```

### 5.2 ❌ Direct Environment Calls in Business Logic

```python
# Bad
subprocess.run(["git", "status"])

# Good
status = get_workspace_status(workspace)
```

### 5.3 ❌ Over-Abstracting Internal Code

```python
# Bad - unnecessary abstraction
class PathNormalizer:
    def __init__(self):
        self.strategy = PathNormalizationStrategy()

    def normalize(self, path):
        return self.strategy.execute(path)

# Good - simple internal helper
def _normalize_path(path: str) -> str:
    return path.replace("\\", "/")
```

### 5.4 ❌ Tight Coupling to Specific Tools

```python
# Bad
if tool == "pytest":
    run_pytest(...)
elif tool == "mypy":
    run_mypy(...)

# Good
run_tool(ToolRunRequestV1(cmd=["pytest", ...]))
```

---

## 6. Template Connection

These abstraction guidelines are enforced through templates:

| Contract | Template |
|----------|----------|
| ExecutionRequestV1/ResultV1 | `TEMPLATE_EXECUTOR.py` |
| ErrorEventV1 | `TEMPLATE_ERROR_PLUGIN.py` |
| LogEventV1 | `TEMPLATE_LOGGING_CALLSITE.py` |
| GitWorkspaceRefV1/StatusV1 | `TEMPLATE_GIT_HELPER.py` |
| Public API declaration | `TEMPLATE_MODULE_PUBLIC_API.md` |

See `templates/contracts/` for complete templates.

---

## 7. Migration Strategy

### For Existing Code

1. **Identify boundaries**: Find all cross-module calls
2. **Add contracts**: Wrap in appropriate `*V1` types
3. **Update callers**: Use contract-based calls
4. **Add tests**: Verify contract compliance
5. **Mark internal**: Prefix internal helpers with `_`

### For New Code

1. **Start with template**: Use appropriate contract template
2. **Define public API**: List public types and functions
3. **Implement internals**: Freely, without over-abstraction
4. **Test boundary**: Verify contracts, not internals

---

## 8. Benefits

Following these guidelines provides:

1. **Swappable implementations**: Change internals without breaking callers
2. **Testability**: Mock contracts, not internals
3. **AI safety**: Contracts prevent AI from inventing incompatible structures
4. **Maintainability**: Clear boundaries, predictable evolution
5. **Parallelization**: Independent teams can work on different sides of contract

---

## 9. Quick Reference

**Use abstraction when**:
- Crossing module boundaries
- Calling external systems (git, DB, filesystem)
- Building reusable executors/plugins
- Enabling parallel development

**Don't abstract when**:
- Inside a single module
- One-off scripts
- Temporary/experimental code
- Simple utilities

**Always**:
- Use versioned contracts (`*V1`)
- Document public API
- Test contract compliance
- Prefix internal helpers with `_`
