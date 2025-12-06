---
doc_id: DOC-GUIDE-README-README-003
---

# AI Tools Log Aggregation & Analysis

Centralized system for capturing, aggregating, and analyzing logs from multiple AI coding assistants.

## Overview

This directory provides tools to aggregate logs from:
- Claude Code (`.claude/`)
- Codex (`.codex/`)
- GitHub Copilot (`.copilot/`)
- Google Gemini (`.gemini/`)
- Aider (`.aider/` and `Documents/aider-config/`)

## Directory Structure

```
ai-logs-analyzer/
├── aggregated/          # Aggregated logs by date
├── analysis/            # Analysis results and reports
├── scripts/             # Collection and analysis scripts
├── config/              # Configuration files
└── README.md            # This file
```

## Quick Start

### 1. Enable Enhanced Logging

Each tool has different logging capabilities:

#### Claude Code
Already logging to:
- `~/.claude/history.jsonl` - Full conversation history
- `~/.claude/debug/*.txt` - Per-session debug logs

#### Codex
Already logging to:
- `~/.codex/history.jsonl` - Conversation history
- `~/.codex/log/codex-tui.log` - Application log

#### Copilot
Already logging to:
- `~/.copilot/logs/session-*.log` - Per-session logs
- `~/.copilot/command-history-state.json` - Command history

#### Aider
Already logging to:
- `~/Documents/aider-config/history/.aider.chat.history.md` - Chat history
- `~/Documents/aider-config/history/.aider.llm.history` - LLM interactions
- `~/Documents/aider-config/history/.aider.input.history` - User inputs

#### Gemini
Needs configuration - Run: `./scripts/enable-gemini-logging.ps1`

### 2. Aggregate Logs

```powershell
# Collect all logs for today
./scripts/aggregate-logs.ps1

# Collect logs for specific date range
./scripts/aggregate-logs.ps1 -StartDate "2025-11-01" -EndDate "2025-11-24"

# Collect logs for specific tools only
./scripts/aggregate-logs.ps1 -Tools "claude","aider"
```

### 3. Analyze Logs

```powershell
# Generate daily summary
./scripts/analyze-logs.ps1 -Type summary

# Extract code changes
./scripts/analyze-logs.ps1 -Type code-changes

# Analyze conversation patterns
./scripts/analyze-logs.ps1 -Type patterns

# Generate full report
./scripts/analyze-logs.ps1 -Type full-report
```

## Analysis Capabilities

### Usage Metrics
- Session count by tool
- Total tokens/messages per tool
- Time spent per tool
- Activity patterns (hourly/daily)

### Content Analysis
- Code changes tracking
- Common prompts/patterns
- Error rates and types
- Feature usage statistics

### Comparative Analysis
- Tool effectiveness comparison
- Response quality metrics
- Task completion rates

## Log Rotation

Logs are automatically rotated:
- Daily aggregation at midnight
- Weekly compression of old logs
- Monthly archival to `aggregated/archive/`

## Privacy & Security

**Important**: These logs may contain:
- API keys and credentials
- Private code snippets
- Personal information

**Best Practices**:
- Never commit logs to git (already in `.gitignore`)
- Encrypt sensitive logs: `./scripts/encrypt-logs.ps1`
- Regularly audit and clean old logs
- Use `./scripts/redact-sensitive.ps1` before sharing

## Configuration

Edit `config/logging-config.json` to customize:
- Log retention periods
- Analysis parameters
- Redaction patterns
- Export formats

## Troubleshooting

### Logs not appearing
- Check tool is actually running
- Verify log paths in `config/logging-config.json`
- Check file permissions
- Review `aggregated/errors.log`

### Large log files
- Use `./scripts/compress-logs.ps1`
- Adjust retention period in config
- Enable sampling for verbose logs

### Analysis failing
- Ensure Python 3.8+ is installed
- Run `pip install -r requirements.txt`
- Check `analysis/error.log`

## Advanced Usage

### Real-time Log Monitoring
```powershell
# Watch all AI tool logs in real-time
./scripts/watch-logs.ps1
```

### Export to External Tools
```powershell
# Export to CSV for Excel/Power BI
./scripts/export-logs.ps1 -Format csv

# Export to JSON for custom analysis
./scripts/export-logs.ps1 -Format json

# Export to SQLite database
./scripts/export-logs.ps1 -Format sqlite
```

### Custom Analysis Scripts
See `scripts/examples/` for templates to create custom analysis scripts.

## Maintenance

### Weekly Tasks
- Review aggregated logs
- Run analysis reports
- Clean up old debug files

### Monthly Tasks
- Archive old logs
- Review storage usage
- Update analysis queries
- Backup important logs

## Related Documentation
- [Log Format Specifications](./docs/log-formats.md)
- [Analysis Query Reference](./docs/queries.md)
- [Privacy Guidelines](./docs/privacy.md)
