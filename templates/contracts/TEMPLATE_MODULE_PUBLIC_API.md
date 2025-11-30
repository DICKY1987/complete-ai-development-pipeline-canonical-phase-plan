---
doc_id: DOC-GUIDE-TEMPLATE-MODULE-PUBLIC-API-1835
---

# {Module Name} – Public API (V1)

**Module ID**: `{module_id}`  
**Status**: Active  
**Last Updated**: {YYYY-MM-DD}

---

## Purpose

{Short description of what this module does - 1-2 sentences}

---

## Public Types (I/O Contracts)

### {TypeName}V1

{Description of this type}

```python
{TypeName}V1 = {
    "field1": str,      # description
    "field2": int,      # description
    "field3": bool,     # description
}
```

**Contract**:
- {Constraint 1}
- {Constraint 2}

---

## Public Functions

### `{function_name}(param1: Type1, param2: Type2) -> ReturnType`

{Brief description of what this function does}

**Inputs**:
- `param1` (Type1): {description}
- `param2` (Type2): {description}

**Outputs**:
- Returns `ReturnType`: {description}

**Errors**:
- Raises `{ErrorType}` when {condition}
- Returns `None` when {condition} (if applicable)

**Contract Guarantees**:
- {Guarantee 1}
- {Guarantee 2}

**Example**:
```python
from {module_path} import {function_name}

result = {function_name}(param1="value", param2=42)
# result is guaranteed to be...
```

---

## Internal Functions (Not for External Callers)

These functions are implementation details and may change without notice:

- `_internal_helper1()` – {brief description}
- `_internal_helper2()` – {brief description}

**Rule**: External callers MUST NOT import or use functions prefixed with `_`.

---

## Dependencies

### Required Contracts
This module requires the following contracts from other modules:

- `{ContractTypeV1}` from `{module_path}` – {why needed}

### Provided Contracts
This module provides these contracts for others to use:

- `{ProvidedTypeV1}` – {description}

---

## Usage Examples

### Example 1: {Common Use Case}

```python
from {module_path} import {function_name}, {TypeNameV1}

# Set up input
input_data: {TypeNameV1} = {
    "field1": "value",
    "field2": 123,
}

# Call public function
result = {function_name}(input_data)

# Use result
if result.success:
    print(f"Success: {result.output}")
```

### Example 2: {Another Use Case}

```python
# TODO: Add second example
```

---

## Testing

### Test Coverage
- Unit tests: `tests/{module_path}/test_{module_name}.py`
- Integration tests: `tests/integration/test_{module_name}_integration.py`

### Contract Validation
All public functions are validated against their contracts in:
- `tests/{module_path}/test_{module_name}_contracts.py`

---

## Version History

### V1 (Current)
- **Released**: {YYYY-MM-DD}
- **Changes**: Initial version

---

## Extension Guidelines

To extend this module:

1. **Adding new public function**: Update this doc first, then implement
2. **Adding new type**: Create `{Type}V2` and document migration path
3. **Breaking changes**: MUST create new version (V2), support both during transition

**Never** modify existing contracts in-place.

---

## Migration Notes

{Leave empty for V1, fill in when creating V2+}
