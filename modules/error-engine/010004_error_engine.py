from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from modules.error_engine import PipelineEngine
from modules.error_engine import PluginManager
from modules.error_engine import FileHashCache
from error.shared.utils.types import PluginIssue
from .error_context import ErrorPipelineContext


def run_error_pipeline(
    python_files: List[str],
    powershell_files: List[str],
    ctx: ErrorPipelineContext,
) -> Dict[str, Any]:
    """
    Run the canonical error pipeline using the plugin-based engine and normalize
    the aggregated report to the Operating Contract schema.
    """
    # For now, powershell_files are ignored until PS plugins are present
    files = [Path(p) for p in python_files]

    cache_path = Path(".state") / "validation_cache.json"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache = FileHashCache(cache_path)
    cache.load()

    pm = PluginManager()
    engine = PipelineEngine(pm, cache)

    all_issues: List[Dict[str, Any]] = []
    outputs: List[Tuple[str, str]] = []  # (input, output)
    totals_by_tool: Dict[str, int] = {}
    totals_by_category: Dict[str, int] = {}
    total_errors = 0
    total_warnings = 0

    for f in files:
        rep = engine.process_file(f)
        if rep.file_out:
            outputs.append((str(f), rep.file_out))
        for iss in rep.issues:
            d = {
                "tool": iss.tool,
                "path": iss.path,
                "line": iss.line,
                "column": iss.column,
                "code": iss.code,
                "category": iss.category,
                "severity": iss.severity,
                "message": iss.message,
            }
            all_issues.append(d)
            tool = d["tool"] or "unknown"
            cat = d["category"] or "other"
            totals_by_tool[tool] = totals_by_tool.get(tool, 0) + 1
            totals_by_category[cat] = totals_by_category.get(cat, 0) + 1
            sev = (d["severity"] or "").lower()
            if sev == "error":
                total_errors += 1
            elif sev == "warning":
                total_warnings += 1

    has_hard_fail = any(totals_by_category.get(k, 0) > 0 for k in ("syntax", "type", "test_failure"))
    total_issues = sum(totals_by_tool.values())
    style_only = (not has_hard_fail) and (
        total_issues == (totals_by_category.get("style", 0) + totals_by_category.get("formatting", 0))
    )

    report = {
        "attempt_number": ctx.attempt_number,
        "ai_agent": ctx.current_agent,
        "run_id": ctx.run_id,
        "workstream_id": ctx.workstream_id,
        "issues": all_issues,
        "outputs": [{"input": i, "output": o} for (i, o) in outputs],
        "summary": {
            "total_issues": total_issues,
            "issues_by_tool": totals_by_tool,
            "issues_by_category": totals_by_category,
            "has_hard_fail": has_hard_fail,
            "style_only": style_only,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
        },
    }

    return report
