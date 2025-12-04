"""Bootstrap Orchestrator - WS-02-04A"""
import json
import sys
from pathlib import Path
from datetime import datetime, UTC
from typing import Dict, Optional

# Add framework root to path when run as script
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.bootstrap.discovery import ProjectScanner
from core.bootstrap.selector import ProfileSelector
from core.bootstrap.generator import ArtifactGenerator
from core.bootstrap.validator import BootstrapValidator


class BootstrapOrchestrator:
    """Orchestrates the complete bootstrap process"""
# DOC_ID: DOC-CORE-BOOTSTRAP-ORCHESTRATOR-140

    def __init__(self, project_path: str, output_dir: Optional[str] = None):
        self.project_path = Path(project_path).resolve()
        self.output_dir = Path(output_dir) if output_dir else self.project_path
        self.framework_root = Path(__file__).parent.parent.parent

        # State tracking
        self.discovery_data = None
        self.selected_profile_id = None
        self.selected_profile = None
        self.generation_result = None
        self.validation_result = None

    def run(self) -> Dict:
        """Execute the complete bootstrap pipeline"""
        print("==> Starting UET Framework Bootstrap...\n")

        # Step 1: Discovery
        print("[1/4] Discovering project structure...")
        try:
            scanner = ProjectScanner(str(self.project_path))
            self.discovery_data = scanner.scan()
            print(f"   OK - Detected domain: {self.discovery_data['domain']}")
            if 'primary_language' in self.discovery_data:
                print(f"   OK - Primary language: {self.discovery_data['primary_language']}")
        except Exception as e:
            return self._failure_report("discovery", str(e))

        # Step 2: Profile Selection
        print("\n[2/4] Selecting appropriate profile...")
        try:
            selector = ProfileSelector(str(self.framework_root / "profiles"))
            self.selected_profile_id, self.selected_profile = selector.select(self.discovery_data)
            print(f"   OK - Selected profile: {self.selected_profile_id}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            return self._failure_report("selection", str(e))

        # Step 3: Artifact Generation
        print("\n[3/4] Generating bootstrap artifacts...")
        try:
            generator = ArtifactGenerator(
                self.discovery_data,
                self.selected_profile,
                str(self.output_dir)
            )
            self.generation_result = generator.generate_all()
            print(f"   OK - Generated PROJECT_PROFILE.yaml")
            print(f"   OK - Generated router_config.json")
            print(f"   OK - Created framework directories")
        except Exception as e:
            return self._failure_report("generation", str(e))

        # Step 4: Validation
        print("\n[4/4] Validating generated artifacts...")
        try:
            validator = BootstrapValidator(
                str(self.output_dir / "PROJECT_PROFILE.yaml"),
                str(self.output_dir / "router_config.json"),
                self.selected_profile_id
            )
            self.validation_result = validator.validate_all()

            if self.validation_result["valid"]:
                print(f"   OK - All validations passed")
            else:
                print(f"   WARNING - Validation issues detected:")
                for error in self.validation_result["errors"]:
                    print(f"      ERROR: {error['message']}")
                for needs_human in self.validation_result["needs_human"]:
                    print(f"      HUMAN: {needs_human['message']}")

            if self.validation_result["auto_fixed"]:
                print(f"   INFO - Auto-fixed {len(self.validation_result['auto_fixed'])} issues")

            if self.validation_result["warnings"]:
                print(f"   INFO - {len(self.validation_result['warnings'])} warnings (non-blocking)")

        except Exception as e:
            return self._failure_report("validation", str(e))

        # Generate final report
        report = self._generate_report()

        # Save report
        report_path = self.output_dir / "bootstrap_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        print(f"\n==> Bootstrap report saved to: {report_path}")

        # Final status
        if report["status"] == "ready":
            print("\nSUCCESS: Bootstrap complete! Framework is ready for workstreams.")
            return report
        elif report["status"] == "needs_human":
            print("\nWARNING: Bootstrap complete but requires human review.")
            print("   See bootstrap_report.json for details.")
            return report
        else:
            print(f"\nERROR: Bootstrap failed with status: {report['status']}")
            return report

    def _generate_report(self) -> Dict:
        """Generate bootstrap_report.v1.json"""

        # Determine overall status
        if not self.validation_result:
            status = "failed"
        elif not self.validation_result["valid"]:
            if self.validation_result["needs_human"]:
                status = "needs_human"
            else:
                status = "failed"
        elif self.validation_result["warnings"]:
            # Check if warnings are just missing directories (expected on first run)
            non_directory_warnings = [
                w for w in self.validation_result["warnings"]
                if w.get("type") != "missing_path"
            ]
            if non_directory_warnings:
                status = "partial"
            else:
                status = "ready"  # Only directory warnings, which is fine
        else:
            status = "ready"

        # Build report
        report = {
            "project_name": self.discovery_data.get("project_name", "Unknown"),
            "domain": self.discovery_data.get("domain", "unknown"),
            "profile_id": self.selected_profile_id,
            "profile_version": self.selected_profile.get("profile_version", "1.0.0"),
            "status": status,
            "discovery_summary": {
                "languages": self._format_languages(),
                "frameworks": self.discovery_data.get("frameworks_detected", []),
                "version_control": "git" if self.discovery_data.get("has_git", False) else "none",
                "ci_cd": "detected" if self.discovery_data.get("ci_config_found", False) else "none"
            },
            "generated_artifacts": [
                {
                    "path": "PROJECT_PROFILE.yaml",
                    "type": "project_profile",
                    "status": "validated" if self.validation_result and self.validation_result["valid"] else "created"
                },
                {
                    "path": "router_config.json",
                    "type": "router_config",
                    "status": "validated" if self.validation_result and self.validation_result["valid"] else "created"
                }
            ],
            "directories_created": [
                ".tasks/", ".ledger/", ".ledger/patches/", ".ledger/runs/",
                ".worktrees/", ".quarantine/", "registry/"
            ],
            "configuration": {
                "patch_only_mode": True,
                "max_lines_per_patch": 500,
                "available_tools": []
            },
            "validation_results": {
                "validation_status": "passed" if self.validation_result["valid"] else (
                    "needs_human" if self.validation_result.get("needs_human") else "failed"
                ),
                "errors": [e.get("message", str(e)) for e in self.validation_result.get("errors", [])],
                "warnings": [w.get("message", str(w)) for w in self.validation_result.get("warnings", [])],
                "auto_fixes_applied": len(self.validation_result.get("auto_fixed", [])),
                "human_decisions_needed": len(self.validation_result.get("needs_human", []))
            },
            "next_steps": self._generate_next_steps(),
            "initialization_time": datetime.now(UTC).isoformat() + "Z",
            "ready_for_workstreams": status == "ready"
        }

        return report

    def _format_languages(self) -> str:
        """Format language distribution as human-readable string"""
        langs = self.discovery_data.get("languages", [])
        if not langs:
            return "Unknown"

        # languages is a list of {"language": "python", "percentage": 87}
        if isinstance(langs, list):
            sorted_langs = sorted(langs, key=lambda x: x.get("percentage", 0), reverse=True)
            return ", ".join([f"{lang['language'].title()} ({lang['percentage']}%)" for lang in sorted_langs[:3]])
        else:
            # Fallback for dict format
            sorted_langs = sorted(langs.items(), key=lambda x: x[1], reverse=True)
            return ", ".join([f"{lang} ({pct}%)" for lang, pct in sorted_langs[:3]])

    def _generate_next_steps(self) -> Dict:
        """Generate recommended next steps"""
        for_human = []
        for_ai = []

        if self.validation_result:
            if self.validation_result.get("needs_human"):
                for item in self.validation_result["needs_human"]:
                    for_human.append(item.get("suggestion", item.get("message")))

            if self.validation_result.get("warnings"):
                for warning in self.validation_result["warnings"]:
                    if "missing_path" in warning.get("type", ""):
                        # These will be created on first run
                        continue
                    for_human.append(f"Review: {warning.get('message')}")

        if self.validation_result and self.validation_result["valid"]:
            for_ai.append("Framework is ready to accept workstreams")
            for_ai.append("Run: uet workstream create <workstream.json>")
        else:
            for_human.append("Resolve validation errors before proceeding")

        return {
            "for_human": for_human if for_human else ["Review bootstrap_report.json"],
            "for_ai_agent": for_ai if for_ai else ["Waiting for human validation"]
        }

    def _failure_report(self, stage: str, error: str) -> Dict:
        """Generate failure report"""
        return {
            "project_name": self.discovery_data.get("project_name", "Unknown") if self.discovery_data else "Unknown",
            "domain": "unknown",
            "profile_id": "none",
            "status": "failed",
            "generated_artifacts": [],
            "directories_created": [],
            "configuration": {},
            "validation_results": {
                "validation_status": "failed",
                "errors": [f"Failed during {stage}: {error}"],
                "warnings": [],
                "auto_fixes_applied": 0,
                "human_decisions_needed": 1
            },
            "next_steps": {
                "for_human": [f"Fix {stage} error: {error}"],
                "for_ai_agent": []
            },
            "initialization_time": datetime.now(UTC).isoformat() + "Z",
            "ready_for_workstreams": False
        }


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py <project_path> [output_dir]")
        print("\nExample:")
        print("  python orchestrator.py /path/to/project")
        print("  python orchestrator.py /path/to/project /custom/output")
        sys.exit(1)

    project_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    orchestrator = BootstrapOrchestrator(project_path, output_dir)
    report = orchestrator.run()

    # Exit with appropriate code
    if report["status"] in ["ready", "partial"]:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
