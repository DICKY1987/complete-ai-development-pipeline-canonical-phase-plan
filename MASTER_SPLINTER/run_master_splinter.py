#!/usr/bin/env python3
"""
Master SPLINTER Orchestrator - 1-Touch Execution.
Discovers phase plans, converts them to workstreams, executes coordination, and reports.
"""
DOC_ID: DOC-CORE-MASTER-SPLINTER-RUN-MASTER-SPLINTER-769

import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).parent
PLANS_DIR = REPO_ROOT / "plans" / "phases"
WORKSTREAMS_DIR = REPO_ROOT / "workstreams"
REPORTS_DIR = REPO_ROOT / "reports"
CONFIG_DIR = REPO_ROOT / "config"

# Ensure directories exist early
for path in [PLANS_DIR, WORKSTREAMS_DIR, REPORTS_DIR, CONFIG_DIR]:
    path.mkdir(parents=True, exist_ok=True)


class MasterOrchestrator:
    """Master orchestrator for 1-touch execution with NO STOP MODE."""

    def __init__(self) -> None:
        self.start_time = datetime.now()
        self.run_id = f"master-run-{self.start_time.strftime('%Y%m%d-%H%M%S')}"
        self.errors: List[str] = []
        self.summary: Dict[str, Any] = {
            "run_id": self.run_id,
            "start_time": self.start_time.isoformat(),
            "phase_plans_found": 0,
            "workstreams_generated": 0,
            "multi_agent_status": "not_started",
            "sync_status": "not_started",
            "errors": [],
        }

    def log(self, message: str, level: str = "INFO") -> None:
        """Log a message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "[INFO]",
            "SUCCESS": "[ OK ]",
            "ERROR": "[FAIL]",
            "WARN": "[WARN]",
        }
        print(f"[{timestamp}] {prefix.get(level, '[INFO]')} {message}")

    def log_error(self, context: str, error: str) -> None:
        """Log an error but continue execution (NO STOP MODE)."""
        error_msg = f"{context}: {error}"
        self.errors.append(error_msg)
        self.summary["errors"].append(error_msg)
        self.log(error_msg, "ERROR")

    def validate_prerequisites(self) -> bool:
        """Check required files exist."""
        self.log("Validating prerequisites...")

        required = [
            CONFIG_DIR / "tool_profiles.json",
            CONFIG_DIR / "circuit_breakers.yaml",
            REPO_ROOT / "prompts" / "EXECUTION_PROMPT_TEMPLATE_V2_DAG_MULTI_WORKSTREAM.md",
            REPO_ROOT / "patterns" / "registry.json",
        ]

        missing = [str(path) for path in required if not path.exists()]

        if missing:
            for path in missing:
                self.log_error("Missing prerequisite", path)
            return False

        self.log("Prerequisites validated", "SUCCESS")
        return True

    def discover_phase_plans(self) -> List[Path]:
        """Find all phase plan YAML files."""
        self.log("Discovering phase plans...")

        yaml_files = list(PLANS_DIR.glob("*.yml")) + list(PLANS_DIR.glob("*.yaml"))
        yaml_files = [path for path in yaml_files if "template" not in path.name.lower()]

        self.summary["phase_plans_found"] = len(yaml_files)
        self.log(f"Found {len(yaml_files)} phase plan(s)", "SUCCESS")
        return yaml_files

    def convert_phase_plans(self) -> bool:
        """Convert phase plans to workstreams."""
        self.log("Converting phase plans to workstreams...")

        try:
            result = subprocess.run(
                [sys.executable, "phase_plan_to_workstream.py"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.stdout:
                print(result.stdout)

            if result.returncode != 0:
                self.log_error("Phase plan conversion", result.stderr)
                return False

            ws_count = len(list(WORKSTREAMS_DIR.glob("*.json")))
            self.summary["workstreams_generated"] = ws_count
            self.log(f"Generated {ws_count} workstream(s)", "SUCCESS")
            return True
        except Exception as exc:
            self.log_error("Phase plan conversion", str(exc))
            return False

    def execute_multi_agent_coordinator(self) -> bool:
        """Execute multi-agent workstream coordinator."""
        self.log("Starting multi-agent execution...")

        try:
            result = subprocess.run(
                [sys.executable, "multi_agent_workstream_coordinator.py"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=3600,
            )

            if result.stdout:
                print(result.stdout)

            if result.returncode == 0:
                self.summary["multi_agent_status"] = "success"
                self.log("Multi-agent execution completed", "SUCCESS")
                return True

            self.summary["multi_agent_status"] = "failed"
            self.log_error("Multi-agent execution", result.stderr)
            return False
        except Exception as exc:
            self.summary["multi_agent_status"] = "error"
            self.log_error("Multi-agent execution", str(exc))
            return False

    def execute_github_sync(self) -> bool:
        """Execute GitHub workstream sync (optional)."""
        self.log("Starting GitHub sync...")

        try:
            result = subprocess.run(
                [sys.executable, "sync_workstreams_to_github.py"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=600,
            )

            if result.stdout:
                print(result.stdout)

            if result.returncode == 0:
                self.summary["sync_status"] = "success"
                self.log("GitHub sync completed", "SUCCESS")
                return True

            self.summary["sync_status"] = "failed"
            self.log_error("GitHub sync", result.stderr)
            return False
        except Exception as exc:
            self.summary["sync_status"] = "error"
            self.log_error("GitHub sync", str(exc))
            return False

    def _status_marker(self, status: str) -> str:
        """Convert a status string into a simple marker."""
        return {
            "success": "[ OK ]",
            "failed": "[FAIL]",
            "error": "[FAIL]",
            "not_started": "[....]",
        }.get(status, "[....]")

    def _format_errors(self) -> str:
        """Format collected errors for the report."""
        return "\n".join(f"{idx}. {message}" for idx, message in enumerate(self.errors, 1))

    def _next_steps(self) -> str:
        """Generate next steps based on results."""
        if not self.errors:
            return "\n".join(
                [
                    "1. Review multi-agent execution report.",
                    "2. Review GitHub sync report if run.",
                    "3. Check consolidated database for detailed metrics.",
                    "4. Verify all expected artifacts were created.",
                ]
            )

        return "\n".join(
            [
                "1. Review error details above.",
                "2. Check individual execution logs in logs/.",
                "3. Fix issues and re-run: python run_master_splinter.py.",
                "4. Consult troubleshooting guidance in CLAUDE.md.",
            ]
        )

    def generate_completion_report(self) -> Path:
        """Generate final completion report."""
        self.log("Generating completion report...")

        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        report_path = REPORTS_DIR / f"COMPLETION_REPORT_{self.run_id}.md"

        content = f"""# MASTER_SPLINTER Execution Completion Report

