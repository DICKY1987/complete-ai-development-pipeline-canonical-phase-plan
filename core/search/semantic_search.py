"""
Semantic search orchestrator.
"""

# DOC_ID: DOC-CORE-SEARCH-SEMANTIC-604

from typing import List, Tuple

from core.search.embeddings import Embeddings
from core.search.vector_store import VectorStore


class SemanticSearch:
    """Simple semantic search built on VectorStore."""

    def __init__(self, store: VectorStore):
        self.store = store

    @classmethod
    def with_default_store(cls):
        emb = Embeddings()
        return cls(VectorStore(emb))

    def index(self, ids: List[str], texts: List[str]):
        self.store.add_texts(ids, texts)

    def query(self, text: str, top_k: int = 5) -> List[Tuple[str, float]]:
        return self.store.search(text, top_k=top_k)


__all__ = ["SemanticSearch"]
