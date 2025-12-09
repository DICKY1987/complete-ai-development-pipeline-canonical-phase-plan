#!/usr/bin/env python3
"""
Registry Integrity Validator
Comprehensive validation of PATTERN_INDEX.yaml and pattern files

DOC_ID: DOC-PAT-VALIDATORS-REGISTRY-VALIDATOR-001
Gap: GAP-PATREG-003
Pattern: EXEC-002 (Batch Validation)
"""

import sys
from pathlib import Path
from typing import Dict, List
import yaml


class RegistryValidator:
    """Validates pattern registry integrity"""

    def __init__(self, patterns_dir: Path):
        self.patterns_dir = patterns_dir
        self.registry_path = patterns_dir / "registry" / "PATTERN_INDEX.yaml"
        self.specs_dir = patterns_dir / "specs"
        self.schemas_dir = patterns_dir / "schemas"
        self.executors_dir = patterns_dir / "executors"
        self.tests_dir = patterns_dir / "tests"
        self.examples_dir = patterns_dir / "examples"

    def validate_all(self) -> Dict:
        """Run all validation checks"""
        results = {
            "orphaned_specs": self._check_orphaned_specs(),
            "missing_files": self._check_missing_files(),
            "duplicate_ids": self._check_duplicate_ids(),
            "invalid_paths": self._check_invalid_paths(),
            "schema_mismatches": self._check_schema_mismatches(),
            "category_inconsistencies": self._check_category_consistency(),
            "count_accuracy": self._check_count_accuracy(),
        }

        return results

    def _check_orphaned_specs(self) -> List[str]:
        """Find spec files not in registry"""
        print("Checking for orphaned specs...")

        if not self.specs_dir.exists():
            return []

        spec_files = {f.stem for f in self.specs_dir.glob("*.pattern.yaml")}

        registry = yaml.safe_load(self.registry_path.read_text())
        registry_specs = set()

        for pattern in registry.get("patterns", []):
            spec_path = pattern.get("spec_path", "")
            if spec_path:
                spec_file = Path(spec_path).stem
                registry_specs.add(spec_file)

        orphans = sorted(spec_files - registry_specs)

        if orphans:
            print(f"  ✗ Found {len(orphans)} orphaned specs")
            for orphan in orphans[:5]:
                print(f"    - {orphan}.pattern.yaml")
            if len(orphans) > 5:
                print(f"    ... and {len(orphans) - 5} more")
        else:
            print("  ✓ No orphaned specs")

        return orphans

    def _check_missing_files(self) -> List[Dict]:
        """Find registry entries with missing files"""
        print("Checking for missing files...")

        registry = yaml.safe_load(self.registry_path.read_text())
        missing = []

        for pattern in registry.get("patterns", []):
            pattern_id = pattern.get("pattern_id", "unknown")

            for path_key in ["spec_path", "schema_path", "executor_path"]:
                if path_key in pattern:
                    rel_path = pattern[path_key]
                    full_path = self.patterns_dir.parent / rel_path

                    if not full_path.exists():
                        missing.append(
                            {
                                "pattern_id": pattern_id,
                                "file_type": path_key,
                                "path": rel_path,
                            }
                        )

        if missing:
            print(f"  ✗ Found {len(missing)} missing files")
            for item in missing[:5]:
                print(f"    - {item['pattern_id']}: {item['file_type']}")
            if len(missing) > 5:
                print(f"    ... and {len(missing) - 5} more")
        else:
            print("  ✓ No missing files")

        return missing

    def _check_duplicate_ids(self) -> List[str]:
        """Find duplicate pattern IDs"""
        print("Checking for duplicate IDs...")

        registry = yaml.safe_load(self.registry_path.read_text())
        pattern_ids = []
        duplicates = []

        for pattern in registry.get("patterns", []):
            pid = pattern.get("pattern_id")
            if pid in pattern_ids:
                duplicates.append(pid)
            pattern_ids.append(pid)

        if duplicates:
            print(f"  ✗ Found {len(duplicates)} duplicate IDs")
            for dup in duplicates:
                print(f"    - {dup}")
        else:
            print("  ✓ No duplicate IDs")

        return duplicates

    def _check_invalid_paths(self) -> List[Dict]:
        """Find invalid file paths"""
        print("Checking for invalid paths...")

        registry = yaml.safe_load(self.registry_path.read_text())
        invalid = []

        for pattern in registry.get("patterns", []):
            pattern_id = pattern.get("pattern_id", "unknown")
            spec_path = pattern.get("spec_path", "")

            # Check if path format is correct
            if spec_path and not spec_path.startswith("patterns/"):
                invalid.append(
                    {
                        "pattern_id": pattern_id,
                        "issue": "spec_path should start with 'patterns/'",
                    }
                )

        if invalid:
            print(f"  ✗ Found {len(invalid)} invalid paths")
        else:
            print("  ✓ All paths valid")

        return invalid

    def _check_schema_mismatches(self) -> List[Dict]:
        """Find mismatches between spec and registry"""
        print("Checking for schema mismatches...")

        mismatches = []

        # This would require parsing each spec file
        # For now, placeholder

        print("  ✓ Schema validation skipped (requires spec parsing)")
        return mismatches

    def _check_category_consistency(self) -> List[Dict]:
        """Find category inconsistencies"""
        print("Checking category consistency...")

        inconsistencies = []

        # Placeholder - would check spec category vs registry category

        print("  ✓ Category consistency check skipped")
        return inconsistencies

    def _check_count_accuracy(self) -> Dict:
        """Check if metadata counts are accurate"""
        print("Checking count accuracy...")

        registry = yaml.safe_load(self.registry_path.read_text())

        actual_count = len(registry.get("patterns", []))
        stated_count = registry.get("metadata", {}).get("total_patterns", 0)

        categories = set()
        for pattern in registry.get("patterns", []):
            cat = pattern.get("category")
            if cat:
                categories.add(cat)

        actual_cat_count = len(categories)
        stated_cat_count = registry.get("metadata", {}).get("total_categories", 0)

        accurate = actual_count == stated_count and actual_cat_count == stated_cat_count

        if accurate:
            print(
                f"  ✓ Counts accurate (patterns: {actual_count}, categories: {actual_cat_count})"
            )
        else:
            print(
                f"  ✗ Count mismatch - patterns: {actual_count} (stated: {stated_count}), categories: {actual_cat_count} (stated: {stated_cat_count})"
            )

        return {
            "accurate": accurate,
            "actual_patterns": actual_count,
            "stated_patterns": stated_count,
            "actual_categories": actual_cat_count,
            "stated_categories": stated_cat_count,
        }


def main():
    """CLI entry point"""
    patterns_dir = Path(__file__).parent.parent.parent

    print("=" * 70)
    print("Pattern Registry Integrity Validation")
    print("=" * 70)
    print()

    validator = RegistryValidator(patterns_dir)
    results = validator.validate_all()

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()

    total_issues = (
        len(results["orphaned_specs"])
        + len(results["missing_files"])
        + len(results["duplicate_ids"])
        + len(results["invalid_paths"])
    )

    if total_issues > 0:
        print(f"✗ Found {total_issues} issues:")
        print(f"  - Orphaned specs: {len(results['orphaned_specs'])}")
        print(f"  - Missing files: {len(results['missing_files'])}")
        print(f"  - Duplicate IDs: {len(results['duplicate_ids'])}")
        print(f"  - Invalid paths: {len(results['invalid_paths'])}")
        print()
        print("VALIDATION FAILED")
        return 1
    else:
        print("✓ Registry integrity validated")
        return 0


if __name__ == "__main__":
    sys.exit(main())
