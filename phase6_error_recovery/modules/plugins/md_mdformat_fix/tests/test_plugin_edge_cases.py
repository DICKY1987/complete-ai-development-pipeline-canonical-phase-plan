"""Tests for mdformat edge cases.

DOC_ID: DOC-CORE-TESTS-TEST-PLUGIN-EDGE-CASES-842
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_mdformat_edge_placeholder():
    """Placeholder test for mdformat edge cases."""
    assert True
