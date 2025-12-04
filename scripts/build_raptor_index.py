"""
CLI to build RAPTOR hierarchical index.
"""

# DOC_ID: DOC-SCRIPT-BUILD-RAPTOR-703

import argparse
from pathlib import Path

from core.ast.repository_mapper import RepositoryMapper
from core.indexing.raptor import RaptorIndexer
from core.indexing.summarizer import Summarizer


def main():
    parser = argparse.ArgumentParser(description="Build RAPTOR index.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(".worktrees/raptor_index"),
        help="Output directory for RAPTOR JSONL",
    )
    args = parser.parse_args()

    repo_map = RepositoryMapper(args.root).generate_map()
    idx = RaptorIndexer(Summarizer(max_len=512), output_dir=args.out)
    counts = idx.build(repo_map)
    print(f"RAPTOR index written to {args.out}")
    print(counts)


if __name__ == "__main__":
    main()
