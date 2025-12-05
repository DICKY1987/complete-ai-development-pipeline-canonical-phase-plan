"""
Phase Contract Enforcement Framework

Provides automated validation of phase entry/exit contracts across
the 8-phase pipeline (Phases 0-7).
"""

from .decorators import (
    ContractViolationError,
    create_phase_decorator,
    enforce_entry_contract,
    enforce_exit_contract,
    validate_schema,
    with_contract_audit,
)
from .schema_registry import SchemaRegistry
from .validator import PhaseContractValidator, ValidationResult

__all__ = [
    "PhaseContractValidator",
    "ValidationResult",
    "SchemaRegistry",
    "enforce_entry_contract",
    "enforce_exit_contract",
    "validate_schema",
    "with_contract_audit",
    "create_phase_decorator",
    "ContractViolationError",
]
