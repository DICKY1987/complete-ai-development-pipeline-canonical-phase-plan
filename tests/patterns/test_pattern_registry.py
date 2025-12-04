"""Tests for pattern registry validation."""

import pytest
import yaml
from pathlib import Path

def test_pattern_index_exists():
    """Test that PATTERN_INDEX.yaml exists."""
# DOC_ID: DOC-TEST-PATTERNS-TEST-PATTERN-REGISTRY-185
    index_path = Path("patterns/registry/PATTERN_INDEX.yaml")
    assert index_path.exists(), "PATTERN_INDEX.yaml not found"

def test_pattern_index_valid_yaml():
    """Test that PATTERN_INDEX.yaml is valid YAML."""
    index_path = Path("patterns/registry/PATTERN_INDEX.yaml")
    with open(index_path) as f:
        data = yaml.safe_load(f)
    assert data is not None
    assert 'patterns' in data

def test_all_patterns_have_doc_id():
    """Test that all patterns have doc_id field."""
    index_path = Path("patterns/registry/PATTERN_INDEX.yaml")
    with open(index_path) as f:
        data = yaml.safe_load(f)

    for pattern in data['patterns']:
        assert 'doc_id' in pattern, f"Pattern {pattern.get('pattern_id')} missing doc_id"
        assert pattern['doc_id'].startswith('DOC-'), f"Invalid doc_id format: {pattern['doc_id']}"
