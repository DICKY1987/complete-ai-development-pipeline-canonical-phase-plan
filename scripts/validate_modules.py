"""
Validate module manifests against schema.

Usage:
    python scripts/validate_modules.py [module_path]
    python scripts/validate_modules.py --all
"""
# DOC_ID: DOC-SCRIPT-SCRIPTS-VALIDATE-MODULES-243
# DOC_ID: DOC-SCRIPT-SCRIPTS-VALIDATE-MODULES-180

import json
import sys
from pathlib import Path
from typing import List, Tuple

try:
    from jsonschema import validate, ValidationError
except ImportError:
    print("❌ jsonschema not installed. Run: pip install jsonschema")
    sys.exit(1)


def load_schema() -> dict:
    """Load module manifest schema."""
    schema_path = Path(__file__).parent.parent / "schema" / "module.schema.json"
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema not found: {schema_path}")
    return json.loads(schema_path.read_text(encoding="utf-8"))


def find_manifests(root: Path = None) -> List[Path]:
    """Find all module.manifest.json files."""
    if root is None:
        root = Path(__file__).parent.parent

    manifests = []

    # Check modules/ directory
    modules_dir = root / "modules"
    if modules_dir.exists():
        for module_path in modules_dir.iterdir():
            if module_path.is_dir():
                manifest = module_path / "module.manifest.json"
                if manifest.exists():
                    manifests.append(manifest)

    # Check docs/examples/
    examples_dir = root / "docs" / "examples"
    if examples_dir.exists():
        for example in examples_dir.glob("*.manifest.*.json"):
            manifests.append(example)

    return manifests


def validate_manifest(manifest_path: Path, schema: dict) -> Tuple[bool, str]:
    """
    Validate a single manifest file.

    Returns:
        (is_valid, error_message)
    """
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"

    # Validate against schema
    try:
        validate(instance=manifest, schema=schema)
    except ValidationError as e:
        return False, f"Schema validation failed: {e.message}"

    # Additional consistency checks
    ulid_prefix = manifest.get("ulid_prefix", "")

    # Check artifact ULID consistency
    artifacts = manifest.get("artifacts", {})
    for artifact_type, artifact_list in artifacts.items():
        for artifact in artifact_list:
            path = artifact.get("path", "")
            if not path.startswith(ulid_prefix):
                return False, f"Artifact {path} does not start with ULID prefix {ulid_prefix}"

    # Check dependencies reference valid modules
    deps = manifest.get("dependencies", {}).get("modules", [])
    # TODO: Cross-validate module dependencies when we have module registry

    return True, "Valid"


def main():
    """Main validation entry point."""
    schema = load_schema()

    # Determine which manifests to validate
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            manifests = find_manifests()
        else:
            manifest_path = Path(sys.argv[1])
            if not manifest_path.exists():
                print(f"❌ Manifest not found: {manifest_path}")
                sys.exit(1)
            manifests = [manifest_path]
    else:
        manifests = find_manifests()

    if not manifests:
        print("⚠️  No module manifests found")
        print("Searched locations:")
        print("  - modules/**/module.manifest.json")
        print("  - docs/examples/*.manifest.*.json")
        sys.exit(0)

    # Validate each manifest
    print(f"Validating {len(manifests)} manifest(s)...\n")

    results = []
    for manifest_path in manifests:
        is_valid, message = validate_manifest(manifest_path, schema)
        results.append((manifest_path, is_valid, message))

        status = "✅" if is_valid else "❌"
        try:
            rel_path = manifest_path.relative_to(Path.cwd())
        except ValueError:
            rel_path = manifest_path
        print(f"{status} {rel_path}")
        if not is_valid:
            print(f"   {message}")

    # Summary
    print()
    valid_count = sum(1 for _, is_valid, _ in results if is_valid)
    total_count = len(results)

    if valid_count == total_count:
        print(f"✅ All {total_count} manifest(s) valid")
        sys.exit(0)
    else:
        print(f"❌ {total_count - valid_count}/{total_count} manifest(s) failed validation")
        sys.exit(1)


if __name__ == "__main__":
    main()
