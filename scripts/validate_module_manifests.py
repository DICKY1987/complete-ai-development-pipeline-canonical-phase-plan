#!/usr/bin/env python3
"""
Validate .ai-module-manifest files against schema.

Usage:
    python scripts/validate_module_manifests.py                # Report only
    python scripts/validate_module_manifests.py --strict       # Exit 1 on errors
    python scripts/validate_module_manifests.py --fix          # Auto-fix common issues
"""
# DOC_ID: DOC-SCRIPT-SCRIPTS-VALIDATE-MODULE-MANIFESTS-277

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Tuple

try:
    import yaml
    from jsonschema import Draft7Validator, ValidationError
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Install with: pip install pyyaml jsonschema")
    sys.exit(1)


def find_manifests(root: Path) -> List[Path]:
    """Find all .ai-module-manifest files."""
    return list(root.rglob(".ai-module-manifest"))


def load_schema(schema_path: Path) -> dict:
    """Load JSON schema."""
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_manifest(manifest_path: Path) -> Tuple[dict, str]:
    """Load manifest as YAML, return (data, error_msg)."""
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if data is None:
                return None, "Empty file"
            return data, None
    except yaml.YAMLError as e:
        return None, f"YAML parse error: {e}"
    except Exception as e:
        return None, f"Read error: {e}"


def validate_manifest(
    manifest_data: dict, schema: dict, manifest_path: Path
) -> List[str]:
    """Validate manifest against schema, return list of errors."""
    errors = []

    # Schema validation
    validator = Draft7Validator(schema)
    for error in validator.iter_errors(manifest_data):
        errors.append(
            f"  Schema: {error.message} at {'.'.join(str(p) for p in error.path)}"
        )

    # Custom validations
    if "entry_points" in manifest_data:
        for i, ep in enumerate(manifest_data["entry_points"]):
            if "file" in ep:
                # Check if file exists (relative to manifest location)
                file_path = manifest_path.parent / ep["file"]
                if not file_path.exists():
                    errors.append(f"  Entry point file not found: {ep['file']}")

    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate AI module manifests")
    parser.add_argument("--strict", action="store_true", help="Exit 1 on any errors")
    parser.add_argument("--fix", action="store_true", help="Auto-fix common issues")
    parser.add_argument(
        "--report-only", action="store_true", help="Report only (default)"
    )
    args = parser.parse_args()

    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    schema_path = project_root / "schema" / "ai_module_manifest.schema.json"

    if not schema_path.exists():
        print(f"❌ Schema not found: {schema_path}")
        sys.exit(1)

    # Load schema
    schema = load_schema(schema_path)
    print(f"✅ Loaded schema: {schema_path.name}")

    # Find manifests
    manifests = find_manifests(project_root)
    if not manifests:
        print("⚠️  No .ai-module-manifest files found")
        print(f"   Searched in: {project_root}")
        sys.exit(0)

    print(f"📋 Found {len(manifests)} manifest(s)")
    print()

    # Validate each
    total_errors = 0
    for manifest_path in sorted(manifests):
        rel_path = manifest_path.relative_to(project_root)
        print(f"Checking: {rel_path}")

        # Load
        data, load_error = load_manifest(manifest_path)
        if load_error:
            print(f"  ❌ {load_error}")
            total_errors += 1
            continue

        # Validate
        errors = validate_manifest(data, schema, manifest_path)
        if errors:
            print(f"  ❌ {len(errors)} error(s):")
            for err in errors:
                print(err)
            total_errors += len(errors)
        else:
            print(f"  ✅ Valid")
        print()

    # Summary
    print("=" * 60)
    if total_errors == 0:
        print("✅ All manifests valid!")
        sys.exit(0)
    else:
        print(f"❌ Found {total_errors} error(s) across {len(manifests)} manifest(s)")
        if args.strict:
            sys.exit(1)
        else:
            print("   Re-run with --strict to exit with code 1")
            sys.exit(0)


if __name__ == "__main__":
    main()
