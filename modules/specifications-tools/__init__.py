"""Module: specifications-tools

ULID Prefix: 010020
Layer: domain
Files: 5

This module dynamically imports ULID-prefixed files and re-exports their symbols.
Import from this module:
    
    from modules.specifications_tools import function_name  # ✅
"""

import importlib
import sys
from pathlib import Path

# Module metadata
__module_id__ = "specifications-tools"
__ulid_prefix__ = "010020"
__layer__ = "domain"

# Dynamically import all ULID-prefixed files and re-export
_module_dir = Path(__file__).parent
_ulid_files = [
    "010020_guard",
    "010020_indexer",
    "010020_patcher",
    "010020_renderer",
    "010020_resolver",
]

for _file_stem in _ulid_files:
    _module_path = f"modules.specifications_tools.{_file_stem}"
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
