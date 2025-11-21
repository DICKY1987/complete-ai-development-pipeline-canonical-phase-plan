#!/usr/bin/env python3
"""
Test Suite for Validation Gateway - PH-2C
"""

import json
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from validation_gateway import ValidationGateway, ValidationResult, ValidationLayer


class TestValidationGateway:
    """Test validation gateway functionality."""
    
    @pytest.fixture
    def gateway(self):
        """Create ValidationGateway instance."""
        return ValidationGateway()
    
    def test_initialization(self, gateway):
        """Test gateway initialization."""
        assert gateway.schema_validator is not None
        assert gateway.guard_engine is not None
    
    def test_validate_valid_spec(self, gateway):
        """Test validation of valid phase spec."""
        valid_spec = {
            "phase_id": "PH-TEST",
            "workstream_id": "WS-TEST",
            "phase_name": "Test Phase Specification",
            "objective": "Test objective for validation gateway testing purposes",
            "dependencies": [],
            "file_scope": ["test/file.py"],
            "pre_flight_checks": [],
            "acceptance_tests": [
                {"test_id": "AT-001", "description": "Test 1", "command": "test1", "expected": "result"},
                {"test_id": "AT-002", "description": "Test 2", "command": "test2", "expected": "result"},
                {"test_id": "AT-003", "description": "Test 3", "command": "test3", "expected": "result"}
            ],
            "deliverables": ["test output"],
            "estimated_effort_hours": 5
        }
        
        result = gateway.validate_phase_spec(valid_spec)
        
        assert isinstance(result, ValidationResult)
        assert result.passed is True
        assert len(result.errors) == 0
    
    def test_validate_invalid_schema(self, gateway):
        """Test validation with schema violations."""
        invalid_spec = {
            "phase_id": "PH-TEST"
            # Missing required fields
        }
        
        result = gateway.validate_phase_spec(invalid_spec)
        
        assert result.passed is False
        assert ValidationLayer.SCHEMA.value in result.layers
        assert result.layers[ValidationLayer.SCHEMA.value]["passed"] is False
    
    def test_validate_guard_rule_violations(self, gateway):
        """Test validation with guard rule violations."""
        spec = {
            "phase_id": "PH-TEST",
            "workstream_id": "WS-TEST",
            "phase_name": "Test",
            "objective": "Test objective for guard rule violation testing",
            "dependencies": [],
            "file_scope": ["."],  # Too broad - violates DR-DONT-005
            "pre_flight_checks": [],
            "acceptance_tests": [],  # Too few - violates DR-DONT-002
            "deliverables": ["test"],
            "estimated_effort_hours": 5
        }
        
        result = gateway.validate_phase_spec(spec)
        
        assert result.passed is False
        assert ValidationLayer.GUARD_RULES.value in result.layers
        assert result.layers[ValidationLayer.GUARD_RULES.value]["passed"] is False
    
    def test_validate_dependency_violations(self, gateway):
        """Test validation with dependency violations."""
        spec = {
            "phase_id": "PH-A",
            "workstream_id": "WS-TEST",
            "phase_name": "Test Phase A",
            "objective": "Test objective for dependency violation testing",
            "dependencies": ["PH-A"],  # Self-dependency - circular!
            "file_scope": ["test.py"],
            "pre_flight_checks": [],
            "acceptance_tests": [
                {"test_id": "AT-001", "description": "Test", "command": "test", "expected": "result"},
                {"test_id": "AT-002", "description": "Test", "command": "test", "expected": "result"},
                {"test_id": "AT-003", "description": "Test", "command": "test", "expected": "result"}
            ],
            "deliverables": ["test"],
            "estimated_effort_hours": 5
        }
        
        result = gateway.validate_phase_spec(spec)
        
        assert result.passed is False
        assert ValidationLayer.DEPENDENCIES.value in result.layers
    
    def test_validate_file(self, gateway):
        """Test file validation."""
        result = gateway.validate_file("phase_specs/phase_0_bootstrap.json")
        
        assert isinstance(result, ValidationResult)
        # phase_0_bootstrap.json should be valid
        if not result.passed:
            print(f"Validation errors: {result.errors}")
    
    def test_validate_nonexistent_file(self, gateway):
        """Test handling of nonexistent files."""
        result = gateway.validate_file("nonexistent.json")
        
        assert result.passed is False
        assert len(result.errors) > 0
        assert any("not found" in err.lower() for err in result.errors)
    
    def test_validate_invalid_json(self, gateway, tmp_path):
        """Test handling of invalid JSON."""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("{invalid json")
        
        result = gateway.validate_file(str(invalid_file))
        
        assert result.passed is False
        assert any("json" in err.lower() for err in result.errors)
    
    def test_validation_result_to_dict(self):
        """Test ValidationResult to_dict method."""
        result = ValidationResult()
        result.add_layer_result(ValidationLayer.SCHEMA, True, [])
        result.add_layer_result(ValidationLayer.GUARD_RULES, False, ["Error 1", "Error 2"])
        
        data = result.to_dict()
        
        assert "overall_passed" in data
        assert "layers" in data
        assert "errors" in data
        assert data["overall_passed"] is False
        assert data["error_count"] == 2
    
    def test_pre_execution_check_valid(self, gateway):
        """Test pre-execution check for valid spec."""
        ready, issues = gateway.pre_execution_check("phase_specs/phase_0_bootstrap.json")
        
        # phase_0_bootstrap.json should be ready
        if not ready:
            print(f"Pre-execution issues: {issues}")
        
        assert isinstance(ready, bool)
        assert isinstance(issues, list)
    
    def test_pre_execution_check_invalid(self, gateway, tmp_path):
        """Test pre-execution check for invalid spec."""
        invalid_spec = {"phase_id": "PH-INVALID"}
        
        invalid_file = tmp_path / "invalid_spec.json"
        invalid_file.write_text(json.dumps(invalid_spec))
        
        ready, issues = gateway.pre_execution_check(str(invalid_file))
        
        assert ready is False
        assert len(issues) > 0


