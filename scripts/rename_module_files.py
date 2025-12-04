"""
Rename Module Files to Python-Safe Names
Adds 'm' prefix to ULID-prefixed files so they can be imported in Python
Pattern: EXEC-001 - Batch file renaming
"""
# DOC_ID: DOC-SCRIPT-SCRIPTS-RENAME-MODULE-FILES-223
# DOC_ID: DOC-SCRIPT-SCRIPTS-RENAME-MODULE-FILES-160

import sys
from pathlib import Path
import shutil

def rename_module_files(dry_run: bool = False) -> int:
    """Rename all ULID-prefixed files to have 'm' prefix."""
    print("=" * 70)
    print("Renaming Module Files to Python-Safe Names")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print("=" * 70)

    modules_dir = Path("modules")
    if not modules_dir.exists():
        print("❌ modules/ directory not found")
        return 1

    # Find all files starting with digits (ULIDs)
    files_to_rename = []
    for py_file in modules_dir.rglob("*.py"):
        # Skip __init__.py and README files
        if py_file.name.startswith('__') or py_file.name.startswith('README'):
            continue

        # Check if starts with digit (ULID)
        if py_file.stem[0].isdigit():
            files_to_rename.append(py_file)

    print(f"\nFound {len(files_to_rename)} files to rename")

    if dry_run:
        print("\n[DRY RUN] Sample renames:")
        for f in files_to_rename[:10]:
            new_name = f"m{f.name}"
            print(f"  {f.name}")
            print(f"  → {new_name}")
        if len(files_to_rename) > 10:
            print(f"  ... and {len(files_to_rename) - 10} more files")
        return 0

    # Rename files
    renamed_count = 0
    errors = []

    for py_file in files_to_rename:
        new_name = f"m{py_file.name}"
        new_path = py_file.parent / new_name

        try:
            py_file.rename(new_path)
            renamed_count += 1

            if renamed_count % 50 == 0:
                print(f"  Renamed {renamed_count}/{len(files_to_rename)} files...")
        except Exception as e:
            errors.append(f"{py_file}: {e}")

    # Summary
    print("\n" + "=" * 70)
    if errors:
        print(f"⚠️  Renamed {renamed_count}/{len(files_to_rename)} files with {len(errors)} errors")
        for err in errors[:5]:
            print(f"  ❌ {err}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors")
        return 1
    else:
        print(f"✅ Successfully renamed {renamed_count} files")
        return 0

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Rename module files to Python-safe names')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be renamed')

    args = parser.parse_args()

    return rename_module_files(args.dry_run)

if __name__ == "__main__":
    sys.exit(main())
