"""
Test that imports work correctly with the new module structure.
"""

# DOC_ID: DOC-SCRIPT-SCRIPTS-TEST-IMPORTS-236
# DOC_ID: DOC-SCRIPT-SCRIPTS-TEST-IMPORTS-173

import sys
from pathlib import Path

print("Testing module imports...")

# Ensure repo root is on sys.path for package discovery
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Test core modules
from modules.core_state import get_connection

print("? from modules.core_state import get_connection")

from modules.core_engine import Orchestrator

print("? from modules.core_engine import Orchestrator")

from modules.core_planning import ParallelismProfile

print("? from modules.core_planning import ParallelismProfile")

# Test error modules
from modules.error_engine import ErrorEngine

print("? from modules.error_engine import ErrorEngine")

# Test AIM modules
from modules.aim_environment import HealthMonitor

print("? from modules.aim_environment import HealthMonitor")

from modules.aim_registry import load_config

print("? from modules.aim_registry import load_config")

# Test error plugin
from modules.error_plugin_python_ruff import parse

print("? from modules.error_plugin_python_ruff import parse")

print("\n?? All imports successful!")
print("Hybrid import strategy working correctly.")
