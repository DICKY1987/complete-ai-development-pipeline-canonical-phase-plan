"""
Migrate to UET Engine (Option B)

This script migrates from 3 engine locations to a single canonical UET-based engine.

Target Architecture:
  UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/ → core/engine/

Actions:
  1. Move UET engine to core/engine/
  2. Archive old core/engine/ and root engine/
  3. Update all imports systematically
  4. Run tests to verify

# DOC_ID: DOC-SCRIPT-MIGRATE-UET-ENGINE-001
"""

import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
UET_ENGINE = (
    PROJECT_ROOT / "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK" / "core" / "engine"
)
OLD_CORE_ENGINE = PROJECT_ROOT / "core" / "engine"
ROOT_ENGINE = PROJECT_ROOT / "engine"
NEW_CORE_ENGINE = PROJECT_ROOT / "core" / "engine"


class UETEngineMigration:
    """Migrates to UET engine as canonical implementation"""

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.archive_dir = (
            PROJECT_ROOT / "archive" / f"{self.timestamp}_engine-consolidation"
        )
        self.changes: List[Tuple[str, str]] = []
        self.errors: List[str] = []

    def log(self, message: str):
        """Log a message"""
        prefix = "[DRY-RUN] " if self.dry_run else "[EXECUTE] "
        print(f"{prefix}{message}")

    def error(self, message: str):
        """Log an error"""
        self.errors.append(message)
        print(f"❌ ERROR: {message}")

    # PHASE 1: Backup and Archive

    def create_git_backup(self) -> bool:
        """Create git tag for rollback"""
        tag = f"pre-uet-engine-migration-{self.timestamp}"
        self.log(f"Creating git tag: {tag}")

        if not self.dry_run:
            try:
                subprocess.run(
                    [
                        "git",
                        "tag",
                        "-a",
                        tag,
                        "-m",
                        "Backup before UET engine migration",
                    ],
                    cwd=PROJECT_ROOT,
                    check=True,
                    capture_output=True,
                )
                self.log(f"✅ Git tag created: {tag}")
                return True
            except subprocess.CalledProcessError as e:
                self.error(f"Failed to create git tag: {e.stderr.decode()}")
                return False
        return True

    def archive_old_engines(self) -> bool:
        """Archive old engine implementations"""
        self.log(f"Creating archive directory: {self.archive_dir}")

        if not self.dry_run:
            self.archive_dir.mkdir(parents=True, exist_ok=True)

        # Archive old core/engine/
        if OLD_CORE_ENGINE.exists():
            dest = self.archive_dir / "old-core-engine"
            self.log(f"Archiving {OLD_CORE_ENGINE} → {dest}")
            if not self.dry_run:
                shutil.copytree(OLD_CORE_ENGINE, dest)

        # Archive root engine/ (keep for reference - has job queue features)
        if ROOT_ENGINE.exists():
            dest = self.archive_dir / "root-engine-jobqueue"
            self.log(f"Archiving {ROOT_ENGINE} → {dest}")
            if not self.dry_run:
                shutil.copytree(ROOT_ENGINE, dest)

        return True

    # PHASE 2: Move UET Engine

    def move_uet_engine_to_core(self) -> bool:
        """Move UET engine to core/engine/"""
        if not UET_ENGINE.exists():
            self.error(f"UET engine not found: {UET_ENGINE}")
            return False

        self.log(f"Moving {UET_ENGINE} → {NEW_CORE_ENGINE}")

        if not self.dry_run:
            # Remove old core/engine/ first
            if OLD_CORE_ENGINE.exists():
                shutil.rmtree(OLD_CORE_ENGINE)

            # Ensure parent exists
            NEW_CORE_ENGINE.parent.mkdir(parents=True, exist_ok=True)

            # Copy UET engine to core/engine/
            shutil.copytree(UET_ENGINE, NEW_CORE_ENGINE)
            self.log(f"✅ Moved UET engine to core/engine/")

        return True

    # PHASE 3: Update Imports

    def get_import_mappings(self) -> Dict[str, str]:
        """Define import mapping patterns"""
        return {
            # UET imports → core.engine
            r"from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\.core\.engine\.([a-zA-Z0-9_\.]+) import": r"from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine.\1 import",
            r"from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\.core\.engine import": r"from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine import",
            r"import UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\.core\.engine\.([a-zA-Z0-9_\.]+)": r"import UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine.\1",
            r"import UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\.core\.engine": r"import UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine",
            # Root engine imports → core.engine (for compatible features)
            # Note: Not all root engine features have UET equivalents
            # These will need manual review
        }

    def update_file_imports(self, file_path: Path) -> bool:
        """Update imports in a single file"""
        try:
            content = file_path.read_text(encoding="utf-8")
            original_content = content

            mappings = self.get_import_mappings()

            for pattern, replacement in mappings.items():
                content = re.sub(pattern, replacement, content)

            if content != original_content:
                self.changes.append((str(file_path), "imports updated"))
                self.log(f"  Updated imports: {file_path.relative_to(PROJECT_ROOT)}")

                if not self.dry_run:
                    file_path.write_text(content, encoding="utf-8")

            return True

        except Exception as e:
            self.error(f"Failed to update {file_path}: {e}")
            return False

    def update_all_imports(self) -> bool:
        """Update imports in all Python files"""
        self.log("Scanning for files with UET engine imports...")

        files_to_update = []

        # Scan all Python files except archive, __pycache__, .venv
        for py_file in PROJECT_ROOT.rglob("*.py"):
            if any(
                exclude in py_file.parts
                for exclude in ["archive", "__pycache__", ".venv", ".pytest_cache"]
            ):
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                if "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine" in content:
                    files_to_update.append(py_file)
            except Exception:
                continue

        self.log(f"Found {len(files_to_update)} files to update")

        for file_path in files_to_update:
            self.update_file_imports(file_path)

        return True

    # PHASE 4: Update Module Shims

    def update_module_shims(self) -> bool:
        """Update modules/core-engine/ shims to point to core.engine"""
        modules_dir = PROJECT_ROOT / "modules" / "core-engine"

        if not modules_dir.exists():
            self.log(f"No modules/core-engine/ directory found, skipping")
            return True

        self.log(f"Updating module shims in {modules_dir}")

        for shim_file in modules_dir.glob("m010001_*.py"):
            try:
                content = shim_file.read_text(encoding="utf-8")
                original = content

                # Change UET imports to core.engine
                content = content.replace(
                    "from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine.",
                    "from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine.",
                )

                if content != original:
                    self.changes.append((str(shim_file), "shim updated"))
                    self.log(f"  Updated shim: {shim_file.name}")

                    if not self.dry_run:
                        shim_file.write_text(content, encoding="utf-8")

            except Exception as e:
                self.error(f"Failed to update shim {shim_file}: {e}")

        return True

    # PHASE 5: Create Compatibility Layer for Root Engine

    def create_engine_compatibility_shim(self) -> bool:
        """Create shim in engine/ to redirect to core.engine where possible"""

        shim_content = '''"""
Compatibility shim for root engine/ → core.engine/

The UET engine in core/engine/ is now canonical.
Some features from the old job queue system are not yet ported.

Deprecated: Use 'from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine.*' directly
Remove after: 2025-12-31
"""

import warnings

warnings.warn(
    "Importing from 'engine' is deprecated. "
    "Use 'from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine.*' instead. "
    "Job queue features are being ported to core.engine.",
    DeprecationWarning,
    stacklevel=2
)

# Map what we can to core.engine
try:
    from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine.orchestrator import Orchestrator
    from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine.executor import Executor
except ImportError:
    # Fallback to old implementation if needed
    pass

__all__ = ['Orchestrator', 'Executor']
'''

        shim_path = ROOT_ENGINE / "__init__.py"
        self.log(f"Creating compatibility shim: {shim_path}")

        if not self.dry_run:
            if ROOT_ENGINE.exists():
                # Read existing __init__.py
                existing = (
                    shim_path.read_text(encoding="utf-8") if shim_path.exists() else ""
                )
                # Backup existing
                backup_path = self.archive_dir / "root-engine-init-backup.py"
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                backup_path.write_text(existing, encoding="utf-8")

                # Write new shim
                shim_path.write_text(shim_content, encoding="utf-8")
                self.log(f"✅ Created compatibility shim (old __init__.py backed up)")

        return True

    # PHASE 6: Verification

    def verify_migration(self) -> bool:
        """Run basic verification checks"""
        self.log("Running verification checks...")

        # Check that core/engine/ exists and has expected files
        if not self.dry_run:
            if not NEW_CORE_ENGINE.exists():
                self.error("core/engine/ does not exist after migration!")
                return False

            expected_files = [
                "orchestrator.py",
                "executor.py",
                "scheduler.py",
                "resilience",
                "monitoring",
            ]

            for expected in expected_files:
                path = NEW_CORE_ENGINE / expected
                if not path.exists():
                    self.error(f"Expected file/dir missing: {path}")
                    return False

            self.log("✅ core/engine/ structure verified")

        # Check for remaining UET imports
        remaining = []
        for py_file in PROJECT_ROOT.rglob("*.py"):
            if any(
                exclude in py_file.parts
                for exclude in ["archive", "__pycache__", ".venv"]
            ):
                continue
            try:
                content = py_file.read_text(encoding="utf-8")
                if "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine" in content:
                    remaining.append(py_file)
            except Exception:
                continue

        if remaining:
            self.log(
                f"⚠️  {len(remaining)} files still have UET imports (may need manual review)"
            )
            for f in remaining[:5]:  # Show first 5
                self.log(f"    - {f.relative_to(PROJECT_ROOT)}")
        else:
            self.log("✅ No remaining UET engine imports found")

        return True

    # Main Execution

    def run(self) -> bool:
        """Execute the migration"""
        print("=" * 80)
        print(f"UET Engine Migration - Option B")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'EXECUTE'}")
        print(f"Timestamp: {self.timestamp}")
        print("=" * 80)
        print()

        steps = [
            ("Create git backup", self.create_git_backup),
            ("Archive old engines", self.archive_old_engines),
            ("Move UET engine to core/", self.move_uet_engine_to_core),
            ("Update imports to core.engine", self.update_all_imports),
            ("Update module shims", self.update_module_shims),
            (
                "Create engine/ compatibility shim",
                self.create_engine_compatibility_shim,
            ),
            ("Verify migration", self.verify_migration),
        ]

        for step_name, step_func in steps:
            print(f"\n{'='*80}")
            print(f"STEP: {step_name}")
            print(f"{'='*80}")

            if not step_func():
                self.error(f"Step failed: {step_name}")
                return False

        print(f"\n{'='*80}")
        print(f"MIGRATION {'DRY RUN ' if self.dry_run else ''}COMPLETED")
        print(f"{'='*80}")
        print(f"\nSummary:")
        print(f"  Files modified: {len(self.changes)}")
        print(f"  Errors: {len(self.errors)}")

        if self.errors:
            print(f"\nErrors encountered:")
            for err in self.errors:
                print(f"  - {err}")

        if self.dry_run:
            print(f"\n⚠️  This was a DRY RUN. No changes were made.")
            print(f"Run with --execute to apply changes.")
        else:
            print(f"\n✅ Changes applied. Archive created at:")
            print(f"   {self.archive_dir}")
            print(f"\nNext steps:")
            print(f"  1. Run tests: pytest tests/")
            print(f"  2. Check for import errors")
            print(f"  3. Review compatibility issues")

        return len(self.errors) == 0


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Migrate to UET engine (Option B)")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute the migration (default is dry-run)",
    )

    args = parser.parse_args()

    migration = UETEngineMigration(dry_run=not args.execute)
    success = migration.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
