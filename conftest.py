"""Root pytest configuration.

This file is loaded before any tests and sets up the Python path.
"""
DOC_ID: DOC-CORE-CONFTEST-240
DOC_ID: DOC-CORE-CONFTEST-201
DOC_ID: DOC-PAT-CONFTEST-690
DOC_ID: DOC-PAT-CONFTEST-399
DOC_ID: DOC-PAT-CONFTEST-338
DOC_ID: DOC-PAT-CONFTEST-294
DOC_ID: DOC-PAT-CONFTEST-279
DOC_ID: DOC-PAT-CONFTEST-264
import sys
from pathlib import Path

# Ensure project root is in sys.path for imports
_root = Path(__file__).parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))


def pytest_configure(config):
    """Called after pytest configuration is set up.
    
    Ensures project root is always in sys.path for imports.
    """
    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

