"""Contract Enforcement Decorators - Automatic validation at function boundaries

DOC_ID: DOC-CORE-CONTRACTS-DECORATORS-864
"""

import functools
import logging
from typing import Any, Callable, Dict, Optional

from .types import Severity, ValidationResult, Violation, ViolationType
from .validator import PhaseContractValidator

logger = logging.getLogger(__name__)


class ContractViolationError(Exception):
    """Raised when contract validation fails"""

    def __init__(self, result: ValidationResult):
        self.result = result
        messages = [
            v.message for v in result.violations if v.severity == Severity.ERROR
        ]
        super().__init__(f"Contract validation failed: {'; '.join(messages)}")


def enforce_entry_contract(
    phase: str,
    validator: Optional[PhaseContractValidator] = None,
    dry_run: bool = False,
):
    """
    Decorator to enforce phase entry contract

    Args:
        phase: Phase identifier (e.g., "phase0", "phase1")
        validator: Optional validator instance (creates new if None)
        dry_run: If True, logs violations but doesn't raise exception

    Example:
        @enforce_entry_contract(phase="phase2_request_building")
        def create_execution_request(workstream_id: str) -> ExecutionRequest:
            # Entry contract automatically validated
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get or create validator
            _validator = validator or PhaseContractValidator()

            # Extract context from kwargs if present
            context = kwargs.get("context", {})

            # Validate entry contract
            result = _validator.validate_entry(phase, context=context)

            if not result.valid:
                error_msg = f"Entry contract violation for {phase}: {len(result.violations)} errors"
                logger.error(error_msg)

                for violation in result.violations:
                    logger.error(
                        f"  [{violation.type.value}] {violation.message}"
                        + (
                            f" -> {violation.remediation}"
                            if violation.remediation
                            else ""
                        )
                    )

                if not dry_run:
                    raise ContractViolationError(result)
                else:
                    logger.warning(
                        f"DRY RUN: Would have raised ContractViolationError for {phase}"
                    )

            # Log warnings
            for warning in result.warnings:
                logger.warning(f"  [{warning.type.value}] {warning.message}")

            # Execute function
            return func(*args, **kwargs)

        # Store contract metadata on function
        wrapper._contract_phase = phase  # type: ignore
        wrapper._contract_type = "entry"  # type: ignore

        return wrapper

    return decorator


def enforce_exit_contract(
    phase: str,
    validator: Optional[PhaseContractValidator] = None,
    dry_run: bool = False,
    strict: bool = False,
):
    """
    Decorator to enforce phase exit contract

    Args:
        phase: Phase identifier
        validator: Optional validator instance
        dry_run: If True, logs violations but doesn't raise
        strict: If True, treats warnings as errors

    Example:
        @enforce_exit_contract(phase="phase2_request_building")
        def finalize_run(run_id: str) -> RunRecord:
            # Exit contract automatically validated after execution
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Execute function first
            result_value = func(*args, **kwargs)

            # Get or create validator
            _validator = validator or PhaseContractValidator()

            # Extract artifacts from kwargs or result
            artifacts = kwargs.get("artifacts", {})

            # If result is a dict, merge it into artifacts
            if isinstance(result_value, dict):
                artifacts = {**artifacts, **result_value}

            # Validate exit contract
            validation_result = _validator.validate_exit(phase, artifacts=artifacts)

            if not validation_result.valid:
                error_msg = f"Exit contract violation for {phase}: {len(validation_result.violations)} errors"
                logger.error(error_msg)

                for violation in validation_result.violations:
                    logger.error(
                        f"  [{violation.type.value}] {violation.message}"
                        + (
                            f" -> {violation.remediation}"
                            if violation.remediation
                            else ""
                        )
                    )

                if not dry_run:
                    raise ContractViolationError(validation_result)
                else:
                    logger.warning(
                        f"DRY RUN: Would have raised ContractViolationError for {phase}"
                    )

            # Handle warnings
            for warning in validation_result.warnings:
                if strict:
                    logger.error(f"STRICT MODE: {warning.message}")
                    if not dry_run:
                        raise ContractViolationError(validation_result)
                else:
                    logger.warning(f"  [{warning.type.value}] {warning.message}")

            return result_value

        # Store contract metadata on function
        wrapper._contract_phase = phase  # type: ignore
        wrapper._contract_type = "exit"  # type: ignore

        return wrapper

    return decorator


