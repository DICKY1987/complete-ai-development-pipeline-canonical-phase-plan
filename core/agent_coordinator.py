from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Sequence


@dataclass
class PluginResult:
    unit_id: str
    ok: bool
    summary: str
    artifacts: Dict[str, Any]


def partition_units(units: Sequence[str], shards: int) -> List[List[str]]:
    if shards <= 0:
        raise ValueError("shards must be positive")
    return [list(units[i::shards]) for i in range(shards)]


def run_parallel(
    units: Sequence[str],
    plugin: Callable[[str, Dict[str, Any]], PluginResult],
    *,
    max_workers: int = 1,
    args: Dict[str, Any] | None = None,
) -> List[PluginResult]:
    args = args or {}
    results = [plugin(unit, args) for unit in units]
    return sorted(results, key=lambda r: r.unit_id)


def summarize(results: Iterable[PluginResult]) -> Dict[str, int]:
    results_list = list(results)
    total = len(results_list)
    ok = sum(1 for r in results_list if r.ok)
    failed = total - ok
    return {"total": total, "ok": ok, "failed": failed}
