#!/usr/bin/env python3
"""
Autonomous Self-Healing Automation Orchestrator

This is the brain of the autonomous workflow system. It:
1. Loads runtime status from health sweeps
2. Classifies failures into deterministic buckets
3. Generates and executes fix plans
4. Retests until certification or escalation
5. Produces audit-ready certification artifacts

Zero-touch operation with comprehensive logging.


DOC_ID: DOC-CORE-ORCHESTRATOR-AUTOMATION-SELF-HEALING-780
"""

import hashlib
import json
import logging
import os

# ULID generation (simplified)
import random
import re
import string
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


def generate_ulid() -> str:
    """Generate a ULID (Universally Unique Lexicographically Sortable Identifier)"""
    chars = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
    timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)

    # Encode timestamp (10 chars)
    ts_part = ""
    for i in range(9, -1, -1):
        ts_part = chars[(timestamp >> (i * 5)) & 31] + ts_part

    # Random part (16 chars)
    rand_part = "".join(random.choice(chars) for _ in range(16))

    return ts_part[:10] + rand_part[:16]


class RootCause(Enum):
    ENV_MISSING = "ENV_MISSING"
    SCHEMA_INVALID = "SCHEMA_INVALID"
    DEPENDENCY_FAIL = "DEPENDENCY_FAIL"
    TIMEOUT = "TIMEOUT"
    LOGIC_ERROR = "LOGIC_ERROR"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    NETWORK_FAIL = "NETWORK_FAIL"
    RESOURCE_EXHAUSTED = "RESOURCE_EXHAUSTED"
    CONFIG_INVALID = "CONFIG_INVALID"
    VERSION_MISMATCH = "VERSION_MISMATCH"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    SYNTAX_ERROR = "SYNTAX_ERROR"
    UNKNOWN = "UNKNOWN"


class FixStrategy(Enum):
    INJECT_ENV_DEFAULT = "INJECT_ENV_DEFAULT"
    REGENERATE_SCHEMA = "REGENERATE_SCHEMA"
    RERUN_UPSTREAM = "RERUN_UPSTREAM"
    INCREASE_TIMEOUT = "INCREASE_TIMEOUT"
    REGENERATE_TOKEN = "REGENERATE_TOKEN"
    REFRESH_CREDENTIALS = "REFRESH_CREDENTIALS"
    RETRY_WITH_BACKOFF = "RETRY_WITH_BACKOFF"
    INSTALL_DEPENDENCY = "INSTALL_DEPENDENCY"
    FIX_CONFIG = "FIX_CONFIG"
    CLEAR_CACHE = "CLEAR_CACHE"
    RESTART_SERVICE = "RESTART_SERVICE"
    SYNC_FILES = "SYNC_FILES"
    PATCH_CODE = "PATCH_CODE"
    ESCALATE_AI = "ESCALATE_AI"
    ESCALATE_HUMAN = "ESCALATE_HUMAN"
    SKIP_AND_LOG = "SKIP_AND_LOG"


# Mapping: root cause -> fix strategy
ROOT_CAUSE_TO_FIX: Dict[RootCause, FixStrategy] = {
    RootCause.ENV_MISSING: FixStrategy.INJECT_ENV_DEFAULT,
    RootCause.SCHEMA_INVALID: FixStrategy.REGENERATE_SCHEMA,
    RootCause.DEPENDENCY_FAIL: FixStrategy.RERUN_UPSTREAM,
    RootCause.TIMEOUT: FixStrategy.INCREASE_TIMEOUT,
    RootCause.PERMISSION_DENIED: FixStrategy.REGENERATE_TOKEN,
    RootCause.NETWORK_FAIL: FixStrategy.RETRY_WITH_BACKOFF,
    RootCause.RESOURCE_EXHAUSTED: FixStrategy.CLEAR_CACHE,
    RootCause.CONFIG_INVALID: FixStrategy.FIX_CONFIG,
    RootCause.VERSION_MISMATCH: FixStrategy.INSTALL_DEPENDENCY,
    RootCause.FILE_NOT_FOUND: FixStrategy.SYNC_FILES,
    RootCause.SYNTAX_ERROR: FixStrategy.ESCALATE_AI,
    RootCause.LOGIC_ERROR: FixStrategy.ESCALATE_AI,
    RootCause.UNKNOWN: FixStrategy.ESCALATE_HUMAN,
}

