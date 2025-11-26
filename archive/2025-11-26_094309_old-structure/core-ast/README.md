# Core AST Utilities

> **Module**: `core.ast`  
> **Purpose**: Abstract Syntax Tree parsing and code analysis  
> **Layer**: Utilities/Analysis  
> **Status**: Production

---

## Overview

The `core/ast/` module provides AST parsing and code analysis utilities for multiple programming languages. It enables:

- **Language-agnostic AST parsing** - Unified interface across Python, JavaScript, TypeScript
- **Code structure extraction** - Extract functions, classes, imports, dependencies
- **Scope analysis** - Identify symbol usage and references
- **Dependency detection** - Infer file dependencies from imports

This module uses **Tree-sitter** for fast, incremental parsing and is designed to support workstream validation and automated planning.

---

## Directory Structure

```
core/ast/
├── extractors.py         # High-level extraction API
├── languages/            # Language-specific parsers
│   ├── __init__.py      # Language registry
│   └── python.py        # Python AST parser
└── README.md            # This file
```

---

## Key Components

### Extractors (`extractors.py`)

High-level API for extracting code elements from source files.

**Core Functions**:

```python
from core.ast.extractors import extract_functions, extract_imports, extract_dependencies

# Extract function definitions
functions = extract_functions("src/auth.py", language="python")
# Returns: [{"name": "authenticate", "line": 10, "signature": "def authenticate(user, password)"}]

# Extract imports
imports = extract_imports("src/auth.py", language="python")
# Returns: [{"module": "hashlib", "names": ["sha256"], "line": 1}]

# Infer file dependencies
deps = extract_dependencies("src/auth.py", project_root=".")
# Returns: ["src/database.py", "src/config.py"]
```

**Use Cases**:
- Validate workstream file scopes
- Auto-detect dependencies for planning
- Generate file relationship graphs
- Support automated decomposition

---

### Language Parsers (`languages/`)

Language-specific AST parsing implementations using Tree-sitter.

#### Python Parser (`languages/python.py`)

```python
from core.ast.languages.python import (
    parse_python,
    extract_python_functions,
    extract_python_classes,
    extract_python_imports
)

# Parse Python source
tree = parse_python("def hello(): pass")

# Extract functions
functions = extract_python_functions("src/auth.py")
# Returns: [
#     {
#         "name": "authenticate",
#         "line_start": 10,
#         "line_end": 25,
#         "params": ["user", "password"],
#         "returns": "bool",
#         "docstring": "Authenticate user credentials."
#     }
# ]

# Extract classes
classes = extract_python_classes("src/models.py")

# Extract imports with detailed metadata
imports = extract_python_imports("src/auth.py")
# Returns: [
#     {"type": "import", "module": "hashlib", "line": 1},
#     {"type": "from_import", "module": "typing", "names": ["Optional", "Dict"], "line": 2}
# ]
```

**Supported Python Features**:
- Function definitions (regular and async)
- Class definitions with methods
- Import statements (import, from...import)
- Docstrings and type hints
- Decorators

#### Adding New Languages

To add support for a new language:

1. Install Tree-sitter grammar:
   ```bash
   pip install tree-sitter-{language}
   ```

2. Create parser module:
   ```python
   # core/ast/languages/javascript.py
   from tree_sitter import Language, Parser
   
   def parse_javascript(source_code: str):
       # Implementation
       pass
   ```

3. Register in `languages/__init__.py`:
   ```python
   from core.ast.languages.python import parse_python
   from core.ast.languages.javascript import parse_javascript
   
   LANGUAGE_PARSERS = {
       "python": parse_python,
       "javascript": parse_javascript,
   }
   ```

---

## Architecture

### Design Principles

1. **Language Independence** - Unified API regardless of source language
2. **Incremental Parsing** - Tree-sitter enables fast re-parsing on edits
3. **Minimal Dependencies** - Only depends on Tree-sitter and language grammars
4. **No Side Effects** - Pure functions, no file I/O in parsers

### Integration Points

- **`core.planning`** - Auto-detect dependencies for workstream planning
- **`core.state.bundles`** - Validate file scopes and detect conflicts
- **`specifications.tools`** - Analyze spec changes and infer impacts
- **`error.plugins`** - Provide AST context for error detection

---

## Usage Patterns

### Validate Workstream File Scope

