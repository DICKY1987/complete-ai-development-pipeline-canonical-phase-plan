"""Module: aim-registry

ULID Prefix: 01001C
Layer: api
Files: 1

This module dynamically imports ULID-prefixed files and re-exports their symbols.
Import from this module:
    
    from modules.aim_registry import function_name  # ✅
"""

import importlib
import sys
from pathlib import Path

# Module metadata
__module_id__ = "aim-registry"
__ulid_prefix__ = "01001C"
__layer__ = "api"

# Dynamically import all ULID-prefixed files and re-export
_module_dir = Path(__file__).parent
_ulid_files = [
    "01001C_config_loader",
]

for _file_stem in _ulid_files:
    _module_path = f"modules.aim_registry.{_file_stem}"
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
