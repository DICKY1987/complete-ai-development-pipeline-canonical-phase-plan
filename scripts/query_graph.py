"""
CLI to query the knowledge graph (GraphRAG).
"""

# DOC_ID: DOC-SCRIPT-QUERY-KG-702

import argparse
from pathlib import Path

from core.knowledge.knowledge_graph import KnowledgeGraph
from core.knowledge.query_engine import QueryEngine


def main():
    parser = argparse.ArgumentParser(description="Query knowledge graph.")
    parser.add_argument(
        "--db",
        type=Path,
        default=Path(".worktrees/knowledge_graph.db"),
        help="SQLite path",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    callers = subparsers.add_parser("callers", help="Find callers/importers of module")
    callers.add_argument("name", help="Module or symbol name")

    deps = subparsers.add_parser("dependents", help="Dependency chain")
    deps.add_argument("name", help="Module name")
    deps.add_argument("--depth", type=int, default=3, help="Traversal depth")

    usages = subparsers.add_parser("usages", help="Find usages by prefix match")
    usages.add_argument("prefix", help="Prefix to match")

    args = parser.parse_args()

    with KnowledgeGraph(args.db) as kg:
        qe = QueryEngine(kg)
        if args.command == "callers":
            results = qe.callers_of(args.name)
        elif args.command == "dependents":
            results = qe.dependents_chain(args.name, depth=args.depth)
        else:
            results = qe.usages_of(args.prefix)

    print(results)


if __name__ == "__main__":
    main()
