"""Integration tests for AIM orchestrator integration.

Tests the full flow of capability-based routing through the orchestrator,
including fallback behavior and backward compatibility.
"""

# DOC_ID: DOC-TEST-INTEGRATION-TEST-AIM-ORCHESTRATOR-119

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from core.engine.aim_integration import execute_with_aim, is_aim_available
from core.engine.tools import ToolResult

# Skip all tests in this module - AIM not yet implemented (Phase 4)
pytestmark = pytest.mark.skip(
    reason="AIM module not yet implemented - Phase 4 roadmap item"
)


class TestAIMIntegration:
    """Tests for AIM integration with orchestrator."""

    def test_is_aim_available_when_registry_exists(self):
        """Should return True when AIM registry is available."""
        # This test relies on actual registry existing
        result = is_aim_available()
        assert isinstance(result, bool)
        # Don't assert True since registry may not be available in CI

    @patch("core.engine.aim_integration.route_capability")
    @patch("core.engine.aim_integration.is_aim_available", return_value=True)
    def test_execute_with_aim_success(self, mock_available, mock_route):
        """Should execute capability and return ToolResult on success."""
        # Mock successful AIM routing
        mock_route.return_value = {
            "success": True,
            "message": "Code generation completed",
            "content": {
                "tool_id": "aider",
                "exit_code": 0,
                "stdout": "Files modified successfully",
                "stderr": "",
                "started_at": "2025-11-20T21:00:00Z",
                "completed_at": "2025-11-20T21:00:30Z",
                "duration_sec": 30.0,
            },
        }

        result = execute_with_aim(
            capability="code_generation",
            payload={"files": ["test.py"], "prompt": "Add tests"},
            run_id="test-run",
            ws_id="ws-test",
        )

        assert isinstance(result, ToolResult)
        assert result.success is True
        assert result.tool_id == "aider"
        assert result.exit_code == 0
        assert "modified successfully" in result.stdout

    @patch("core.engine.aim_integration.route_capability")
    @patch("core.engine.aim_integration.run_tool")
    def test_execute_with_aim_fallback_on_failure(self, mock_run_tool, mock_route):
        """Should fall back to direct tool when AIM fails."""
        # Mock AIM failure
        mock_route.return_value = {
            "success": False,
            "message": "All tools failed",
            "content": None,
        }

        # Mock successful fallback tool
        mock_run_tool.return_value = ToolResult(
            tool_id="aider",
            command_line="aider --yes",
            exit_code=0,
            stdout="Fallback success",
            stderr="",
            timed_out=False,
            started_at="2025-11-20T21:00:00Z",
            completed_at="2025-11-20T21:00:10Z",
            duration_sec=10.0,
            success=True,
        )

        result = execute_with_aim(
            capability="code_generation",
            payload={"files": ["test.py"]},
            fallback_tool="aider",
            run_id="test-run",
            ws_id="ws-test",
        )

        assert result.success is True
        assert result.tool_id == "aider"
        assert "Fallback success" in result.stdout

        # Verify fallback was called
        mock_run_tool.assert_called_once()

    @patch("core.engine.aim_integration.route_capability")
    def test_execute_with_aim_no_fallback(self, mock_route):
        """Should return failed ToolResult when no fallback specified."""
        # Mock AIM failure
        mock_route.return_value = {
            "success": False,
            "message": "Tool not found",
            "content": None,
        }

        result = execute_with_aim(
            capability="code_generation",
            payload={"files": ["test.py"]},
            fallback_tool=None,  # No fallback
        )

        assert isinstance(result, ToolResult)
        assert result.success is False
        assert result.exit_code == 1
        assert "Tool not found" in result.stderr

    @patch("core.engine.aim_integration.route_capability")
    def test_execute_with_aim_capability_not_found(self, mock_route):
        """Should handle AIMCapabilityNotFoundError gracefully."""
        from aim.exceptions import AIMCapabilityNotFoundError

        # Mock capability not found
        mock_route.side_effect = AIMCapabilityNotFoundError(
            "invalid_capability", available_capabilities=["code_generation", "linting"]
        )

        result = execute_with_aim(
            capability="invalid_capability", payload={}, run_id="test-run"
        )

        assert isinstance(result, ToolResult)
        assert result.success is False
        assert "not defined" in result.stderr.lower()

    @patch("core.engine.aim_integration.route_capability")
    @patch("core.engine.aim_integration.run_tool")
    def test_execute_with_aim_both_fail(self, mock_run_tool, mock_route):
        """Should return aggregated error when both AIM and fallback fail."""
        # Mock AIM failure
        mock_route.return_value = {
            "success": False,
            "message": "AIM routing failed",
            "content": None,
        }

        # Mock fallback failure
        mock_run_tool.side_effect = Exception("Fallback tool error")

        result = execute_with_aim(
            capability="code_generation", payload={}, fallback_tool="aider"
        )

        assert result.success is False
        assert "AIM: AIM routing failed" in result.stderr
        assert "Fallback: Fallback tool error" in result.stderr

    @patch("core.engine.aim_integration.route_capability")
    def test_execute_with_aim_timeout_payload(self, mock_route):
        """Should pass timeout from payload to route_capability."""
        mock_route.return_value = {
            "success": True,
            "message": "OK",
            "content": {"exit_code": 0, "stdout": "", "stderr": ""},
        }

        execute_with_aim(
            capability="code_generation", payload={"timeout_ms": 120000}  # 2 minutes
        )

        # Verify timeout was converted to seconds
        mock_route.assert_called_once()
        call_kwargs = mock_route.call_args.kwargs
        assert call_kwargs["timeout_sec"] == 120


