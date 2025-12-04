"""
In-memory vector store for semantic search.
"""

# DOC_ID: DOC-CORE-SEARCH-VECTOR-STORE-603

import json
from typing import List, Tuple

from core.search.embeddings import Embeddings


class VectorStore:
    """Minimal in-memory vector store."""

    def __init__(self, embeddings: Embeddings):
        self.embeddings = embeddings
        self.records: List[Tuple[str, str, object]] = []  # (id, text, vector)

    def add_texts(self, ids: List[str], texts: List[str]):
        vectors = self.embeddings.encode(texts)
        for i, text, vec in zip(ids, texts, vectors):
            self.records.append((i, text, vec))

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        q_vec = self.embeddings.encode([query])[0]
        scored = []
        for rec_id, _text, vec in self.records:
            score = self.embeddings.cosine_sim(q_vec, vec)
            scored.append((rec_id, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def save(self, path):
        """Persist store to json."""
        serializable = []
        for rec_id, text, vec in self.records:
            counts, norm = vec
            serializable.append(
                {"id": rec_id, "text": text, "counts": dict(counts), "norm": norm}
            )
        with open(path, "w", encoding="utf-8") as f:
            json.dump(serializable, f)

    @classmethod
    def load(cls, path, embeddings: Embeddings):
        """Load store from json."""
        store = cls(embeddings)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for item in data:
            counts = item["counts"]
            norm = item["norm"]
            store.records.append((item["id"], item["text"], (counts, norm)))
        return store


__all__ = ["VectorStore"]
