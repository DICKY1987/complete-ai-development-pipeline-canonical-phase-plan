#!/usr/bin/env python3
"""
Comprehensive Archival Analyzer - Master Orchestrator
======================================================
Orchestrates all cleanup analyzers and generates unified tiered reports.

Integrates 6 signals:
1. Duplication (EXEC-014)
2. Staleness (EXEC-015)
3. Obsolescence
4. Isolation (EXEC-013)
5. Reachability (NEW)
6. Test Coverage (NEW)

Outputs:
- comprehensive_archival_report.json
- archival_plan_tier1_automated.ps1
- archival_plan_tier2_review.json
- archival_plan_tier3_manual.json
- parallel_implementations_decision_checklist.md
- validation_checklist.md

Pattern: EXEC-017
Author: GitHub Copilot CLI
Version: 1.0.0
Date: 2025-12-02
"""
DOC_ID: DOC-SCRIPT-SCRIPTS-COMPREHENSIVE-ARCHIVAL-ANALYZER-708
DOC_ID: DOC - SCRIPT - SCRIPTS - COMPREHENSIVE - ARCHIVAL - ANALYZER - 708

import argparse
import json
import logging
import subprocess
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@dataclass
class ComprehensiveFileScore:
    """Comprehensive file scoring with 6 signals."""

    path: str
    duplication_score: int = 0
    staleness_score: int = 0
    obsolescence_score: int = 0
    isolation_score: int = 0
    reachability_score: int = 0
    test_coverage_score: int = 0
    composite_score: int = 0
    confidence: int = 0
    tier: str = "TIER_4"  # TIER_1, TIER_2, TIER_3, TIER_4
    action: str = "KEEP"
    reasons: List[str] = None

    def __post_init__(self):
        if self.reasons is None:
            self.reasons = []

        # Weighted composite (matching EXEC-017 spec)
        self.composite_score = int(
            self.duplication_score * 0.25
            + self.staleness_score * 0.15
            + self.obsolescence_score * 0.20
            + self.isolation_score * 0.15
            + self.reachability_score * 0.15
            + self.test_coverage_score * 0.10
        )

        # Confidence boost if multiple signals agree
        high_signal_count = sum(
            [
                self.duplication_score >= 80,
                self.staleness_score >= 80,
                self.obsolescence_score >= 80,
                self.isolation_score >= 80,
                self.reachability_score >= 80,
                self.test_coverage_score >= 80,
            ]
        )

        self.confidence = min(
            100, self.composite_score + (10 if high_signal_count >= 3 else 0)
        )

        # Tier assignment
        if self.confidence >= 90:
            self.tier = "TIER_1"
            self.action = "ARCHIVE"
        elif self.confidence >= 75:
            self.tier = "TIER_2"
            self.action = "REVIEW"
        elif self.confidence >= 60:
            self.tier = "TIER_3"
            self.action = "EXPERT_REVIEW"
        else:
            self.tier = "TIER_4"
            self.action = "KEEP"


