# DOC_LINK: DOC-TEST-TESTS-TEST-PARALLEL-ORCHESTRATOR-095
# DOC_LINK: DOC-TEST-TESTS-TEST-PARALLEL-ORCHESTRATOR-056
from __future__ import annotations

from src.orchestrator import parallel


def test_run_many_dry_run():
    # Use two sample workstreams from workstreams/example_multi.json
    ws_ids = ["ws-core-lib", "ws-cli"]
    res = parallel.run_many(
        ws_ids, max_workers=2, context={"dry_run": True, "static_tools": []}
    )
    got = {r.ws_id: r.final_status for r in res}
    for ws in ws_ids:
        assert got.get(ws) == "done"