```python
from core.ast.extractors import extract_dependencies
from core.state.bundles import WorkstreamBundle

def validate_file_scope(bundle: WorkstreamBundle, project_root: str) -> bool:
    """
    Validate that bundle's file scope includes all dependencies.
    """
    all_files = set(bundle.files_scope)
    
    for file_path in bundle.files_scope:
        deps = extract_dependencies(file_path, project_root)
        all_files.update(deps)
    
    missing = all_files - set(bundle.files_scope)
    if missing:
        print(f"Warning: Missing dependencies: {missing}")
        return False
    
    return True
```

### Auto-Detect Module Imports

```python
from core.ast.languages.python import extract_python_imports

def get_third_party_dependencies(file_path: str) -> set[str]:
    """
    Extract third-party package names from imports.
    """
    imports = extract_python_imports(file_path)
    
    # Filter standard library imports
    stdlib = {"os", "sys", "pathlib", "typing", "collections"}
    third_party = set()
    
    for imp in imports:
        module = imp["module"].split(".")[0]
        if module not in stdlib:
            third_party.add(module)
    
    return third_party
```

### Generate Dependency Graph

```python
from core.ast.extractors import extract_dependencies
from pathlib import Path

def build_dependency_graph(project_root: str) -> dict[str, list[str]]:
    """
    Build project-wide dependency graph.
    """
    graph = {}
    
    for py_file in Path(project_root).rglob("*.py"):
        deps = extract_dependencies(str(py_file), project_root)
        graph[str(py_file)] = deps
    
    return graph
```

---

## Configuration

### Environment Variables

- **`TREE_SITTER_LIB_PATH`** - Override Tree-sitter library location (optional)

### Dependencies

Required packages (see `requirements.txt`):
- `tree-sitter>=0.20.0`
- `tree-sitter-python>=0.20.0`
- `tree-sitter-javascript>=0.20.0` (optional)
- `tree-sitter-typescript>=0.20.0` (optional)

---

## Testing

Tests are located in `tests/ast/`:

```bash
# Run AST tests
pytest tests/ast/ -v

# Test Python parser
pytest tests/ast/test_python_parser.py -v

# Test extractors
pytest tests/ast/test_extractors.py -v
```

---

## Performance

- **Parsing Speed**: ~1000 files/sec for Python (depends on file size)
- **Memory**: Low overhead due to incremental parsing
- **Caching**: Parse trees are not cached; re-parse on each call

**Optimization Tips**:
- Parse files once and cache results if analyzing multiple times
- Use `extract_dependencies()` instead of manual import parsing
- Consider parallel processing for large codebases

---

## Roadmap

### Current (Production)
- ✅ Python AST parsing
- ✅ Function/class extraction
- ✅ Import analysis
- ✅ Dependency detection

### Planned
- 🔜 JavaScript/TypeScript support
- 🔜 Go parser
- 🔜 Cross-language call graph analysis
- 🔜 Symbol resolution and type inference
- 🔜 AST-based diff generation

---

## Best Practices

1. **Always specify language explicitly** - Don't rely on file extension inference
2. **Handle parse errors gracefully** - Invalid syntax should not crash analysis
3. **Use extractors for high-level tasks** - Avoid raw Tree-sitter API when possible
4. **Cache parse results** - If analyzing same file multiple times
5. **Validate dependencies** - AST analysis may miss dynamic imports

---

## Related Documentation

- **Language Parsers**: `core/ast/languages/README.md` - Language-specific details
- **Tree-sitter**: https://tree-sitter.github.io/tree-sitter/ - Official docs
- **Parent Module**: `core/README.md` - Core pipeline overview
- **Planning**: `core/planning/README.md` - Automated planning integration

---

## Troubleshooting

### "No module named tree_sitter"

Install Tree-sitter:
```bash
pip install tree-sitter tree-sitter-python
```

### "Language grammar not found"

Install language-specific grammar:
```bash
pip install tree-sitter-python  # For Python
pip install tree-sitter-javascript  # For JavaScript
```

### Parse errors on valid code

Check Tree-sitter grammar version compatibility. Update to latest:
```bash
pip install --upgrade tree-sitter tree-sitter-python
```

---

**For AI Tools**: This module enables static code analysis without executing code. Use it to validate file scopes, detect dependencies, and support automated planning decisions.
