"""
Ground Truth Validation - Phase 1 Checks

Validates module-centric migration progress with programmatic verification.
No hallucination - all checks use exit codes and file system verification.

Usage:
    python scripts/validate_migration_phase1.py
"""

# DOC_ID: DOC-SCRIPT-SCRIPTS-VALIDATE-MIGRATION-PHASE1-242
# DOC_ID: DOC-SCRIPT-SCRIPTS-VALIDATE-MIGRATION-PHASE1-179

import subprocess
import sys
from pathlib import Path
from typing import List, Tuple
import yaml


class ValidationGate:
    """Base class for validation gates."""

    def __init__(self, name: str):
        self.name = name

    def check(self) -> Tuple[bool, str]:
        """Return (passed, message)."""
        raise NotImplementedError


class InventoryExistsGate(ValidationGate):
    """Verify MODULES_INVENTORY.yaml exists and is valid."""

    def __init__(self):
        super().__init__("Inventory File Exists")

    def check(self) -> Tuple[bool, str]:
        inventory_path = Path("MODULES_INVENTORY.yaml")

        if not inventory_path.exists():
            return False, "MODULES_INVENTORY.yaml not found"

        try:
            data = yaml.safe_load(inventory_path.read_text(encoding="utf-8"))

            if "modules" not in data:
                return False, "Inventory missing 'modules' key"

            module_count = len(data["modules"])
            return True, f"Inventory valid with {module_count} modules"

        except yaml.YAMLError as e:
            return False, f"Invalid YAML: {e}"


class SchemaValidGate(ValidationGate):
    """Verify module.schema.json is valid JSON schema."""

    def __init__(self):
        super().__init__("Module Schema Valid")

    def check(self) -> Tuple[bool, str]:
        schema_path = Path("schema/module.schema.json")

        if not schema_path.exists():
            return False, "schema/module.schema.json not found"

        try:
            import json

            schema = json.loads(schema_path.read_text(encoding="utf-8"))

            # Check required top-level keys
            required_keys = ["$schema", "type", "properties"]
            missing = [k for k in required_keys if k not in schema]

            if missing:
                return False, f"Schema missing keys: {missing}"

            return True, "Schema valid"

        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {e}"


class TemplatesExistGate(ValidationGate):
    """Verify required templates exist."""

    def __init__(self):
        super().__init__("Templates Exist")

    def check(self) -> Tuple[bool, str]:
        required_templates = ["templates/module.manifest.template.yaml"]

        missing = []
        for template in required_templates:
            if not Path(template).exists():
                missing.append(template)

        if missing:
            return False, f"Missing templates: {missing}"

        return True, f"All {len(required_templates)} templates present"


class ScriptsExecutableGate(ValidationGate):
    """Verify required scripts are present and have correct structure."""

    def __init__(self):
        super().__init__("Scripts Present")

    def check(self) -> Tuple[bool, str]:
        required_scripts = [
            "scripts/generate_module_inventory.py",
            "scripts/template_renderer.py",
            "scripts/validate_modules.py",
        ]

        missing = []
        for script in required_scripts:
            if not Path(script).exists():
                missing.append(script)

        if missing:
            return False, f"Missing scripts: {missing}"

        return True, f"All {len(required_scripts)} scripts present"


class NoTODOsGate(ValidationGate):
    """Verify no TODO markers in critical files (incomplete implementation)."""

    def __init__(self):
        super().__init__("No TODO Markers")

    def check(self) -> Tuple[bool, str]:
        # Check key scripts and schema
        critical_files = [
            "scripts/generate_module_inventory.py",
            "scripts/template_renderer.py",
            "schema/module.schema.json",
        ]

        todos_found = []
        for file_path in critical_files:
            path = Path(file_path)
            if path.exists():
                content = path.read_text(encoding="utf-8")
                if "# TODO" in content or "// TODO" in content:
                    todos_found.append(file_path)

        if todos_found:
            return False, f"TODOs found in: {todos_found}"

        return True, "No TODO markers in critical files"


class PythonSyntaxGate(ValidationGate):
    """Verify all Python scripts have valid syntax."""

    def __init__(self):
        super().__init__("Python Syntax Valid")

    def check(self) -> Tuple[bool, str]:
        python_files = [
            "scripts/generate_module_inventory.py",
            "scripts/template_renderer.py",
            "scripts/validate_modules.py",
        ]

        errors = []
        for py_file in python_files:
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", py_file],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                errors.append(f"{py_file}: {result.stderr}")

        if errors:
            return False, f"Syntax errors: {errors}"

        return True, f"All {len(python_files)} scripts have valid syntax"


class ModulesDirectoryGate(ValidationGate):
    """Check if modules/ directory structure is starting."""

    def __init__(self):
        super().__init__("Modules Directory Status")

    def check(self) -> Tuple[bool, str]:
        modules_dir = Path("modules")

        if not modules_dir.exists():
            return True, "modules/ not yet created (expected for Phase 1)"

        # If it exists, count modules
        module_count = len([d for d in modules_dir.iterdir() if d.is_dir()])
        return True, f"modules/ exists with {module_count} modules"


def run_validation() -> int:
    """
    Run all validation gates.

    Returns:
        Exit code (0 = success, 1 = failure)
    """
    gates: List[ValidationGate] = [
        InventoryExistsGate(),
        SchemaValidGate(),
        TemplatesExistGate(),
        ScriptsExecutableGate(),
        NoTODOsGate(),
        PythonSyntaxGate(),
        ModulesDirectoryGate(),
    ]

    print("🔍 Running Phase 1 Validation Gates...\n")

    results = []
    for gate in gates:
        try:
            passed, message = gate.check()
            results.append((gate.name, passed, message))

            status = "✅" if passed else "❌"
            print(f"{status} {gate.name}")
            print(f"   {message}")
        except Exception as e:
            results.append((gate.name, False, f"Exception: {e}"))
            print(f"❌ {gate.name}")
            print(f"   Exception: {e}")

    # Summary
    print("\n" + "=" * 60)
    passed_count = sum(1 for _, passed, _ in results if passed)
    total_count = len(results)

    if passed_count == total_count:
        print(f"✅ ALL {total_count} VALIDATION GATES PASSED")
        print("\nPhase 1 Status: COMPLETE")
        print("Next: Create first proof-of-concept module")
        return 0
    else:
        print(f"❌ {total_count - passed_count}/{total_count} GATES FAILED")
        print("\nFix failures before proceeding.")
        return 1


if __name__ == "__main__":
    exit_code = run_validation()
    sys.exit(exit_code)
