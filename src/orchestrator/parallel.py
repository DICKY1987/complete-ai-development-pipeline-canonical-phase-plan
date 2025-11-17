"""
Parallel workstream orchestration (scaffold).

Provides a minimal interface to run multiple workstreams concurrently with a
bounded level of parallelism. Actual step execution delegates to the existing
single-workstream orchestrator.

This module focuses on structure and safe defaults; it can be expanded with
queueing, dependency handling, and richer telemetry.
"""

from __future__ import annotations

import concurrent.futures as _fut
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Callable, Set

from src.pipeline import orchestrator as _single
from src.pipeline import bundles as _bundles


@dataclass
class ParallelResult:
    ws_id: str
    run_id: str
    final_status: str
    result: Dict[str, Any]


def run_many(
    ws_ids: Iterable[str],
    *,
    max_workers: int = 2,
    context: Optional[Mapping[str, Any]] = None,
    on_start: Optional[Callable[[str], None]] = None,
    on_end: Optional[Callable[[str], None]] = None,
) -> List[ParallelResult]:
    """Run multiple workstreams concurrently with dependency awareness.

    - Resolves bundles once
    - Honors dependencies among the provided `ws_ids` (dependencies not in the
      set are treated as already satisfied)
    - Submits work up to `max_workers` in parallel
    - Returns results in the order tasks complete
    """
    items = _bundles.load_and_validate_bundles()
    by_id = {b.id: b for b in items}
    target: Set[str] = set(ws_ids)

    # Build graph restricted to the target set
    indeg: Dict[str, int] = {w: 0 for w in target}
    adj: Dict[str, List[str]] = {w: [] for w in target}
    for w in list(target):
        b = by_id.get(w)
        if not b:
            raise ValueError(f"Workstream '{w}' not found")
        for dep in getattr(b, "depends_on", ()) or ():
            if dep in target:
                indeg[w] += 1
                adj.setdefault(dep, []).append(w)

    results: List[ParallelResult] = []

    def _run(ws_id: str) -> ParallelResult:
        b = by_id.get(ws_id)
        if not b:
            raise ValueError(f"Workstream '{ws_id}' not found")
        run_id = f"run-{ws_id}"
        if on_start:
            try:
                on_start(ws_id)
            except Exception:
                pass
        r = _single.run_workstream(run_id, ws_id, b, context=context)
        if on_end:
            try:
                on_end(ws_id)
            except Exception:
                pass
        return ParallelResult(ws_id=ws_id, run_id=run_id, final_status=str(r.get("final_status")), result=r)

    # Kahn-like scheduling with bounded parallelism
    ready: List[str] = sorted([w for w, d in indeg.items() if d == 0])
    submitted: Set[str] = set()
    in_flight: Dict["_fut.Future[ParallelResult]", str] = {}

    with _fut.ThreadPoolExecutor(max_workers=max_workers) as ex:
        while ready or in_flight:
            # submit until capacity
            while ready and len(in_flight) < max_workers:
                ws_id = ready.pop(0)
                submitted.add(ws_id)
                in_flight[ex.submit(_run, ws_id)] = ws_id

            if not in_flight:
                break

            # wait for any to complete
            done, _ = _fut.wait(in_flight.keys(), return_when=_fut.FIRST_COMPLETED)
            for f in done:
                ws_id = in_flight.pop(f)
                res = f.result()
                results.append(res)
                # reduce indegree for dependents
                for nxt in adj.get(ws_id, []):
                    indeg[nxt] -= 1
                    if indeg[nxt] == 0:
                        ready.append(nxt)
                ready.sort()

    # Detect unresolved nodes (cycle among provided set)
    if len(submitted) != len(target):
        missing = sorted(target - submitted)
        raise ValueError(f"Dependency cycle or unresolved deps among: {', '.join(missing)}")

    return results