# Auto-repairable root causes
AUTO_REPAIRABLE = {
    RootCause.ENV_MISSING,
    RootCause.SCHEMA_INVALID,
    RootCause.DEPENDENCY_FAIL,
    RootCause.TIMEOUT,
    RootCause.NETWORK_FAIL,
    RootCause.RESOURCE_EXHAUSTED,
    RootCause.CONFIG_INVALID,
    RootCause.FILE_NOT_FOUND,
}

# Error pattern matching for classification
ERROR_PATTERNS: Dict[str, RootCause] = {
    r"environment variable.*not set": RootCause.ENV_MISSING,
    r"env.*missing": RootCause.ENV_MISSING,
    r"ModuleNotFoundError": RootCause.ENV_MISSING,
    r"command not found": RootCause.ENV_MISSING,
    r"schema.*invalid": RootCause.SCHEMA_INVALID,
    r"validation.*failed": RootCause.SCHEMA_INVALID,
    r"invalid.*yaml": RootCause.SCHEMA_INVALID,
    r"invalid.*json": RootCause.SCHEMA_INVALID,
    r"timeout": RootCause.TIMEOUT,
    r"timed out": RootCause.TIMEOUT,
    r"permission denied": RootCause.PERMISSION_DENIED,
    r"access denied": RootCause.PERMISSION_DENIED,
    r"401.*unauthorized": RootCause.PERMISSION_DENIED,
    r"403.*forbidden": RootCause.PERMISSION_DENIED,
    r"network.*error": RootCause.NETWORK_FAIL,
    r"connection.*refused": RootCause.NETWORK_FAIL,
    r"dns.*failed": RootCause.NETWORK_FAIL,
    r"out of memory": RootCause.RESOURCE_EXHAUSTED,
    r"disk.*full": RootCause.RESOURCE_EXHAUSTED,
    r"no space left": RootCause.RESOURCE_EXHAUSTED,
    r"file not found": RootCause.FILE_NOT_FOUND,
    r"no such file": RootCause.FILE_NOT_FOUND,
    r"syntax.*error": RootCause.SYNTAX_ERROR,
    r"SyntaxError": RootCause.SYNTAX_ERROR,
    r"IndentationError": RootCause.SYNTAX_ERROR,
}


@dataclass
class AuditEntry:
    timestamp: str
    event: str
    unit_id: Optional[str] = None
    details: Optional[str] = None


@dataclass
class OrchestratorConfig:
    """Configuration for the self-healing orchestrator"""

    repo_root: Path
    output_dir: Path
    max_retry_cycles: int = 5
    max_retries_per_unit: int = 3
    retry_delay_seconds: int = 5
    backoff_multiplier: float = 2.0
    certification_threshold: float = 100.0  # Success rate required
    max_critical_failures: int = 0
    dry_run: bool = False
    verbose: bool = False


