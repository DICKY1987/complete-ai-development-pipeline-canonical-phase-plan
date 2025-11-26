"""Module: error-engine

ULID Prefix: 010004
Layer: domain
Files: 9

This module dynamically imports ULID-prefixed files and re-exports their symbols.
Import from this module:
    
    from modules.error_engine import function_name  # ✅
"""

import importlib
import sys
from pathlib import Path

# Module metadata
__module_id__ = "error-engine"
__ulid_prefix__ = "010004"
__layer__ = "domain"

# Dynamically import all ULID-prefixed files and re-export
_module_dir = Path(__file__).parent
_ulid_files = [
    "010004_agent_adapters",
    "010004_error_context",
    "010004_error_engine",
    "010004_error_pipeline_cli",
    "010004_error_pipeline_service",
    "010004_error_state_machine",
    "010004_file_hash_cache",
    "010004_pipeline_engine",
    "010004_plugin_manager",
]

for _file_stem in _ulid_files:
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
    except Exception as e:
        print(f"Warning: Could not import {_module_path}: {e}", file=sys.stderr)
