# Specifications Tools

**Module ID**: `specifications.tools`  
**Priority**: HIGH  
**Purpose**: Tools for processing, validating, and enforcing UET specifications

## Overview

This module provides utilities that work with UET specifications: indexing, guarding (validation), patching, rendering, and resolving references.

## Tools

### 1. **Indexer** (`indexer/`)
Generates indices and catalogs from specification documents.

```python
from specifications.tools.indexer.indexer import generate_index

index = generate_index("path/to/specs/")
```

### 2. **Guard** (`guard/`)
Validates specifications against schemas and enforces contracts.

```python
from specifications.tools.guard.guard import validate_spec

result = validate_spec(spec_path, schema_path)
```

### 3. **Patcher** (`patcher/`)
Applies versioned patches to specifications safely.

```python
from specifications.tools.patcher.patcher import apply_patch

apply_patch(spec_path, patch_path)
```

### 4. **Renderer** (`renderer/`)
Renders specifications to various output formats (HTML, PDF, Markdown).

```python
from specifications.tools.renderer.renderer import render

render(spec_path, output_format="html")
```

### 5. **Resolver** (`resolver/`)
Resolves cross-references and dependencies between specifications.

```python
from specifications.tools.resolver.resolver import resolve_refs

resolved = resolve_refs(spec_path)
```

## Edit Policy

✅ **SAFE TO MODIFY** - Tool implementation code

- Add new tools as needed
- Improve existing tools
- Add tests for tools in `tests/specifications/tools/`

## Common Use Cases

### Generate Specification Index
```bash
python -m specifications.tools.indexer.indexer specifications/content/
```

### Validate All Specs
```bash
python -m specifications.tools.guard.guard validate-all
```

### Render Specs to HTML
```bash
python -m specifications.tools.renderer.renderer --format html --output docs/specs/
```

## For AI Agents

**When to use**:
- Generating specification indices
- Validating spec changes
- Rendering specs for documentation
- Resolving spec references

**Safe to modify**:
- Tool implementation code
- Add new tools
- Improve validation logic
- Add tests

## Testing

Tests are located in `tests/specifications/tools/`:

```bash
pytest tests/specifications/tools/
```

## Related Modules

- `specifications.content` - The specs these tools process
- `core.state` - Uses indexer for catalog generation
- `quality.gates` - Uses guard for validation gates

## References

- [CODEBASE_INDEX.yaml](../../CODEBASE_INDEX.yaml) - Module dependencies
- [docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md) - Tool architecture
- [tests/specifications/tools/](../../tests/specifications/tools/) - Test suite
