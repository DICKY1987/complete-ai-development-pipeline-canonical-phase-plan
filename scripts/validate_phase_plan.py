#!/usr/bin/env python
"""
validate_phase_plan.py

PAT-CHECK-001-aligned validator for SPLINTER Phase Plans.

Validation order:

1. Pattern Registry & GH_SYNC pattern:
   - patterns/registry/PATTERN_INDEX.yaml
   - patterns/specs/GH_SYNC_PHASE_V1.pattern.yaml
   - patterns/schemas/GH_SYNC_PHASE_V1.schema.json

2. Full Phase Plan schema:
   - patterns/schemas/SPLINTER_PHASE_PLAN_V1.schema.json

3. Nested github_integration block:
   - validate via GH_SYNC_PHASE_V1.schema.json

Outputs a machine-readable JSON report to stdout.
"""

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml  # pip install pyyaml
from jsonschema import Draft7Validator  # pip install jsonschema

# =========================
# DATA MODELS
# =========================


@dataclass
class CheckResult:
    id: str
    description: str
    status: str  # "PASS" | "FAIL" | "SKIP"
    details: Optional[str] = None
    errors: Optional[List[Dict[str, Any]]] = None


@dataclass
class ValidationReport:
    ok: bool
    phase_file: str
    checks: List[CheckResult]
    errors: List[Dict[str, Any]]


