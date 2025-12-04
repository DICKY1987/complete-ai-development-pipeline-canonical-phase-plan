from core.search.semantic_search import SemanticSearch


def test_semantic_search_basic():
    ss = SemanticSearch.with_default_store()
    ids = ["f1", "f2", "f3"]
    texts = [
        "function to add numbers",
        "class to manage files",
        "utility to search text",
    ]
    ss.index(ids, texts)
    results = ss.query("search files", top_k=2)
    assert results[0][0] in {"f2", "f3"}
    assert len(results) == 2
