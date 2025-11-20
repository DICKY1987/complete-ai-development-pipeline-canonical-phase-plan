#!/usr/bin/env python3
"""
Test Suite for Prompt Renderer - PH-3A
"""

import json
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from prompt_renderer import PromptRenderer


class TestPromptRenderer:
    """Test prompt rendering functionality."""
    
    @pytest.fixture
    def renderer(self):
        """Create PromptRenderer instance."""
        return PromptRenderer()
    
    @pytest.fixture
    def sample_spec(self):
        """Create sample phase specification."""
        return {
            "phase_id": "PH-TEST",
            "workstream_id": "WS-TEST",
            "phase_name": "Test Phase",
            "objective": "Test objective for prompt rendering",
            "dependencies": ["PH-01"],
            "file_scope": ["src/test.py", "tests/test_test.py"],
            "pre_flight_checks": [
                {
                    "check_id": "PFC-TEST-001",
                    "description": "Check test environment",
                    "command": "python --version",
                    "expected": "Python 3.x"
                }
            ],
            "acceptance_tests": [
                {
                    "test_id": "AT-TEST-001",
                    "description": "Test passes",
                    "command": "pytest tests/test_test.py",
                    "expected": "all tests pass"
                },
                {
                    "test_id": "AT-TEST-002",
                    "description": "Code quality check",
                    "command": "pylint src/test.py",
                    "expected": "score >= 8.0"
                },
                {
                    "test_id": "AT-TEST-003",
                    "description": "Documentation exists",
                    "command": "test -f README.md",
                    "expected": "exit code 0"
                }
            ],
            "deliverables": [
                "src/test.py - Main implementation",
                "tests/test_test.py - Test suite"
            ],
            "estimated_effort_hours": 4,
            "risk_level": "low",
            "notes": "This is a test phase"
        }
    
    def test_initialization(self, renderer):
        """Test renderer initialization."""
        assert renderer.spec_renderer is not None
        assert renderer.template_path.name == "workstream_v1.1.txt"
    
    def test_render_header(self, renderer, sample_spec):
        """Test header rendering."""
        header = renderer._render_header(sample_spec)
        
        assert "WORKSTREAM_V1.1" in header
        assert "PH-TEST" in header
        assert "Test Phase" in header
        assert "=" * 80 in header
    
    def test_render_objective(self, renderer, sample_spec):
        """Test objective rendering."""
        objective = renderer._render_objective(sample_spec)
        
        assert "OBJECTIVE:" in objective
        assert "Test objective for prompt rendering" in objective
        assert "-" * 80 in objective
    
    def test_render_pre_flight_checks(self, renderer, sample_spec):
        """Test pre-flight checks rendering."""
        checks = renderer._render_pre_flight_checks(sample_spec)
        
        assert "PRE_FLIGHT_CHECKS:" in checks
        assert "PFC-TEST-001" in checks
        assert "Check test environment" in checks
        assert "python --version" in checks
    
    def test_render_file_scope(self, renderer, sample_spec):
        """Test file scope rendering."""
        scope = renderer._render_file_scope(sample_spec)
        
        assert "FILE_SCOPE:" in scope
        assert "src/test.py" in scope
        assert "tests/test_test.py" in scope
        assert "DO NOT modify" in scope
    
    def test_render_deliverables(self, renderer, sample_spec):
        """Test deliverables rendering."""
        deliverables = renderer._render_deliverables(sample_spec)
        
        assert "DELIVERABLES:" in deliverables
        assert "src/test.py" in deliverables
        assert "tests/test_test.py" in deliverables
    
    def test_render_acceptance_tests(self, renderer, sample_spec):
        """Test acceptance tests rendering."""
        tests = renderer._render_acceptance_tests(sample_spec)
        
        assert "ACCEPTANCE_TESTS" in tests
        assert "AT-TEST-001" in tests
        assert "AT-TEST-002" in tests
        assert "AT-TEST-003" in tests
        assert "pytest tests/test_test.py" in tests
    
    def test_render_dependencies(self, renderer, sample_spec):
        """Test dependencies rendering."""
        deps = renderer._render_dependencies(sample_spec)
        
        assert "DEPENDENCIES:" in deps
        assert "PH-01" in deps
    
    def test_render_footer(self, renderer, sample_spec):
        """Test footer rendering."""
        footer = renderer._render_footer(sample_spec)
        
        assert "EXECUTION_METADATA:" in footer
        assert "4 hours" in footer
        assert "low" in footer
        assert "BEGIN IMPLEMENTATION" in footer
        assert "This is a test phase" in footer
    
    def test_render_complete_prompt(self, renderer, sample_spec):
        """Test complete prompt rendering."""
        prompt = renderer.render_prompt(sample_spec)
        
        # Check all major sections present
        assert "WORKSTREAM_V1.1" in prompt
        assert "OBJECTIVE:" in prompt
        assert "PRE_FLIGHT_CHECKS:" in prompt
        assert "FILE_SCOPE:" in prompt
        assert "DELIVERABLES:" in prompt
        assert "ACCEPTANCE_TESTS" in prompt
        assert "DEPENDENCIES:" in prompt
        assert "BEGIN IMPLEMENTATION" in prompt
    
    def test_render_prompt_without_embed(self, renderer, sample_spec):
        """Test rendering without embedded specs."""
        prompt = renderer.render_prompt(sample_spec, embed_specs=False)
        
        assert "EMBEDDED_SPECIFICATION_CONTEXT:" not in prompt
    
    def test_render_from_file(self, renderer):
        """Test rendering from actual phase spec file."""
        if Path("phase_specs/phase_0_bootstrap.json").exists():
            prompt = renderer.render_from_file("phase_specs/phase_0_bootstrap.json")
            
            assert "ERROR" not in prompt
            assert "WORKSTREAM_V1.1" in prompt
            assert "PH-0" in prompt
    
    def test_render_from_nonexistent_file(self, renderer):
        """Test handling of nonexistent files."""
        prompt = renderer.render_from_file("nonexistent.json")
        
        assert "ERROR" in prompt
        assert "not found" in prompt
    
    def test_render_from_invalid_json(self, renderer, tmp_path):
        """Test handling of invalid JSON."""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("{invalid json")
        
        prompt = renderer.render_from_file(str(invalid_file))
        
        assert "ERROR" in prompt
    
    def test_save_prompt(self, renderer, sample_spec, tmp_path):
        """Test saving prompt to file."""
        output_file = tmp_path / "test_prompt.txt"
        
        prompt = renderer.render_prompt(sample_spec)
        renderer.save_prompt(prompt, str(output_file))
        
        assert output_file.exists()
        content = output_file.read_text()
        assert "WORKSTREAM_V1.1" in content
    
    def test_ascii_only_output(self, renderer, sample_spec):
        """Test that output is ASCII-only."""
        prompt = renderer.render_prompt(sample_spec)
        
        # Should be encodable as ASCII
        try:
            prompt.encode('ascii')
            ascii_only = True
        except UnicodeEncodeError:
            ascii_only = False
        
        assert ascii_only is True


