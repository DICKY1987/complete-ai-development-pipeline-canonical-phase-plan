  1. Copy the template to a new phase file

  - Command (PowerShell):
    Copy-Item MASTER_SPLINTER_Phase_Plan_Template.yml plans/phases/PH-XX_ws-yyy.yml

  2. Fill only the variable fields

  - Required to change:
      - doc_id, phase_identity.phase_id, phase_identity.workstream_id, phase_identity.title,
        phase_identity.summary, phase_identity.objective, phase_identity.status (not_started|
        in_progress|planned|blocked|done), estimate_hours (rough), tags.
      - dag_and_dependencies (depends_on, may_run_parallel_with, parallel_group, is_critical_path).
      - scope_and_modules (modules, file_scope lists; optional worktree_strategy.worktrees if using
        multiple worktrees).
      - environment_and_tools (only if defaults don’t fit).
      - execution_plan.steps[*] (keep structure; adjust pattern_ids/tool_id/commands and add any
        execution_templates IDs if relevant).
      - expected_artifacts, acceptance_tests, completion_gate.rules (set to your phase needs).
  - Leave structure, headings, and unused optional fields intact.

  3. Keep machine hints intact

  - Do not remove table_of_contents, index, or any keys—only change values.
  - If not using multi-worktrees, leave multi_worktree_enabled: false and the sample entry as-is.

  4. Quick validity check

  - Optional YAML parse check:
    python - <<'PY'\nimport yaml;yaml.safe_load(open('plans/phases/PH-XX_ws-
    yyy.yml'))\nprint("OK")\nPY

  Prompt template for the CLI tool

  - “Copy MASTER_SPLINTER_Phase_Plan_Template.yml to plans/phases/PH-XX_ws-yyy.yml and fill only
    these fields: doc_id, phase_identity (phase_id, workstream_id, title, summary, objective, status,
    estimate_hours, tags), dag_and_dependencies, scope_and_modules (modules, file_scope; optional
    worktrees), execution_plan.steps inputs/commands/tool_ids/pattern_ids, expected_artifacts,
    acceptance_tests, completion_gate.rules. Do not change structure or keys. Leave table_of_contents/
    index as-is. Set multi_worktree_enabled false unless needed. Keep YAML valid.”

---

## Workstream Sync to GitHub Project Manager

### Quick Reference Commands

```powershell
# Sync all workstreams to GitHub PM (NO STOP MODE)
python scripts/sync_workstreams_to_github.py

# Custom feature branch
python scripts/sync_workstreams_to_github.py --branch feature/ws-batch-2024

# Preview mode (dry run)
python scripts/sync_workstreams_to_github.py --dry-run
```

### Critical Feature: NO STOP EXECUTION

**INSTRUCTION TO AI/TOOLS**: When processing workstreams, the engine MUST:

✅ **Continue through all tasks** - Never halt on single failure  
✅ **Collect all errors** - Record every error encountered  
✅ **Track all successes** - Log every successful operation  
✅ **Generate final report** - Always produce complete summary  

Template location: `templates/workstream_summary_report.md`
Script location: `scripts/sync_workstreams_to_github.py`
