"""Module: core-engine

ULID Prefix: 010001
Layer: domain
Files: 31

This module dynamically imports ULID-prefixed files and re-exports their symbols.
Import from this module:
    
    from modules.core_engine import function_name  # ✅
"""

import importlib
import sys
from pathlib import Path

# Module metadata
__module_id__ = "core-engine"
__ulid_prefix__ = "010001"
__layer__ = "domain"

# Dynamically import all ULID-prefixed files and re-export
_module_dir = Path(__file__).parent
_ulid_files = [
    "010001_aim_integration",
    "010001_circuit_breakers",
    "010001_compensation",
    "010001_context_estimator",
    "010001_cost_tracker",
    "010001_dag_builder",
    "010001_event_bus",
    "010001_executor",
    "010001_hardening",
    "010001_integration_worker",
    "010001_metrics",
    "010001_orchestrator",
    "010001_patch_applier",
    "010001_patch_converter",
    "010001_performance",
    "010001_pipeline_plus_orchestrator",
    "010001_plan_validator",
    "010001_process_spawner",
    "010001_prompt_engine",
    "010001_recovery",
    "010001_recovery_manager",
    "010001_scheduler",
    "010001_test_gates",
    "010001_tools",
    "010001_uet_orchestrator",
    "010001_uet_patch_ledger",
    "010001_uet_router",
    "010001_uet_scheduler",
    "010001_uet_state_machine",
    "010001_validators",
    "010001_worker",
]

for _file_stem in _ulid_files:
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
    except Exception as e:
        print(f"Warning: Could not import {_module_path}: {e}", file=sys.stderr)
