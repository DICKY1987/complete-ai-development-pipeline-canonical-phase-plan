# DOC_LINK: DOC-ERROR-UNIT-TEST-ERROR-ENGINE-SHIM-150
# START <TestKey>
# TestType: Unit
# TargetModule: phase6_error_recovery/modules/error_engine/src/engine/error_engine.py
# TargetFunction: module import shim
# Purpose: Verify the compatibility shim correctly re-exports pipeline_engine symbols under the expected namespace
# OptimizationPattern: Fixture-Based
# CoverageGoalAchieved: 100% True
# END <TestKey>

from __future__ import annotations

import importlib
import sys
import types

from phase6_error_recovery.modules.error_engine.src.shared.utils import (
    jsonl_manager,
)
from phase6_error_recovery.modules.error_engine.src.shared.utils import (
    time as time_utils,
)
from phase6_error_recovery.modules.error_engine.src.shared.utils import (
    types as types_mod,
)


def test_error_engine_shim_reexports(monkeypatch):
    # Alias the expected namespace before importing shimmed modules.
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

    import phase6_error_recovery.modules.error_engine.src.engine.pipeline_engine as pipeline_engine

    engine_mod.pipeline_engine = pipeline_engine
    monkeypatch.setitem(
        sys.modules,
        "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.engine.pipeline_engine",
        pipeline_engine,
    )

    import phase6_error_recovery.modules.error_engine.src.engine.error_engine as shim

    shim_reloaded = importlib.reload(shim)

    assert shim_reloaded.PipelineEngine is pipeline_engine.PipelineEngine