def validate_schema(
    schema_name: str,
    schema_version: str = "v1",
    data_key: Optional[str] = None,
    validator: Optional[PhaseContractValidator] = None,
    dry_run: bool = False,
):
    """
    Decorator to validate data against schema

    Args:
        schema_name: Schema name (e.g., "execution_request")
        schema_version: Schema version (default: "v1")
        data_key: Key in kwargs to validate (if None, validates first arg)
        validator: Optional validator instance
        dry_run: If True, logs violations but doesn't raise

    Example:
        @validate_schema(schema="ExecutionRequestV1")
        def build_request(data: dict) -> ExecutionRequest:
            # Data automatically validated against schema
            pass

        # Or with data_key:
        @validate_schema(schema="RunRecordV1", data_key="run_data")
        def create_run(run_id: str, run_data: dict) -> RunRecord:
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get or create validator
            _validator = validator or PhaseContractValidator()

            # Extract data to validate
            if data_key:
                if data_key not in kwargs:
                    raise ValueError(
                        f"data_key '{data_key}' not found in function kwargs"
                    )
                data = kwargs[data_key]
            else:
                if not args:
                    raise ValueError(
                        "No arguments provided to validate (use data_key if data is in kwargs)"
                    )
                data = args[0]

            # Validate against schema
            result = _validator.validate_schema(data, schema_name, schema_version)

            if not result.valid:
                error_msg = (
                    f"Schema validation failed for {schema_name}.{schema_version}"
                )
                logger.error(error_msg)

                for violation in result.violations:
                    logger.error(f"  {violation.message}")
                    if violation.details:
                        logger.error(f"    Details: {violation.details}")

                if not dry_run:
                    raise ContractViolationError(result)
                else:
                    logger.warning(
                        f"DRY RUN: Would have raised ContractViolationError for schema {schema_name}"
                    )

            # Execute function
            return func(*args, **kwargs)

        # Store schema metadata on function
        wrapper._schema_name = schema_name  # type: ignore
        wrapper._schema_version = schema_version  # type: ignore

        return wrapper

    return decorator


def with_contract_audit(audit_logger: Optional[logging.Logger] = None):
    """
    Decorator to log contract validation to audit trail

    Args:
        audit_logger: Logger for audit trail (uses default if None)

    Example:
        @with_contract_audit()
        @enforce_entry_contract(phase="phase2")
        def my_function():
            pass
    """
    _audit_logger = audit_logger or logging.getLogger("contract_audit")

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get contract metadata if present
            phase = getattr(func, "_contract_phase", None)
            contract_type = getattr(func, "_contract_type", None)
            schema_name = getattr(func, "_schema_name", None)

            # Log entry
            if phase:
                _audit_logger.info(
                    f"Contract validation: {func.__name__} ({phase} {contract_type})"
                )
            elif schema_name:
                _audit_logger.info(
                    f"Schema validation: {func.__name__} ({schema_name})"
                )

            # Execute function
            try:
                result = func(*args, **kwargs)
                _audit_logger.info(f"  ✅ Validation passed")
                return result
            except ContractViolationError as e:
                _audit_logger.error(f"  ❌ Validation failed: {e}")
                raise

        return wrapper

    return decorator


# Convenience function for creating pre-configured decorators
def create_phase_decorator(
    phase: str, validator: Optional[PhaseContractValidator] = None
):
    """
    Create entry/exit decorators pre-configured for a specific phase

    Args:
        phase: Phase identifier
        validator: Optional validator instance

    Returns:
        Tuple of (entry_decorator, exit_decorator)

    Example:
        entry, exit = create_phase_decorator("phase2_request_building")

        @entry
        def start_request_building():
            pass

        @exit
        def finish_request_building():
            pass
    """
    entry_dec = functools.partial(
        enforce_entry_contract, phase=phase, validator=validator
    )
    exit_dec = functools.partial(
        enforce_exit_contract, phase=phase, validator=validator
    )

    return entry_dec, exit_dec
