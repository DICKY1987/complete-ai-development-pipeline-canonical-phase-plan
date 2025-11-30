#!/usr/bin/env python3
"""Compatibility wrapper for the doc_id registry CLI."""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from doc_id.doc_id_registry_cli import main as doc_id_main

    doc_id_main()


if __name__ == "__main__":
    main()
# DOC_LINK: DOC-SCRIPT-SCRIPTS-DOC-ID-REGISTRY-CLI-142
# DOC_LINK: DOC-SCRIPT-SCRIPTS-DOC-ID-REGISTRY-CLI-205
