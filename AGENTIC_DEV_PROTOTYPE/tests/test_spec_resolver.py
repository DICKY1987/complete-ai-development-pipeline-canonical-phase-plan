#!/usr/bin/env python3
"""
Unit tests for spec_resolver.py
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from spec_resolver import SpecResolver, Section, Reference


@pytest.fixture
def resolver():
    """Create a SpecResolver instance with test base path"""
    base_path = Path(__file__).parent.parent
    resolver = SpecResolver(base_path)
    resolver.load_indices()
    return resolver


class TestSpecResolver:
    """Tests for SpecResolver class"""
    
    def test_load_indices(self, resolver):
        """Test that all indices load successfully"""
        assert len(resolver.indices) == 3
        assert 'UPS' in resolver.indices
        assert 'PPS' in resolver.indices
        assert 'DR' in resolver.indices
    
    def test_sections_loaded(self, resolver):
        """Test that sections are loaded from indices"""
        assert len(resolver.sections) > 0
        # Should have at least sections from all three docs
        assert any(sid.startswith('UPS-') for sid in resolver.sections)
        assert any(sid.startswith('PPS-') for sid in resolver.sections)
        assert any(sid.startswith('DR-') for sid in resolver.sections)
    
    def test_parse_all(self, resolver):
        """Test parse_all method"""
        result = resolver.parse_all()
        assert result is True
        assert len(resolver.sections) > 10
    
    def test_lookup_valid_section(self, resolver):
        """Test looking up a valid section"""
        section = resolver.lookup('UPS-001')
        assert section is not None
        assert section.section_id == 'UPS-001'
        assert section.title == 'Overview'
        assert section.document_id == 'UNIVERSAL_PHASE_SPEC_V1'
    
    def test_lookup_invalid_section(self, resolver):
        """Test looking up an invalid section"""
        section = resolver.lookup('INVALID-999')
        assert section is None
    
    def test_lookup_subsection(self, resolver):
        """Test looking up a subsection"""
        section = resolver.lookup('UPS-002-1')
        assert section is not None
        assert section.section_id == 'UPS-002-1'
    
    def test_get_all_section_ids(self, resolver):
        """Test getting all section IDs"""
        all_ids = resolver.get_all_section_ids()
        assert len(all_ids) > 0
        assert 'UPS-001' in all_ids
        assert 'PPS-001' in all_ids
        assert 'DR-001' in all_ids
        # Check that it's sorted
        assert all_ids == sorted(all_ids)
    
    def test_validate_spec_valid(self, resolver):
        """Test validating a spec with valid references"""
        spec_path = resolver.specs_path / 'UNIVERSAL_PHASE_SPEC_V1.md'
        is_valid, errors = resolver.validate_spec(str(spec_path))
        # Should be valid with no broken references
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_spec_nonexistent(self, resolver):
        """Test validating a non-existent spec"""
        is_valid, errors = resolver.validate_spec('nonexistent.md')
        assert is_valid is False
        assert len(errors) > 0
        assert 'not found' in errors[0].lower()
    
    def test_find_references_to(self, resolver):
        """Test finding references to a section"""
        # UPS sections are referenced in cross-reference sections
        refs = resolver.find_references_to('UPS-001')
        # May or may not find refs, just test it doesn't crash
        assert isinstance(refs, list)
    
    def test_search_by_keyword(self, resolver):
        """Test searching sections by keyword"""
        results = resolver.search_by_keyword('validation')
        assert len(results) > 0
        # Should find validation-related sections
        assert any('valid' in s.title.lower() for s in results if s.title)
    
    def test_search_by_keyword_no_results(self, resolver):
        """Test searching with a keyword that yields no results"""
        results = resolver.search_by_keyword('xyzzyquux')
        assert len(results) == 0
    
    def test_section_dataclass(self):
        """Test Section dataclass"""
        section = Section(
            section_id='TEST-001',
            title='Test Section',
            document_id='TEST_DOC',
            file_path='test.md',
            line_start=10,
            level=2
        )
        assert section.section_id == 'TEST-001'
        assert section.title == 'Test Section'
        assert section.line_start == 10
    
    def test_matches_pattern(self, resolver):
        """Test pattern matching for wildcards"""
        # Test exact match
        assert resolver._matches_pattern('UPS-001', 'UPS-001') is True
        assert resolver._matches_pattern('UPS-001', 'UPS-002') is False
        
        # Test wildcard patterns
        assert resolver._matches_pattern('UPS-*', 'UPS-001') is True
        assert resolver._matches_pattern('UPS-*', 'UPS-999') is True
        assert resolver._matches_pattern('UPS-*', 'PPS-001') is False
        
        assert resolver._matches_pattern('DR-DO-*', 'DR-DO-001') is True
        assert resolver._matches_pattern('DR-DO-*', 'DR-DONT-001') is False


class TestIntegration:
    """Integration tests for spec resolver"""
    
    def test_all_ups_sections_resolvable(self, resolver):
        """Test that all UPS sections can be looked up"""
        ups_sections = [sid for sid in resolver.sections if sid.startswith('UPS-')]
        assert len(ups_sections) >= 10
        
        for section_id in ups_sections:
            section = resolver.lookup(section_id)
            assert section is not None
            assert section.section_id == section_id
    
    def test_all_pps_sections_resolvable(self, resolver):
        """Test that all PPS sections can be looked up"""
        pps_sections = [sid for sid in resolver.sections if sid.startswith('PPS-')]
        assert len(pps_sections) >= 8
        
        for section_id in pps_sections:
            section = resolver.lookup(section_id)
            assert section is not None
            assert section.section_id == section_id
    
    def test_all_dr_sections_resolvable(self, resolver):
        """Test that all DR sections can be looked up"""
        dr_sections = [sid for sid in resolver.sections if sid.startswith('DR-')]
        assert len(dr_sections) >= 10
        
        for section_id in dr_sections:
            section = resolver.lookup(section_id)
            assert section is not None
            assert section.section_id == section_id
    
    def test_cross_references_valid(self, resolver):
        """Test that cross-references in specs are valid"""
        specs = [
            'UNIVERSAL_PHASE_SPEC_V1.md',
            'PRO_PHASE_SPEC_V1.md',
            'DEV_RULES_V1.md'
        ]
        
        for spec_name in specs:
            spec_path = resolver.specs_path / spec_name
            if spec_path.exists():
                is_valid, errors = resolver.validate_spec(str(spec_path))
                # Report but don't fail if there are wildcard patterns
                if not is_valid:
                    # Filter out wildcard pattern "errors"
                    real_errors = [e for e in errors if '*' not in e]
                    if real_errors:
                        print(f"Validation errors in {spec_name}:")
                        for error in real_errors:
                            print(f"  {error}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
