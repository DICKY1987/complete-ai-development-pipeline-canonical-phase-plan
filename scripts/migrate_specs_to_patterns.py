#!/usr/bin/env python3
"""
Migrate pattern files from specs/ to patterns/ directory.

This script moves pattern files (.pattern.yaml, .pattern.md, EXEC-*.md, PAT-*.md)
from specs/ to appropriate subdirectories in patterns/.
"""

import shutil
from pathlib import Path
from typing import Dict, List, Tuple

# Repository root
REPO_ROOT = Path(__file__).parent.parent
SPECS_DIR = REPO_ROOT / "specs"
PATTERNS_DIR = REPO_ROOT / "patterns"

# Migration mapping: (file_pattern, destination_subdir)
MIGRATION_RULES = [
    # Execution patterns
    (lambda f: f.startswith("EXEC-") and f.endswith(".md"), "execution"),
    # PAT- prefixed patterns
    (lambda f: f.startswith("PAT-") and f.endswith(".md"), "registry"),
    # Automation patterns
    (lambda f: "automation" in f.lower() and f.endswith(".pattern.yaml"), "automation"),
    (lambda f: "automation" in f.lower() and f.endswith(".pattern.md"), "automation"),
    # Pattern events
    (
        lambda f: "pattern_event" in f.lower() and f.endswith(".pattern.yaml"),
        "pattern_event_system",
    ),
    # Module/refactor patterns
    (
        lambda f: ("module" in f.lower() or "refactor" in f.lower())
        and f.endswith(".pattern.yaml"),
        "behavioral",
    ),
    # Execution-related patterns
    (lambda f: "execution" in f.lower() and f.endswith(".pattern.yaml"), "execution"),
    (lambda f: "exec" in f.lower() and f.endswith(".pattern.yaml"), "execution"),
    # Pattern management patterns
    (lambda f: f.startswith("pattern_") and f.endswith(".pattern.yaml"), "registry"),
    # Workflow/session patterns
    (
        lambda f: ("workflow" in f.lower() or "session" in f.lower())
        and f.endswith(".pattern.yaml"),
        "behavioral",
    ),
    # All other .pattern.yaml files go to behavioral by default
    (lambda f: f.endswith(".pattern.yaml"), "behavioral"),
    (lambda f: f.endswith(".pattern.md"), "behavioral"),
]

# Files to keep in specs (actual specifications)
KEEP_IN_SPECS = {
    "GLOSSARY_SSOT_POLICY_SPEC.md",
    "TEST_DEMO_SPEC.md",
    "README.md",
    "README.yaml",
    "README_GITHUB_PROJECT_INTEGRATION.md",
}


def categorize_file(filename: str) -> str | None:
    """Determine which patterns subdirectory a file belongs to."""
    if filename in KEEP_IN_SPECS:
        return None

    for matcher, subdir in MIGRATION_RULES:
        if matcher(filename):
            return subdir

    return None


def collect_migrations() -> Dict[str, List[str]]:
    """Collect all files to migrate, grouped by destination."""
    migrations: Dict[str, List[str]] = {}

    if not SPECS_DIR.exists():
        print(f"❌ specs directory not found: {SPECS_DIR}")
        return migrations

    for item in SPECS_DIR.iterdir():
        if not item.is_file():
            continue

        filename = item.name
        dest_subdir = categorize_file(filename)

        if dest_subdir:
            if dest_subdir not in migrations:
                migrations[dest_subdir] = []
            migrations[dest_subdir].append(filename)

    return migrations


def preview_migrations(migrations: Dict[str, List[str]]) -> None:
    """Show what would be migrated."""
    total = sum(len(files) for files in migrations.values())

    print(f"\n📋 Migration Preview ({total} files)")
    print("=" * 80)

    for subdir in sorted(migrations.keys()):
        files = migrations[subdir]
        print(f"\n📁 patterns/{subdir}/ ({len(files)} files):")
        for filename in sorted(files):
            print(f"   • {filename}")

    # Show files staying in specs
    print(f"\n✅ Keeping in specs/ ({len(KEEP_IN_SPECS)} files):")
    for filename in sorted(KEEP_IN_SPECS):
        if (SPECS_DIR / filename).exists():
            print(f"   • {filename}")


def execute_migrations(
    migrations: Dict[str, List[str]], dry_run: bool = True
) -> Tuple[int, int]:
    """Execute the file migrations."""
    success_count = 0
    error_count = 0

    for subdir, files in migrations.items():
        dest_dir = PATTERNS_DIR / subdir

        # Create destination directory if needed
        if not dry_run:
            dest_dir.mkdir(parents=True, exist_ok=True)

        for filename in files:
            src = SPECS_DIR / filename
            dst = dest_dir / filename

            try:
                if dry_run:
                    print(f"[DRY RUN] Would move: {src} -> {dst}")
                else:
                    if dst.exists():
                        print(f"⚠️  Skipping {filename} (already exists in {subdir})")
                        continue

                    shutil.move(str(src), str(dst))
                    print(f"✓ Moved: {filename} -> patterns/{subdir}/")

                success_count += 1
            except Exception as e:
                print(f"❌ Error moving {filename}: {e}")
                error_count += 1

    return success_count, error_count


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Migrate pattern files from specs/ to patterns/"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute the migration (default is dry-run/preview only)",
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite existing files in destination"
    )

    args = parser.parse_args()

    print("🔍 Analyzing specs/ directory...")
    migrations = collect_migrations()

    if not migrations:
        print("✅ No files to migrate.")
        return 0

    preview_migrations(migrations)

    if not args.execute:
        print("\n" + "=" * 80)
        print("ℹ️  This was a DRY RUN. No files were moved.")
        print("   Run with --execute to perform the migration.")
        return 0

    print("\n" + "=" * 80)
    print("🚀 Executing migration...")

    success, errors = execute_migrations(migrations, dry_run=False)

    print("\n" + "=" * 80)
    print(f"✅ Migration complete: {success} files moved, {errors} errors")

    if errors == 0:
        print("\n💡 Next steps:")
        print("   1. Review moved files in patterns/ subdirectories")
        print("   2. Update any references to old paths")
        print("   3. Commit changes: git add specs/ patterns/")

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    exit(main())
