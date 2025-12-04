#!/usr/bin/env python3
"""
Rank modules by importance using PageRank algorithm.

Usage:
    python scripts/rank_modules.py
    python scripts/rank_modules.py --top 20
    python scripts/rank_modules.py --metric in_degree
"""
# DOC_ID: DOC-SCRIPTS-RANK-MODULES-209

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.ast.centrality_analyzer import CentralityAnalyzer
from core.ast.import_graph import ImportGraph


def main():
    parser = argparse.ArgumentParser(description="Rank modules by importance")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("MODULE_IMPORTANCE_RANKING.yaml"),
        help="Output file path (default: MODULE_IMPORTANCE_RANKING.yaml)",
    )
    parser.add_argument(
        "--metric",
        choices=["pagerank", "in_degree", "out_degree", "total_degree"],
        default="pagerank",
        help="Ranking metric (default: pagerank)",
    )
    parser.add_argument(
        "--top",
        "-n",
        type=int,
        default=50,
        help="Number of top modules to show (default: 50)",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root path (default: current directory)",
    )

    args = parser.parse_args()

    print(f"Analyzing module importance for: {args.root}")
    print(f"Metric: {args.metric}")
    print(f"Building import graph...")

    # Build import graph
    graph = ImportGraph(args.root)
    graph.build_graph()

    print(f"Found {len(graph.get_all_modules())} modules")
    print(f"Computing {args.metric} scores...")

    # Analyze centrality
    analyzer = CentralityAnalyzer(graph)
    analyzer.export_ranking(args.output, metric=args.metric, top_n=args.top)

    # Show top modules
    ranked = analyzer.rank_modules(args.metric, top_n=10)
    print(f"\nTop 10 modules by {args.metric}:")
    for i, (module, score) in enumerate(ranked, 1):
        print(f"  {i}. {module}: {score:.6f}")

    print("\nDone!")


if __name__ == "__main__":
    main()
