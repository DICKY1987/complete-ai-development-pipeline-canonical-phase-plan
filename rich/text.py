from __future__ import annotations


class Text(str):
    def __new__(cls, value: str, *, style: str | None = None) -> "Text":
        obj = str.__new__(cls, value)
        obj.style = style
        return obj
