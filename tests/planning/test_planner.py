# DOC_LINK: DOC-TEST-PLANNING-TEST-PLANNER-311
import json
import pytest

from core.planning.planner import plan_workstreams_from_spec


def test_plan_from_mapping_applies_defaults():
    spec = {
        "workstreams": [
            {"id": "ws-b", "files_scope": ["core/foo.py"], "tasks": ["refine"]},
            {"id": "ws-a", "files_scope": ["core/bar.py"], "tasks": ["add tests"]},
        ]
    }
    result = plan_workstreams_from_spec(spec, {"default_gate": 2, "default_tool": "aider"})

    assert [ws["id"] for ws in result] == ["ws-a", "ws-b"]  # sorted by id
    assert all(ws["gate"] == 2 for ws in result)
    assert all(ws["tool"] == "aider" for ws in result)


def test_plan_from_path_reads_json(tmp_path):
    data = {
        "items": [
            {"id": "ws-1", "files_scope": ["a/b.py"], "tasks": ["task 1"], "gate": 3}
        ]
    }
    spec_file = tmp_path / "spec.json"
    spec_file.write_text(json.dumps(data), encoding="utf-8")

    result = plan_workstreams_from_spec(spec_file)

    assert result == [
        {"id": "ws-1", "files_scope": ["a/b.py"], "tasks": ["task 1"], "gate": 3}
    ]


def test_missing_required_fields_raise():
    spec = {"workstreams": [{"id": "ws-missing-files", "tasks": ["noop"]}]}

    with pytest.raises(ValueError):
        plan_workstreams_from_spec(spec)
