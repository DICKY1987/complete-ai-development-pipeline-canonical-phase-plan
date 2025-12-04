"""
Lightweight summarizer abstraction (mockable for tests).
"""

# DOC_ID: DOC-CORE-INDEXING-SUMMARIZER-502

from typing import List


class Summarizer:
    """Placeholder summarizer; replace with LLM-backed implementation."""

    def __init__(self, max_len: int = 256):
        self.max_len = max_len

    def summarize(self, chunks: List[str]) -> str:
        """Return a simple concatenated summary trimmed to max_len."""
        text = " ".join(chunks)
        return text[: self.max_len]


__all__ = ["Summarizer"]
