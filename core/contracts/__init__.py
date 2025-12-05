"""
Phase Contract Enforcement Framework

Provides automated validation of phase entry/exit contracts across
the 8-phase pipeline (Phases 0-7).
"""

from .schema_registry import SchemaRegistry
from .validator import PhaseContractValidator, ValidationResult

__all__ = ["PhaseContractValidator", "ValidationResult", "SchemaRegistry"]
