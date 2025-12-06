#!/usr/bin/env python3
"""
Dependency Graph Validator - Enforce architectural layer compliance

Validates:
1. Layer compliance (no domain imports from UI layer)
2. Circular dependency detection
3. Import path standards enforcement
4. Deprecated import blocking

Exit codes: 0=pass, 1=violations
"""
# DOC_LINK: DOC-SCRIPT-SCRIPTS-VALIDATE-DEPENDENCY-GRAPH-769

from __future__ import annotations

import argparse
import ast
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

import yaml

# Layer hierarchy: infra < domain < api < ui
LAYER_HIERARCHY = {"infra": 0, "domain": 1, "api": 2, "ui": 3}

# Deprecated patterns
DEPRECATED_PATTERNS = ["src.pipeline", "MOD_ERROR_PIPELINE", "legacy."]


class DependencyGraphValidator:
    def __init__(self, codebase_index_path: Path):
        self.index_path = codebase_index_path
        self.index = self._load_index()
        self.violations: List[Dict] = []
        self.module_to_layer = self._build_module_layer_map()
        self.import_graph: Dict[str, Set[str]] = defaultdict(set)

    def _load_index(self) -> Dict:
        """Load CODEBASE_INDEX.yaml"""
        if not self.index_path.exists():
            print(f"⚠️  CODEBASE_INDEX.yaml not found at {self.index_path}")
            return {}
        with open(self.index_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def _build_module_layer_map(self) -> Dict[str, str]:
        """Map module paths to layer names"""
        module_map = {}
        modules = self.index.get("modules", [])

        # Handle both dict and list formats
        if isinstance(modules, dict):
            for module_id, module_info in modules.items():
                if isinstance(module_info, dict):
                    layer = module_info.get("layer", "unknown")
                    path = module_info.get("path", "")
                    if path:
                        module_map[path] = layer
        elif isinstance(modules, list):
            for module_info in modules:
                if isinstance(module_info, dict):
                    layer = module_info.get("layer", "unknown")
                    path = module_info.get("path", "")
                    if path:
                        module_map[path] = layer

        return module_map

    def _get_layer_for_file(self, file_path: str) -> str:
        """Determine layer for a given file"""
        p = Path(file_path)
        for module_path, layer in self.module_to_layer.items():
            if str(p).startswith(module_path):
                return layer
        # Fallback heuristics
        if "gui" in file_path or "ui" in file_path:
            return "ui"
        elif "core" in file_path or "engine" in file_path or "error" in file_path:
            return "domain"
        elif "infra" in file_path:
            return "infra"
        elif "specifications" in file_path or "adapters" in file_path:
            return "api"
        return "unknown"

    def _extract_imports(self, file_path: Path) -> Set[str]:
        """Extract import statements from a Python file"""
        imports = set()
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(file_path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)
        except (SyntaxError, UnicodeDecodeError, FileNotFoundError):
            pass
        return imports

    def _check_layer_violations(self):
        """Check for layer hierarchy violations"""
        repo_root = Path.cwd()
        python_files = list(repo_root.rglob("*.py"))

        for py_file in python_files:
            # Skip tests, archives, legacy
            if any(
                x in str(py_file)
                for x in ["tests", "_ARCHIVE", "legacy", "__pycache__"]
            ):
                continue

            file_layer = self._get_layer_for_file(str(py_file.relative_to(repo_root)))
            if file_layer == "unknown":
                continue

            imports = self._extract_imports(py_file)
            for imp in imports:
                # Build module path from import
                imp_parts = imp.split(".")
                imp_layer = self._get_layer_for_file(imp_parts[0] if imp_parts else "")

                if imp_layer == "unknown":
                    continue

                # Check hierarchy violation
                file_level = LAYER_HIERARCHY.get(file_layer, 99)
                imp_level = LAYER_HIERARCHY.get(imp_layer, 99)

                if imp_level > file_level:
                    self.violations.append(
                        {
                            "type": "layer_violation",
                            "severity": "major",
                            "file": str(py_file.relative_to(repo_root)),
                            "file_layer": file_layer,
                            "import": imp,
                            "import_layer": imp_layer,
                            "reason": f"{file_layer} layer cannot import from {imp_layer} layer",
                        }
                    )

                # Build graph for cycle detection
                self.import_graph[str(py_file.relative_to(repo_root))].add(imp)

    def _check_circular_dependencies(self):
        """Detect circular dependencies using DFS"""
        visited = set()
        rec_stack = set()

        def has_cycle(node: str, path: List[str]) -> bool:
            if node in rec_stack:
                cycle = path[path.index(node) :] + [node]
                self.violations.append(
                    {
                        "type": "circular_dependency",
                        "severity": "critical",
                        "cycle": cycle,
                        "reason": "Circular dependency detected",
                    }
                )
                return True

            if node in visited:
                return False

            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.import_graph.get(node, []):
                if has_cycle(neighbor, path.copy()):
                    pass  # Already recorded

            rec_stack.remove(node)
            return False

        for node in self.import_graph:
            if node not in visited:
                has_cycle(node, [])

    def _check_deprecated_imports(self):
        """Check for deprecated import patterns"""
        repo_root = Path.cwd()
        python_files = list(repo_root.rglob("*.py"))

        for py_file in python_files:
            if any(
                x in str(py_file)
                for x in ["tests", "_ARCHIVE", "legacy", "__pycache__"]
            ):
                continue

            imports = self._extract_imports(py_file)
            for imp in imports:
                for pattern in DEPRECATED_PATTERNS:
                    if pattern in imp:
                        self.violations.append(
                            {
                                "type": "deprecated_import",
                                "severity": "major",
                                "file": str(py_file.relative_to(repo_root)),
                                "import": imp,
                                "pattern": pattern,
                                "reason": f"Import uses deprecated pattern: {pattern}",
                            }
                        )

    def validate_all(self) -> bool:
        """Run all validation checks. Returns True if valid."""
        print("🔍 Validating dependency graph...")
        self._check_layer_violations()
        self._check_circular_dependencies()
        self._check_deprecated_imports()
        return len(self.violations) == 0

    def print_report(self):
        """Print validation report to console"""
        if not self.violations:
            print("✅ Dependency graph validation passed")
            return

        print(f"\n❌ Found {len(self.violations)} violation(s):\n")

        by_type = defaultdict(list)
        for v in self.violations:
            by_type[v["type"]].append(v)

        for vtype, violations in by_type.items():
            print(f"  {vtype.upper().replace('_', ' ')} ({len(violations)}):")
            for v in violations[:5]:  # Show first 5
                if vtype == "layer_violation":
                    print(
                        f"    - {v['file']}: imports {v['import']} ({v['file_layer']} → {v['import_layer']})"
                    )
                elif vtype == "circular_dependency":
                    print(f"    - Cycle: {' → '.join(v['cycle'])}")
                elif vtype == "deprecated_import":
                    print(f"    - {v['file']}: uses deprecated {v['pattern']}")
            if len(violations) > 5:
                print(f"    ... and {len(violations) - 5} more")
            print()

    def save_report(self, output_path: Path):
        """Save validation report to JSON"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        report = {
            "timestamp": str(Path.cwd()),
            "total_violations": len(self.violations),
            "violations": self.violations,
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"📊 Report saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Validate dependency graph")
    parser.add_argument(
        "--index",
        type=Path,
        default=Path("docs/DOC_reference/CODEBASE_INDEX.yaml"),
        help="Path to CODEBASE_INDEX.yaml",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path(".state/dependency_graph_report.json"),
        help="Output path for JSON report",
    )
    args = parser.parse_args()

    validator = DependencyGraphValidator(args.index)
    is_valid = validator.validate_all()
    validator.print_report()
    validator.save_report(args.report)

    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
