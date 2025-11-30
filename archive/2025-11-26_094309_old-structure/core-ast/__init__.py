"""Core AST (Abstract Syntax Tree) Parsing

Code analysis and structure extraction using Tree-sitter.

This module provides language-agnostic AST parsing for:
- Function and class extraction
- Import analysis and dependency detection
- Code structure understanding

Supports multiple languages (Python production, JS/TS planned).

Public API:
    High-level Extractors:
        - extractors.extract_functions() - Extract function metadata
        - extractors.extract_classes() - Extract class metadata
        - extractors.extract_imports() - Extract import statements
        - extractors.extract_dependencies() - Infer file dependencies
    
    Python Parser:
        - languages.python.parse_python()
        - languages.python.extract_python_functions()
        - languages.python.extract_python_classes()
        - languages.python.extract_python_imports()
    
    Language Registry:
        - languages.LANGUAGE_PARSERS - Available parsers

Usage:
    from modules.core_ast.m010000_extractors import extract_functions, extract_dependencies
    from core.ast.languages.python import extract_python_functions
    
    # High-level API (language-agnostic)
    functions = extract_functions("src/auth.py", language="python")
    deps = extract_dependencies("src/auth.py", project_root=".")
    
    # Language-specific API
    py_functions = extract_python_functions("src/auth.py")

For details, see:
    - core/ast/README.md
    - core/ast/languages/README.md
    - core/ast/dependencies.yaml

This module supports Phase 4 AI Enhancement features:
- Repository mapping (AST + PageRank)
- Knowledge graph construction
- Semantic code understanding
"""
DOC_ID: DOC-PAT-CORE-AST-INIT-385

from modules.core_ast.m010000_extractors import (
    extract_functions,
    extract_classes,
    extract_imports,
    extract_dependencies,
)

__all__ = [
    "extractors",
    "languages",
    # High-level API
    "extract_functions",
    "extract_classes",
    "extract_imports",
    "extract_dependencies",
]

__version__ = "1.0.0"