# =========================
# UTILITIES
# =========================


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _make_error(
    code: str, message: str, context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    return {
        "code": code,
        "message": message,
        "context": context or {},
    }


def validate_with_schema(
    instance: Any,
    schema: Dict[str, Any],
    schema_dir: Path,
) -> List[Dict[str, Any]]:
    """
    Return a list of error dicts (empty list == no errors).
    """

    # Simple file-based resolver for $ref
    def ref_resolver(uri):
        if uri.startswith("file:///"):
            file_path = uri.replace("file:///", "").replace("/", "\\")
            return load_json(Path(file_path))
        elif not uri.startswith("http"):
            # Relative ref
            return load_json(schema_dir / uri)
        return None

    validator = Draft7Validator(schema)

    errors: List[Dict[str, Any]] = []
    for e in validator.iter_errors(instance):
        errors.append(
            {
                "path": list(e.path),
                "message": e.message,
                "validator": e.validator,
                "validator_value": str(e.validator_value)[:200],  # Limit length
            }
        )
    return errors


# =========================
# VALIDATION STEPS
# =========================


def step_1_validate_pattern_registry_and_gh_sync(
    repo_root: Path,
) -> CheckResult:
    """
    Step 1: Validate PATTERN_INDEX and GH_SYNC pattern spec/schema.
    """
    description = "Validate PATTERN_INDEX and GH_SYNC pattern (spec + schema)"
    errors: List[Dict[str, Any]] = []

    try:
        patterns_dir = repo_root / "patterns"
        registry_path = patterns_dir / "registry" / "PATTERN_INDEX.yaml"
        gh_spec_path = patterns_dir / "specs" / "GH_SYNC_PHASE_V1.pattern.yaml"
        gh_schema_path = patterns_dir / "schemas" / "GH_SYNC_PHASE_V1.schema.json"

        # 1.1 PATTERN_INDEX.yaml exists and is valid YAML
        if not registry_path.is_file():
            errors.append(
                _make_error(
                    "PAT_INDEX_MISSING",
                    f"Missing pattern registry at {registry_path}",
                )
            )
        else:
            try:
                registry_data = load_yaml(registry_path)
            except Exception as ex:
                errors.append(
                    _make_error(
                        "PAT_INDEX_INVALID_YAML",
                        f"Failed to parse PATTERN_INDEX.yaml: {ex}",
                    )
                )
                registry_data = None

            # Minimal structural sanity check
            if registry_data is not None and not isinstance(
                registry_data.get("patterns"), list
            ):
                errors.append(
                    _make_error(
                        "PAT_INDEX_BAD_STRUCTURE",
                        "Expected PATTERN_INDEX.yaml to have 'patterns' as a list.",
                    )
                )

        # 1.2 GH_SYNC spec exists and is valid YAML
        if not gh_spec_path.is_file():
            errors.append(
                _make_error(
                    "GH_SYNC_SPEC_MISSING",
                    f"Missing GH_SYNC pattern spec at {gh_spec_path}",
                )
            )
        else:
            try:
                _ = load_yaml(gh_spec_path)
            except Exception as ex:
                errors.append(
                    _make_error(
                        "GH_SYNC_SPEC_INVALID_YAML",
                        f"Failed to parse GH_SYNC spec: {ex}",
                    )
                )

        # GH_SYNC schema exists and is valid JSON
        if not gh_schema_path.is_file():
            errors.append(
                _make_error(
                    "GH_SYNC_SCHEMA_MISSING",
                    f"Missing GH_SYNC schema at {gh_schema_path}",
                )
            )
        else:
            try:
                _ = load_json(gh_schema_path)
            except Exception as ex:
                errors.append(
                    _make_error(
                        "GH_SYNC_SCHEMA_INVALID_JSON",
                        f"Failed to parse GH_SYNC schema: {ex}",
                    )
                )

    except Exception as ex:
        errors.append(
            _make_error(
                "STEP1_UNEXPECTED_EXCEPTION",
                f"Unexpected exception during step 1: {ex}",
            )
        )

    if errors:
        return CheckResult(
            id="STEP_1_PATTERN_REGISTRY_AND_GH_SYNC",
            description=description,
            status="FAIL",
            errors=errors,
            details="One or more registry/spec/schema checks failed.",
        )
    else:
        return CheckResult(
            id="STEP_1_PATTERN_REGISTRY_AND_GH_SYNC",
            description=description,
            status="PASS",
            details="PATTERN_INDEX and GH_SYNC spec/schema are present and parseable.",
        )


def step_2_validate_phase_plan_structure(
    repo_root: Path,
    phase_path: Path,
) -> CheckResult:
    """
    Step 2: Validate full Phase Plan YAML against SPLINTER_PHASE_PLAN_V1 schema.
    """
    description = "Validate Phase Plan against SPLINTER_PHASE_PLAN_V1.schema.json"
    errors: List[Dict[str, Any]] = []

    try:
        phase_data = load_yaml(phase_path)

        schema_path = (
            repo_root / "patterns" / "schemas" / "SPLINTER_PHASE_PLAN_V1.schema.json"
        )
        if not schema_path.is_file():
            errors.append(
                _make_error(
                    "SPLINTER_SCHEMA_MISSING",
                    f"Missing SPLINTER Phase Plan schema at {schema_path}",
                )
            )
        else:
            try:
                schema = load_json(schema_path)
            except json.JSONDecodeError as ex:
                errors.append(
                    _make_error(
                        "SPLINTER_SCHEMA_INVALID_JSON",
                        f"Failed to parse SPLINTER schema as JSON: {ex}",
                    )
                )
                return CheckResult(
                    id="STEP_2_SPLINTER_PHASE_SCHEMA",
                    description=description,
                    status="FAIL",
                    errors=errors,
                    details="Schema file is not valid JSON.",
                )

            schema_dir = schema_path.parent

            schema_errors = validate_with_schema(phase_data, schema, schema_dir)
            if schema_errors:
                errors.append(
                    _make_error(
                        "SPLINTER_SCHEMA_VALIDATION_ERROR",
                        "SPLINTER Phase Plan failed schema validation.",
                        {"schema_errors": schema_errors},
                    )
                )

    except Exception as ex:
        errors.append(
            _make_error(
                "STEP2_UNEXPECTED_EXCEPTION",
                f"Unexpected exception during step 2: {ex}",
            )
        )

    if errors:
        return CheckResult(
            id="STEP_2_SPLINTER_PHASE_SCHEMA",
            description=description,
            status="FAIL",
            errors=errors,
            details="Phase Plan did not pass SPLINTER_PHASE_PLAN_V1 schema validation.",
        )
    else:
        return CheckResult(
            id="STEP_2_SPLINTER_PHASE_SCHEMA",
            description=description,
            status="PASS",
            details="Phase Plan conforms to SPLINTER_PHASE_PLAN_V1 schema.",
        )


def step_3_validate_github_integration_block(
    repo_root: Path,
    phase_path: Path,
) -> CheckResult:
    """
    Step 3: Validate github_integration block with GH_SYNC_PHASE_V1 schema.
    """
    description = (
        "Validate github_integration block against GH_SYNC_PHASE_V1.schema.json"
    )
    errors: List[Dict[str, Any]] = []

    try:
        phase_data = load_yaml(phase_path)
        gh_block = phase_data.get("github_integration")

        if gh_block is None:
            # Not an error if github_integration is optional
            return CheckResult(
                id="STEP_3_GH_SYNC_SCHEMA",
                description=description,
                status="SKIP",
                details="Phase Plan does not contain github_integration block (optional).",
            )
        else:
            schema_path = (
                repo_root / "patterns" / "schemas" / "GH_SYNC_PHASE_V1.schema.json"
            )
            if not schema_path.is_file():
                errors.append(
                    _make_error(
                        "GH_SYNC_SCHEMA_MISSING",
                        f"Missing GH_SYNC schema at {schema_path}",
                    )
                )
            else:
                schema = load_json(schema_path)
                schema_dir = schema_path.parent
                schema_errors = validate_with_schema(gh_block, schema, schema_dir)
                if schema_errors:
                    errors.append(
                        _make_error(
                            "GH_SYNC_SCHEMA_VALIDATION_ERROR",
                            "github_integration block failed GH_SYNC schema validation.",
                            {"schema_errors": schema_errors},
                        )
                    )

    except Exception as ex:
        errors.append(
            _make_error(
                "STEP3_UNEXPECTED_EXCEPTION",
                f"Unexpected exception during step 3: {ex}",
            )
        )

    if errors:
        return CheckResult(
            id="STEP_3_GH_SYNC_SCHEMA",
            description=description,
            status="FAIL",
            errors=errors,
            details="github_integration block did not pass GH_SYNC_PHASE_V1 schema validation.",
        )
    else:
        return CheckResult(
            id="STEP_3_GH_SYNC_SCHEMA",
            description=description,
            status="PASS",
            details="github_integration block conforms to GH_SYNC_PHASE_V1 schema.",
        )


# =========================
# MAIN ENTRYPOINT
# =========================


def build_report(repo_root: Path, phase_file: Path) -> ValidationReport:
    all_checks: List[CheckResult] = []
    all_errors: List[Dict[str, Any]] = []

    # Step 1: Registry + GH_SYNC pattern
    step1 = step_1_validate_pattern_registry_and_gh_sync(repo_root)
    all_checks.append(step1)
    if step1.errors:
        all_errors.extend(step1.errors)

    # Step 2: SPLINTER Phase Plan schema
    step2 = step_2_validate_phase_plan_structure(repo_root, phase_file)
    all_checks.append(step2)
    if step2.errors:
        all_errors.extend(step2.errors)

    # Step 3: GH_SYNC github_integration block
    step3 = step_3_validate_github_integration_block(repo_root, phase_file)
    all_checks.append(step3)
    if step3.errors:
        all_errors.extend(step3.errors)

    ok = all(c.status in ["PASS", "SKIP"] for c in all_checks)

    return ValidationReport(
        ok=ok,
        phase_file=str(phase_file),
        checks=all_checks,
        errors=all_errors,
    )


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a SPLINTER Phase Plan against PAT-CHECK-001 + GH_SYNC schemas."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        required=True,
        help="Path to repository root (where patterns/, phases/, etc. live).",
    )
    parser.add_argument(
        "--phase-file",
        type=Path,
        required=True,
        help="Path to the SPLINTER Phase Plan YAML file to validate.",
    )

    args = parser.parse_args(argv)

    repo_root: Path = args.repo_root.resolve()
    phase_file: Path = args.phase_file.resolve()

    report = build_report(repo_root, phase_file)

    # Emit machine-readable JSON report to stdout
    output = asdict(report)
    # Convert dataclass CheckResult objects to dicts explicitly
    output["checks"] = [asdict(c) for c in report.checks]

    print(json.dumps(output, indent=2))

    # Exit code: 0 if ok, 1 if any failures
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
