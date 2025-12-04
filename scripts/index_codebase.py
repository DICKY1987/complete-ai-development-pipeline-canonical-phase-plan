"""
CLI to index codebase for semantic search.
"""

# DOC_ID: DOC-SCRIPT-INDEX-SEMANTIC-704

import argparse
from pathlib import Path

from core.ast.repository_mapper import RepositoryMapper
from core.search.embeddings import Embeddings
from core.search.semantic_search import SemanticSearch
from core.search.vector_store import VectorStore


def _collect_texts(repo_map):
    ids = []
    texts = []
    modules = repo_map.get("modules", {})
    for module_name, module_info in modules.items():
        base_text = f"module {module_name}"
        ids.append(module_name)
        texts.append(base_text)

        for func in module_info.get("functions", []):
            fid = f"{module_name}.{func.get('name','')}"
            sig = f"{fid}({', '.join(func.get('params', []))})"
            ids.append(fid)
            texts.append(sig)

        for cls in module_info.get("classes", []):
            cid = f"{module_name}.{cls.get('name','')}"
            bases = ", ".join(cls.get("bases", []))
            ids.append(cid)
            texts.append(f"class {cid}({bases})")
    return ids, texts


def main():
    parser = argparse.ArgumentParser(description="Index codebase for semantic search.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(".worktrees/vector_index.json"),
        help="Output JSON index",
    )
    parser.add_argument(
        "--query", type=str, help="Optional query to run after indexing"
    )
    parser.add_argument("--topk", type=int, default=5, help="Results to return")
    args = parser.parse_args()

    repo_map = RepositoryMapper(args.root).generate_map()
    ids, texts = _collect_texts(repo_map)

    emb = Embeddings()
    store = VectorStore(emb)
    ss = SemanticSearch(store)
    ss.index(ids, texts)
    store.save(args.out)
    print(f"Vector index written to {args.out} (records: {len(ids)})")

    if args.query:
        results = ss.query(args.query, top_k=args.topk)
        print("Top results:")
        for rec_id, score in results:
            print(f"{rec_id}: {score:.3f}")


if __name__ == "__main__":
    main()
