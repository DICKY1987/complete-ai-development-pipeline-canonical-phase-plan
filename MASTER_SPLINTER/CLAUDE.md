---
doc_id: DOC-GUIDE-CLAUDE-146
---

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 1-Touch Execution for AI

**Single Command**:
```bash
python run_master_splinter.py
```

This master orchestrator:
1. Discovers phase plans in `plans/phases/`
2. Converts them to executable workstreams
3. Runs the multi-agent coordinator
4. Optionally syncs to GitHub
5. Generates a completion report

Output: `reports/COMPLETION_REPORT_<timestamp>.md`

The user reviews this report to verify execution results.

## Repository Overview

**MASTER_SPLINTER** is a phase plan orchestration system that coordinates multi-agent workstreams using YAML templates, Python automation scripts, and GitHub project management integration. The system emphasizes "NO STOP MODE" execution - scripts continue through errors to provide complete visibility.

## Core Architecture

### 1. Phase Plan Template System
- **Template**: `MASTER_SPLINTER_Phase_Plan_Template.yml` - Machine-readable YAML template for defining phases
- **Guide**: `MASTER_SPLINTER_Phase_Plan_Template_GUIDE.md` - Field-by-field instructions and decision-elimination rules
- **Quick Reference**: `MASTER_SPLINTER_paste_dir.md` - Copy-paste commands for rapid phase creation

### 2. Automation Scripts
Two main Python scripts orchestrate workstream execution:

#### `sync_workstreams_to_github.py`
- Creates feature branches with timestamped names
- Commits each workstream separately with structured metadata
- Pushes to remote repository
- Generates summary reports from templates
- **NO STOP MODE**: Continues through errors, collecting all successes/failures

#### `multi_agent_workstream_coordinator.py`
- Executes workstreams across multiple agents in parallel
- Consolidates results from all agents into SQLite database
- Generates unified reports with agent performance metrics
- **NO STOP MODE**: Full execution with comprehensive error collection
- Uses `networkx` for DAG-based dependency resolution
- Database: `.state/multi_agent_consolidated.db`

### 3. Key Concepts
- **Workstreams**: JSON/YAML task definitions processed by scripts
- **Phase Plans**: Complete execution blueprints with pre-flight checks, execution steps, and acceptance tests
- **NO STOP MODE**: Critical design pattern - scripts never halt on individual failures, always produce complete reports
- **Decision-Elimination**: Pre-answer structural questions in templates to remove runtime choices

## Common Commands

### Validate Phase Plan YAML
```powershell
# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('MASTER_SPLINTER_Phase_Plan_Template.yml'))"
```

### Sync Workstreams to GitHub
```powershell
# Full sync with auto-generated branch name
python sync_workstreams_to_github.py

# Custom branch name
python sync_workstreams_to_github.py --branch feature/my-sync

# Dry run (preview only)
python sync_workstreams_to_github.py --dry-run
```

### Multi-Agent Execution
```powershell
# Execute with default agent count (3) and consolidation
python multi_agent_workstream_coordinator.py

# Review consolidated results
sqlite3 .state/multi_agent_consolidated.db
```

### Query Consolidated Database
```sql
-- View all runs
SELECT * FROM consolidated_runs ORDER BY timestamp DESC;

-- View agent results for specific run
SELECT * FROM agent_results WHERE run_id = 'RUN-ID';

-- Performance metrics
SELECT agent_id, COUNT(*) as tasks, AVG(duration_seconds) as avg_duration
FROM agent_results
WHERE run_id = 'RUN-ID'
GROUP BY agent_id;
```

## Development Workflow

### Creating New Phase Plans
1. Copy template: `MASTER_SPLINTER_Phase_Plan_Template.yml`
2. Follow field-by-field guide: `MASTER_SPLINTER_Phase_Plan_Template_GUIDE.md`
3. Set required fields: `phase_id`, `workstream_id`, `title`, `objective`, `status`
4. Define scope: `file_scope.modify`, `file_scope.create`, `forbidden_paths`
5. Validate YAML syntax before committing

