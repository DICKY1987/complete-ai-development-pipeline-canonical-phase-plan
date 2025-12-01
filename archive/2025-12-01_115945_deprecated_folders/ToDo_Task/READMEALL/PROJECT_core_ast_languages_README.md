---
doc_id: DOC-GUIDE-PROJECT-CORE-AST-LANGUAGES-README-1576
---

# AST Language Parsers

> **Module**: `core.ast.languages`  
> **Purpose**: Language-specific AST parsing implementations  
> **Layer**: Utilities/Analysis  
> **Status**: Production (Python), Planned (JavaScript, TypeScript, Go)

---

## Overview

This directory contains language-specific AST parsers built on **Tree-sitter**. Each parser provides:

- **Syntax tree parsing** - Convert source code to traversable AST
- **Element extraction** - Functions, classes, imports, variables
- **Metadata collection** - Line numbers, signatures, docstrings
- **Error handling** - Graceful degradation on parse errors

All parsers implement a common interface for consistency.

---

## Available Parsers

### Python (`python.py`)

**Status**: ✅ Production  
**Grammar**: `tree-sitter-python>=0.20.0`

#### Functions

```python
from core.ast.languages.python import (
    parse_python,
    extract_python_functions,
    extract_python_classes,
    extract_python_imports,
    extract_python_variables
)
```

#### Usage Examples

**Parse Python Source**:
```python
from core.ast.languages.python import parse_python

source_code = """
def authenticate(user: str, password: str) -> bool:
    '''Verify user credentials.'''
    return check_password(user, password)
"""

tree = parse_python(source_code)
# Returns: Tree-sitter AST object
```

**Extract Functions**:
```python
from core.ast.languages.python import extract_python_functions

functions = extract_python_functions("src/auth.py")
# Returns: [
#     {
#         "name": "authenticate",
#         "line_start": 2,
#         "line_end": 4,
#         "params": [
#             {"name": "user", "type": "str"},
#             {"name": "password", "type": "str"}
#         ],
#         "return_type": "bool",
#         "docstring": "Verify user credentials.",
#         "is_async": False,
#         "decorators": []
#     }
# ]
```

**Extract Classes**:
```python
from core.ast.languages.python import extract_python_classes

classes = extract_python_classes("src/models.py")
# Returns: [
#     {
#         "name": "User",
#         "line_start": 10,
#         "line_end": 25,
#         "bases": ["BaseModel"],
#         "methods": [
#             {"name": "__init__", "line": 11},
#             {"name": "authenticate", "line": 15}
#         ],
#         "attributes": ["username", "email"],
#         "docstring": "User model class."
#     }
# ]
```

**Extract Imports**:
```python
from core.ast.languages.python import extract_python_imports

imports = extract_python_imports("src/auth.py")
# Returns: [
#     {"type": "import", "module": "hashlib", "alias": None, "line": 1},
#     {
#         "type": "from_import",
#         "module": "typing",
#         "names": [
#             {"name": "Optional", "alias": None},
#             {"name": "Dict", "alias": None}
#         ],
#         "line": 2
#     }
# ]
```

#### Supported Python Features

- ✅ Function definitions (regular and async)
- ✅ Class definitions with inheritance
- ✅ Import statements (import, from...import, as)
- ✅ Docstrings (module, class, function)
- ✅ Type hints (parameters, returns, variables)
- ✅ Decorators
- ✅ Variable assignments
- ✅ Lambda functions
- 🔜 Comprehensions
- 🔜 Context managers

---

### JavaScript (Planned)

**Status**: 🔜 Planned  
**Grammar**: `tree-sitter-javascript`

#### Planned Functions

```python
from core.ast.languages.javascript import (
    parse_javascript,
    extract_js_functions,
    extract_js_classes,
    extract_js_imports  # ES6 modules
)
```

#### Example Usage (Future)

```python
functions = extract_js_functions("src/api.js")
# Will return: [
#     {
#         "name": "authenticate",
#         "type": "arrow_function",
#         "params": ["user", "password"],
#         "is_async": True,
#         "line": 10
#     }
# ]
```

---

### TypeScript (Planned)

**Status**: 🔜 Planned  
**Grammar**: `tree-sitter-typescript`

Similar to JavaScript parser with additional type information extraction.

---

### Go (Planned)

**Status**: 🔜 Future  
**Grammar**: `tree-sitter-go`

---

## Parser Interface Specification

All language parsers should implement this interface for consistency:

### Core Functions

```python
def parse_{language}(source_code: str) -> Tree:
    """
    Parse source code into AST.
    
    Args:
        source_code: Source code string
    
    Returns:
        Tree-sitter Tree object
    
    Raises:
        ParseError: If source code has fatal syntax errors
    """
    pass

def extract_{language}_functions(file_path: str) -> list[dict]:
    """
    Extract function definitions.
    
    Returns:
        List of function metadata dictionaries with keys:
        - name: str
        - line_start: int
        - line_end: int
        - params: list[dict]  # [{"name": str, "type": str?}]
        - return_type: str?
        - docstring: str?
        - is_async: bool
        - decorators: list[str]
    """
    pass

def extract_{language}_classes(file_path: str) -> list[dict]:
    """
    Extract class definitions.
    
    Returns:
        List of class metadata dictionaries with keys:
        - name: str
        - line_start: int
        - line_end: int
        - bases: list[str]  # Base classes
        - methods: list[dict]
        - attributes: list[str]
        - docstring: str?
    """
    pass

def extract_{language}_imports(file_path: str) -> list[dict]:
    """
    Extract import statements.
    
    Returns:
        List of import metadata dictionaries with keys:
        - type: str  # "import" | "from_import" | "require" | etc.
        - module: str
        - names: list[dict]?  # For from_import: [{"name": str, "alias": str?}]
        - alias: str?
        - line: int
    """
    pass
```

