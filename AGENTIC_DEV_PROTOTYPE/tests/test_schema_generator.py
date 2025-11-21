#!/usr/bin/env python3
"""
Test Suite for Schema Generator - PH-1E

Comprehensive tests for schema generation from specification documents.
"""

import json
import pytest
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from schema_generator import SchemaGenerator


class TestSchemaGenerator:
    """Test schema generation functionality."""
    
    @pytest.fixture
    def generator(self):
        """Create SchemaGenerator instance."""
        return SchemaGenerator()
    
    def test_load_indices(self, generator):
        """Test loading metadata indices."""
        assert generator.pps_index is not None
        assert generator.ups_index is not None
        assert generator.dr_index is not None
        assert "sections" in generator.pps_index
        assert "sections" in generator.ups_index
        assert "sections" in generator.dr_index
    
    def test_generate_phase_spec_schema(self, generator):
        """Test phase specification schema generation."""
        schema = generator.generate_phase_spec_schema()
        
        assert schema is not None
        assert "$schema" in schema
        assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema
    
    def test_phase_spec_required_fields(self, generator):
        """Test that phase spec schema enforces required fields."""
        schema = generator.generate_phase_spec_schema()
        
        required = schema["required"]
        assert "phase_id" in required
        assert "objective" in required
        assert "file_scope" in required
        assert "acceptance_tests" in required
        assert "deliverables" in required
    
    def test_phase_spec_phase_id_pattern(self, generator):
        """Test phase_id pattern validation."""
        schema = generator.generate_phase_spec_schema()
        
        phase_id_prop = schema["properties"]["phase_id"]
        assert "pattern" in phase_id_prop
        assert phase_id_prop["pattern"] == "^PH-[0-9A-Z]+$"
    
    def test_phase_spec_acceptance_tests_structure(self, generator):
        """Test acceptance_tests array structure."""
        schema = generator.generate_phase_spec_schema()
        
        at_prop = schema["properties"]["acceptance_tests"]
        assert at_prop["type"] == "array"
        assert "items" in at_prop
        assert at_prop["minItems"] == 3
        
        item_schema = at_prop["items"]
        assert "test_id" in item_schema["required"]
        assert "description" in item_schema["required"]
        assert "command" in item_schema["required"]
        assert "expected" in item_schema["required"]
    
    def test_generate_validation_rules_schema(self, generator):
        """Test validation rules schema generation."""
        schema = generator.generate_validation_rules_schema()
        
        assert schema is not None
        assert "$schema" in schema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "rules_version" in schema["required"]
        assert "rules" in schema["required"]
    
    def test_validation_rules_severity_enum(self, generator):
        """Test validation rules severity enumeration."""
        schema = generator.generate_validation_rules_schema()
        
        rules_items = schema["properties"]["rules"]["items"]
        severity = rules_items["properties"]["severity"]
        assert severity["type"] == "string"
        assert set(severity["enum"]) == {"ERROR", "WARNING", "INFO"}
    
    def test_validation_rules_category_enum(self, generator):
        """Test validation rules category enumeration."""
        schema = generator.generate_validation_rules_schema()
        
        rules_items = schema["properties"]["rules"]["items"]
        category = rules_items["properties"]["category"]
        assert category["type"] == "string"
        assert "STRUCTURE" in category["enum"]
        assert "ANTI_PATTERN" in category["enum"]
    
    def test_generate_workstream_schema(self, generator):
        """Test workstream schema generation."""
        schema = generator.generate_workstream_schema()
        
        assert schema is not None
        assert "$schema" in schema
        assert schema["type"] == "object"
        assert "workstream_id" in schema["required"]
        assert "phases" in schema["required"]
    
    def test_validate_generated_schema_valid(self, generator):
        """Test validation of valid generated schema."""
        schema = generator.generate_phase_spec_schema()
        assert generator.validate_generated_schema(schema) is True
    
    def test_validate_generated_schema_invalid(self, generator):
        """Test validation of invalid schema."""
        invalid_schema = {"type": "object"}  # Missing $schema
        assert generator.validate_generated_schema(invalid_schema) is False
    
    def test_save_schema(self, generator, tmp_path):
        """Test saving schema to file."""
        schema = generator.generate_phase_spec_schema()
        output_path = tmp_path / "test_schema.json"
        
        generator.save_schema(schema, str(output_path))
        
        assert output_path.exists()
        
        with open(output_path, 'r') as f:
            loaded = json.load(f)
        
        assert loaded == schema


class TestSchemaIntegration:
    """Integration tests for schema generation."""
    
    def test_generate_all_schemas(self, tmp_path):
        """Test generating all schemas at once."""
        generator = SchemaGenerator()
        
        schemas = {
            "phase_spec.schema.json": generator.generate_phase_spec_schema(),
            "validation_rules.schema.json": generator.generate_validation_rules_schema(),
            "workstream.schema.json": generator.generate_workstream_schema()
        }
        
        for filename, schema in schemas.items():
            output_path = tmp_path / filename
            generator.save_schema(schema, str(output_path))
            assert output_path.exists()
            
            # Validate each is valid JSON
            with open(output_path, 'r') as f:
                loaded = json.load(f)
                assert loaded["$schema"] == "http://json-schema.org/draft-07/schema#"
    
    def test_schemas_have_unique_ids(self):
        """Test that all schemas have unique $id values."""
        generator = SchemaGenerator()
        
        phase_schema = generator.generate_phase_spec_schema()
        rules_schema = generator.generate_validation_rules_schema()
        ws_schema = generator.generate_workstream_schema()
        
        ids = [
            phase_schema["$id"],
            rules_schema["$id"],
            ws_schema["$id"]
        ]
        
        assert len(ids) == len(set(ids))  # All unique


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