### Modifying Python Scripts
- Scripts use `pathlib.Path` for cross-platform paths
- REPO_ROOT detection: `Path(__file__).parent.parent`
- All scripts create required directories automatically: `REPORTS_DIR`, `LOGS_DIR`, `STATE_DIR`
- Error handling: Log errors but continue execution (NO STOP MODE pattern)
- Use `typing` module for type hints
- Async operations use `asyncio`

### Report Generation
- Reports use template substitution: `templates/workstream_summary_report.md`
- Variables: `${TIMESTAMP}`, `${FEATURE_BRANCH}`, `${WORKSTREAMS_PROCESSED}`, etc.
- Output location: `reports/` with timestamped filenames

## Architecture Principles

### Ground Truth Over Vibes
Success determined by observable facts:
- Files exist at expected paths
- Commands exit with success codes
- Tests match success patterns
- Git scope limited to allowed paths

### Scope Enforcement
- All edits constrained to `scope_and_modules.file_scope`
- NEVER write to `forbidden_paths`
- Pre-flight checks verify scope before execution

### NO STOP MODE Pattern
When implementing or modifying scripts:
- Collect errors in lists, don't raise exceptions that halt execution
- Always generate final reports even if errors occurred
- Provide complete execution summary with successes + failures
- Log errors to stderr but continue processing

### Template Versioning
- `template_version` field tracks breaking changes
- Keep structure unchanged when filling templates
- Version bump only for structural modifications

## File Locations

```
MASTER_SPLINTER/
├── MASTER_SPLINTER_Phase_Plan_Template.yml    # Core template
├── MASTER_SPLINTER_Phase_Plan_Template_GUIDE.md
├── sync_workstreams_to_github.py              # GitHub sync script
├── multi_agent_workstream_coordinator.py       # Multi-agent coordinator
├── templates/
│   └── workstream_summary_report.md            # Report template
├── logs/                                       # Execution logs
├── reports/                                    # Generated reports
└── .state/
    └── multi_agent_consolidated.db             # Results database
```

## Dependencies

### Python Environment
- Python 3.12+ (tested with 3.12.10)
- Required packages:
  - `networkx` - DAG dependency resolution
  - `sqlite3` - Built-in, for result consolidation
  - Standard library: `asyncio`, `pathlib`, `subprocess`, `json`, `datetime`

### External Tools
- Git - Required for all workstream sync operations
- GitHub CLI (`gh`) - Optional, for advanced GitHub integration

## Integration Points

### GitHub Project Manager
- Workstreams sync to GitHub as separate commits
- `gh_item_id` field populated during sync
- Feature branches follow pattern: `feature/ws-sync-YYYYMMDD-HHMMSS`

### Database Schema
Consolidated results stored in SQLite with tables:
- `consolidated_runs` - Run-level metadata
- `agent_results` - Individual agent execution results
- `execution_metrics` - Performance and timing data

## Troubleshooting

### YAML Validation Fails
Check for:
- Missing required fields in `phase_identity` section
- Invalid enum values (e.g., `status`, `phase_type`)
- Malformed lists or dictionaries

### Workstream Sync Fails
- Verify git repository is initialized
- Check write permissions to `reports/` and `logs/`
- Ensure no uncommitted changes conflict with branch creation
- Review error collection in generated report

### Multi-Agent Execution Issues
- Check `.state/` directory exists and is writable
- Verify `networkx` is installed: `pip install networkx`
- Review consolidated database for error details
- Check logs in `logs/` directory for stack traces

## Testing Strategy

Scripts implement NO STOP MODE testing:
- Run scripts and verify reports are generated
- Check database for consolidated results
- Validate error collection (errors logged but execution completes)
- Verify file scope constraints are respected
