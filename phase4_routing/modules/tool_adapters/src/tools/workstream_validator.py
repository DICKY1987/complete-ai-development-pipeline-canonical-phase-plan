"""
Workstream Validator - Validates UET YAML Workstreams
Checks schema compliance and dependency cycles
"""
# DOC_ID: DOC-PAT-TOOLS-WORKSTREAM-VALIDATOR-370
# DOC_ID: DOC-PAT-TOOLS-WORKSTREAM-VALIDATOR-326

import yaml
from pathlib import Path
from typing import List, Dict, Set
import sys


class WorkstreamValidator:
    """Validate UET YAML workstreams."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_against_uet_schema(self, workstream: Dict) -> bool:
        """Validate workstream against UET schema requirements."""
        required_fields = ['workstream_id']
        
        for field in required_fields:
            if field not in workstream:
                self.errors.append(f"Missing required field: {field}")
                return False
        
        return True
    
    def check_dependency_cycles(self, workstreams: List[Dict]) -> bool:
        """Check for dependency cycles using DFS."""
        graph = {}
        for ws in workstreams:
            ws_id = ws.get('workstream_id')
            deps = ws.get('dependencies', [])
            graph[ws_id] = deps
        
        def has_cycle(node, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    self.errors.append(f"Dependency cycle detected: {node} -> {neighbor}")
                    return True
            
            rec_stack.remove(node)
            return False
        
        visited = set()
        for node in graph:
            if node not in visited:
                if has_cycle(node, visited, set()):
                    return False
        
        return True
    
    def verify_tool_exists(self, workstream: Dict) -> bool:
        """Verify tool_id is specified (stub - actual tool check would go here)."""
        exec_req = workstream.get('execution_request', {})
        if 'tool_id' not in exec_req:
            self.warnings.append(f"No tool_id specified for {workstream.get('workstream_id')}")
            return False
        return True
    
    def validate_file(self, yaml_file: Path) -> bool:
        """Validate a single YAML file."""
        try:
            with open(yaml_file, 'r') as f:
                workstream = yaml.safe_load(f)
            
            if not self.validate_against_uet_schema(workstream):
                return False
            
            self.verify_tool_exists(workstream)
            return True
            
        except Exception as e:
            self.errors.append(f"{yaml_file}: {str(e)}")
            return False
    
    def validate_directory(self, directory: Path) -> bool:
        """Validate all YAML files in directory."""
        yaml_files = list(directory.glob('*.yaml'))
        
        workstreams = []
        all_valid = True
        
        for yaml_file in yaml_files:
            if not self.validate_file(yaml_file):
                all_valid = False
            else:
                with open(yaml_file, 'r') as f:
                    workstreams.append(yaml.safe_load(f))
        
        if workstreams and not self.check_dependency_cycles(workstreams):
            all_valid = False
        
        return all_valid


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python workstream_validator.py <directory>")
        sys.exit(1)
    
    directory = Path(sys.argv[1])
    
    if '--check-cycles' in sys.argv:
        # Just check for cycles
        validator = WorkstreamValidator()
        workstreams = []
        for f in directory.glob('*.yaml'):
            with open(f, 'r') as file:
                workstreams.append(yaml.safe_load(file))
        
        if validator.check_dependency_cycles(workstreams):
            print("✅ No dependency cycles")
            sys.exit(0)
        else:
            print("❌ Dependency cycles found")
            for error in validator.errors:
                print(f"  - {error}")
            sys.exit(1)
    
    validator = WorkstreamValidator()
    is_valid = validator.validate_directory(directory)
    
    if is_valid:
        print("✅ All workstreams valid")
        sys.exit(0)
    else:
        print("❌ Validation failed")
        for error in validator.errors:
            print(f"  - {error}")
        for warning in validator.warnings:
            print(f"  ⚠️  {warning}")
        sys.exit(1)


if __name__ == '__main__':
    main()
