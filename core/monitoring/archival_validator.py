"""Phase 7 (Monitoring) Contract Validator - Task 2.8

DOC_ID: DOC-CORE-MONITORING-ARCHIVAL-VALIDATOR-850
"""

import sqlite3
from pathlib import Path
from typing import Dict, Optional

from core.contracts import PhaseContractValidator, ValidationResult


class MonitoringContractValidator:
    """Validates Phase 7 (Monitoring & Archival) entry/exit contracts"""

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path.cwd()
        self.contract_validator = PhaseContractValidator(repo_root=self.repo_root)

    def validate_entry(self, context: Optional[Dict] = None) -> ValidationResult:
        """Validate Phase 7 entry requirements"""
        return self.contract_validator.validate_entry("phase7", context=context or {})

    def validate_exit(self, artifacts: Optional[Dict] = None) -> ValidationResult:
        """Validate Phase 7 exit artifacts"""
        result = self.contract_validator.validate_exit(
            "phase7", artifacts=artifacts or {}
        )

        run_id = (artifacts or {}).get("run_id")
        if run_id:
            archive_dir = self.repo_root / ".archive" / run_id
            if not archive_dir.exists():
                result.violations.append(
                    {"type": "missing_file", "message": f"Archive not found: {run_id}"}
                )
                result.valid = False

        return result