class TestPromptRendererIntegration:
    """Integration tests for prompt renderer."""
    
    def test_render_all_phase_specs(self):
        """Test rendering prompts from all phase specs."""
        renderer = PromptRenderer()
        
        phase_specs_dir = Path("phase_specs")
        if not phase_specs_dir.exists():
            pytest.skip("phase_specs directory not found")
        
        spec_files = list(phase_specs_dir.glob("phase_*.json"))
        assert len(spec_files) > 0
        
        for spec_file in spec_files[:5]:  # Test first 5
            prompt = renderer.render_from_file(str(spec_file))
            
            assert "ERROR" not in prompt
            assert "WORKSTREAM_V1.1" in prompt
            assert "OBJECTIVE:" in prompt
    
    def test_prompt_has_all_required_sections(self):
        """Test that rendered prompts have all required sections."""
        renderer = PromptRenderer()
        
        required_sections = [
            "WORKSTREAM_V1.1",
            "PHASE_ID:",
            "OBJECTIVE:",
            "PRE_FLIGHT_CHECKS:",
            "FILE_SCOPE:",
            "DELIVERABLES:",
            "ACCEPTANCE_TESTS",
            "DEPENDENCIES:",
            "EXECUTION_METADATA:",
            "BEGIN IMPLEMENTATION"
        ]
        
        if Path("phase_specs/phase_0_bootstrap.json").exists():
            prompt = renderer.render_from_file("phase_specs/phase_0_bootstrap.json")
            
            for section in required_sections:
                assert section in prompt, f"Missing section: {section}"
    
    def test_acceptance_tests_count(self):
        """Test that all acceptance tests are included."""
        renderer = PromptRenderer()
        
        if Path("phase_specs/phase_0_bootstrap.json").exists():
            with open("phase_specs/phase_0_bootstrap.json", 'r') as f:
                spec = json.load(f)
            
            prompt = renderer.render_prompt(spec)
            
            # Count ACCEPTANCE_TEST occurrences
            at_count = prompt.count("ACCEPTANCE_TEST")
            expected_count = len(spec.get("acceptance_tests", []))
            
            assert at_count == expected_count


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
