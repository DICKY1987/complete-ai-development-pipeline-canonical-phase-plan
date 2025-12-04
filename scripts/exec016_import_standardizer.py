"""
EXEC-016: Import Path Standardizer - Simplified Executor
Based on: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/specs/EXEC-016-import-path-standardizer.md
"""
DOC_ID: DOC-SCRIPT-SCRIPTS-EXEC016-IMPORT-STANDARDIZER-712

import re
from pathlib import Path
from typing import List, Dict, Tuple

# Import mapping (old → new patterns)
IMPORT_MAP = {
    r"from core\.": "from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.",
    r"from error\.": "from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.",
    r"from aim\.": "from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.aim.",
    r"from pm\.": "from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.pm.",
    r"import core\.": "import UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.",
    r"import error\.": "import UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.",
    r"import aim\.": "import UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.aim.",
    r"import pm\.": "import UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.pm.",
}

SKIP_PATTERNS = [
    "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK",  # Already UET
    "archive/",  # Historical
    "legacy/",  # Historical
    "__pycache__",  # Generated
    ".venv",  # Virtual env
    "node_modules",  # JS deps
]

def should_skip(file_path: Path) -> bool:
    """Check if file should be skipped."""
    path_str = str(file_path)
    return any(pattern in path_str for pattern in SKIP_PATTERNS)

def analyze_file(file_path: Path) -> Tuple[List[str], int]:
    """Analyze file for old import patterns."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return [], 0

    old_imports = []
    for old_pattern in IMPORT_MAP.keys():
        matches = re.findall(old_pattern, content, re.MULTILINE)
        old_imports.extend(matches)

    return old_imports, len(old_imports)

def rewrite_imports(file_path: Path, dry_run: bool = True) -> Tuple[bool, int]:
    """Rewrite old imports to UET paths."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original = content

        changes = 0
        for old_pattern, new_prefix in IMPORT_MAP.items():
            new_content, count = re.subn(old_pattern, new_prefix, content)
            content = new_content
            changes += count

        if content != original:
            if not dry_run:
                file_path.write_text(content, encoding="utf-8")
            return True, changes
        return False, 0

    except Exception as e:
        print(f"ERROR processing {file_path}: {e}")
        return False, 0

def main():
    """Execute EXEC-016: Import Path Standardizer."""
    import sys

    # Check for --execute flag
    execute = "--execute" in sys.argv

    print("="*70)
    print("EXEC-016: Import Path Standardizer")
    print(f"Mode: {'EXECUTE' if execute else 'DISCOVERY'}")
    print("="*70)
    print()

    # Phase 1: Discovery
    print("Phase 1: Discovery & Analysis")
    print("-" * 70)

    root = Path(".")
    files_to_update = []
    total_imports = 0

    for py_file in root.rglob("*.py"):
        if should_skip(py_file):
            continue

        old_imports, count = analyze_file(py_file)
        if count > 0:
            files_to_update.append((py_file, count))
            total_imports += count

    print(f"Files with old imports: {len(files_to_update)}")
    print(f"Total import statements to update: {total_imports}")
    print()

    if not execute:
        # Show top 20 files
        print("Top 20 files needing updates:")
        print("-" * 70)
        sorted_files = sorted(files_to_update, key=lambda x: x[1], reverse=True)
        for file_path, count in sorted_files[:20]:
            rel_path = str(file_path.relative_to(root))
            print(f"  {count:3d} imports - {rel_path}")

        print()
        print("=" * 70)
        print(f"SUMMARY: {len(files_to_update)} files, {total_imports} imports")
        print("=" * 70)
        print()
        print("Next steps:")
        print("1. Review the files above")
        print("2. Run with --execute to perform the migration")
        print("3. Test after migration: pytest tests/ -v")
        print()

        # Save report
        report_path = Path("import_migration_analysis.txt")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("EXEC-016: Import Path Standardizer - Analysis Report\\n")
            f.write("=" * 70 + "\\n\\n")
            f.write(f"Files to update: {len(files_to_update)}\\n")
            f.write(f"Total imports: {total_imports}\\n\\n")
            f.write("Files (sorted by import count):\\n")
            f.write("-" * 70 + "\\n")
            for file_path, count in sorted_files:
                rel_path = str(file_path.relative_to(root))
                f.write(f"{count:3d} imports - {rel_path}\\n")

        print(f"Report saved: {report_path}")
        return

    # Phase 2: Execute Migration (Batched)
    print()
    print("Phase 2: Executing Migration")
    print("-" * 70)

    # Sort files by import count (do high-impact files first)
    sorted_files = sorted(files_to_update, key=lambda x: x[1], reverse=True)

    # Batch files (25 per batch per EXEC-016 spec)
    batch_size = 25
    batches = [sorted_files[i:i+batch_size] for i in range(0, len(sorted_files), batch_size)]

    print(f"Total batches: {len(batches)}")
    print()

    files_updated = 0
    imports_changed = 0

    for batch_num, batch in enumerate(batches, 1):
        print(f"Batch {batch_num}/{len(batches)}: Processing {len(batch)} files...")

        batch_files_updated = 0
        batch_imports_changed = 0

        for file_path, expected_count in batch:
            changed, count = rewrite_imports(file_path, dry_run=False)
            if changed:
                batch_files_updated += 1
                batch_imports_changed += count
                rel_path = str(file_path.relative_to(root))
                print(f"  ✓ {rel_path} ({count} imports)")

        files_updated += batch_files_updated
        imports_changed += batch_imports_changed

        print(f"  Batch {batch_num} complete: {batch_files_updated} files, {batch_imports_changed} imports")
        print()

    print("=" * 70)
    print("MIGRATION COMPLETE")
    print("=" * 70)
    print(f"Files updated: {files_updated}/{len(files_to_update)}")
    print(f"Imports changed: {imports_changed}/{total_imports}")
    print()
    print("Next steps:")
    print("1. Git status: git status")
    print("2. Review changes: git diff")
    print("3. Commit: git add . && git commit -m 'refactor(exec-016): Update imports to UET paths'")
    print("4. Test: pytest tests/ -v")

if __name__ == "__main__":
    main()
