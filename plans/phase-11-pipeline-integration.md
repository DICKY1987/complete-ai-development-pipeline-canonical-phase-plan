# Phase 11: Pipeline integration (file-analyzer, test-runner, code-analyzer)

Wire the OpenSpec bundle inputs and Agent Coordinator into an executable pipeline
that invokes three key agents (file-analyzer, test-runner, code-analyzer) and
respects simple state transitions (S0 → S1 → S2 → S3_RECHECK → S_SUCCESS/S_FAILED).

## Objectives

- Define minimal state model and transitions for the error pipeline.
- Integrate Agent Coordinator to run each stage in parallel across units.
- Add adapters for the three agents with a uniform plugin interface.
- Provide tests that simulate end-to-end stage progression and outcomes.

## Prerequisites

- Phase 09 and Phase 10 completed or code snippets available.
- Python 3.10+, `pytest`.
- Access to `MOD_ERROR_PIPELINE/pipeline_engine.py` for reference.

## Tasks

1. Create `src/pipeline/error_pipeline_service.py` with a simple state machine.
2. Write thin adapters for: file-analyzer, test-runner, code-analyzer.
3. Use `run_parallel` for each stage and collect results.
4. Implement S3_RECHECK strategy: re-run failed units once (test-runner).
5. Emit a final summary with success/failure counts per stage.
6. Add tests in `tests/test_pipeline_integration.py`.

## Code snippets

Place at `src/pipeline/error_pipeline_service.py`.

```python
# src/pipeline/error_pipeline_service.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Sequence

from .agent_coordinator import PluginResult, run_parallel


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
    sumqa = _sum(S1_FILE_ANALYZED, sqa)  # reuse structure; stage name not strictly needed here

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
```

Create `tests/test_pipeline_integration.py`:

```python
# tests/test_pipeline_integration.py
from src.pipeline.error_pipeline_service import run_pipeline, S_SUCCESS, S_FAILED


def test_pipeline_success():
    units = ["alpha", "beta"]
    out = run_pipeline(units, max_workers=2)
    assert out["state"] == S_SUCCESS
    assert out["S2"]["failed"] == 0


def test_pipeline_recheck_and_fail():
    units = ["ok-1", "must-fail-2"]
    out = run_pipeline(units, max_workers=2)
    assert out["state"] == S_FAILED
    assert "must-fail-2" in out["failed_units"]
```

Run tests:

```bash
pytest -q -k pipeline_integration
```

## Integration points

- Replace stubs with real adapters:
  - file-analyzer: invoke actual tool/agent, map outputs to `PluginResult`.
  - test-runner: call local runner or CI command, capture pass/fail per unit.
  - code-analyzer: connect to linter/static analysis;
- Embed `run_pipeline` into the dispatcher within
  `MOD_ERROR_PIPELINE/pipeline_engine.py` or a new entry in `scripts/`.

## Rollback plan

- Remove `src/pipeline/error_pipeline_service.py` and the tests for this phase.
- Restore previous pipeline entry behavior if any scripts were modified.

