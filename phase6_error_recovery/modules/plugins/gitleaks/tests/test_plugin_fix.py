"""Test Gitleaks plugin fix capabilities (N/A - detection only).

DOC_ID: DOC-CORE-TESTS-TEST-PLUGIN-FIX-807
"""

from __future__ import annotations

import shutil

import pytest

from phase6_error_recovery.modules.plugins.gitleaks.src.gitleaks.plugin import (
    GitleaksPlugin,
)


@pytest.mark.skipif(not shutil.which("gitleaks"), reason="gitleaks not installed")
class TestGitleaksFix:
    """Test Gitleaks plugin - no auto-fix, detection only."""

    def test_no_fix_method(self):
        """Verify Gitleaks plugin is detection-only (no auto-fix)."""
        plugin = GitleaksPlugin()

        # Gitleaks is detection-only, no fix method
        assert not hasattr(plugin, "fix")

    def test_plugin_purpose_is_detection(self):
        """Verify plugin is configured for detection, not fixing."""
        plugin = GitleaksPlugin()

        # Plugin should only detect secrets
        assert hasattr(plugin, "execute")
        assert hasattr(plugin, "check_tool_available")
        assert hasattr(plugin, "build_command")

        # No fix capabilities
        assert not hasattr(plugin, "fix")
        assert not hasattr(plugin, "apply_fix")


def test_gitleaks_is_detection_only():
    """Document that Gitleaks plugin is detection-only."""
    plugin = GitleaksPlugin()

    # This plugin only detects secrets
    # Secrets must be removed/rotated manually
    assert plugin.plugin_id == "gitleaks"
    assert plugin.name == "Gitleaks"
