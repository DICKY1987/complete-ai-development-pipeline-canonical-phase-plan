"""
Batch Module Migration

Migrates multiple modules from inventory in one operation.

Usage:
    python scripts/batch_migrate_modules.py <module_id_pattern>
    python scripts/batch_migrate_modules.py --layer ui
    python scripts/batch_migrate_modules.py --independent

Examples:
    python scripts/batch_migrate_modules.py error-plugin-*
    python scripts/batch_migrate_modules.py --layer ui --independent
"""

# DOC_ID: DOC-SCRIPT-SCRIPTS-BATCH-MIGRATE-MODULES-193
# DOC_ID: DOC-SCRIPT-SCRIPTS-BATCH-MIGRATE-MODULES-130

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List

import yaml


def load_inventory() -> dict:
    """Load module inventory."""
    inventory_path = Path("MODULES_INVENTORY.yaml")

    if not inventory_path.exists():
        raise FileNotFoundError("MODULES_INVENTORY.yaml not found")

    return yaml.safe_load(inventory_path.read_text(encoding="utf-8"))


def filter_modules(inventory: dict, args) -> List[dict]:
    """Filter modules based on criteria."""
    modules = inventory["modules"]

    filtered = []

    for module in modules:
        # Filter by layer
        if args.layer and module["layer"] != args.layer:
            continue

        # Filter by independent (no dependencies)
        if args.independent and len(module.get("dependencies", [])) > 0:
            continue

        # Filter by pattern
        if args.pattern:
            import fnmatch

            if not fnmatch.fnmatch(module["id"], args.pattern):
                continue

        # Filter by module IDs
        if args.modules:
            if module["id"] not in args.modules:
                continue

        filtered.append(module)

    return filtered


def migrate_module(module_id: str, use_symlinks: bool = False) -> bool:
    """
    Migrate a single module using create_module_from_inventory.py

    Returns:
        True if successful, False otherwise
    """
    cmd = [sys.executable, "scripts/create_module_from_inventory.py", module_id]

    if use_symlinks:
        cmd.append("--symlinks")

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)

    if result.returncode != 0:
        print(f"Failed to migrate {module_id}")
        print(f"   {result.stderr}")
        return False

    return True


def main():
    parser = argparse.ArgumentParser(description="Batch migrate modules")
    parser.add_argument(
        "--layer",
        choices=["infra", "domain", "api", "ui"],
        help="Filter by architectural layer",
    )
    parser.add_argument(
        "--independent",
        action="store_true",
        help="Only migrate modules with no dependencies",
    )
    parser.add_argument("--pattern", help="Module ID pattern (e.g., 'error-plugin-*')")
    parser.add_argument("--modules", nargs="+", help="Specific module IDs to migrate")
    parser.add_argument(
        "--symlinks",
        action="store_true",
        help="Use symlinks instead of copying (Phase 2 mode)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be migrated without doing it",
    )

    args = parser.parse_args()

    # Load inventory
    inventory = load_inventory()

    # Filter modules
    modules_to_migrate = filter_modules(inventory, args)

    if not modules_to_migrate:
        print("No modules match the criteria")
        return

    print(f"Found {len(modules_to_migrate)} module(s) to migrate:\n")
    for module in modules_to_migrate:
        deps = len(module.get("dependencies", []))
        files = module.get("file_count", 0)
        print(
            f"   - {module['id']}: {files} file(s), {deps} dep(s), layer={module['layer']}"
        )

    if args.dry_run:
        print(f"\nDry run complete. Use without --dry-run to execute.")
        return

    # Confirm
    if not args.dry_run:
        print(f"\nMigrating {len(modules_to_migrate)} modules...")
        print(f"Mode: {'Symlinks (Phase 2)' if args.symlinks else 'Copy (Phase 3)'}\n")

    # Migrate each module
    succeeded = []
    failed = []

    for module in modules_to_migrate:
        module_id = module["id"]
        print(f"Migrating {module_id}...", end=" ")

        if migrate_module(module_id, use_symlinks=args.symlinks):
            print("[OK]")
            succeeded.append(module_id)
        else:
            print("[FAIL]")
            failed.append(module_id)

    print(f"\n{'='*60}")
    print(f"[OK] Successfully migrated: {len(succeeded)}/{len(modules_to_migrate)}")

    if failed:
        print(f"[FAIL] Failed: {len(failed)}")
        for module_id in failed:
            print(f"   - {module_id}")
        sys.exit(1)
    else:
        print(f"\nAll modules migrated successfully!")
        print(f"\nNext steps:")
        print(f"   1. Validate all modules: python scripts/validate_modules.py --all")
        print(f"   2. Review manifests in modules/*/")
        print(f"   3. Update MODULE_MIGRATION_PROGRESS.md")


if __name__ == "__main__":
    main()
