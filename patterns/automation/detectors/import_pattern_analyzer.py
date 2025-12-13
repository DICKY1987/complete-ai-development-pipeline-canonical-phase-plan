"""Import Pattern Analyzer - EXEC-016 Implementation

Analyzes and migrates Python import statements to canonical paths.
Detects deprecated import patterns and provides migration recommendations.

Usage:
    python import_pattern_analyzer.py --check-all --report violations.json
    python import_pattern_analyzer.py --check-deprecated --fail-on-violation
    python import_pattern_analyzer.py --migrate --dry-run
"""
# DOC_ID: DOC-PAT-DETECTORS-IMPORT-PATTERN-ANALYZER-883

from __future__ import annotations

import re
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Tuple

import yaml


@dataclass
class ImportViolation:
    """Detected import pattern violation."""
    file_path: str
    line_number: int
    old_import: str
    recommended_import: str
    confidence: int
    pattern_id: str


@dataclass
class MigrationPlan:
    """Plan for migrating imports."""
    files_to_update: int
    total_import_changes: int
    batches: List[Dict]
    estimated_commits: int
    violations: List[ImportViolation]


class ImportPatternAnalyzer:
    """Analyze and migrate import patterns."""

    def __init__(self, config_path: str = "config/cleanup_automation_config.yaml"):
        """Initialize analyzer with configuration."""
        self.config = self._load_config(config_path)
        self.migration_map = self._load_migration_map()

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file) as f:
                return yaml.safe_load(f)
        return {}

    def _load_migration_map(self) -> List[Dict]:
        """Load import migration map."""
        map_file = self.config.get("patterns", {}).get("EXEC-016", {}).get("migration_map_file")

        if map_file and Path(map_file).exists():
            with open(map_file) as f:
                data = yaml.safe_load(f)
                return data.get("migrations", [])

        # Default migration patterns
        return [
            {
                "old_pattern": r"^from core\.orchestrator import",
                "new_pattern": "from core.engine import",
                "confidence": 100
            },
            {
                "old_pattern": r"^from core\.executor import",
                "new_pattern": "from core.engine import",
                "confidence": 100
            },
            {
                "old_pattern": r"^from error\.engine import",
                "new_pattern": "from error.engine import",
                "confidence": 100
            },
            {
                "old_pattern": r"^from modules\.core_engine import",
                "new_pattern": "from core.engine import",
                "confidence": 100
            },
            {
                "old_pattern": r"^from modules\.error_shared import",
                "new_pattern": "from error.shared.utils import",
                "confidence": 100
            },
            # Deprecated patterns (should be blocked)
            {
                "old_pattern": r"^from src\.pipeline",
                "action": "block",
                "message": "Deprecated: use core module instead",
                "confidence": 100
            },
            {
                "old_pattern": r"^from MOD_ERROR_PIPELINE",
                "action": "block",
                "message": "Deprecated: use error module instead",
                "confidence": 100
            }
        ]

    def scan_file_imports(self, file_path: Path) -> List[ImportViolation]:
        """Scan a single file for import pattern violations."""
        violations = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                line_stripped = line.strip()

                # Check each migration pattern
                for migration in self.migration_map:
                    old_pattern = migration["old_pattern"]

                    if re.match(old_pattern, line_stripped):
                        action = migration.get("action", "migrate")

                        if action == "block":
                            recommended = migration.get("message", "Remove this import")
                        else:
                            # Generate recommended import
                            new_pattern = migration.get("new_pattern", "")
                            recommended = re.sub(old_pattern, new_pattern, line_stripped)

                        violation = ImportViolation(
                            file_path=str(file_path),
                            line_number=line_num,
                            old_import=line_stripped,
                            recommended_import=recommended,
                            confidence=migration.get("confidence", 100),
                            pattern_id=f"IMPORT-{hash(old_pattern) % 10000:04d}"
                        )
                        violations.append(violation)

        except (IOError, UnicodeDecodeError) as e:
            print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)

        return violations

    def scan_directory(self, scan_paths: List[str]) -> MigrationPlan:
        """Scan directories for import violations."""
        all_violations = []
        scanned_files = 0

        for scan_path in scan_paths:
            root = Path(scan_path)
            if not root.exists():
                continue

            for py_file in root.rglob("*.py"):
                if self._should_exclude(py_file):
                    continue

                scanned_files += 1
                violations = self.scan_file_imports(py_file)
                all_violations.extend(violations)

        # Group violations by file for batching
        files_with_violations = set(v.file_path for v in all_violations)

        # Create batches
        batch_size = self.config.get("patterns", {}).get("EXEC-016", {}).get("batch_size", 25)
        file_list = list(files_with_violations)
        batches = []

        for i in range(0, len(file_list), batch_size):
            batch_files = file_list[i:i+batch_size]
            batch_violations = [v for v in all_violations if v.file_path in batch_files]

            batches.append({
                "batch_id": len(batches) + 1,
                "files": batch_files,
                "import_count": len(batch_violations),
                "dependency_level": 0  # Would need dependency graph analysis
            })

        return MigrationPlan(
            files_to_update=len(files_with_violations),
            total_import_changes=len(all_violations),
            batches=batches,
            estimated_commits=len(batches),
            violations=all_violations
        )

    def _should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded."""
        path_str = str(path)
        exclusions = self.config.get("global", {}).get("exclusions", {})

        for excl_dir in exclusions.get("directories", []):
            if excl_dir in path_str:
                return True

        return False

    def migrate_file_imports(self, file_path: Path, dry_run: bool = False) -> int:
        """Migrate imports in a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content
            changes_made = 0

            # Apply each migration pattern
            for migration in self.migration_map:
                old_pattern = migration["old_pattern"]
                action = migration.get("action", "migrate")

                if action == "migrate":
                    new_pattern = migration.get("new_pattern", "")

                    # Count matches before replacement
                    matches = len(re.findall(old_pattern, content, re.MULTILINE))

                    if matches > 0:
                        content = re.sub(old_pattern, new_pattern, content, flags=re.MULTILINE)
                        changes_made += matches

            # Write changes if not dry run
            if changes_made > 0 and not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            return changes_made

        except (IOError, UnicodeDecodeError) as e:
            print(f"Error migrating {file_path}: {e}", file=sys.stderr)
            return 0

    def check_deprecated_imports(self, scan_paths: List[str]) -> bool:
        """Check for deprecated import patterns (quality gate)."""
        deprecated_patterns = [
            r"^from src\.pipeline",
            r"^from MOD_ERROR_PIPELINE",
            r"^from legacy\.",
        ]

        found_deprecated = False

        for scan_path in scan_paths:
            root = Path(scan_path)
            if not root.exists():
                continue

            for py_file in root.rglob("*.py"):
                if self._should_exclude(py_file):
                    continue

                with open(py_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        for pattern in deprecated_patterns:
                            if re.match(pattern, line.strip()):
                                print(f"Deprecated import: {py_file}:{line_num}: {line.strip()}", file=sys.stderr)
                                found_deprecated = True

        return not found_deprecated  # Return True if clean (no deprecated)

    def export_report(self, plan: MigrationPlan, output_path: str) -> None:
        """Export migration plan to JSON."""
        output_data = {
            "files_to_update": plan.files_to_update,
            "total_import_changes": plan.total_import_changes,
            "estimated_commits": plan.estimated_commits,
            "batches": plan.batches,
            "violations": [asdict(v) for v in plan.violations]
        }

        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"Migration plan exported to: {output_path}")


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Analyze and migrate import patterns")
    parser.add_argument("--scan-paths", nargs="+", default=["."], help="Paths to scan")
    parser.add_argument("--config", default="config/cleanup_automation_config.yaml", help="Config file")
    parser.add_argument("--check-all", action="store_true", help="Check all imports")
    parser.add_argument("--check-deprecated", action="store_true", help="Check only deprecated")
    parser.add_argument("--check-staged", action="store_true", help="Check staged git files")
    parser.add_argument("--fail-on-violation", action="store_true", help="Exit 1 if violations found")
    parser.add_argument("--migrate", action="store_true", help="Migrate imports")
    parser.add_argument("--dry-run", action="store_true", help="Report only, no changes")
    parser.add_argument("--report", help="Export report to JSON")

    args = parser.parse_args()

    analyzer = ImportPatternAnalyzer(config_path=args.config)

    if args.check_deprecated or args.fail_on_violation:
        is_clean = analyzer.check_deprecated_imports(args.scan_paths)

        if is_clean:
            print("✓ No deprecated imports detected")
            sys.exit(0)
        else:
            print("✗ Deprecated imports found", file=sys.stderr)
            sys.exit(1)

    if args.check_all or args.migrate:
        plan = analyzer.scan_directory(args.scan_paths)

        print(f"\nImport Pattern Analysis Results:")
        print(f"  Files to update: {plan.files_to_update}")
        print(f"  Total import changes: {plan.total_import_changes}")
        print(f"  Estimated batches: {len(plan.batches)}")
        print(f"  Estimated commits: {plan.estimated_commits}")

        if args.migrate and not args.dry_run:
            print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Migrating imports...")
            total_changes = 0

            for violation in plan.violations:
                file_path = Path(violation.file_path)
                changes = analyzer.migrate_file_imports(file_path, dry_run=args.dry_run)
                total_changes += changes

            print(f"{'[DRY RUN] ' if args.dry_run else ''}Total changes: {total_changes}")

        if args.report:
            analyzer.export_report(plan, args.report)


if __name__ == "__main__":
    main()
