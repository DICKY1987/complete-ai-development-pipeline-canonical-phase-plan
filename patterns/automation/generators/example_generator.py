#!/usr/bin/env python3
"""
Example Instance Generator
Generate example JSON instances from JSON schemas

DOC_ID: DOC-PAT-GENERATORS-EXAMPLE-GENERATOR-001
Gap: GAP-PATREG-011
Pattern: EXEC-009 (Meta-Execution)
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict


def generate_minimal(schema: Dict) -> Dict:
    """Generate minimal instance (required fields only)"""
    instance = {}

    if "properties" in schema:
        for prop, prop_schema in schema["properties"].items():
            if "required" in schema and prop in schema["required"]:
                instance[prop] = generate_value(prop_schema)

    return instance


def generate_full(schema: Dict) -> Dict:
    """Generate full instance (all fields)"""
    instance = {}

    if "properties" in schema:
        for prop, prop_schema in schema["properties"].items():
            instance[prop] = generate_value(prop_schema)

    return instance


def generate_test(schema: Dict) -> Dict:
    """Generate test instance (CI-friendly, deterministic)"""
    instance = generate_minimal(schema)
    instance["_test"] = True
    return instance


def generate_value(prop_schema: Dict) -> Any:
    """Generate value based on property schema"""
    prop_type = prop_schema.get("type", "string")

    if "const" in prop_schema:
        return prop_schema["const"]

    if "default" in prop_schema:
        return prop_schema["default"]

    type_defaults = {
        "string": "example_value",
        "number": 42,
        "integer": 42,
        "boolean": True,
        "array": [],
        "object": {},
    }

    return type_defaults.get(prop_type, "value")


def main():
    """CLI entry point"""
    if len(sys.argv) < 3:
        print("Usage: python example_generator.py <schema_path> <output_dir>")
        sys.exit(1)

    schema_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])

    if not schema_path.exists():
        print(f"Error: Schema file not found: {schema_path}")
        sys.exit(1)

    schema = json.loads(schema_path.read_text())

    # Generate instances
    minimal = generate_minimal(schema)
    full = generate_full(schema)
    test = generate_test(schema)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write instances
    (output_dir / "instance_minimal.json").write_text(json.dumps(minimal, indent=2))
    (output_dir / "instance_full.json").write_text(json.dumps(full, indent=2))
    (output_dir / "instance_test.json").write_text(json.dumps(test, indent=2))

    print(f"✓ Generated 3 example instances in {output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
