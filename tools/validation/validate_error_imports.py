#!/usr/bin/env python3
"""
Validate that all imports from the error package follow the correct path structure.

Correct patterns:
  - from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.engine.* import ...
  - from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.plugins.* import ...
  - from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.shared.* import ...

Incorrect patterns (deprecated):
  - from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.plugin_manager import ...  (should be error.engine.plugin_manager)
  - from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.pipeline_engine import ... (should be error.engine.pipeline_engine)
  - from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.file_hash_cache import ... (should be error.engine.file_hash_cache)
"""
# DOC_ID: DOC-PAT-VALIDATION-VALIDATE-ERROR-IMPORTS-637
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Tuple


def check_file(file_path: Path) -> List[Tuple[int, str, str]]:
    """Check a Python file for incorrect error imports.
    
    Returns:
        List of (line_number, line_content, reason) for violations
    """
    violations = []
    
    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines()
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)
        return violations
    
    # Pattern to match: from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.XXX import ... where XXX is not engine/plugins/shared
    bad_pattern = re.compile(r'^from error\.(?!engine|plugins|shared)(\w+)')
    
    for line_num, line in enumerate(lines, start=1):
        line = line.strip()
        match = bad_pattern.match(line)
        if match:
            module = match.group(1)
            reason = f"Deprecated import pattern - should use 'from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.engine.{module}' instead"
            violations.append((line_num, line, reason))
    
    return violations


def main() -> int:
    """Validate all Python files in the repository."""
    root = Path(__file__).resolve().parents[1]
    
    # Directories to check
    check_dirs = [
        root / "error",
        root / "tests",
        root / "scripts",
    ]
    
    all_violations = []
    
    for directory in check_dirs:
        if not directory.exists():
            continue
            
        for py_file in directory.rglob("*.py"):
            # Skip __pycache__ and similar
            if "__pycache__" in str(py_file):
                continue
            
            violations = check_file(py_file)
            if violations:
                all_violations.append((py_file, violations))
    
    # Report results
    if not all_violations:
        print("✅ All error imports follow the correct path structure!")
        return 0
    
    print("❌ Found incorrect error import patterns:\n")
    total_violations = 0
    
    for file_path, violations in all_violations:
        rel_path = file_path.relative_to(root)
        print(f"📁 {rel_path}")
        for line_num, line, reason in violations:
            print(f"   Line {line_num}: {line}")
            print(f"   ⚠️  {reason}\n")
            total_violations += 1
    
    print(f"\n❌ Total violations: {total_violations} across {len(all_violations)} files")
    print("\nFix these imports to use the section-based structure:")
    print("  - error.engine.*   (orchestration, state, plugins)")
    print("  - error.plugins.*  (individual validation plugins)")
    print("  - error.shared.*   (utilities, types, helpers)")
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
