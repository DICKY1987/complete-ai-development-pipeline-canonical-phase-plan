"""Tests for contract enforcement decorators"""
DOC_ID: DOC-TEST-CONTRACTS-TEST-DECORATORS-372

import pytest

from core.contracts import (
    ContractViolationError,
    create_phase_decorator,
    enforce_entry_contract,
    enforce_exit_contract,
    validate_schema,
    with_contract_audit,
)
from core.contracts.validator import PhaseContractValidator


@pytest.fixture
def mock_validator(tmp_path):
    """Create validator with test repo structure"""
    # Create minimal test structure
    phase_dir = tmp_path / "phase0_test"
    phase_dir.mkdir()

    readme = phase_dir / "README.md"
    readme.write_text(
        """
# Phase 0

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
    - PROJECT_PROFILE.yaml
  updated_db_tables:
    - bootstrap_state
  emitted_events:
    - BOOTSTRAP_COMPLETE
"""
    )

    # Create .git directory
    (tmp_path / ".git").mkdir()

    # Create schema directory with test schema
    schema_dir = tmp_path / "schema"
    schema_dir.mkdir()

    import json

    test_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {"name": {"type": "string"}, "value": {"type": "integer"}},
        "required": ["name"],
    }
    (schema_dir / "test_data.v1.json").write_text(json.dumps(test_schema))

    return PhaseContractValidator(repo_root=tmp_path)


class TestEnforceEntryContract:
    """Test @enforce_entry_contract decorator"""

    def test_entry_contract_success(self, mock_validator):
        """Test successful entry contract validation"""

        @enforce_entry_contract(phase="phase0", validator=mock_validator)
        def my_function():
            return "success"

        # Should not raise
        result = my_function()
        assert result == "success"

    def test_entry_contract_failure(self, mock_validator, tmp_path):
        """Test entry contract violation raises error"""
        # Remove .git directory to cause violation
        import shutil

        shutil.rmtree(tmp_path / ".git")

        # Recreate validator after removing .git
        validator = PhaseContractValidator(repo_root=tmp_path)

        @enforce_entry_contract(phase="phase0", validator=validator)
        def my_function():
            return "should not execute"

        with pytest.raises(ContractViolationError) as exc_info:
            my_function()

        assert "Contract validation failed" in str(exc_info.value)

    def test_entry_contract_dry_run(self, mock_validator, tmp_path):
        """Test dry_run mode logs but doesn't raise"""
        # Remove .git to cause violation
        import shutil

        shutil.rmtree(tmp_path / ".git")

        validator = PhaseContractValidator(repo_root=tmp_path)

        @enforce_entry_contract(phase="phase0", validator=validator, dry_run=True)
        def my_function():
            return "executed despite violation"

        # Should not raise in dry_run mode
        result = my_function()
        assert result == "executed despite violation"

    def test_entry_contract_metadata(self, mock_validator):
        """Test decorator adds contract metadata"""

        @enforce_entry_contract(phase="phase0", validator=mock_validator)
        def my_function():
            pass

        assert hasattr(my_function, "_contract_phase")
        assert my_function._contract_phase == "phase0"
        assert my_function._contract_type == "entry"


class TestEnforceExitContract:
    """Test @enforce_exit_contract decorator"""

    def test_exit_contract_success(self, mock_validator, tmp_path):
        """Test successful exit contract validation"""
        # Create required output file
        (tmp_path / "PROJECT_PROFILE.yaml").write_text("test: profile")

        @enforce_exit_contract(phase="phase0", validator=mock_validator)
        def my_function():
            return "success"

        result = my_function()
        assert result == "success"

    def test_exit_contract_failure(self, mock_validator):
        """Test exit contract violation raises error"""

        @enforce_exit_contract(phase="phase0", validator=mock_validator)
        def my_function():
            return "should execute but fail validation"

        # Should execute function but fail on exit validation
        with pytest.raises(ContractViolationError) as exc_info:
            my_function()

        assert "Contract validation failed" in str(exc_info.value)

    def test_exit_contract_dry_run(self, mock_validator):
        """Test dry_run mode logs but doesn't raise"""

        @enforce_exit_contract(phase="phase0", validator=mock_validator, dry_run=True)
        def my_function():
            return "executed"

        # Should not raise in dry_run mode
        result = my_function()
        assert result == "executed"

    def test_exit_contract_strict_mode(self, mock_validator, tmp_path):
        """Test strict mode treats warnings as errors"""
        # Create output file to pass basic validation
        (tmp_path / "PROJECT_PROFILE.yaml").write_text("test: profile")

        @enforce_exit_contract(phase="phase0", validator=mock_validator, strict=False)
        def my_function():
            return {"events": []}  # Missing expected event - should be warning

        # Should not fail without strict mode
        result = my_function()
        assert result == {"events": []}

    def test_exit_contract_metadata(self, mock_validator):
        """Test decorator adds contract metadata"""

        @enforce_exit_contract(phase="phase0", validator=mock_validator)
        def my_function():
            pass

        assert hasattr(my_function, "_contract_phase")
        assert my_function._contract_phase == "phase0"
        assert my_function._contract_type == "exit"


