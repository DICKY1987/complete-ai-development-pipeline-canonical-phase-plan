"""Pytest configuration for Phase 6 plugin tests."""

import sys
from pathlib import Path

# Add the shared utilities to Python path
shared_utils_path = Path(__file__).parent.parent / "error_engine" / "src"
if str(shared_utils_path) not in sys.path:
    sys.path.insert(0, str(shared_utils_path))

# Create a mock UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK module for imports
import types

# Create the nested module structure
uet = types.ModuleType("UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK")
uet_error = types.ModuleType("error")
uet_shared = types.ModuleType("shared")
uet_utils = types.ModuleType("utils")

# Import the actual modules from shared
from shared.utils import env
from shared.utils import types as shared_types

# Assign them to the mock structure
uet_utils.env = env
uet_utils.types = shared_types
uet_shared.utils = uet_utils
uet_error.shared = uet_shared
uet.error = uet_error

# Register the mock modules
sys.modules["UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK"] = uet
sys.modules["UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error"] = uet_error
sys.modules["UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.shared"] = uet_shared
sys.modules["UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.shared.utils"] = uet_utils
sys.modules["UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.shared.utils.env"] = env
sys.modules["UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.shared.utils.types"] = (
    shared_types
)
