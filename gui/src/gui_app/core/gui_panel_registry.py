"""GUI panel registry.

Manages registration and instantiation of GUI panels.
"""

# DOC_ID: DOC-GUI-APP-CORE-GUI-PANEL-REGISTRY-404

from typing import Callable, Dict, Optional

from gui_app.core.gui_panel_plugin import GuiPanelPlugin


class GuiPanelRegistry:
    """Registry for GUI panel plugins."""

    def __init__(self):
        self._panels: Dict[str, Callable[[], GuiPanelPlugin]] = {}

    def register(self, panel_id: str, factory: Callable[[], GuiPanelPlugin]) -> None:
        """Register a panel factory."""
        self._panels[panel_id] = factory

    def create_panel(self, panel_id: str) -> Optional[GuiPanelPlugin]:
        """Create a panel instance by ID."""
        factory = self._panels.get(panel_id)
        if factory:
            return factory()
        return None

    def list_panels(self) -> list[str]:
        """List all registered panel IDs."""
        return list(self._panels.keys())


_registry: Optional[GuiPanelRegistry] = None


def get_registry() -> GuiPanelRegistry:
    """Get the global GUI panel registry."""
    global _registry
    if _registry is None:
        _registry = GuiPanelRegistry()
    return _registry


def register_panel(panel_id: str):
    """Decorator to register a GUI panel."""

    def decorator(cls):
        registry = get_registry()
        registry.register(panel_id, cls)
        return cls

    return decorator
