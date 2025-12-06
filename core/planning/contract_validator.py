"""Phase 1 (Planning) Contract Validator - Task 2.2"""
DOC_ID: DOC-CORE-PLANNING-CONTRACT-VALIDATOR-869

from pathlib import Path
from typing import Dict, List, Optional

from core.contracts import PhaseContractValidator, ValidationResult


class PlanningContractValidator:
    """Validates Phase 1 (Planning & Spec Alignment) entry/exit contracts"""

    def __init__(self, repo_root: Optional[Path] = None):
        """
        Initialize Planning contract validator

        Args:
            repo_root: Repository root path
        """
        self.repo_root = repo_root or Path.cwd()
        self.contract_validator = PhaseContractValidator(repo_root=self.repo_root)

    def validate_entry(self, context: Optional[Dict] = None) -> ValidationResult:
        """
        Validate Phase 1 entry requirements

        Entry requirements:
        - PROJECT_PROFILE.yaml exists (from phase0)
        - specifications/*.md files exist
        - bootstrap_state table exists
        - BOOTSTRAP_COMPLETE flag is set

        Args:
            context: Optional context dict

        Returns:
            ValidationResult
        """
        result = self.contract_validator.validate_entry("phase1", context=context or {})

        # Phase-specific validations
        specs_dir = self.repo_root / "specifications"
        if specs_dir.exists():
            spec_files = list(specs_dir.glob("*.md"))
            if len(spec_files) == 0:
                result.violations.append(
                    {
                        "type": "missing_file",
                        "message": "No specification files found in specifications/",
                        "remediation": "Add at least one .md file to specifications/",
                    }
                )
                result.valid = False

        return result

    def validate_exit(self, artifacts: Optional[Dict] = None) -> ValidationResult:
        """
        Validate Phase 1 exit artifacts

        Exit artifacts:
        - workstreams/*.json files created
        - .state/spec_index.json created
        - workstreams table populated
        - PLANNING_COMPLETE event emitted

        Args:
            artifacts: Optional artifacts dict (events, workstreams, etc.)

        Returns:
            ValidationResult
        """
        result = self.contract_validator.validate_exit(
            "phase1", artifacts=artifacts or {}
        )

        # Phase-specific validations
        workstreams_dir = self.repo_root / "workstreams"
        if workstreams_dir.exists():
            ws_files = list(workstreams_dir.glob("*.json"))
            if len(ws_files) == 0:
                result.violations.append(
                    {
                        "type": "missing_file",
                        "message": "No workstream JSON files found in workstreams/",
                        "remediation": "Phase 1 must generate at least one workstream",
                    }
                )
                result.valid = False

        # Check spec index
        spec_index = self.repo_root / ".state" / "spec_index.json"
        if not spec_index.exists():
            result.violations.append(
                {
                    "type": "missing_file",
                    "message": "Spec index not found: .state/spec_index.json",
                    "remediation": "Phase 1 must create spec index",
                }
            )
            result.valid = False

        return result

    def validate_workstream_count(self, min_count: int = 1) -> bool:
        """
        Validate minimum workstream count

        Args:
            min_count: Minimum expected workstreams

        Returns:
            True if sufficient workstreams exist
        """
        workstreams_dir = self.repo_root / "workstreams"
        if not workstreams_dir.exists():
            return False

        ws_count = len(list(workstreams_dir.glob("*.json")))
        return ws_count >= min_count

    def get_planning_metrics(self) -> Dict:
        """
        Get planning phase metrics

        Returns:
            Dict with spec count, workstream count, etc.
        """
        specs_dir = self.repo_root / "specifications"
        workstreams_dir = self.repo_root / "workstreams"

        return {
            "spec_count": (
                len(list(specs_dir.glob("*.md"))) if specs_dir.exists() else 0
            ),
            "workstream_count": (
                len(list(workstreams_dir.glob("*.json")))
                if workstreams_dir.exists()
                else 0
            ),
            "spec_index_exists": (
                self.repo_root / ".state" / "spec_index.json"
            ).exists(),
        }
