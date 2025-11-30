"""
Anti-Pattern Guard Enforcement Script
Prevents 79h of waste during module migration
"""
DOC_ID: DOC-SCRIPT-SCRIPTS-ENFORCE-GUARDS-208
DOC_ID: DOC-SCRIPT-SCRIPTS-ENFORCE-GUARDS-145

import subprocess
import sys
from pathlib import Path
import yaml

def check_incomplete_implementation() -> list:
    """Check for incomplete implementations (TODOs, pass statements)."""
    violations = []
    
    # Check in modules directory
    modules_path = Path("modules")
    if modules_path.exists():
        todo_count = 0
        for py_file in modules_path.rglob("*.py"):
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            todo_count += content.count("# TODO")
        
        if todo_count > 0:
            violations.append(f"Incomplete implementation: {todo_count} TODOs found in modules/")
    
    return violations

def check_silent_failures() -> list:
    """Check for subprocess.run without check=True."""
    violations = []
    
    python_files = list(Path(".").rglob("*.py"))
    for py_file in python_files:
        if "legacy" in str(py_file) or ".venv" in str(py_file):
            continue
            
        content = py_file.read_text(encoding='utf-8', errors='ignore')
        if "subprocess.run(" in content and "check=" not in content:
            violations.append(f"Silent failure risk in {py_file}: subprocess.run without check=True")
    
    return violations

def check_unused_worktrees() -> list:
    """Check for unused worktrees."""
    violations = []
    
    result = subprocess.run(
        ["git", "worktree", "list"],
        capture_output=True,
        text=True
    )
    
    worktrees = result.stdout.splitlines()
    if len(worktrees) > 5:  # Main + 4 migration worktrees
        violations.append(f"Too many worktrees: {len(worktrees)} (max recommended: 5)")
    
    return violations

def check_configuration_drift() -> list:
    """Check for hardcoded paths not from config."""
    violations = []
    
    python_files = list(Path("scripts").rglob("*.py"))
    for py_file in python_files:
        content = py_file.read_text(encoding='utf-8', errors='ignore')
        
        # Simple heuristic: absolute paths without config
        if ('Path("C:\\' in content or 'Path("/home/' in content) and 'config' not in content.lower():
            violations.append(f"Hardcoded path in {py_file}")
    
    return violations

def check_guards():
    """Enforce anti-pattern guards."""
    print("🛡️  Checking Anti-Pattern Guards...")
    print("=" * 60)
    
    all_violations = []
    
    # Guard 1: Incomplete Implementation
    print("\n1. Incomplete Implementation Guard...")
    violations = check_incomplete_implementation()
    if violations:
        all_violations.extend(violations)
        for v in violations:
            print(f"   ❌ {v}")
    else:
        print("   ✅ No incomplete implementations found")
    
    # Guard 2: Silent Failures
    print("\n2. Silent Failures Guard...")
    violations = check_silent_failures()
    if violations:
        all_violations.extend(violations)
        for v in violations:
            print(f"   ⚠️  {v}")
    else:
        print("   ✅ No silent failures detected")
    
    # Guard 3: Framework Over-Engineering
    print("\n3. Framework Over-Engineering Guard...")
    violations = check_unused_worktrees()
    if violations:
        all_violations.extend(violations)
        for v in violations:
            print(f"   ⚠️  {v}")
    else:
        print("   ✅ Worktree count within limits")
    
    # Guard 4: Configuration Drift
    print("\n4. Configuration Drift Guard...")
    violations = check_configuration_drift()
    if violations:
        all_violations.extend(violations)
        for v in violations:
            print(f"   ⚠️  {v}")
    else:
        print("   ✅ No hardcoded paths detected")
    
    # Summary
    print("\n" + "=" * 60)
    if all_violations:
        print(f"❌ FOUND {len(all_violations)} ANTI-PATTERN VIOLATIONS")
        print("\nRecommendation: Fix violations before proceeding")
        return 1
    else:
        print("✅ ALL GUARDS PASSED")
        print("\nSafe to proceed with migration")
        return 0

if __name__ == "__main__":
    sys.exit(check_guards())
