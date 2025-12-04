"""HyDE (Hypothetical Document Embeddings) search implementation (WS-04-03C)."""
DOC_ID: DOC-CORE-SEARCH-HYDE-744

from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Sequence, Tuple

Embedder = Callable[[str], List[float]]


def _normalize_vector(vector: Sequence[float]) -> List[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return [0.0 for _ in vector]
    return [value / norm for value in vector]


def _default_embedder(text: str, dimensions: int = 16) -> List[float]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    vector = [0.0] * dimensions
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        idx = digest[0] % dimensions
        vector[idx] += 1.0
    return _normalize_vector(vector)


def _cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    if len(a) != len(b):
        return 0.0
    numerator = sum(x * y for x, y in zip(a, b))
    denom_a = math.sqrt(sum(x * x for x in a))
    denom_b = math.sqrt(sum(y * y for y in b))
    if denom_a == 0 or denom_b == 0:
        return 0.0
    return numerator / (denom_a * denom_b)


@dataclass
class SearchResult:
    doc_id: str
    score: float
    metadata: Dict[str, object]


class InMemoryVectorStore:
    """Minimal vector store for HyDE tests and local use."""
DOC_ID: DOC-CORE-SEARCH-HYDE-739
DOC_ID: DOC-CORE-SEARCH-HYDE-640
DOC_ID: DOC-CORE-SEARCH-HYDE-618

    def __init__(self, embedder: Embedder | None = None):
        self.embedder = embedder or _default_embedder
        self._store: Dict[str, Tuple[List[float], Dict[str, object]]] = {}

    def add_documents(
        self, documents: Iterable[Tuple[str, str, Dict[str, object]]]
    ) -> None:
        for doc_id, text, metadata in documents:
            self._store[doc_id] = (self.embedder(text), metadata)

    def search(
        self, query_embedding: Sequence[float], top_k: int = 5
    ) -> List[SearchResult]:
        results: List[SearchResult] = []
        for doc_id, (embedding, metadata) in self._store.items():
            score = _cosine_similarity(query_embedding, embedding)
            results.append(SearchResult(doc_id=doc_id, score=score, metadata=metadata))
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]


class HyDESearch:
    """Generates hypothetical code for a query, embeds it, and searches vectors."""

    def __init__(
        self,
        vector_store: InMemoryVectorStore,
        embedder: Embedder | None = None,
    ):
        self.vector_store = vector_store
        self.embedder = embedder or _default_embedder

    def generate_hypothetical(self, query: str) -> str:
        # Lightweight heuristic: wrap query into a code-like snippet.
        safe_name = re.sub(r"[^a-zA-Z0-9_]+", "_", query.strip()) or "function"
        return f"def {safe_name}():\n    # hypothetical implementation for {query}\n    pass"

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        hypo = self.generate_hypothetical(query)
        query_embedding = self.embedder(hypo)
        return self.vector_store.search(query_embedding, top_k=top_k)
