"""
Migrate openspec/ and spec/ into unified specifications/ directory.

This script:
1. Creates the new specifications/ structure
2. Moves content from openspec/specs/ to specifications/content/
3. Moves openspec/changes/ to specifications/changes/
4. Moves openspec/archive/ to specifications/archive/
5. Moves spec/tools/ to specifications/tools/
6. Creates bridge/ directory with documentation
7. Updates all import statements in Python files
8. Creates a .index/ directory for generated files
9. Generates a migration report

Usage:
    python scripts/migrate_spec_folders.py [--dry-run] [--backup]
"""
# DOC_ID: DOC-SCRIPT-SCRIPTS-MIGRATE-SPEC-FOLDERS-218
# DOC_ID: DOC-SCRIPT-SCRIPTS-MIGRATE-SPEC-FOLDERS-155

import argparse
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Tuple


# Define the migration mapping
MIGRATION_MAP = {
    # openspec content
    "openspec/specs": "specifications/content",
    "openspec/changes": "specifications/changes",
    "openspec/archive": "specifications/archive",

    # spec tools
    "spec/tools/spec_indexer": "specifications/tools/indexer",
    "spec/tools/spec_resolver": "specifications/tools/resolver",
    "spec/tools/spec_guard": "specifications/tools/guard",
    "spec/tools/spec_patcher": "specifications/tools/patcher",
    "spec/tools/spec_renderer": "specifications/tools/renderer",

    # Bridge documentation
    "openspec/OPENSPEC_BRIDGE_SUMMARY.md": "specifications/bridge/BRIDGE_SUMMARY.md",
    "openspec/project.md": "specifications/bridge/project_conventions.md",
}

# Import path replacements
IMPORT_REPLACEMENTS = [
    ("from specifications.tools.indexer", "from specifications.tools.indexer"),
    ("from specifications.tools.resolver", "from specifications.tools.resolver"),
    ("from specifications.tools.guard", "from specifications.tools.guard"),
    ("from specifications.tools.patcher", "from specifications.tools.patcher"),
    ("from specifications.tools.renderer", "from specifications.tools.renderer"),
    ("import specifications.tools.indexer", "import specifications.tools.indexer"),
    ("import specifications.tools.resolver", "import specifications.tools.resolver"),
    ("import specifications.tools.guard", "import specifications.tools.guard"),
    ("import specifications.tools.patcher", "import specifications.tools.patcher"),
    ("import specifications.tools.renderer", "import specifications.tools.renderer"),
]


def get_repo_root() -> Path:
    """Get repository root directory."""
    script_path = Path(__file__).resolve()
    return script_path.parent.parent


def create_directory_structure(root: Path, dry_run: bool = False) -> List[Path]:
    """Create the new specifications/ directory structure."""
    spec_root = root / "specifications"

    directories = [
        spec_root,
        spec_root / "content",
        spec_root / "changes",
        spec_root / "archive",
        spec_root / "tools",
        spec_root / "tools" / "indexer",
        spec_root / "tools" / "resolver",
        spec_root / "tools" / "guard",
        spec_root / "tools" / "patcher",
        spec_root / "tools" / "renderer",
        spec_root / ".index",
        spec_root / "bridge",
        spec_root / "schemas",
    ]

    created = []
    for directory in directories:
        if not directory.exists():
            if not dry_run:
                directory.mkdir(parents=True, exist_ok=True)
            created.append(directory)
            print(f"  CREATE: {directory.relative_to(root)}")

    return created


def migrate_files(root: Path, dry_run: bool = False) -> Dict[str, str]:
    """Move files according to migration map."""
    migrated = {}

    for src_path, dest_path in MIGRATION_MAP.items():
        src = root / src_path
        dest = root / dest_path

        if not src.exists():
            print(f"  SKIP (not found): {src_path}")
            continue

        if src.is_file():
            # Move individual file
            if not dry_run:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
            print(f"  MOVE: {src_path} → {dest_path}")
            migrated[str(src)] = str(dest)

        elif src.is_dir():
            # Move directory contents
            if not dry_run:
                dest.mkdir(parents=True, exist_ok=True)
                # Copy entire directory tree
                for item in src.rglob("*"):
                    if item.is_file():
                        rel_path = item.relative_to(src)
                        dest_file = dest / rel_path
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, dest_file)
            print(f"  MOVE: {src_path}/ → {dest_path}/")
            migrated[str(src)] = str(dest)

    return migrated


