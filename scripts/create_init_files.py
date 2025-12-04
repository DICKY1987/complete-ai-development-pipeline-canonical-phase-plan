"""
Create __init__.py files for modules to enable imports.

Each module's __init__.py will re-export its contents with clean names.
"""

# DOC_ID: DOC-SCRIPT-SCRIPTS-CREATE-INIT-FILES-199
# DOC_ID: DOC-SCRIPT-SCRIPTS-CREATE-INIT-FILES-136

from pathlib import Path
import yaml


def create_init_files():
    """Create __init__.py for each module."""
    modules_dir = Path("modules")
    inventory = yaml.safe_load(Path("MODULES_INVENTORY.yaml").read_text())

    for module in inventory["modules"]:
        module_id = module["id"]
        ulid_prefix = module["ulid_prefix"]
        module_dir = modules_dir / module_id

        if not module_dir.exists():
            continue

        # Find all Python files with ULID prefix
        py_files = list(module_dir.glob(f"{ulid_prefix}_*.py"))

        if not py_files:
            continue

        # Generate __init__.py content
        init_content = f'"""Module: {module_id}"""\n\n'

        for py_file in sorted(py_files):
            if py_file.name.endswith("_README.md") or py_file.name.endswith(
                ".manifest.yaml"
            ):
                continue

            # Import from ULID file
            module_name = py_file.stem  # e.g., "010003_db"

            # Re-export with clean name (remove ULID prefix)
            clean_name = (
                module_name.split("_", 1)[1] if "_" in module_name else module_name
            )

            init_content += f"from .{module_name} import *\n"

        # Write __init__.py
        init_file = module_dir / "__init__.py"
        init_file.write_text(init_content, encoding="utf-8")
        print(f"Created {module_id}/__init__.py")


if __name__ == "__main__":
    create_init_files()