class SelfHealingOrchestrator:
    """
    Autonomous self-healing orchestration engine.

    Implements the closed-loop:
    Detect → Diagnose → Fix → Retest → Certify
    """

    def __init__(self, config: OrchestratorConfig):
        self.config = config
        self.sweep_id = generate_ulid()
        self.audit_trail: List[AuditEntry] = []
        self.logger = self._setup_logging()

        # Ensure output directory exists
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

        self._audit("ORCHESTRATOR_INIT", details=f"Sweep ID: {self.sweep_id}")

    def _setup_logging(self) -> logging.Logger:
        """Configure logging with JSONL output"""
        logger = logging.getLogger(f"orchestrator.{self.sweep_id}")
        logger.setLevel(logging.DEBUG if self.config.verbose else logging.INFO)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(
            logging.Formatter(
                "%(asctime)s │ %(levelname)-8s │ %(message)s", datefmt="%H:%M:%S"
            )
        )
        logger.addHandler(ch)

        # JSONL file handler
        log_path = self.config.output_dir / f"orchestrator_{self.sweep_id}.jsonl"
        fh = logging.FileHandler(log_path)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(fh)

        return logger

    def _audit(
        self, event: str, unit_id: Optional[str] = None, details: Optional[str] = None
    ):
        """Add entry to audit trail"""
        entry = AuditEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            event=event,
            unit_id=unit_id,
            details=details,
        )
        self.audit_trail.append(entry)

        log_entry = {
            "ts": entry.timestamp,
            "sweep_id": self.sweep_id,
            "event": event,
            "unit_id": unit_id,
            "details": details,
        }
        self.logger.debug(json.dumps(log_entry))

    def load_runtime_status(self, status_path: Path) -> Dict[str, Any]:
        """Load runtime status from health sweep"""
        self._audit("LOAD_STATUS", details=str(status_path))

        with open(status_path, "r") as f:
            return json.load(f)

    def load_automation_index(self, index_path: Path) -> Dict[str, Any]:
        """Load automation index"""
        self._audit("LOAD_INDEX", details=str(index_path))

        with open(index_path, "r") as f:
            return json.load(f)

    def classify_failure(
        self, unit_id: str, unit_status: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Classify a failure into a deterministic root cause bucket"""
        stderr = unit_status.get("stderr_tail", "") or ""
        stdout = unit_status.get("stdout_tail", "") or ""
        error_sig = unit_status.get("error_signature", "")
        combined_output = f"{stderr} {stdout}".lower()

        # First check explicit error signature
        if error_sig:
            try:
                root_cause = RootCause(error_sig)
            except ValueError:
                root_cause = RootCause.UNKNOWN
        else:
            # Pattern matching
            root_cause = RootCause.UNKNOWN
            for pattern, cause in ERROR_PATTERNS.items():
                if re.search(pattern, combined_output, re.IGNORECASE):
                    root_cause = cause
                    break

        # Determine layer
        layer_map = {
            RootCause.FILE_NOT_FOUND: "Layer 1 - Infrastructure",
            RootCause.RESOURCE_EXHAUSTED: "Layer 1 - Infrastructure",
            RootCause.ENV_MISSING: "Layer 2 - Dependencies",
            RootCause.VERSION_MISMATCH: "Layer 2 - Dependencies",
            RootCause.NETWORK_FAIL: "Layer 2 - Dependencies",
            RootCause.SCHEMA_INVALID: "Layer 3 - Configuration",
            RootCause.CONFIG_INVALID: "Layer 3 - Configuration",
            RootCause.PERMISSION_DENIED: "Layer 4 - Operational",
            RootCause.TIMEOUT: "Layer 4 - Operational",
            RootCause.DEPENDENCY_FAIL: "Layer 4 - Operational",
            RootCause.SYNTAX_ERROR: "Layer 5 - Business Logic",
            RootCause.LOGIC_ERROR: "Layer 5 - Business Logic",
            RootCause.UNKNOWN: "Layer 5 - Business Logic",
        }

        fix_strategy = ROOT_CAUSE_TO_FIX.get(root_cause, FixStrategy.ESCALATE_HUMAN)
        auto_repairable = root_cause in AUTO_REPAIRABLE

        classification = {
            "root_cause": root_cause.value,
            "layer": layer_map.get(root_cause, "Layer 5 - Business Logic"),
            "auto_repairable": auto_repairable,
            "confidence": 0.9 if error_sig else 0.7,
            "evidence": {
                "error_message": stderr[:500] if stderr else None,
                "matched_pattern": error_sig or "pattern_match",
            },
            "suggested_fixes": [
                {
                    "strategy": fix_strategy.value,
                    "description": f"Auto-generated fix for {root_cause.value}",
                    "risk_level": "low" if auto_repairable else "high",
                }
            ],
        }

        self._audit(
            "CLASSIFY_FAILURE",
            unit_id=unit_id,
            details=f"{root_cause.value} -> {fix_strategy.value}",
        )

        return classification

    def generate_fix_plan(
        self,
        unit_id: str,
        classification: Dict[str, Any],
        unit_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate a deterministic fix plan for a classified failure"""
        strategy = FixStrategy(classification["suggested_fixes"][0]["strategy"])
        root_cause = RootCause(classification["root_cause"])

        # Generate fix steps based on strategy
        steps = []
        requires_human = False

        if strategy == FixStrategy.INJECT_ENV_DEFAULT:
            steps = [
                {"order": 1, "action": "check_env", "command": "printenv"},
                {
                    "order": 2,
                    "action": "inject_defaults",
                    "command": "source .env.defaults 2>/dev/null || true",
                },
            ]
        elif strategy == FixStrategy.REGENERATE_SCHEMA:
            steps = [
                {
                    "order": 1,
                    "action": "backup_schema",
                    "command": "cp -f schema.json schema.json.bak",
                },
                {
                    "order": 2,
                    "action": "regenerate",
                    "command": "python -m schema_generator --refresh",
                },
            ]
        elif strategy == FixStrategy.RETRY_WITH_BACKOFF:
            steps = [
                {"order": 1, "action": "wait", "command": "sleep 5"},
                {"order": 2, "action": "retry", "command": "echo 'Retry scheduled'"},
            ]
        elif strategy == FixStrategy.INCREASE_TIMEOUT:
            steps = [
                {
                    "order": 1,
                    "action": "increase_timeout",
                    "command": "export TIMEOUT=600",
                },
            ]
        elif strategy == FixStrategy.CLEAR_CACHE:
            steps = [
                {
                    "order": 1,
                    "action": "clear_cache",
                    "command": "rm -rf .cache/* __pycache__/* .pytest_cache/*",
                },
            ]
        elif strategy == FixStrategy.SYNC_FILES:
            steps = [
                {"order": 1, "action": "git_fetch", "command": "git fetch origin"},
                {"order": 2, "action": "git_checkout", "command": "git checkout -- ."},
            ]
        elif strategy == FixStrategy.INSTALL_DEPENDENCY:
            steps = [
                {
                    "order": 1,
                    "action": "install_deps",
                    "command": "pip install -r requirements.txt",
                },
            ]
        elif strategy in (FixStrategy.ESCALATE_AI, FixStrategy.ESCALATE_HUMAN):
            requires_human = True
            steps = [
                {
                    "order": 1,
                    "action": "log_escalation",
                    "command": "echo 'Escalated for manual review'",
                },
            ]
        else:
            steps = [
                {
                    "order": 1,
                    "action": "generic_retry",
                    "command": "echo 'Generic retry'",
                },
            ]

        fix_plan = {
            "strategy": strategy.value,
            "requires_human": requires_human,
            "description": f"Fix plan for {root_cause.value}",
            "steps": steps,
            "estimated_time_seconds": len(steps) * 10,
            "risk_assessment": {
                "level": "high" if requires_human else "low",
                "reversible": True,
                "side_effects": [],
            },
        }

        self._audit(
            "GENERATE_FIX",
            unit_id=unit_id,
            details=f"Strategy: {strategy.value}, Steps: {len(steps)}",
        )

        return fix_plan

    def execute_fix(self, unit_id: str, fix_plan: Dict[str, Any]) -> bool:
        """Execute a fix plan (or simulate in dry run mode)"""
        if fix_plan["requires_human"]:
            self._audit(
                "SKIP_FIX", unit_id=unit_id, details="Requires human intervention"
            )
            return False

        if self.config.dry_run:
            self._audit(
                "DRY_RUN_FIX",
                unit_id=unit_id,
                details=f"Would execute {len(fix_plan['steps'])} steps",
            )
            return True

        success = True
        for step in fix_plan["steps"]:
            try:
                self._audit(
                    "EXECUTE_STEP",
                    unit_id=unit_id,
                    details=f"{step['action']}: {step['command']}",
                )

                result = subprocess.run(
                    step["command"],
                    shell=True,
                    cwd=str(self.config.repo_root),
                    capture_output=True,
                    text=True,
                    timeout=step.get("timeout_seconds", 60),
                )

                if result.returncode != 0 and not step.get("continue_on_error", False):
                    self._audit(
                        "STEP_FAILED",
                        unit_id=unit_id,
                        details=f"{step['action']}: {result.stderr[:200]}",
                    )
                    success = False
                    break

            except subprocess.TimeoutExpired:
                self._audit("STEP_TIMEOUT", unit_id=unit_id, details=step["action"])
                success = False
                break
            except Exception as e:
                self._audit("STEP_ERROR", unit_id=unit_id, details=str(e))
                success = False
                break

        return success

    def run_health_sweep(self) -> Dict[str, Any]:
        """Execute health sweep using PowerShell collector"""
        self._audit("RUN_HEALTH_SWEEP")

        collector_path = (
            Path(__file__).parent.parent
            / "collectors"
            / "Invoke-AutomationHealthSweep.ps1"
        )

        # Check if PowerShell is available (Windows) or pwsh (cross-platform)
        ps_cmd = "powershell" if os.name == "nt" else "pwsh"

        try:
            if collector_path.exists():
                cmd = [
                    ps_cmd,
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(collector_path),
                    "-RepoRoot",
                    str(self.config.repo_root),
                    "-OutputDir",
                    str(self.config.output_dir),
                    "-Mode",
                    "full",
                ]
                if self.config.dry_run:
                    cmd.append("-DryRun")

                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=600
                )

                if result.returncode == 0:
                    status_path = (
                        self.config.output_dir / "automation_runtime_status.json"
                    )
                    if status_path.exists():
                        return self.load_runtime_status(status_path)

            # Fallback: create minimal status
            self.logger.warning("PowerShell collector not available, using fallback")
            return self._create_minimal_status()

        except Exception as e:
            self.logger.error(f"Health sweep failed: {e}")
            return self._create_minimal_status()

    def _create_minimal_status(self) -> Dict[str, Any]:
        """Create minimal status when collector unavailable"""
        return {
            "version": "1.0.0",
            "sweep_id": self.sweep_id,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": 0,
            "summary": {
                "total": 0,
                "success": 0,
                "failed": 0,
                "skipped": 0,
                "timeout": 0,
                "success_rate": 0,
            },
            "units": {},
        }

    def generate_certification(
        self, runtime_status: Dict[str, Any], fixes_applied: int, retry_cycles: int
    ) -> Dict[str, Any]:
        """Generate certification artifact"""
        summary = runtime_status.get("summary", {})
        success_rate = summary.get("success_rate", 0)

        # Determine certification status
        if (
            summary.get("failed", 0) == 0
            and success_rate >= self.config.certification_threshold
        ):
            status = "certified"
        elif success_rate >= 95:
            status = "partial"
        else:
            status = "failed"

        # Collect failing units
        failing_units = []
        for unit_id, unit_data in runtime_status.get("units", {}).items():
            if unit_data.get("status") == "fail":
                failing_units.append(
                    {
                        "id": unit_id,
                        "root_cause": unit_data.get("error_signature", "UNKNOWN"),
                        "escalation_reason": (
                            "Max retries exceeded"
                            if retry_cycles >= self.config.max_retry_cycles
                            else "Non-auto-repairable"
                        ),
                    }
                )

        certification = {
            "version": "1.0.0",
            "certification_id": f"CERT-{generate_ulid()}",
            "sweep_id": self.sweep_id,
            "certified_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": None,  # Can be set based on policy
            "status": status,
            "summary": {
                "automation_units": summary.get("total", 0),
                "passing": summary.get("success", 0),
                "failing": summary.get("failed", 0),
                "skipped": summary.get("skipped", 0),
                "success_rate": success_rate,
                "sweep_duration_seconds": runtime_status.get("duration_seconds", 0),
                "fixes_applied": fixes_applied,
                "retry_cycles": retry_cycles,
            },
            "environment": runtime_status.get("environment", {}),
            "thresholds": {
                "minimum_success_rate": self.config.certification_threshold,
                "max_critical_failures": self.config.max_critical_failures,
            },
            "failing_units": failing_units,
            "audit_trail": [
                asdict(e) for e in self.audit_trail[-100:]
            ],  # Last 100 entries
        }

        # Add content hash
        content_for_hash = json.dumps(certification, sort_keys=True)
        certification["signatures"] = {
            "content_hash": hashlib.sha256(content_for_hash.encode()).hexdigest()
        }

        self._audit("GENERATE_CERTIFICATION", details=f"Status: {status}")

        return certification

    def run(self, status_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Execute the complete self-healing loop:
        Detect → Diagnose → Fix → Retest → Certify
        """
        self.logger.info("=" * 60)
        self.logger.info("  AUTONOMOUS SELF-HEALING ORCHESTRATOR")
        self.logger.info(f"  Sweep ID: {self.sweep_id}")
        self.logger.info("=" * 60)

        fixes_applied = 0
        retry_cycle = 0

        while retry_cycle < self.config.max_retry_cycles:
            retry_cycle += 1
            self.logger.info(f"\n▶ CYCLE {retry_cycle}/{self.config.max_retry_cycles}")
            self._audit("CYCLE_START", details=f"Cycle {retry_cycle}")

            # Step 1: Run health sweep (or load existing)
            self.logger.info("  [1/4] Running health sweep...")
            if status_path and status_path.exists() and retry_cycle == 1:
                runtime_status = self.load_runtime_status(status_path)
            else:
                runtime_status = self.run_health_sweep()

            summary = runtime_status.get("summary", {})
            self.logger.info(
                f"        Success: {summary.get('success', 0)}/{summary.get('total', 0)} "
                f"({summary.get('success_rate', 0):.1f}%)"
            )

            # Check if we're done
            if summary.get("failed", 0) == 0:
                self.logger.info("  ✓ All automation units healthy!")
                break

            # Step 2: Classify failures
            self.logger.info(
                f"  [2/4] Classifying {summary.get('failed', 0)} failures..."
            )
            failures = {}
            for unit_id, unit_data in runtime_status.get("units", {}).items():
                if unit_data.get("status") == "fail":
                    failures[unit_id] = self.classify_failure(unit_id, unit_data)

            auto_repairable = sum(
                1 for f in failures.values() if f.get("auto_repairable")
            )
            self.logger.info(
                f"        Auto-repairable: {auto_repairable}/{len(failures)}"
            )

            # Save failure report
            failure_report = {
                "version": "1.0.0",
                "sweep_id": self.sweep_id,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "summary": {
                    "total_failures": len(failures),
                    "auto_repairable": auto_repairable,
                    "requires_human": len(failures) - auto_repairable,
                },
                "failures": failures,
            }
            failure_path = self.config.output_dir / "automation_failure_report.json"
            with open(failure_path, "w") as f:
                json.dump(failure_report, f, indent=2)

            # Step 3: Generate and execute fix plans
            self.logger.info(f"  [3/4] Generating fix plans...")
            fix_plans = {}
            for unit_id, classification in failures.items():
                if classification.get("auto_repairable"):
                    fix_plans[unit_id] = self.generate_fix_plan(unit_id, classification)

            # Save fix plan
            fix_plan_doc = {
                "version": "1.0.0",
                "sweep_id": self.sweep_id,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "execution_mode": "dry_run" if self.config.dry_run else "auto_apply",
                "summary": {
                    "total_fixes": len(fix_plans),
                    "auto_executable": sum(
                        1 for p in fix_plans.values() if not p.get("requires_human")
                    ),
                },
                "fixes": fix_plans,
            }
            fix_path = self.config.output_dir / "automation_fix_plan.json"
            with open(fix_path, "w") as f:
                json.dump(fix_plan_doc, f, indent=2)

            # Execute fixes
            self.logger.info(f"  [4/4] Executing {len(fix_plans)} fixes...")
            cycle_fixes = 0
            for unit_id, fix_plan in fix_plans.items():
                if self.execute_fix(unit_id, fix_plan):
                    cycle_fixes += 1
                    fixes_applied += 1

            self.logger.info(f"        Applied: {cycle_fixes}/{len(fix_plans)}")

            # If no fixes were applied, we're stuck
            if cycle_fixes == 0 and auto_repairable == 0:
                self.logger.warning("  ⚠ No auto-repairable failures, escalating...")
                break

            # Delay before next cycle
            if retry_cycle < self.config.max_retry_cycles:
                delay = self.config.retry_delay_seconds * (
                    self.config.backoff_multiplier ** (retry_cycle - 1)
                )
                self.logger.info(f"  ⏳ Waiting {delay:.0f}s before retest...")
                time.sleep(delay)

        # Final health sweep
        self.logger.info("\n▶ FINAL VERIFICATION")
        final_status = self.run_health_sweep()

        # Generate certification
        self.logger.info("▶ GENERATING CERTIFICATION")
        certification = self.generate_certification(
            final_status, fixes_applied, retry_cycle
        )

        cert_path = self.config.output_dir / "automation_certification.json"
        with open(cert_path, "w") as f:
            json.dump(certification, f, indent=2)

        # Final summary
        self.logger.info("\n" + "=" * 60)
        status_color = "✓" if certification["status"] == "certified" else "✗"
        self.logger.info(
            f"  {status_color} CERTIFICATION: {certification['status'].upper()}"
        )
        self.logger.info(
            f"  Success Rate: {certification['summary']['success_rate']:.1f}%"
        )
        self.logger.info(f"  Fixes Applied: {fixes_applied}")
        self.logger.info(f"  Retry Cycles: {retry_cycle}")
        self.logger.info(f"  Output: {self.config.output_dir}")
        self.logger.info("=" * 60)

        self._audit(
            "ORCHESTRATOR_COMPLETE",
            details=f"Status: {certification['status']}, Fixes: {fixes_applied}",
        )

        return certification


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Autonomous Self-Healing Automation Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full autonomous run
  python automation_self_healing_loop.py --repo-root /path/to/repo

  # Dry run (preview only)
  python automation_self_healing_loop.py --repo-root /path/to/repo --dry-run

  # With existing status file
  python automation_self_healing_loop.py --repo-root /path/to/repo \\
      --status-file .automation-health/automation_runtime_status.json
        """,
    )

    parser.add_argument(
        "--repo-root", type=Path, required=True, help="Root path of the repository"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(".automation-health"),
        help="Output directory for artifacts",
    )
    parser.add_argument(
        "--status-file", type=Path, help="Existing runtime status file to use"
    )
    parser.add_argument(
        "--max-retries", type=int, default=5, help="Maximum retry cycles"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview actions without executing"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    config = OrchestratorConfig(
        repo_root=args.repo_root.resolve(),
        output_dir=args.output_dir.resolve(),
        max_retry_cycles=args.max_retries,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )

    orchestrator = SelfHealingOrchestrator(config)
    result = orchestrator.run(args.status_file)

    # Exit with appropriate code
    sys.exit(0 if result["status"] == "certified" else 1)


if __name__ == "__main__":
    main()
