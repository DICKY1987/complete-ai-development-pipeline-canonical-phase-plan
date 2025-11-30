"""Python-specific AST extractor using the stdlib ast module."""
from __future__ import annotations

import ast
from typing import List

from modules.core_ast.m010000_extractors import (
    BaseExtractor,
    ClassInfo,
    FunctionInfo,
    ImportInfo,
)


def _unparse(node: ast.AST) -> str:
    """Safely render an AST node to source."""
# DOC_ID: DOC-PAT-LANGUAGES-PYTHON-609
    try:
        return ast.unparse(node)  # type: ignore[attr-defined]
    except Exception:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return f"{_unparse(node.value)}.{node.attr}"
        return ""


class PythonExtractor(BaseExtractor):
    """Extract functions, classes, and imports from Python code."""

    def _load_ast(self) -> ast.AST:
        source_text = (
            self.source.decode("utf-8") if isinstance(self.source, (bytes, bytearray)) else str(self.source)
        )
        return ast.parse(source_text)

    def extract_functions(self) -> List[FunctionInfo]:
        tree = self._load_ast()
        functions: List[FunctionInfo] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                params = [arg.arg for arg in node.args.args]
                docstring = ast.get_docstring(node)
                decorators = [_unparse(d) for d in node.decorator_list]
                functions.append(
                    FunctionInfo(
                        name=node.name,
                        start_line=getattr(node, "lineno", 0),
                        end_line=getattr(node, "end_lineno", getattr(node, "lineno", 0)),
                        params=params,
                        return_type=None,
                        docstring=docstring,
                        decorators=decorators,
                        is_async=isinstance(node, ast.AsyncFunctionDef),
                    )
                )
        return functions

    def extract_classes(self) -> List[ClassInfo]:
        tree = self._load_ast()
        classes: List[ClassInfo] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                bases = [_unparse(base) for base in node.bases]
                docstring = ast.get_docstring(node)
                decorators = [_unparse(d) for d in node.decorator_list]
                classes.append(
                    ClassInfo(
                        name=node.name,
                        start_line=getattr(node, "lineno", 0),
                        end_line=getattr(node, "end_lineno", getattr(node, "lineno", 0)),
                        bases=bases,
                        methods=methods,
                        docstring=docstring,
                        decorators=decorators,
                    )
                )
        return classes

    def extract_imports(self) -> List[ImportInfo]:
        tree = self._load_ast()
        imports: List[ImportInfo] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(
                        ImportInfo(
                            module=alias.name,
                            names=[alias.name],
                            alias=alias.asname,
                            is_from_import=False,
                            start_line=getattr(node, "lineno", 0),
                        )
                    )
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module or ""
                for alias in node.names:
                    imports.append(
                        ImportInfo(
                            module=module_name,
                            names=[alias.name],
                            alias=alias.asname,
                            is_from_import=True,
                            start_line=getattr(node, "lineno", 0),
                        )
                    )
        return imports


__all__ = ["PythonExtractor"]
