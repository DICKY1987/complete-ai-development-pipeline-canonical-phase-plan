"""
Simple embedding generator (bag-of-words counts) for offline semantic search.
"""

# DOC_ID: DOC-CORE-SEARCH-EMBEDDINGS-602

import math
from collections import Counter
from typing import List


class Embeddings:
    """Lightweight embedding using token frequency."""

    def encode(self, texts: List[str]) -> List[List[float]]:
        """Encode texts into sparse frequency vectors."""
        vectors = []
        for text in texts:
            tokens = text.lower().split()
            counts = Counter(tokens)
            norm = math.sqrt(sum(v * v for v in counts.values())) or 1.0
            vectors.append([counts, norm])
        return vectors

    @staticmethod
    def cosine_sim(vec_a, vec_b) -> float:
        counts_a, norm_a = vec_a
        counts_b, norm_b = vec_b
        dot = sum(counts_a[t] * counts_b.get(t, 0) for t in counts_a.keys())
        denom = norm_a * norm_b or 1.0
        return dot / denom


__all__ = ["Embeddings"]
