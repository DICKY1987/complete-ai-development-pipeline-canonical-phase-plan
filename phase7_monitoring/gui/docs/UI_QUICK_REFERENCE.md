---
doc_id: DOC-GUIDE-UI-QUICK-REFERENCE-1430
---

# UI Quick Reference Guide

This guide provides concrete examples and common usage patterns for the command-line interface.

## Quick Command Reference

### Most Commonly Used Commands

```bash
# Quick health check
python -m core.ui_cli dashboard

# What's running right now?
python -m core.ui_cli workstreams --status running

# Any errors?
python -m core.ui_cli errors --severity error

# Tool health check
python -m core.ui_cli tools --summary
```

## Command Examples with Sample Output

### 1. Dashboard - System Overview

**Command:**
```bash
python -m core.ui_cli dashboard
```

**Sample Output:**
```
PIPELINE DASHBOARD
============================================================

Workstreams:
  Running:    2
  Queued:     4
  Completed:  18
  Failed:     0

Files:
  Intake:           3
  Classified:       8
  In Flight:        2
  Awaiting Review:  1
  Committed:        67
  Quarantined:      0

Throughput:
  Files/hour:  8.5
  Jobs/hour:   2.1

Errors:
  Errors/hour: 0.3
  Top errors:
    - config: 2
    - timeout: 1
```

**JSON Version:**
```bash
python -m core.ui_cli dashboard --json
```

```json
{
  "workstreams_running": 2,
  "workstreams_queued": 4,
  "workstreams_completed": 18,
  "workstreams_failed": 0,
  "files_intake": 3,
  "files_classified": 8,
  "files_in_flight": 2,
  "files_awaiting_review": 1,
  "files_committed": 67,
  "files_quarantined": 0,
  "files_per_hour": 8.5,
  "errors_per_hour": 0.3,
  "top_error_types": [
    ["config", 2],
    ["timeout", 1]
  ]
}
```

### 2. Files - Track File Processing

**Command: List all files being processed**
```bash
python -m core.ui_cli files --state processing
```

**Sample Output:**
```
File ID       Path                                     State       Workstream    Last Processed
-------------------------------------------------------------------------------------------------------
file-a1b2c3d  src/core/engine/orchestrator.py          processing  ws-refact01   2025-11-22 14:45
file-e4f5g6h  tests/test_orchestrator.py               processing  ws-refact01   2025-11-22 14:46

Total: 2 files
```

**Command: Find files that failed**
```bash
python -m core.ui_cli files --state quarantined
```

**Sample Output:**
```
File ID       Path                                     State        Workstream    Last Processed
-------------------------------------------------------------------------------------------------------
file-x9y8z7w  src/broken/module.py                     quarantined  ws-config02   2025-11-22 13:30

Total: 1 files
```

**Command: All files in a specific workstream**
```bash
python -m core.ui_cli files --workstream-id ws-refact01 --limit 50
```

**Command: Files modified by a specific tool**
```bash
python -m core.ui_cli files --tool-id aider --limit 20
```

### 3. File Counts - State Distribution

**Command:**
```bash
python -m core.ui_cli file-counts
```

**Sample Output:**
```
State               Count
--------------------------
committed           67
classified          8
processing          2
intake              3
awaiting_review     1
quarantined         0
```

**Command: For a specific run**
```bash
python -m core.ui_cli file-counts --run-id run-2025-11-22-001
```

### 4. Workstreams - What's Happening

**Command: See all active workstreams**
```bash
python -m core.ui_cli workstreams --status running
```

**Sample Output:**
```
Workstream ID  Status   Files    Duration  Started
----------------------------------------------------
ws-refact01    running  8/10     45.2s     2025-11-22 14:45
ws-config02    running  3/5      12.8s     2025-11-22 14:50

Total: 2 workstreams
```

**Command: See completed workstreams**
```bash
python -m core.ui_cli workstreams --status completed --limit 10
```

**Sample Output:**
```
Workstream ID  Status     Files    Duration  Started
------------------------------------------------------
ws-tests03     completed  12/12    234.5s    2025-11-22 13:00
ws-docs04      completed  5/5      89.3s     2025-11-22 13:30
ws-refact00    completed  20/20    456.7s    2025-11-22 12:00

Total: 3 workstreams
```

