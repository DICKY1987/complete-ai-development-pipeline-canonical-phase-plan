"""Module: error-shared

ULID Prefix: 010021
Layer: domain
Status: Shared utilities for error detection pipeline
"""
# DOC_ID: DOC-PAT-ERROR-SHARED-INIT-600

import importlib
import sys
from pathlib import Path

__module_id__ = "error-shared"
__ulid_prefix__ = "010021"
__layer__ = "domain"

# Find all ULID-prefixed files
_module_dir = Path(__file__).parent
_ulid_files = [f.stem for f in _module_dir.glob("m010021_*.py")]

# Dynamic import with dependency resolution
_pending = list(_ulid_files)
_errors = {}

while _pending:
    _progress = False
    for _file_stem in list(_pending):
        try:
            _module_path = f"modules.error_shared.{_file_stem}"
            _mod = importlib.import_module(_module_path)
            
            # Re-export all public symbols
            if hasattr(_mod, '__all__'):
                for _name in _mod.__all__:
                    globals()[_name] = getattr(_mod, _name)
            else:
                for _name in dir(_mod):
                    if not _name.startswith('_'):
                        globals()[_name] = getattr(_mod, _name)
            
            _pending.remove(_file_stem)
            _progress = True
        except ImportError as e:
            _errors[_file_stem] = str(e)
    
    if not _progress:
        break

# Import submodules for backward compatibility
try:
    from . import m010021_types
    from . import m010021_time
    from . import m010021_hashing
    from . import m010021_jsonl_manager
    from . import m010021_env
    from . import m010021_security
except ImportError as e:
    pass

# Create utils submodule for backward compatibility
class UtilsModule:
    """Compatibility shim for error.shared.utils imports"""
    def __init__(self):
        self.types = m010021_types
        self.time = m010021_time
        self.hashing = m010021_hashing
        self.jsonl_manager = m010021_jsonl_manager
        self.env = m010021_env
        self.security = m010021_security

utils = UtilsModule()

# Re-export all public symbols at module level
for _name in dir(m010021_types):
    if not _name.startswith('_'):
        globals()[_name] = getattr(m010021_types, _name)

# Legacy imports for backward compatibility
sys.modules['error.shared'] = sys.modules[__name__]
sys.modules['error.shared.utils'] = utils
sys.modules['error.shared.utils.types'] = m010021_types
sys.modules['error.shared.utils.time'] = m010021_time
sys.modules['error.shared.utils.hashing'] = m010021_hashing
sys.modules['error.shared.utils.jsonl_manager'] = m010021_jsonl_manager
sys.modules['error.shared.utils.env'] = m010021_env
sys.modules['error.shared.utils.security'] = m010021_security

__all__ = ['utils']
