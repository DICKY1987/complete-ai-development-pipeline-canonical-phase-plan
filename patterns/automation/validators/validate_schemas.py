#!/usr/bin/env python3
"""
Schema Validation Script for Pattern Registry
Validates all JSON schemas and example instances

DOC_ID: DOC-PAT-VALIDATORS-VALIDATE-SCHEMAS-001
Gap: GAP-PATREG-006
Pattern: EXEC-002 (Batch Validation)
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Tuple

try:
    import jsonschema
except ImportError:
    print("ERROR: jsonschema library not installed")
    print("Install with: pip install jsonschema")
    sys.exit(1)


def validate_all_schemas(patterns_dir: Path = None) -> Tuple[List[Dict], List[Dict]]:
    """
    Validate all schemas and examples

    Returns:
        Tuple of (errors, warnings)
    """
    if patterns_dir is None:
        patterns_dir = Path(__file__).parent.parent.parent

    schemas_dir = patterns_dir / "schemas"
    examples_dir = patterns_dir / "examples"

    errors = []
    warnings = []

    # Validate JSON syntax for all schema files
    print("Validating schema JSON syntax...")
    schema_count = 0
    for schema_file in schemas_dir.glob("*.schema.json"):
        schema_count += 1
        try:
            with open(schema_file, "r", encoding="utf-8") as f:
                json.load(f)
            print(f"  ✓ {schema_file.name}")
        except json.JSONDecodeError as e:
            errors.append(
                {"type": "json_syntax", "file": str(schema_file), "error": str(e)}
            )
            print(f"  ✗ {schema_file.name}: {e}")

    print(f"\nValidated {schema_count} schema files")

    # Validate examples against their schemas
    print("\nValidating examples against schemas...")
    example_count = 0
    validated_count = 0

    if examples_dir.exists():
        for example_dir in examples_dir.iterdir():
            if not example_dir.is_dir():
                continue

            pattern_name = example_dir.name
            schema_file = schemas_dir / f"{pattern_name}.schema.json"

            if not schema_file.exists():
                warnings.append(
                    {
                        "type": "missing_schema",
                        "pattern": pattern_name,
                        "message": f"No schema found for examples in {pattern_name}/",
                    }
                )
                continue

            # Load schema
            try:
                with open(schema_file, "r", encoding="utf-8") as f:
                    schema = json.load(f)
            except Exception as e:
                errors.append(
                    {
                        "type": "schema_load_error",
                        "file": str(schema_file),
                        "error": str(e),
                    }
                )
                continue

            # Validate each example instance
            for instance_file in example_dir.glob("*.json"):
                example_count += 1
                try:
                    with open(instance_file, "r", encoding="utf-8") as f:
                        instance = json.load(f)

                    jsonschema.validate(instance, schema)
                    validated_count += 1
                    print(f"  ✓ {pattern_name}/{instance_file.name}")

                except json.JSONDecodeError as e:
                    errors.append(
                        {
                            "type": "instance_json_error",
                            "file": str(instance_file),
                            "error": str(e),
                        }
                    )
                    print(f"  ✗ {pattern_name}/{instance_file.name}: JSON syntax error")

                except jsonschema.ValidationError as e:
                    errors.append(
                        {
                            "type": "schema_validation",
                            "file": str(instance_file),
                            "error": e.message,
                            "path": list(e.path),
                        }
                    )
                    print(f"  ✗ {pattern_name}/{instance_file.name}: {e.message}")

                except Exception as e:
                    errors.append(
                        {
                            "type": "unknown_error",
                            "file": str(instance_file),
                            "error": str(e),
                        }
                    )
                    print(f"  ✗ {pattern_name}/{instance_file.name}: {e}")

    print(f"\nValidated {validated_count}/{example_count} example instances")

    return errors, warnings


def main():
    """CLI entry point"""
    print("=" * 70)
    print("Pattern Schema Validation")
    print("=" * 70)
    print()

    errors, warnings = validate_all_schemas()

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()

    if warnings:
        print(f"⚠️  {len(warnings)} warnings:")
        for warning in warnings:
            print(
                f"  - {warning['type']}: {warning.get('message', warning.get('pattern'))}"
            )
        print()

    if errors:
        print(f"✗ {len(errors)} errors found:")
        for error in errors:
            print(f"  - {error['type']}: {error['file']}")
            print(f"    {error['error']}")
        print()
        print("VALIDATION FAILED")
        return 1
    else:
        print("✓ All schemas and examples valid")
        return 0


if __name__ == "__main__":
    sys.exit(main())