**Command: See failed workstreams**
```bash
python -m core.ui_cli workstreams --status failed
```

**Command: All workstreams for a run**
```bash
python -m core.ui_cli workstreams --run-id run-2025-11-22-001 --limit 100
```

### 5. Workstream Counts - Status Summary

**Command:**
```bash
python -m core.ui_cli workstream-counts
```

**Sample Output:**
```
Status      Count
-------------------
completed   18
running     2
queued      4
failed      0
pending     1
```

### 6. Errors - Problem Tracking

**Command: Show critical errors**
```bash
python -m core.ui_cli errors --severity critical
```

**Sample Output:**
```
Error ID      Severity  Category  Message                                           Count
-------------------------------------------------------------------------------------------
err-crit001   critical  network   Connection to API endpoint failed after 5 retries  1

Total: 1 errors
```

**Command: Show all errors**
```bash
python -m core.ui_cli errors --severity error
```

**Sample Output:**
```
Error ID      Severity  Category  Message                                           Count
-------------------------------------------------------------------------------------------
err-syn001    error     syntax    SyntaxError at line 42: unexpected token          2
err-cfg002    error     config    Missing required environment variable OLLAMA_AP   1

Total: 2 errors
```

**Command: Filter by category**
```bash
python -m core.ui_cli errors --category syntax
```

```bash
python -m core.ui_cli errors --category config
```

**Command: Errors for a specific workstream**
```bash
python -m core.ui_cli errors --workstream-id ws-refact01
```

**Command: Errors from a specific tool**
```bash
python -m core.ui_cli errors --tool-id aider --limit 10
```

**Command: Errors in a specific run**
```bash
python -m core.ui_cli errors --run-id run-2025-11-22-001
```

### 7. Tools - Health Monitoring

**Command: Summary of all tools**
```bash
python -m core.ui_cli tools --summary
```

**Sample Output:**
```
Tool          Status     Success Rate  P95 Latency
--------------------------------------------------
Aider         healthy    96.8%         8.45s
Codex         healthy    98.2%         12.32s
Tests         degraded   78.5%         45.67s
Git           healthy    99.1%         2.15s
```

**Command: Full details for all tools**
```bash
python -m core.ui_cli tools
```

**Sample Output:**
```
Tool ID  Name    Status     Success Rate  Requests (5m)
---------------------------------------------------------
aider    Aider   healthy    96.8%         15
codex    Codex   healthy    98.2%         8
tests    Tests   degraded   78.5%         12
git      Git     healthy    99.1%         45

Total: 4 tools
```

**Command: Detailed info for specific tool**
```bash
python -m core.ui_cli tools --tool-id aider
```

**Sample Output:**
```
Tool: Aider
Status: healthy
Success Rate: 96.8%
P95 Latency: 8.45s
Requests (5m/15m/60m): 15/42/156
```

## Common Workflows

### Morning Check-in

```bash
# 1. Check overall health
python -m core.ui_cli dashboard

# 2. Any failures overnight?
python -m core.ui_cli errors --severity critical
python -m core.ui_cli errors --severity error

# 3. What's in quarantine?
python -m core.ui_cli files --state quarantined

# 4. Tool health
python -m core.ui_cli tools --summary
```

### Debugging a Failed Workstream

```bash
# 1. Find failed workstreams
python -m core.ui_cli workstreams --status failed

# 2. Get details for specific workstream (using ID from above)
python -m core.ui_cli files --workstream-id ws-refact01

# 3. Check errors for that workstream
python -m core.ui_cli errors --workstream-id ws-refact01

# 4. See which tool had issues
python -m core.ui_cli files --workstream-id ws-refact01 --state quarantined
```

### Monitoring Active Work

```bash
# Watch what's currently running (run periodically)
watch -n 5 'python -m core.ui_cli workstreams --status running'

# Or create a simple monitoring script:
#!/bin/bash
while true; do
    clear
    echo "=== Active Workstreams ==="
    python -m core.ui_cli workstreams --status running
    echo ""
    echo "=== Processing Files ==="
    python -m core.ui_cli files --state processing --limit 10
    echo ""
    echo "=== Recent Errors ==="
    python -m core.ui_cli errors --limit 5
    sleep 5
done
```

