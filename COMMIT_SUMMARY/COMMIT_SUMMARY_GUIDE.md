---
doc_id: DOC-GUIDE-COMMIT-SUMMARY-GUIDE-158
---

# Commit Summary System Guide

## Overview

The commit summary system automatically generates structured 6-hour snapshots of repository activity, aligned with the phase-based architecture and subsystem organization.

**Purpose:**
- Provide AI agents with focused context about recent changes
- Track automation health (strengthened vs weakened)
- Identify risk patterns and open loops
- Guide next actions with phase/subsystem alignment

## Quick Start

### Generate a summary on-demand
```powershell
.\scripts\generate_commit_summary.ps1
```

### Generate for last 12 hours across multiple branches
```powershell
.\scripts\generate_commit_summary.ps1 -Hours 12 -Branches "main,feature/x"
```

### Run in automated mode (for scheduled tasks)
```powershell
.\scripts\generate_commit_summary.ps1 -Mode auto_6h
```

## Architecture Integration

### Phase Mapping
Commits are automatically categorized by phase based on file paths:

| File Pattern | Phase |
|--------------|-------|
| `phase0_*/`, `core/state/` | Phase 0 – Initialization |
| `phase1_*/` | Phase 1 – Planning |
| `phase2_*/` | Phase 2 – Scheduling |
| `phase3_*/` | Phase 3 – Routing |
| `phase4_*/` | Phase 4 – (Name TBD) |
| `phase5_*/`, `core/engine/` | Phase 5 – Execution & Validation |
| `phase6_*/`, `error/` | Phase 6 – Error Recovery |
| `phase7_*/` | Phase 7 – Monitoring & UX |

### Subsystem Mapping
Commits are categorized by architectural subsystem:

| File Pattern | Subsystem |
|--------------|-----------|
| `core/engine/`, `core/state/` | Core Engine |
| `error/engine/`, `error/plugins/` | Error Detection & Recovery |
| `specifications/`, `schema/` | Specification & Workstream Bridge |
| `aim/`, `config/tool_profiles*` | Tool Selection & Adapters |
| `.state/` | File & Task Lifecycle / State & Persistence |
| `gui/`, `pm/` | GUI / PM / CCPM Integration |
| `docs/`, `schema/` | Docs / Diagrams / Schemas |

## Output Structure

Summaries are written to: `docs/commit_summaries/COMMIT_SUMMARY_YYYYMMDD_HHMM.md`

### Key Sections for AI Agents

1. **Section 0 – Mission & Focus Anchor**
   - Quick orientation: what this window was about
   - Phases and subsystems touched

2. **Section 1 – Executive Summary**
   - Net effect on system
   - Risk assessment
   - Automation posture (strengthened/weakened/neutral)
   - High-priority notes for next run

3. **Section 5 – Focus Guidance (CRITICAL)**
   - Threads to continue
   - Areas NOT to touch
   - Open loops requiring action

4. **Section 6 – Commit Inventory (Machine-Readable)**
   - JSON structure for downstream tools
   - Phase/subsystem tags per commit
   - Risk and automation impact per commit

## Risk Assessment

Commits are automatically classified:

- **LOW**: Few files, has tests
- **MEDIUM**: >10 files OR no tests with >3 files
- **HIGH**: CI/workflow changes OR >20 files

Overall risk = highest individual commit risk in window.

## Automation Impact

Automatic classification:

- **STRENGTHENED**: Tests added/improved
- **WEAKENED**: Tests removed, validation bypassed
- **NEUTRAL**: No test/validation changes
- **UNKNOWN**: Cannot determine

## Integration with Orchestrator

The commit summary feeds into:

1. **Context for AI agents** – Read section 5 first before working
2. **Registry updates** – Track file lifecycle changes
3. **GUI panels** – Display recent activity by phase/subsystem
4. **CCPM integration** – Link commits to workstreams/tasks
5. **Error detection** – Flag automation weakening patterns

## Scheduled Automation (Future)

To run every 6 hours via Task Scheduler:

```powershell
# Create scheduled task (Windows)
$Action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-File C:\path\to\scripts\generate_commit_summary.ps1 -Mode auto_6h"
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 6)
Register-ScheduledTask -TaskName "CommitSummaryGenerator" -Action $Action -Trigger $Trigger
```

## Schema Validation

The output conforms to `schema/commit_summary.schema.json`.

Validate a generated summary:
```powershell
# Using jsonschema (Python)
pip install jsonschema
python -c "import json, jsonschema; ..."

# Or using ajv (Node.js)
npm install -g ajv-cli
ajv validate -s schema/commit_summary.schema.json -d docs/commit_summaries/COMMIT_SUMMARY_*.md
```

## Agent Usage Patterns

### Before starting work
```markdown
1. Read latest commit summary (section 5 first)
2. Check "Do NOT touch" areas
3. Identify relevant threads to continue
4. Note open loops related to your task
```

### After generating code
```markdown
1. Update commit summary if running in agent mode
2. Mark threads as progressed/completed
3. Add new open loops if issues discovered
4. Update automation impact assessment
```

## Customization

### Add custom phase mappings
Edit `$PhasePatterns` in `scripts/generate_commit_summary.ps1`:
```powershell
$PhasePatterns = @{
    'your/path/' = 'Phase X'
    # ...
}
```

### Add custom subsystem mappings
Edit `$SubsystemPatterns`:
```powershell
$SubsystemPatterns = @{
    'your/module/' = 'your_subsystem'
    # ...
}
```

### Adjust risk heuristics
Edit risk calculation logic in the script (search for `# Simple risk heuristic`).

## File Lifecycle

- **Generated**: Every 6 hours (automated) or on-demand
- **Location**: `docs/commit_summaries/`
- **Retention**: Keep last 30 days (manual cleanup or add to archive script)
- **Archival**: Old summaries → `_ARCHIVE/commit_summaries/`

## Troubleshooting

### No commits found
```powershell
# Check git log directly
git log --since="6 hours ago" --pretty=oneline

# Verify time zone
Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz"
```

### Wrong phases detected
- Check file path patterns in script
- Verify file locations match phase structure
- Add custom mappings if needed

### Template not found
```powershell
# Ensure template exists
Test-Path templates\COMMIT_SUMMARY_TEMPLATE.md

# Regenerate if missing from git
git checkout templates\COMMIT_SUMMARY_TEMPLATE.md
```

## Future Enhancements

- [ ] Automatic linking to workstream IDs
- [ ] Integration with doc_id system for unique IDs
- [ ] GUI panel showing latest summaries
- [ ] Diff comparison between summaries
- [ ] Trend analysis (automation health over time)
- [ ] Email/Slack notifications for HIGH risk windows
- [ ] Integration with test_gate acceptance criteria

## References

- Template: `templates/COMMIT_SUMMARY_TEMPLATE.md`
- Schema: `schema/commit_summary.schema.json`
- Generator: `scripts/generate_commit_summary.ps1`
- Output: `docs/commit_summaries/`
