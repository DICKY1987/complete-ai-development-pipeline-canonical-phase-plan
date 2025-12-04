# DOC_LINK: DOC-ERROR-UNIT-TEST-PLUGIN-MANAGER-CUSTOM-156
# START <TestKey>
# TestType: Unit
# TargetModule: phase6_error_recovery/modules/error_engine/src/engine/plugin_manager.py
# TargetFunction: PluginManager.discover|get_plugins_for_file|run_plugins
# Purpose: Ensure plugin discovery, dependency ordering, and execution error handling behave deterministically
# OptimizationPattern: Fixture-Based
# CoverageGoalAchieved: 100% True
# END <TestKey>

from __future__ import annotations

import importlib
import json
import sys
import types
from pathlib import Path

import pytest

from phase6_error_recovery.modules.error_engine.src.shared.utils import (
    types as engine_types,
)


def _alias_missing_namespace(monkeypatch):
    """Expose the error_engine types module under the expected namespace used in plugin_manager."""
    root_mod = types.ModuleType("UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK")
    error_mod = types.ModuleType("UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error")
    shared_mod = types.ModuleType(
        "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.shared"
    )
    utils_mod = types.ModuleType(
        "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.shared.utils"
    )

    root_mod.error = error_mod
    error_mod.shared = shared_mod
    shared_mod.utils = utils_mod
    utils_mod.types = engine_types

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
        "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.shared.utils.types",
        engine_types,
    )


@pytest.fixture
def plugin_manager_module(monkeypatch):
    _alias_missing_namespace(monkeypatch)
    import phase6_error_recovery.modules.error_engine.src.engine.plugin_manager as pm

    return importlib.reload(pm)


def _write_plugin(
    tmp_path: Path, name: str, *, manifest_extra=None, available: bool = True
):
    plugin_dir = tmp_path / name
    plugin_dir.mkdir()
    manifest = {
        "plugin_id": name,
        "name": name,
        "file_extensions": ["txt"],
        **(manifest_extra or {}),
    }
    (plugin_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    plugin_body = f"""
from phase6_error_recovery.modules.error_engine.src.shared.utils.types import PluginResult

class DemoPlugin:
    plugin_id = "placeholder"
    name = "placeholder"
    manifest = {{}}

    def check_tool_available(self):
        return {str(available)}

    def execute(self, file_path):
        return PluginResult(plugin_id=self.plugin_id, success=True, issues=[])


def register():
    return DemoPlugin()
"""
    (plugin_dir / "plugin.py").write_text(plugin_body.strip(), encoding="utf-8")
    return plugin_dir


def test_discover_registers_available_plugins(tmp_path, plugin_manager_module):
    _write_plugin(tmp_path, "alpha")
    _write_plugin(tmp_path, "beta", available=False)
    manager = plugin_manager_module.PluginManager(plugins_path=tmp_path)

    manager.discover()

    assert set(manager._plugins.keys()) == {"alpha"}
    alpha = manager._plugins["alpha"]
    # Manifest values should override placeholder defaults from plugin implementation.
    assert alpha.plugin_id == "alpha"
    assert alpha.name == "alpha"
    assert alpha.manifest["file_extensions"] == ["txt"]


def test_get_plugins_for_file_orders_dependencies(tmp_path, plugin_manager_module):
    _write_plugin(tmp_path, "base")
    _write_plugin(tmp_path, "dependent", manifest_extra={"requires": ["base"]})
    manager = plugin_manager_module.PluginManager(plugins_path=tmp_path)
    manager.discover()

    ordered = manager.get_plugins_for_file(Path("sample.txt"))
    assert [p.plugin_id for p in ordered] == ["base", "dependent"]


def test_get_plugins_for_file_cycles_fallbacks_to_sorted(
    tmp_path, plugin_manager_module
):
    _write_plugin(tmp_path, "plugin_x", manifest_extra={"requires": ["plugin_y"]})
    _write_plugin(tmp_path, "plugin_y", manifest_extra={"requires": ["plugin_x"]})
    manager = plugin_manager_module.PluginManager(plugins_path=tmp_path)
    manager.discover()

    ordered = manager.get_plugins_for_file(Path("anything.txt"))
    # Cycle triggers fallback alphabetical ordering.
    assert [p.plugin_id for p in ordered] == ["plugin_x", "plugin_y"]


def test_run_plugins_wraps_exceptions(plugin_manager_module):
    manager = plugin_manager_module.PluginManager()

    class HappyPlugin:
        plugin_id = "ok"

        def execute(self, file_path):
            return plugin_manager_module.PluginResult(
                plugin_id=self.plugin_id, success=True, issues=[]
            )

    class FailingPlugin:
        plugin_id = "boom"

        def execute(self, file_path):
            raise RuntimeError("explode")

    results = manager.run_plugins([HappyPlugin(), FailingPlugin()], Path("file.txt"))

    assert len(results) == 2
    assert results[0].plugin_id == "ok" and results[0].success is True
    assert results[1].plugin_id == "boom" and results[1].success is False
    assert results[1].returncode == 1
