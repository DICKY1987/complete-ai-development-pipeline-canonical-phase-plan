# Log Review Sub-System

This directory contains a comprehensive logging and log analysis system for the AI development pipeline.

## Contents

### Documentation
- `README_Log Review Sub-System.md` - Main documentation for the log review system
- `CONSOLIDATION_REPORT.md` - Report on log consolidation activities
- `DEVELOPMENT_PROGRESS.md` - Development progress tracking
- `FILE_ORGANIZATION.md` - File organization documentation
- `QUICKSTART.md` - Quick start guide for the log review system

### Configuration
- `logging-config.json` - Logging configuration settings
- `.gitignore` - Git ignore rules for log files

### Python Modules
- `logger.py` - Core logging module
- `structured_logger.py` - Structured logging implementation
- `audit_logger.py` - Audit trail logging
- `multi_ai_log_miner.py` - Multi-AI log mining and analysis
- `export_to_sqlite.py` - SQLite export functionality
- `extract_patterns_from_logs.py` - Pattern extraction from logs
- `sync_log_summary.py` - Log summary synchronization

### PowerShell Scripts
- `aggregate-logs.ps1` - Aggregate logs from multiple sources
- `analyze-logs.ps1` - Analyze log files
- `export-logs.ps1` - Export logs in various formats
- `quick-analysis.ps1` - Quick log analysis
- `run-all-tests.ps1` - Run all log system tests
- `setup-scheduled-task.ps1` - Setup scheduled log processing
- `watch-logs.ps1` - Watch logs in real-time

### Subdirectories
- `tests/` - Test suite for the log review system
- `exports/` - Exported log data and reports

## Purpose

This comprehensive log review sub-system provides:
- Structured logging capabilities across the pipeline
- Log aggregation from multiple sources
- Pattern detection and analysis
- Audit trail generation
- Real-time log monitoring
- Export and reporting functionality

## Usage

1. **Quick Start**: Refer to `QUICKSTART.md` for initial setup
2. **Configuration**: Edit `logging-config.json` to configure logging behavior
3. **Analysis**: Use PowerShell scripts for various log analysis tasks
4. **Monitoring**: Run `watch-logs.ps1` for real-time log monitoring

## Integration

The log review system integrates with other pipeline components to provide comprehensive visibility into system operations, errors, and performance.
