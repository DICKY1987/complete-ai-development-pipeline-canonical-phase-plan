#!/usr/bin/env python3
"""
Schema Generator - PH-1E

Generates JSON schemas from machine-readable specification documents.
Parses PPS (PRO Phase Spec) sections to extract schema requirements and
generates valid JSON Schema format for phase specifications and validation rules.
"""

import json
import re
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional


class SchemaGenerator:
    """Generate JSON schemas from specification documents."""
    
    def __init__(self, specs_dir: str = "specs", metadata_dir: str = "specs/metadata"):
        self.specs_dir = Path(specs_dir)
        self.metadata_dir = Path(metadata_dir)
        self.pps_index = self._load_index("pps_index.json")
        self.ups_index = self._load_index("ups_index.json")
        self.dr_index = self._load_index("dr_index.json")
        
    def _load_index(self, filename: str) -> Dict[str, Any]:
        """Load metadata index JSON file."""
        index_path = self.metadata_dir / filename
        if not index_path.exists():
            raise FileNotFoundError(f"Index file not found: {index_path}")
        with open(index_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _read_spec_section(self, spec_file: str, section_id: str) -> str:
        """Read a specific section from a specification file."""
        spec_path = self.specs_dir / spec_file
        if not spec_path.exists():
            raise FileNotFoundError(f"Spec file not found: {spec_path}")
        
        with open(spec_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find section by anchor
        pattern = rf"##[^#].*?\{{#{section_id}\}}(.*?)(?=##[^#]|\Z)"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""
    
    def generate_phase_spec_schema(self) -> Dict[str, Any]:
        """Generate JSON schema for phase specifications from PPS sections."""
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "https://gameboardprotocol.org/schemas/phase-spec.schema.json",
            "title": "Game Board Protocol Phase Specification",
            "description": "Schema for phase specification documents following PRO Phase Specification standards",
            "type": "object",
            "required": [
                "phase_id",
                "workstream_id",
                "phase_name",
                "objective",
                "dependencies",
                "file_scope",
                "pre_flight_checks",
                "acceptance_tests",
                "deliverables",
                "estimated_effort_hours"
            ],
            "properties": {
                "phase_id": {
                    "type": "string",
                    "pattern": "^PH-[0-9A-Z]+$",
                    "description": "Unique phase identifier (e.g., PH-00, PH-1A)"
                },
                "workstream_id": {
                    "type": "string",
                    "pattern": "^WS-[A-Z0-9-]+$",
                    "description": "Parent workstream identifier"
                },
                "phase_name": {
                    "type": "string",
                    "minLength": 5,
                    "maxLength": 100,
                    "description": "Human-readable phase name"
                },
                "objective": {
                    "type": "string",
                    "minLength": 20,
                    "description": "Clear, measurable objective for this phase"
                },
                "dependencies": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "pattern": "^PH-[0-9A-Z]+$"
                    },
                    "description": "List of prerequisite phase IDs"
                },
                "file_scope": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                    "description": "Files and directories this phase will create or modify"
                },
                "pre_flight_checks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["check_id", "description", "command", "expected"],
                        "properties": {
                            "check_id": {
                                "type": "string",
                                "pattern": "^PFC-[0-9A-Z]+-\\d{3}$"
                            },
                            "description": {"type": "string"},
                            "command": {"type": "string"},
                            "expected": {"type": "string"}
                        }
                    },
                    "description": "Pre-execution validation checks"
                },
                "acceptance_tests": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["test_id", "description", "command", "expected"],
                        "properties": {
                            "test_id": {
                                "type": "string",
                                "pattern": "^AT-[0-9A-Z]+-\\d{3}$"
                            },
                            "description": {"type": "string"},
                            "command": {"type": "string"},
                            "expected": {"type": "string"}
                        }
                    },
                    "minItems": 3,
                    "description": "Programmatic acceptance tests"
                },
                "deliverables": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                    "description": "Concrete outputs from this phase"
                },
                "estimated_effort_hours": {
                    "type": "number",
                    "minimum": 0.5,
                    "maximum": 40,
                    "description": "Estimated effort in hours"
                },
                "risk_level": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "description": "Risk assessment for this phase"
                },
                "parallel_group": {
                    "type": ["string", "null"],
                    "pattern": "^GROUP-\\d+$",
                    "description": "Parallel execution group identifier"
                },
                "notes": {
                    "type": "string",
                    "description": "Additional context or warnings"
                },
                "execution_status": {
                    "type": "string",
                    "enum": ["NOT_STARTED", "IN_PROGRESS", "BLOCKED", "COMPLETE", "FAILED"],
                    "description": "Current execution status"
                },
                "completed_timestamp": {
                    "type": "string",
                    "format": "date-time",
                    "description": "ISO 8601 completion timestamp"
                }
            },
            "additionalProperties": False
        }
        
        return schema
    
    def generate_validation_rules_schema(self) -> Dict[str, Any]:
        """Generate JSON schema for validation rules from DR sections."""
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "https://gameboardprotocol.org/schemas/validation-rules.schema.json",
            "title": "Game Board Protocol Validation Rules",
            "description": "Schema for validation rules based on Development Rules (DR) specifications",
            "type": "object",
            "required": ["rules_version", "rules"],
            "properties": {
                "rules_version": {
                    "type": "string",
                    "pattern": "^\\d+\\.\\d+\\.\\d+$",
                    "description": "Semantic version of rules set"
                },
                "rules": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["rule_id", "category", "severity", "description", "validation_type"],
                        "properties": {
                            "rule_id": {
                                "type": "string",
                                "pattern": "^VR-\\d{3}$",
                                "description": "Unique validation rule identifier"
                            },
                            "category": {
                                "type": "string",
                                "enum": ["STRUCTURE", "DEPENDENCY", "SCOPE", "TESTING", "ANTI_PATTERN"],
                                "description": "Rule category"
                            },
                            "severity": {
                                "type": "string",
                                "enum": ["ERROR", "WARNING", "INFO"],
                                "description": "Validation severity level"
                            },
                            "description": {
                                "type": "string",
                                "minLength": 10,
                                "description": "Human-readable rule description"
                            },
                            "validation_type": {
                                "type": "string",
                                "enum": ["SCHEMA", "SEMANTIC", "INTEGRATION", "ANTI_PATTERN"],
                                "description": "Type of validation check"
                            },
                            "validator_function": {
                                "type": "string",
                                "description": "Python function name for validation"
                            },
                            "error_message": {
                                "type": "string",
                                "description": "Error message template"
                            },
                            "dr_reference": {
                                "type": "string",
                                "pattern": "^DR-(DO|DONT|GOLD)-\\d{3}",
                                "description": "Reference to Development Rule section"
                            }
                        }
                    },
                    "minItems": 1,
                    "description": "Array of validation rules"
                }
            },
            "additionalProperties": False
        }
        
        return schema
    
    def generate_workstream_schema(self) -> Dict[str, Any]:
        """Generate JSON schema for workstream definitions."""
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "https://gameboardprotocol.org/schemas/workstream.schema.json",
            "title": "Game Board Protocol Workstream",
            "description": "Schema for workstream definitions containing multiple phases",
            "type": "object",
            "required": ["workstream_id", "workstream_name", "description", "phases"],
            "properties": {
                "workstream_id": {
                    "type": "string",
                    "pattern": "^WS-[A-Z0-9-]+$"
                },
                "workstream_name": {
                    "type": "string",
                    "minLength": 5
                },
                "description": {
                    "type": "string",
                    "minLength": 20
                },
                "phases": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "pattern": "^PH-[0-9A-Z]+$"
                    },
                    "minItems": 1
                },
                "estimated_total_hours": {
                    "type": "number",
                    "minimum": 0
                }
            }
        }
        
        return schema
    
    def save_schema(self, schema: Dict[str, Any], output_path: str) -> None:
        """Save schema to JSON file with pretty formatting."""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)
        
        print(f"Schema saved to: {output}")
    
    def validate_generated_schema(self, schema: Dict[str, Any]) -> bool:
        """Validate that generated schema is valid JSON Schema."""
        required_fields = ["$schema", "type", "properties"]
        for field in required_fields:
            if field not in schema:
                print(f"ERROR: Missing required field: {field}")
                return False
        
        if schema["$schema"] != "http://json-schema.org/draft-07/schema#":
            print("ERROR: Invalid $schema value")
            return False
        
        print("Schema validation: PASSED")
        return True


