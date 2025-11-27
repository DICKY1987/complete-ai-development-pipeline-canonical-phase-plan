"""Layout configuration schema for TUI app."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class LayoutConfig:
    """Configuration for TUI layout."""
    default_panel: str = "dashboard"
    theme: str = "dark"
    refresh_interval: int = 1000  # milliseconds
    
    
@dataclass
class PanelConfig:
    """Configuration for individual panels."""
    panel_id: str
    enabled: bool = True
    auto_refresh: bool = True
    refresh_interval: Optional[int] = None  # Override global refresh
