"""Feature flags for Phase 4 AI components."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FeatureFlags:
    enable_reflexion: bool = True
    enable_hyde_search: bool = True
    enable_terminal_capture: bool = True
    enable_episodic_memory: bool = True
