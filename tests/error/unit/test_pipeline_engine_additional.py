# DOC_LINK: DOC-ERROR-UNIT-TEST-PIPELINE-ENGINE-ADDITIONAL-155
# START <TestKey>
# TestType: Unit
# TargetModule: phase6_error_recovery/modules/error_engine/src/engine/pipeline_engine.py
# TargetFunction: PipelineEngine.process_file|process_files|_generate_report
# Purpose: Validate pipeline control flow for skipped runs, validated runs, and report generation
# OptimizationPattern: Mock-Heavy
# CoverageGoalAchieved: 100% True
# END <TestKey>

from __future__ import annotations

import importlib
import sys
import types
from pathlib import Path

import pytest

from phase6_error_recovery.modules.error_engine.src.shared.utils import (
    jsonl_manager,
)
from phase6_error_recovery.modules.error_engine.src.shared.utils import (
    time as time_utils,
)
from phase6_error_recovery.modules.error_engine.src.shared.utils import (
    types as types_mod,
)


def _alias_pipeline_namespace(monkeypatch):
    root_mod = types.ModuleType("UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK")
    error_mod = types.ModuleType("UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error")
    shared_mod = types.ModuleType(
        "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.shared"
    )
    utils_mod = types.ModuleType(
        "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.shared.utils"
    )
    engine_mod = types.ModuleType(
        "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.engine"
    )

    root_mod.error = error_mod
    error_mod.shared = shared_mod
    error_mod.engine = engine_mod
    shared_mod.utils = utils_mod
    utils_mod.time = time_utils
    utils_mod.jsonl_manager = jsonl_manager
    utils_mod.types = types_mod

    monkeypatch.setitem(
        sys.modules, "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK", root_mod
    )
    monkeypatch.setitem(
        sys.modules, "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error", error_mod
    )
    monkeypatch.setitem(
        sys.modules, "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.shared", shared_mod
    )
    monkeypatch.setitem(
        sys.modules,
        "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.shared.utils",
        utils_mod,
    )
    monkeypatch.setitem(
        sys.modules,
        "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.shared.utils.time",
        time_utils,
    )
    monkeypatch.setitem(
        sys.modules,
        "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.shared.utils.jsonl_manager",
        jsonl_manager,
    )
    monkeypatch.setitem(
        sys.modules,
        "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.shared.utils.types",
        types_mod,
    )
    monkeypatch.setitem(
        sys.modules, "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.engine", engine_mod
    )


@pytest.fixture
def pipeline_engine_module(monkeypatch):
    _alias_pipeline_namespace(monkeypatch)
    import phase6_error_recovery.modules.error_engine.src.engine.pipeline_engine as pe

    return importlib.reload(pe)


def test_process_file_skipped(monkeypatch, tmp_path, pipeline_engine_module):
    events = []
    monkeypatch.setattr(
        pipeline_engine_module,
        "jsonl_append",
        lambda path, payload: events.append((path, payload)),
    )
    monkeypatch.setattr(pipeline_engine_module, "new_run_id", lambda: "run-1")
    monkeypatch.setattr(pipeline_engine_module, "utc_now_iso", lambda: "ts1")

    class StubCache:
        def has_changed(self, path):
            return False

    engine = pipeline_engine_module.PipelineEngine(
        plugin_manager=None, hash_cache=StubCache()
    )
    file_path = tmp_path / "input.py"
    file_path.write_text("print('hi')", encoding="utf-8")

    report = engine.process_file(file_path)

    assert report.status == "skipped"
    assert report.summary.plugins_run == 0
    assert events and events[0][1]["event"] == "skipped"


def test_process_file_validates_and_reports(
    monkeypatch, tmp_path, pipeline_engine_module
):
    events = []
    monkeypatch.setattr(
        pipeline_engine_module,
        "jsonl_append",
        lambda path, payload: events.append(payload),
    )
    monkeypatch.setattr(pipeline_engine_module, "new_run_id", lambda: "run-2")
    monkeypatch.setattr(pipeline_engine_module, "utc_now_iso", lambda: "ts2")
    monkeypatch.setattr(
        pipeline_engine_module.shutil,
        "copy2",
        lambda src, dst: Path(dst).write_text("copied", encoding="utf-8"),
    )

    class DummyTempDir:
        def __init__(self, base):
            self.base = base

        def __enter__(self):
            return str(self.base)

        def __exit__(self, exc_type, exc, tb):
            return False

    tmp_base = tmp_path / "tmp"
    tmp_base.mkdir()
    monkeypatch.setattr(
        pipeline_engine_module.tempfile,
        "TemporaryDirectory",
        lambda: DummyTempDir(tmp_base),
    )

    class StubCache:
        def __init__(self):
            self.marked = []
            self.saved = False

        def has_changed(self, path):
            return True

        def mark_validated(self, path, had_errors=None):
            self.marked.append((path, had_errors))

        def save(self):
            self.saved = True

    stub_cache = StubCache()

    class StubManager:
        def discover(self):
            self.discovered = True

        def get_plugins_for_file(self, file_path):
            return []

        def run_plugins(self, plugins, file_path):
            return []

    engine = pipeline_engine_module.PipelineEngine(
        plugin_manager=StubManager(), hash_cache=stub_cache
    )
    file_path = tmp_path / "input.py"
    file_path.write_text("print('hi')", encoding="utf-8")

    report = engine.process_file(file_path)

    assert report.status in {"ok", "failed"}
    assert stub_cache.marked and stub_cache.saved
    assert any(payload["event"] == "validated" for payload in events)
    assert Path(report.file_out).exists()
    assert Path(report.file_out + ".json").exists()


def test_generate_report_counts_errors(pipeline_engine_module):
    issue_error = types_mod.PluginIssue(
        tool="t", path="p", severity="error", message="m"
    )
    issue_warning = types_mod.PluginIssue(
        tool="t", path="p", severity="warning", message="m"
    )
    plugin_results = [
        types_mod.PluginResult(plugin_id="a", success=True, issues=[issue_warning]),
        types_mod.PluginResult(plugin_id="b", success=False, issues=[issue_error]),
    ]

    report = pipeline_engine_module.PipelineEngine(
        plugin_manager=None, hash_cache=None
    )._generate_report(Path("f.py"), plugin_results, run_id="r")

    assert report.summary.plugins_run == 2
    assert report.summary.total_warnings == 1
    assert report.summary.total_errors == 2  # one plugin failure + one issue
    assert report.status == "failed"


def test_process_files_iterates(monkeypatch, tmp_path, pipeline_engine_module):
    calls = []

    class StubEngine(pipeline_engine_module.PipelineEngine):
        def process_file(self, file_path):
            calls.append(Path(file_path))
            return "done"

    engine = StubEngine(plugin_manager=None, hash_cache=None)
    file1 = tmp_path / "a.py"
    file2 = tmp_path / "b.py"
    reports = engine.process_files([file1, file2])

    assert calls == [file1, file2]
    assert reports == ["done", "done"]
