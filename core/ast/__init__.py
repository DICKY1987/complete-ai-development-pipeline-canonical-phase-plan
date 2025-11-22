"""
AST (Abstract Syntax Tree) parsing module.

Provides Tree-sitter-based parsing for multiple languages with
signature extraction, import analysis, and structural understanding.

This module supports Phase 4 AI Enhancement features:
- Repository mapping (AST + PageRank)
- Knowledge graph construction
- Semantic code understanding
"""

from core.ast.parser import ASTParser
from core.ast.extractors import (
    BaseExtractor,
    FunctionInfo,
    ClassInfo,
    ImportInfo,
)

__all__ = [
    "ASTParser",
    "BaseExtractor",
    "FunctionInfo",
    "ClassInfo",
    "ImportInfo",
]

__version__ = "0.1.0"