### Performance Analysis

```bash
# Export all data to JSON
python -m core.ui_cli dashboard --json > data/dashboard-$(date +%Y%m%d-%H%M).json
python -m core.ui_cli tools --json > data/tools-$(date +%Y%m%d-%H%M).json
python -m core.ui_cli workstreams --json > data/workstreams-$(date +%Y%m%d-%H%M).json

# Analyze with jq
cat data/tools-*.json | jq '.[].metrics.success_rate' | sort -n

# Find slowest tools
cat data/tools-*.json | jq '.[] | {tool: .display_name, latency: .metrics.p95_latency}' | jq -s 'sort_by(.latency) | reverse'
```

### Finding Specific Files

```bash
# Files committed today (requires processing JSON)
python -m core.ui_cli files --state committed --json | \
  jq '.[] | select(.last_processed | startswith("2025-11-22"))'

# Files processed by Aider
python -m core.ui_cli files --tool-id aider --limit 50

# Files in a specific workstream
python -m core.ui_cli files --workstream-id ws-refact01
```

## Advanced Usage

### Combining with Other Tools

**Using jq for filtering:**
```bash
# Only show workstreams that took longer than 100s
python -m core.ui_cli workstreams --json | \
  jq '.[] | select(.total_duration_sec > 100)'

# Count files by state
python -m core.ui_cli files --json | \
  jq 'group_by(.current_state) | map({state: .[0].current_state, count: length})'

# Show errors with more than 3 occurrences
python -m core.ui_cli errors --json | \
  jq '.[] | select(.occurrence_count > 3)'
```

**Creating reports:**
```bash
# Daily summary report
cat > daily_report.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y-%m-%d)
REPORT="reports/daily-$DATE.txt"

echo "Daily Pipeline Report - $DATE" > $REPORT
echo "======================================" >> $REPORT
echo "" >> $REPORT

echo "## Dashboard" >> $REPORT
python -m core.ui_cli dashboard >> $REPORT
echo "" >> $REPORT

echo "## Errors" >> $REPORT
python -m core.ui_cli errors --severity error >> $REPORT
python -m core.ui_cli errors --severity critical >> $REPORT
echo "" >> $REPORT

echo "## Tool Health" >> $REPORT
python -m core.ui_cli tools --summary >> $REPORT

cat $REPORT
EOF

chmod +x daily_report.sh
./daily_report.sh
```

**Alerting on issues:**
```bash
# Check for critical errors and send alert
cat > check_health.sh << 'EOF'
#!/bin/bash

CRITICAL_COUNT=$(python -m core.ui_cli errors --severity critical --json | jq '. | length')

if [ "$CRITICAL_COUNT" -gt 0 ]; then
    echo "ALERT: $CRITICAL_COUNT critical errors detected!"
    python -m core.ui_cli errors --severity critical
    # Send email, Slack notification, etc.
fi

# Check for degraded tools
DEGRADED=$(python -m core.ui_cli tools --json | jq '.[] | select(.status == "degraded") | .display_name' | wc -l)

if [ "$DEGRADED" -gt 0 ]; then
    echo "WARNING: $DEGRADED tools are degraded"
    python -m core.ui_cli tools --summary
fi
EOF

chmod +x check_health.sh
# Run via cron every 5 minutes
# */5 * * * * /path/to/check_health.sh
```

### Pagination and Limits

```bash
# Get first 10 files
python -m core.ui_cli files --limit 10

# Get more results
python -m core.ui_cli files --limit 100

# Get all workstreams (be careful with large datasets)
python -m core.ui_cli workstreams --limit 9999
```

### Environment Variables

```bash
# Set custom database path
export PIPELINE_DB_PATH=/custom/path/to/pipeline.db
python -m core.ui_cli dashboard

# Or use --db-path flag
python -m core.ui_cli dashboard --db-path /custom/path/to/pipeline.db
```

## Troubleshooting

### "No such table" Error

**Problem:**
```
Error: no such table: workstreams
```

