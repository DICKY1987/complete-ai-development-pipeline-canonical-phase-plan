"""
Contract Validation CLI - Quick validation tool

Usage:
    python scripts/validate_contracts.py --phase phase0
    python scripts/validate_contracts.py --all
    python scripts/validate_contracts.py --phase phase1 --dry-run
"""

import argparse
import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

from core.contracts import PhaseContractValidator


def main():
    parser = argparse.ArgumentParser(description="Validate phase contracts")
    parser.add_argument(
        "--phase",
        type=str,
        help="Phase to validate (e.g., phase0, phase1)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Validate all phases",
    )
    parser.add_argument(
        "--entry",
        action="store_true",
        help="Validate entry contracts only",
    )
    parser.add_argument(
        "--exit",
        action="store_true",
        help="Validate exit contracts only",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be validated without failing",
    )

    args = parser.parse_args()

    # Create validator
    validator = PhaseContractValidator(repo_root=repo_root)

    phases_to_validate = []

    if args.all:
        phases_to_validate = [f"phase{i}" for i in range(8)]
    elif args.phase:
        phases_to_validate = [args.phase]
    else:
        parser.print_help()
        return 1

    total_errors = 0
    total_warnings = 0

    print("\n" + "=" * 70)
    print("PHASE CONTRACT VALIDATION")
    print("=" * 70 + "\n")

    for phase in phases_to_validate:
        print(f"\n{'=' * 70}")
        print(f"Validating: {phase}")
        print(f"{'=' * 70}\n")

        # Validate entry contract
        if not args.exit:
            print(f"  Entry Contract:")
            result = validator.validate_entry(phase, context={})

            if result.valid:
                print(f"    ✅ VALID")
            else:
                print(f"    ❌ INVALID ({len(result.violations)} violations)")
                for v in result.violations:
                    print(f"       - [{v.type.value}] {v.message}")
                    if v.remediation:
                        print(f"         → {v.remediation}")

            if result.warnings:
                print(f"    ⚠️  {len(result.warnings)} warnings")
                for w in result.warnings:
                    print(f"       - {w.message}")

            total_errors += len(result.violations)
            total_warnings += len(result.warnings)

        # Validate exit contract
        if not args.entry:
            print(f"\n  Exit Contract:")
            result = validator.validate_exit(phase, artifacts={})

            if result.valid:
                print(f"    ✅ VALID")
            else:
                print(f"    ❌ INVALID ({len(result.violations)} violations)")
                for v in result.violations:
                    print(f"       - [{v.type.value}] {v.message}")
                    if v.remediation:
                        print(f"         → {v.remediation}")

            if result.warnings:
                print(f"    ⚠️  {len(result.warnings)} warnings")
                for w in result.warnings:
                    print(f"       - {w.message}")

            total_errors += len(result.violations)
            total_warnings += len(result.warnings)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Phases validated: {len(phases_to_validate)}")
    print(f"  Total errors:     {total_errors}")
    print(f"  Total warnings:   {total_warnings}")

    if total_errors > 0:
        print(f"\n❌ Validation FAILED with {total_errors} errors\n")
        return 1 if not args.dry_run else 0
    else:
        print(f"\n✅ All validations PASSED\n")
        return 0


if __name__ == "__main__":
    sys.exit(main())
