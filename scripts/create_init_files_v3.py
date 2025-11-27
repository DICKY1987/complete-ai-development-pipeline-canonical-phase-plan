"""
Create __init__.py files (v3) - Using importlib for ULID files.

Since Python identifiers can't start with digits, we use importlib
to dynamically import ULID-prefixed files and re-export their symbols.

Usage:
    python scripts/create_init_files_v3.py --all --execute
"""

from pathlib import Path
import argparse
import textwrap
import yaml


def create_init_file_v3(module_dir: Path, module_id: str, ulid_prefix: str, layer: str) -> str:
    """Create __init__.py content using importlib for ULID files."""
    prefixes = [ulid_prefix]
    if ulid_prefix and not ulid_prefix.startswith("m"):
        prefixes.append(f"m{ulid_prefix}")
    py_files = []
    for prefix in prefixes:
        py_files.extend(module_dir.glob(f"{prefix}_*.py"))
    py_files = sorted(set(py_files))

    def sort_key(path: Path):
        stem = path.stem
        slug = stem.split("_", 1)[1] if "_" in stem else stem
        if slug.startswith("db") or slug.startswith("pipeline_service") or slug.startswith("error_pipeline_service"):
            pri = 0
        elif slug.startswith("crud") or slug.startswith("error_pipeline_cli"):
            pri = 1
        else:
            pri = 2
        return (pri, slug)

    code_files = sorted([
        f for f in py_files
        if not f.name.endswith(('_README.md', '.manifest.yaml', '.manifest.json'))
    ], key=sort_key)
    if not code_files:
        return None

    module_import_name = module_id.replace('-', '_')
    ulid_lines = "\n".join(f'    "{py_file.stem}",' for py_file in code_files)

    template = """\
    \"\"\"Module: {module_id}

    ULID Prefix: {ulid_prefix}
    Layer: {layer}
    Files: {file_count}

    This module dynamically imports ULID-prefixed files and re-exports their symbols.
    Import from this module:

        from modules.{module_import_name} import function_name  # ?
    \"\"\"

    import importlib
    import sys
    from pathlib import Path

    # Module metadata
    __module_id__ = "{module_id}"
    __ulid_prefix__ = "{ulid_prefix}"
    __layer__ = "{layer}"
    module_import_name = "{module_import_name}"

    # Dynamically import all ULID-prefixed files and re-export
    _module_dir = Path(__file__).parent
    _ulid_files = [
{ulid_lines}
    ]

    _pending = list(_ulid_files)
    _errors = {{stem: None for stem in _pending}}

    while _pending:
        _progress = False
        for _file_stem in list(_pending):
            _module_path = f"modules.{module_import_name}.{{_file_stem}}"
            try:
                _mod = importlib.import_module(_module_path)

                # Re-export all public symbols
                if hasattr(_mod, '__all__'):
                    for _name in _mod.__all__:
                        globals()[_name] = getattr(_mod, _name)
                else:
                    # Export everything that doesn't start with underscore
                    for _name in dir(_mod):
                        if not _name.startswith('_'):
                            globals()[_name] = getattr(_mod, _name)
                # Alias without ULID prefix to support relative imports (e.g., db_sqlite)
                if "_" in _file_stem:
                    _alias = _file_stem.split("_", 1)[1]
                    sys.modules[f"modules.{module_import_name}.{{_alias}}"] = _mod
                    globals()[_alias] = _mod
                _pending.remove(_file_stem)
                _progress = True
            except Exception as e:
                _errors[_file_stem] = e
                continue
        if not _progress:
            for _file_stem in _pending:
                _module_path = f"modules.{module_import_name}.{{_file_stem}}"
                _err = _errors.get(_file_stem)
                print(f"Warning: Could not import {{_module_path}}: {{_err}}", file=sys.stderr)
            break
    """

    return textwrap.dedent(template.format(
        module_id=module_id,
        ulid_prefix=ulid_prefix,
        layer=layer,
        file_count=len(code_files),
        module_import_name=module_import_name,
        ulid_lines=ulid_lines,
    ))


def main():
    parser = argparse.ArgumentParser(description="Create __init__.py files (v3 - importlib)")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--module", help="Process specific module")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--execute", action="store_true")

    args = parser.parse_args()
    dry_run = not args.execute

    print("Create __init__.py Files (v3 - importlib)")
    print(f"Mode: {'DRY-RUN' if dry_run else 'EXECUTE'}\n")

    inventory = yaml.safe_load(Path("MODULES_INVENTORY.yaml").read_text())

    if args.all:
        modules = inventory["modules"]
    elif args.module:
        modules = [m for m in inventory["modules"] if m["id"] == args.module]
        if not modules:
            print(f"Module '{args.module}' not found")
            return 1
    else:
        print("Specify --all or --module")
        return 1

    created = 0
    skipped = 0

    for module in modules:
        module_id = module["id"]
        ulid_prefix = module["ulid_prefix"]
        layer = module.get("layer", "unknown")

        module_dir = Path("modules") / module_id
        if not module_dir.exists():
            print(f"[SKIP] {module_id} - directory not found")
            skipped += 1
            continue

        content = create_init_file_v3(module_dir, module_id, ulid_prefix, layer)
        if not content:
            print(f"[SKIP] {module_id} - no Python files")
            skipped += 1
            continue

        init_file = module_dir / "__init__.py"
        if dry_run:
            print(f"[DRY-RUN] {module_id} ({len(content)} bytes)")
        else:
            init_file.write_text(content, encoding="utf-8")
            print(f"[CREATED] {module_id} ({len(content)} bytes)")
            created += 1

    print(f"\n{'='*60}")
    print(f"Created: {created}, Skipped: {skipped}")

    if dry_run:
        print("\nTo apply: --execute")
    else:
        print("\nValidate: python -m compileall modules/ -q")


if __name__ == "__main__":
    import sys

    sys.exit(main() or 0)
