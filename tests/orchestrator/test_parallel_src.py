from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Dict, List

import pytest


def _make_bundle(ws_id: str, deps: List[str] | None = None):
    return SimpleNamespace(id=ws_id, depends_on=deps or [])


def test_run_many_respects_dependencies(monkeypatch):
    # Graph: A -> C, B -> C; A and B can run in parallel, C after both
    bundles = [_make_bundle("A"), _make_bundle("B"), _make_bundle("C", ["A", "B"])]

    called: List[str] = []

    def fake_load_and_validate_bundles():
        return bundles

    def fake_run_workstream(run_id: str, ws_id: str, b: Any, context=None) -> Dict[str, Any]:
        called.append(ws_id)
        return {"final_status": "ok", "ws_id": ws_id, "run_id": run_id}

    import src.orchestrator.parallel as par
    monkeypatch.setattr(par._bundles, "load_and_validate_bundles", fake_load_and_validate_bundles)
    monkeypatch.setattr(par._single, "run_workstream", fake_run_workstream)

    res = par.run_many(["A", "B", "C"], max_workers=2)
    # All three ran
    assert sorted(r.ws_id for r in res) == ["A", "B", "C"]
    # C must be called after A and B
    assert called.index("C") > called.index("A")
    assert called.index("C") > called.index("B")


def test_run_many_missing_workstream(monkeypatch):
    bundles = [_make_bundle("A")]
    import src.orchestrator.parallel as par
    monkeypatch.setattr(par._bundles, "load_and_validate_bundles", lambda: bundles)

    with pytest.raises(ValueError):
        par.run_many(["A", "X"])  # X not found


def test_run_many_cycle_detection(monkeypatch):
    # Provided set has a cycle A<->B
    bundles = [_make_bundle("A", ["B"]), _make_bundle("B", ["A"])]
    import src.orchestrator.parallel as par
    monkeypatch.setattr(par._bundles, "load_and_validate_bundles", lambda: bundles)
    # run_workstream should never be called; still mock to be safe
    monkeypatch.setattr(par._single, "run_workstream", lambda *a, **k: {})

    with pytest.raises(ValueError):
        par.run_many(["A", "B"])  # cycle among target set
