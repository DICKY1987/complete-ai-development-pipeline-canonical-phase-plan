from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Any, Dict, List, Sequence

from core.agent_coordinator import PluginResult, run_parallel


S0_INIT = "S0_INIT"
S1_FILE_ANALYZED = "S1_FILE_ANALYZED"
S2_TESTED = "S2_TESTED"
S3_RECHECK = "S3_RECHECK"
S_SUCCESS = "S_SUCCESS"
S_FAILED = "S_FAILED"


@dataclass
class StageSummary:
    stage: str
    total: int
    ok: int
    failed: int
    units: List[str]


def _adapter_file_analyzer(uid: str, args: Dict[str, Any]) -> PluginResult:
    # Stub: summarize errors; in real impl, invoke tool/agent
    return PluginResult(unit_id=uid, ok=True, summary="file analyzed", artifacts={})


def _adapter_test_runner(uid: str, args: Dict[str, Any]) -> PluginResult:
    # Stub: run tests; simulate failure if unit id contains "fail"
    ok = "fail" not in uid
    return PluginResult(unit_id=uid, ok=ok, summary="tests run", artifacts={})


def _adapter_code_analyzer(uid: str, args: Dict[str, Any]) -> PluginResult:
    # Stub: code quality checks
    return PluginResult(unit_id=uid, ok=True, summary="code analyzed", artifacts={})


def _sum(stage: str, results: Sequence[PluginResult]) -> StageSummary:
    total = len(results)
    ok = sum(1 for r in results if r.ok)
    return StageSummary(stage=stage, total=total, ok=ok, failed=total - ok, units=[r.unit_id for r in results])


def run_pipeline(units: Sequence[str], max_workers: int = 4) -> Dict[str, Any]:
    # S0 -> S1 (file analyzer)
    s1 = run_parallel(units, _adapter_file_analyzer, max_workers=max_workers)
    sum1 = _sum(S1_FILE_ANALYZED, s1)

    # S1 -> S2 (test runner)
    s2 = run_parallel(units, _adapter_test_runner, max_workers=max_workers)
    sum2 = _sum(S2_TESTED, s2)

    # S2 -> S3_RECHECK for failed units
    failed_units = [r.unit_id for r in s2 if not r.ok]
    if failed_units:
        s3 = run_parallel(failed_units, _adapter_test_runner, {"recheck": True}, max_workers=max_workers)
        sum3 = _sum(S3_RECHECK, s3)
        final_failed = [r.unit_id for r in s3 if not r.ok]
    else:
        sum3 = StageSummary(stage=S3_RECHECK, total=0, ok=0, failed=0, units=[])
        final_failed = []

    # Code analyzer always runs on all units for consistency
    sqa = run_parallel(units, _adapter_code_analyzer, max_workers=max_workers)
    sumqa = _sum("S_QA_CODE_ANALYZED", sqa)

    # Final state
    overall = S_SUCCESS if not final_failed else S_FAILED
    return {
        "state": overall,
        "S1": dataclasses.asdict(sum1),
        "S2": dataclasses.asdict(sum2),
        "S3": dataclasses.asdict(sum3),
        "QA": dataclasses.asdict(sumqa),
        "failed_units": final_failed,
    }

