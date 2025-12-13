# LOG_REVIEW_SUB_SYS - File Organization

**Last Updated**: 2025-12-08

## Directory Structure

All core files for the LOG_REVIEW_SUB_SYS are contained within this directory:

\\\
LOG_REVIEW_SUB_SYS/
├── Core Python Modules
│   ├── logger.py                    # Protocol definition
│   ├── structured_logger.py         # JSON logger implementation
│   ├── audit_logger.py              # Audit trail & patch ledger
│   ├── sync_log_summary.py          # Policy gate
│   ├── export_to_sqlite.py          # SQLite export utility
│   ├── multi_ai_log_miner.py        # Pattern detection (needs implementation)
│   └── extract_patterns_from_logs.py # Pattern extraction (needs implementation)
│
├── PowerShell Scripts
│   ├── aggregate-logs.ps1           # Log aggregation with privacy redaction
│   ├── quick-analysis.ps1           # Quick summary analysis
│   ├── analyze-logs.ps1             # Detailed analysis (partial)
│   ├── export-logs.ps1              # Export to CSV/JSON/SQLite
│   ├── watch-logs.ps1               # Real-time monitoring
│   └── setup-scheduled-task.ps1     # Windows Task Scheduler setup
│
├── Tests
│   ├── test_structured_logger.py    # Unit tests for structured logger
│   ├── test_audit_logger.py         # Unit tests for audit logger
│   └── test_aggregate_script.ps1    # Integration tests
│
├── Configuration & Documentation
│   ├── logging-config.json          # Configuration file
│   ├── README.md                    # Main documentation
│   ├── QUICKSTART.md                # Quick start guide
│   ├── DEVELOPMENT_PROGRESS.md      # Development tracking
│   ├── CONSOLIDATION_REPORT.md      # Consolidation documentation
│   ├── .gitignore                   # Git ignore patterns
│   └── FILE_ORGANIZATION.md         # This file
│
└── Output Directories (auto-created)
    ├── aggregated/                  # Aggregated log files
    ├── exports/                     # Exported files (CSV, JSON, SQLite)
    ├── analysis/                    # Analysis reports
    └── .runs/                       # Audit trail logs
\\\

## External Dependencies (Backward Compatibility)

For backward compatibility with existing code, the following shim files exist outside this directory:

### core/logging/__init__.py
- **Purpose**: Provides import compatibility for code that uses \rom core.logging import StructuredLogger\
- **Function**: Re-exports StructuredLogger from LOG_REVIEW_SUB_SYS
- **Status**: Deprecated but maintained for compatibility

### tests/interfaces/test_event_bus_logger.py
- **Purpose**: Tests Logger protocol compliance across the codebase
- **Function**: Ensures StructuredLogger implements the Logger protocol
- **Status**: Active - tests both core.logger and LOG_REVIEW_SUB_SYS.logger

## Import Guidelines

### Recommended (Direct Import)
\\\python
# Add LOG_REVIEW_SUB_SYS to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "LOG_REVIEW_SUB_SYS"))

from structured_logger import StructuredLogger
from audit_logger import AuditLogger, EventFilters
from logger import Logger
\\\

### Legacy (Via Shim)
\\\python
# Uses shim file - deprecated but supported
from core.logging import StructuredLogger
\\\

## Self-Contained Design

The LOG_REVIEW_SUB_SYS is designed to be **self-contained and portable**:

✅ **All core functionality** is within this directory
✅ **No external dependencies** (except Python stdlib)
✅ **Can be moved** to any location
✅ **Can be packaged** as a standalone tool
✅ **Version controlled** independently

## Installation

To use this subsystem in another project:

\\\ash
# Copy the entire directory
cp -r LOG_REVIEW_SUB_SYS /path/to/your/project/

# Or clone as submodule
git submodule add <repo-url> LOG_REVIEW_SUB_SYS
\\\

## Verification

To verify all files are present:

\\\powershell
Get-ChildItem LOG_REVIEW_SUB_SYS -Recurse | 
    Where-Object { -not \.PSIsContainer } | 
    Measure-Object | Select-Object Count
\\\

Expected: ~30+ files (excluding output directories)

## Notes

- **Output directories** (.runs/, aggregated/, exports/, analysis/) are created on first use
- **Python cache** (__pycache__/) is excluded via .gitignore
- **Test data** in aggregated/ should not be committed (in .gitignore)
- **Exports** in exports/ should not be committed (in .gitignore)
