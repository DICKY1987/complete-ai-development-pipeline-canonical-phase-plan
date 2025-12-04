# DOC_LINK: DOC-TEST-PIPELINE-TEST-BUNDLES-135
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Ensure repository root is on sys.path so `src` package is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest
from modules.core_state import m010003_bundles as ws


def write_bundle(path: Path, data):
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def with_ws_dir(tmp_path: Path):
    os.environ["PIPELINE_WORKSTREAM_DIR"] = str(tmp_path)


def test_valid_bundles_no_cycles_no_overlaps(tmp_path: Path, monkeypatch):
    with_ws_dir(tmp_path)
    # Two independent bundles
    write_bundle(
        tmp_path / "a.json",
        {
            "id": "ws-a",
            "openspec_change": "OS-A",
            "ccpm_issue": 1,
            "gate": 1,
            "files_scope": ["src/a.py"],
            "tasks": ["A"],
            "tool": "aider",
        },
    )
    write_bundle(
        tmp_path / "b.json",
        {
            "id": "ws-b",
            "openspec_change": "OS-B",
            "ccpm_issue": 2,
            "gate": 1,
            "files_scope": ["src/b.py"],
            "tasks": ["B"],
            "tool": "aider",
            "depends_on": ["ws-a"],
        },
    )

    bundles = ws.load_and_validate_bundles()
    graph, parents = ws.build_dependency_graph(bundles)
    assert set(graph.keys()) == {"ws-a", "ws-b"}
    assert graph["ws-a"] == ["ws-b"]
    assert graph["ws-b"] == []
    assert ws.detect_cycles(graph) == []
    assert ws.detect_filescope_overlaps(bundles) == {}


def test_duplicate_id_raises(tmp_path: Path):
    with_ws_dir(tmp_path)
    write_bundle(
        tmp_path / "x1.json",
        {
            "id": "ws-x",
            "openspec_change": "OS-X",
            "ccpm_issue": 1,
            "gate": 1,
            "files_scope": ["src/x.py"],
            "tasks": ["X"],
            "tool": "aider",
        },
    )
    write_bundle(
        tmp_path / "x2.json",
        {
            "id": "ws-x",
            "openspec_change": "OS-X2",
            "ccpm_issue": 2,
            "gate": 1,
            "files_scope": ["src/x2.py"],
            "tasks": ["X2"],
            "tool": "aider",
        },
    )
    with pytest.raises(ws.BundleValidationError) as ei:
        ws.load_and_validate_bundles()
    assert "Duplicate bundle id" in str(ei.value)


def test_missing_dependency_raises(tmp_path: Path):
    with_ws_dir(tmp_path)
    write_bundle(
        tmp_path / "a.json",
        {
            "id": "ws-a",
            "openspec_change": "OS-A",
            "ccpm_issue": 1,
            "gate": 1,
            "files_scope": ["src/a.py"],
            "tasks": ["A"],
            "tool": "aider",
            "depends_on": ["ws-missing"],
        },
    )
    with pytest.raises(ws.BundleDependencyError) as ei:
        ws.load_and_validate_bundles()
    assert "Missing dependency references" in str(ei.value)


def test_simple_cycle_raises(tmp_path: Path):
    with_ws_dir(tmp_path)
    write_bundle(
        tmp_path / "a.json",
        {
            "id": "ws-a",
            "openspec_change": "OS-A",
            "ccpm_issue": 1,
            "gate": 1,
            "files_scope": ["src/a.py"],
            "tasks": ["A"],
            "tool": "aider",
            "depends_on": ["ws-b"],
        },
    )
    write_bundle(
        tmp_path / "b.json",
        {
            "id": "ws-b",
            "openspec_change": "OS-B",
            "ccpm_issue": 2,
            "gate": 1,
            "files_scope": ["src/b.py"],
            "tasks": ["B"],
            "tool": "aider",
            "depends_on": ["ws-a"],
        },
    )
    with pytest.raises(ws.BundleCycleError) as ei:
        ws.load_and_validate_bundles()
    assert "cycle" in str(ei.value).lower()


def test_filescope_overlap_raises_from_cli(tmp_path: Path):
    # Create two bundles claiming same file
    with_ws_dir(tmp_path)
    write_bundle(
        tmp_path / "a.json",
        {
            "id": "ws-a",
            "openspec_change": "OS-A",
            "ccpm_issue": 1,
            "gate": 1,
            "files_scope": ["src/shared.py"],
            "tasks": ["A"],
            "tool": "aider",
        },
    )
    write_bundle(
        tmp_path / "b.json",
        {
            "id": "ws-b",
            "openspec_change": "OS-B",
            "ccpm_issue": 2,
            "gate": 1,
            "files_scope": ["src/shared.py"],
            "tasks": ["B"],
            "tool": "aider",
        },
    )

    bundles = ws.load_and_validate_bundles()
    overlaps = ws.detect_filescope_overlaps(bundles)
    assert overlaps == {"src/shared.py": ["ws-a", "ws-b"]}


def test_schema_validation_errors(tmp_path: Path):
    with_ws_dir(tmp_path)
    # Missing required fields
    write_bundle(tmp_path / "bad_missing.json", {"id": "ws-x"})
    with pytest.raises(ws.BundleValidationError):
        ws.load_and_validate_bundles()

    # Wrong type
    (tmp_path / "bad_missing.json").unlink()
    write_bundle(
        tmp_path / "bad_type.json",
        {
            "id": "ws-y",
            "openspec_change": "OS-Y",
            "ccpm_issue": 1,
            "gate": 1,
            "files_scope": ["f"],
            "tasks": "should-be-array",
            "tool": "aider",
        },
    )
    with pytest.raises(ws.BundleValidationError):
        ws.load_and_validate_bundles()