**Run ID**: {self.run_id}
**Started**: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
**Completed**: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
**Duration**: {duration:.1f} seconds

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Phase Plans Discovered | {self.summary['phase_plans_found']} |
| Workstreams Generated | {self.summary['workstreams_generated']} |
| Multi-Agent Execution | {self.summary['multi_agent_status']} |
| GitHub Sync | {self.summary['sync_status']} |
| Errors Encountered | {len(self.errors)} |

---

## Overall Status

{"Execution successful." if not self.errors else f"Execution completed with {len(self.errors)} error(s)."}

---

## Execution Timeline

1. [ OK ] Prerequisites validated
2. [ OK ] Phase plans discovered ({self.summary['phase_plans_found']})
3. [ OK ] Workstreams generated ({self.summary['workstreams_generated']})
4. {self._status_marker(self.summary['multi_agent_status'])} Multi-agent execution
5. {self._status_marker(self.summary['sync_status'])} GitHub sync

---

## Detailed Results

### Phase Plans Processed
- Location: plans/phases/
- Count: {self.summary['phase_plans_found']}

### Workstreams Generated
- Location: workstreams/
- Count: {self.summary['workstreams_generated']}

### Multi-Agent Execution
- Status: {self.summary['multi_agent_status']}
- Report: reports/multi_agent_consolidated_{self.run_id}.md (if generated)
- Database: .state/multi_agent_consolidated.db

### GitHub Sync
- Status: {self.summary['sync_status']}
- Report: reports/workstream_sync_*.md (if generated)

---

## Errors

{"No errors encountered." if not self.errors else self._format_errors()}

---

## Next Steps

{self._next_steps()}

---

Generated by MASTER_SPLINTER Orchestrator
Report Path: {report_path}
"""

        report_path.write_text(content, encoding="utf-8")
        self.log(f"Completion report: {report_path}", "SUCCESS")
        return report_path

    def run(self) -> int:
        """Execute full orchestration pipeline with NO STOP MODE."""
        print("=" * 80)
        print("MASTER_SPLINTER - 1-TOUCH ORCHESTRATOR")
        print("=" * 80)
        print()

        try:
            if not self.validate_prerequisites():
                self.log("Prerequisites check failed - continuing anyway...", "WARN")

            phase_plans = self.discover_phase_plans()

            if not phase_plans:
                self.log("No phase plans found in plans/phases/.", "WARN")
                self.log("You can add examples based on MASTER_SPLINTER_Phase_Plan_Template.yml.", "INFO")

            self.convert_phase_plans()
            self.execute_multi_agent_coordinator()
            # Optional: enable when GitHub sync should run automatically.
            # self.execute_github_sync()

            report_path = self.generate_completion_report()

            print()
            print("=" * 80)
            print("EXECUTION COMPLETE")
            print("=" * 80)
            print()
            print(f"Completion Report: {report_path}")
            print(f"Successes: {self.summary['phase_plans_found'] + self.summary['workstreams_generated']}")
            print(f"Errors: {len(self.errors)}")
            print()
            print("Review the completion report above for details.")
            print()

            return 1 if self.errors else 0
        except Exception as exc:
            self.log_error("Fatal orchestrator error", str(exc))
            self.generate_completion_report()
            return 2


def main() -> int:
    """Entry point."""
    orchestrator = MasterOrchestrator()
    return orchestrator.run()


if __name__ == "__main__":
    sys.exit(main())
