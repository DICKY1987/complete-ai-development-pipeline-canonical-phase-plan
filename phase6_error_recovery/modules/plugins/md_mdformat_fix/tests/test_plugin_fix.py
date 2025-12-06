"""Tests for mdformat fix plugin.

DOC_ID: DOC-CORE-TESTS-TEST-PLUGIN-FIX-843
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_mdformat_placeholder():
    """Placeholder test for mdformat plugin."""
    assert True
