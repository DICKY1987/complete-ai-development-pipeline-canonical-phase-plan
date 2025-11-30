"""Tree-sitter backed AST parser with a lightweight API used in tests."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple, Union

from tree_sitter import Language, Parser, Tree
import tree_sitter_python
import tree_sitter_javascript
import tree_sitter_typescript


_LANGUAGES = {
    "python": Language(tree_sitter_python.language()),
    "javascript": Language(tree_sitter_javascript.language()),
    "typescript": Language(tree_sitter_typescript.language_typescript()),
}


class ASTParser:
    """Simple wrapper around tree-sitter parsers for multiple languages."""
# DOC_ID: DOC-PAT-CORE-AST-PARSER-487

    def __init__(self, language: str):
        if not language:
            raise ValueError("Language name is required")

        self.language_name = language.lower()
        if self.language_name not in _LANGUAGES:
            raise ValueError(f"Unsupported language: {language}")

        self.parser = Parser(_LANGUAGES[self.language_name])

    def parse_string(self, source: Union[str, bytes]) -> Tree:
        """Parse a string or bytes into a tree-sitter Tree."""
        if isinstance(source, str):
            source_bytes = source.encode("utf-8")
        elif isinstance(source, (bytes, bytearray)):
            source_bytes = bytes(source)
        else:
            raise TypeError("source must be str or bytes")

        return self.parser.parse(source_bytes)

    def parse_file(self, path: Union[str, Path]) -> Tree:
        """Parse a file from disk."""
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(str(file_path))

        data = file_path.read_bytes()
        return self.parse_string(data)

    @staticmethod
    def has_errors(tree: Tree) -> bool:
        """Return True if the parsed tree contains errors."""
        return bool(tree and tree.root_node and tree.root_node.has_error)

    @staticmethod
    def get_error_nodes(tree: Tree) -> List[Dict[str, Tuple[int, int]]]:
        """Collect error nodes with location details."""
        errors: List[Dict[str, Tuple[int, int]]] = []
        if not tree or not tree.root_node:
            return errors

        stack = [tree.root_node]
        while stack:
            node = stack.pop()
            if getattr(node, "is_missing", False) or node.type == "ERROR":
                errors.append(
                    {
                        "type": node.type,
                        "start_point": node.start_point,
                        "end_point": node.end_point,
                    }
                )
            stack.extend(node.children)
        return errors


__all__ = ["ASTParser"]
