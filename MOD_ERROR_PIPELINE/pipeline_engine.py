"""Minimal deterministic pipeline engine implementation.

Coordinates hashing, plugin execution, temp-dir isolation, and reporting.
"""
from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from src.utils.time import new_run_id, utc_now_iso
from src.utils.jsonl_manager import append as jsonl_append
from src.utils.types import (
    PipelineReport,
    PluginResult,
    PipelineSummary,
    PluginIssue,
)


class PipelineEngine:
    """Co-ordinates validation work across the GUI and plugin system."""

    def __init__(
        self,
        plugin_manager,
        hash_cache,
    ) -> None:
        self._plugin_manager = plugin_manager
        self._hash_cache = hash_cache

    def process_files(self, file_paths: Iterable[Path]) -> List[PipelineReport]:
        """Process a batch of files through the validation pipeline."""
        reports: List[PipelineReport] = []
        for file_path in file_paths:
            reports.append(self.process_file(file_path))
        return reports

    def process_file(self, file_path: Path) -> PipelineReport:
        """Validate a single file using the registered plugins."""
        run_id = new_run_id()
        ts = utc_now_iso()

        # Incremental skip check
        changed = self._hash_cache.has_changed(file_path)
        if not changed:
            report = PipelineReport(
                run_id=run_id,
                file_in=str(file_path),
                file_out=None,
                timestamp_utc=ts,
                toolchain={},
                summary=PipelineSummary(
                    plugins_run=0, total_errors=0, total_warnings=0, auto_fixed=0
                ),
                issues=[],
                status="skipped",
            )
            # Append event to JSONL
            jsonl_append(Path("pipeline_errors.jsonl"), {"event": "skipped", "file": str(file_path), "run_id": run_id, "ts": ts})
            return report

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            tmp_file = tmpdir_path / file_path.name
            shutil.copy2(file_path, tmp_file)

            # Discover/apply plugins
            self._plugin_manager.discover()
            plugins = self._plugin_manager.get_plugins_for_file(tmp_file)
            plugin_results = self._run_plugins(tmp_file)

            # Copy out with validated name
            out_name = f"{file_path.stem}_VALIDATED_{ts.replace(':','').replace('-','').replace('.','')}_{run_id}{file_path.suffix}"
            out_file = file_path.parent / out_name
            shutil.copy2(tmp_file, out_file)

        # Generate and persist report
        report = self._generate_report(file_path, plugin_results, run_id)
        report.file_out = str(out_file)
        # Write per-file JSON next to output
        report_json_path = out_file.with_suffix(out_file.suffix + ".json")
        report_json_path.write_text(json.dumps(_report_to_dict(report), ensure_ascii=False, indent=2), encoding="utf-8")

        # Append aggregated JSONL
        jsonl_append(Path("pipeline_errors.jsonl"), {
            "event": "validated",
            "file": str(file_path),
            "out": str(out_file),
            "run_id": run_id,
            "ts": ts,
            "summary": {
                "errors": report.summary.total_errors if report.summary else 0,
                "warnings": report.summary.total_warnings if report.summary else 0,
            },
        })

        # Update cache
        had_errors = (report.summary.total_errors > 0) if report.summary else False
        self._hash_cache.mark_validated(file_path, had_errors=had_errors)
        self._hash_cache.save()

        return report

    def _run_plugins(self, file_path: Path) -> List[PluginResult]:
        """Execute all applicable plugins for the given file."""
        plugins = self._plugin_manager.get_plugins_for_file(file_path)
        results = self._plugin_manager.run_plugins(plugins, file_path)
        return results

    def _generate_report(
        self,
        file_path: Path,
        plugin_results: List[PluginResult],
        run_id: Optional[str] = None,
    ) -> PipelineReport:
        """Create the final report structure returned to the GUI layer."""
        ts = utc_now_iso()
        # Flatten issues and compute summary
        issues: List[PluginIssue] = []
        issues_by_tool: Dict[str, int] = {}
        issues_by_category: Dict[str, int] = {}
        total_errors = 0
        total_warnings = 0
        for r in plugin_results:
            for iss in r.issues:
                issues.append(iss)
                issues_by_tool[iss.tool] = issues_by_tool.get(iss.tool, 0) + 1
                cat = iss.category or "other"
                issues_by_category[cat] = issues_by_category.get(cat, 0) + 1
                sev = (iss.severity or "").lower()
                if sev == "error":
                    total_errors += 1
                elif sev == "warning":
                    total_warnings += 1

        has_hard_fail = any(c in issues_by_category and issues_by_category[c] > 0 for c in ("syntax", "type", "test_failure"))
        style_only = (not has_hard_fail) and (sum(issues_by_category.values()) == issues_by_category.get("style", 0) + issues_by_category.get("formatting", 0))

        summary = PipelineSummary(
            plugins_run=len(plugin_results),
            total_errors=total_errors,
            total_warnings=total_warnings,
            auto_fixed=0,
            issues_by_tool=issues_by_tool,
            issues_by_category=issues_by_category,
            has_hard_fail=has_hard_fail,
            style_only=style_only,
        )

        report = PipelineReport(
            run_id=run_id or new_run_id(),
            file_in=str(file_path),
            file_out=None,
            timestamp_utc=ts,
            toolchain={},
            summary=summary,
            issues=issues,
            status="completed",
        )
        return report


def _report_to_dict(report: PipelineReport) -> dict:
    def issue_to_dict(i: PluginIssue) -> dict:
        return {
            "tool": i.tool,
            "path": i.path,
            "line": i.line,
            "column": i.column,
            "code": i.code,
            "category": i.category,
            "severity": i.severity,
            "message": i.message,
        }

    def summary_to_dict(s: PipelineSummary) -> dict:
        return {
            "plugins_run": s.plugins_run,
            "total_errors": s.total_errors,
            "total_warnings": s.total_warnings,
            "auto_fixed": s.auto_fixed,
            "issues_by_tool": s.issues_by_tool,
            "issues_by_category": s.issues_by_category,
            "has_hard_fail": s.has_hard_fail,
            "style_only": s.style_only,
        }

    return {
        "run_id": report.run_id,
        "file_in": report.file_in,
        "file_out": report.file_out,
        "timestamp_utc": report.timestamp_utc,
        "toolchain": report.toolchain,
        "summary": summary_to_dict(report.summary) if report.summary else None,
        "issues": [issue_to_dict(i) for i in report.issues],
        "status": report.status,
    }
