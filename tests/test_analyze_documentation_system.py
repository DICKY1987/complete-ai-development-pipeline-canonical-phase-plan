"""
Tests for documentation system analysis CLI tool
"""

import json
import tempfile
from pathlib import Path
import pytest
import sys

# Add scripts to path for import
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from analyze_documentation_system import (
    DocumentationAnalyzer,
    SSOTCategoryStatus,
    SSOT_CATEGORIES,
)


@pytest.fixture
def temp_repo(tmp_path):
    """Create a temporary repository structure for testing"""
    repo = tmp_path / "test_repo"
    repo.mkdir()
    
    # Create some basic structure
    (repo / "docs").mkdir()
    (repo / "patterns").mkdir()
    (repo / "patterns" / "registry").mkdir()
    (repo / "scripts").mkdir()
    (repo / ".github").mkdir()
    (repo / ".github" / "workflows").mkdir()
    
    # Create a doc with frontmatter
    doc1 = repo / "docs" / "test_doc.md"
    doc1.write_text("""---
doc_id: DOC-TEST-001
related_doc_ids:
  - DOC-TEST-002
---

# Test Document

This references PAT-TEST-001 and MOD-TEST-001.
""")
    
    # Create README
    readme = repo / "README.md"
    readme.write_text("""---
doc_id: DOC-README-001
---

# Test Repository
""")
    
    # Create a validator script
    validator = repo / "scripts" / "validate_test.py"
    validator.write_text("# Test validator")
    
    # Create a generator script
    generator = repo / "scripts" / "generate_test.py"
    generator.write_text("# Test generator")
    
    # Create a workflow that uses validator
    workflow = repo / ".github" / "workflows" / "test.yml"
    workflow.write_text("""
name: Test
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: python scripts/validate_test.py
""")
    
    return repo


def test_analyzer_initialization(temp_repo):
    """Test analyzer initialization"""
    analyzer = DocumentationAnalyzer(temp_repo)
    assert analyzer.repo_root == temp_repo
    assert len(analyzer.all_doc_ids) == 0


def test_scan_docs_for_ids(temp_repo):
    """Test scanning documents for IDs"""
    analyzer = DocumentationAnalyzer(temp_repo)
    analyzer._scan_docs_for_ids()
    
    # Should find doc_ids
    assert "DOC-TEST-001" in analyzer.all_doc_ids
    assert "DOC-README-001" in analyzer.all_doc_ids
    
    # Should find pattern_ids
    assert "PAT-TEST-001" in analyzer.all_pattern_ids
    
    # Should find module_ids
    assert "MOD-TEST-001" in analyzer.all_module_ids


def test_extract_frontmatter(temp_repo):
    """Test frontmatter extraction"""
    analyzer = DocumentationAnalyzer(temp_repo)
    
    content = """---
doc_id: DOC-TEST-123
version: 1.0
---

# Content
"""
    
    frontmatter = analyzer._extract_frontmatter(content)
    assert frontmatter is not None
    assert frontmatter['doc_id'] == 'DOC-TEST-123'
    assert frontmatter['version'] == 1.0


def test_ssot_categories_complete():
    """Test that all 22 SSOT categories are defined"""
    all_categories = []
    for group_categories in SSOT_CATEGORIES.values():
        all_categories.extend(group_categories)
    
    assert len(all_categories) == 22


def test_analyze_link_integrity(temp_repo):
    """Test link integrity analysis"""
    analyzer = DocumentationAnalyzer(temp_repo)
    analyzer._scan_docs_for_ids()
    
    integrity = analyzer._analyze_link_integrity()
    
    # Should track doc_ids
    assert integrity.doc_ids['total_in_files'] >= 2
    
    # Should find dangling reference (DOC-TEST-002 referenced but not exists)
    assert len(integrity.doc_ids['dangling_references']) > 0


def test_analyze_automation_state(temp_repo):
    """Test automation state analysis"""
    analyzer = DocumentationAnalyzer(temp_repo)
    
    state = analyzer._analyze_automation_state()
    
    # Should find validators
    assert 'validate_test.py' in state.validators['found']
    
    # Should find generators
    assert 'generate_test.py' in state.generators['found']
    
    # Should identify wired validators
    assert 'validate_test.py' in state.validators['wired_into_ci']


def test_full_analysis_runs(temp_repo):
    """Test that full analysis runs without errors"""
    analyzer = DocumentationAnalyzer(temp_repo)
    report = analyzer.analyze()
    
    # Should have all sections
    assert 'total_categories' in report.ssot_coverage
    assert report.link_integrity is not None
    assert report.automation_state is not None
    assert report.overall_assessment is not None


def test_ssot_category_status():
    """Test SSOT category status dataclass"""
    status = SSOTCategoryStatus(name="Test Category")
    assert status.name == "Test Category"
    assert status.expected is True
    assert status.ssot_doc_found is False
    assert status.status == "missing"


def test_duplicate_doc_ids(temp_repo):
    """Test duplicate doc_id detection"""
    # Create another doc with same ID
    doc2 = temp_repo / "docs" / "duplicate.md"
    doc2.write_text("""---
doc_id: DOC-TEST-001
---

# Duplicate
""")
    
    analyzer = DocumentationAnalyzer(temp_repo)
    analyzer._scan_docs_for_ids()
    
    duplicates = analyzer._find_duplicate_doc_ids()
    assert "DOC-TEST-001" in duplicates


def test_overall_assessment_risk_levels(temp_repo):
    """Test risk level calculation"""
    analyzer = DocumentationAnalyzer(temp_repo)
    report = analyzer.analyze()
    
    # Risk level should be set
    assert report.overall_assessment['risk_level'] in ['low', 'medium', 'high']
    
    # Should have summary
    assert len(report.overall_assessment['summary']) > 0
    
    # Should have findings
    assert len(report.overall_assessment['key_findings']) > 0


def test_json_serialization(temp_repo):
    """Test that report can be serialized to JSON"""
    analyzer = DocumentationAnalyzer(temp_repo)
    report = analyzer.analyze()
    
    # Should be able to convert to dict and serialize
    from dataclasses import asdict
    report_dict = asdict(report)
    json_str = json.dumps(report_dict)
    
    # Should be valid JSON
    parsed = json.loads(json_str)
    assert 'ssot_coverage' in parsed
    assert 'link_integrity' in parsed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
