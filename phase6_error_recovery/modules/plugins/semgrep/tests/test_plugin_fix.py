"""Test Semgrep plugin fix capabilities (N/A - detection only).

DOC_ID: DOC-CORE-TESTS-TEST-PLUGIN-FIX-840
"""

from __future__ import annotations

import shutil

import pytest

from phase6_error_recovery.modules.plugins.semgrep.src.semgrep.plugin import (
    SemgrepPlugin,
)


@pytest.mark.skipif(not shutil.which("semgrep"), reason="semgrep not installed")
class TestSemgrepFix:
    """Test Semgrep plugin - no auto-fix, detection only."""

    def test_no_fix_method(self):
        """Verify Semgrep plugin is detection-only (no auto-fix)."""
        plugin = SemgrepPlugin()

        # Semgrep is detection-only, no fix method
        assert not hasattr(plugin, "fix")

    def test_plugin_purpose_is_detection(self):
        """Verify plugin is configured for detection, not fixing."""
        plugin = SemgrepPlugin()

        # Plugin should only detect issues
        assert hasattr(plugin, "execute")
        assert hasattr(plugin, "check_tool_available")
        assert hasattr(plugin, "build_command")

        # No fix capabilities
        assert not hasattr(plugin, "fix")
        assert not hasattr(plugin, "apply_fix")


def test_semgrep_is_detection_only():
    """Document that Semgrep plugin is detection-only."""
    plugin = SemgrepPlugin()

    # This plugin only detects security issues
    # Fixes must be applied manually by developer
    assert plugin.plugin_id == "semgrep"
    assert plugin.name == "Semgrep"
