#!/usr/bin/env python3
"""
Test Coverage Archival Analyzer
================================
Identifies untested files that are candidates for archival.

Analyzes:
- Test coverage mapping (module -> test files)
- Cross-references with staleness and isolation
- Identifies abandoned code (no tests + old + not imported)

Output: test_coverage_archival_report.json

Pattern: EXEC-017
Author: GitHub Copilot CLI
Version: 1.0.0
Date: 2025-12-02
"""
DOC_ID: DOC-SCRIPT-SCRIPTS-TEST-COVERAGE-ARCHIVAL-729
DOC_ID: DOC - SCRIPT - SCRIPTS - TEST - COVERAGE - ARCHIVAL - 729

import argparse
import ast
import json
import logging
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

STALENESS_DAYS = 90  # 3 months threshold


@dataclass
class TestCoverageScore:
    """Test coverage scoring for archival purposes."""

    module_path: str
    has_tests: bool
    test_files: List[str]
    is_stale: bool
    days_since_modified: int
    is_imported: bool
    score: int  # 0-100 (100=no tests + stale + not imported)
    reasons: List[str]


class TestCoverageArchivalAnalyzer:
    """Analyze test coverage for archival decisions."""

    def __init__(self, root: Path):
        self.root = root
        self.test_coverage: Dict[str, Set[str]] = defaultdict(
            set
        )  # module -> test files
        self.all_modules: Set[str] = set()
        self.import_graph: Dict[str, Set[str]] = defaultdict(set)
        self.scores: Dict[str, TestCoverageScore] = {}

    def scan_test_directories(self):
        """Scan ./tests/ and UETF/tests/ for test files."""
        logger.info("Scanning test directories...")

        test_dirs = [
            self.root / "tests",
            self.root / "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK" / "tests",
        ]

        test_count = 0
        for test_dir in test_dirs:
            if not test_dir.exists():
                continue

            for test_file in test_dir.rglob("test_*.py"):
                test_count += 1
                self._extract_test_targets(test_file)

        logger.info(f"Scanned {test_count} test files")
        logger.info(f"Coverage mapping: {len(self.test_coverage)} modules with tests")

    def scan_all_modules(self):
        """Scan all Python modules in repository."""
        logger.info("Scanning all modules...")

        for py_file in self.root.rglob("*.py"):
            if self._should_skip(py_file):
                continue

            module_name = self._get_module_name(py_file)
            self.all_modules.add(module_name)

            # Build import graph for isolation analysis
            imports = self._extract_imports(py_file)
            self.import_graph[module_name].update(imports)

        logger.info(f"Found {len(self.all_modules)} total modules")

    def compute_scores(self):
        """Compute test coverage scores for archival."""
        logger.info("Computing test coverage scores...")

        for module in self.all_modules:
            # Check if module has tests
            has_tests = module in self.test_coverage
            test_files = list(self.test_coverage.get(module, set()))

            # Check staleness
            module_file = self._module_to_path(module)
            days_stale = self._get_days_since_modified(module_file)
            is_stale = days_stale >= STALENESS_DAYS

            # Check if imported by other modules
            is_imported = any(
                module in imports for imports in self.import_graph.values()
            )

            # Scoring (0-100, where 100 = strong archival candidate)
            score = 0
            reasons = []

            if not has_tests:
                if is_stale and not is_imported:
                    score = 95
                    reasons = [
                        "No test coverage",
                        f"{days_stale} days since modified (>= {STALENESS_DAYS} threshold)",
                        "Not imported by any module",
                    ]
                elif self._has_deprecated_naming(module):
                    score = 80
                    reasons = ["No test coverage", "Deprecated naming pattern detected"]
                elif not is_imported:
                    score = 70
                    reasons = ["No test coverage", "Not imported by any module"]
                else:
                    score = 50
                    reasons = ["No test coverage"]
            else:
                score = 0
                reasons = [f"Has test coverage ({len(test_files)} test files)"]

            self.scores[module] = TestCoverageScore(
                module_path=module,
                has_tests=has_tests,
                test_files=test_files,
                is_stale=is_stale,
                days_since_modified=days_stale,
                is_imported=is_imported,
                score=score,
                reasons=reasons,
            )

        untested_count = sum(1 for s in self.scores.values() if not s.has_tests)
        high_score_count = sum(1 for s in self.scores.values() if s.score >= 70)
        logger.info(
            f"Scoring complete: {untested_count} untested, {high_score_count} high-risk"
        )

    def _extract_test_targets(self, test_file: Path):
        """Extract modules being tested from a test file."""
        try:
            content = test_file.read_text(encoding="utf-8")
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.test_coverage[alias.name].add(str(test_file))
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self.test_coverage[node.module].add(str(test_file))
        except Exception as e:
            logger.debug(f"Cannot parse {test_file}: {e}")

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
        except Exception as e:
            logger.debug(f"Cannot parse {file_path}: {e}")

        return imports

    def _get_days_since_modified(self, file_path: Path) -> int:
        """Get days since file was last modified."""
        try:
            if not file_path.exists():
                return 999999  # File doesn't exist

            mtime = datetime.fromtimestamp(file_path.stat().st_mtime, tz=timezone.utc)
            delta = datetime.now(timezone.utc) - mtime
            return delta.days
        except Exception:
            return 999999

    def _has_deprecated_naming(self, module: str) -> bool:
        """Check if module has deprecated naming patterns."""
        deprecated_keywords = [
            "deprecated",
            "old",
            "legacy",
            "backup",
            "tmp",
            "temp",
            "archive",
            "_bak",
        ]
        module_lower = module.lower()
        return any(keyword in module_lower for keyword in deprecated_keywords)

    def _should_skip(self, path: Path) -> bool:
        """Skip __pycache__, .git, etc."""
        parts = path.parts
        skip_dirs = {"__pycache__", ".git", ".venv", ".worktrees", "node_modules"}
        return any(part in skip_dirs for part in parts)

    def _get_module_name(self, path: Path) -> str:
        """Convert file path to module name."""
        try:
            relative = path.relative_to(self.root)
        except ValueError:
            relative = path

        module_path = str(relative.with_suffix(""))
        return module_path.replace("\\", ".").replace("/", ".")

    def _module_to_path(self, module: str) -> Path:
        """Convert module name back to file path."""
        file_path = module.replace(".", "\\") + ".py"
        return self.root / file_path

    def generate_report(self, output_path: Path):
        """Generate JSON report."""
        logger.info(f"Generating report: {output_path}")

        report = {
            "metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "root_directory": str(self.root),
                "total_modules": len(self.all_modules),
                "staleness_threshold_days": STALENESS_DAYS,
                "pattern": "EXEC-017",
            },
            "test_coverage_scores": {
                module: asdict(score)
                for module, score in sorted(
                    self.scores.items(), key=lambda x: x[1].score, reverse=True
                )
            },
            "statistics": {
                "total_modules": len(self.all_modules),
                "modules_with_tests": sum(
                    1 for s in self.scores.values() if s.has_tests
                ),
                "modules_without_tests": sum(
                    1 for s in self.scores.values() if not s.has_tests
                ),
                "score_95_plus": sum(1 for s in self.scores.values() if s.score >= 95),
                "score_80_plus": sum(1 for s in self.scores.values() if s.score >= 80),
                "score_70_plus": sum(1 for s in self.scores.values() if s.score >= 70),
                "score_50_plus": sum(1 for s in self.scores.values() if s.score >= 50),
            },
            "coverage_gaps": [
                module
                for module, score in self.scores.items()
                if not score.has_tests and score.score >= 70
            ],
        }

        output_path.parent.mkdir(exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Report written: {output_path}")

        # Print summary
        print("\n" + "=" * 70)
        print("TEST COVERAGE ARCHIVAL ANALYSIS")
        print("=" * 70)
        print(f"\nTotal modules: {len(self.all_modules):,}")
        print(f"Modules with tests: {report['statistics']['modules_with_tests']:,}")
        print(
            f"Modules without tests: {report['statistics']['modules_without_tests']:,}"
        )
        print(f"\nArchival candidates (by score):")
        print(
            f"  Score 95+ (no tests + stale + isolated): {report['statistics']['score_95_plus']:,}"
        )
        print(
            f"  Score 80+ (no tests + deprecated):       {report['statistics']['score_80_plus']:,}"
        )
        print(
            f"  Score 70+ (no tests + isolated):         {report['statistics']['score_70_plus']:,}"
        )
        print(
            f"  Score 50+ (no tests):                    {report['statistics']['score_50_plus']:,}"
        )
        print(f"\nReport: {output_path}")
        print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Test Coverage Archival Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--root",
        "-r",
        type=Path,
        default=Path.cwd(),
        help="Repository root path (default: current directory)",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("cleanup_reports/test_coverage_archival_report.json"),
        help="Output report path",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    analyzer = TestCoverageArchivalAnalyzer(args.root)
    analyzer.scan_test_directories()
    analyzer.scan_all_modules()
    analyzer.compute_scores()
    analyzer.generate_report(args.output)


if __name__ == "__main__":
    main()
