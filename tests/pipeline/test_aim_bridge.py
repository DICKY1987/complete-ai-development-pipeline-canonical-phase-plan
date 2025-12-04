"""Unit tests for AIM bridge module.

Tests cover:
- Registry loading
- Coordination rules loading
- Adapter invocation
- Capability routing with fallbacks
- Tool detection
- Audit logging
"""

# DOC_ID: DOC-TEST-PIPELINE-TEST-AIM-BRIDGE-134

import json
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, call, mock_open, patch

import pytest
from aim.bridge import (
    detect_tool,
    get_aim_registry_path,
    get_tool_version,
    invoke_adapter,
    load_aim_registry,
    load_coordination_rules,
    record_audit_log,
    route_capability,
)

# Skip all tests in this module - AIM not yet implemented (Phase 4)
pytestmark = pytest.mark.skip(
    reason="AIM module not yet implemented - Phase 4 roadmap item"
)


class TestGetAimRegistryPath:
    """Tests for get_aim_registry_path()."""

    def test_returns_env_var_path_when_set(self):
        """Should return AIM_REGISTRY_PATH env var if set and exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict("os.environ", {"AIM_REGISTRY_PATH": tmpdir}):
                result = get_aim_registry_path()
                assert result == Path(tmpdir)

    def test_raises_if_env_var_path_not_exists(self):
        """Should raise FileNotFoundError if env var path doesn't exist."""
        with patch.dict("os.environ", {"AIM_REGISTRY_PATH": "/nonexistent/path"}):
            with pytest.raises(FileNotFoundError, match="AIM_REGISTRY_PATH"):
                get_aim_registry_path()

    def test_auto_detects_relative_to_repo_root(self):
        """Should auto-detect .AIM_ai-tools-registry relative to repo root."""
        # This test relies on the actual .AIM_ai-tools-registry existing
        with patch.dict("os.environ", {}, clear=True):
            result = get_aim_registry_path()
            assert result.name == ".AIM_ai-tools-registry"
            assert result.exists()


class TestLoadAimRegistry:
    """Tests for load_aim_registry()."""

    @patch("aim.bridge.get_aim_registry_path")
    def test_loads_valid_registry(self, mock_get_path):
        """Should load and parse valid AIM_registry.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            mock_get_path.return_value = tmpdir_path

            # Create fake registry
            registry_data = {"tools": {"aider": {"name": "Aider"}}}
            registry_file = tmpdir_path / "AIM_registry.json"
            with open(registry_file, "w") as f:
                json.dump(registry_data, f)

            result = load_aim_registry()
            assert result == registry_data

    @patch("aim.bridge.get_aim_registry_path")
    def test_raises_on_missing_registry_file(self, mock_get_path):
        """Should raise FileNotFoundError if AIM_registry.json missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_get_path.return_value = Path(tmpdir)

            with pytest.raises(FileNotFoundError, match="Registry file not found"):
                load_aim_registry()

    @patch("aim.bridge.get_aim_registry_path")
    def test_raises_on_invalid_json(self, mock_get_path):
        """Should raise JSONDecodeError if registry has invalid JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            mock_get_path.return_value = tmpdir_path

            # Create invalid JSON file
            registry_file = tmpdir_path / "AIM_registry.json"
            with open(registry_file, "w") as f:
                f.write("{invalid json}")

            with pytest.raises(json.JSONDecodeError):
                load_aim_registry()


class TestLoadCoordinationRules:
    """Tests for load_coordination_rules()."""

    @patch("aim.bridge.get_aim_registry_path")
    def test_loads_valid_rules(self, mock_get_path):
        """Should load and parse valid coordination rules."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            mock_get_path.return_value = tmpdir_path

            # Create fake rules
            rules_data = {"capabilities": {"code_generation": {"primary": "aider"}}}
            rules_dir = tmpdir_path / "AIM_cross-tool"
            rules_dir.mkdir()
            rules_file = rules_dir / "AIM_coordination-rules.json"
            with open(rules_file, "w") as f:
                json.dump(rules_data, f)

            result = load_coordination_rules()
            assert result == rules_data


class TestInvokeAdapter:
    """Tests for invoke_adapter()."""

    @patch("aim.bridge.subprocess.run")
    @patch("aim.bridge.load_aim_registry")
    def test_success_with_valid_output(self, mock_load_registry, mock_run):
        """Should parse and return adapter output on success."""
        # Mock registry
        mock_load_registry.return_value = {
            "tools": {"aider": {"adapterScript": "C:/fake/adapter.ps1"}}
        }

        # Mock subprocess success
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(
            {"success": True, "message": "OK", "content": {"result": "data"}}
        )
        mock_run.return_value = mock_result

        # Mock file existence
        with patch("aim.bridge.Path.exists", return_value=True):
            result = invoke_adapter("aider", "code_generation", {"prompt": "test"})

        assert result["success"] is True
        assert result["message"] == "OK"

    @patch("aim.bridge.subprocess.run")
    @patch("aim.bridge.load_aim_registry")
    def test_timeout_handling(self, mock_load_registry, mock_run):
        """Should return timeout error if subprocess times out."""
        mock_load_registry.return_value = {
            "tools": {"aider": {"adapterScript": "C:/fake/adapter.ps1"}}
        }

        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 30)

        with patch("aim.bridge.Path.exists", return_value=True):
            result = invoke_adapter("aider", "code_generation", {})

        assert result["success"] is False
        assert "timed out" in result["message"].lower()

    @patch("aim.bridge.load_aim_registry")
    def test_tool_not_found(self, mock_load_registry):
        """Should return error if tool not in registry."""
        mock_load_registry.return_value = {"tools": {}}

        result = invoke_adapter("nonexistent", "code_generation", {})

        assert result["success"] is False
        assert "not found in AIM registry" in result["message"]


