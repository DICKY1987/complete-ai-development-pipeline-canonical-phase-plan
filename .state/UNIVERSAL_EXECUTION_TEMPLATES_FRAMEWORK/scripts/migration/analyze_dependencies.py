# DOC_LINK: DOC-SCRIPT-MIGRATION-ANALYZE-DEPENDENCIES-336
import ast
import re
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
import json
from datetime import datetime, timezone


class DependencyMapper:
    """Map Python import dependencies for migration planning."""

    def __init__(self, root_dir: Path):
        self.root = root_dir
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.all_modules: Set[str] = set()

    def scan_directory(self, patterns: List[str] = None) -> Dict:
        """Scan directory for Python files and extract dependencies."""
        patterns = patterns or ["**/*.py"]

        print("?? Analyzing import dependencies...")

        for pattern in patterns:
            for py_file in self.root.glob(pattern):
                if self._should_skip(py_file):
                    continue

                module_name = self._get_module_name(py_file)
                self.all_modules.add(module_name)

                imports = self._extract_imports(py_file)
                self.dependencies[module_name].update(imports)

        return self._generate_report()

    def _should_skip(self, path: Path) -> bool:
        """Skip __init__, tests, and hidden files."""
        return (
            path.name == "__init__.py"
            or "test_" in path.name
            or path.name.startswith(".")
            or "__pycache__" in str(path)
            or "archive/legacy" in str(path)
        )

    def _get_module_name(self, path: Path) -> str:
        """Convert file path to module name."""
        relative = path.relative_to(self.root)
        module_path = str(relative.with_suffix(""))
        return module_path.replace("\\", ".").replace("/", ".")

    def _extract_imports(self, file_path: Path) -> Set[str]:
        """Extract import statements using AST parsing."""
        imports = set()

        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)

        except (SyntaxError, UnicodeDecodeError):
            imports = self._extract_imports_regex(file_path)

        return {imp for imp in imports if self._is_internal(imp)}

    def _extract_imports_regex(self, file_path: Path) -> Set[str]:
        """Fallback regex-based import extraction."""
        imports = set()
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")

            from_pattern = r"from\s+([\w\.]+)\s+import"
            imports.update(re.findall(from_pattern, content))

            import_pattern = r"import\s+([\w\.]+)"
            imports.update(re.findall(import_pattern, content))
        except Exception:
            pass

        return imports

    def _is_internal(self, module_name: str) -> bool:
        """Check if module is internal (not stdlib or external)."""
        external = {
            "typing",
            "pathlib",
            "os",
            "sys",
            "json",
            "yaml",
            "pytest",
            "click",
            "pydantic",
            "sqlalchemy",
            "fastapi",
            "requests",
            "numpy",
            "pandas",
            "re",
            "hashlib",
            "shutil",
            "subprocess",
            "datetime",
        }

        base_module = module_name.split(".")[0]
        return base_module not in external

    def _generate_report(self) -> Dict:
        """Generate dependency analysis report."""
        total_modules = len(self.all_modules)
        total_dependencies = sum(len(deps) for deps in self.dependencies.values())
        avg_dependencies = total_dependencies / total_modules if total_modules > 0 else 0

        circular = self._find_circular_dependencies()

        migration_order = self._topological_sort()

        leaf_modules = {mod for mod in self.all_modules if len(self.dependencies[mod]) == 0}

        highly_coupled = sorted(
            [(mod, len(deps)) for mod, deps in self.dependencies.items()],
            key=lambda x: x[1],
            reverse=True,
        )[:10]

        return {
            "analysis_date": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_modules": total_modules,
                "total_dependencies": total_dependencies,
                "average_dependencies": round(avg_dependencies, 2),
                "leaf_modules_count": len(leaf_modules),
                "circular_dependencies_count": len(circular),
            },
            "leaf_modules": sorted(leaf_modules),
            "highly_coupled": highly_coupled,
            "circular_dependencies": circular,
            "migration_order": migration_order,
            "dependency_graph": {k: list(v) for k, v in self.dependencies.items()},
        }

    def _find_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependency chains."""
        circular = []
        visited = set()
        rec_stack = set()

        def visit(module: str, path: List[str]):
            if module in rec_stack:
                cycle_start = path.index(module) if module in path else 0
                cycle = path[cycle_start:] + [module]
                if cycle not in circular:
                    circular.append(cycle)
                return

            if module in visited:
                return

            visited.add(module)
            rec_stack.add(module)

            for dep in self.dependencies.get(module, set()):
                if dep in self.all_modules:
                    visit(dep, path + [module])

            rec_stack.remove(module)

        for module in self.all_modules:
            if module not in visited:
                visit(module, [])

        return circular

    def _topological_sort(self) -> List[str]:
        """Return migration order (dependencies first)."""
        in_degree = {mod: 0 for mod in self.all_modules}

        for deps in self.dependencies.values():
            for dep in deps:
                if dep in in_degree:
                    in_degree[dep] += 1

        queue = [mod for mod, deg in in_degree.items() if deg == 0]
        result = []

        while queue:
            module = queue.pop(0)
            result.append(module)

            for dependent in self.all_modules:
                if module in self.dependencies.get(dependent, set()):
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)

        if len(result) != len(self.all_modules):
            remaining = self.all_modules - set(result)
            result.extend(sorted(remaining))

        return result


if __name__ == "__main__":
    root = Path(".")
    mapper = DependencyMapper(root)

    patterns = [
        "core/**/*.py",
        "error/**/*.py",
        "aim/**/*.py",
        "pm/**/*.py",
        "modules/**/*.py",
        "engine/**/*.py",
        "specifications/**/*.py",
    ]

    report = mapper.scan_directory(patterns)

    print("\n?? Dependency Analysis Report")
    print("=" * 60)
    print(f"Total modules: {report['summary']['total_modules']}")
    print(f"Total dependencies: {report['summary']['total_dependencies']}")
    print(f"Average deps/module: {report['summary']['average_dependencies']}")
    print(f"Leaf modules: {report['summary']['leaf_modules_count']}")

    if report["circular_dependencies"]:
        print(f"\n??  Circular Dependencies: {len(report['circular_dependencies'])}")
        for cycle in report["circular_dependencies"][:3]:
            print(f"  - {' -> '.join(cycle)}")
    else:
        print("\n? No circular dependencies")

    print("\n?? Leaf Modules (migrate first):")
    for mod in report["leaf_modules"][:5]:
        print(f"  - {mod}")

    print("\n?? Highly Coupled (migrate last):")
    for mod, count in report["highly_coupled"][:3]:
        print(f"  - {mod} ({count} deps)")

    output_path = Path(
        "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/dependency_report.json"
    )
    output_path.write_text(json.dumps(report, indent=2))

    print(f"\n?? Full report: {output_path}")
