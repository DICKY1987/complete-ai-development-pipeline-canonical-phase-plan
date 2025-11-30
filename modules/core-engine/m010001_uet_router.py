from __future__ import annotations


class Router:
    """Minimal router placeholder."""

    def route(self, name: str, payload: dict) -> dict:
        return {"route": name, "payload": payload}


__all__ = ["Router"]
