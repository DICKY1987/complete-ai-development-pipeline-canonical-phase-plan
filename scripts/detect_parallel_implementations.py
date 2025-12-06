#!/usr/bin/env python3
"""
Parallel Implementation Detector
=================================
Identifies and compares competing implementations of similar functionality.

Detects overlap groups like:
- Orchestration: ./modules/core-engine/ vs ./engine/
- Error systems: ./modules/error-engine/ vs ./UETF/error/
- State management: multiple implementations

Scores each implementation using 200-point system to determine primary version.

Output: parallel_implementations_analysis.json

Pattern: EXEC-017
Author: GitHub Copilot CLI
Version: 1.0.0
Date: 2025-12-02
"""
DOC_ID: DOC-SCRIPT-SCRIPTS-DETECT-PARALLEL-IMPLEMENTATIONS-776
DOC_ID: DOC - SCRIPT - SCRIPTS - DETECT - PARALLEL - IMPLEMENTATIONS - 710
DOC_ID: DOC - SCRIPT - SCRIPTS - DETECT - PARALLEL - IMPLEMENTATIONS - 710

import argparse
import json
import logging
import subprocess
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@dataclass
class ImplementationScore:
    """Scoring for a single implementation."""

    path: str
    score: int  # 0-200 points
    ranking: int
    status: str  # PRIMARY - KEEP, SECONDARY - REVIEW FOR ARCHIVAL
    strengths: List[str]
    concerns: List[str]
    characteristics: Dict
    recommendation: Optional[str]


