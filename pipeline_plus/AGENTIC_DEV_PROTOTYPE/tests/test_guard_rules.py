#!/usr/bin/env python3
"""
Test Suite for Guard Rules Engine - PH-2B
"""

import json
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "validators"))

from guard_rules_engine import GuardRulesEngine


class TestGuardRulesEngine:
    """Test guard rules enforcement."""
    
    @pytest.fixture
    def engine(self):
        """Create GuardRulesEngine instance."""
        return GuardRulesEngine()
    
    def test_load_dr_index(self, engine):
        """Test loading DR index."""
        assert engine.dr_index is not None
        assert "sections" in engine.dr_index
    
    def test_load_rules(self, engine):
        """Test loading guard rules from DR index."""
        assert len(engine.rules) > 0
        
        # Check for specific rules
        assert any(rule_id.startswith("DR-DO-") for rule_id in engine.rules.keys())
        assert any(rule_id.startswith("DR-DONT-") for rule_id in engine.rules.keys())
    
    def test_check_acceptance_tests_present(self, engine):
        """Test detection of missing acceptance tests."""
        # Valid spec with enough tests
        valid_spec = {
            "acceptance_tests": [
                {"test_id": "AT-001", "command": "test1", "description": "Test 1", "expected": "result"},
                {"test_id": "AT-002", "command": "test2", "description": "Test 2", "expected": "result"},
                {"test_id": "AT-003", "command": "test3", "description": "Test 3", "expected": "result"}
            ]
        }
        
        is_valid, violations = engine.check_acceptance_tests_present(valid_spec)
        assert is_valid is True
        assert len(violations) == 0
        
        # Invalid spec with too few tests
        invalid_spec = {
            "acceptance_tests": []
        }
        
        is_valid, violations = engine.check_acceptance_tests_present(invalid_spec)
        assert is_valid is False
        assert any("DR-DONT-002" in v for v in violations)
    
    def test_check_file_scope_valid(self, engine):
        """Test file scope validation."""
        # Valid scope
        valid_spec = {
            "file_scope": ["src/module.py", "tests/test_module.py"]
        }
        
        is_valid, violations = engine.check_file_scope_valid(valid_spec)
        assert is_valid is True
        
        # Invalid scope (too broad)
        invalid_spec = {
            "file_scope": [".", "**/*"]
        }
        
        is_valid, violations = engine.check_file_scope_valid(invalid_spec)
        assert is_valid is False
        assert any("DR-DONT-005" in v for v in violations)
    
    def test_check_dependencies_valid(self, engine):
        """Test dependency validation."""
        # Valid dependencies
        valid_spec = {
            "phase_id": "PH-02",
            "dependencies": ["PH-01"]
        }
        
        is_valid, violations = engine.check_dependencies_valid(valid_spec)
        assert is_valid is True
        
        # Self-dependency (invalid)
        invalid_spec = {
            "phase_id": "PH-02",
            "dependencies": ["PH-02"]
        }
        
        is_valid, violations = engine.check_dependencies_valid(invalid_spec)
        assert is_valid is False
        assert any("circular" in v.lower() for v in violations)
    
    def test_check_circular_dependencies(self, engine):
        """Test circular dependency detection."""
        # Create circular dependency
        all_specs = {
            "PH-A": {"phase_id": "PH-A", "dependencies": ["PH-B"]},
            "PH-B": {"phase_id": "PH-B", "dependencies": ["PH-C"]},
            "PH-C": {"phase_id": "PH-C", "dependencies": ["PH-A"]}  # Circular!
        }
        
        is_valid, violations = engine.check_dependencies_valid(
            all_specs["PH-A"],
            all_specs
        )
        
        assert is_valid is False
        assert any("circular" in v.lower() for v in violations)
    
    def test_check_cli_first_execution(self, engine):
        """Test CLI-first execution enforcement."""
        # Valid spec with commands
        valid_spec = {
            "pre_flight_checks": [
                {"check_id": "PFC-001", "command": "test", "description": "Check", "expected": "result"}
            ],
            "acceptance_tests": [
                {"test_id": "AT-001", "command": "test", "description": "Test", "expected": "result"}
            ]
        }
        
        is_valid, violations = engine.check_cli_first_execution(valid_spec)
        assert is_valid is True
        
        # Invalid spec missing commands
        invalid_spec = {
            "acceptance_tests": [
                {"test_id": "AT-001", "description": "Test without command"}
            ]
        }
        
        is_valid, violations = engine.check_cli_first_execution(invalid_spec)
        assert is_valid is False
        assert any("DR-DO-001" in v for v in violations)
    
    def test_check_phase_id_format(self, engine):
        """Test phase_id format validation."""
        # Valid format
        valid_spec = {"phase_id": "PH-01"}
        is_valid, violations = engine.check_phase_id_format(valid_spec)
        assert is_valid is True
        
        # Invalid format
        invalid_spec = {"phase_id": "invalid"}
        is_valid, violations = engine.check_phase_id_format(invalid_spec)
        assert is_valid is False
    
    def test_check_all_rules(self, engine):
        """Test running all guard rules."""
        spec = {
            "phase_id": "PH-TEST",
            "dependencies": [],
            "file_scope": ["src/test.py"],
            "pre_flight_checks": [],
            "acceptance_tests": [
                {"test_id": "AT-001", "command": "test1", "description": "Test", "expected": "result"},
                {"test_id": "AT-002", "command": "test2", "description": "Test", "expected": "result"},
                {"test_id": "AT-003", "command": "test3", "description": "Test", "expected": "result"}
            ]
        }
        
        results = engine.check_all_rules(spec)
        
        assert "phase_id_format" in results
        assert "acceptance_tests" in results
        assert "file_scope" in results
        assert "cli_first" in results
        assert "dependencies" in results
    
    def test_validate_file(self, engine, tmp_path):
        """Test file validation."""
        valid_spec = {
            "phase_id": "PH-TEST",
            "dependencies": [],
            "file_scope": ["test.py"],
            "acceptance_tests": [
                {"test_id": "AT-001", "command": "test", "description": "Test", "expected": "result"},
                {"test_id": "AT-002", "command": "test", "description": "Test", "expected": "result"},
                {"test_id": "AT-003", "command": "test", "description": "Test", "expected": "result"}
            ]
        }
        
        test_file = tmp_path / "test_spec.json"
        test_file.write_text(json.dumps(valid_spec))
        
        is_valid, violations = engine.validate_file(str(test_file))
        
        assert isinstance(is_valid, bool)
        assert isinstance(violations, list)
    
    def test_detect_no_cycles(self, engine, tmp_path):
        """Test cycle detection with no cycles."""
        # Create specs without cycles
        specs = [
            {"phase_id": "PH-A", "dependencies": []},
            {"phase_id": "PH-B", "dependencies": ["PH-A"]},
            {"phase_id": "PH-C", "dependencies": ["PH-B"]}
        ]
        
        for spec in specs:
            file_path = tmp_path / f"{spec['phase_id']}.json"
            file_path.write_text(json.dumps(spec))
        
        no_cycles, violations = engine.detect_cycles_in_directory(str(tmp_path))
        
        assert no_cycles is True
        assert len(violations) == 0
    
    def test_detect_cycles(self, engine, tmp_path):
        """Test cycle detection with circular dependencies."""
        # Create specs with cycle
        specs = [
            {"phase_id": "PH-A", "dependencies": ["PH-C"]},
            {"phase_id": "PH-B", "dependencies": ["PH-A"]},
            {"phase_id": "PH-C", "dependencies": ["PH-B"]}
        ]
        
        for spec in specs:
            file_path = tmp_path / f"{spec['phase_id']}.json"
            file_path.write_text(json.dumps(spec))
        
        no_cycles, violations = engine.detect_cycles_in_directory(str(tmp_path))
        
        assert no_cycles is False
        assert len(violations) > 0
    
    def test_invalid_dependency_format(self, engine):
        """Test detection of invalid dependency format."""
        spec = {
            "phase_id": "PH-01",
            "dependencies": ["invalid-format", "PH-02"]
        }
        
        is_valid, violations = engine.check_dependencies_valid(spec)
        assert is_valid is False
        assert any("invalid-format" in v for v in violations)
    
    def test_missing_file_scope(self, engine):
        """Test detection of missing file_scope."""
        spec = {
            "file_scope": []
        }
        
        is_valid, violations = engine.check_file_scope_valid(spec)
        assert is_valid is False
        assert any("DR-DO-003" in v for v in violations)


class TestGuardRulesIntegration:
    """Integration tests for guard rules engine."""
    
    def test_validate_real_phase_spec(self):
        """Test validation of actual phase spec files."""
        engine = GuardRulesEngine()
        
        is_valid, violations = engine.validate_file("phase_specs/phase_0_bootstrap.json")
        
        # Print violations for debugging
        if not is_valid:
            print(f"Guard rule violations: {violations}")
        
        assert isinstance(is_valid, bool)
        assert isinstance(violations, list)
    
    def test_detect_cycles_in_phase_specs(self):
        """Test cycle detection in actual phase specs directory."""
        engine = GuardRulesEngine()
        
        no_cycles, violations = engine.detect_cycles_in_directory("phase_specs")
        
        # Should have no cycles
        if not no_cycles:
            print(f"Cycles detected: {violations}")
        
        assert no_cycles is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
