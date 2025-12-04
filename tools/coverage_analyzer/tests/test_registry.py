"""Tests for the adapter registry."""

from unittest.mock import Mock

import pytest
from coverage_analyzer.adapters.base_adapter import BaseAdapter, ToolNotAvailableError
from coverage_analyzer.registry import AnalyzerRegistry, get_registry


class MockAdapter(BaseAdapter):
    """Mock adapter for testing."""

    def _get_tool_name(self) -> str:
        return "mock_tool"

    def execute(self, target_path: str, **kwargs):
        return {"mock": "result"}


class TestAnalyzerRegistry:
    """Tests for AnalyzerRegistry class."""

    def test_initialization(self):
        registry = AnalyzerRegistry()
        assert registry._adapters == {}
        assert all(
            layer in registry._layer_mapping
            for layer in ["0", "0.5", "1", "2", "3", "4"]
        )

    def test_register_adapter(self):
        registry = AnalyzerRegistry()
        registry.register("mock", MockAdapter, "1")

        assert "mock" in registry._adapters
        assert "mock" in registry.get_adapters_for_layer("1")

    def test_register_invalid_adapter(self):
        registry = AnalyzerRegistry()

        with pytest.raises(ValueError, match="must inherit from BaseAdapter"):
            registry.register("invalid", str, "1")

    def test_register_invalid_layer(self):
        registry = AnalyzerRegistry()

        with pytest.raises(ValueError, match="Invalid layer"):
            registry.register("mock", MockAdapter, "99")

    def test_get_adapter_not_registered(self):
        registry = AnalyzerRegistry()

        with pytest.raises(KeyError, match="not registered"):
            registry.get_adapter("nonexistent")

    def test_get_adapters_for_layer(self):
        registry = AnalyzerRegistry()
        registry.register("mock1", MockAdapter, "1")
        registry.register("mock2", MockAdapter, "1")
        registry.register("mock3", MockAdapter, "2")

        layer1_adapters = registry.get_adapters_for_layer("1")
        assert "mock1" in layer1_adapters
        assert "mock2" in layer1_adapters
        assert "mock3" not in layer1_adapters

    def test_get_adapters_for_empty_layer(self):
        registry = AnalyzerRegistry()
        assert registry.get_adapters_for_layer("4") == []

    def test_is_adapter_available_not_registered(self):
        registry = AnalyzerRegistry()
        assert registry.is_adapter_available("nonexistent") is False


def test_get_registry_singleton():
    """Test that get_registry returns the same instance."""
    registry1 = get_registry()
    registry2 = get_registry()
    assert registry1 is registry2
