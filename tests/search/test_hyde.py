from core.search import HyDESearch, InMemoryVectorStore


def test_hyde_prioritizes_related_documents():
    store = InMemoryVectorStore()
    store.add_documents(
        [
            ("doc-auth", "def login_user(): pass", {"tags": ["auth"]}),
            ("doc-payments", "def process_payment(): pass", {"tags": ["payments"]}),
            ("doc-logging", "def init_logging(): pass", {"tags": ["logging"]}),
        ]
    )

    hyde = HyDESearch(vector_store=store)
    results = hyde.search("login user", top_k=2)

    top_ids = [r.doc_id for r in results]
    assert "doc-auth" in top_ids
    assert len(results) == 2


def test_generate_hypothetical_is_deterministic():
    store = InMemoryVectorStore()
    hyde = HyDESearch(vector_store=store)
    snippet1 = hyde.generate_hypothetical("validate email")
    snippet2 = hyde.generate_hypothetical("validate email")
    assert snippet1 == snippet2
