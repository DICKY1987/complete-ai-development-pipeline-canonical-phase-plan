"""Tests for mdformat fix plugin."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_mdformat_placeholder():
    """Placeholder test for mdformat plugin."""
    assert True
