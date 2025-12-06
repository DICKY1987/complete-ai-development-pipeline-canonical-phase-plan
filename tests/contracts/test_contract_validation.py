"""Tests for contract enforcement framework"""
DOC_ID: DOC-TEST-CONTRACTS-TEST-CONTRACT-VALIDATION-373

from pathlib import Path

import pytest

from core.contracts import PhaseContractValidator, SchemaRegistry, ValidationResult
from core.contracts.types import Severity, ViolationType


@pytest.fixture
def repo_root(tmp_path):
    """Create temporary repo structure"""
    # Create phase directories
    for i in range(8):
        phase_dir = tmp_path / f"phase{i}_test"
        phase_dir.mkdir()

        # Create README with contract
        readme = phase_dir / "README.md"
        readme.write_text(
            f"""
# Phase {i}

## Phase Contracts

entry_requirements:
  required_files:
    - .git/
  required_db_tables:
    - None
  required_state_flags:
    - None
exit_artifacts:
  produced_files:
    - test_output.txt
  updated_db_tables:
    - test_table
  emitted_events:
    - TEST_EVENT
"""
        )

    # Create .git directory
    (tmp_path / ".git").mkdir()

    # Create schema directory
    schema_dir = tmp_path / "schema"
    schema_dir.mkdir()

    # Create test schema
    import json

    test_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {"name": {"type": "string"}, "value": {"type": "integer"}},
        "required": ["name"],
    }

    (schema_dir / "test_schema.v1.json").write_text(json.dumps(test_schema))

    return tmp_path


class TestPhaseContractValidator:
    """Test PhaseContractValidator"""

    def test_init(self, repo_root):
        """Test validator initialization"""
        validator = PhaseContractValidator(repo_root=repo_root)
        assert len(validator.contracts) > 0

    def test_validate_entry_success(self, repo_root):
        """Test successful entry validation"""
        validator = PhaseContractValidator(repo_root=repo_root)

        result = validator.validate_entry("phase0", context={})

        assert isinstance(result, ValidationResult)
        assert result.phase_id == "phase0"
        assert result.contract_type == "entry"
        # Should pass because .git/ exists

    def test_validate_entry_missing_file(self, repo_root):
        """Test entry validation with missing file"""
        # Remove .git directory
        import shutil

        shutil.rmtree(repo_root / ".git")

        validator = PhaseContractValidator(repo_root=repo_root)
        result = validator.validate_entry("phase0", context={})

        assert not result.valid
        assert len(result.violations) > 0
        assert any(v.type == ViolationType.MISSING_FILE for v in result.violations)

    def test_validate_exit_missing_file(self, repo_root):
        """Test exit validation with missing output file"""
        validator = PhaseContractValidator(repo_root=repo_root)

        result = validator.validate_exit("phase0", artifacts={})

        assert not result.valid
        assert len(result.violations) > 0
        # test_output.txt should be missing

    def test_validate_schema_success(self, repo_root):
        """Test successful schema validation"""
        validator = PhaseContractValidator(repo_root=repo_root)

        data = {"name": "test", "value": 42}
        result = validator.validate_schema(data, "test_schema", "v1")

        assert result.valid
        assert len(result.violations) == 0

    def test_validate_schema_failure(self, repo_root):
        """Test failed schema validation"""
        validator = PhaseContractValidator(repo_root=repo_root)

        # Missing required 'name' field
        data = {"value": 42}
        result = validator.validate_schema(data, "test_schema", "v1")

        assert not result.valid
        assert len(result.violations) > 0
        assert any(v.type == ViolationType.INVALID_SCHEMA for v in result.violations)


class TestSchemaRegistry:
    """Test SchemaRegistry"""

    def test_init(self, repo_root):
        """Test registry initialization"""
        registry = SchemaRegistry(schema_dir=repo_root / "schema")
        assert "test_schema" in registry.schemas
        assert "v1" in registry.schemas["test_schema"]

    def test_get_schema(self, repo_root):
        """Test getting schema by name and version"""
        registry = SchemaRegistry(schema_dir=repo_root / "schema")

        schema = registry.get_schema("test_schema", "v1")
        assert schema is not None
        assert schema["type"] == "object"
        assert "name" in schema["properties"]

    def test_get_latest_version(self, repo_root):
        """Test getting latest schema version"""
        schema_dir = repo_root / "schema"

        # Create v2 schema
        import json

        v2_schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        (schema_dir / "test_schema.v2.json").write_text(json.dumps(v2_schema))

        registry = SchemaRegistry(schema_dir=schema_dir)
        latest = registry.get_latest_version("test_schema")

        assert latest == "v2"

    def test_list_schemas(self, repo_root):
        """Test listing all schemas"""
        registry = SchemaRegistry(schema_dir=repo_root / "schema")

        schemas = registry.list_schemas()
        assert len(schemas) >= 1
        assert all(hasattr(s, "name") and hasattr(s, "version") for s in schemas)

    def test_validate_compatibility_compatible(self, repo_root):
        """Test compatible schema upgrade"""
        schema_dir = repo_root / "schema"

        # Create v2 with additional optional field
        import json

        v2_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "value": {"type": "integer"},
                "extra": {"type": "string"},
            },
            "required": ["name"],
        }
        (schema_dir / "test_schema.v2.json").write_text(json.dumps(v2_schema))

        registry = SchemaRegistry(schema_dir=schema_dir)
        result = registry.validate_compatibility("test_schema", "v1", "v2")

        assert result.compatible
        assert len(result.breaking_changes) == 0

    def test_validate_compatibility_breaking(self, repo_root):
        """Test incompatible schema upgrade"""
        schema_dir = repo_root / "schema"

        # Create v2 with new required field (breaking change)
        import json

        v2_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "value": {"type": "integer"},
                "required_field": {"type": "string"},
            },
            "required": ["name", "required_field"],
        }
        (schema_dir / "test_schema.v2.json").write_text(json.dumps(v2_schema))

        registry = SchemaRegistry(schema_dir=schema_dir)
        result = registry.validate_compatibility("test_schema", "v1", "v2")

        assert not result.compatible
        assert len(result.breaking_changes) > 0
