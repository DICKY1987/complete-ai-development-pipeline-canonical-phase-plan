---
doc_id: DOC-GUIDE-START-HERE-AI-138
---

# AI Execution Instructions - MASTER_SPLINTER

## Single Command Execution

```bash
python run_master_splinter.py
```

### What This Does

The master orchestrator executes the complete pipeline:

1. Validates prerequisites
   - Checks config files exist
   - Verifies pattern registry
   - Validates prompt templates
2. Discovers phase plans
   - Scans `plans/phases/*.yml`
   - Identifies filled phase plan templates
3. Converts to workstreams
   - Runs `phase_plan_to_workstream.py`
   - Generates `workstreams/*.json`
4. Executes multi-agent coordinator
   - Runs `multi_agent_workstream_coordinator.py`
   - Parallel agent execution
   - Consolidates results to database
5. Syncs to GitHub (optional)
   - Runs `sync_workstreams_to_github.py`
   - Creates feature branch
   - Pushes commits
6. Generates completion report
   - Creates `reports/COMPLETION_REPORT_*.md`
   - Summarizes all results
   - Lists errors and next steps

### Expected Output

```
MASTER_SPLINTER - 1-TOUCH ORCHESTRATOR
================================================================================

[14:30:22] [INFO] Validating prerequisites...
[14:30:22] [ OK ] Prerequisites validated
[14:30:22] [INFO] Discovering phase plans...
[14:30:22] [ OK ] Found 3 phase plan(s)
[14:30:23] [INFO] Converting phase plans to workstreams...
[14:30:23] [ OK ] Generated 3 workstream(s)
[14:30:23] [INFO] Starting multi-agent execution...
[14:30:45] [ OK ] Multi-agent execution completed
[14:30:45] [INFO] Generating completion report...
[14:30:45] [ OK ] Completion report: reports/COMPLETION_REPORT_master-run-20241202-143022.md

================================================================================
EXECUTION COMPLETE
================================================================================

Completion Report: reports/COMPLETION_REPORT_master-run-20241202-143022.md
Successes: 6
Errors: 0

Review the completion report above for details.
```

### User Review Location

Report path: `reports/COMPLETION_REPORT_<timestamp>.md`

The user should review this file for:
- Execution summary
- Success/failure status
- Detailed results
- Any errors encountered
- Next steps

### NO STOP MODE

The orchestrator continues through all steps even if errors occur.
All errors are collected and reported at the end.

### Troubleshooting

If execution fails:
1. Check `logs/` directory for detailed error logs.
2. Review `reports/COMPLETION_REPORT_*.md`.
3. Verify prerequisites in `config/`.
4. Consult `CLAUDE.md` for configuration details.
