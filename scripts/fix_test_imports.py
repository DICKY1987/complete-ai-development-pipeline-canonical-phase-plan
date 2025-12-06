#!/usr/bin/env python3
"""Fix deprecated UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK imports in test files.

Part of PH-TEST-INFRA-001: Fix Test Infrastructure Import Issues


DOC_ID: DOC-SCRIPT-SCRIPTS-FIX-TEST-IMPORTS-785
"""
# DOC_ID: DOC - SCRIPT - SCRIPTS - FIX - TEST - IMPORTS - 714
# DOC_ID: DOC - SCRIPT - SCRIPTS - FIX - TEST - IMPORTS - 714

import re
from pathlib import Path


def fix_imports(file_path: Path) -> bool:
    """Fix deprecated imports in a single file.

    Returns True if file was modified.
    """
    content = file_path.read_text(encoding="utf-8")
    original = content

    # Define replacements (order matters - specific before general)
    replacements = [
        (
            r"from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\.core\.interfaces",
            "from core",
        ),
        (
            r"from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\.core\.config",
            "from core.config",
        ),
        (
            r"from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\.core\.execution",
            "from core.execution",
        ),
        (
            r"from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\.core\.state",
            "from core.state",
        ),
        (
            r"from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\.core\.adapters",
            "from core.adapters",
        ),
        (
            r"from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\.core\.workstreams",
            "from core.workstreams",
        ),
        (r"from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\.core\.ast", "from core.ast"),
        (
            r"from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\.core\.engine",
            "from core.engine",
        ),
        (r"from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\.core", "from core"),
        (r"from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\.aim", "from aim"),
        (r"from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\.error", "from error"),
    ]

    # Apply all replacements
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)

    # Save if changed
    if content != original:
        file_path.write_text(content, encoding="utf-8")
        return True

    return False


def main():
    """Fix all test files with deprecated imports."""
    test_dir = Path("tests")
    pattern = r"from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK"

    fixed_count = 0
    skipped_count = 0
    error_count = 0

    # Find all Python files with deprecated imports
    for file_path in test_dir.rglob("*.py"):
        try:
            content = file_path.read_text(encoding="utf-8")

            if re.search(pattern, content):
                print(f"Processing: {file_path}")

                if fix_imports(file_path):
                    print(f"  ✅ Fixed")
                    fixed_count += 1
                else:
                    print(f"  ⚠️  No changes needed")
                    skipped_count += 1

        except Exception as e:
            print(f"  ❌ Error: {e}")
            error_count += 1

    # Summary
    print(f"\n{'='*50}")
    print(f"Import Fix Results:")
    print(f"  Fixed: {fixed_count} files")
    print(f"  Skipped: {skipped_count} files")
    print(f"  Errors: {error_count} files")
    print(f"{'='*50}\n")

    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    exit(main())
