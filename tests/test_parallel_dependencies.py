# DOC_LINK: DOC-TEST-TESTS-TEST-PARALLEL-DEPENDENCIES-094
# DOC_LINK: DOC-TEST-TESTS-TEST-PARALLEL-DEPENDENCIES-055
from __future__ import annotations

from src.orchestrator import parallel


def test_dependency_ordering_within_target_set():
    # Use three workstreams with dependencies (see workstreams/example_multi.json)
    order = []

    def on_start(ws_id: str):
        order.append(("start", ws_id))

    def on_end(ws_id: str):
        order.append(("end", ws_id))

    res = parallel.run_many(
        ["ws-core-lib", "ws-api-layer", "ws-cli"],
        max_workers=3,
        context={"dry_run": True, "static_tools": []},
        on_start=on_start,
        on_end=on_end,
    )
    # Build first-start index map
    first_start = {}
    for kind, ws in order:
        if kind == "start" and ws not in first_start:
            first_start[ws] = len(first_start)

    assert first_start["ws-core-lib"] < first_start["ws-api-layer"] < first_start["ws-cli"]
    # All should complete successfully
    status = {r.ws_id: r.final_status for r in res}
    assert status["ws-core-lib"] == status["ws-api-layer"] == status["ws-cli"] == "done"

