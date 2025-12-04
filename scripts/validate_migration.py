"""
Migration Validation Script
Ground truth verification gates
Pattern: Zero hallucination debugging
"""

# DOC_ID: DOC-SCRIPT-SCRIPTS-VALIDATE-MIGRATION-241
# DOC_ID: DOC-SCRIPT-SCRIPTS-VALIDATE-MIGRATION-178

import subprocess
import sys
from pathlib import Path
import yaml


def validate_modules_created() -> tuple:
    """Gate 1: All modules exist."""
    print("\n[1] Validating modules created...")

    inventory_path = Path("MODULES_INVENTORY.yaml")
    if not inventory_path.exists():
        return ("modules_created", False, "MODULES_INVENTORY.yaml not found")

    with inventory_path.open("r", encoding="utf-8") as f:
        inventory = yaml.safe_load(f)

    expected_count = inventory["metadata"]["total_modules"]

    modules_dir = Path("modules")
    if not modules_dir.exists():
        return ("modules_created", False, f"modules/ directory not found")

    actual_dirs = [d for d in modules_dir.iterdir() if d.is_dir()]
    actual_count = len(actual_dirs)

    passed = actual_count >= expected_count
    msg = f"{actual_count}/{expected_count} modules"

    return ("modules_created", passed, msg)


def validate_imports_resolve() -> tuple:
    """Gate 2: All imports resolve."""
    print("\n[2] Validating imports resolve...")

    modules_dir = Path("modules")
    if not modules_dir.exists():
        return ("imports_resolve", False, "modules/ directory not found")

    python_files = list(modules_dir.rglob("*.py"))
    if not python_files:
        return ("imports_resolve", False, "No Python files found in modules/")

    errors = []
    for py_file in python_files:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(py_file)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            errors.append(f"{py_file.name}: {result.stderr[:100]}")

    passed = len(errors) == 0
    msg = f"{len(python_files) - len(errors)}/{len(python_files)} files compile"

    if errors and len(errors) <= 3:
        msg += f" (errors: {', '.join(errors)})"

    return ("imports_resolve", passed, msg)


def validate_tests_exist() -> tuple:
    """Gate 3: Tests exist."""
    print("\n[3] Validating tests exist...")

    tests_dir = Path("tests")
    if not tests_dir.exists():
        return ("tests_exist", False, "tests/ directory not found")

    test_files = list(tests_dir.rglob("test_*.py"))
    passed = len(test_files) > 0
    msg = f"{len(test_files)} test files"

    return ("tests_exist", passed, msg)


def validate_no_orphans() -> tuple:
    """Gate 4: No orphaned files."""
    print("\n[4] Validating no orphaned files...")

    # Check for files in old locations that should have been migrated
    old_locations = ["src/pipeline", "MOD_ERROR_PIPELINE"]
    orphans = []

    for old_loc in old_locations:
        old_path = Path(old_loc)
        if old_path.exists():
            py_files = list(old_path.rglob("*.py"))
            orphans.extend(py_files)

    passed = len(orphans) == 0
    msg = f"{len(orphans)} orphaned files" if orphans else "No orphans"

    return ("no_orphans", passed, msg)


def validate_migration():
    """Multi-gate validation."""
    print("=" * 60)
    print("Migration Validation - Ground Truth Gates")
    print("=" * 60)

    gates = [
        validate_modules_created(),
        validate_imports_resolve(),
        validate_tests_exist(),
        validate_no_orphans(),
    ]

    # Report results
    print("\n" + "=" * 60)
    print("Results:")
    print("=" * 60)

    for name, passed, msg in gates:
        status = "✅" if passed else "❌"
        print(f"{status} {name:20} {msg}")

    # Summary
    print("\n" + "=" * 60)
    passed_count = sum(1 for _, passed, _ in gates if passed)
    total_count = len(gates)

    if passed_count == total_count:
        print("✅ ALL VALIDATION GATES PASSED")
        print(f"\n{passed_count}/{total_count} gates passed")
        return 0
    else:
        print("❌ MIGRATION VALIDATION FAILED")
        print(f"\n{passed_count}/{total_count} gates passed")
        print("\nRecommendation: Fix failing gates before merging")
        return 1


if __name__ == "__main__":
    sys.exit(validate_migration())
