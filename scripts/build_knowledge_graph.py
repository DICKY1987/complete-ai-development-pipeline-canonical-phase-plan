"""
CLI to build the knowledge graph database.
"""

# DOC_ID: DOC-SCRIPT-BUILD-KG-701

import argparse
from pathlib import Path

from core.knowledge.graph_builder import GraphBuilder


def main():
    parser = argparse.ArgumentParser(description="Build knowledge graph.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument(
        "--db",
        type=Path,
        default=Path(".worktrees/knowledge_graph.db"),
        help="Output SQLite path",
    )
    args = parser.parse_args()

    builder = GraphBuilder(root_path=args.root, db_path=args.db)
    summary = builder.build()
    print(f"Knowledge graph built at {args.db}")
    print(f"Nodes: {summary['nodes']}, Edges: {summary['edges']}")


if __name__ == "__main__":
    main()
