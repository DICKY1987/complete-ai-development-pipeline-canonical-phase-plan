"""
Extract function and class signatures from source files.

Provides signature-only extraction (no implementation details).
"""

# DOC_ID: DOC-CORE-AST-SIGNATURE-EXTRACTOR-203

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional

from .languages.python import PythonExtractor
from .parser import ASTParser


@dataclass
class Signature:
    """Represents a function or method signature."""

    name: str
    params: List[str]
    return_type: Optional[str] = None
    is_async: bool = False
    decorators: List[str] = None

    def __post_init__(self):
        if self.decorators is None:
            self.decorators = []

    def to_string(self) -> str:
        """Format signature as string."""
        decorators_str = (
            "\n".join(f"@{d}" for d in self.decorators) + "\n"
            if self.decorators
            else ""
        )
        async_str = "async " if self.is_async else ""
        params_str = ", ".join(self.params)
        return_str = f" -> {self.return_type}" if self.return_type else ""
        return f"{decorators_str}{async_str}def {self.name}({params_str}){return_str}"


@dataclass
class ClassSignature:
    """Represents a class signature."""

    name: str
    bases: List[str]
    methods: List[str]
    decorators: List[str] = None

    def __post_init__(self):
        if self.decorators is None:
            self.decorators = []

    def to_string(self) -> str:
        """Format class signature as string."""
        decorators_str = (
            "\n".join(f"@{d}" for d in self.decorators) + "\n"
            if self.decorators
            else ""
        )
        bases_str = f"({', '.join(self.bases)})" if self.bases else ""
        return f"{decorators_str}class {self.name}{bases_str}"


class SignatureExtractor:
    """Extract signatures from source files without implementation details."""

    def __init__(self):
        """Initialize signature extractor."""
        self.parser = ASTParser()

    def extract_file_signatures(self, file_path: Path) -> Dict[str, any]:
        """
        Extract all signatures from a file.

        Args:
            file_path: Path to source file

        Returns:
            Dict with 'functions' and 'classes' signatures
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Parse file
        tree = self.parser.parse_file(file_path)
        if not tree:
            return {"functions": [], "classes": []}

        # Extract based on language
        language = self.parser.current_language
        if language == "python":
            return self._extract_python_signatures(tree, file_path)
        else:
            # For now, only Python is supported
            return {"functions": [], "classes": []}

    def _extract_python_signatures(self, tree, file_path: Path) -> Dict[str, any]:
        """Extract signatures from Python file."""
        with open(file_path, "rb") as f:
            source = f.read()

        extractor = PythonExtractor(tree, source)

        # Extract functions
        func_infos = extractor.extract_functions()
        functions = [
            Signature(
                name=f.name,
                params=f.params,
                return_type=f.return_type,
                is_async=f.is_async,
                decorators=f.decorators,
            )
            for f in func_infos
        ]

        # Extract classes
        class_infos = extractor.extract_classes()
        classes = [
            ClassSignature(
                name=c.name, bases=c.bases, methods=c.methods, decorators=c.decorators
            )
            for c in class_infos
        ]

        return {
            "functions": [asdict(f) for f in functions],
            "classes": [asdict(c) for c in classes],
        }

    def extract_module_signatures(self, module_path: Path) -> Dict[str, Dict]:
        """
        Extract signatures from all files in a module/directory.

        Args:
            module_path: Path to module directory

        Returns:
            Dict mapping file paths to signatures
        """
        signatures = {}

        # Find all Python files
        if module_path.is_dir():
            py_files = list(module_path.rglob("*.py"))
        else:
            py_files = [module_path]

        for py_file in py_files:
            try:
                file_sigs = self.extract_file_signatures(py_file)
                # Use relative path as key
                rel_path = str(
                    py_file.relative_to(module_path.parent)
                    if module_path.is_dir()
                    else py_file.name
                )
                signatures[rel_path] = file_sigs
            except Exception as e:
                # Skip files that can't be parsed
                print(f"Warning: Could not extract signatures from {py_file}: {e}")
                continue

        return signatures


__all__ = ["SignatureExtractor", "Signature", "ClassSignature"]
