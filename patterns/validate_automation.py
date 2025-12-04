"""
Pattern Automation - Complete System Validation & Completion Script

This script validates the pattern automation system and provides
completion guidance for remaining tasks.
"""
# DOC_ID: DOC-PAT-PATTERNS-VALIDATE-AUTOMATION-655

import sqlite3
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


class PatternAutomationValidator:
    """Validates pattern automation system completeness."""

    def __init__(self, base_dir: Path = None):
        if base_dir is None:
            base_dir = Path(__file__).parent
        self.base_dir = base_dir
        self.db_path = base_dir / "metrics" / "pattern_automation.db"
        self.config_path = base_dir / "automation" / "config" / "detection_config.yaml"

        self.results = {
            "infrastructure": {},
            "database": {},
            "patterns": {},
            "executors": {},
            "overall_status": "UNKNOWN"
        }

    def validate_all(self) -> Dict:
        """Run all validation checks."""
        print("=" * 80)
        print("PATTERN AUTOMATION SYSTEM - VALIDATION REPORT")
        print("=" * 80)
        print(f"Generated: {datetime.now().isoformat()}")
        print(f"Base Directory: {self.base_dir}")
        print()

        self._validate_infrastructure()
        self._validate_database()
        self._validate_patterns()
        self._validate_executors()
        self._calculate_overall_status()
        self._print_summary()
        self._print_next_actions()

        return self.results

    def _validate_infrastructure(self):
        """Check infrastructure components."""
        print("[1/4] Validating Infrastructure...")

        checks = {
            "database_exists": self.db_path.exists(),
            "config_exists": self.config_path.exists(),
            "hooks_module": (self.base_dir / "automation" / "integration" / "orchestrator_hooks.py").exists(),
            "execution_detector": (self.base_dir / "automation" / "detectors" / "execution_detector.py").exists(),
            "anti_pattern_detector": (self.base_dir / "automation" / "detectors" / "anti_pattern_detector.py").exists(),
            "file_pattern_miner": (self.base_dir / "automation" / "detectors" / "file_pattern_miner.py").exists(),
        }

        self.results["infrastructure"] = checks

        for name, status in checks.items():
            icon = "✅" if status else "❌"
            print(f"  {icon} {name.replace('_', ' ').title()}")

        # Load config
        if checks["config_exists"]:
            with open(self.config_path) as f:
                config = yaml.safe_load(f)
                print(f"\n  Configuration:")
                print(f"    Automation Enabled: {config.get('automation_enabled', 'N/A')}")
                print(f"    Auto-Approve: {config.get('auto_approve_high_confidence', 'N/A')}")
                print(f"    Similarity Threshold: {config.get('detection', {}).get('similarity_threshold', 'N/A')}")

        print()

    def _validate_database(self):
        """Check database tables and data."""
        print("[2/4] Validating Database...")

        if not self.db_path.exists():
            print("  ❌ Database not found!")
            self.results["database"] = {"exists": False}
            print()
            return

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Check tables
        tables = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = [t[0] for t in tables]

        required_tables = ["execution_logs", "pattern_candidates", "anti_patterns"]
        tables_status = {
            table: table in table_names for table in required_tables
        }

        # Count rows
        row_counts = {}
        for table in required_tables:
            if table in table_names:
                count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                row_counts[table] = count
            else:
                row_counts[table] = 0

        self.results["database"] = {
            "exists": True,
            "tables": tables_status,
            "row_counts": row_counts
        }

        for table, exists in tables_status.items():
            icon = "✅" if exists else "❌"
            count = row_counts.get(table, 0)
            print(f"  {icon} {table}: {count} rows")

        # Show pattern candidates details
        if "pattern_candidates" in table_names and row_counts.get("pattern_candidates", 0) > 0:
            print(f"\n  Pattern Candidates:")
            candidates = cursor.execute(
                "SELECT pattern_id, confidence, status FROM pattern_candidates"
            ).fetchall()
            for pid, conf, status in candidates:
                print(f"    • {pid}: {conf:.1%} confidence ({status})")

        conn.close()
        print()

    def _validate_patterns(self):
        """Check pattern specifications and drafts."""
        print("[3/4] Validating Patterns...")

        specs_dir = self.base_dir / "specs"
        drafts_dir = self.base_dir / "drafts"
        registry_file = self.base_dir / "registry" / "PATTERN_INDEX.yaml"

        # Count pattern specs
        pattern_specs = list(specs_dir.glob("*.pattern.yaml")) if specs_dir.exists() else []

        # Count auto-generated patterns
        auto_patterns = list(drafts_dir.glob("AUTO-*.yaml")) if drafts_dir.exists() else []

        # Load registry
        registry_count = 0
        if registry_file.exists():
            with open(registry_file) as f:
                registry = yaml.safe_load(f)
                if registry and "patterns" in registry:
                    registry_count = len(registry["patterns"])

        self.results["patterns"] = {
            "specs_count": len(pattern_specs),
            "auto_generated_count": len(auto_patterns),
            "registry_count": registry_count
        }

        print(f"  ✅ Pattern Specs: {len(pattern_specs)}")
        print(f"  ✅ Registry Entries: {registry_count}")
        print(f"  {'✅' if len(auto_patterns) > 0 else '⚠️ '} Auto-Generated Patterns: {len(auto_patterns)}")

        if len(auto_patterns) > 0:
            print(f"\n  Recent Auto-Generated Patterns:")
            for pattern in sorted(auto_patterns, reverse=True)[:5]:
                print(f"    • {pattern.name}")

        print()

    def _validate_executors(self):
        """Check pattern executors."""
        print("[4/4] Validating Executors...")

        executors_dir = self.base_dir / "executors"

        # Core patterns that need executors
        core_patterns = [
            "atomic_create",
            "batch_create",
            "self_heal",
            "verify_commit",
            "refactor_patch",
            "module_creation",
            "worktree_lifecycle"
        ]

        executors_status = {}
        for pattern in core_patterns:
            ps1_executor = executors_dir / f"{pattern}_executor.ps1"
            py_executor = executors_dir / f"{pattern}_executor.py"
            has_executor = ps1_executor.exists() or py_executor.exists()
            executors_status[pattern] = has_executor

        complete_count = sum(1 for v in executors_status.values() if v)
        total_count = len(executors_status)

        self.results["executors"] = {
            "status": executors_status,
            "complete": complete_count,
            "total": total_count,
            "percentage": (complete_count / total_count * 100) if total_count > 0 else 0
        }

        for pattern, exists in executors_status.items():
            icon = "✅" if exists else "⏳"
            status = "Complete" if exists else "Spec Only"
            print(f"  {icon} {pattern}: {status}")

        print(f"\n  Progress: {complete_count}/{total_count} ({self.results['executors']['percentage']:.0f}%)")
        print()

    def _calculate_overall_status(self):
        """Determine overall system status."""
        infra_complete = all(self.results["infrastructure"].values())
        db_complete = (
            self.results["database"].get("exists", False) and
            all(self.results["database"].get("tables", {}).values())
        )
        has_patterns = self.results["patterns"]["registry_count"] > 0
        executor_progress = self.results["executors"]["percentage"]

        if infra_complete and db_complete and has_patterns:
            if executor_progress >= 100:
                self.results["overall_status"] = "COMPLETE"
            elif executor_progress >= 50:
                self.results["overall_status"] = "OPERATIONAL"
            else:
                self.results["overall_status"] = "FUNCTIONAL"
        elif infra_complete and db_complete:
            self.results["overall_status"] = "INFRASTRUCTURE_READY"
        else:
            self.results["overall_status"] = "INCOMPLETE"

    def _print_summary(self):
        """Print summary of validation results."""
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)

        status = self.results["overall_status"]
        status_icons = {
            "COMPLETE": "✅",
            "OPERATIONAL": "✅",
            "FUNCTIONAL": "⚠️ ",
            "INFRASTRUCTURE_READY": "⚠️ ",
            "INCOMPLETE": "❌"
        }

        icon = status_icons.get(status, "❓")
        print(f"\nOverall Status: {icon} {status}")

        # Completion metrics
        print(f"\nCompletion Metrics:")
        print(f"  Infrastructure: {'100%' if all(self.results['infrastructure'].values()) else 'Incomplete'}")
        print(f"  Database: {'Operational' if self.results['database'].get('exists') else 'Missing'}")
        print(f"  Patterns: {self.results['patterns']['registry_count']} registered")
        print(f"  Executors: {self.results['executors']['percentage']:.0f}% complete")

        # Database activity
        if self.results["database"].get("exists"):
            exec_count = self.results["database"]["row_counts"].get("execution_logs", 0)
            cand_count = self.results["database"]["row_counts"].get("pattern_candidates", 0)
            print(f"\nActivity:")
            print(f"  Executions Logged: {exec_count}")
            print(f"  Patterns Detected: {cand_count}")
            if cand_count > 0 and exec_count > 0:
                detection_rate = (cand_count / exec_count) * 100
                print(f"  Detection Rate: {detection_rate:.1f}%")

        print()

    def _print_next_actions(self):
        """Print recommended next actions based on status."""
        print("=" * 80)
        print("NEXT ACTIONS")
        print("=" * 80)
        print()

        status = self.results["overall_status"]

        if status == "COMPLETE":
            print("✅ System is fully operational!")
            print("\nMaintenance Tasks:")
            print("  1. Monitor pattern detection weekly")
            print("  2. Review and approve auto-generated patterns")
            print("  3. Update executor implementations as needed")

        elif status == "OPERATIONAL":
            print("✅ Core automation is working!")
            print("\nTo achieve 100% completion:")
            incomplete = [
                name for name, complete in self.results["executors"]["status"].items()
                if not complete
            ]
            print(f"\nBuild remaining executors ({len(incomplete)}):")
            for pattern in incomplete:
                print(f"  • {pattern}_executor.ps1")
            print(f"\nTemplate: Use executors/atomic_create_executor.ps1 as reference")

        elif status == "FUNCTIONAL":
            print("⚠️  System is functional but needs executor implementations.")
            print("\nPriority Actions:")
            print("  1. Build batch_create executor (88% time savings)")
            print("  2. Build self_heal executor (90% time savings)")
            print("  3. Build verify_commit executor (85% time savings)")

        elif status == "INFRASTRUCTURE_READY":
            print("⚠️  Infrastructure ready, needs pattern integration.")
            print("\nNext Steps:")
            print("  1. Integrate hooks into main orchestrator")
            print("  2. Run test executions to generate patterns")
            print("  3. Review detected patterns in drafts/")

        else:  # INCOMPLETE
            print("❌ System needs setup.")
            print("\nSetup Steps:")
            if not self.results["database"].get("exists"):
                print("  1. Create database: patterns/metrics/pattern_automation.db")
                print("  2. Run migration: scripts/create_pattern_tables.sql")
            if not all(self.results["infrastructure"].values()):
                print("  3. Ensure all detector modules exist")
                print("  4. Create configuration file")

        print("\n" + "=" * 80)
        print(f"For detailed guidance, see: AUTOMATION_STATUS_REPORT.md")
        print("=" * 80)
        print()


def main():
    """Run validation and print report."""
    validator = PatternAutomationValidator()
    results = validator.validate_all()

    # Save results to JSON for programmatic access
    results_file = Path(__file__).parent / "automation_validation_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to: {results_file}")

    # Exit with appropriate code
    status = results["overall_status"]
    exit_codes = {
        "COMPLETE": 0,
        "OPERATIONAL": 0,
        "FUNCTIONAL": 1,
        "INFRASTRUCTURE_READY": 1,
        "INCOMPLETE": 2
    }
    return exit_codes.get(status, 2)


if __name__ == "__main__":
    exit(main())
