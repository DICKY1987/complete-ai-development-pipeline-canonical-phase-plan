"""Phase Contract Validator - Core validation engine

DOC_ID: DOC-CORE-CONTRACTS-VALIDATOR-863
"""

import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .types import PhaseContract, Severity, ValidationResult, Violation, ViolationType


class PhaseContractValidator:
    """Validates phase entry/exit contracts"""

    def __init__(self, repo_root: Optional[Path] = None):
        """
        Initialize validator

        Args:
            repo_root: Repository root path (defaults to current dir)
        """
        self.repo_root = repo_root or Path.cwd()
        self.contracts: Dict[str, PhaseContract] = {}
        self._load_contracts()

    def _load_contracts(self):
        """Load all phase contracts from README files"""
        for phase_id in range(8):  # Phases 0-7
            phase_dir = self.repo_root / f"phase{phase_id}_*"
            # Find phase directory using glob
            matches = list(self.repo_root.glob(f"phase{phase_id}_*"))
            if matches:
                readme_path = matches[0] / "README.md"
                if readme_path.exists():
                    try:
                        contract = self._parse_contract_from_readme(
                            f"phase{phase_id}", readme_path
                        )
                        self.contracts[f"phase{phase_id}"] = contract
                    except Exception as e:
                        # Log warning but continue
                        print(
                            f"Warning: Failed to load contract for phase{phase_id}: {e}"
                        )

    def _parse_contract_from_readme(
        self, phase_id: str, readme_path: Path
    ) -> PhaseContract:
        """Parse phase contract from README.md YAML sections"""
        content = readme_path.read_text(encoding="utf-8")

        # Extract YAML blocks from README
        entry_pattern = r"entry_requirements:\s*\n((?:  .*\n)*)"
        exit_pattern = r"exit_artifacts:\s*\n((?:  .*\n)*)"

        entry_match = re.search(entry_pattern, content)
        exit_match = re.search(exit_pattern, content)

        entry_requirements = {}
        exit_artifacts = {}

        if entry_match:
            entry_yaml = "entry_requirements:\n" + entry_match.group(1)
            try:
                parsed = yaml.safe_load(entry_yaml)
                entry_requirements = parsed.get("entry_requirements", {})
            except yaml.YAMLError:
                pass

        if exit_match:
            exit_yaml = "exit_artifacts:\n" + exit_match.group(1)
            try:
                parsed = yaml.safe_load(exit_yaml)
                exit_artifacts = parsed.get("exit_artifacts", {})
            except yaml.YAMLError:
                pass

        return PhaseContract(
            phase_id=phase_id,
            entry_requirements=entry_requirements,
            exit_artifacts=exit_artifacts,
        )

    def validate_entry(
        self, phase_id: str, context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate phase entry requirements

        Args:
            phase_id: Phase identifier (e.g., "phase0", "phase1")
            context: Optional context for validation

        Returns:
            ValidationResult with violations and warnings
        """
        context = context or {}
        violations = []
        warnings = []

        contract = self.contracts.get(phase_id)
        if not contract:
            violations.append(
                Violation(
                    type=ViolationType.MISSING_FILE,
                    severity=Severity.ERROR,
                    message=f"No contract found for {phase_id}",
                    details={"phase_id": phase_id},
                    remediation=f"Create {phase_id}/README.md with contract definition",
                )
            )
            return ValidationResult(
                phase_id=phase_id,
                contract_type="entry",
                valid=False,
                violations=violations,
            )

        # Validate required files
        required_files = contract.entry_requirements.get("required_files", [])
        for file_req in required_files:
            # Parse file requirement (may include description)
            file_path = file_req.split("(")[0].strip()
            if file_path == "None":
                continue

            full_path = self.repo_root / file_path
            if not full_path.exists():
                violations.append(
                    Violation(
                        type=ViolationType.MISSING_FILE,
                        severity=Severity.ERROR,
                        message=f"Required file missing: {file_path}",
                        details={"file": file_path, "phase": phase_id},
                        remediation=f"Create or verify path: {full_path}",
                    )
                )

        # Validate required DB tables
        required_tables = contract.entry_requirements.get("required_db_tables", [])
        if required_tables and "None" not in required_tables:
            db_path = self.repo_root / ".state" / "orchestration.db"
            if db_path.exists():
                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()

                    for table_req in required_tables:
                        # Parse table requirement
                        table_name = table_req.split("(")[0].strip()
                        cursor.execute(
                            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                            (table_name,),
                        )
                        if not cursor.fetchone():
                            violations.append(
                                Violation(
                                    type=ViolationType.MISSING_DB_TABLE,
                                    severity=Severity.ERROR,
                                    message=f"Required DB table missing: {table_name}",
                                    details={"table": table_name, "phase": phase_id},
                                    remediation=f"Run previous phase to create {table_name}",
                                )
                            )

                    conn.close()
                except sqlite3.Error as e:
                    warnings.append(
                        Violation(
                            type=ViolationType.DEPENDENCY_ERROR,
                            severity=Severity.WARNING,
                            message=f"Could not validate DB tables: {e}",
                            details={"error": str(e)},
                        )
                    )
            else:
                if required_tables:
                    violations.append(
                        Violation(
                            type=ViolationType.MISSING_FILE,
                            severity=Severity.ERROR,
                            message="Database file missing: .state/orchestration.db",
                            details={"file": str(db_path)},
                            remediation="Run bootstrap phase to initialize database",
                        )
                    )

        # Validate required state flags
        required_flags = contract.entry_requirements.get("required_state_flags", [])
        if required_flags and "None" not in required_flags:
            # Check state flags in DB or context
            for flag in required_flags:
                if not context.get(flag):
                    violations.append(
                        Violation(
                            type=ViolationType.MISSING_STATE_FLAG,
                            severity=Severity.ERROR,
                            message=f"Required state flag not set: {flag}",
                            details={"flag": flag, "phase": phase_id},
                            remediation=f"Complete previous phase to set {flag} flag",
                        )
                    )

        valid = len(violations) == 0
        return ValidationResult(
            phase_id=phase_id,
            contract_type="entry",
            valid=valid,
            violations=violations,
            warnings=warnings,
            metadata={"contract": contract.__dict__},
        )

    def validate_exit(
        self, phase_id: str, artifacts: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate phase exit artifacts

        Args:
            phase_id: Phase identifier
            artifacts: Optional artifacts dict for validation

        Returns:
            ValidationResult with violations and warnings
        """
        artifacts = artifacts or {}
        violations = []
        warnings = []

        contract = self.contracts.get(phase_id)
        if not contract:
            violations.append(
                Violation(
                    type=ViolationType.MISSING_FILE,
                    severity=Severity.ERROR,
                    message=f"No contract found for {phase_id}",
                    details={"phase_id": phase_id},
                )
            )
            return ValidationResult(
                phase_id=phase_id,
                contract_type="exit",
                valid=False,
                violations=violations,
            )

        # Validate produced files
        produced_files = contract.exit_artifacts.get("produced_files", [])
        for file_req in produced_files:
            # Parse file requirement
            file_path = file_req.split("(")[0].strip()

            full_path = self.repo_root / file_path
            if not full_path.exists():
                violations.append(
                    Violation(
                        type=ViolationType.MISSING_FILE,
                        severity=Severity.ERROR,
                        message=f"Expected output file missing: {file_path}",
                        details={"file": file_path, "phase": phase_id},
                        remediation=f"Phase {phase_id} must create {file_path}",
                    )
                )

        # Validate updated DB tables
        updated_tables = contract.exit_artifacts.get("updated_db_tables", [])
        if updated_tables:
            db_path = self.repo_root / ".state" / "orchestration.db"
            if db_path.exists():
                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()

                    for table_req in updated_tables:
                        # Parse table requirement
                        table_name = table_req.split("(")[0].strip()
                        cursor.execute(
                            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                            (table_name,),
                        )
                        if not cursor.fetchone():
                            violations.append(
                                Violation(
                                    type=ViolationType.MISSING_DB_TABLE,
                                    severity=Severity.ERROR,
                                    message=f"Expected DB table not created: {table_name}",
                                    details={"table": table_name, "phase": phase_id},
                                    remediation=f"Phase {phase_id} must create/update {table_name}",
                                )
                            )

                    conn.close()
                except sqlite3.Error as e:
                    warnings.append(
                        Violation(
                            type=ViolationType.DEPENDENCY_ERROR,
                            severity=Severity.WARNING,
                            message=f"Could not validate DB tables: {e}",
                            details={"error": str(e)},
                        )
                    )

        # Validate emitted events
        emitted_events = contract.exit_artifacts.get("emitted_events", [])
        if emitted_events and artifacts.get("events"):
            for event in emitted_events:
                if event not in artifacts["events"]:
                    violations.append(
                        Violation(
                            type=ViolationType.MISSING_EVENT,
                            severity=Severity.WARNING,
                            message=f"Expected event not emitted: {event}",
                            details={"event": event, "phase": phase_id},
                            remediation=f"Phase {phase_id} should emit {event} event",
                        )
                    )

        valid = len(violations) == 0
        return ValidationResult(
            phase_id=phase_id,
            contract_type="exit",
            valid=valid,
            violations=violations,
            warnings=warnings,
            metadata={"contract": contract.__dict__},
        )

    def validate_schema(
        self, data: Dict[str, Any], schema_name: str, schema_version: str = "v1"
    ) -> ValidationResult:
        """
        Validate data against versioned schema

        Args:
            data: Data to validate
            schema_name: Schema name (e.g., "execution_request")
            schema_version: Schema version (e.g., "v1")

        Returns:
            ValidationResult
        """
        violations = []

        schema_path = self.repo_root / "schema" / f"{schema_name}.{schema_version}.json"

        if not schema_path.exists():
            violations.append(
                Violation(
                    type=ViolationType.MISSING_FILE,
                    severity=Severity.ERROR,
                    message=f"Schema file not found: {schema_path.name}",
                    details={"schema": schema_name, "version": schema_version},
                    remediation=f"Create schema file at {schema_path}",
                )
            )
            return ValidationResult(
                phase_id="schema_validation",
                contract_type="schema",
                valid=False,
                violations=violations,
            )

        # Use jsonschema for validation
        try:
            import json

            from jsonschema import ValidationError, validate

            with open(schema_path, "r", encoding="utf-8") as f:
                schema = json.load(f)

            validate(instance=data, schema=schema)

            return ValidationResult(
                phase_id="schema_validation",
                contract_type="schema",
                valid=True,
                metadata={"schema": schema_name, "version": schema_version},
            )

        except ValidationError as e:
            violations.append(
                Violation(
                    type=ViolationType.INVALID_SCHEMA,
                    severity=Severity.ERROR,
                    message=f"Schema validation failed: {e.message}",
                    details={
                        "schema": schema_name,
                        "version": schema_version,
                        "path": ".".join(str(p) for p in e.path),
                    },
                    remediation="Fix data to match schema requirements",
                )
            )
            return ValidationResult(
                phase_id="schema_validation",
                contract_type="schema",
                valid=False,
                violations=violations,
            )
        except Exception as e:
            violations.append(
                Violation(
                    type=ViolationType.INVALID_SCHEMA,
                    severity=Severity.ERROR,
                    message=f"Validation error: {str(e)}",
                    details={"error": str(e)},
                )
            )
            return ValidationResult(
                phase_id="schema_validation",
                contract_type="schema",
                valid=False,
                violations=violations,
            )
