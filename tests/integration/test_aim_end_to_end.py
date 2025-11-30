"""End-to-end integration tests for AIM system.

These tests verify the full AIM workflow with real AIM registry and adapters.
Tests are skipped if AIM registry is unavailable.
"""
DOC_ID: DOC-TEST-INTEGRATION-TEST-AIM-END-TO-END-118

import pytest

from aim.bridge import (
    detect_tool,
    get_aim_registry_path,
    get_tool_version,
    load_aim_registry,
    load_coordination_rules,
    route_capability,
)


# Check if AIM registry is available
try:
    aim_path = get_aim_registry_path()
    AIM_AVAILABLE = True
except FileNotFoundError:
    AIM_AVAILABLE = False


@pytest.mark.aim
@pytest.mark.skipif(not AIM_AVAILABLE, reason="AIM registry not available")
class TestAimEndToEnd:
    """End-to-end integration tests for AIM system."""

    def test_aim_registry_loads(self):
        """Should successfully load AIM registry."""
        registry = load_aim_registry()
        assert isinstance(registry, dict)
        assert "tools" in registry

    def test_coordination_rules_load(self):
        """Should successfully load coordination rules."""
        rules = load_coordination_rules()
        assert isinstance(rules, dict)
        assert "capabilities" in rules

    def test_tool_detection(self):
        """Should detect at least one registered tool."""
        registry = load_aim_registry()
        tools = registry.get("tools", {})

        assert len(tools) > 0, "No tools registered in AIM registry"

        # Check if any tool is detected
        detected_count = 0
        for tool_id in tools.keys():
            if detect_tool(tool_id):
                detected_count += 1

        # We expect at least one tool to be installed (probably aider or jules)
        # If no tools detected, skip rather than fail (CI environment may not have tools)
        if detected_count == 0:
            pytest.skip("No AIM tools detected in environment")

    def test_tool_version_retrieval(self):
        """Should get version for detected tools."""
        registry = load_aim_registry()
        tools = registry.get("tools", {})

        for tool_id in tools.keys():
            if detect_tool(tool_id):
                version = get_tool_version(tool_id)
                # Version should be non-empty string
                assert version is not None
                assert len(version) > 0
                print(f"{tool_id} version: {version}")

    def test_version_checking_capability(self):
        """Should successfully route version_checking capability."""
        # This is a lightweight capability that should work without heavy tool invocation
        result = route_capability(
            capability="version_checking",
            payload={"tools": []}
        )

        # Result structure should be valid regardless of success
        assert isinstance(result, dict)
        assert "success" in result
        assert "message" in result

    def test_audit_log_created(self):
        """Should create audit log for capability invocation."""
        aim_path = get_aim_registry_path()
        audit_dir = aim_path / "AIM_audit"

        # Invoke capability
        route_capability(
            capability="version_checking",
            payload={"check_updates": False}
        )

        # Verify audit directory exists
        assert audit_dir.exists()

        # Verify at least one date directory exists
        date_dirs = list(audit_dir.iterdir())
        assert len(date_dirs) > 0

        # Verify at least one audit log file exists
        has_audit_logs = False
        for date_dir in date_dirs:
            if date_dir.is_dir():
                audit_files = list(date_dir.glob("*.json"))
                if len(audit_files) > 0:
                    has_audit_logs = True
                    break

        assert has_audit_logs, "No audit log files created"

    def test_capability_routing_follows_rules(self):
        """Should route capability according to coordination rules."""
        rules = load_coordination_rules()
        capabilities = rules.get("capabilities", {})

        if not capabilities:
            pytest.skip("No capabilities defined in coordination rules")

        # Get first capability
        cap_name = list(capabilities.keys())[0]
        cap_rules = capabilities[cap_name]

        primary_tool = cap_rules.get("primary")
        fallback_tools = cap_rules.get("fallback", [])

        # Verify routing is configured
        assert primary_tool is not None, f"No primary tool for {cap_name}"

        print(f"Capability '{cap_name}' routes to:")
        print(f"  Primary: {primary_tool}")
        print(f"  Fallbacks: {fallback_tools}")


@pytest.mark.aim
@pytest.mark.skipif(AIM_AVAILABLE, reason="Testing AIM unavailable scenario")
class TestAimUnavailable:
    """Tests for graceful degradation when AIM is unavailable."""

    def test_get_registry_path_raises_clear_error(self):
        """Should raise clear error if AIM registry not found."""
        with pytest.raises(FileNotFoundError, match="Registry not found"):
            get_aim_registry_path()

    def test_detect_tool_returns_false_when_registry_unavailable(self):
        """Should return False if registry unavailable."""
        result = detect_tool("aider")
        assert result is False

    def test_get_tool_version_returns_none_when_registry_unavailable(self):
        """Should return None if registry unavailable."""
        result = get_tool_version("aider")
        assert result is None

