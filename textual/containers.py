from __future__ import annotations

from typing import Iterable

from textual.widget import Widget


class Container(Widget):
    def __init__(self, *children: Widget, **kwargs: object) -> None:
        super().__init__(**kwargs)
        for child in children:
            self.mount(child)

    def add(self, widget: Widget) -> Widget:
        return self.mount(widget)

    def remove_children(self) -> None:
        super().remove_children()


class Horizontal(Container):
    pass


class Vertical(Container):
    pass
