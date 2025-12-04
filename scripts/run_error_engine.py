# DOC_LINK: DOC-SCRIPT-SCRIPTS-RUN-ERROR-ENGINE-229
# DOC_LINK: DOC-SCRIPT-SCRIPTS-RUN-ERROR-ENGINE-166
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure repository root and 'src' are importable when launched from scripts/
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "src"))
from typing import List

from modules.error_engine.m010004_file_hash_cache import FileHashCache
from modules.error_engine.m010004_pipeline_engine import PipelineEngine
from modules.error_engine.m010004_plugin_manager import PluginManager


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the deterministic error pipeline on files."
    )
    parser.add_argument("files", nargs="+", help="Files to validate")
    parser.add_argument(
        "--cache",
        default=str(Path(".state") / "validation_cache.json"),
        help="Path to hash cache JSON",
    )
    args = parser.parse_args()

    cache_path = Path(args.cache)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache = FileHashCache(cache_path)
    cache.load()

    pm = PluginManager()
    engine = PipelineEngine(pm, cache)

    exit_code = 0
    for f in args.files:
        p = Path(f)
        report = engine.process_file(p)
        print(
            f"{p}: {report.status} | errors={report.summary.total_errors if report.summary else 0} warnings={report.summary.total_warnings if report.summary else 0}"
        )
        if report.summary and report.summary.total_errors:
            exit_code = 1

    cache.save()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
