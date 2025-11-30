# DOC_LINK: DOC-PAT-RICH-TEXT-357
# DOC_LINK: DOC-PAT-RICH-TEXT-313
from __future__ import annotations


class Text(str):
    def __new__(cls, value: str, *, style: str | None = None) -> "Text":
        obj = str.__new__(cls, value)
        obj.style = style
        return obj
