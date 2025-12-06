"""Config validation script using JSON Schema."""
import json
import sys
from pathlib import Path
import jsonschema


SCHEMAS = {
    "tool_profiles": {
        "type": "object",
        "patternProperties": {
            ".*": {
                "type": "object",
                "required": ["command", "timeout_seconds"],
                "properties": {
                    "command": {"type": "string"},
                    "args": {"type": "array"},
                    "timeout_seconds": {"type": "number"}
                }
            }
        }
    }
}


def validate_config(config_path: Path, schema_name: str):
    """Validate config file against schema."""
    try:
        with open(config_path, encoding='utf-8') as f:
            data = json.load(f)
        
        if schema_name in SCHEMAS:
            jsonschema.validate(data, SCHEMAS[schema_name])
        
        print(f"✅ {config_path.name} is valid")
        return True
    except Exception as e:
        print(f"❌ {config_path.name}: {e}")
        return False


if __name__ == "__main__":
    success = validate_config(Path("config/tool_profiles.json"), "tool_profiles")
    sys.exit(0 if success else 1)
