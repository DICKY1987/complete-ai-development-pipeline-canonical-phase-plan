# Phase 10: Agent coordinator for parallel processing

This phase introduces a lightweight agent coordinator to partition work items and
run agent plugins in parallel, consolidating results deterministically.

## Objectives

- Partition input files/units across worker slots.
- Execute agent plugins in parallel with bounded concurrency.
- Provide standardized result envelopes (status, logs, artifacts).
- Include tests for partitioning and parallel execution behavior.

## Prerequisites

- Python 3.10+
- `pytest`
- Basic understanding of plugin interface contracts used by agents.

## Tasks

1. Implement coordinator in `src/pipeline/agent_coordinator.py`.
2. Define plugin call contract and result envelope.
3. Add balanced partitioning with stable assignment.
4. Add parallel execution via `ThreadPoolExecutor`.
5. Consolidate results with deterministic ordering and summary.
6. Add tests `tests/test_agent_coordinator.py`.

## Code snippets

Place the following at `src/pipeline/agent_coordinator.py`.

```python
# src/pipeline/agent_coordinator.py
from __future__ import annotations

import concurrent.futures as cf
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Sequence, Tuple


@dataclass
class PluginResult:
    unit_id: str
    ok: bool
    summary: str
    artifacts: Dict[str, Any]


PluginFn = Callable[[str, Dict[str, Any]], PluginResult]


def partition_units(units: Sequence[str], shards: int) -> List[List[str]]:
    shards = max(1, shards)
    buckets: List[List[str]] = [[] for _ in range(shards)]
    for idx, u in enumerate(units):
        buckets[idx % shards].append(u)
    return buckets


def run_parallel(
    units: Sequence[str],
    plugin: PluginFn,
    plugin_args: Dict[str, Any] | None = None,
    max_workers: int = 4,
) -> List[PluginResult]:
    plugin_args = plugin_args or {}
    if not units:
        return []
    results: List[PluginResult] = []
    with cf.ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = [ex.submit(plugin, u, plugin_args) for u in units]
        for fut in cf.as_completed(futs):
            results.append(fut.result())
    # Deterministic order by unit_id
    results.sort(key=lambda r: r.unit_id)
    return results


def summarize(results: Sequence[PluginResult]) -> Dict[str, Any]:
    total = len(results)
    ok = sum(1 for r in results if r.ok)
    return {
        "total": total,
        "ok": ok,
        "failed": total - ok,
        "units": [r.unit_id for r in results],
    }


def example_plugin(unit_id: str, args: Dict[str, Any]) -> PluginResult:
    # Example no-op plugin used in docs/tests.
    label = args.get("label", "")
    return PluginResult(
        unit_id=unit_id,
        ok=True,
        summary=f"processed {unit_id} {label}".strip(),
        artifacts={"echo": unit_id},
    )


if __name__ == "__main__":
    # Simple demo usage
    units = [f"file-{i}.txt" for i in range(6)]
    res = run_parallel(units, example_plugin, {"label": "demo"}, max_workers=3)
    print(summarize(res))
```

## Tests

Create `tests/test_agent_coordinator.py`:

```python
# tests/test_agent_coordinator.py
from src.pipeline.agent_coordinator import partition_units, run_parallel, summarize, PluginResult


def dummy_plugin(uid, args):
    return PluginResult(unit_id=uid, ok=True, summary="ok", artifacts={})


def test_partition_stable():
    units = [f"u{i}" for i in range(7)]
    parts = partition_units(units, shards=3)
    assert parts[0] == ["u0", "u3", "u6"]
    assert parts[1] == ["u1", "u4"]
    assert parts[2] == ["u2", "u5"]


def test_run_parallel_and_summarize():
    units = ["b", "a", "c"]
    res = run_parallel(units, dummy_plugin, max_workers=2)
    # Results should be sorted by unit_id
    assert [r.unit_id for r in res] == ["a", "b", "c"]
    s = summarize(res)
    assert s["total"] == 3 and s["ok"] == 3 and s["failed"] == 0
```

Run tests:

```bash
pytest -q
```

## Integration points

- Upstream: consume unit identifiers from OpenSpec bundles (Phase 09).
- Downstream: feed `file-analyzer`, `test-runner`, and `code-analyzer` by
  invoking their plugin wrappers with `run_parallel`.
- Error pipeline: embed coordinator within dispatch loop (see
  `MOD_ERROR_PIPELINE/pipeline_engine.py`).

## Rollback plan

- Remove `src/pipeline/agent_coordinator.py` and associated tests.
- Revert any CI steps invoking the coordinator.

