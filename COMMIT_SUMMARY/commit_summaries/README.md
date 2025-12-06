---
doc_id: DOC-GUIDE-README-226
---

# Commit Summary System

**Automated 6-hour repository activity snapshots aligned with phase-based architecture**

## What is this?

The commit summary system generates structured reports every 6 hours (or on-demand) that:
- Categorize commits by **phase** (0-7) and **subsystem** (core engine, error engine, etc.)
- Assess **risk** and **automation health** automatically
- Provide **focus guidance** for AI agents on what to work on next
- Track **open loops** and areas requiring attention

## Quick Start

```powershell
# Generate summary for last 6 hours (default)
.\scripts\generate_commit_summary.ps1

# Generate for last 24 hours
.\scripts\generate_commit_summary.ps1 -Hours 24

# Generate across multiple branches
.\scripts\generate_commit_summary.ps1 -Branches "main,feature/x,feature/y"

# Run in automated mode (for scheduled tasks)
.\scripts\generate_commit_summary.ps1 -Mode auto_6h
```

## Files

| File | Purpose |
|------|---------|
| `templates/COMMIT_SUMMARY_TEMPLATE.md` | Template with YAML frontmatter and structured sections |
| `schema/commit_summary.schema.json` | JSON schema for validation |
| `scripts/generate_commit_summary.ps1` | Generator script (PowerShell) |
| `docs/reference/COMMIT_SUMMARY_GUIDE.md` | Complete documentation |
| `docs/commit_summaries/` | Generated summaries (output directory) |

## For AI Agents

**Before starting work:**
1. Read latest summary: `docs/commit_summaries/COMMIT_SUMMARY_*.md`
2. Jump to **Section 5** (Focus Guidance) first
3. Check "Do NOT touch" areas
4. Identify threads to continue
5. Note open loops related to your task

**Key sections:**
- **Section 0**: Mission & phases touched
- **Section 1**: Executive summary + risk + automation posture
- **Section 5**: ⭐ **CRITICAL** – What to do next, what NOT to touch, open loops
- **Section 6**: Machine-readable commit inventory (JSON)

## Phase & Subsystem Mapping

Commits are auto-categorized based on file paths:

### Phases
- `phase0_*/`, `core/state/` → Phase 0 (Initialization)
- `phase1_*/` → Phase 1 (Planning)
- `phase5_*/`, `core/engine/` → Phase 5 (Execution)
- `phase6_*/`, `error/` → Phase 6 (Error Recovery)
- etc.

### Subsystems
- `core/engine/`, `core/state/` → Core Engine
- `error/engine/`, `error/plugins/` → Error Engine
- `specifications/`, `schema/` → Spec Bridge
- `aim/`, `config/tool_profiles*` → Tool Adapters
- `gui/`, `pm/` → GUI/PM Integration

## Risk Levels

- **LOW**: Few files (<10), has tests
- **MEDIUM**: Many files (10-20) OR no tests with changes
- **HIGH**: CI/workflow changes OR >20 files

## Automation Impact

- **STRENGTHENED**: Tests added/improved
- **WEAKENED**: Tests removed, validation bypassed
- **NEUTRAL**: No test changes
- **UNKNOWN**: Cannot determine

## Scheduled Automation (Optional)

Run every 6 hours via Windows Task Scheduler:

```powershell
$Action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-File C:\path\to\scripts\generate_commit_summary.ps1 -Mode auto_6h"
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 6)
Register-ScheduledTask -TaskName "CommitSummary" -Action $Action -Trigger $Trigger
```

## Integration Points

The commit summary system integrates with:

1. **Orchestrator** – Feed commit context to planning phase
2. **Registry** – Track file lifecycle changes
3. **GUI** – Display recent activity by phase/subsystem
4. **CCPM** – Link commits to workstreams/tasks
5. **Error Engine** – Flag automation weakening patterns
6. **Doc ID System** – Assign unique IDs to summaries

## Example Output

```yaml
---
doc_type: commit_summary
doc_id: COMMIT-SUMMARY-20251205-0902
generated_by:
  tool: commit_summary_agent
  mode: auto_6h
  run_id: RUN-20251205-090245
time_window:
  start: 2025-12-05T00:00:00-06:00
  end: 2025-12-05T06:00:00-06:00
stats:
  commit_count: 12
  authors_count: 2
  files_changed: 47
  tests_changed: 8
  pipelines_touched: 0
risk_overall: MEDIUM
focus_signal: Phase 5 executor wiring
---

# Section 5: Focus Guidance (CRITICAL)

## Do more of this (next 6 hours)
1. Thread-1: Complete executor retry logic
   - Context: Added basic retry in executor.py
   - Next step: Add exponential backoff + circuit breaker

2. Thread-2: Wire test_gate to acceptance tests
   - Context: Stub created in phase5_execution/
   - Next step: Implement validation criteria checking
...
```

## Full Documentation

See `docs/reference/COMMIT_SUMMARY_GUIDE.md` for:
- Complete architecture integration details
- Customization options
- Troubleshooting guide
- Future enhancements
- Schema validation

## Why This Matters

**For humans:**
- Quick snapshot of what happened while you were away
- Risk awareness before merging branches
- Trend analysis of automation health

**For AI agents:**
- Context-aware work continuation
- Avoid conflicting with recent changes
- Prioritize based on open loops and threads
- Maintain automation discipline

## Status

✅ **IMPLEMENTED** (2025-12-05)
- Template created with YAML frontmatter
- Schema defined and validated
- PowerShell generator script working
- Auto-categorization by phase/subsystem
- Risk and automation impact assessment
- Integration hooks for orchestrator/GUI

🔄 **Next Steps:**
- Integrate with doc_id system for unique IDs
- Add scheduled task setup script
- Wire into orchestrator context gathering
- Create GUI panel for summary display
- Add trend analysis (automation health over time)
