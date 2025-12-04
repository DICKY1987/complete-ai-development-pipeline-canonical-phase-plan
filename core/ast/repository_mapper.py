"""
Generate repository map with signatures and structure.

Creates a comprehensive map of the codebase showing all modules, functions, and classes.
"""

# DOC_ID: DOC-CORE-AST-REPOSITORY-MAPPER-205

import time
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from .import_graph import ImportGraph
from .signature_extractor import SignatureExtractor


class RepositoryMapper:
    """Generate comprehensive repository map."""

    def __init__(self, root_path: Path):
        """
        Initialize repository mapper.

        Args:
            root_path: Root directory of repository
        """
        self.root_path = Path(root_path)
        self.signature_extractor = SignatureExtractor()
        self.import_graph = ImportGraph(self.root_path)

    def generate_map(
        self,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
    ) -> Dict:
        """
        Generate repository map.

        Args:
            include_patterns: Glob patterns to include (default: ["**/*.py"])
            exclude_patterns: Glob patterns to exclude

        Returns:
            Dictionary containing repository map
        """
        start_time = time.time()

        if include_patterns is None:
            include_patterns = ["**/*.py"]

        if exclude_patterns is None:
            exclude_patterns = [
                "**/__pycache__/**",
                "**/.venv/**",
                "**/.git/**",
                "**/node_modules/**",
                "**/_ARCHIVE/**",
                "**/tests/**",  # Optionally exclude tests
            ]

        # Find all Python files
        py_files = self._find_files(include_patterns, exclude_patterns)

        # Extract signatures
        modules = {}
        for py_file in py_files:
            try:
                rel_path = py_file.relative_to(self.root_path)
                module_name = self._path_to_module(rel_path)

                sigs = self.signature_extractor.extract_file_signatures(py_file)

                modules[module_name] = {
                    "file": str(rel_path),
                    "functions": sigs["functions"],
                    "classes": sigs["classes"],
                }
            except Exception as e:
                print(f"Warning: Could not process {py_file}: {e}")
                continue

        # Build import graph
        self.import_graph.build_graph(include_patterns)

        elapsed = time.time() - start_time

        return {
            "metadata": {
                "root_path": str(self.root_path),
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "generation_time_seconds": round(elapsed, 2),
                "total_modules": len(modules),
                "total_files": len(py_files),
            },
            "modules": modules,
            "import_graph": {
                "edges": [
                    {
                        "from": edge.from_module,
                        "to": edge.to_module,
                        "names": edge.imported_names,
                    }
                    for edge in self.import_graph.edges
                ]
            },
        }

    def _find_files(
        self, include_patterns: List[str], exclude_patterns: List[str]
    ) -> List[Path]:
        """Find files matching include patterns but not exclude patterns."""
        files = set()

        # Add included files
        for pattern in include_patterns:
            files.update(self.root_path.rglob(pattern))

        # Remove excluded files
        excluded = set()
        for pattern in exclude_patterns:
            excluded.update(self.root_path.rglob(pattern))

        # Also check if file path contains excluded patterns
        final_files = []
        for f in files:
            if f in excluded:
                continue
            # Check if any part of path matches exclude pattern
            rel_path = str(f.relative_to(self.root_path))
            excluded_match = False
            for pattern in exclude_patterns:
                pattern_parts = pattern.replace("**", "").replace("*", "").strip("/")
                if pattern_parts and pattern_parts in rel_path:
                    excluded_match = True
                    break
            if not excluded_match:
                final_files.append(f)

        return sorted(final_files)

    def _path_to_module(self, rel_path: Path) -> str:
        """Convert file path to module name."""
        module_name = str(rel_path.with_suffix("")).replace("\\", ".").replace("/", ".")
        if module_name.endswith(".__init__"):
            module_name = module_name[:-9]
        return module_name

    def save_map(self, output_path: Path, repo_map: Dict):
        """
        Save repository map to YAML file.

        Args:
            output_path: Path to output file
            repo_map: Repository map dictionary
        """
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(repo_map, f, default_flow_style=False, sort_keys=False)

        print(f"Repository map saved to: {output_path}")
        print(f"  Total modules: {repo_map['metadata']['total_modules']}")
        print(f"  Generation time: {repo_map['metadata']['generation_time_seconds']}s")

    def generate_and_save(
        self,
        output_path: Path,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
    ):
        """
        Generate repository map and save to file.

        Args:
            output_path: Path to output YAML file
            include_patterns: Glob patterns to include
            exclude_patterns: Glob patterns to exclude
        """
        repo_map = self.generate_map(include_patterns, exclude_patterns)
        self.save_map(output_path, repo_map)


__all__ = ["RepositoryMapper"]
