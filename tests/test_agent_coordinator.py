# DOC_LINK: DOC-TEST-TESTS-TEST-AGENT-COORDINATOR-074
# DOC_LINK: DOC-TEST-TESTS-TEST-AGENT-COORDINATOR-035
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.agent_coordinator import partition_units, run_parallel, summarize, PluginResult


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
