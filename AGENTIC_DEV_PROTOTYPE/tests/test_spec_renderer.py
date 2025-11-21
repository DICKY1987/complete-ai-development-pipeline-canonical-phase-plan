#!/usr/bin/env python3
"""
Test Suite for Spec Renderer - PH-1F

Comprehensive tests for specification rendering functionality.
"""

import pytest
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from spec_renderer import SpecRenderer


class TestSpecRenderer:
    """Test specification rendering functionality."""
    
    @pytest.fixture
    def renderer(self):
        """Create SpecRenderer instance."""
        return SpecRenderer()
    
    def test_load_indices(self, renderer):
        """Test loading all metadata indices."""
        assert "UPS" in renderer.indices
        assert "PPS" in renderer.indices
        assert "DR" in renderer.indices
    
    def test_load_specs(self, renderer):
        """Test loading all specification documents."""
        assert "UPS" in renderer.specs_content
        assert "PPS" in renderer.specs_content
        assert "DR" in renderer.specs_content
        
        assert len(renderer.specs_content["UPS"]) > 0
        assert len(renderer.specs_content["PPS"]) > 0
        assert len(renderer.specs_content["DR"]) > 0
    
    def test_get_spec_type_ups(self, renderer):
        """Test spec type detection for UPS."""
        assert renderer._get_spec_type("UPS-001") == "UPS"
        assert renderer._get_spec_type("UPS-002-1") == "UPS"
    
    def test_get_spec_type_pps(self, renderer):
        """Test spec type detection for PPS."""
        assert renderer._get_spec_type("PPS-001") == "PPS"
        assert renderer._get_spec_type("PPS-005-2") == "PPS"
    
    def test_get_spec_type_dr(self, renderer):
        """Test spec type detection for DR."""
        assert renderer._get_spec_type("DR-DO-001") == "DR"
        assert renderer._get_spec_type("DR-DONT-001") == "DR"
        assert renderer._get_spec_type("DR-GOLD-001") == "DR"
    
    def test_get_spec_type_invalid(self, renderer):
        """Test spec type detection for invalid ID."""
        assert renderer._get_spec_type("INVALID-001") is None
    
    def test_extract_section_content(self, renderer):
        """Test extracting section content from spec."""
        content = renderer._extract_section_content("UPS", "UPS-001")
        assert content is not None
        assert "UPS-001" in content
    
    def test_find_section_metadata(self, renderer):
        """Test finding section metadata."""
        metadata = renderer._find_section_metadata("UPS-001")
        assert metadata is not None
        assert "section_id" in metadata
        assert metadata["section_id"] == "UPS-001"
    
    def test_extract_references(self, renderer):
        """Test extracting section ID references from content."""
        content = "See UPS-001 and PPS-002 for details. Also DR-DO-001."
        refs = renderer._extract_references(content)
        
        assert "UPS-001" in refs
        assert "PPS-002" in refs
        assert "DR-DO-001" in refs
    
    def test_render_section_markdown(self, renderer):
        """Test rendering section in markdown format."""
        output = renderer.render_section("UPS-001", format="markdown")
        
        assert "UPS-001" in output
        assert "<!--" in output  # Markdown comments
        assert len(output) > 50
    
    def test_render_section_prompt(self, renderer):
        """Test rendering section in prompt format."""
        output = renderer.render_section("UPS-001", format="prompt")
        
        assert "UPS-001" in output
        assert "[Section:" in output
        assert "=" in output  # Separator lines
        # Should not have markdown formatting
        assert "{#UPS-001}" not in output
    
    def test_render_section_html(self, renderer):
        """Test rendering section in HTML format."""
        output = renderer.render_section("UPS-001", format="html")
        
        assert "UPS-001" in output
        assert "<div" in output
        assert "</div>" in output
    
    def test_render_section_invalid_id(self, renderer):
        """Test rendering with invalid section ID."""
        output = renderer.render_section("INVALID-999", format="markdown")
        assert "ERROR" in output
    
    def test_render_section_with_deps(self, renderer):
        """Test rendering section with dependencies included."""
        output = renderer.render_section("UPS-001", format="markdown", include_deps=True)
        
        assert "UPS-001" in output
        # Should include referenced sections if any
        if "Referenced Sections" in output:
            assert "=" * 80 in output
    
    def test_bundle_sections(self, renderer):
        """Test bundling multiple sections."""
        section_ids = ["UPS-001", "PPS-001"]
        output = renderer.bundle_sections(section_ids, format="markdown")
        
        assert "Context Bundle" in output
        assert "UPS-001" in output
        assert "PPS-001" in output
        assert "-" * 80 in output  # Section separators
    
    def test_bundle_sections_empty_list(self, renderer):
        """Test bundling with empty section list."""
        output = renderer.bundle_sections([], format="markdown")
        assert "Context Bundle" in output
    
    def test_save_output(self, renderer, tmp_path):
        """Test saving rendered output to file."""
        output_path = tmp_path / "test_output.md"
        content = "Test content"
        
        renderer.save_output(content, str(output_path))
        
        assert output_path.exists()
        with open(output_path, 'r') as f:
            saved = f.read()
        assert saved == content


class TestRenderFormats:
    """Test different rendering formats."""
    
    @pytest.fixture
    def renderer(self):
        return SpecRenderer()
    
    def test_markdown_preserves_structure(self, renderer):
        """Test markdown format preserves document structure."""
        output = renderer.render_section("UPS-001", format="markdown")
        
        # Should have headers
        assert "##" in output or "#" in output
    
    def test_prompt_removes_markdown(self, renderer):
        """Test prompt format removes markdown syntax."""
        output = renderer.render_section("UPS-001", format="prompt")
        
        # Should not have markdown anchors
        assert "{#" not in output
        # Should have section marker
        assert "[Section:" in output
    
    def test_html_has_valid_structure(self, renderer):
        """Test HTML format produces valid structure."""
        output = renderer.render_section("UPS-001", format="html")
        
        assert '<div class="spec-section"' in output
        assert "</div>" in output


class TestSpecRendererIntegration:
    """Integration tests for spec renderer."""
    
    def test_render_all_spec_types(self):
        """Test rendering sections from all spec types."""
        renderer = SpecRenderer()
        
        test_sections = [
            ("UPS-001", "UPS"),
            ("PPS-001", "PPS"),
            ("DR-DO-001", "DR")
        ]
        
        for section_id, expected_type in test_sections:
            output = renderer.render_section(section_id, format="markdown")
            assert section_id in output
            assert "ERROR" not in output
    
    def test_full_workflow(self, tmp_path):
        """Test complete workflow from render to save."""
        renderer = SpecRenderer()
        
        # Render a section
        content = renderer.render_section("UPS-001", format="markdown")
        assert len(content) > 0
        
        # Save to file
        output_path = tmp_path / "rendered_section.md"
        renderer.save_output(content, str(output_path))
        
        # Verify file
        assert output_path.exists()
        with open(output_path, 'r') as f:
            saved = f.read()
        assert saved == content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
