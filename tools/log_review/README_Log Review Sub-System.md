# Log Review Sub-System

**Unified logging, aggregation, and analysis infrastructure for AI development tools**

A comprehensive system for collecting, analyzing, and monitoring logs from multiple AI coding assistants (Claude Code, GitHub Copilot, Codex CLI, Gemini, Aider) with privacy-first design, structured logging, and policy enforcement capabilities.

---

## 🎯 Overview

The Log Review Sub-System provides a centralized solution for managing logs across multiple AI development tools. It consolidates duplicate files, enforces privacy standards, detects usage patterns, and enables data-driven insights into AI-assisted development workflows.

### Key Features

- **Multi-tool log aggregation**: Collect logs from 5+ AI coding assistants into unified format
- **Structured logging**: JSON/JSONL format with timestamps, levels, and contextual metadata
- **Privacy-first**: Built-in redaction for API keys, tokens, passwords, and email addresses
- **Real-time monitoring**: Watch logs as they're created with live updates
- **Policy enforcement**: Sync log gates to prevent merges during high-activity periods
- **Pattern detection**: Auto-discover repetitive user requests and workflows across tools
- **Export formats**: CSV, SQLite, JSON for downstream analysis and integration
- **Audit trail**: JSONL-based event logging with flexible query capabilities
- **Automated scheduling**: Windows Task Scheduler integration for hands-free operation

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [Python API](#-python-api)
- [Privacy & Security](#-privacy--security)
- [Integration Examples](#-integration-examples)
- [Troubleshooting](#-troubleshooting)
- [Advanced Usage](#-advanced-usage)

---

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.11 or higher
- **PowerShell**: 7+ (Windows 11 includes this by default)
- **AI Tools**: At least one of: Claude Code, GitHub Copilot, Codex CLI, Gemini, or Aider

### Installation

```bash
# Clone or navigate to the repository
cd "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\LOG_REVIEW_SUB_SYS"

# Verify Python installation
python --version

# No additional dependencies required for core functionality
```

### Basic Workflow

```powershell
# 1. Configure log paths (edit logging-config.json to match your system)
notepad logging-config.json

# 2. Aggregate logs from all AI tools
.\aggregate-logs.ps1 -StartDate "2025-12-01" -EndDate "2025-12-08"

# 3. Generate analysis report
.\analyze-logs.ps1 -Type summary

# 4. Export to SQLite for querying
.\export-logs.ps1 -Format sqlite
```

**Output**: 
- Aggregated logs: `~/ALL_AI/.../aggregated/aggregated-YYYYMMDD-HHMMSS.jsonl`
- Analysis reports: `~/ALL_AI/.../analysis/{summary,usage-metrics,patterns}.md`
- Database: `~/ALL_AI/.../logs.db`

---

## 🏗️ Architecture

### Component Overview

```
LOG_REVIEW_SUB_SYS/
│
├── Core Python Modules
│   ├── logger.py                      # Protocol definition for structured logging
│   ├── structured_logger.py           # Lightweight JSON logger implementation
│   ├── audit_logger.py                # Audit trail and patch ledger system
│   ├── sync_log_summary.py            # Sync log policy gate (MERGE-002)
│   ├── multi_ai_log_miner.py          # Pattern detection from AI tool logs
│   └── extract_patterns_from_logs.py  # Pattern extraction utilities
│
├── PowerShell Scripts
│   ├── aggregate-logs.ps1             # Multi-tool log aggregation
│   ├── analyze-logs.ps1               # Log analysis and reporting
│   ├── export-logs.ps1                # Export to CSV/SQLite/JSON
│   ├── watch-logs.ps1                 # Real-time log monitoring
│   └── setup-scheduled-task.ps1       # Windows Task Scheduler setup
│
├── Configuration & Documentation
│   ├── logging-config.json            # Central configuration file
│   ├── README.md                      # This file
│   ├── QUICKSTART.md                  # Rapid onboarding guide
│   └── CONSOLIDATION_REPORT.md        # File deduplication history
│
└── Output Directories (auto-created)
    ├── aggregated/                    # Aggregated JSONL logs
    ├── analysis/                      # Analysis reports
    └── .runs/                         # Audit logs
```

### Data Flow Architecture

```
┌─────────────────────────────────────────────────────────┐
│  AI Tools (Claude, Copilot, Codex, Gemini, Aider)      │
│  Generate logs in tool-specific formats                 │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  aggregate-logs.ps1                                     │
│  • Reads from configured log paths                      │
│  • Applies privacy redaction                            │
│  • Normalizes to unified JSONL format                   │
│  • Output: aggregated-TIMESTAMP.jsonl                   │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  analyze-logs.ps1                                       │
│  • Usage metrics (sessions, API calls, duration)        │
│  • Code change patterns (files modified, languages)     │
│  • Error clustering and frequency analysis              │
│  • Output: Markdown reports                             │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  export-logs.ps1                                        │
│  • SQLite database (queryable)                          │
│  • CSV files (spreadsheet-compatible)                   │
│  • JSON (pretty-printed for humans)                     │
└─────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Privacy by Default**: All sensitive data redacted before storage
2. **Append-Only Logs**: JSONL format enables streaming and incremental processing
3. **Tool Agnostic**: Extensible parsers for any AI coding assistant
4. **Minimal Dependencies**: Core functionality requires only Python stdlib and PowerShell
5. **Audit Trail**: Every operation logged for compliance and debugging

---

## 📖 Usage

### Log Aggregation

#### Basic Usage

```powershell
# Aggregate today's logs from all enabled tools
.\aggregate-logs.ps1
```

#### Advanced Options

```powershell
# Specific date range
.\aggregate-logs.ps1 -StartDate "2025-12-01" -EndDate "2025-12-08"

# Select specific tools only
.\aggregate-logs.ps1 -Tools @("claude", "copilot")

# Enable gzip compression for large logs
.\aggregate-logs.ps1 -Compress

# Custom output directory
.\aggregate-logs.ps1 -OutputDir "C:\MyLogs\aggregated"
```

**Output Format** (JSONL):
```json
{"tool":"claude","type":"conversation","timestamp":"2025-12-08T20:24:20.123Z","sessionId":"sess-456","data":{"user":"Fix the bug","assistant":"I'll help..."}}
{"tool":"copilot","type":"suggestion","timestamp":"2025-12-08T20:25:15.789Z","sessionId":"","data":{"file":"main.py","line":42,"suggestion":"Use list comprehension"}}
```

### Log Analysis

#### Summary Report

```powershell
# Generate high-level summary
.\analyze-logs.ps1 -Type summary
```

Output includes:
- Total log entries per tool
- Active session count
- Time range covered
- Error frequency

#### Usage Metrics

```powershell
# Detailed usage statistics
.\analyze-logs.ps1 -Type usage-metrics
```

Metrics provided:
- Sessions per tool
- Average session duration
- API call frequency
- Most active time periods

#### Code Change Patterns

```powershell
# Analyze what code was changed
.\analyze-logs.ps1 -Type code-changes
```

Analysis includes:
- Most frequently modified files
- Languages used
- Refactoring vs. new code ratio

#### Full Report

```powershell
# Generate comprehensive analysis (all types)
.\analyze-logs.ps1 -Type full-report
```

### Real-time Monitoring

```powershell
# Monitor all tools with 2-second refresh
.\watch-logs.ps1

# Monitor specific tool
.\watch-logs.ps1 -Tool claude

# Custom refresh rate
.\watch-logs.ps1 -RefreshSeconds 5
```

Press `Ctrl+C` to stop monitoring.

### Exporting Logs

#### SQLite Database

```powershell
.\export-logs.ps1 -Format sqlite
```

Query example:
```sql
SELECT tool, COUNT(*) as count 
FROM logs 
WHERE timestamp > '2025-12-01' 
GROUP BY tool;
```

#### CSV Export

```powershell
.\export-logs.ps1 -Format csv
```

Opens in Excel, Google Sheets, or any spreadsheet application.

#### Pretty JSON

```powershell
.\export-logs.ps1 -Format json
```

Human-readable JSON with indentation.

### Policy Enforcement

Check sync log for merge safety:

```bash
# Basic check
python sync_log_summary.py /path/to/.sync-log.txt

# With policy thresholds
python sync_log_summary.py /path/to/.sync-log.txt \
    --max-errors 5 \
    --max-pushes-per-hour 10 \
    --time-window 60

# JSON output for CI/CD integration
python sync_log_summary.py /path/to/.sync-log.txt --json
```

**Exit Codes**:
- `0`: Safe to merge (all thresholds passed)
- `1`: Policy violation (errors or activity exceeded limits)
- `2`: Parse error (malformed log file)

**Policy Rules**:
- **max-errors**: Maximum error events allowed
- **max-pushes-per-hour**: Maximum git push operations per hour
- **time-window**: Only consider events within N minutes

### Pattern Mining

Auto-detect repetitive workflows:

```python
from multi_ai_log_miner import MultiAILogMiner
import sqlite3

db = sqlite3.connect('patterns.db')
miner = MultiAILogMiner(db)

# Mine all logs from past 30 days
requests = miner.mine_all_logs()
print(f"Found {len(requests)} user requests")

# Detect patterns (3+ similar occurrences)
patterns = miner.detect_patterns(requests)
print(f"Detected {len(patterns)} patterns")

# Generate pattern files for automation
miner.generate_pattern_files(patterns, output_dir='./patterns')
```

**Output**: Auto-generated pattern templates for common tasks

---

## ⚙️ Configuration

### logging-config.json Structure

```json
{
  "version": "1.0.0",
  
  "logPaths": {
    "claude": {
      "history": "~/.claude/history.jsonl",
      "debug": "~/.claude/debug",
      "enabled": true
    },
    "codex": {
      "history": "~/.codex/history.jsonl",
      "log": "~/.codex/log/codex-tui.log",
      "sessions": "~/.codex/sessions",
      "enabled": true
    },
    "copilot": {
      "logs": "~/.copilot/logs",
      "commandHistory": "~/.copilot/command-history-state.json",
      "enabled": true
    },
    "gemini": {
      "tmp": "~/.gemini/tmp",
      "enabled": true,
      "note": "Gemini has minimal built-in logging"
    },
    "aider": {
      "chatHistory": "~/Documents/aider-config/history/.aider.chat.history.md",
      "llmHistory": "~/Documents/aider-config/history/.aider.llm.history",
      "inputHistory": "~/Documents/aider-config/history/.aider.input.history",
      "enabled": true
    }
  },
  
  "aggregation": {
    "outputDir": "~/ALL_AI/Complete AI Development Pipeline – Canonical Phase Plan/ai-logs-analyzer/aggregated",
    "format": "jsonl",
    "compression": {
      "enabled": false,
      "algorithm": "gzip"
    },
    "rotation": {
      "enabled": true,
      "frequency": "daily",
      "retention": {
        "days": 90,
        "maxSizeMB": 1000
      }
    }
  },
  
  "privacy": {
    "redaction": {
      "enabled": true,
      "patterns": [
        {
          "name": "api_keys",
          "regex": "(sk-[a-zA-Z0-9]{32,}|[a-zA-Z0-9]{32,}-[a-zA-Z0-9]{8,})",
          "replacement": "[REDACTED_API_KEY]"
        },
        {
          "name": "tokens",
          "regex": "(ghp_[a-zA-Z0-9]{36}|gho_[a-zA-Z0-9]{36})",
          "replacement": "[REDACTED_TOKEN]"
        },
        {
          "name": "passwords",
          "regex": "(password|passwd|pwd)\\s*[=:]\\s*['\"]?([^'\"\\s]+)",
          "replacement": "$1=[REDACTED]"
        },
        {
          "name": "email",
          "regex": "\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b",
          "replacement": "[REDACTED_EMAIL]"
        }
      ]
    },
    "encryption": {
      "enabled": false,
      "algorithm": "AES256"
    }
  },
  
  "export": {
    "formats": {
      "csv": {
        "enabled": true,
        "delimiter": ","
      },
      "sqlite": {
        "enabled": true,
        "database": "~/ALL_AI/Complete AI Development Pipeline – Canonical Phase Plan/ai-logs-analyzer/logs.db"
      },
      "json": {
        "enabled": true,
        "pretty": true
      }
    }
  },
  
  "doc_id": "DOC-CONFIG-LOGGING-CONFIG-JSON-001"
}
```

### Customization

#### Add New AI Tool

```json
"my-tool": {
  "logPath": "~/.mytool/logs.jsonl",
  "enabled": true,
  "note": "Custom AI coding assistant"
}
```

#### Add Custom Redaction Pattern

```json
{
  "name": "custom_secret",
  "regex": "SECRET_[A-Z0-9]{32}",
  "replacement": "[REDACTED_SECRET]"
}
```

#### Adjust Retention Policy

```json
"rotation": {
  "enabled": true,
  "frequency": "weekly",  // Change to weekly rotation
  "retention": {
    "days": 180,         // Keep for 6 months
    "maxSizeMB": 5000    // Allow up to 5GB
  }
}
```

### Scheduled Tasks

Automate daily log aggregation:

```powershell
# Setup daily aggregation at 11:00 PM
.\setup-scheduled-task.ps1 -Time "23:00" -Frequency Daily

# Weekly aggregation
.\setup-scheduled-task.ps1 -Time "23:00" -Frequency Weekly
```

Verify scheduled task:
```powershell
Get-ScheduledTask -TaskName "AI-Logs-Aggregation"
```

---

## 🐍 Python API

### Structured Logger

Simple structured logging to stderr in JSON format:

```python
from structured_logger import StructuredLogger

logger = StructuredLogger(name="my-pipeline")

# Basic logging with context
logger.info("Processing started", file_count=42, status="ok")
logger.warning("High memory usage", memory_mb=1024, threshold=800)
logger.error("Failed to process", file="data.csv", reason="Invalid format")
logger.debug("Cache hit", key="user-123", value="cached_data")

# Job-specific events
logger.job_event(job_id="job-123", event="started", worker="worker-01")
logger.job_event(job_id="job-123", event="progress", percent=50)
logger.job_event(job_id="job-123", event="completed", duration=12.5, rows_processed=1000)
```

**Output** (stderr, JSONL format):
```json
{"timestamp":"2025-12-08T20:24:20.123456Z","level":"INFO","logger":"my-pipeline","message":"Processing started","data":{"file_count":42,"status":"ok"}}
{"timestamp":"2025-12-08T20:24:25.789012Z","level":"JOB","logger":"my-pipeline","message":"job_event:job-123:completed","data":{"job_id":"job-123","event":"completed","duration":12.5,"rows_processed":1000}}
```

### Audit Logger

JSONL-based audit trail for compliance and debugging:

```python
from audit_logger import AuditLogger, EventFilters

audit = AuditLogger(log_path=".runs/audit.jsonl")

# Log various events
audit.log_event("task_received", task_id="task-456", data={
    "source": "api",
    "user": "developer-01",
    "priority": "high"
})

audit.log_event("process_started", task_id="task-456", data={
    "worker": "worker-03",
    "estimated_duration": 120
})

audit.log_event("patch_applied", task_id="task-456", data={
    "files": ["main.py", "utils.py"],
    "lines_changed": 42
})

audit.log_event("completed", task_id="task-456", data={
    "actual_duration": 98,
    "success": True
})

# Query events
filters = EventFilters(
    task_id="task-456",
    event_type="patch_applied",
    since="2025-12-08T00:00:00Z"
)
events = audit.query_events(filters)

for event in events:
    print(f"{event.timestamp}: {event.event_type}")
    print(f"  Data: {event.data}")
```

**Supported Event Types**:
- `task_received`, `task_routed`, `process_started`
- `patch_captured`, `patch_validated`, `patch_applied`
- `scope_violation`, `oscillation_detected`, `circuit_breaker_trip`
- `retry_scheduled`, `completed`, `failed`

### Patch Ledger

Version-controlled patch artifact storage:

```python
from audit_logger import PatchLedger, PatchArtifact
from pathlib import Path
import hashlib

ledger = PatchLedger(ledger_path=".ledger/patches")

# Read patch file and compute hash
patch_content = Path("changes.patch").read_text()
diff_hash = hashlib.sha256(patch_content.encode()).hexdigest()

# Create patch artifact
patch = PatchArtifact(
    patch_id="patch-001",
    patch_file=Path("changes.patch"),
    diff_hash=diff_hash,
    files_modified=["main.py", "tests/test_main.py"],
    line_count=42,
    created_at="2025-12-08T20:24:20Z",
    ws_id="ws-789",
    run_id="run-abc123"
)

# Store in ledger
ledger.store_patch(patch)

# Retrieve specific patch
retrieved = ledger.get_patch(patch_id="patch-001")
print(f"Patch modified: {retrieved.files_modified}")

# Get all patches for workstream
history = ledger.get_history(ws_id="ws-789")
for p in history:
    print(f"{p.created_at}: {p.patch_id} - {len(p.files_modified)} files")
```

**Use Cases**:
- Track all code changes made by AI assistants
- Audit trail for compliance
- Rollback capability
- Diff analysis across workstreams

---

## 🔒 Privacy & Security

### Built-in Redaction

The system automatically redacts sensitive data before storage:

| Pattern | Example | Redacted |
|---------|---------|----------|
| OpenAI API keys | `sk-1234567890abcdef...` | `[REDACTED_API_KEY]` |
| GitHub tokens | `ghp_AbCdEf123456...` | `[REDACTED_TOKEN]` |
| Passwords | `password=mysecret` | `password=[REDACTED]` |
| Email addresses | `user@example.com` | `[REDACTED_EMAIL]` |

### Adding Custom Redaction Patterns

Edit `logging-config.json`:

```json
{
  "privacy": {
    "redaction": {
      "enabled": true,
      "patterns": [
        {
          "name": "custom_api_key",
          "regex": "API_KEY_[A-Z0-9]{32}",
          "replacement": "[REDACTED_CUSTOM_KEY]"
        },
        {
          "name": "credit_cards",
          "regex": "\\b\\d{4}[\\s-]?\\d{4}[\\s-]?\\d{4}[\\s-]?\\d{4}\\b",
          "replacement": "[REDACTED_CC]"
        }
      ]
    }
  }
}
```

### Encryption (Optional)

Enable AES-256 encryption for logs at rest:

```json
{
  "privacy": {
    "encryption": {
      "enabled": true,
      "algorithm": "AES256",
      "keyFile": "~/.log-review-keys/encryption.key"
    }
  }
}
```

**Note**: Requires additional setup for key management.

### Best Practices

1. **Never commit logs to version control**: Add `aggregated/`, `analysis/`, `.runs/` to `.gitignore`
2. **Regularly rotate logs**: Enable automatic rotation in config
3. **Limit retention**: Set `retention.days` appropriately for your compliance needs
4. **Review redaction patterns**: Periodically audit logs to ensure sensitive data is properly masked
5. **Encrypt sensitive environments**: Enable encryption for production systems

---

## 🔗 Integration Examples

### CI/CD Pre-merge Check

Prevent merges during high-activity periods:

```yaml
# .github/workflows/merge-check.yml
name: Merge Safety Check
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  check-sync-log:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Check sync log policy
        run: |
          python sync_log_summary.py .sync-log.txt \
            --max-errors 3 \
            --max-pushes-per-hour 15 \
            --time-window 60 \
            --json > policy-check.json
      
      - name: Upload policy check results
        uses: actions/upload-artifact@v3
        with:
          name: policy-check
          path: policy-check.json
```

### Daily Log Report

Automated daily summary email:

```powershell
# Create daily-report.ps1
$today = (Get-Date).ToString("yyyy-MM-dd")

# Aggregate logs
.\aggregate-logs.ps1 -StartDate $today -EndDate $today

# Generate full report
.\analyze-logs.ps1 -Type full-report

# Export to SQLite
.\export-logs.ps1 -Format sqlite

# Email results (requires Send-MailMessage or external SMTP tool)
$reportPath = Resolve-Path "analysis\full-report.md"
Send-MailMessage `
    -To "team@example.com" `
    -From "ai-logs@example.com" `
    -Subject "AI Tool Usage Report - $today" `
    -Body "Daily AI tool usage report attached." `
    -Attachments $reportPath `
    -SmtpServer "smtp.example.com"
```

Schedule with Task Scheduler:
```powershell
.\setup-scheduled-task.ps1 -Time "23:00" -Frequency Daily -ScriptPath "daily-report.ps1"
```

### Claude Code Integration

Use Claude Code to run log analysis:

```
# In Claude Code chat:
"Use the shell MCP tool to run this PowerShell script:

Set-Location 'C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\LOG_REVIEW_SUB_SYS'

# Aggregate today's logs
.\aggregate-logs.ps1

# Generate summary
.\analyze-logs.ps1 -Type summary

# Show me the summary report
Get-Content (Get-ChildItem analysis\summary-*.md | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName

Report what you found."
```

### Prometheus/Grafana Integration

Export metrics for monitoring:

```python
# metrics-exporter.py
from audit_logger import AuditLogger
from prometheus_client import Gauge, generate_latest

audit = AuditLogger()
events = audit.query_events()

# Create metrics
tasks_completed = Gauge('ai_tasks_completed_total', 'Total completed tasks')
tasks_failed = Gauge('ai_tasks_failed_total', 'Total failed tasks')
patches_applied = Gauge('ai_patches_applied_total', 'Total patches applied')

# Count events
tasks_completed.set(len([e for e in events if e.event_type == 'completed']))
tasks_failed.set(len([e for e in events if e.event_type == 'failed']))
patches_applied.set(len([e for e in events if e.event_type == 'patch_applied']))

# Expose metrics
print(generate_latest().decode('utf-8'))
```

---

## 🔧 Troubleshooting

### Issue: No logs found

**Symptom**: `aggregate-logs.ps1` reports 0 entries

**Solutions**:

1. **Check log paths**:
   ```powershell
   # Verify paths in logging-config.json match actual locations
   Test-Path "$HOME\.claude\history.jsonl"
   Test-Path "$HOME\.copilot\logs"
   ```

2. **Enable tools**:
   ```json
   {
     "claude": {
       "enabled": true  // Ensure this is true
     }
   }
   ```

3. **Generate logs first**:
   - Use the AI tools (Claude, Copilot, etc.) to create some logs
   - Wait a few minutes for logs to be written to disk

### Issue: Permission denied

**Symptom**: Cannot read log files

**Solutions**:

Windows:
```powershell
# Run PowerShell as Administrator
Start-Process powershell -Verb RunAs

# Or adjust file permissions
icacls "$HOME\.claude\history.jsonl" /grant "${env:USERNAME}:R"
```

Unix/Linux:
```bash
chmod 644 ~/.claude/history.jsonl
chmod 755 ~/.claude
```

### Issue: Parse errors

**Symptom**: `sync_log_summary.py` fails to parse log

**Solutions**:

1. **Verify log format**:
   ```bash
   # Expected format: YYYY-MM-DD HH:MM:SS [LEVEL] message
   head -5 .sync-log.txt
   ```

2. **Check for corrupted lines**:
   ```python
   # Find lines that don't match expected format
   with open('.sync-log.txt') as f:
       for i, line in enumerate(f, 1):
           parts = line.strip().split(' ', 2)
           if len(parts) < 3:
               print(f"Line {i}: Malformed - {line}")
   ```

3. **Regenerate log**:
   ```bash
   # Backup and recreate
   mv .sync-log.txt .sync-log.txt.bak
   # Re-run operations to generate fresh log
   ```

### Issue: High memory usage

**Symptom**: Aggregation uses too much memory with large logs

**Solutions**:

1. **Use streaming mode**:
   ```powershell
   # Process logs in chunks
   .\aggregate-logs.ps1 -StartDate "2025-12-01" -EndDate "2025-12-02"
   .\aggregate-logs.ps1 -StartDate "2025-12-03" -EndDate "2025-12-04"
   ```

2. **Enable compression**:
   ```powershell
   .\aggregate-logs.ps1 -Compress
   ```

3. **Reduce retention**:
   ```json
   "rotation": {
     "retention": {
       "days": 30,  // Reduce from 90
       "maxSizeMB": 500  // Reduce from 1000
     }
   }
   ```

### Issue: Scheduled task not running

**Symptom**: Logs not aggregated automatically

**Solutions**:

1. **Verify task exists**:
   ```powershell
   Get-ScheduledTask -TaskName "AI-Logs-Aggregation"
   ```

2. **Check task history**:
   ```powershell
   Get-ScheduledTaskInfo -TaskName "AI-Logs-Aggregation"
   ```

3. **Test task manually**:
   ```powershell
   Start-ScheduledTask -TaskName "AI-Logs-Aggregation"
   ```

4. **Review permissions**:
   - Ensure task runs with appropriate user account
   - Check PowerShell execution policy: `Get-ExecutionPolicy`

---

## 🚀 Advanced Usage

### Custom Log Parsers

Add support for additional AI tools:

```powershell
# In aggregate-logs.ps1, add new section after existing tool parsers:

# Process My Custom AI Tool logs
if ($Tools -contains "my-tool") {
    Write-Host "[MyTool] Processing logs..." -ForegroundColor Green
    try {
        if (Test-Path "$HOME\.mytool\logs.jsonl") {
            Get-Content "$HOME\.mytool\logs.jsonl" | ForEach-Object {
                try {
                    $entry = $_ | ConvertFrom-Json
                    Write-AggregatedLog -Tool "my-tool" -Type "event" `
                        -Timestamp ([datetime]$entry.timestamp) `
                        -Data $entry -SessionId $entry.session_id
                } catch {
                    $stats.errors++
                }
            }
        }
    } catch {
        Write-Host "  Error processing MyTool logs: $_" -ForegroundColor Red
        $stats.errors++
    }
}
```

Update `logging-config.json`:
```json
{
  "my-tool": {
    "logPath": "~/.mytool/logs.jsonl",
    "enabled": true,
    "format": "jsonl"
  }
}
```

### Pattern Auto-generation Workflow

Complete workflow for detecting and generating patterns:

```python
#!/usr/bin/env python3
"""Generate automation patterns from AI tool logs."""

from multi_ai_log_miner import MultiAILogMiner
import sqlite3
from pathlib import Path

# Setup
db_path = Path('patterns.db')
db = sqlite3.connect(db_path)
miner = MultiAILogMiner(db, lookback_days=30)

# Mine logs
print("Mining AI tool logs...")
requests = miner.mine_all_logs()
print(f"Found {len(requests)} user requests")

# Detect patterns (3+ similar occurrences)
print("Detecting patterns...")
patterns = miner.detect_patterns(requests)
print(f"Detected {len(patterns)} patterns")

# Display patterns
for i, pattern in enumerate(patterns, 1):
    print(f"\nPattern {i}: {pattern.name}")
    print(f"  Occurrences: {pattern.count}")
    print(f"  Similarity: {pattern.similarity:.1%}")
    print(f"  Template: {pattern.template[:100]}...")

# Generate pattern files
output_dir = Path('./generated-patterns')
output_dir.mkdir(exist_ok=True)

print(f"\nGenerating pattern files to {output_dir}...")
miner.generate_pattern_files(patterns, output_dir=output_dir)

print("Done! Review generated patterns and integrate into automation.")
```

### Custom Analysis Metrics

Extend analysis with custom metrics:

```powershell
# In analyze-logs.ps1, add custom analysis function:

function Get-CustomMetrics {
    param($logs)
    
    # Example: Measure AI response quality based on follow-up questions
    $conversations = $logs | Where-Object { $_.type -eq "conversation" }
    $followUps = @{}
    
    foreach ($conv in $conversations) {
        $sessionId = $conv.sessionId
        if (-not $followUps.ContainsKey($sessionId)) {
            $followUps[$sessionId] = 0
        }
        if ($conv.data.user -match "what|how|why|can you") {
            $followUps[$sessionId]++
        }
    }
    
    # Sessions with fewer follow-ups = better initial responses
    $avgFollowUps = ($followUps.Values | Measure-Object -Average).Average
    
    return @{
        averageFollowUpQuestions = $avgFollowUps
        sessionsWithNoFollowUps = ($followUps.Values | Where-Object { $_ -eq 0 }).Count
        totalConversations = $conversations.Count
    }
}

# Call in main analysis
$customMetrics = Get-CustomMetrics -logs $logs
$customMetrics | ConvertTo-Json | Out-File "$OutputDir\custom-metrics.json"
```

### Log Correlation Analysis

Correlate AI tool usage with code quality metrics:

```python
#!/usr/bin/env python3
"""Correlate AI tool usage with test pass rates."""

import json
from pathlib import Path
from datetime import datetime
import subprocess

def get_ai_tool_usage(date):
    """Get AI tool usage for a specific date."""
    log_file = Path(f"aggregated/aggregated-{date}.jsonl")
    if not log_file.exists():
        return 0
    return sum(1 for _ in open(log_file))

def get_test_pass_rate(date):
    """Get test pass rate for a specific date from git history."""
    result = subprocess.run(
        ['git', 'log', '--since', date, '--until', f'{date} 23:59:59', 
         '--grep', 'tests:', '--oneline'],
        capture_output=True, text=True
    )
    commits = result.stdout.strip().split('\n')
    # Simplified: assume commit message contains pass rate
    pass_count = sum(1 for c in commits if 'passed' in c.lower())
    return pass_count / max(len(commits), 1)

# Analyze correlation
dates = ["2025-12-01", "2025-12-02", "2025-12-03", "2025-12-04"]
data = []

for date in dates:
    usage = get_ai_tool_usage(date)
    pass_rate = get_test_pass_rate(date)
    data.append({"date": date, "ai_usage": usage, "test_pass_rate": pass_rate})
    print(f"{date}: {usage} AI interactions, {pass_rate:.1%} test pass rate")

# Save results
with open('correlation-analysis.json', 'w') as f:
    json.dump(data, f, indent=2)
```

---

## 📚 Related Documentation

- **[QUICKSTART.md](QUICKSTART.md)**: Rapid onboarding guide for Claude Code + Aider integration
- **[CONSOLIDATION_REPORT.md](CONSOLIDATION_REPORT.md)**: File deduplication and cleanup history
- **[logging-config.json](logging-config.json)**: Central configuration reference

---

## 🗺️ Roadmap

### Planned Features

- [ ] **Web Dashboard**: Real-time visualization with charts and graphs
- [ ] **Slack/Discord Notifications**: Alert on anomalies or policy violations
- [ ] **Machine Learning**: Predict workflow needs based on historical patterns
- [ ] **Multi-user Analytics**: Team-wide usage and productivity metrics
- [ ] **Auto-remediation**: Automatically fix common errors detected in logs
- [ ] **Cloud Integration**: Support for cloud-hosted AI tools (Azure OpenAI, AWS Bedrock)
- [ ] **Advanced Querying**: GraphQL or SQL interface for complex queries
- [ ] **Compliance Reports**: GDPR, SOC2, HIPAA-compliant audit trails

### Version History

- **v1.0.0** (2025-12-08): Initial release with core functionality
  - Multi-tool aggregation (5 AI tools)
  - Privacy redaction
  - Policy enforcement
  - Pattern detection
  - Export to CSV/SQLite/JSON

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/log-review-sub-sys.git
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make your changes**
   - Add tests for new functionality
   - Update documentation as needed
   - Follow existing code style

4. **Test thoroughly**
   ```powershell
   # Run aggregation
   .\aggregate-logs.ps1
   
   # Run analysis
   .\analyze-logs.ps1 -Type full-report
   
   # Verify output
   ```

5. **Commit with descriptive message**
   ```bash
   git commit -m "feat: Add support for Cursor AI tool"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

7. **Open a Pull Request**
   - Describe the changes
   - Reference related issues
   - Include screenshots if applicable

### Code Style

- **PowerShell**: Follow [PowerShell Best Practices](https://poshcode.gitbook.io/powershell-practice-and-style/)
- **Python**: Follow [PEP 8](https://pep8.org/)
- **JSON**: Use 2-space indentation
- **Documentation**: Use Markdown with proper headings

---

## 📄 License

MIT License - See LICENSE file for details.

Copyright (c) 2025 AI Development Pipeline Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

---

## 📞 Support

### Getting Help

- **Documentation**: Start with this README and [QUICKSTART.md](QUICKSTART.md)
- **Issues**: File bug reports or feature requests on GitHub
- **Discussions**: Ask questions in GitHub Discussions
- **Email**: Contact maintainers at ai-logs-support@example.com

### Reporting Bugs

Include the following information:
1. Operating system and version
2. PowerShell version (`$PSVersionTable.PSVersion`)
3. Python version (`python --version`)
4. Steps to reproduce
5. Expected vs. actual behavior
6. Relevant log snippets (redacted for privacy)

### Security Issues

Report security vulnerabilities privately to security@example.com.
Do not open public issues for security concerns.

---

## 🙏 Acknowledgments

- **Inspired by**: ELK Stack, Splunk, and modern observability platforms
- **Built with**: PowerShell 7, Python 3.11, and open-source libraries
- **Special thanks**: Contributors to the AI Development Pipeline project

---

**Document ID**: DOC-LOG-REVIEW-SUB-SYS-README-001  
**Last Updated**: 2025-12-08  
**Version**: 1.0.0  
**Maintainer**: AI Development Pipeline Team