class TestRouteCapability:
    """Tests for route_capability()."""

    @patch("aim.bridge.invoke_adapter")
    @patch("aim.bridge.load_coordination_rules")
    @patch("aim.bridge.record_audit_log")
    def test_primary_tool_success(self, mock_audit, mock_load_rules, mock_invoke):
        """Should return result from primary tool if it succeeds."""
        mock_load_rules.return_value = {
            "capabilities": {
                "code_generation": {"primary": "aider", "fallback": ["jules"]}
            }
        }

        mock_invoke.return_value = {"success": True, "message": "OK", "content": {}}

        result = route_capability("code_generation", {"prompt": "test"})

        assert result["success"] is True
        # Should only invoke primary tool
        assert mock_invoke.call_count == 1

    @patch("aim.bridge.invoke_adapter")
    @patch("aim.bridge.load_coordination_rules")
    @patch("aim.bridge.record_audit_log")
    def test_fallback_on_primary_failure(
        self, mock_audit, mock_load_rules, mock_invoke
    ):
        """Should try fallback tool if primary fails."""
        mock_load_rules.return_value = {
            "capabilities": {
                "code_generation": {"primary": "jules", "fallback": ["aider"]}
            }
        }

        # Primary fails, fallback succeeds
        mock_invoke.side_effect = [
            {"success": False, "message": "Jules failed", "content": None},
            {"success": True, "message": "Aider succeeded", "content": {}},
        ]

        result = route_capability("code_generation", {"prompt": "test"})

        assert result["success"] is True
        assert result["message"] == "Aider succeeded"
        # Should invoke both primary and fallback
        assert mock_invoke.call_count == 2

    @patch("aim.bridge.invoke_adapter")
    @patch("aim.bridge.load_coordination_rules")
    @patch("aim.bridge.record_audit_log")
    def test_all_tools_fail(self, mock_audit, mock_load_rules, mock_invoke):
        """Should return aggregated error if all tools fail."""
        mock_load_rules.return_value = {
            "capabilities": {
                "code_generation": {"primary": "jules", "fallback": ["aider"]}
            }
        }

        # All tools fail
        mock_invoke.return_value = {
            "success": False,
            "message": "Failed",
            "content": None,
        }

        result = route_capability("code_generation", {"prompt": "test"})

        assert result["success"] is False
        assert "All tools failed" in result["message"]


class TestDetectTool:
    """Tests for detect_tool()."""

    @patch("aim.bridge.subprocess.run")
    @patch("aim.bridge.load_aim_registry")
    def test_returns_true_if_detect_command_succeeds(
        self, mock_load_registry, mock_run
    ):
        """Should return True if any detect command exits with 0."""
        mock_load_registry.return_value = {
            "tools": {"aider": {"detectCommands": ["aider", "C:/path/aider.exe"]}}
        }

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = detect_tool("aider")
        assert result is True

    @patch("aim.bridge.subprocess.run")
    @patch("aim.bridge.load_aim_registry")
    def test_returns_false_if_all_detect_commands_fail(
        self, mock_load_registry, mock_run
    ):
        """Should return False if all detect commands fail."""
        mock_load_registry.return_value = {
            "tools": {"aider": {"detectCommands": ["aider"]}}
        }

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        result = detect_tool("aider")
        assert result is False


class TestGetToolVersion:
    """Tests for get_tool_version()."""

    @patch("aim.bridge.subprocess.run")
    @patch("aim.bridge.load_aim_registry")
    def test_returns_version_string_on_success(self, mock_load_registry, mock_run):
        """Should return version string if command succeeds."""
        mock_load_registry.return_value = {
            "tools": {"aider": {"versionCommand": ["aider", "--version"]}}
        }

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "aider 0.5.0\n"
        mock_run.return_value = mock_result

        result = get_tool_version("aider")
        assert result == "aider 0.5.0"

    @patch("aim.bridge.subprocess.run")
    @patch("aim.bridge.load_aim_registry")
    def test_returns_none_on_failure(self, mock_load_registry, mock_run):
        """Should return None if version command fails."""
        mock_load_registry.return_value = {
            "tools": {"aider": {"versionCommand": ["aider", "--version"]}}
        }

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        result = get_tool_version("aider")
        assert result is None


class TestRecordAuditLog:
    """Tests for record_audit_log()."""

    @patch("aim.bridge.get_aim_registry_path")
    def test_writes_audit_log_to_correct_location(self, mock_get_path):
        """Should write audit log to AIM_audit/<date>/<timestamp>_<tool>_<cap>.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            mock_get_path.return_value = tmpdir_path

            payload = {"prompt": "test"}
            result = {"success": True, "message": "OK"}

            record_audit_log("aider", "code_generation", payload, result)

            # Verify audit file created
            audit_dir = tmpdir_path / "AIM_audit"
            assert audit_dir.exists()

            # Find the audit file
            date_dirs = list(audit_dir.iterdir())
            assert len(date_dirs) == 1

            audit_files = list(date_dirs[0].glob("*.json"))
            assert len(audit_files) == 1

            # Verify audit log content
            with open(audit_files[0]) as f:
                entry = json.load(f)

            assert entry["actor"] == "pipeline"
            assert entry["tool_id"] == "aider"
            assert entry["capability"] == "code_generation"
            assert entry["payload"] == payload
            assert entry["result"] == result

    @patch("aim.bridge.get_aim_registry_path")
    def test_handles_missing_registry_gracefully(self, mock_get_path):
        """Should not crash if registry path not found."""
        mock_get_path.side_effect = FileNotFoundError("Registry not found")

        # Should not raise exception
        record_audit_log("aider", "code_generation", {}, {})
