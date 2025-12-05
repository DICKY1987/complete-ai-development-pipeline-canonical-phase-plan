"""Enhanced Bootstrap Validator with Contract Enforcement - Task 2.1"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from jsonschema import SchemaError, ValidationError, validate

from core.contracts import (
    PhaseContractValidator,
    ValidationResult,
    enforce_entry_contract,
    enforce_exit_contract,
)


class EnhancedBootstrapValidator:
    """Enhanced bootstrap validator with full contract enforcement"""

    def __init__(
        self,
        project_profile_path: Optional[str] = None,
        router_config_path: Optional[str] = None,
        profile_id: Optional[str] = None,
        repo_root: Optional[Path] = None,
    ):
        """
        Initialize enhanced bootstrap validator

        Args:
            project_profile_path: Path to PROJECT_PROFILE.yaml
            router_config_path: Path to router_config.json
            profile_id: Profile identifier
            repo_root: Repository root (defaults to current dir)
        """
        self.repo_root = repo_root or Path.cwd()
        self.project_profile_path = (
            Path(project_profile_path) if project_profile_path else None
        )
        self.router_config_path = (
            Path(router_config_path) if router_config_path else None
        )
        self.profile_id = profile_id

        # Contract validator
        self.contract_validator = PhaseContractValidator(repo_root=self.repo_root)

        # Tracking
        self.errors: List[Dict] = []
        self.warnings: List[Dict] = []
        self.auto_fixed: List[Dict] = []
        self.needs_human: List[Dict] = []

    @enforce_entry_contract(phase="phase0", dry_run=False)
    def validate_entry_contract(self, context: Optional[Dict] = None) -> Dict:
        """
        Validate Phase 0 entry contract

        Args:
            context: Optional context dict

        Returns:
            Validation result dict
        """
        result = self.contract_validator.validate_entry("phase0", context=context or {})

        if not result.valid:
            self.errors.extend(
                [
                    {
                        "type": v.type.value,
                        "message": v.message,
                        "remediation": v.remediation,
                    }
                    for v in result.violations
                ]
            )

        return result.to_dict()

    @enforce_exit_contract(phase="phase0", dry_run=False)
    def validate_exit_contract(
        self, artifacts: Optional[Dict] = None
    ) -> ValidationResult:
        """
        Validate Phase 0 exit contract

        Args:
            artifacts: Optional artifacts dict (events, files, etc.)

        Returns:
            ValidationResult
        """
        result = self.contract_validator.validate_exit(
            "phase0", artifacts=artifacts or {}
        )

        if not result.valid:
            self.errors.extend(
                [
                    {
                        "type": v.type.value,
                        "message": v.message,
                        "remediation": v.remediation,
                    }
                    for v in result.violations
                ]
            )

        return result

    def validate_all(self) -> Dict:
        """
        Run all validations (legacy method for compatibility)

        Returns:
            Validation result dict
        """
        # Load artifacts if paths provided
        if self.project_profile_path and self.project_profile_path.exists():
            with open(self.project_profile_path, "r", encoding="utf-8") as f:
                self.project_profile = yaml.safe_load(f)
        else:
            self.project_profile = None

        if self.router_config_path and self.router_config_path.exists():
            with open(self.router_config_path, "r", encoding="utf-8") as f:
                self.router_config = json.load(f)
        else:
            self.router_config = None

        # Validate schemas if artifacts exist
        if self.project_profile:
            self._validate_project_profile_schema()

        if self.router_config:
            self._validate_router_config_schema()

        # Check constraints
        self._check_constraints()

        # Auto-fix common issues
        self._auto_fix_common_issues()

        return {
            "valid": len(self.errors) == 0 and len(self.needs_human) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "auto_fixed": self.auto_fixed,
            "needs_human": self.needs_human,
        }

    def _validate_project_profile_schema(self):
        """Validate PROJECT_PROFILE.yaml against schema"""
        schema_path = self.repo_root / "schema" / "project_profile.v1.json"

        if not schema_path.exists():
            self.warnings.append(
                {
                    "type": "missing_schema",
                    "message": f"Schema not found: {schema_path}",
                }
            )
            return

        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                schema = json.load(f)

            validate(self.project_profile, schema)

        except ValidationError as e:
            self.errors.append(
                {
                    "type": "schema_validation",
                    "artifact": "PROJECT_PROFILE.yaml",
                    "message": e.message,
                    "path": ".".join(str(p) for p in e.path),
                }
            )
        except SchemaError as e:
            self.errors.append(
                {
                    "type": "schema_error",
                    "artifact": "project_profile.v1.json",
                    "message": str(e),
                }
            )

    def _validate_router_config_schema(self):
        """Validate router_config.json against schema"""
        schema_path = self.repo_root / "schema" / "router_config.v1.json"

        if not schema_path.exists():
            self.warnings.append(
                {
                    "type": "missing_schema",
                    "message": f"Schema not found: {schema_path}",
                }
            )
            return

        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                schema = json.load(f)

            validate(self.router_config, schema)

        except ValidationError as e:
            self.errors.append(
                {
                    "type": "schema_validation",
                    "artifact": "router_config.json",
                    "message": e.message,
                    "path": ".".join(str(p) for p in e.path),
                }
            )
        except SchemaError as e:
            self.errors.append(
                {
                    "type": "schema_error",
                    "artifact": "router_config.v1.json",
                    "message": str(e),
                }
            )

    def _check_constraints(self):
        """Check profile constraints"""
        if not self.project_profile:
            return

        # Check max_lines_changed
        max_lines = self.project_profile.get("constraints", {}).get("max_lines_changed")
        if max_lines and max_lines > 500:
            self.needs_human.append(
                {
                    "type": "relaxed_constraint",
                    "constraint": "max_lines_changed",
                    "value": max_lines,
                    "message": f"max_lines_changed relaxed to {max_lines} (recommended: 500)",
                }
            )

    def _auto_fix_common_issues(self):
        """Auto-fix common bootstrap issues"""
        # Create .state directory if missing
        state_dir = self.repo_root / ".state"
        if not state_dir.exists():
            try:
                state_dir.mkdir(parents=True)
                self.auto_fixed.append(
                    {
                        "type": "directory_created",
                        "path": str(state_dir),
                        "message": "Created .state directory",
                    }
                )
            except Exception as e:
                self.errors.append(
                    {
                        "type": "auto_fix_failed",
                        "message": f"Failed to create .state directory: {e}",
                    }
                )

        # Create .ledger directory if missing
        ledger_dir = self.repo_root / ".ledger"
        if not ledger_dir.exists():
            try:
                ledger_dir.mkdir(parents=True)
                self.auto_fixed.append(
                    {
                        "type": "directory_created",
                        "path": str(ledger_dir),
                        "message": "Created .ledger directory",
                    }
                )
            except Exception as e:
                self.errors.append(
                    {
                        "type": "auto_fix_failed",
                        "message": f"Failed to create .ledger directory: {e}",
                    }
                )

    def emit_bootstrap_complete_event(self) -> bool:
        """
        Emit BOOTSTRAP_COMPLETE event to state DB

        Returns:
            True if successful
        """
        db_path = self.repo_root / ".state" / "orchestration.db"

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Create events table if not exists
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    phase_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    details TEXT
                )
            """
            )

            # Insert BOOTSTRAP_COMPLETE event
            cursor.execute(
                """
                INSERT INTO events (event_type, phase_id, details)
                VALUES (?, ?, ?)
            """,
                (
                    "BOOTSTRAP_COMPLETE",
                    "phase0",
                    json.dumps({"profile_id": self.profile_id}),
                ),
            )

            conn.commit()
            conn.close()

            return True

        except sqlite3.Error as e:
            self.errors.append(
                {
                    "type": "database_error",
                    "message": f"Failed to emit BOOTSTRAP_COMPLETE event: {e}",
                }
            )
            return False

    def log_validation_results(self) -> bool:
        """
        Log validation results to .ledger/framework.db

        Returns:
            True if successful
        """
        ledger_path = self.repo_root / ".ledger" / "framework.db"

        try:
            conn = sqlite3.connect(ledger_path)
            cursor = conn.cursor()

            # Create validation_log table if not exists
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS validation_log (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phase_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    valid BOOLEAN NOT NULL,
                    errors_count INTEGER NOT NULL,
                    warnings_count INTEGER NOT NULL,
                    details TEXT
                )
            """
            )

            # Insert validation results
            cursor.execute(
                """
                INSERT INTO validation_log (phase_id, valid, errors_count, warnings_count, details)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    "phase0",
                    len(self.errors) == 0,
                    len(self.errors),
                    len(self.warnings),
                    json.dumps(
                        {
                            "errors": self.errors,
                            "warnings": self.warnings,
                            "auto_fixed": self.auto_fixed,
                        }
                    ),
                ),
            )

            conn.commit()
            conn.close()

            return True

        except sqlite3.Error as e:
            self.errors.append(
                {
                    "type": "database_error",
                    "message": f"Failed to log validation results: {e}",
                }
            )
            return False