class TestValidateSchema:
    """Test @validate_schema decorator"""

    def test_schema_validation_success(self, mock_validator):
        """Test successful schema validation"""

        @validate_schema(schema_name="test_data", validator=mock_validator)
        def my_function(data):
            return data

        valid_data = {"name": "test", "value": 42}
        result = my_function(valid_data)
        assert result == valid_data

    def test_schema_validation_failure(self, mock_validator):
        """Test schema validation failure"""

        @validate_schema(schema_name="test_data", validator=mock_validator)
        def my_function(data):
            return data

        # Missing required 'name' field
        invalid_data = {"value": 42}

        with pytest.raises(ContractViolationError) as exc_info:
            my_function(invalid_data)

        assert "Schema validation failed" in str(exc_info.value)

    def test_schema_validation_with_data_key(self, mock_validator):
        """Test schema validation with data_key parameter"""

        @validate_schema(
            schema_name="test_data", data_key="config", validator=mock_validator
        )
        def my_function(id, config):
            return config

        valid_data = {"name": "test", "value": 42}
        result = my_function(123, config=valid_data)
        assert result == valid_data

    def test_schema_validation_dry_run(self, mock_validator):
        """Test dry_run mode logs but doesn't raise"""

        @validate_schema(
            schema_name="test_data", validator=mock_validator, dry_run=True
        )
        def my_function(data):
            return "executed despite invalid data"

        invalid_data = {"value": 42}  # Missing 'name'

        # Should not raise in dry_run mode
        result = my_function(invalid_data)
        assert result == "executed despite invalid data"

    def test_schema_validation_metadata(self, mock_validator):
        """Test decorator adds schema metadata"""

        @validate_schema(
            schema_name="test_data", schema_version="v1", validator=mock_validator
        )
        def my_function(data):
            pass

        assert hasattr(my_function, "_schema_name")
        assert my_function._schema_name == "test_data"
        assert my_function._schema_version == "v1"


class TestWithContractAudit:
    """Test @with_contract_audit decorator"""

    def test_audit_logging(self, mock_validator, caplog):
        """Test audit logging works"""
        import logging

        caplog.set_level(logging.INFO, logger="contract_audit")

        @with_contract_audit()
        @enforce_entry_contract(phase="phase0", validator=mock_validator)
        def my_function():
            return "success"

        result = my_function()
        assert result == "success"

        # Check audit log contains contract info
        log_messages = [record.message for record in caplog.records]
        assert any("Contract validation" in msg for msg in log_messages)

    def test_audit_logging_on_failure(self, mock_validator, tmp_path, caplog):
        """Test audit logging on contract violation"""
        # Remove .git to cause violation
        import shutil

        shutil.rmtree(tmp_path / ".git")

        validator = PhaseContractValidator(repo_root=tmp_path)

        @with_contract_audit()
        @enforce_entry_contract(phase="phase0", validator=validator)
        def my_function():
            pass

        with pytest.raises(ContractViolationError):
            my_function()

        # Check audit log contains failure info
        assert any("Validation failed" in record.message for record in caplog.records)


class TestCreatePhaseDecorator:
    """Test create_phase_decorator helper"""

    def test_create_phase_decorator(self, mock_validator):
        """Test creating phase-specific decorators"""

        entry, exit = create_phase_decorator("phase0", validator=mock_validator)

        @entry()
        def start_phase():
            return "started"

        @exit()
        def end_phase():
            return "ended"

        # Both should work
        assert start_phase() == "started"

        # Exit will fail due to missing artifacts but function executes
        with pytest.raises(ContractViolationError):
            end_phase()


class TestDecoratorComposition:
    """Test combining multiple decorators"""

    def test_entry_and_schema_validation(self, mock_validator):
        """Test combining entry contract and schema validation"""

        @enforce_entry_contract(phase="phase0", validator=mock_validator)
        @validate_schema(schema_name="test_data", validator=mock_validator)
        def my_function(data):
            return data

        valid_data = {"name": "test", "value": 42}
        result = my_function(valid_data)
        assert result == valid_data

    def test_full_stack_decorators(self, mock_validator, tmp_path):
        """Test full decorator stack with audit"""
        (tmp_path / "PROJECT_PROFILE.yaml").write_text("test: profile")

        @with_contract_audit()
        @enforce_exit_contract(phase="phase0", validator=mock_validator)
        @enforce_entry_contract(phase="phase0", validator=mock_validator)
        def my_function():
            return "success"

        result = my_function()
        assert result == "success"
