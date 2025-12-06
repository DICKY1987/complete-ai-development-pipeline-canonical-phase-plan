"""
Analyzer registry for dynamic tool adapter discovery and instantiation.

The registry pattern allows for flexible addition of new adapters without
modifying core code.
"""
DOC_ID: DOC-SCRIPT-COVERAGE-ANALYZER-REGISTRY-795

import logging
from typing import Dict, List, Optional, Type

from .adapters.base_adapter import BaseAdapter, ToolNotAvailableError

logger = logging.getLogger(__name__)


class AnalyzerRegistry:
    """
    Registry for coverage analyzer tool adapters.

    Manages registration and instantiation of tool adapters for all 5 layers.
    """

    def __init__(self):
        self._adapters: Dict[str, Type[BaseAdapter]] = {}
        self._layer_mapping: Dict[str, List[str]] = {
            "0": [],  # Static Analysis
            "0.5": [],  # SCA
            "1": [],  # Structural Coverage
            "2": [],  # Mutation Testing
            "3": [],  # Complexity
            "4": [],  # Operational Validation
        }

    def register(self, name: str, adapter_class: Type[BaseAdapter], layer: str) -> None:
        """
        Register a tool adapter.

        Args:
            name: Unique name for the adapter (e.g., "coverage.py", "bandit")
            adapter_class: Adapter class (must inherit from BaseAdapter)
            layer: Coverage layer ("0", "0.5", "1", "2", "3", "4")

        Raises:
            ValueError: If adapter_class doesn't inherit from BaseAdapter
        """
        if not issubclass(adapter_class, BaseAdapter):
            raise ValueError(f"Adapter {name} must inherit from BaseAdapter")

        if layer not in self._layer_mapping:
            raise ValueError(
                f"Invalid layer '{layer}'. Must be one of: 0, 0.5, 1, 2, 3, 4"
            )

        self._adapters[name] = adapter_class
        if name not in self._layer_mapping[layer]:
            self._layer_mapping[layer].append(name)

        logger.info(f"Registered adapter '{name}' for layer {layer}")

    def get_adapter(self, name: str, config: Optional[Dict] = None) -> BaseAdapter:
        """
        Get an instantiated adapter by name.

        Args:
            name: Adapter name
            config: Optional configuration for the adapter

        Returns:
            Instantiated adapter

        Raises:
            KeyError: If adapter not found
            ToolNotAvailableError: If tool is not installed
        """
        if name not in self._adapters:
            raise KeyError(f"Adapter '{name}' not registered")

        adapter_class = self._adapters[name]
        adapter = adapter_class(config=config)

        if not adapter.is_tool_available():
            raise ToolNotAvailableError(
                f"Tool '{adapter.tool_name}' is not installed or not available in PATH"
            )

        return adapter

    def get_adapters_for_layer(self, layer: str) -> List[str]:
        """
        Get all adapter names registered for a specific layer.

        Args:
            layer: Coverage layer

        Returns:
            List of adapter names
        """
        return self._layer_mapping.get(layer, [])

    def list_available_adapters(self) -> Dict[str, List[str]]:
        """
        List all available (installed) adapters by layer.

        Returns:
            Dictionary mapping layer to list of available adapter names
        """
        available = {}

        for layer, adapter_names in self._layer_mapping.items():
            available[layer] = []
            for name in adapter_names:
                try:
                    adapter = self._adapters[name]()
                    if adapter.is_tool_available():
                        available[layer].append(name)
                except Exception as e:
                    logger.debug(f"Adapter '{name}' not available: {e}")

        return available

    def is_adapter_available(self, name: str) -> bool:
        """
        Check if an adapter is registered and its tool is available.

        Args:
            name: Adapter name

        Returns:
            True if adapter is registered and tool is available
        """
        if name not in self._adapters:
            return False

        try:
            adapter = self._adapters[name]()
            return adapter.is_tool_available()
        except Exception:
            return False


# Global registry instance
_registry = AnalyzerRegistry()


def get_registry() -> AnalyzerRegistry:
    """Get the global analyzer registry instance."""
    return _registry
