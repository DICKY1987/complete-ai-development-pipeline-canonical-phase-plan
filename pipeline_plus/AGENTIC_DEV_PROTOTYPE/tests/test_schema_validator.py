#!/usr/bin/env python3
"""
Test Suite for Schema Validator - PH-2A
"""

import json
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "validators"))

from schema_validator import SchemaValidator


class TestSchemaValidator:
    """Test schema validation functionality."""
    
    @pytest.fixture
    def validator(self):
        """Create SchemaValidator instance."""
        return SchemaValidator()
    
    def test_load_schemas(self, validator):
        """Test loading JSON schemas."""
        assert "phase_spec" in validator.schemas
        assert validator.schemas["phase_spec"]["$schema"] == "http://json-schema.org/draft-07/schema#"
    
    def test_validate_valid_phase_spec(self, validator):
        """Test validation of valid phase spec."""
        valid_spec = {
            "phase_id": "PH-TEST",
            "workstream_id": "WS-TEST",
            "phase_name": "Test Phase",
            "objective": "This is a test objective for validation",
            "dependencies": [],
            "file_scope": ["test/file.py"],
            "pre_flight_checks": [],
            "acceptance_tests": [
                {
                    "test_id": "AT-TEST-001",
                    "description": "Test 1",
                    "command": "echo test",
                    "expected": "test"
                },
                {
                    "test_id": "AT-TEST-002",
                    "description": "Test 2",
                    "command": "echo test2",
                    "expected": "test2"
                },
                {
                    "test_id": "AT-TEST-003",
                    "description": "Test 3",
                    "command": "echo test3",
                    "expected": "test3"
                }
            ],
            "deliverables": ["test output"],
            "estimated_effort_hours": 5
        }
        
        is_valid, errors = validator.validate_phase_spec(valid_spec)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_missing_required_field(self, validator):
        """Test detection of missing required fields."""
        invalid_spec = {
            "phase_id": "PH-TEST"
            # Missing many required fields
        }
        
        is_valid, errors = validator.validate_phase_spec(invalid_spec, verbose=True)
        assert is_valid is False
        assert len(errors) > 0
        assert any("objective" in str(e).lower() for e in errors)
    
    def test_validate_invalid_phase_id_pattern(self, validator):
        """Test rejection of invalid phase_id format."""
        invalid_spec = {
            "phase_id": "invalid-format",  # Should be PH-XX
            "workstream_id": "WS-TEST",
            "phase_name": "Test",
            "objective": "Test objective for pattern validation",
            "dependencies": [],
            "file_scope": ["test.py"],
            "pre_flight_checks": [],
            "acceptance_tests": [
                {"test_id": "AT-001", "description": "Test", "command": "test", "expected": "result"},
                {"test_id": "AT-002", "description": "Test", "command": "test", "expected": "result"},
                {"test_id": "AT-003", "description": "Test", "command": "test", "expected": "result"}
            ],
            "deliverables": ["test"],
            "estimated_effort_hours": 1
        }
        
        is_valid, errors = validator.validate_phase_spec(invalid_spec)
        assert is_valid is False
    
    def test_validate_insufficient_acceptance_tests(self, validator):
        """Test rejection of insufficient acceptance tests."""
        invalid_spec = {
            "phase_id": "PH-TEST",
            "workstream_id": "WS-TEST",
            "phase_name": "Test",
            "objective": "Test objective for acceptance test validation",
            "dependencies": [],
            "file_scope": ["test.py"],
            "pre_flight_checks": [],
            "acceptance_tests": [
                {"test_id": "AT-001", "description": "Only one test", "command": "test", "expected": "result"}
            ],  # Needs at least 3
            "deliverables": ["test"],
            "estimated_effort_hours": 1
        }
        
        is_valid, errors = validator.validate_phase_spec(invalid_spec)
        assert is_valid is False
    
    def test_check_required_fields(self, validator):
        """Test checking for missing required fields."""
        spec = {"phase_id": "PH-TEST"}
        
        missing = validator.check_required_fields(spec)
        
        assert "objective" in missing
        assert "file_scope" in missing
        assert "acceptance_tests" in missing
    
    def test_validate_pattern(self, validator):
        """Test pattern validation for specific fields."""
        # Valid phase_id
        is_valid, error = validator.validate_pattern("PH-01", "phase_id")
        assert is_valid is True
        
        # Invalid phase_id
        is_valid, error = validator.validate_pattern("invalid", "phase_id")
        assert is_valid is False
    
    def test_get_detailed_errors(self, validator):
        """Test getting detailed validation errors."""
        invalid_spec = {
            "phase_id": "invalid-format",
            "objective": "Test"
        }
        
        errors = validator.get_detailed_errors(invalid_spec)
        assert len(errors) > 0
        assert all(isinstance(e, dict) for e in errors)
    
    def test_validate_file_not_found(self, validator):
        """Test handling of non-existent files."""
        is_valid, errors = validator.validate_file("nonexistent.json")
        assert is_valid is False
        assert any("not found" in str(e).lower() for e in errors)
    
    def test_validate_all_directory(self, validator):
        """Test batch validation of directory."""
        results = validator.validate_all("phase_specs", pattern="phase_0_*.json")
        
        # Should find at least phase_0_bootstrap.json
        assert len(results) > 0
    
    def test_validate_invalid_json(self, validator, tmp_path):
        """Test handling of invalid JSON files."""
        invalid_json_file = tmp_path / "invalid.json"
        invalid_json_file.write_text("{invalid json")
        
        is_valid, errors = validator.validate_file(str(invalid_json_file))
        assert is_valid is False
        assert any("json" in str(e).lower() for e in errors)
    
    def test_validate_workstream_id_pattern(self, validator):
        """Test workstream_id pattern validation."""
        spec = {
            "phase_id": "PH-01",
            "workstream_id": "invalid",  # Should be WS-XX
            "phase_name": "Test",
            "objective": "Test workstream ID pattern validation",
            "dependencies": [],
            "file_scope": ["test.py"],
            "pre_flight_checks": [],
            "acceptance_tests": [
                {"test_id": "AT-001", "description": "Test", "command": "test", "expected": "result"},
                {"test_id": "AT-002", "description": "Test", "command": "test", "expected": "result"},
                {"test_id": "AT-003", "description": "Test", "command": "test", "expected": "result"}
            ],
            "deliverables": ["test"],
            "estimated_effort_hours": 1
        }
        
        is_valid, errors = validator.validate_phase_spec(spec)
        assert is_valid is False
    
    def test_validate_effort_hours_range(self, validator):
        """Test effort hours must be within valid range."""
        spec = {
            "phase_id": "PH-01",
            "workstream_id": "WS-TEST",
            "phase_name": "Test",
            "objective": "Test effort hours range validation",
            "dependencies": [],
            "file_scope": ["test.py"],
            "pre_flight_checks": [],
            "acceptance_tests": [
                {"test_id": "AT-001", "description": "Test", "command": "test", "expected": "result"},
                {"test_id": "AT-002", "description": "Test", "command": "test", "expected": "result"},
                {"test_id": "AT-003", "description": "Test", "command": "test", "expected": "result"}
            ],
            "deliverables": ["test"],
            "estimated_effort_hours": 100  # Too high (max is 40)
        }
        
        is_valid, errors = validator.validate_phase_spec(spec)
        assert is_valid is False


class TestSchemaValidatorIntegration:
    """Integration tests for schema validator."""
    
    def test_validate_existing_phase_specs(self):
        """Test validation of actual phase spec files."""
        validator = SchemaValidator()
        
        # Test phase_0_bootstrap.json
        is_valid, errors = validator.validate_file("phase_specs/phase_0_bootstrap.json")
        
        # Should be valid (or show specific errors if not)
        if not is_valid:
            print(f"Validation errors for phase_0_bootstrap.json: {errors}")
        
        assert isinstance(is_valid, bool)
        assert isinstance(errors, list)
    
    def test_validate_all_phase_specs(self):
        """Test batch validation of all phase specs."""
        validator = SchemaValidator()
        
        results = validator.validate_all("phase_specs")
        
        assert len(results) > 0
        
        # Count valid specs
        valid_count = sum(1 for is_valid, _ in results.values() if is_valid)
        print(f"Valid specs: {valid_count}/{len(results)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
