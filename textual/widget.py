from __future__ import annotations

from typing import Iterable, List, Optional, Sequence, Union


class Widget:
    def __init__(
        self,
        content: str | None = None,
        *,
        id: Optional[str] = None,
        classes: Sequence[str] | None = None,
    ) -> None:
        self.content = content or ""
        self.id = id
        self.classes = list(classes or [])
        self.children: List["Widget"] = []

    def mount(self, widget: "Widget") -> "Widget":
        self.children.append(widget)
        return widget

    def remove_children(self) -> None:
        self.children.clear()

    def __repr__(self) -> str:
        return f"<Widget id={self.id} classes={self.classes}>"
