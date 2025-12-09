---
doc_id: DOC-GUIDE-NEW-SHARED-MODULE-TEMPLATE-098
---

# Template: Creating a New Shared Module

This template guides you through creating a new shared module that follows UET contracts.

---

## 1. Module Metadata

Fill in the basic information about your module:

- **module_id**: `mod.shared.{name}` (e.g. `mod.shared.path_resolver`)
- **purpose**: {One sentence describing what this module does}
- **category**: `shared` | `executor` | `plugin` | `helper`
- **contract_version**: `V1`

---

## 2. Define Public Types (I/O Contracts)

List all data structures this module accepts as input or returns as output.

### Example:

```python
# Link to UET_SUBMODULE_IO_CONTRACTS.md for shared contracts
# Uses: RepoPathRefV1, ResolvedPathV1

# Module-specific types
{ModuleName}RequestV1 = {
    "field1": str,      # description
    "field2": int,      # description
}

{ModuleName}ResultV1 = {
    "success": bool,
    "output": str,
    "details": dict,
}
```

**Questions to answer**:
- What data does this module accept?
- What data does this module return?
- Does it use any existing contracts from `UET_SUBMODULE_IO_CONTRACTS.md`?

---

## 3. Define Public Functions

List all functions that external modules can call.

### Template for each function:

```python
def {function_name}(param1: Type1, param2: Type2) -> ReturnType:
    """
    {One-line description}

    REQUIRED CONTRACT:
    - {Contract requirement 1}
    - {Contract requirement 2}

    Args:
        param1: {description}
        param2: {description}

    Returns:
        {description of return value}

    Raises:
        {ExceptionType}: When {condition}
    """
```

**Questions to answer**:
- What are the core operations this module provides?
- What guarantees does each function make?
- What errors can each function raise?

---

## 4. Internal Design Notes

Document implementation details that don't affect the public contract.

### File Structure

```
modules/{name}/
├── __init__.py           # Public exports only
├── {name}.py             # Main implementation
├── _helpers.py           # Internal helpers (prefix with _)
└── README.md             # Public API documentation
```

### Key Implementation Details

- {Implementation choice 1}
- {Implementation choice 2}
- {Performance considerations}
- {Caching strategy, if any}

---

## 5. Tests

### Required Test Coverage

Create tests in: `tests/modules/shared/test_{name}.py`

**Required test cases**:
- [ ] Happy path - normal successful execution
- [ ] Invalid input - verify error handling
- [ ] Edge cases - boundary conditions
- [ ] Contract compliance - verify all contracts are followed
- [ ] Integration - test with real dependencies

### Contract Validation Tests

Create: `tests/modules/shared/test_{name}_contracts.py`

```python
def test_accepts_valid_input_contract():
    """Verify function accepts valid contract input."""
    pass

def test_returns_valid_output_contract():
    """Verify function returns valid contract output."""
    pass

def test_handles_invalid_input_gracefully():
    """Verify function doesn't crash on invalid input."""
    pass
```

---

## 6. Dependencies

### This Module Requires

List contracts/modules this module depends on:

- `{ContractTypeV1}` from `{module_path}` – {why needed}
- `{AnotherContract}` from `{module_path}` – {why needed}

### This Module Provides

List contracts this module provides for others:

- `{ProvidedTypeV1}` – {description}
- `{ProvidedFunction}` – {description}

---

## 7. Documentation

Create `modules/{name}/README.md` using `TEMPLATE_MODULE_PUBLIC_API.md`.

**Required sections**:
- [ ] Purpose
- [ ] Public Types
- [ ] Public Functions
- [ ] Usage Examples
- [ ] Internal Functions (marked as off-limits)
- [ ] Testing information

---

## 8. Implementation Checklist

Before marking the module complete:

### Code
- [ ] All public functions have type hints
- [ ] All public functions have docstrings with contracts
- [ ] All internal functions prefixed with `_`
- [ ] `__init__.py` exports only public API
- [ ] No direct environment calls (subprocess, file I/O) - use abstractions

### Documentation
- [ ] Public API documented in README.md
- [ ] All contracts clearly stated
- [ ] Usage examples provided
- [ ] Dependencies listed

### Testing
- [ ] Unit tests for all public functions
- [ ] Contract validation tests
- [ ] Integration tests (if applicable)
- [ ] All tests passing

### Integration
- [ ] Added to module registry
- [ ] Contracts added to `UET_SUBMODULE_IO_CONTRACTS.md` (if new)
- [ ] Other modules updated to use this (if replacing old code)

---

## 9. Example: Creating `path_resolver` Module

### Step 1: Metadata

- **module_id**: `mod.shared.path_resolver`
- **purpose**: Resolves logical path references to absolute filesystem paths
- **category**: `shared`

### Step 2: Contracts

Uses: `RepoPathRefV1`, `ResolvedPathV1`

### Step 3: Public Functions

```python
def resolve_path(ref: RepoPathRefV1) -> ResolvedPathV1:
    """Resolve logical path reference to absolute path."""
    pass

def resolve_doc_id(doc_id: str) -> ResolvedPathV1:
    """Resolve doc_id to absolute path via registry."""
    pass
```

### Step 4: Internal Design

- Uses doc_id registry for lookups
- Caches workspace roots for performance
- Never creates directories

### Step 5: Tests

- `tests/modules/shared/test_path_resolver.py`
- `tests/modules/shared/test_path_resolver_contracts.py`

---

## 10. Quick Start

1. Copy this template to `docs/planning/NEW_MODULE_{name}.md`
2. Fill in sections 1-3 (metadata, contracts, functions)
3. Review with team/AI
4. Implement following section 8 checklist
5. Delete planning doc when module is complete

---

## Notes

- **Keep it simple**: Start with minimal functionality, extend later
- **Contract first**: Define contracts before implementation
- **Test early**: Write tests alongside code, not after
- **Document as you go**: Update docs with each function
- **Use templates**: All the contract templates are in `templates/contracts/`
