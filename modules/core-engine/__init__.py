"""Module: core-engine

ULID Prefix: 010001
Layer: domain
Files: 31

This module dynamically imports ULID-prefixed files and re-exports their symbols.
Import from this module:

    from modules.core_engine import function_name  # ?
"""

import importlib
import sys
from pathlib import Path

# Module metadata
__module_id__ = "core-engine"
__ulid_prefix__ = "010001"
__layer__ = "domain"
module_import_name = "core_engine"

# Dynamically import all ULID-prefixed files and re-export
_module_dir = Path(__file__).parent
_ulid_files = [
"m010001_aim_integration",
"m010001_circuit_breakers",
"m010001_compensation",
"m010001_context_estimator",
"m010001_cost_tracker",
"m010001_dag_builder",
"m010001_event_bus",
"m010001_executor",
"m010001_hardening",
"m010001_integration_worker",
"m010001_metrics",
"m010001_orchestrator",
"m010001_patch_applier",
"m010001_patch_converter",
"m010001_performance",
"m010001_pipeline_plus_orchestrator",
"m010001_plan_validator",
"m010001_process_spawner",
"m010001_prompt_engine",
"m010001_recovery",
"m010001_recovery_manager",
"m010001_scheduler",
"m010001_test_gates",
"m010001_tools",
"m010001_uet_orchestrator",
"m010001_uet_patch_ledger",
"m010001_uet_router",
"m010001_uet_scheduler",
"m010001_uet_state_machine",
"m010001_validators",
"m010001_worker",
]

_pending = list(_ulid_files)
_errors = {stem: None for stem in _pending}

while _pending:
    _progress = False
    for _file_stem in list(_pending):
        _module_path = f"modules.core_engine.{_file_stem}"
        try:
            _mod = importlib.import_module(_module_path)

            # Re-export all public symbols
            if hasattr(_mod, '__all__'):
                for _name in _mod.__all__:
                    globals()[_name] = getattr(_mod, _name)
            else:
                # Export everything that doesn't start with underscore
                for _name in dir(_mod):
                    if not _name.startswith('_'):
                        globals()[_name] = getattr(_mod, _name)
            # Alias without ULID prefix to support relative imports (e.g., db_sqlite)
            if "_" in _file_stem:
                _alias = _file_stem.split("_", 1)[1]
                sys.modules[f"modules.core_engine.{_alias}"] = _mod
                globals()[_alias] = _mod
            _pending.remove(_file_stem)
            _progress = True
        except Exception as e:
            _errors[_file_stem] = e
            continue
    if not _progress:
        for _file_stem in _pending:
            _module_path = f"modules.core_engine.{_file_stem}"
            _err = _errors.get(_file_stem)
            print(f"Warning: Could not import {_module_path}: {_err}", file=sys.stderr)
        break
