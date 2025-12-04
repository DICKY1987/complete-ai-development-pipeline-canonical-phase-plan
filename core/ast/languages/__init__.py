"""
Language-specific AST extractors.

Each module provides specialized extraction for a programming language.
"""

# DOC_ID: DOC-CORE-AST-LANGUAGES-INIT-201

from .python import PythonExtractor

__all__ = ["PythonExtractor"]
