---
doc_id: DOC-GUIDE-QUICKSTART-218
---

# Quick Start Guide - AI Logs Analyzer

## Initial Setup (One-Time)

1. **Verify log locations exist**:
   ```powershell
   # Check which AI tools are actively logging
   ls ~/.claude/history.jsonl     # Claude Code
   ls ~/.codex/history.jsonl      # Codex
   ls ~/.copilot/logs/            # Copilot
   ls ~/.aider/                   # Aider
   ls ~/Documents/aider-config/history/  # Aider history
   ```

2. **Create output directories**:
   ```powershell
   cd ~/ALL_AI/ai-logs-analyzer
   mkdir aggregated, analysis -Force
   ```

3. **Test the aggregation script**:
   ```powershell
   ./scripts/aggregate-logs.ps1
   ```

## Daily Usage

### Collect Today's Logs
```powershell
cd ~/ALL_AI/ai-logs-analyzer
./scripts/aggregate-logs.ps1
```

### Generate Summary Report
```powershell
./scripts/analyze-logs.ps1 -Type summary
```

### Watch Logs in Real-Time
```powershell
./scripts/watch-logs.ps1
```

## Common Workflows

### Weekly Review
```powershell
# Aggregate last 7 days
$startDate = (Get-Date).AddDays(-7).ToString("yyyy-MM-dd")
$endDate = (Get-Date).ToString("yyyy-MM-dd")

./scripts/aggregate-logs.ps1 -StartDate $startDate -EndDate $endDate

# Generate full report
./scripts/analyze-logs.ps1 -Type full-report
```

### Compare Tool Usage
```powershell
./scripts/analyze-logs.ps1 -Type usage-metrics
```

### Analyze Activity Patterns
```powershell
./scripts/analyze-logs.ps1 -Type patterns
```

### Track Code Changes
```powershell
./scripts/analyze-logs.ps1 -Type code-changes
```

## Tips

- **Large Logs**: Use `-Compress` flag to save disk space
  ```powershell
  ./scripts/aggregate-logs.ps1 -Compress
  ```

- **Specific Tools Only**:
  ```powershell
  ./scripts/aggregate-logs.ps1 -Tools "claude","aider"
  ```

- **Custom Date Range**:
  ```powershell
  ./scripts/aggregate-logs.ps1 -StartDate "2025-11-01" -EndDate "2025-11-23"
  ```

## Troubleshooting

### "No log file found"
Run `aggregate-logs.ps1` first to collect logs.

### "Permission denied"
Run PowerShell as Administrator or check file permissions.

### Empty analysis
Check that the AI tools have actually been used and generated logs.

## Next Steps

- Set up scheduled task for automatic daily aggregation
- Configure privacy redaction rules in `config/logging-config.json`
- Create custom analysis scripts based on your needs
- Export to external tools (CSV, SQLite) for advanced analysis