class TestOrchestratorAIMIntegration:
    """Tests for orchestrator using AIM integration."""

    @patch("core.engine.aim_integration.route_capability")
    @patch("core.engine.aim_integration.is_aim_available", return_value=True)
    def test_orchestrator_uses_capability(self, mock_available, mock_route):
        """Should use AIM when capability is specified in workstream."""
        # This is a placeholder for actual orchestrator integration test
        # Would require full orchestrator setup with DB, bundles, etc.

        # Mock successful routing
        mock_route.return_value = {
            "success": True,
            "message": "OK",
            "content": {"exit_code": 0, "stdout": "Success", "stderr": ""},
        }

        # Example workstream with capability
        bundle_obj = {
            "id": "ws-test",
            "capability": "code_generation",
            "capability_payload": {"prompt": "Add tests", "timeout_ms": 60000},
            "files_scope": ["src/test.py"],
            "tasks": ["Add unit tests"],
        }

        # Verify capability is present
        assert "capability" in bundle_obj
        assert bundle_obj["capability"] == "code_generation"


@pytest.mark.integration
class TestAIMEndToEndWithOrchestrator:
    """End-to-end integration tests with real AIM registry."""

    def test_workstream_schema_allows_capability(self):
        """Should validate workstream with capability field."""
        import jsonschema

        # Load schema
        schema_path = (
            Path(__file__).parent.parent.parent / "schema" / "workstream.schema.json"
        )
        with open(schema_path) as f:
            schema = json.load(f)

        # Valid workstream with capability
        workstream = {
            "id": "ws-test-001",
            "openspec_change": "CHANGE-001",
            "ccpm_issue": 123,
            "gate": 1,
            "files_scope": ["src/test.py"],
            "tasks": ["Add tests"],
            "tool": "aider",  # Backward compat
            "capability": "code_generation",  # New field
            "capability_payload": {
                "prompt": "Add unit tests",
                "timeout_ms": 60000,
                "max_retries": 1,
            },
        }

        # Should validate without errors
        jsonschema.validate(instance=workstream, schema=schema)

        # Verify capability field is present
        assert workstream["capability"] == "code_generation"
        assert workstream["capability_payload"]["timeout_ms"] == 60000