---

## Implementation Guidelines

### Adding a New Language Parser

1. **Install Tree-sitter Grammar**:
   ```bash
   pip install tree-sitter-{language}
   ```

2. **Create Parser Module**:
   ```python
   # core/ast/languages/{language}.py
   
   from tree_sitter import Language, Parser
   import tree_sitter_{language}
   
   # Initialize parser
   LANGUAGE = Language(tree_sitter_{language}.language())
   
   def parse_{language}(source_code: str):
       parser = Parser(LANGUAGE)
       tree = parser.parse(bytes(source_code, "utf8"))
       return tree
   
   def extract_{language}_functions(file_path: str) -> list[dict]:
       # Implementation
       pass
   ```

3. **Register in `__init__.py`**:
   ```python
   from core.ast.languages.python import parse_python
   from core.ast.languages.{language} import parse_{language}
   
   LANGUAGE_PARSERS = {
       "python": parse_python,
       "{language}": parse_{language},
   }
   ```

4. **Add Tests**:
   ```bash
   # tests/ast/test_{language}_parser.py
   pytest tests/ast/test_{language}_parser.py -v
   ```

### Best Practices

1. **Handle Parse Errors Gracefully**:
   ```python
   def parse_python(source_code: str):
       parser = Parser(LANGUAGE)
       tree = parser.parse(bytes(source_code, "utf8"))
       
       if tree.root_node.has_error:
           # Log error but don't crash
           logger.warning(f"Parse error in source: {source_code[:50]}...")
       
       return tree
   ```

2. **Use Tree-sitter Queries**:
   ```python
   # Efficient extraction using queries
   FUNCTION_QUERY = LANGUAGE.query("""
       (function_definition
         name: (identifier) @func_name
         parameters: (parameters) @params
         body: (block) @body)
   """)
   
   def extract_python_functions(source):
       tree = parse_python(source)
       matches = FUNCTION_QUERY.matches(tree.root_node)
       # Process matches...
   ```

3. **Cache Parser Instances**:
   ```python
   _parser_cache = {}
   
   def get_parser(language: str) -> Parser:
       if language not in _parser_cache:
           _parser_cache[language] = Parser(LANGUAGE_MAP[language])
       return _parser_cache[language]
   ```

4. **Provide Fallbacks**:
   ```python
   def extract_python_functions(file_path: str) -> list[dict]:
       try:
           # Try AST parsing
           return _extract_via_ast(file_path)
       except ParseError:
           # Fallback to regex-based extraction
           return _extract_via_regex(file_path)
   ```

---

## Testing

Tests for language parsers are in `tests/ast/`:

```bash
# Test all parsers
pytest tests/ast/ -v

# Test specific language
pytest tests/ast/test_python_parser.py -v

# Test with coverage
pytest tests/ast/ --cov=core.ast.languages
```

### Test Structure

Each parser should have:
- Unit tests for extraction functions
- Integration tests with real files
- Error handling tests
- Performance benchmarks

Example test:
```python
# tests/ast/test_python_parser.py

def test_extract_functions():
    source = """
    def hello(name: str) -> str:
        return f"Hello, {name}"
    """
    
    functions = extract_python_functions(source)
    
    assert len(functions) == 1
    assert functions[0]["name"] == "hello"
    assert functions[0]["return_type"] == "str"
    assert len(functions[0]["params"]) == 1
```

---

## Dependencies

### Required Packages

```txt
tree-sitter>=0.20.0
tree-sitter-python>=0.20.0
```

### Optional Packages (for additional languages)

```txt
tree-sitter-javascript>=0.20.0
tree-sitter-typescript>=0.20.0
tree-sitter-go>=0.20.0
```

---

## Performance Considerations

- **Parsing Speed**: Tree-sitter is very fast (~100K lines/sec)
- **Memory Usage**: Minimal for individual files
- **Caching**: Consider caching parse results for frequently analyzed files
- **Parallel Processing**: Safe to parse multiple files concurrently

**Benchmark** (typical laptop):
```
Parse 1000 Python files: ~1.2 seconds
Extract functions from 1000 files: ~1.8 seconds
```

---

## Related Documentation

- **Parent Module**: `core/ast/README.md` - AST utilities overview
- **Extractors**: `core/ast/extractors.py` - High-level API
- **Tree-sitter**: https://tree-sitter.github.io/ - Official documentation
- **Grammar Specs**: https://github.com/tree-sitter - Language grammars

---

## Troubleshooting

### Tree-sitter Installation Issues

If installation fails:
```bash
# Install build dependencies
pip install setuptools wheel

# Install with pre-built wheels
pip install tree-sitter --prefer-binary
```

### Grammar Not Found

Ensure language grammar is installed:
```bash
pip list | grep tree-sitter
# Should show tree-sitter-python, etc.
```

### Parse Errors on Valid Code

Check Tree-sitter grammar version:
```bash
pip show tree-sitter-python
# Version should be >=0.20.0
```

Update if needed:
```bash
pip install --upgrade tree-sitter-python
```

---

**For AI Tools**: These parsers enable deep code understanding without execution. Use them to validate file scopes, infer dependencies, and support intelligent planning decisions.
