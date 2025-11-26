"""Module: core-state

ULID Prefix: 010003
Layer: infra
Files: 12

This module dynamically imports ULID-prefixed files and re-exports their symbols.
Import from this module:
    
    from modules.core_state import function_name  # ✅
"""

import importlib
import sys
from pathlib import Path

# Module metadata
__module_id__ = "core-state"
__ulid_prefix__ = "010003"
__layer__ = "infra"

# Dynamically import all ULID-prefixed files and re-export
_module_dir = Path(__file__).parent
_ulid_files = [
    "010003_audit_logger",
    "010003_bundles",
    "010003_crud",
    "010003_dag_utils",
    "010003_db",
    "010003_db_sqlite",
    "010003_db_unified",
    "010003_pattern_telemetry_db",
    "010003_task_queue",
    "010003_uet_db",
    "010003_uet_db_adapter",
    "010003_worktree",
]

for _file_stem in _ulid_files:
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
    except Exception as e:
        print(f"Warning: Could not import {_module_path}: {e}", file=sys.stderr)
