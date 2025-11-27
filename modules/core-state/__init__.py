"""Module: core-state

ULID Prefix: 010003
Layer: infra
Files: 12

This module dynamically imports ULID-prefixed files and re-exports their symbols.
Import from this module:

    from modules.core_state import function_name  # ?
"""

import importlib
import sys
from pathlib import Path

# Module metadata
__module_id__ = "core-state"
__ulid_prefix__ = "010003"
__layer__ = "infra"
module_import_name = "core_state"

# Dynamically import all ULID-prefixed files and re-export
_module_dir = Path(__file__).parent
_ulid_files = [
"m010003_db",
"m010003_db_sqlite",
"m010003_db_unified",
"m010003_crud",
"m010003_audit_logger",
"m010003_bundles",
"m010003_dag_utils",
"m010003_pattern_telemetry_db",
"m010003_task_queue",
"m010003_uet_db",
"m010003_uet_db_adapter",
"m010003_worktree",
]

_pending = list(_ulid_files)
_errors = {stem: None for stem in _pending}

while _pending:
    _progress = False
    for _file_stem in list(_pending):
        _module_path = f"modules.core_state.{_file_stem}"
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
                sys.modules[f"modules.core_state.{_alias}"] = _mod
                globals()[_alias] = _mod
            _pending.remove(_file_stem)
            _progress = True
        except Exception as e:
            _errors[_file_stem] = e
            continue
    if not _progress:
        for _file_stem in _pending:
            _module_path = f"modules.core_state.{_file_stem}"
            _err = _errors.get(_file_stem)
            print(f"Warning: Could not import {_module_path}: {_err}", file=sys.stderr)
        break
