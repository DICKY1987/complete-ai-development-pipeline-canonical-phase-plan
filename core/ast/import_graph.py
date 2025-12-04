"""
Build import dependency graph for a codebase.

Analyzes import relationships to understand module dependencies.
"""

# DOC_ID: DOC-CORE-AST-IMPORT-GRAPH-204

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set

from .languages.python import PythonExtractor
from .parser import ASTParser


@dataclass
class ImportEdge:
    """Represents an import dependency."""

    from_module: str
    to_module: str
    imported_names: List[str]
    is_from_import: bool


class ImportGraph:
    """Build and analyze import dependency graph."""

    def __init__(self, root_path: Path):
        """
        Initialize import graph.

        Args:
            root_path: Root directory of codebase
        """
        self.root_path = root_path
        self.parser = ASTParser()
        self.edges: List[ImportEdge] = []
        self.adjacency: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_adjacency: Dict[str, Set[str]] = defaultdict(set)

    def build_graph(self, include_patterns: Optional[List[str]] = None):
        """
        Build import graph for codebase.

        Args:
            include_patterns: Optional list of glob patterns to include
        """
        # Find all Python files
        if include_patterns:
            py_files = []
            for pattern in include_patterns:
                py_files.extend(self.root_path.rglob(pattern))
        else:
            py_files = list(self.root_path.rglob("*.py"))

        # Extract imports from each file
        for py_file in py_files:
            try:
                self._process_file(py_file)
            except Exception as e:
                print(f"Warning: Could not process {py_file}: {e}")
                continue

    def _process_file(self, file_path: Path):
        """Process a single file and extract imports."""
        # Parse file
        tree = self.parser.parse_file(file_path)
        if not tree:
            return

        # Get module name from file path
        try:
            rel_path = file_path.relative_to(self.root_path)
            module_name = (
                str(rel_path.with_suffix("")).replace("\\", ".").replace("/", ".")
            )
            if module_name.endswith(".__init__"):
                module_name = module_name[:-9]  # Remove .__init__
        except ValueError:
            # File is outside root path
            return

        # Extract imports
        with open(file_path, "rb") as f:
            source = f.read()

        extractor = PythonExtractor(tree, source)
        imports = extractor.extract_imports()

        # Add edges to graph
        for imp in imports:
            # Normalize import module name
            to_module = imp.module

            # Add edge
            edge = ImportEdge(
                from_module=module_name,
                to_module=to_module,
                imported_names=imp.names,
                is_from_import=imp.is_from_import,
            )
            self.edges.append(edge)

            # Update adjacency
            self.adjacency[module_name].add(to_module)
            self.reverse_adjacency[to_module].add(module_name)

    def get_dependencies(self, module: str) -> Set[str]:
        """
        Get all modules that the given module imports.

        Args:
            module: Module name

        Returns:
            Set of module names
        """
        return self.adjacency.get(module, set())

    def get_dependents(self, module: str) -> Set[str]:
        """
        Get all modules that import the given module.

        Args:
            module: Module name

        Returns:
            Set of module names
        """
        return self.reverse_adjacency.get(module, set())

    def get_all_modules(self) -> Set[str]:
        """Get all modules in the graph."""
        modules = set(self.adjacency.keys())
        modules.update(self.reverse_adjacency.keys())
        return modules

    def has_circular_dependency(self) -> bool:
        """Check if graph has circular dependencies."""
        visited = set()
        rec_stack = set()

        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)

            for neighbor in self.adjacency.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        for module in self.get_all_modules():
            if module not in visited:
                if has_cycle(module):
                    return True

        return False

    def find_circular_dependencies(self) -> List[List[str]]:
        """
        Find all circular dependency chains.

        Returns:
            List of circular dependency chains
        """
        cycles = []
        visited = set()
        rec_stack = []

        def find_cycles(node):
            visited.add(node)
            rec_stack.append(node)

            for neighbor in self.adjacency.get(node, []):
                if neighbor not in visited:
                    find_cycles(neighbor)
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = rec_stack.index(neighbor)
                    cycle = rec_stack[cycle_start:] + [neighbor]
                    cycles.append(cycle)

            rec_stack.pop()

        for module in self.get_all_modules():
            if module not in visited:
                find_cycles(module)

        return cycles

    def to_dict(self) -> Dict:
        """
        Export graph to dictionary format.

        Returns:
            Dict representation of graph
        """
        return {
            "modules": list(self.get_all_modules()),
            "edges": [
                {
                    "from": edge.from_module,
                    "to": edge.to_module,
                    "names": edge.imported_names,
                    "is_from_import": edge.is_from_import,
                }
                for edge in self.edges
            ],
            "adjacency": {
                module: list(deps) for module, deps in self.adjacency.items()
            },
        }


__all__ = ["ImportGraph", "ImportEdge"]