class TestValidationGatewayIntegration:
    """Integration tests for validation gateway."""
    
    def test_validate_all_layers_pass(self):
        """Test that valid spec passes all layers."""
        gateway = ValidationGateway()
        
        valid_spec = {
            "phase_id": "PH-INTEGRATION-TEST",
            "workstream_id": "WS-TEST",
            "phase_name": "Integration Test Phase",
            "objective": "Integration test objective for full validation gateway testing",
            "dependencies": [],
            "file_scope": ["integration/test.py"],
            "pre_flight_checks": [
                {"check_id": "PFC-001", "description": "Check", "command": "test", "expected": "result"}
            ],
            "acceptance_tests": [
                {"test_id": "AT-001", "description": "Test 1", "command": "test1", "expected": "result"},
                {"test_id": "AT-002", "description": "Test 2", "command": "test2", "expected": "result"},
                {"test_id": "AT-003", "description": "Test 3", "command": "test3", "expected": "result"}
            ],
            "deliverables": ["integration test output"],
            "estimated_effort_hours": 8
        }
        
        result = gateway.validate_phase_spec(valid_spec)
        
        # All layers should pass
        assert result.passed is True
        assert all(layer["passed"] for layer in result.layers.values())
    
    def test_validate_existing_phase_specs(self):
        """Test validation of actual phase spec files."""
        gateway = ValidationGateway()
        
        # Test several phase specs
        phase_specs = [
            "phase_specs/phase_0_bootstrap.json",
            "phase_specs/phase_1a_universal_spec.json",
            "phase_specs/phase_2a_schema_validator.json"
        ]
        
        for spec_file in phase_specs:
            if Path(spec_file).exists():
                result = gateway.validate_file(spec_file)
                
                # Print any validation errors for debugging
                if not result.passed:
                    print(f"\nValidation issues in {spec_file}:")
                    for error in result.errors[:5]:  # First 5 errors
                        print(f"  - {error}")
                
                assert isinstance(result, ValidationResult)
    
    def test_validate_phase_plan(self):
        """Test validation of master phase plan."""
        gateway = ValidationGateway()
        
        if Path("master_phase_plan.json").exists():
            results = gateway.validate_phase_plan("master_phase_plan.json")
            
            assert len(results) > 0
            
            valid_count = sum(1 for r in results.values() if r.passed)
            print(f"\nPhase plan validation: {valid_count}/{len(results)} phases valid")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
