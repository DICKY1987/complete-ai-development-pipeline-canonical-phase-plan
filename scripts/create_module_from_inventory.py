"""
Create Module from Inventory

Generates a complete module structure from MODULES_INVENTORY.yaml entry.

Usage:
    python scripts/create_module_from_inventory.py <module_id>

Example:
    python scripts/create_module_from_inventory.py error-plugin-ruff
"""

# DOC_ID: DOC-SCRIPT-SCRIPTS-CREATE-MODULE-FROM-INVENTORY-202
# DOC_ID: DOC-SCRIPT-SCRIPTS-CREATE-MODULE-FROM-INVENTORY-139

import shutil
import sys
from pathlib import Path

import yaml
from template_renderer import render_module_manifest


def find_module_in_inventory(module_id: str) -> dict:
    """Find module data in inventory."""
    inventory_path = Path("MODULES_INVENTORY.yaml")

    if not inventory_path.exists():
        raise FileNotFoundError(
            "MODULES_INVENTORY.yaml not found. Run generate_module_inventory.py first."
        )

    inventory = yaml.safe_load(inventory_path.read_text(encoding="utf-8"))

    for module in inventory["modules"]:
        if module["id"] == module_id:
            return module

    raise ValueError(f"Module '{module_id}' not found in inventory")


def create_module_structure(module_data: dict, use_symlinks: bool = False):
    """
    Create module directory structure.

    Args:
        module_data: Module data from inventory
        use_symlinks: If True, create symlinks to original files (Phase 2 approach)
                     If False, copy files (Phase 3 approach)
    """
    module_id = module_data["id"]
    ulid_prefix = module_data["ulid_prefix"]
    source_dir = Path(module_data["source_dir"])
    dest_dir = Path(f"modules/{module_id}")

    # Create module directory
    dest_dir.mkdir(parents=True, exist_ok=True)
    print(f"[+] Created {dest_dir}")

    # Generate and write manifest
    manifest_yaml = render_module_manifest(module_data)
    manifest_path = dest_dir / f"{ulid_prefix}_module.manifest.yaml"
    manifest_path.write_text(manifest_yaml, encoding="utf-8")
    print(f"[+] Generated {manifest_path}")

    # Copy or symlink source files
    files_migrated = 0
    for i, file_path in enumerate(module_data["files"]):
        src = Path(file_path)

        if not src.exists():
            print(f"⚠️  Source file not found: {src}")
            continue

        # Determine destination filename with ULID prefix
        dest_filename = f"{ulid_prefix}_{src.name}"
        dest_file = dest_dir / dest_filename

        if use_symlinks:
            # Create relative symlink
            relative_src = Path("..") / ".." / src
            dest_file.symlink_to(relative_src)
            print(f"[+] Symlinked {src} -> {dest_file}")
        else:
            # Copy file
            shutil.copy2(src, dest_file)
            print(f"[+] Copied {src} -> {dest_file}")

        files_migrated += 1

    # Create README
    readme_path = dest_dir / f"{ulid_prefix}_README.md"
    readme_content = f"""# {module_data['name']}

**Module ID**: {module_id}
**ULID Prefix**: {ulid_prefix}
**Layer**: {module_data['layer']}
**Source**: {module_data['source_dir']}

## Purpose

{module_data.get('name', 'Module documentation')}

## Files

{chr(10).join(f'- `{ulid_prefix}_{Path(f).name}`' for f in module_data['files'])}

## Dependencies

{', '.join(module_data.get('dependencies', [])) if module_data.get('dependencies') else 'None (independent module)'}

## Migration Status

- [x] Module structure created
- [x] Manifest generated
- [x] Files {'symlinked' if use_symlinks else 'migrated'}
- [ ] Tests added
- [ ] Documentation complete

---

**Created**: {Path(__file__).stat().st_mtime if Path(__file__).exists() else 'auto-generated'}
**Status**: Proof-of-concept module
"""
    readme_path.write_text(readme_content, encoding="utf-8")
    print(f"[+] Created {readme_path}")

    # Create .state directory (for modules that need state)
    state_dir = dest_dir / ".state"
    state_dir.mkdir(exist_ok=True)

    state_file = state_dir / "current.json"
    state_file.write_text(
        '{"status": "active", "last_updated": null}', encoding="utf-8"
    )
    print(f"[+] Created {state_dir}")

    return files_migrated


def validate_module(module_id: str) -> bool:
    """Validate created module using validation script."""
    manifest_path = Path(f"modules/{module_id}") / f"*_module.manifest.yaml"

    # Find manifest
    manifests = list(Path(f"modules/{module_id}").glob("*_module.manifest.yaml"))

    if not manifests:
        print(f"[!] No manifest found in modules/{module_id}")
        return False

    # Note: We'll validate after converting YAML to JSON
    print(f"[+] Module structure created, manual validation recommended")
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/create_module_from_inventory.py <module_id>")
        print(
            "\nExample: python scripts/create_module_from_inventory.py error-plugin-ruff"
        )
        sys.exit(1)

    module_id = sys.argv[1]
    use_symlinks = "--symlinks" in sys.argv  # Phase 2 mode

    print(f"Creating module: {module_id}")
    print(f"Mode: {'Symlinks (Phase 2)' if use_symlinks else 'Copy (Phase 3)'}\n")

    try:
        # Find module in inventory
        module_data = find_module_in_inventory(module_id)

        # Create module structure
        files_migrated = create_module_structure(module_data, use_symlinks=use_symlinks)

        # Validate
        validate_module(module_id)

        print(f"\nModule created successfully!")
        print(f"   Location: modules/{module_id}/")
        print(f"   Files: {files_migrated}")
        print(f"   ULID: {module_data['ulid_prefix']}")

        print(f"\nNext steps:")
        print(
            f"   1. Review modules/{module_id}/{module_data['ulid_prefix']}_module.manifest.yaml"
        )
        print(
            f"   2. Validate: python scripts/validate_modules.py (after converting to JSON)"
        )
        print(f"   3. Test: Import and verify functionality")

    except Exception as e:
        print(f"\n[!] Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