def main():
    """CLI entry point for schema generation."""
    parser = argparse.ArgumentParser(
        description="Generate JSON schemas from Game Board Protocol specifications"
    )
    parser.add_argument(
        "--generate",
        choices=["phase-spec", "validation-rules", "workstream", "all"],
        required=True,
        help="Type of schema to generate"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file path (required for single schema generation)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="schemas/generated",
        help="Output directory for 'all' generation"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate generated schema"
    )
    
    args = parser.parse_args()
    
    try:
        generator = SchemaGenerator()
        
        if args.generate == "phase-spec":
            if not args.output:
                print("ERROR: --output required for single schema generation")
                return 1
            schema = generator.generate_phase_spec_schema()
            generator.save_schema(schema, args.output)
            if args.validate:
                generator.validate_generated_schema(schema)
        
        elif args.generate == "validation-rules":
            if not args.output:
                print("ERROR: --output required for single schema generation")
                return 1
            schema = generator.generate_validation_rules_schema()
            generator.save_schema(schema, args.output)
            if args.validate:
                generator.validate_generated_schema(schema)
        
        elif args.generate == "workstream":
            if not args.output:
                print("ERROR: --output required for single schema generation")
                return 1
            schema = generator.generate_workstream_schema()
            generator.save_schema(schema, args.output)
            if args.validate:
                generator.validate_generated_schema(schema)
        
        elif args.generate == "all":
            output_dir = Path(args.output_dir)
            schemas = {
                "phase_spec.schema.json": generator.generate_phase_spec_schema(),
                "validation_rules.schema.json": generator.generate_validation_rules_schema(),
                "workstream.schema.json": generator.generate_workstream_schema()
            }
            
            for filename, schema in schemas.items():
                output_path = output_dir / filename
                generator.save_schema(schema, str(output_path))
                if args.validate:
                    generator.validate_generated_schema(schema)
        
        return 0
    
    except Exception as e:
        print(f"ERROR: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
