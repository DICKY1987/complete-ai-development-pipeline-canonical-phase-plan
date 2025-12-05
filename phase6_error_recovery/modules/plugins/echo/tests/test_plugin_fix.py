"""Test Echo plugin fix capabilities (N/A - no-op validator)."""

from __future__ import annotations

from phase6_error_recovery.modules.plugins.echo.src.echo.plugin import EchoPlugin


class TestEchoFix:
    """Test Echo plugin - no fix needed, always succeeds."""

    def test_no_fix_method(self):
        """Verify Echo plugin has no fix method."""
        plugin = EchoPlugin()

        # Echo is no-op, no fix method
        assert not hasattr(plugin, "fix")

    def test_no_fix_needed(self):
        """Verify Echo never produces issues to fix."""
        plugin = EchoPlugin()

        # Echo never reports issues, so no fixes needed
        assert hasattr(plugin, "execute")
        assert not hasattr(plugin, "fix")


def test_echo_no_op_validator():
    """Document that Echo is a no-op validator."""
    plugin = EchoPlugin()

    # This plugin exists for testing framework
    # Always succeeds, never fixes anything
    assert plugin.plugin_id == "echo"
    assert plugin.name == "Echo Validator"