**Solution:**
The database hasn't been initialized. The pipeline must run at least once to create the database schema and populate data.

```bash
# Check if database exists
ls -la .worktrees/pipeline_state.db

# If missing, run a workstream or initialize the database
# (specific command depends on your setup)
```

### Empty Results

**Problem:**
Commands return no data or "Total: 0"

**Reasons:**
1. Database is empty (no pipeline runs yet)
2. Filters are too restrictive
3. Wrong database path

**Solutions:**
```bash
# Check without filters
python -m core.ui_cli files

# Verify database has data
python -m core.ui_cli dashboard

# Check database path
python -m core.ui_cli dashboard --db-path .worktrees/pipeline_state.db
```

### JSON Parsing Errors

**Problem:**
JSON output is malformed or truncated

**Solution:**
```bash
# Increase limit if results are being truncated
python -m core.ui_cli files --json --limit 1000

# Validate JSON output
python -m core.ui_cli dashboard --json | jq '.'

# Save to file first, then process
python -m core.ui_cli dashboard --json > dashboard.json
jq '.' dashboard.json
```

## Reference Tables

### File States
| State | Description | Typical Next State |
|-------|-------------|-------------------|
| intake | File discovered | classified |
| classified | Role identified | processing |
| processing | Being worked on | in_flight, quarantined |
| in_flight | Active processing | awaiting_review, committed |
| awaiting_review | Human review needed | committed, quarantined |
| committed | Successfully saved | locked |
| quarantined | Failed, needs attention | processing (retry) |
| locked | Complete, immutable | archived |
| archived | Moved to archive | - |
| deleted | Removed | - |

### Workstream Statuses
| Status | Description | Terminal? |
|--------|-------------|-----------|
| pending | Not started | No |
| queued | Waiting for resources | No |
| running | Active execution | No |
| paused | Temporarily stopped | No |
| completed | Successfully finished | Yes |
| failed | Encountered errors | Yes |
| cancelled | User cancelled | Yes |
| blocked | Waiting on dependencies | No |

### Error Severities
| Severity | Impact | Action Required |
|----------|--------|-----------------|
| warning | Minor issues | Monitor |
| error | Serious problems | Investigate |
| critical | Severe issues | Immediate attention |

### Error Categories
| Category | Examples |
|----------|----------|
| syntax | Code syntax errors, parsing failures |
| config | Missing config, invalid settings |
| network | Connection failures, timeouts |
| timeout | Operation timeouts |
| permission | File access, system permissions |
| dependency | Missing packages, version conflicts |
| validation | Input validation, schema errors |
| resource | Memory, disk space exhaustion |
| tool | Tool-specific failures |
| integration | Inter-tool communication issues |
| unknown | Uncategorized errors |

### Tool Statuses
| Status | Meaning | Action |
|--------|---------|--------|
| healthy | Operating normally | None |
| degraded | Issues but functional | Monitor, investigate if persists |
| unreachable | Cannot connect | Check tool availability |
| circuit_open | Too many failures | Wait for auto-recovery or manual intervention |
| unknown | Cannot determine | Check tool configuration |

## Tips and Best Practices

1. **Use JSON for automation:** Always use `--json` flag when scripting
2. **Start broad, then filter:** Run without filters first to see what data exists
3. **Monitor regularly:** Set up cron jobs or scheduled tasks for health checks
4. **Export historical data:** Save JSON outputs periodically for trend analysis
5. **Combine with jq:** Use jq for powerful JSON filtering and transformation
6. **Use meaningful limits:** Default limit is 100, adjust based on your needs
7. **Check tool health first:** If workstreams fail, check tool status
8. **Review quarantined files:** Regular reviews prevent backlog
9. **Export before cleanup:** Save data before any cleanup operations
10. **Document your queries:** Keep a notebook of useful query patterns

## Next Steps

- See `docs/CURRENT_USER_INTERFACE.md` for detailed interface description
- See `docs/UI_FLOW_DIAGRAM.md` for visual workflow diagrams
- See `docs/UI_IMPLEMENTATION_SUMMARY.md` for technical implementation details
- See `gui/` directory for future GUI design documents
