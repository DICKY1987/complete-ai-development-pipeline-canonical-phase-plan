"""
Workstream Converter - JSON to UET YAML Format
Converts legacy JSON workstreams to UET YAML format
"""
# DOC_ID: DOC-PAT-TOOLS-WORKSTREAM-CONVERTER-369
# DOC_ID: DOC-PAT-TOOLS-WORKSTREAM-CONVERTER-325

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any
import sys


class WorkstreamConverter:
    """Convert legacy JSON workstreams to UET YAML format."""
    
    MAPPING_RULES = {
        'id': 'workstream_id',
        'tool': lambda x: {'execution_request': {'tool_id': x}},
        'files_scope': lambda x: {'constraints': {'file_scope': {'allowed_paths': x if isinstance(x, list) else [x]}}},
        'tasks': lambda x: {'execution_request': {'prompt': ' '.join(x) if isinstance(x, list) else x}},
        'acceptance_tests': lambda x: {'acceptance_criteria': {'commands': x if isinstance(x, list) else [x]}},
        'depends_on': lambda x: {'dependencies': x if isinstance(x, list) else ([x] if x else [])},
        'circuit_breaker': lambda x: {'resilience_policy': x}
    }
    
    def __init__(self):
        self.converted_count = 0
        self.errors = []
    
    def convert_bundle(self, json_path: Path) -> Dict[str, Any]:
        """Convert a single JSON workstream to YAML format."""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            converted = self.map_fields_json_to_yaml(data)
            dependencies = self.extract_dependencies_for_dag(data)
            
            if dependencies:
                converted['dependencies'] = dependencies
            
            return converted
        except Exception as e:
            self.errors.append(f"{json_path}: {str(e)}")
            return {}
    
    def map_fields_json_to_yaml(self, data: Dict) -> Dict[str, Any]:
        """Map JSON fields to YAML structure."""
        result = {}
        
        for old_key, new_key in self.MAPPING_RULES.items():
            if old_key in data:
                value = data[old_key]
                if callable(new_key):
                    mapped = new_key(value)
                    result.update(mapped)
                else:
                    result[new_key] = value
        
        # Copy unmapped fields
        for key, value in data.items():
            if key not in self.MAPPING_RULES and key not in result:
                result[key] = value
        
        return result
    
    def extract_dependencies_for_dag(self, data: Dict) -> List[str]:
        """Extract dependencies for DAG construction."""
        deps = data.get('depends_on', [])
        if isinstance(deps, str):
            return [deps] if deps else []
        return deps if deps else []
    
    def validate_converted_workstream(self, converted: Dict) -> bool:
        """Validate converted workstream has required fields."""
        required = ['workstream_id']
        return all(field in converted for field in required)
    
    def convert_directory(self, input_dir: Path, output_dir: Path) -> int:
        """Convert all JSON files in directory to YAML."""
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        json_files = list(input_dir.glob('*.json'))
        
        for json_file in json_files:
            converted = self.convert_bundle(json_file)
            if converted and self.validate_converted_workstream(converted):
                yaml_file = output_dir / f"{json_file.stem}.yaml"
                with open(yaml_file, 'w') as f:
                    yaml.dump(converted, f, default_flow_style=False, sort_keys=False)
                self.converted_count += 1
        
        return self.converted_count


def main():
    """CLI entry point."""
    if len(sys.argv) < 3:
        print("Usage: python workstream_converter.py <input_dir> <output_dir>")
        sys.exit(1)
    
    input_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    
    converter = WorkstreamConverter()
    count = converter.convert_directory(input_dir, output_dir)
    
    print(f"✅ Converted {count} workstreams")
    if converter.errors:
        print(f"⚠️  Errors: {len(converter.errors)}")
        for error in converter.errors:
            print(f"  - {error}")
        sys.exit(1)
    
    sys.exit(0)


if __name__ == '__main__':
    main()