class ComprehensiveArchivalAnalyzer:
    """Master orchestrator for comprehensive archival analysis."""

    def __init__(
        self,
        root: Path,
        confidence_threshold: int,
        staleness_days: int,
        exclude_extensions: List[str],
        output_dir: Path,
    ):
        self.root = root
        self.confidence_threshold = confidence_threshold
        self.staleness_days = staleness_days
        self.exclude_extensions = set(exclude_extensions)
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)

        self.reachability_data: Dict = {}
        self.test_coverage_data: Dict = {}
        self.parallel_impl_data: Dict = {}
        self.cleanup_data: Dict = {}

        self.comprehensive_scores: Dict[str, ComprehensiveFileScore] = {}

    def run_all_analyzers(self):
        """Execute all analyzer scripts in sequence."""
        logger.info("=" * 70)
        logger.info("COMPREHENSIVE ARCHIVAL ANALYSIS - EXEC-017")
        logger.info("=" * 70)
        logger.info("")

        # Step 1: Entry Point Reachability
        logger.info("Step 1/5: Running entry point reachability analysis...")
        self._run_analyzer(
            "python",
            "scripts/entry_point_reachability.py",
            "--output",
            str(self.output_dir / "entry_point_reachability_report.json"),
        )
        self.reachability_data = self._load_json(
            self.output_dir / "entry_point_reachability_report.json"
        )

        # Step 2: Test Coverage
        logger.info("\nStep 2/5: Running test coverage analysis...")
        self._run_analyzer(
            "python",
            "scripts/test_coverage_archival.py",
            "--output",
            str(self.output_dir / "test_coverage_archival_report.json"),
        )
        self.test_coverage_data = self._load_json(
            self.output_dir / "test_coverage_archival_report.json"
        )

        # Step 3: Parallel Implementations
        logger.info("\nStep 3/5: Running parallel implementation detection...")
        self._run_analyzer(
            "python",
            "scripts/detect_parallel_implementations.py",
            "--output",
            str(self.output_dir / "parallel_implementations_analysis.json"),
        )
        self.parallel_impl_data = self._load_json(
            self.output_dir / "parallel_implementations_analysis.json"
        )

        # Step 4: Main Cleanup Analyzer (with new thresholds)
        logger.info("\nStep 4/5: Running main cleanup analyzer...")
        self._run_analyzer(
            "python",
            "scripts/analyze_cleanup_candidates.py",
            "--confidence-threshold",
            str(self.confidence_threshold),
            "--exclude-extensions",
            ",".join(self.exclude_extensions),
            "--output-dir",
            str(self.output_dir),
        )
        # Load most recent cleanup report
        cleanup_reports = sorted(self.output_dir.glob("cleanup_report_*.json"))
        if cleanup_reports:
            self.cleanup_data = self._load_json(cleanup_reports[-1])

        # Step 5: Aggregate signals
        logger.info("\nStep 5/5: Aggregating signals and scoring...")
        self._aggregate_signals()

        logger.info("\n✅ All analyzers completed successfully")

    def _run_analyzer(self, *args):
        """Run an analyzer script."""
        try:
            result = subprocess.run(
                args,
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=600,  # Increased to 10 minutes for large codebases
            )

            if result.returncode != 0:
                logger.error(f"Analyzer failed: {' '.join(args)}")
                logger.error(f"Error: {result.stderr}")
                return False

            return True
        except subprocess.TimeoutExpired:
            logger.error(f"Analyzer timed out: {' '.join(args)}")
            return False
        except Exception as e:
            logger.error(f"Analyzer exception: {e}")
            return False

    def _load_json(self, path: Path) -> Dict:
        """Load JSON file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Cannot load {path}: {e}")
            return {}

    def _aggregate_signals(self):
        """Aggregate all signals into comprehensive scores."""
        logger.info("Aggregating signals from all analyzers...")

        # Extract scores from each analyzer
        reachability_scores = self.reachability_data.get("reachability_scores", {})
        test_coverage_scores = self.test_coverage_data.get("test_coverage_scores", {})

        # Get all Python files
        all_files = set()
        for py_file in self.root.rglob("*.py"):
            if self._should_skip(py_file):
                continue

            ext = py_file.suffix.lower()
            if ext in self.exclude_extensions:
                continue

            rel_path = str(py_file.relative_to(self.root))
            all_files.add(rel_path)

        # Create comprehensive scores
        for file_path in all_files:
            module_name = self._path_to_module(file_path)

            # Get reachability score
            reach_data = reachability_scores.get(module_name, {})
            reach_score = (
                reach_data.get("score", 0) if isinstance(reach_data, dict) else 0
            )

            # Get test coverage score
            test_data = test_coverage_scores.get(module_name, {})
            test_score = test_data.get("score", 0) if isinstance(test_data, dict) else 0

            # Get cleanup analyzer scores (if available)
            dup_score = 0
            stale_score = 0
            obs_score = 0
            iso_score = 0

            if self.cleanup_data:
                # Handle different possible data structures
                if "file_scores" in self.cleanup_data:
                    for file_score in self.cleanup_data["file_scores"]:
                        if (
                            isinstance(file_score, dict)
                            and file_score.get("path") == file_path
                        ):
                            dup_score = file_score.get("duplication_score", 0)
                            stale_score = file_score.get("staleness_score", 0)
                            obs_score = file_score.get("obsolescence_score", 0)
                            iso_score = file_score.get("isolation_score", 0)
                            break
                elif "files" in self.cleanup_data:
                    # Alternative structure
                    file_data = self.cleanup_data["files"].get(file_path, {})
                    if isinstance(file_data, dict):
                        dup_score = file_data.get("duplication_score", 0)
                        stale_score = file_data.get("staleness_score", 0)
                        obs_score = file_data.get("obsolescence_score", 0)
                        iso_score = file_data.get("isolation_score", 0)

            # Build comprehensive score
            reasons = []
            if reach_score >= 80:
                reasons.append(f"Reachability: {reach_score}/100 (orphaned)")
            if test_score >= 80:
                reasons.append(f"Test coverage: {test_score}/100 (untested)")
            if stale_score >= 80:
                reasons.append(f"Staleness: {stale_score}/100 (90+ days)")
            if iso_score >= 80:
                reasons.append(f"Isolation: {iso_score}/100 (not imported)")
            if dup_score >= 80:
                reasons.append(f"Duplication: {dup_score}/100")
            if obs_score >= 80:
                reasons.append(f"Obsolescence: {obs_score}/100 (deprecated)")

            self.comprehensive_scores[file_path] = ComprehensiveFileScore(
                path=file_path,
                duplication_score=dup_score,
                staleness_score=stale_score,
                obsolescence_score=obs_score,
                isolation_score=iso_score,
                reachability_score=reach_score,
                test_coverage_score=test_score,
                reasons=reasons,
            )

        logger.info(f"Aggregated scores for {len(self.comprehensive_scores)} files")

    def _should_skip(self, path: Path) -> bool:
        """Check if path should be skipped."""
        parts = path.parts
        skip_dirs = {"__pycache__", ".git", ".venv", ".worktrees", "node_modules"}
        return any(part in skip_dirs for part in parts)

    def _path_to_module(self, file_path: str) -> str:
        """Convert file path to module name."""
        module_path = file_path.replace("\\", ".").replace("/", ".").replace(".py", "")
        return module_path

    def generate_tiered_reports(self):
        """Generate tiered reports based on confidence levels."""
        logger.info("Generating tiered reports...")

        tier1_files = []
        tier2_files = []
        tier3_files = []
        tier4_files = []

        for path, score in self.comprehensive_scores.items():
            if score.tier == "TIER_1":
                tier1_files.append(asdict(score))
            elif score.tier == "TIER_2":
                tier2_files.append(asdict(score))
            elif score.tier == "TIER_3":
                tier3_files.append(asdict(score))
            else:
                tier4_files.append(asdict(score))

        # Sort by confidence descending
        tier1_files.sort(key=lambda x: x["confidence"], reverse=True)
        tier2_files.sort(key=lambda x: x["confidence"], reverse=True)
        tier3_files.sort(key=lambda x: x["confidence"], reverse=True)

        # Generate comprehensive report
        report = {
            "metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "pattern": "EXEC-017",
                "configuration": {
                    "confidence_threshold": self.confidence_threshold,
                    "staleness_days": self.staleness_days,
                    "exclude_extensions": list(self.exclude_extensions),
                },
            },
            "statistics": {
                "total_files_analyzed": len(self.comprehensive_scores),
                "tier_1_count": len(tier1_files),
                "tier_2_count": len(tier2_files),
                "tier_3_count": len(tier3_files),
                "tier_4_count": len(tier4_files),
            },
            "tier_1_summary": {
                "count": len(tier1_files),
                "confidence_range": "90-100%",
                "action": "SAFE FOR AUTOMATED ARCHIVAL",
                "files": tier1_files[:10],  # Top 10 for summary
            },
            "tier_2_summary": {
                "count": len(tier2_files),
                "confidence_range": "75-89%",
                "action": "REVIEW RECOMMENDED",
                "files": tier2_files[:10],
            },
            "tier_3_summary": {
                "count": len(tier3_files),
                "confidence_range": "60-74%",
                "action": "MANUAL EXPERT REVIEW",
                "files": tier3_files[:10],
            },
            "signal_convergence": {
                "3_plus_signals": sum(
                    1
                    for s in self.comprehensive_scores.values()
                    if sum(
                        [
                            s.duplication_score >= 80,
                            s.staleness_score >= 80,
                            s.obsolescence_score >= 80,
                            s.isolation_score >= 80,
                            s.reachability_score >= 80,
                            s.test_coverage_score >= 80,
                        ]
                    )
                    >= 3
                )
            },
        }

        # Write comprehensive report
        report_path = self.output_dir / "comprehensive_archival_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        logger.info(f"✅ Comprehensive report: {report_path}")

        # Write tier-specific reports
        tier2_path = self.output_dir / "archival_plan_tier2_review.json"
        with open(tier2_path, "w", encoding="utf-8") as f:
            json.dump({"tier_2_files": tier2_files}, f, indent=2)
        logger.info(f"✅ Tier 2 review list: {tier2_path}")

        tier3_path = self.output_dir / "archival_plan_tier3_manual.json"
        with open(tier3_path, "w", encoding="utf-8") as f:
            json.dump({"tier_3_files": tier3_files}, f, indent=2)
        logger.info(f"✅ Tier 3 manual review: {tier3_path}")

        # Generate PowerShell script for Tier 1
        self._generate_tier1_script(tier1_files)

        # Generate validation checklist
        self._generate_validation_checklist()

        return report

    def _generate_tier1_script(self, tier1_files: List[Dict]):
        """Generate PowerShell script for Tier 1 automated archival."""
        script_path = self.output_dir / "archival_plan_tier1_automated.ps1"

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        archive_dir = f"archive/{timestamp}_python-code-cleanup"

        script_lines = [
            "# EXEC-017 Tier 1 Automated Archival Script",
            "# Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "# Confidence: 90-100% (Safe for automated archival)",
            "",
            "$DryRun = $true  # Set to $false to execute",
            f"$ArchiveDir = '{archive_dir}'",
            "",
            "# Create archive directory",
            "if (-not $DryRun) {",
            "    New-Item -ItemType Directory -Force -Path $ArchiveDir | Out-Null",
            "    Write-Host '✅ Created archive directory: $ArchiveDir' -ForegroundColor Green",
            "}",
            "",
            f"# Archive {len(tier1_files)} files",
            "",
        ]

        for i, file_data in enumerate(tier1_files, 1):
            file_path = file_data["path"]
            confidence = file_data["confidence"]
            reasons = file_data.get("reasons", [])

            script_lines.append(f"# File {i}/{len(tier1_files)}: {file_path}")
            script_lines.append(f"# Confidence: {confidence}%")
            for reason in reasons[:3]:  # Top 3 reasons
                script_lines.append(f"#   - {reason}")

            script_lines.append("if ($DryRun) {")
            script_lines.append(
                f"    Write-Host '[DRY RUN] Would archive: {file_path}' -ForegroundColor Yellow"
            )
            script_lines.append("} else {")
            script_lines.append(f"    $Source = '{file_path}'")
            script_lines.append("    $Dest = Join-Path $ArchiveDir $Source")
            script_lines.append(
                "    New-Item -ItemType Directory -Force -Path (Split-Path $Dest) | Out-Null"
            )
            script_lines.append("    Move-Item -Path $Source -Destination $Dest -Force")
            script_lines.append(
                f"    Write-Host '✅ Archived: {file_path}' -ForegroundColor Green"
            )
            script_lines.append("}")
            script_lines.append("")

        script_lines.extend(
            [
                "if ($DryRun) {",
                "    Write-Host ''",
                "    Write-Host '[!] DRY RUN MODE - No files were moved' -ForegroundColor Yellow",
                "    Write-Host 'To execute: Edit this script and set $DryRun = $false' -ForegroundColor Yellow",
                "} else {",
                "    Write-Host ''",
                "    Write-Host '[OK] Archival complete!' -ForegroundColor Green",
                f"    Write-Host 'Files archived to: {archive_dir}' -ForegroundColor Green",
                "}",
            ]
        )

        with open(script_path, "w", encoding="utf-8") as f:
            f.write("\n".join(script_lines))

        logger.info(f"✅ Tier 1 PowerShell script: {script_path}")

    def _generate_validation_checklist(self):
        """Generate validation checklist markdown."""
        checklist_path = self.output_dir / "validation_checklist.md"

        lines = [
            "# Archival Validation Checklist",
            "",
            "**Generated**: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "**Pattern**: EXEC-017",
            "",
            "## Pre-Archive Validation",
            "",
            "- [ ] Review comprehensive_archival_report.json",
            "- [ ] Review parallel_implementations_decision_checklist.md",
            "- [ ] Review Tier 1 candidates (90%+ confidence)",
            "- [ ] Run pre-archive validation:",
            "  ```bash",
            "  python scripts/validate_archival_safety.py --mode pre-archive",
            "  ```",
            "- [ ] Git status clean (no uncommitted changes)",
            "- [ ] Test suite passing:",
            "  ```bash",
            "  pytest -q tests/",
            "  ```",
            "",
            "## Execution",
            "",
            "- [ ] Run Tier 1 script in DRY RUN mode:",
            "  ```powershell",
            "  .\\cleanup_reports\\archival_plan_tier1_automated.ps1",
            "  ```",
            "- [ ] Review dry run output",
            "- [ ] If satisfied, edit script: Set `$DryRun = $false`",
            "- [ ] Execute archival",
            "",
            "## Post-Archive Validation",
            "",
            "- [ ] Run post-archive validation:",
            "  ```bash",
            "  python scripts/validate_archival_safety.py --mode post-archive",
            "  ```",
            "- [ ] Test suite still passing:",
            "  ```bash",
            "  pytest -q tests/",
            "  ```",
            "- [ ] No import errors",
            "- [ ] Entry points functional",
            "- [ ] Git status check:",
            "  ```bash",
            "  git status",
            "  ```",
            "",
            "## Commit",
            "",
            "- [ ] Review changes",
            "- [ ] Commit with pattern-compliant message:",
            "  ```bash",
            "  git add .",
            '  git commit -m "chore: Archive obsolete Python code (Tier 1 - EXEC-017)',
            "",
            "  Archived N files based on comprehensive 6-signal analysis",
            "  Pattern: EXEC-017",
            "  Confidence: 90-100%",
            "  Configuration: 90-day staleness, 90% threshold",
            "",
            '  All validation checks passed"',
            "  ```",
            "",
            "## Rollback (if needed)",
            "",
            "- [ ] Option 1: Git revert",
            "  ```bash",
            "  git revert HEAD",
            "  ```",
            "- [ ] Option 2: Restore from archive",
            "  ```bash",
            "  # Copy files back from archive directory",
            "  ```",
            "",
        ]

        with open(checklist_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        logger.info(f"✅ Validation checklist: {checklist_path}")

    def print_summary(self, report: Dict):
        """Print execution summary."""
        print("\n" + "=" * 70)
        print("COMPREHENSIVE ARCHIVAL ANALYSIS SUMMARY")
        print("=" * 70)

        stats = report["statistics"]
        print(f"\nTotal files analyzed: {stats['total_files_analyzed']:,}")
        print(f"\nTiered Results:")
        print(
            f"  TIER 1 (90-100%): {stats['tier_1_count']:,} files - SAFE FOR AUTOMATED ARCHIVAL"
        )
        print(
            f"  TIER 2 (75-89%):  {stats['tier_2_count']:,} files - REVIEW RECOMMENDED"
        )
        print(
            f"  TIER 3 (60-74%):  {stats['tier_3_count']:,} files - MANUAL EXPERT REVIEW"
        )
        print(f"  TIER 4 (<60%):    {stats['tier_4_count']:,} files - KEEP")

        print(f"\nSignal Convergence:")
        print(
            f"  3+ signals ≥80:   {report['signal_convergence']['3_plus_signals']:,} files"
        )

        print(f"\nOutput files:")
        print(f"  1. comprehensive_archival_report.json")
        print(f"  2. archival_plan_tier1_automated.ps1")
        print(f"  3. archival_plan_tier2_review.json")
        print(f"  4. archival_plan_tier3_manual.json")
        print(f"  5. parallel_implementations_decision_checklist.md")
        print(f"  6. validation_checklist.md")

        print("\nNEXT STEPS:")
        print("=" * 70)
        print("1. Review: cleanup_reports/comprehensive_archival_report.json")
        print(
            "2. Review: cleanup_reports/parallel_implementations_decision_checklist.md"
        )
        print(
            "3. Validate: python scripts/validate_archival_safety.py --mode pre-archive"
        )
        print(
            "4. Execute (dry-run): .\\cleanup_reports\\archival_plan_tier1_automated.ps1"
        )
        print("5. Follow: cleanup_reports/validation_checklist.md")
        print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive Archival Analyzer - EXEC-017",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with defaults (90% threshold, 90-day staleness)
  python comprehensive_archival_analyzer.py

  # Run with custom settings
  python comprehensive_archival_analyzer.py --confidence-threshold 95 --staleness-days 60
        """,
    )

    parser.add_argument(
        "--root",
        "-r",
        type=Path,
        default=Path.cwd(),
        help="Repository root path (default: current directory)",
    )

    parser.add_argument(
        "--confidence-threshold",
        "-c",
        type=int,
        default=90,
        help="Confidence threshold for automated cleanup (default: 90)",
    )

    parser.add_argument(
        "--staleness-days",
        "-s",
        type=int,
        default=90,
        help="Days threshold for staleness (default: 90)",
    )

    parser.add_argument(
        "--exclude-extensions",
        type=str,
        default=".md,.txt",
        help="Comma-separated list of extensions to exclude (default: .md,.txt)",
    )

    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=Path("cleanup_reports"),
        help="Output directory for reports (default: cleanup_reports/)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    exclude_ext = [ext.strip() for ext in args.exclude_extensions.split(",")]

    analyzer = ComprehensiveArchivalAnalyzer(
        root=args.root,
        confidence_threshold=args.confidence_threshold,
        staleness_days=args.staleness_days,
        exclude_extensions=exclude_ext,
        output_dir=args.output_dir,
    )

    try:
        analyzer.run_all_analyzers()
        report = analyzer.generate_tiered_reports()
        analyzer.print_summary(report)

        sys.exit(0)
    except KeyboardInterrupt:
        logger.error("\n[X] Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n[X] Analysis failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
