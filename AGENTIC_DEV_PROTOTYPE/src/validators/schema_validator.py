#!/usr/bin/env python3
"""
Schema Validator - PH-2A

Validates phase specification JSON files against generated JSON schemas.
Ensures structural integrity before phase execution.
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import jsonschema
from jsonschema import validate, ValidationError, Draft7Validator


class SchemaValidator:
    """Validate phase specifications against JSON schemas."""
    
    def __init__(self, schemas_dir: str = "schemas/generated"):
        self.schemas_dir = Path(schemas_dir)
        self.schemas = self._load_schemas()
    
    def _load_schemas(self) -> Dict[str, Any]:
        """Load all available JSON schemas."""
        schemas = {}
        schema_files = {
            "phase_spec": "phase_spec.schema.json",
            "validation_rules": "validation_rules.schema.json",
            "workstream": "workstream.schema.json"
        }
        
        for schema_name, filename in schema_files.items():
            schema_path = self.schemas_dir / filename
            if schema_path.exists():
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schemas[schema_name] = json.load(f)
        
        return schemas
    
    def validate_phase_spec(
        self,
        spec_data: Dict[str, Any],
        verbose: bool = False
    ) -> Tuple[bool, List[str]]:
        """
        Validate a phase specification against the phase_spec schema.
        
        Args:
            spec_data: Phase specification as dictionary
            verbose: If True, include detailed error messages
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        if "phase_spec" not in self.schemas:
            return False, ["Schema not found: phase_spec.schema.json"]
        
        schema = self.schemas["phase_spec"]
        errors = []
        
        try:
            validate(instance=spec_data, schema=schema)
            return True, []
        except ValidationError as e:
            if verbose:
                errors.append(f"Validation error at {'.'.join(str(p) for p in e.path)}: {e.message}")
                
                # Add details about missing required fields
                if e.validator == "required":
                    missing = set(e.validator_value) - set(spec_data.keys())
                    if missing:
                        errors.append(f"Missing required fields: {', '.join(missing)}")
                
                # Add details about pattern mismatches
                if e.validator == "pattern":
                    errors.append(f"Value '{e.instance}' does not match pattern '{e.validator_value}'")
            else:
                errors.append(e.message)
            
            return False, errors
    
    def validate_file(
        self,
        file_path: str,
        verbose: bool = False
    ) -> Tuple[bool, List[str]]:
        """
        Validate a phase spec file.
        
        Args:
            file_path: Path to JSON file (or '-' for stdin)
            verbose: If True, include detailed error messages
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            if file_path == '-':
                spec_data = json.load(sys.stdin)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    spec_data = json.load(f)
            
            return self.validate_phase_spec(spec_data, verbose)
        
        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON: {e.msg} at line {e.lineno}"]
        except FileNotFoundError:
            return False, [f"File not found: {file_path}"]
        except Exception as e:
            return False, [f"Error reading file: {str(e)}"]
    
    def validate_all(
        self,
        directory: str,
        pattern: str = "*.json",
        verbose: bool = False
    ) -> Dict[str, Tuple[bool, List[str]]]:
        """
        Validate all phase spec files in a directory.
        
        Args:
            directory: Directory containing phase spec files
            pattern: File pattern to match
            verbose: If True, include detailed error messages
        
        Returns:
            Dictionary mapping file paths to (is_valid, errors) tuples
        """
        results = {}
        dir_path = Path(directory)
        
        if not dir_path.exists():
            return {directory: (False, ["Directory not found"])}
        
        for file_path in dir_path.glob(pattern):
            is_valid, errors = self.validate_file(str(file_path), verbose)
            results[str(file_path)] = (is_valid, errors)
        
        return results
    
    def get_detailed_errors(
        self,
        spec_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get detailed validation errors with field paths.
        
        Returns:
            List of error dictionaries with path, message, and validator info
        """
        if "phase_spec" not in self.schemas:
            return [{"error": "Schema not found"}]
        
        schema = self.schemas["phase_spec"]
        validator = Draft7Validator(schema)
        
        detailed_errors = []
        for error in validator.iter_errors(spec_data):
            detailed_errors.append({
                "path": ".".join(str(p) for p in error.path),
                "message": error.message,
                "validator": error.validator,
                "value": error.instance if len(str(error.instance)) < 50 else str(error.instance)[:50] + "..."
            })
        
        return detailed_errors
    
    def check_required_fields(
        self,
        spec_data: Dict[str, Any]
    ) -> List[str]:
        """
        Check for missing required fields.
        
        Returns:
            List of missing required field names
        """
        if "phase_spec" not in self.schemas:
            return []
        
        schema = self.schemas["phase_spec"]
        required_fields = schema.get("required", [])
        
        missing = []
        for field in required_fields:
            if field not in spec_data:
                missing.append(field)
        
        return missing
    
    def validate_pattern(
        self,
        value: str,
        field_name: str
    ) -> Tuple[bool, str]:
        """
        Validate a specific field against its pattern.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if "phase_spec" not in self.schemas:
            return False, "Schema not found"
        
        schema = self.schemas["phase_spec"]
        properties = schema.get("properties", {})
        
        if field_name not in properties:
            return False, f"Field '{field_name}' not defined in schema"
        
        field_schema = properties[field_name]
        
        try:
            validate(instance=value, schema=field_schema)
            return True, ""
        except ValidationError as e:
            return False, e.message


def main():
    """CLI entry point for schema validation."""
    parser = argparse.ArgumentParser(
        description="Validate phase specifications against JSON schemas"
    )
    parser.add_argument(
        "--validate",
        type=str,
        help="Path to phase spec file to validate (or '-' for stdin)"
    )
    parser.add_argument(
        "--validate-all",
        type=str,
        help="Directory containing phase specs to validate"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed error messages"
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="*.json",
        help="File pattern for batch validation"
    )
    
    args = parser.parse_args()
    
    if not args.validate and not args.validate_all:
        parser.error("Either --validate or --validate-all must be specified")
    
    try:
        validator = SchemaValidator()
        
        if args.validate:
            is_valid, errors = validator.validate_file(args.validate, args.verbose)
            
            if is_valid:
                print(f"✓ Valid: {args.validate}")
                return 0
            else:
                print(f"✗ Invalid: {args.validate}")
                for error in errors:
                    print(f"  - {error}")
                return 1
        
        elif args.validate_all:
            results = validator.validate_all(args.validate_all, args.pattern, args.verbose)
            
            valid_count = sum(1 for is_valid, _ in results.values() if is_valid)
            total_count = len(results)
            
            print(f"\nValidation Results: {valid_count}/{total_count} files valid\n")
            
            for file_path, (is_valid, errors) in sorted(results.items()):
                status = "✓" if is_valid else "✗"
                print(f"{status} {file_path}")
                if errors and args.verbose:
                    for error in errors:
                        print(f"    - {error}")
            
            return 0 if valid_count == total_count else 1
    
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