def update_imports(root: Path, dry_run: bool = False) -> List[Tuple[Path, int]]:
    """Update import statements in all Python files."""
    updated_files = []

    # Find all Python files
    python_files = list(root.rglob("*.py"))

    for py_file in python_files:
        # Skip files in old directories or __pycache__
        if "__pycache__" in str(py_file):
            continue
        if str(py_file).startswith(str(root / "openspec")):
            continue
        if str(py_file).startswith(str(root / "spec")):
            continue

        try:
            content = py_file.read_text(encoding="utf-8")
            original_content = content
            changes = 0

            # Apply replacements
            for old_import, new_import in IMPORT_REPLACEMENTS:
                if old_import in content:
                    content = content.replace(old_import, new_import)
                    changes += content.count(new_import) - original_content.count(new_import)

            if changes > 0:
                if not dry_run:
                    py_file.write_text(content, encoding="utf-8")
                print(f"  UPDATE: {py_file.relative_to(root)} ({changes} imports)")
                updated_files.append((py_file, changes))

        except Exception as e:
            print(f"  ERROR reading {py_file}: {e}")

    return updated_files


def create_readme(root: Path, dry_run: bool = False) -> None:
    """Create README.md for specifications/ directory."""
    readme_path = root / "specifications" / "README.md"

    content = """# Specifications Directory

This directory contains all specification documents and tools for managing them.

## Structure

- **`content/`** - Specification documents organized by domain
  - `orchestration/` - Pipeline orchestration specs
  - `plugin-system/` - Plugin architecture specs
  - `validation-pipeline/` - Validation flow specs

- **`changes/`** - Active OpenSpec change proposals
  - Each change has `proposal.md`, `tasks.md`, and modified specs

- **`archive/`** - Completed and historical changes

- **`tools/`** - Specification processing utilities
  - `indexer/` - Generate indices and sidecars
  - `resolver/` - Resolve spec URIs (spec://, specid://)
  - `guard/` - Validate consistency
  - `patcher/` - Update paragraphs by ID
  - `renderer/` - Render specs to Markdown

- **`.index/`** - Generated index files (gitignored)
  - `suite-index.yaml` - Main specification index
  - `document-index.json` - Document metadata

- **`bridge/`** - OpenSpec → Workstream integration
  - Documentation on converting specs to workstreams

- **`schemas/`** - Metadata validation schemas

## Workflow

1. **Create change proposal**: `/openspec:proposal "Feature description"`
2. **Convert to workstream**: `python scripts/spec_to_workstream.py --interactive`
3. **Execute**: `python scripts/run_workstream.py --ws-id ws-feature-x`
4. **Archive**: After completion, move from `changes/` to `archive/`

## Tools Usage

```bash
# Generate indices
python specifications/tools/indexer/indexer.py --source specifications/content

# Resolve spec URI
python specifications/tools/resolver/resolver.py spec://VOLUME/SECTION

# Validate consistency
python specifications/tools/guard/guard.py

# Render to Markdown
python specifications/tools/renderer/renderer.py --output rendered_spec.md
```

## Import Paths

```python
from modules.specifications_tools.m010020_indexer import generate_index
from modules.specifications_tools.m010020_resolver import resolve_spec_uri
from modules.specifications_tools.m010020_guard import validate_suite
```

## Migration

This directory was created by consolidating:
- `openspec/` - Specification content and change management
- `spec/` - Specification processing tools

See `scripts/migrate_spec_folders.py` for migration details.
"""

    if not dry_run:
        readme_path.write_text(content, encoding="utf-8")
    print(f"  CREATE: specifications/README.md")


def create_tool_inits(root: Path, dry_run: bool = False) -> None:
    """Create __init__.py files for tool modules."""
    spec_root = root / "specifications"

    init_files = [
        spec_root / "tools" / "__init__.py",
        spec_root / "tools" / "indexer" / "__init__.py",
        spec_root / "tools" / "resolver" / "__init__.py",
        spec_root / "tools" / "guard" / "__init__.py",
        spec_root / "tools" / "patcher" / "__init__.py",
        spec_root / "tools" / "renderer" / "__init__.py",
    ]

    for init_file in init_files:
        if not init_file.exists():
            if not dry_run:
                init_file.write_text('"""Specification tools."""\n', encoding="utf-8")
            print(f"  CREATE: {init_file.relative_to(root)}")


