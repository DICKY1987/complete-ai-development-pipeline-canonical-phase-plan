"""Lightweight parallel orchestrator used by migration tests."""
from __future__ import annotations

from typing import Dict, List, Set


class ParallelOrchestrator:
    """Execute simple dependency graphs in waves."""
DOC_ID: DOC-PAT-CORE-ENGINE-PARALLEL-ORCHESTRATOR-520

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers

    def _wave_ready(self, workstreams: List[Dict], completed: Set[str]) -> List[str]:
        ready = []
        for ws in workstreams:
            ws_id = ws.get("workstream_id")
            deps = ws.get("dependencies", []) or []
            if ws_id is None:
                continue
            if all(dep in completed for dep in deps):
                ready.append(ws_id)
        return ready

    def execute_phase(self, workstreams: List[Dict]) -> Dict[str, int]:
        """Return a summary without executing external work."""
        remaining = {ws.get("workstream_id") for ws in workstreams if ws.get("workstream_id")}
        completed: Set[str] = set()
        waves = 0

        while remaining:
            current_wave = [ws_id for ws_id in self._wave_ready(workstreams, completed) if ws_id in remaining]
            if not current_wave:
                break

            waves += 1
            for ws_id in current_wave:
                if ws_id in remaining:
                    completed.add(ws_id)
                    remaining.remove(ws_id)

        failed = len(remaining)
        successful = len(completed)
        return {
            "total_workstreams": len(workstreams),
            "successful": successful,
            "failed": failed,
            "waves_executed": waves,
        }

    def shutdown(self) -> None:
        """No-op placeholder for compatibility with legacy orchestrators."""
        return None


__all__ = ["ParallelOrchestrator"]
