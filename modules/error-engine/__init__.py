"""Module: error-engine

ULID Prefix: 010004
Layer: domain
Files: 9

This module dynamically imports ULID-prefixed files and re-exports their symbols.
Import from this module:

    from modules.error_engine import function_name  # ?
"""

import importlib
import sys
from pathlib import Path

# Module metadata
__module_id__ = "error-engine"
__ulid_prefix__ = "010004"
__layer__ = "domain"
module_import_name = "error_engine"

# Dynamically import all ULID-prefixed files and re-export
_module_dir = Path(__file__).parent
_ulid_files = [
    "m010004_agent_adapters",
    "m010004_error_context",
    "m010004_error_state_machine",
    "m010004_error_pipeline_service",
    "m010004_error_engine",
    "m010004_file_hash_cache",
    "m010004_pipeline_engine",
    "m010004_plugin_manager",
    "m010004_test_helpers",
]

_pending = list(_ulid_files)
_errors = {stem: None for stem in _pending}

while _pending:
    _progress = False
    for _file_stem in list(_pending):
        _module_path = f"modules.error_engine.{_file_stem}"
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
                sys.modules[f"modules.error_engine.{_alias}"] = _mod
                globals()[_alias] = _mod
            _pending.remove(_file_stem)
            _progress = True
        except Exception as e:
            _errors[_file_stem] = e
            continue
    if not _progress:
        for _file_stem in _pending:
            _module_path = f"modules.error_engine.{_file_stem}"
            _err = _errors.get(_file_stem)
            print(f"Warning: Could not import {_module_path}: {_err}", file=sys.stderr)
        break
