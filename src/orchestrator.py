from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence


@dataclass(frozen=True)
class RunResult:
    ws_id: str
    final_status: str = "done"


class ParallelRunner:
    def run_many(
        self,
        ws_ids: Sequence[str],
        *,
        max_workers: int,
        context: Optional[Dict[str, Any]] = None,
        on_start: Optional[Callable[[str], None]] = None,
        on_end: Optional[Callable[[str], None]] = None,
    ) -> List[RunResult]:
        for ws_id in ws_ids:
            if on_start:
                on_start(ws_id)
            if on_end:
                on_end(ws_id)
        return [RunResult(ws_id=ws_id, final_status="done") for ws_id in ws_ids]


parallel = ParallelRunner()
