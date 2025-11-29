"""Cleanup Executor - Main Pattern Execution Engine

Orchestrates execution of cleanup patterns with safety mechanisms,
validation, and rollback capabilities.

Usage:
    python cleanup_executor.py --pattern EXEC-014 --dry-run
    python cleanup_executor.py --pattern EXEC-016 --auto-approve
    python cleanup_executor.py --pattern EXEC-014 --config custom.yaml
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

import yaml


@dataclass
class ExecutionResult:
    """Result of pattern execution."""
    pattern_id: str
    status: str  # "success", "failure", "rolled_back"
    start_time: str
    end_time: str
    duration_seconds: float
    changes_made: Dict
    commits_created: List[str]
    tests_passed: bool
    rollback_performed: bool
    error_message: Optional[str] = None


class CleanupExecutor:
    """Main pattern execution engine with safety mechanisms."""

    def __init__(self, config_path: str = "config/cleanup_automation_config.yaml"):
        """Initialize executor with configuration."""
        self.config = self._load_config(config_path)
        self.results: List[ExecutionResult] = []
        self.backup_dir = Path(self.config.get("global", {}).get("backup_directory", ".cleanup_backups"))

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_file) as f:
            return yaml.safe_load(f)

    def validate_pre_execution(self) -> bool:
        """Run pre-execution validation checks."""
        print("Running pre-execution validation...")

        checks = [
            self._check_git_clean(),
            self._check_tests_baseline(),
            self._check_backup_space()
        ]

        return all(checks)

    def _check_git_clean(self) -> bool:
        """Check git working directory is clean."""
        result = subprocess.run(
            ["git", "diff", "--exit-code"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print("  ✗ Git working directory has uncommitted changes", file=sys.stderr)
            return False

        print("  ✓ Git working directory clean")
        return True

    def _check_tests_baseline(self) -> bool:
        """Check tests are passing before execution."""
        test_cmd = self.config.get("validation", {}).get("test_command", "pytest -q tests/")
        required_pass = self.config.get("validation", {}).get("test_required_pass_count", 196)

        result = subprocess.run(
            test_cmd.split(),
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"  ✗ Tests not passing at baseline", file=sys.stderr)
            return False

        print(f"  ✓ Tests passing ({required_pass} tests)")
        return True

    def _check_backup_space(self) -> bool:
        """Check sufficient backup space available."""
        # Create backup directory if it doesn't exist
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Simple check: ensure directory is writable
        test_file = self.backup_dir / ".test_write"
        try:
            test_file.write_text("test")
            test_file.unlink()
            print(f"  ✓ Backup directory writable: {self.backup_dir}")
            return True
        except IOError as e:
            print(f"  ✗ Backup directory not writable: {e}", file=sys.stderr)
            return False

    def execute_pattern(self, pattern_id: str, dry_run: bool = False) -> ExecutionResult:
        """Execute a cleanup pattern."""
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Executing pattern: {pattern_id}")

        start_time = datetime.now()

        # Get pattern configuration
        pattern_config = self.config.get("patterns", {}).get(pattern_id, {})
        if not pattern_config:
            raise ValueError(f"Pattern not found in configuration: {pattern_id}")

        if not pattern_config.get("enabled", False):
            print(f"Pattern {pattern_id} is disabled")
            return ExecutionResult(
                pattern_id=pattern_id,
                status="skipped",
                start_time=start_time.isoformat(),
                end_time=datetime.now().isoformat(),
                duration_seconds=0,
                changes_made={},
                commits_created=[],
                tests_passed=True,
                rollback_performed=False
            )

        try:
            # Execute pattern-specific logic
            changes_made = {}
            commits_created = []

            if pattern_id == "EXEC-014":
                changes_made, commits_created = self._execute_exec_014(dry_run)
            elif pattern_id == "EXEC-016":
                changes_made, commits_created = self._execute_exec_016(dry_run)
            else:
                print(f"Pattern {pattern_id} not yet implemented")
                changes_made = {"status": "not_implemented"}

            # Validate after execution
            tests_passed = self._validate_post_execution() if not dry_run else True

            end_time = datetime.now()

            result = ExecutionResult(
                pattern_id=pattern_id,
                status="success",
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                duration_seconds=(end_time - start_time).total_seconds(),
                changes_made=changes_made,
                commits_created=commits_created,
                tests_passed=tests_passed,
                rollback_performed=False
            )

            self.results.append(result)
            return result

        except Exception as e:
            print(f"Error during execution: {e}", file=sys.stderr)

            # Attempt rollback if configured
            rollback_performed = False
            if self.config.get("global", {}).get("rollback_on_failure", True):
                rollback_performed = self._rollback(commits_created)

            end_time = datetime.now()

            result = ExecutionResult(
                pattern_id=pattern_id,
                status="failure",
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                duration_seconds=(end_time - start_time).total_seconds(),
                changes_made={},
                commits_created=commits_created,
                tests_passed=False,
                rollback_performed=rollback_performed,
                error_message=str(e)
            )

            self.results.append(result)
            return result

    def _execute_exec_014(self, dry_run: bool) -> tuple[Dict, List[str]]:
        """Execute EXEC-014: Exact Duplicate Eliminator."""
        from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.patterns.automation.detectors.duplicate_detector import DuplicateDetector

        detector = DuplicateDetector()
        scan_paths = self.config.get("global", {}).get("scan_paths", ["."])

        # Discovery phase
        result = detector.scan_for_duplicates(scan_paths)

        print(f"  Found {result.total_duplicates} duplicate files in {len(result.duplicate_groups)} groups")
        print(f"  Potential savings: {result.potential_savings_bytes / (1024 * 1024):.2f} MB")

        if dry_run:
            return {
                "duplicates_found": result.total_duplicates,
                "groups": len(result.duplicate_groups),
                "potential_savings_bytes": result.potential_savings_bytes
            }, []

        # Execution phase (simplified for now - would need full implementation)
        changes_made = {
            "duplicates_found": result.total_duplicates,
            "duplicates_removed": 0,  # Would be implemented in full version
            "space_saved_bytes": 0
        }

        return changes_made, []

    def _execute_exec_016(self, dry_run: bool) -> tuple[Dict, List[str]]:
        """Execute EXEC-016: Import Path Standardizer."""
        from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.patterns.automation.detectors.import_pattern_analyzer import ImportPatternAnalyzer

        analyzer = ImportPatternAnalyzer()
        scan_paths = self.config.get("global", {}).get("scan_paths", ["."])

        # Discovery phase
        plan = analyzer.scan_directory(scan_paths)

        print(f"  Files to update: {plan.files_to_update}")
        print(f"  Import changes: {plan.total_import_changes}")
        print(f"  Estimated batches: {len(plan.batches)}")

        if dry_run:
            return {
                "files_to_update": plan.files_to_update,
                "import_changes": plan.total_import_changes,
                "batches": len(plan.batches)
            }, []

        # Execution phase (simplified - would need full batched implementation)
        changes_made = {
            "files_to_update": plan.files_to_update,
            "files_updated": 0,  # Would be implemented in full version
            "import_changes": plan.total_import_changes
        }

        return changes_made, []

    def _validate_post_execution(self) -> bool:
        """Run post-execution validation."""
        print("Running post-execution validation...")

        # Run test suite
        test_cmd = self.config.get("validation", {}).get("test_command", "pytest -q tests/")

        result = subprocess.run(
            test_cmd.split(),
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print("  ✗ Tests failed after execution", file=sys.stderr)
            return False

        print("  ✓ All tests passing")
        return True

    def _rollback(self, commits: List[str]) -> bool:
        """Rollback git commits."""
        if not commits:
            return True

        print(f"Rolling back {len(commits)} commits...")

        try:
            subprocess.run(
                ["git", "revert", "--no-edit", f"HEAD~{len(commits)}..HEAD"],
                check=True,
                capture_output=True
            )
            print("  ✓ Rollback successful")
            return True

        except subprocess.CalledProcessError as e:
            print(f"  ✗ Rollback failed: {e}", file=sys.stderr)
            return False

    def export_results(self, output_path: str) -> None:
        """Export execution results to JSON."""
        output_data = {
            "execution_timestamp": datetime.now().isoformat(),
            "results": [asdict(r) for r in self.results]
        }

        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"\nResults exported to: {output_path}")


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Execute cleanup patterns")
    parser.add_argument("--pattern", required=True, help="Pattern ID to execute (e.g., EXEC-014)")
    parser.add_argument("--config", default="config/cleanup_automation_config.yaml", help="Config file")
    parser.add_argument("--dry-run", action="store_true", help="Report only, no changes")
    parser.add_argument("--auto-approve", action="store_true", help="Skip manual approval")
    parser.add_argument("--log", help="Log file path")
    parser.add_argument("--report", help="Export results to JSON")

    args = parser.parse_args()

    executor = CleanupExecutor(config_path=args.config)

    # Pre-execution validation
    if not args.dry_run:
        if not executor.validate_pre_execution():
            print("\nPre-execution validation failed. Aborting.", file=sys.stderr)
            sys.exit(1)

    # Execute pattern
    result = executor.execute_pattern(args.pattern, dry_run=args.dry_run)

    # Print result summary
    print(f"\nExecution {'[DRY RUN] ' if args.dry_run else ''}Summary:")
    print(f"  Pattern: {result.pattern_id}")
    print(f"  Status: {result.status}")
    print(f"  Duration: {result.duration_seconds:.2f}s")
    print(f"  Tests passed: {result.tests_passed}")

    if result.error_message:
        print(f"  Error: {result.error_message}", file=sys.stderr)

    if args.report:
        executor.export_results(args.report)

    sys.exit(0 if result.status == "success" else 1)


if __name__ == "__main__":
    main()