class ParallelImplementationDetector:
    """Detect and compare parallel implementations."""

    def __init__(self, root: Path):
        self.root = root
        self.codebase_index = None
        self.import_counts: Dict[str, int] = defaultdict(int)

    def load_codebase_index(self):
        """Load CODEBASE_INDEX.yaml if exists."""
        index_path = self.root / "docs" / "CODEBASE_INDEX.yaml"
        if not index_path.exists():
            logger.warning(f"CODEBASE_INDEX.yaml not found at {index_path}")
            return None

        try:
            with open(index_path, "r", encoding="utf-8") as f:
                self.codebase_index = yaml.safe_load(f)
            logger.info("Loaded CODEBASE_INDEX.yaml")
        except Exception as e:
            logger.warning(f"Cannot load CODEBASE_INDEX.yaml: {e}")

        return self.codebase_index

    def detect_overlap_groups(self) -> List[Dict]:
        """Detect potential overlap groups based on directory names and purpose."""
        logger.info("Detecting overlap groups...")

        overlap_groups = []

        # Orchestration engines
        orchestration_paths = []
        for path_str in [
            "modules/core-engine/",
            "engine/",
            "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/",
        ]:
            path = self.root / path_str
            if path.exists():
                orchestration_paths.append(path_str)

        if len(orchestration_paths) >= 2:
            overlap_groups.append(
                {
                    "group_id": "orchestration_engines",
                    "purpose": "Workstream orchestration and execution",
                    "paths": orchestration_paths,
                }
            )

        # Error systems
        error_paths = []
        for path_str in [
            "modules/error-engine/",
            "error/",
            "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/error/",
        ]:
            path = self.root / path_str
            if path.exists():
                error_paths.append(path_str)

        if len(error_paths) >= 2:
            overlap_groups.append(
                {
                    "group_id": "error_systems",
                    "purpose": "Error detection and handling",
                    "paths": error_paths,
                }
            )

        # State management
        state_paths = []
        for path_str in [
            "modules/core-state/",
            "state/",
            "engine/state_store/",
            "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/state/",
        ]:
            path = self.root / path_str
            if path.exists():
                state_paths.append(path_str)

        if len(state_paths) >= 2:
            overlap_groups.append(
                {
                    "group_id": "state_management",
                    "purpose": "State persistence and management",
                    "paths": state_paths,
                }
            )

        logger.info(f"Detected {len(overlap_groups)} overlap groups")
        return overlap_groups

    def score_implementation(
        self, path_str: str
    ) -> Tuple[int, List[str], List[str], Dict]:
        """Score an implementation using 200-point system."""
        path = self.root / path_str

        score = 0
        strengths = []
        concerns = []
        characteristics = {}

        # 1. Canonical path in CODEBASE_INDEX.yaml: +50 pts
        if self.codebase_index:
            canonical_paths = [
                m.get("path", "") for m in self.codebase_index.get("modules", [])
            ]
            if any(path_str in cp for cp in canonical_paths):
                score += 50
                strengths.append("Canonical path in CODEBASE_INDEX.yaml")
            else:
                concerns.append("Not in CODEBASE_INDEX canonical paths")

        # 2. ULID-prefixed files: +40 pts
        ulid_files = list(path.rglob("m[0-9][0-9][0-9][0-9][0-9]*.*"))
        if ulid_files:
            score += 40
            strengths.append(f"ULID-prefixed files ({len(ulid_files)} files)")
        else:
            concerns.append("No ULID prefixes")

        # 3. Most recent git activity: +30 pts
        days_since_update = self._get_days_since_last_commit(path)
        if days_since_update <= 7:
            score += 30
            strengths.append("Most recent commits (last 7 days)")
        elif days_since_update <= 30:
            score += 20
            strengths.append("Recent commits (last 30 days)")
        elif days_since_update <= 90:
            score += 10
        else:
            concerns.append(
                f"Older codebase ({days_since_update} days since major update)"
            )

        characteristics["days_since_update"] = days_since_update

        # 4. Higher import reference count: +25 pts
        import_count = self._count_imports_to_path(path_str)
        if import_count >= 30:
            score += 25
            strengths.append(f"High import reference count ({import_count})")
        elif import_count >= 15:
            score += 15
        elif import_count >= 5:
            score += 5
        else:
            concerns.append(f"Lower import reference count ({import_count})")

        characteristics["import_references"] = import_count

        # 5. Test coverage: +25 pts
        test_files = self._count_test_files(path)
        py_files = len(list(path.rglob("*.py")))
        test_ratio = test_files / max(py_files, 1)

        if test_ratio >= 0.5:
            score += 25
            strengths.append(f"Full test coverage ({test_files} test files)")
        elif test_ratio >= 0.3:
            score += 15
        elif test_ratio >= 0.1:
            score += 5
        else:
            concerns.append("Partial test coverage")

        characteristics["test_files"] = test_files

        # 6. Documentation quality: +15 pts
        readme_files = list(path.glob("README.md")) + list(path.glob("*.md"))
        if len(readme_files) >= 3:
            score += 15
            strengths.append("High documentation quality")
        elif len(readme_files) >= 1:
            score += 10
        else:
            concerns.append("Low documentation")

        characteristics["documentation"] = (
            "High"
            if len(readme_files) >= 3
            else "Medium" if len(readme_files) >= 1 else "Low"
        )

        # 7. Code size (prefer smaller/cleaner): +15 pts
        total_loc = self._count_lines_of_code(path)
        if total_loc <= 3000:
            score += 15
        elif total_loc <= 5000:
            score += 10
        elif total_loc <= 10000:
            score += 5

        characteristics["files"] = py_files
        characteristics["lines_of_code"] = total_loc

        return score, strengths, concerns, characteristics

    def _get_days_since_last_commit(self, path: Path) -> int:
        """Get days since last git commit in directory."""
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%cI", "--", str(path)],
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                commit_date = datetime.fromisoformat(
                    result.stdout.strip().replace("Z", "+00:00")
                )
                delta = datetime.now(timezone.utc) - commit_date
                return delta.days
        except Exception as e:
            logger.debug(f"Git log failed for {path}: {e}")

        return 999999

    def _count_imports_to_path(self, path_str: str) -> int:
        """Count how many files import from this path."""
        import ast

        count = 0
        normalized_path = path_str.replace("/", ".").replace("\\", ".").rstrip(".")

        for py_file in self.root.rglob("*.py"):
            if py_file.is_relative_to(self.root / path_str):
                continue  # Skip files within the same directory

            try:
                content = py_file.read_text(encoding="utf-8")
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module and normalized_path in node.module:
                            count += 1
                            break
            except Exception:
                pass

        return count

    def _count_test_files(self, path: Path) -> int:
        """Count test files in directory."""
        test_count = 0
        test_count += len(list(path.rglob("test_*.py")))
        test_count += len(list(path.rglob("*_test.py")))

        # Check for adjacent tests/ directory
        if (path.parent / "tests").exists():
            test_count += len(list((path.parent / "tests").rglob("*.py")))

        return test_count

    def _count_lines_of_code(self, path: Path) -> int:
        """Count total lines of code in directory."""
        total = 0
        for py_file in path.rglob("*.py"):
            try:
                total += len(py_file.read_text(encoding="utf-8").splitlines())
            except Exception:
                pass
        return total

    def analyze_overlap_groups(self, overlap_groups: List[Dict]) -> List[Dict]:
        """Analyze each overlap group and rank implementations."""
        logger.info("Analyzing overlap groups...")

        results = []

        for group in overlap_groups:
            implementations = []

            for path_str in group["paths"]:
                score, strengths, concerns, chars = self.score_implementation(path_str)

                implementations.append(
                    {
                        "path": path_str,
                        "score": score,
                        "strengths": strengths,
                        "concerns": concerns,
                        "characteristics": chars,
                    }
                )

            # Rank implementations
            implementations.sort(key=lambda x: x["score"], reverse=True)

            for i, impl in enumerate(implementations, 1):
                impl["ranking"] = i
                if i == 1:
                    impl["status"] = "PRIMARY - KEEP"
                    impl["recommendation"] = None
                else:
                    impl["status"] = "SECONDARY - REVIEW FOR ARCHIVAL"
                    impl["recommendation"] = (
                        f"ANALYZE: Determine if {impl['path']} has unique functionality not in primary"
                    )

            results.append(
                {
                    "group_id": group["group_id"],
                    "purpose": group["purpose"],
                    "implementations": implementations,
                    "decision_needed": True,
                    "question": f"Does secondary implementation have unique features not in {implementations[0]['path']}?",
                }
            )

        return results

    def generate_decision_checklist(self, overlap_analysis: List[Dict]) -> str:
        """Generate markdown checklist for human decisions."""
        lines = ["# Parallel Implementations Decision Checklist\n"]
        lines.append("**Generated by EXEC-017 Pattern**\n")
        lines.append(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        for group in overlap_analysis:
            lines.append(f"## {group['group_id']}: {group['purpose']}\n")
            lines.append(f"**Question**: {group['question']}\n\n")

            primary = group["implementations"][0]
            lines.append(f"### Primary (KEEP): `{primary['path']}`\n")
            lines.append(f"- Score: {primary['score']}/200\n")
            lines.append(f"- Strengths:\n")
            for strength in primary["strengths"]:
                lines.append(f"  - {strength}\n")
            lines.append("\n")

            for impl in group["implementations"][1:]:
                lines.append(f"### Secondary: `{impl['path']}`\n")
                lines.append(f"- Score: {impl['score']}/200\n")
                lines.append(f"- Strengths:\n")
                for strength in impl["strengths"]:
                    lines.append(f"  - {strength}\n")
                lines.append(f"- Concerns:\n")
                for concern in impl["concerns"]:
                    lines.append(f"  - {concern}\n")
                lines.append(f"- **Recommendation**: {impl['recommendation']}\n\n")

            lines.append("**Decision**:\n")
            lines.append("- [ ] Archive secondary (functionality is redundant)\n")
            lines.append("- [ ] Keep both (unique functionality exists)\n")
            lines.append("- [ ] Needs investigation\n\n")
            lines.append("**Notes**:\n\n")
            lines.append("---\n\n")

        return "".join(lines)

    def generate_report(self, output_path: Path):
        """Generate comprehensive analysis report."""
        logger.info("Generating analysis...")

        self.load_codebase_index()
        overlap_groups = self.detect_overlap_groups()
        overlap_analysis = self.analyze_overlap_groups(overlap_groups)

        report = {
            "metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "root_directory": str(self.root),
                "pattern": "EXEC-017",
            },
            "overlap_groups": overlap_analysis,
            "statistics": {
                "total_groups": len(overlap_analysis),
                "total_implementations": sum(
                    len(g["implementations"]) for g in overlap_analysis
                ),
            },
        }

        # Write JSON report
        output_path.parent.mkdir(exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        logger.info(f"JSON report written: {output_path}")

        # Generate decision checklist
        checklist_path = (
            output_path.parent / "parallel_implementations_decision_checklist.md"
        )
        checklist = self.generate_decision_checklist(overlap_analysis)
        with open(checklist_path, "w", encoding="utf-8") as f:
            f.write(checklist)

        logger.info(f"Decision checklist written: {checklist_path}")

        # Print summary
        print("\n" + "=" * 70)
        print("PARALLEL IMPLEMENTATIONS ANALYSIS")
        print("=" * 70)
        print(f"\nOverlap groups detected: {len(overlap_analysis)}")

        for group in overlap_analysis:
            print(f"\n{group['group_id'].upper()}: {group['purpose']}")
            for impl in group["implementations"]:
                status_icon = "[PRIMARY]" if impl["ranking"] == 1 else "[SECONDARY]"
                print(
                    f"  {status_icon} {impl['path']} - Score: {impl['score']}/200 (Rank #{impl['ranking']})"
                )

        print(f"\nJSON Report: {output_path}")
        print(f"Decision Checklist: {checklist_path}")
        print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Parallel Implementation Detector",
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
        default=Path("cleanup_reports/parallel_implementations_analysis.json"),
        help="Output report path",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    detector = ParallelImplementationDetector(args.root)
    detector.generate_report(args.output)


if __name__ == "__main__":
    main()