def create_gitignore(root: Path, dry_run: bool = False) -> None:
    """Create .gitignore for specifications/.index/."""
    gitignore_path = root / "specifications" / ".index" / ".gitignore"

    content = """# Generated index files
*.yaml
*.json
*.yml

# Keep this file
!.gitignore
"""

    if not dry_run:
        gitignore_path.parent.mkdir(parents=True, exist_ok=True)
        gitignore_path.write_text(content, encoding="utf-8")
    print(f"  CREATE: specifications/.index/.gitignore")


def create_backup(root: Path) -> Path:
    """Create backup of old directories."""
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = root / f".migration_backup_{timestamp}"
    backup_dir.mkdir(exist_ok=True)

    # Backup openspec/
    if (root / "openspec").exists():
        shutil.copytree(root / "openspec", backup_dir / "openspec")
        print(f"  BACKUP: openspec/ → {backup_dir.name}/openspec/")

    # Backup spec/
    if (root / "spec").exists():
        shutil.copytree(root / "spec", backup_dir / "spec")
        print(f"  BACKUP: spec/ → {backup_dir.name}/spec/")

    return backup_dir


def generate_report(root: Path, migrated: Dict[str, str], updated_files: List[Tuple[Path, int]]) -> str:
    """Generate migration report."""
    report = []
    report.append("=" * 70)
    report.append("SPECIFICATION FOLDER MIGRATION REPORT")
    report.append("=" * 70)
    report.append("")

    report.append(f"Files migrated: {len(migrated)}")
    report.append(f"Python files updated: {len(updated_files)}")
    report.append("")

    if migrated:
        report.append("MIGRATION DETAILS:")
        for src, dest in migrated.items():
            src_rel = Path(src).relative_to(root) if root in Path(src).parents else src
            dest_rel = Path(dest).relative_to(root) if root in Path(dest).parents else dest
            report.append(f"  {src_rel} → {dest_rel}")
        report.append("")

    if updated_files:
        report.append("UPDATED IMPORTS:")
        total_changes = sum(count for _, count in updated_files)
        for file, count in updated_files:
            file_rel = file.relative_to(root)
            report.append(f"  {file_rel} ({count} imports)")
        report.append(f"  Total import changes: {total_changes}")
        report.append("")

    report.append("NEXT STEPS:")
    report.append("  1. Review the migrated files in specifications/")
    report.append("  2. Run tests: pytest -q")
    report.append("  3. Verify imports work correctly")
    report.append("  4. Update documentation references")
    report.append("  5. Delete old directories (openspec/, spec/) if satisfied")
    report.append("  6. Commit changes to git")
    report.append("")
    report.append("=" * 70)

    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description="Migrate spec folders to unified structure")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--backup", action="store_true", help="Create backup of old directories before migration")
    args = parser.parse_args()

    root = get_repo_root()

    print("\n" + "=" * 70)
    print("SPECIFICATION FOLDER MIGRATION")
    print("=" * 70)
    print(f"Repository root: {root}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE MIGRATION'}")
    print("=" * 70)
    print()

    # Create backup if requested
    if args.backup and not args.dry_run:
        print("Creating backup...")
        backup_dir = create_backup(root)
        print(f"Backup created: {backup_dir}")
        print()

    # Step 1: Create directory structure
    print("Step 1: Creating directory structure...")
    create_directory_structure(root, args.dry_run)
    print()

    # Step 2: Migrate files
    print("Step 2: Migrating files...")
    migrated = migrate_files(root, args.dry_run)
    print()

    # Step 3: Create supporting files
    print("Step 3: Creating supporting files...")
    create_readme(root, args.dry_run)
    create_tool_inits(root, args.dry_run)
    create_gitignore(root, args.dry_run)
    print()

    # Step 4: Update imports
    print("Step 4: Updating import statements...")
    updated_files = update_imports(root, args.dry_run)
    print()

    # Generate report
    report = generate_report(root, migrated, updated_files)
    print(report)

    # Save report to file
    if not args.dry_run:
        report_path = root / "specifications" / "MIGRATION_REPORT.txt"
        report_path.write_text(report, encoding="utf-8")
        print(f"\nReport saved to: {report_path.relative_to(root)}")

    if args.dry_run:
        print("\n⚠️  This was a DRY RUN. No changes were made.")
        print("Run without --dry-run to perform the migration.")
    else:
        print("\n✅ Migration complete!")
        print("\nReview the changes and run tests before committing.")


if __name__ == "__main__":
    main()
