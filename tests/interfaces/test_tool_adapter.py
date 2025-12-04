"""Tests for ToolAdapter protocol and implementations."""

import pytest
from typing import Any

from core.tool_adapter import (
    ToolAdapter,
    CapabilityNotSupportedError,
    JobPreparationError,
)
from core.adapters.base import BaseToolAdapter
from core.adapters.registry import ToolRegistry, MockAdapter
from core.execution.subprocess_executor import SubprocessExecutor
from core.process_executor import ProcessResult


class TestToolAdapterProtocol:
    """Test ToolAdapter protocol compliance."""

    # DOC_ID: DOC-TEST-INTERFACES-TEST-TOOL-ADAPTER-125

    def test_base_adapter_implements_protocol(self):
        """BaseToolAdapter implements ToolAdapter protocol."""
        adapter = BaseToolAdapter("test", {"test"})
        assert isinstance(adapter, ToolAdapter)

    def test_mock_adapter_implements_protocol(self):
        """MockAdapter implements ToolAdapter protocol."""
        adapter = MockAdapter("mock", {"test"})
        assert isinstance(adapter, ToolAdapter)


class TestBaseToolAdapter:
    """Test BaseToolAdapter implementation."""

    def test_name_and_capabilities(self):
        """Adapter exposes name and capabilities."""
        adapter = BaseToolAdapter("test", {"cap1", "cap2"})

        assert adapter.name == "test"
        assert adapter.capabilities == {"cap1", "cap2"}

    def test_supports_all_capabilities(self):
        """supports() returns True when all capabilities present."""
        adapter = BaseToolAdapter("test", {"a", "b", "c"})

        assert adapter.supports({"a"}) is True
        assert adapter.supports({"a", "b"}) is True
        assert adapter.supports({"a", "b", "c"}) is True

    def test_supports_missing_capability(self):
        """supports() returns False when capability missing."""
        adapter = BaseToolAdapter("test", {"a", "b"})

        assert adapter.supports({"c"}) is False
        assert adapter.supports({"a", "c"}) is False

    def test_prepare_job_validates_required_fields(self):
        """prepare_job() raises error if action missing."""
        adapter = BaseToolAdapter("test", {"test"})

        with pytest.raises(JobPreparationError) as exc_info:
            adapter.prepare_job({})

        assert "action" in str(exc_info.value)

    def test_prepare_job_returns_copy(self):
        """prepare_job() returns copy of job spec."""
        adapter = BaseToolAdapter("test", {"test"})
        job = {"action": "test", "data": "value"}

        prepared = adapter.prepare_job(job)

        assert prepared == job
        assert prepared is not job  # Different object

    def test_normalize_result_success(self):
        """normalize_result() formats successful result."""
        adapter = BaseToolAdapter("test", {"test"})
        result = ProcessResult(
            exit_code=0,
            stdout="output",
            stderr="",
            duration_s=1.5,
            command=["test"],
        )

        normalized = adapter.normalize_result(result)

        assert normalized["status"] == "success"
        assert normalized["exit_code"] == 0
        assert normalized["stdout"] == "output"
        assert normalized["duration_s"] == 1.5
        assert normalized["tool"] == "test"

    def test_normalize_result_failure(self):
        """normalize_result() formats failed result."""
        adapter = BaseToolAdapter("test", {"test"})
        result = ProcessResult(
            exit_code=1,
            stdout="",
            stderr="error",
            duration_s=0.5,
            command=["test"],
        )

        normalized = adapter.normalize_result(result)

        assert normalized["status"] == "failed"
        assert normalized["exit_code"] == 1
        assert normalized["stderr"] == "error"


class TestToolRegistry:
    """Test ToolRegistry functionality."""

    def test_register_adapter(self):
        """Can register new adapter."""
        registry = ToolRegistry()
        adapter = MockAdapter("custom", {"custom_cap"})

        registry.register(adapter)

        assert "custom" in registry.list_adapters()

    def test_register_duplicate_raises(self):
        """Registering duplicate adapter raises error."""
        registry = ToolRegistry()
        adapter1 = MockAdapter("test", {"test"})
        adapter2 = MockAdapter("test", {"test"})

        registry.register(adapter1)

        with pytest.raises(ValueError, match="already registered"):
            registry.register(adapter2)

    def test_get_adapter_by_capability(self):
        """get_adapter() finds adapter by capability."""
        registry = ToolRegistry()
        adapter = MockAdapter("test", {"test_cap"})
        registry.register(adapter)

        found = registry.get_adapter({"test_cap"})

        assert found.name == "test"

    def test_get_adapter_preferred(self):
        """get_adapter() prefers specified adapter."""
        registry = ToolRegistry()
        adapter1 = MockAdapter("adapter1", {"test"})
        adapter2 = MockAdapter("adapter2", {"test"})
        registry.register(adapter1)
        registry.register(adapter2)

        found = registry.get_adapter({"test"}, preferred="adapter2")

        assert found.name == "adapter2"

    def test_get_adapter_no_support_raises(self):
        """get_adapter() raises if no adapter supports capability."""
        registry = ToolRegistry()

        with pytest.raises(CapabilityNotSupportedError):
            registry.get_adapter({"nonexistent_capability"})

    def test_list_adapters(self):
        """list_adapters() returns all registered names."""
        registry = ToolRegistry()

        adapters = registry.list_adapters()

        assert isinstance(adapters, list)
        assert "echo" in adapters  # Built-in mock adapter

    def test_get_by_name(self):
        """get_by_name() retrieves adapter by name."""
        registry = ToolRegistry()

        adapter = registry.get_by_name("echo")

        assert adapter is not None
        assert adapter.name == "echo"

    def test_get_by_name_not_found(self):
        """get_by_name() returns None if not found."""
        registry = ToolRegistry()

        adapter = registry.get_by_name("nonexistent")

        assert adapter is None


class TestMockAdapter:
    """Test MockAdapter functionality."""

    def test_run_executes_job(self):
        """MockAdapter.run() executes and returns result."""
        adapter = MockAdapter("mock", {"test"})
        executor = SubprocessExecutor()
        job = {"action": "test_action"}

        result = adapter.run(job, executor=executor)

        assert result.success
        assert "test_action" in result.stdout
        assert "mock" in result.stdout.lower()

    def test_full_workflow(self):
        """Full workflow: prepare -> run -> normalize."""
        adapter = MockAdapter("mock", {"test"})
        executor = SubprocessExecutor()

        # Prepare
        job_spec = {"action": "test"}
        job = adapter.prepare_job(job_spec)

        # Run
        result = adapter.run(job, executor=executor)

        # Normalize
        normalized = adapter.normalize_result(result)

        assert normalized["status"] == "success"
        assert normalized["tool"] == "mock"


class TestToolAdapterIntegration:
    """Integration tests for tool adapter system."""

    def test_registry_adapter_workflow(self):
        """Complete workflow using registry."""
        registry = ToolRegistry()

        # Get adapter by capability
        adapter = registry.get_adapter({"test"})

        # Prepare job
        job = adapter.prepare_job({"action": "test"})

        # Execute
        executor = SubprocessExecutor()
        result = adapter.run(job, executor=executor)

        # Normalize
        normalized = adapter.normalize_result(result)

        assert normalized["status"] == "success"
        assert result.success


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
