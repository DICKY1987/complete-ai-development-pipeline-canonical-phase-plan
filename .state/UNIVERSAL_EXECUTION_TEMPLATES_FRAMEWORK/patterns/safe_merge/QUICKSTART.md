---
doc_id: DOC-PAT-QUICKSTART-830
---

# Safe Merge Automation - Quick Start

## Installation

No installation required - patterns are self-contained scripts.

## Prerequisites

- Git CLI installed
- Python 3.8+ (for Python scripts)
- PowerShell 5.1+ (for PowerShell scripts)

## Phase 0: Reality Scan

### Scan Environment

```powershell
cd /path/to/your/repo

# Run environment scan
.\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\patterns\safe_merge\scripts\merge_env_scan.ps1 `
    -BaseBranch "main" `
    -FeatureBranch "feature/your-branch"
```

### Analyze Sync Log

```bash
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/safe_merge/scripts/sync_log_summary.py \
    .sync-log.txt --time-window "24h"
```

### Detect Nested Repos

```bash
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/safe_merge/scripts/nested_repo_detector.py .
```

## Phase 2: Safe Push

### Before Every Push

```powershell
# Use instead of raw 'git push'
.\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\patterns\safe_merge\scripts\safe_pull_and_push.ps1
```

### With Custom Settings

```powershell
.\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\patterns\safe_merge\scripts\safe_pull_and_push.ps1 `
    -Branch "my-feature" `
    -RemoteName "origin" `
    -RebaseMode "ff-only"
```

## Phase 3: File Classification

```bash
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/safe_merge/scripts/merge_file_classifier.py .
```

## Example Workflow

```powershell
# 1. Scan environment
.\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\patterns\safe_merge\scripts\merge_env_scan.ps1 `
    -BaseBranch "main" -FeatureBranch "feature/new-module"

# 2. Check for nested repos
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/safe_merge/scripts/nested_repo_detector.py .

# 3. Classify files
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/safe_merge/scripts/merge_file_classifier.py .

# 4. Safe push
.\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\patterns\safe_merge\scripts\safe_pull_and_push.ps1
```

## Outputs

All patterns generate structured JSON reports:

- `env_scan.safe_merge.json` - Environment scan results
- `sync_log_summary.json` - Sync log analysis
- `nested_repos_report.json` - Nested repo classification
- `merge_file_classes.json` - File classifications
- `safe_push_events.jsonl` - Push event log

## Next Steps

See full documentation in `README.md` and individual pattern docs in `patterns/`.
