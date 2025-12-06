"""Type definitions for contract enforcement

DOC_ID: DOC-CORE-CONTRACTS-TYPES-862
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Severity(Enum):
    """Validation issue severity"""

    ERROR = "error"  # Blocks execution
    WARNING = "warning"  # Logs but allows execution
    INFO = "info"  # Informational only


class ViolationType(Enum):
    """Types of contract violations"""

    MISSING_FILE = "missing_file"
    MISSING_DB_TABLE = "missing_db_table"
    MISSING_STATE_FLAG = "missing_state_flag"
    INVALID_SCHEMA = "invalid_schema"
    MISSING_EVENT = "missing_event"
    CONSTRAINT_VIOLATION = "constraint_violation"
    DEPENDENCY_ERROR = "dependency_error"


@dataclass
class Violation:
    """Single contract violation"""

    type: ViolationType
    severity: Severity
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    remediation: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "type": self.type.value,
            "severity": self.severity.value,
            "message": self.message,
            "details": self.details,
            "remediation": self.remediation,
        }


@dataclass
class ValidationResult:
    """Result of contract validation"""

    phase_id: str
    contract_type: str  # "entry" | "exit"
    valid: bool
    violations: List[Violation] = field(default_factory=list)
    warnings: List[Violation] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def has_errors(self) -> bool:
        """Check if result has errors"""
        return any(v.severity == Severity.ERROR for v in self.violations)

    @property
    def has_warnings(self) -> bool:
        """Check if result has warnings"""
        return any(v.severity == Severity.WARNING for v in self.violations)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "phase_id": self.phase_id,
            "contract_type": self.contract_type,
            "valid": self.valid,
            "violations": [v.to_dict() for v in self.violations],
            "warnings": [w.to_dict() for w in self.warnings],
            "metadata": self.metadata,
        }


@dataclass
class PhaseContract:
    """Phase contract definition"""

    phase_id: str
    entry_requirements: Dict[str, List[str]]
    exit_artifacts: Dict[str, List[str]]

    @classmethod
    def from_readme(cls, readme_path: str) -> "PhaseContract":
        """Parse phase contract from README.md"""
        # Implementation in validator.py
        raise NotImplementedError
