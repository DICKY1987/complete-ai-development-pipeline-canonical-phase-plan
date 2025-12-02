#!/usr/bin/env python3
"""
Entry Point Reachability Analyzer
==================================
Identifies orphaned code unreachable from any entry point.

Entry points include:
- Files with if __name__ == "__main__":
- Test files in ./tests/
- CLI entry points
- Scripts in ./scripts/
- Pytest fixtures (conftest.py)

Uses BFS traversal of import graph to mark reachable modules.

Output: entry_point_reachability_report.json

Pattern: EXEC-017
Author: GitHub Copilot CLI
Version: 1.0.0
Date: 2025-12-02
"""

import argparse
import ast
import json
import logging
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Set, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

@dataclass
class ReachabilityScore:
    """Reachability scoring for a module."""
    module_path: str
    is_reachable: bool
    reachability_distance: int  # Hops from entry point (0=entry, -1=unreachable)
    reachable_from: List[str]  # List of entry points that can reach this
    score: int  # 0-100 (100=completely orphaned)
    reasons: List[str]
    
class EntryPointReachabilityAnalyzer:
    """Analyze reachability from entry points."""
    
    def __init__(self, root: Path):
        self.root = root
        self.entry_points: Set[str] = set()
        self.import_graph: Dict[str, Set[str]] = defaultdict(set)
        self.all_modules: Set[str] = set()
        self.reachability: Dict[str, ReachabilityScore] = {}
        
    def find_entry_points(self) -> Set[str]:
        """Identify all entry points in the repository."""
        logger.info("Finding entry points...")
        entry_points = set()
        
        # 1. Files with if __name__ == "__main__":
        for py_file in self.root.rglob('*.py'):
            if self._should_skip(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                if 'if __name__ == "__main__":' in content or "if __name__ == '__main__':" in content:
                    module = self._get_module_name(py_file)
                    entry_points.add(module)
                    logger.debug(f"Entry point (__main__): {module}")
            except Exception as e:
                logger.debug(f"Cannot read {py_file}: {e}")
        
        # 2. Test files in ./tests/
        tests_dir = self.root / 'tests'
        if tests_dir.exists():
            for test_file in tests_dir.rglob('test_*.py'):
                module = self._get_module_name(test_file)
                entry_points.add(module)
                logger.debug(f"Entry point (test): {module}")
        
        # 3. CLI entry points (modules/*/m*_main.py pattern)
        modules_dir = self.root / 'modules'
        if modules_dir.exists():
            for main_file in modules_dir.rglob('*_main.py'):
                module = self._get_module_name(main_file)
                entry_points.add(module)
                logger.debug(f"Entry point (CLI): {module}")
        
        # 4. Scripts in ./scripts/
        scripts_dir = self.root / 'scripts'
        if scripts_dir.exists():
            for script_file in scripts_dir.glob('*.py'):
                if script_file.name.startswith('_'):
                    continue
                module = self._get_module_name(script_file)
                entry_points.add(module)
                logger.debug(f"Entry point (script): {module}")
        
        # 5. Pytest fixtures (conftest.py)
        for conftest in self.root.rglob('conftest.py'):
            module = self._get_module_name(conftest)
            entry_points.add(module)
            logger.debug(f"Entry point (conftest): {module}")
        
        logger.info(f"Found {len(entry_points)} entry points")
        return entry_points
    
    def build_import_graph(self) -> Dict[str, Set[str]]:
        """Build import dependency graph."""
        logger.info("Building import graph...")
        
        for py_file in self.root.rglob('*.py'):
            if self._should_skip(py_file):
                continue
            
            module_name = self._get_module_name(py_file)
            self.all_modules.add(module_name)
            
            imports = self._extract_imports(py_file)
            self.import_graph[module_name].update(imports)
        
        logger.info(f"Import graph built: {len(self.all_modules)} modules, {sum(len(v) for v in self.import_graph.values())} edges")
        return self.import_graph
    
    def compute_reachability(self) -> Dict[str, ReachabilityScore]:
        """Compute reachability scores using BFS from entry points."""
        logger.info("Computing reachability...")
        
        reachable: Dict[str, int] = {}  # module -> distance
        reachable_from: Dict[str, Set[str]] = defaultdict(set)  # module -> entry points
        
        # BFS from each entry point
        for entry_point in self.entry_points:
            queue = deque([(entry_point, 0)])
            visited = {entry_point}
            
            while queue:
                current, distance = queue.popleft()
                
                # Mark as reachable
                if current not in reachable or distance < reachable[current]:
                    reachable[current] = distance
                reachable_from[current].add(entry_point)
                
                # Explore imports
                for imported_module in self.import_graph.get(current, set()):
                    if imported_module not in visited:
                        visited.add(imported_module)
                        queue.append((imported_module, distance + 1))
        
        # Score all modules
        for module in self.all_modules:
            is_reachable = module in reachable
            distance = reachable.get(module, -1)
            from_entries = list(reachable_from.get(module, set()))
            
            # Scoring (0-100, where 100 = completely orphaned)
            if not is_reachable:
                score = 100
                reasons = ["Not reachable from any entry point", "No test references"]
            elif not from_entries:
                score = 85
                reasons = ["Only reachable from other orphans"]
            elif distance > 5:
                score = 70
                reasons = [f"Deep dependency chain (distance={distance})"]
            else:
                score = max(0, (distance / 5) * 50)  # Linear scale based on distance
                reasons = [f"Reachable at distance {distance}"]
            
            self.reachability[module] = ReachabilityScore(
                module_path=module,
                is_reachable=is_reachable,
                reachability_distance=distance,
                reachable_from=from_entries,
                score=score,
                reasons=reasons
            )
        
        unreachable_count = sum(1 for r in self.reachability.values() if not r.is_reachable)
        logger.info(f"Reachability computed: {unreachable_count} unreachable modules")
        
        return self.reachability
    
    def _should_skip(self, path: Path) -> bool:
        """Skip __pycache__, .git, etc."""
        parts = path.parts
        skip_dirs = {'__pycache__', '.git', '.venv', '.worktrees', 'node_modules'}
        return any(part in skip_dirs for part in parts)
    
    def _get_module_name(self, path: Path) -> str:
        """Convert file path to module name."""
        try:
            relative = path.relative_to(self.root)
        except ValueError:
            relative = path
        
        module_path = str(relative.with_suffix(''))
        return module_path.replace('\\', '.').replace('/', '.')
    
    def _extract_imports(self, file_path: Path) -> Set[str]:
        """Extract import statements using AST parsing."""
        imports = set()
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)
        except Exception as e:
            logger.debug(f"Cannot parse {file_path}: {e}")
        
        return imports
    
    def generate_report(self, output_path: Path):
        """Generate JSON report."""
        logger.info(f"Generating report: {output_path}")
        
        report = {
            "metadata": {
                "timestamp": str(Path(__file__).stat().st_mtime),
                "root_directory": str(self.root),
                "total_modules": len(self.all_modules),
                "entry_points_count": len(self.entry_points),
                "pattern": "EXEC-017"
            },
            "entry_points": sorted(list(self.entry_points)),
            "reachability_scores": {
                module: asdict(score) 
                for module, score in sorted(self.reachability.items(), key=lambda x: x[1].score, reverse=True)
            },
            "statistics": {
                "reachable": sum(1 for r in self.reachability.values() if r.is_reachable),
                "unreachable": sum(1 for r in self.reachability.values() if not r.is_reachable),
                "score_100": sum(1 for r in self.reachability.values() if r.score == 100),
                "score_85_plus": sum(1 for r in self.reachability.values() if r.score >= 85),
                "score_70_plus": sum(1 for r in self.reachability.values() if r.score >= 70),
            }
        }
        
        output_path.parent.mkdir(exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report written: {output_path}")
        
        # Print summary
        print("\n" + "="*70)
        print("ENTRY POINT REACHABILITY ANALYSIS")
        print("="*70)
        print(f"\nTotal modules: {len(self.all_modules):,}")
        print(f"Entry points: {len(self.entry_points):,}")
        print(f"\nReachability:")
        print(f"  Reachable:   {report['statistics']['reachable']:,}")
        print(f"  Unreachable: {report['statistics']['unreachable']:,}")
        print(f"\nScore distribution:")
        print(f"  Score 100 (orphaned):     {report['statistics']['score_100']:,}")
        print(f"  Score 85+ (questionable): {report['statistics']['score_85_plus']:,}")
        print(f"  Score 70+ (deep deps):    {report['statistics']['score_70_plus']:,}")
        print(f"\nReport: {output_path}")
        print("="*70 + "\n")

def main():
    parser = argparse.ArgumentParser(
        description="Entry Point Reachability Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--root', '-r',
        type=Path,
        default=Path.cwd(),
        help='Repository root path (default: current directory)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=Path('cleanup_reports/entry_point_reachability_report.json'),
        help='Output report path'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    analyzer = EntryPointReachabilityAnalyzer(args.root)
    analyzer.entry_points = analyzer.find_entry_points()
    analyzer.build_import_graph()
    analyzer.compute_reachability()
    analyzer.generate_report(args.output)

if __name__ == '__main__':
    main()
