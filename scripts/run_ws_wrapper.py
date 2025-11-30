#!/usr/bin/env python
"""Wrapper to run workstreams with proper Python path setup."""
import sys
from pathlib import Path

# Add repo root to Python path
repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root))

# Import and run the actual script
from scripts.run_workstream import main

if __name__ == "__main__":
    sys.exit(main())
# DOC_LINK: DOC-SCRIPT-SCRIPTS-RUN-WS-WRAPPER-168
# DOC_LINK: DOC-SCRIPT-SCRIPTS-RUN-WS-WRAPPER-231
