from __future__ import annotations

import concurrent.futures as cf
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Sequence


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
    units = [f"file-{i}.txt" for i in range(6)]
    res = run_parallel(units, example_plugin, {"label": "demo"}, max_workers=3)
    print(summarize(res))

