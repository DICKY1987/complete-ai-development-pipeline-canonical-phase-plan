# DOC_LINK: DOC-CORE-CORE-ERROR-PIPELINE-SERVICE-040
# DOC_LINK: DOC-CORE-CORE-ERROR-PIPELINE-SERVICE-017
from __future__ import annotations

from typing import Any, Dict, Iterable, List

S_SUCCESS = "S_SUCCESS"
S_FAILED = "S_FAILED"


def run_pipeline(units: Iterable[str], *, max_workers: int = 2) -> Dict[str, Any]:
    units_list = list(units)
    failed_units = [unit for unit in units_list if "fail" in unit.lower()]
    state = S_FAILED if failed_units else S_SUCCESS
    return {
        "state": state,
        "units": units_list,
        "failed_units": failed_units,
        "S2": {
            "failed": len(failed_units),
            "total": len(units_list),
        },
        "max_workers": max_workers,
    }


__all__ = ["run_pipeline", "S_SUCCESS", "S_FAILED"]
