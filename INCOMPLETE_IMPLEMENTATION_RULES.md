# Incomplete Implementation Detection Rules

**DOC_ID**: `DOC-RULES-INCOMPLETE-DETECTION`

## Purpose

This document defines the detection rules for the incomplete implementation scanner. It establishes what constitutes an "incomplete" or "stub" implementation versus legitimate code.

---

## Detection Categories

### A. Stub / Placeholder Code

#### Python
**Function/Method stubs**:
- Body contains only `pass`
- Body contains only `...` (Ellipsis)
- Body contains only `return None`
- Immediately raises `NotImplementedError`, `NotImplemented`, or `TODO` exception
- Only contains comment lines (e.g., `# TODO implement this`)

**Class stubs**:
- All methods match stub criteria above
- Abstract base classes with no concrete implementations in codebase
- Classes declared in `if TYPE_CHECKING:` blocks only

#### JavaScript/TypeScript
- Empty function bodies: `{}`
- Throws error: `throw new Error("Not implemented")`
- Placeholder returns: `return null;` or `return undefined;` with TODO comment
- Functions that only contain `// TODO` comments

#### General (all languages)
- Functions/classes with TODO/FIXME comments and no actual logic

---

### B. Empty or Useless Structure

**Empty directories**:
- Zero files (ignoring `.gitkeep`, `__pycache__`, etc.)
- Only contains `__init__.py` with no content (or just imports)

**Trivial files**:
- Files with ≤ 3 lines (excluding imports, docstrings)
- Files with only comments or docstrings, no executable code
- Files with only type annotations in `TYPE_CHECKING` blocks

**Configuration without implementation**:
- Entry points declared in `pyproject.toml` but module doesn't exist
- Routes/endpoints declared but handler functions are stubs
- Plugin registrations where plugin modules are missing

---

### C. Broken or Dangling References

**Import failures**:
- Imports reference non-existent modules/packages
- Relative imports that resolve to missing files

**Test references**:
- Tests import symbols that don't exist in source
- Tests call functions/methods never implemented
- Tests reference fixtures that are undefined

**Dead-end calls**:
- Function calls to undefined functions
- Method calls on objects where method is abstract/not implemented

---

## Severity Levels

### Critical
- Stub in core module (`core/`, `engine/`, `error/`)
- Missing implementation referenced in:
  - Configuration files (entry points, routes)
  - Active test files
  - Public API modules
- Abstract methods not implemented in concrete classes

### Major
- Stub in domain modules (`aim/`, `pm/`, `specifications/`)
- Empty directories in main structure
- Imported but not implemented functions

### Minor
- Stub in experimental/example code
- Empty directories in scratch/archive areas
- TODO comments with partial implementation

### Allowed
- Marked with special comment: `# INCOMPLETE_OK` or `# STUB_ALLOWED`
- In paths matching allowlist patterns:
  - `tests/fixtures/` (test data stubs)
  - `docs/examples/` (example stubs)
  - `_ARCHIVE/`, `legacy/` (archived code)
  - Files in `incomplete_allowlist.yaml`

---

## Context Scoring

**High priority paths** (multiply severity):
- `core/`, `engine/`, `error/` → ×3
- Public APIs, CLI entry points → ×2
- Referenced in tests → ×2

**Low priority paths** (reduce severity):
- `experiments/`, `scratch/` → ×0.1
- `_ARCHIVE/`, `legacy/` → ×0.01
- `docs/examples/` → ×0.5

---

## Whitelist Mechanisms

### 1. Inline Markers
Add to line or block:
```python
# INCOMPLETE_OK: Interface definition only
def process_payment(amount: float) -> bool:
    raise NotImplementedError
```

### 2. File Header Marker
```python
# INCOMPLETE_ALLOWED: Example code for documentation
```

### 3. Allowlist File
`incomplete_allowlist.yaml`:
```yaml
allowed_stubs:
  - path: "core/interfaces.py"
    reason: "Abstract base classes only"
  - path: "tests/fixtures/dummy_*.py"
    reason: "Test fixtures"
  - pattern: "docs/examples/**/*.py"
    reason: "Example/tutorial code"
```

---

## False Positive Reduction

**Not stubs**:
- Functions that only validate inputs then raise `ValueError` (logic, not stub)
- Methods that delegate to other methods (`return self._internal_method()`)
- Properties that return constants
- Functions that only log/print (legitimate minimal functions)
- Context managers with only `pass` in `__enter__`/`__exit__` (intentional no-op)

**Special cases**:
- `__init__.py` with only imports is **not** a stub (package initialization)
- Test fixtures that return simple values are **not** stubs
- Type stub files (`.pyi`) are **not** incomplete (intentional type-only)

---

## Output Format

Each finding must include:
```json
{
  "kind": "stub_function|stub_class|empty_dir|missing_reference|dangling_import",
  "path": "relative/path/to/file",
  "symbol": "function_or_class_name",
  "line": 42,
  "reason": "function_body_is_pass|raises_not_implemented|...",
  "severity": "critical|major|minor|allowed",
  "context_score": 1.5,
  "body_preview": "    pass  # TODO implement"
}
```

---

## Version

- **Version**: 1.0.0
- **Last Updated**: 2025-12-04
- **Applies To**: All Python, TypeScript, JavaScript code in repository
