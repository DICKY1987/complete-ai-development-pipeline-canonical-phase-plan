"""
Tests for doc-meta.v1.json schema validation.
"""

import json
import pytest
from pathlib import Path

pytest.importorskip("jsonschema")
from jsonschema import validate, ValidationError, Draft7Validator

SCHEMA_PATH = Path(__file__).parent.parent.parent / "schema" / "doc-meta.v1.json"
with open(SCHEMA_PATH, "r") as f:
    DOC_META_SCHEMA = json.load(f)

def test_schema_is_valid():
    """Verify the schema itself is valid."""
    Draft7Validator.check_schema(DOC_META_SCHEMA)

def test_minimal_valid_doc_meta():
    """Test minimal valid document metadata."""
    valid_meta = {
        "meta_version": "doc-meta.v1",
        "doc_ulid": "01JDCQM8XZABCDEFGHJKMNPQRS",
        "doc_type": "core_spec",
        "doc_layer": "framework",
        "title": "Test Document",
        "summary": "A test document for validation.",
        "version": "1.0.0",
        "status": "active",
        "schema_ref": "schema/test.v1.json",
        "created_at": "2025-11-20T20:00:00Z",
        "updated_at": "2025-11-20T20:00:00Z",
        "author_type": "ai",
        "owner": "SYSTEM:TEST",
        "security_tier": "internal"
    }
    validate(instance=valid_meta, schema=DOC_META_SCHEMA)

def test_invalid_ulid_format():
    """Test that invalid ULID is rejected."""
    invalid_meta = {
        "meta_version": "doc-meta.v1",
        "doc_ulid": "invalid-ulid-123",
        "doc_type": "core_spec",
        "doc_layer": "framework",
        "title": "Test",
        "summary": "Test.",
        "version": "1.0.0",
        "status": "active",
        "schema_ref": "schema/test.v1.json",
        "created_at": "2025-11-20T20:00:00Z",
        "updated_at": "2025-11-20T20:00:00Z",
        "author_type": "ai",
        "owner": "SYSTEM:TEST",
        "security_tier": "internal"
    }
    with pytest.raises(ValidationError):
        validate(instance=invalid_meta, schema=DOC_META_SCHEMA)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
