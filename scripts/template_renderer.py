"""
Template Renderer - Variable expansion for module templates

Usage:
    from template_renderer import render_template

    context = {
        'module_id': 'core-state',
        'ulid_prefix': '010003',
        'purpose': 'Database operations and state management'
    }

    output = render_template('templates/module.manifest.template.yaml', context)
"""

# DOC_ID: DOC-SCRIPT-SCRIPTS-TEMPLATE-RENDERER-234
# DOC_ID: DOC-SCRIPT-SCRIPTS-TEMPLATE-RENDERER-171

from pathlib import Path
from typing import Dict, Any, List
import re
from datetime import datetime


def render_template(template_path: str, context: Dict[str, Any]) -> str:
    """
    Render template with variable substitution.

    Supports:
    - Simple variables: {var_name}
    - List expansion: {list_var} where list_var is ['a', 'b'] -> "['a', 'b']"

    Args:
        template_path: Path to template file
        context: Dictionary of variables to substitute

    Returns:
        Rendered template string
    """
    template_file = Path(template_path)
    if not template_file.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    template = template_file.read_text(encoding="utf-8")

    # Render template
    result = template
    for key, value in context.items():
        placeholder = f"{{{key}}}"

        # Convert value to string representation
        if isinstance(value, list):
            if all(isinstance(item, str) for item in value):
                # List of strings - render as YAML list
                if value:
                    value_str = "\n".join(f'  - "{item}"' for item in value)
                else:
                    value_str = "[]"
            else:
                value_str = str(value)
        elif isinstance(value, dict):
            value_str = str(value)
        else:
            value_str = str(value)

        result = result.replace(placeholder, value_str)

    return result


def generate_code_artifacts_yaml(files: List[str], ulid_prefix: str) -> str:
    """
    Generate YAML code artifacts section from file list.

    Args:
        files: List of source file paths
        ulid_prefix: Module ULID prefix

    Returns:
        YAML-formatted code artifacts
    """
    artifacts = []

    for i, file_path in enumerate(files):
        file_path_obj = Path(file_path)
        file_name = file_path_obj.name

        # Generate unique ULID for artifact (increment last chars)
        artifact_ulid = f"{ulid_prefix}{i:020X}"

        # Determine new file name with ULID prefix
        new_name = f"{ulid_prefix}_{file_name}"

        artifact = {
            "path": new_name,
            "ulid": artifact_ulid,
            "entry_point": i == 0,  # First file is entry point
        }

        # Format as YAML
        artifacts.append(
            f"""    - path: "{artifact['path']}"
      ulid: "{artifact['ulid']}"
      entry_point: {str(artifact['entry_point']).lower()}"""
        )

    return "\n".join(artifacts) if artifacts else "    []"


def generate_import_patterns_yaml(
    module_id: str, files: List[str], ulid_prefix: str
) -> str:
    """
    Generate YAML import patterns section.

    Args:
        module_id: Module identifier
        files: List of source file paths
        ulid_prefix: Module ULID prefix

    Returns:
        YAML-formatted import patterns
    """
    patterns = []

    for file_path in files[:3]:  # First 3 files only
        file_path_obj = Path(file_path)
        file_name = file_path_obj.stem  # Without extension

        # Old import pattern
        old_import = file_path_obj.as_posix().replace("/", ".").replace(".py", "")

        # New import pattern
        new_module_path = module_id.replace("-", "_")
        new_file = f"{ulid_prefix}_{file_name}"

        pattern = f"""  - pattern: "from {old_import} import"
    description: "Import from {file_name}"
    deprecated: false"""

        patterns.append(pattern)

    return "\n".join(patterns) if patterns else "  []"


def render_module_manifest(module_data: Dict[str, Any]) -> str:
    """
    Render complete module manifest from inventory data.

    Args:
        module_data: Module data from MODULES_INVENTORY.yaml

    Returns:
        Rendered manifest YAML
    """
    ulid_prefix = module_data["ulid_prefix"]
    files = module_data.get("files", [])

    # Build context
    context = {
        "module_id": module_data["id"],
        "ulid_prefix": ulid_prefix,
        "purpose": module_data.get("name", "Module purpose"),
        "layer": module_data["layer"],
        "dependencies": module_data.get("dependencies", []),
        "created_date": datetime.now().isoformat() + "Z",
        "code_artifacts": generate_code_artifacts_yaml(files, ulid_prefix),
        "import_patterns": generate_import_patterns_yaml(
            module_data["id"], files, ulid_prefix
        ),
    }

    return render_template("templates/module.manifest.template.yaml", context)


if __name__ == "__main__":
    # Test with sample data
    test_context = {
        "module_id": "test-module",
        "ulid_prefix": "01TEST",
        "purpose": "Test module",
        "layer": "domain",
        "dependencies": ["dep1", "dep2"],
        "created_date": "2025-11-25T22:00:00Z",
        "code_artifacts": '    - path: "01TEST_test.py"\n      ulid: "01TEST00000000000000000001"',
        "import_patterns": '  - pattern: "from test import"\n    description: "Test import"',
    }

    result = render_template("templates/module.manifest.template.yaml", test_context)
    print(result)
