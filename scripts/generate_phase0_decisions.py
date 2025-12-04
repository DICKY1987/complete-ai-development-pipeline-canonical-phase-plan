#!/usr/bin/env python3
"""Generate Phase 0 decision documents in batch

Usage:
    python scripts/generate_phase0_decisions.py

Generates:
    - DECISION_LOG_DATABASE_STRATEGY.md
    - DECISION_LOG_SUPERVISOR_DEPLOYMENT.md
    - DESIGN_APPROVAL_DECISION_INTERFACE.md
    - DESIGN_TOOL_RESUME_STRATEGY.md
"""

from datetime import datetime
from pathlib import Path

from jinja2 import Template

# Decision specifications
DECISIONS = [
    {
        "topic": "DATABASE_STRATEGY",
        "title": "Database Unification Strategy",
        "context": """
The codebase currently has two separate database systems:
- core/state/db.py → .ledger/framework.db (runs, step_attempts tables)
- gui/tui_app/core/sqlite_state_backend.py → .worktrees/pipeline_state.db (uet_executions, patch_ledger tables)

The headless CLI supervision feature needs to add tool_runs and approvals tables.
We must decide which database to use and how to handle the schema divergence.
        """,
        "problem": "Two separate databases with different schemas create maintenance burden and data consistency issues",
        "options": [
            {
                "name": "unified_db",
                "description": "Merge both databases into single schema at .worktrees/pipeline_state.db",
                "pros": [
                    "Single source of truth - no data sync issues",
                    "Atomic transactions across all tables",
                    "Simpler code - one connection, one schema",
                    "Easier to maintain and evolve",
                ],
                "cons": [
                    "Significant migration effort required",
                    "Potential breaking changes to existing code",
                    "Risk during migration (need rollback plan)",
                ],
                "recommendation": "RECOMMENDED - Long-term cleanest solution",
            },
            {
                "name": "dual_db_with_sync",
                "description": "Keep separate databases, sync tool_runs/approvals between them",
                "pros": [
                    "Less disruptive to existing code",
                    "Gradual migration path possible",
                    "Lower immediate risk",
                ],
                "cons": [
                    "Data consistency issues (sync lag, conflicts)",
                    "Increased complexity (sync daemon required)",
                    "Two schemas to maintain forever",
                ],
                "recommendation": "Acceptable fallback if migration too risky",
            },
            {
                "name": "supervisor_writes_both",
                "description": "cli_supervisor writes tool_runs/approvals to both databases",
                "pros": [
                    "Quick implementation - no migration needed",
                    "Works with existing architecture immediately",
                ],
                "cons": [
                    "Technical debt - double writes error-prone",
                    "Complex failure handling (what if one write fails?)",
                    "Performance overhead",
                    "Still need to unify eventually",
                ],
                "recommendation": "AVOID - Creates more problems than it solves",
            },
        ],
        "chosen_option": "TBD - Team decision required",
        "rationale": "Decision pending team discussion of migration effort vs long-term benefits",
        "positive_consequences": ["TBD after decision"],
        "negative_consequences": ["TBD after decision"],
        "risks": ["TBD after decision"],
        "implementation_notes": """
If unified_db chosen:
1. Create migration script to merge schemas
2. Back up both databases before migration
3. Test migration on copy of production data
4. Create rollback procedure
5. Update all code to use unified schema

If dual_db_with_sync chosen:
1. Create sync daemon
2. Define sync protocol (eventual consistency)
3. Handle conflict resolution
4. Monitor sync lag
        """,
        "implementation_start": "TBD",
        "expected_completion": "TBD",
        "related_decisions": [],
        "references": [
            "gui/HEADLESS_CLI_SUPERVISION_PLAN.json - Phase 1 tasks",
            "gui/HEADLESS_CLI_SUPERVISION_GAP_ANALYSIS.md - Gap #3",
        ],
    },
    {
        "topic": "SUPERVISOR_DEPLOYMENT",
        "title": "Supervisor Deployment Mode",
        "context": """
The CLI supervisor needs to run continuously to monitor tools and handle approvals.
We must decide whether it runs as part of the orchestrator process, as a separate daemon, or on-demand.
        """,
        "problem": "How should cli_supervisor run: embedded, daemon, or on-demand?",
        "options": [
            {
                "name": "embedded_in_orchestrator",
                "description": "Supervisor runs as part of orchestrator process",
                "pros": [
                    "Simple deployment - one process to manage",
                    "Shared state - direct access to orchestrator data",
                    "No IPC overhead",
                    "Easier to debug",
                ],
                "cons": [
                    "Orchestrator crash kills supervisor",
                    "Tightly coupled - harder to scale independently",
                    "Resource contention in single process",
                ],
                "recommendation": "RECOMMENDED for MVP",
            },
            {
                "name": "separate_daemon",
                "description": "Supervisor runs as independent background service",
                "pros": [
                    "Independent lifecycle - survives orchestrator restarts",
                    "Can scale independently",
                    "Better fault isolation",
                ],
                "cons": [
                    "Deployment complexity - two processes to manage",
                    "IPC required for communication",
                    "Extra monitoring and health checks needed",
                ],
                "recommendation": "Future enhancement for production",
            },
            {
                "name": "on_demand_per_tool",
                "description": "Spawn supervisor instance for each tool execution",
                "pros": [
                    "No persistent process - clean isolation",
                    "Simple process model",
                ],
                "cons": [
                    "Startup overhead per tool",
                    "No shared state between tools",
                    "Process sprawl with many concurrent tools",
                ],
                "recommendation": "AVOID - Too complex, poor performance",
            },
        ],
        "chosen_option": "TBD - Team decision required",
        "rationale": "Decision pending team discussion of MVP vs production requirements",
        "positive_consequences": ["TBD after decision"],
        "negative_consequences": ["TBD after decision"],
        "risks": ["TBD after decision"],
        "implementation_notes": """
If embedded chosen:
1. Add supervisor module to orchestrator
2. Start supervisor threads on orchestrator init
3. Share database connection
4. Implement graceful shutdown

If daemon chosen:
1. Create systemd service file
2. Implement IPC (HTTP REST API or message queue)
3. Add health check endpoint
4. Create deployment scripts
        """,
        "implementation_start": "TBD",
        "expected_completion": "TBD",
        "related_decisions": ["DECISION-DATABASE_STRATEGY-001"],
        "references": [
            "gui/HEADLESS_CLI_SUPERVISION_PLAN.json - Phase 0",
            "gui/EXECUTION_PATTERN_ANALYSIS.md",
        ],
    },
    {
        "topic": "APPROVAL_DECISION_INTERFACE",
        "title": "Approval Decision Mechanism Design",
        "context": """
Users need a way to approve/reject pending approvals from tools running in headless mode.
The solution must work when no terminal is available and support both interactive and scripted workflows.
        """,
        "problem": "How do users approve/reject pending approvals?",
        "options": [
            {
                "name": "tui_interactive",
                "description": "Keybindings in TUI approvals panel",
                "pros": [
                    "Visual and intuitive",
                    "Quick keyboard navigation",
                    "Real-time feedback",
                ],
                "cons": ["Requires TUI to be running", "Not scriptable"],
                "recommendation": "Must-have for interactive use",
            },
            {
                "name": "cli_commands",
                "description": "Command-line approval interface",
                "pros": [
                    "Scriptable and automatable",
                    "Works in headless environments",
                    "Can be called from scripts/CI",
                ],
                "cons": ["Less intuitive than TUI", "Requires remembering commands"],
                "recommendation": "Must-have for automation",
            },
            {
                "name": "http_api",
                "description": "REST API for external integrations",
                "pros": [
                    "Enables web UI",
                    "Supports remote approval",
                    "Integrates with external tools",
                ],
                "cons": [
                    "Adds deployment complexity (web server)",
                    "Security considerations (auth, TLS)",
                    "Not needed for MVP",
                ],
                "recommendation": "Nice-to-have for future (Phase 9)",
            },
        ],
        "chosen_option": "Multi-modal: TUI + CLI (MVP), HTTP API (future)",
        "rationale": "Both TUI and CLI are needed to support interactive and scripted workflows. HTTP API deferred to future phase.",
        "positive_consequences": [
            "Supports both interactive and automated approval",
            "Flexible deployment (can use TUI or CLI as needed)",
            "No web server complexity in MVP",
        ],
        "negative_consequences": [
            "Must maintain two interfaces (TUI + CLI)",
            "Remote approval requires SSH access (until HTTP API added)",
        ],
        "risks": [
            "CLI and TUI implementations could drift (mitigate: shared backend logic)"
        ],
        "implementation_notes": """
Phase 3.5 implementation:

TUI (CRIT-001):
- Create approvals_panel.py with DataTable widget
- Keybindings: a=approve, r=reject, enter=show options dialog
- Refresh every 5 seconds
- Call state_client.update_approval_status()

CLI (CRIT-002):
- Add commands to core/ui_cli.py:
  - python -m core.ui_cli approvals [--all] [--json]
  - python -m core.ui_cli approve <id> --choice <value>
  - python -m core.ui_cli reject <id> [--reason <text>]
- Use same state_client backend as TUI

Shared backend:
- state_client.update_approval_status() handles DB write
- Prevent race conditions with WHERE status='pending' check
        """,
        "implementation_start": "Phase 3.5",
        "expected_completion": "Phase 3.5 + 2 weeks",
        "related_decisions": ["DECISION-SUPERVISOR_DEPLOYMENT-001"],
        "references": [
            "gui/HEADLESS_CLI_SUPERVISION_PLAN.json - Phase 3.5, CRIT-001, CRIT-002",
            "gui/HEADLESS_CLI_SUPERVISION_GAP_ANALYSIS.md - Gap #1",
        ],
    },
    {
        "topic": "TOOL_RESUME_STRATEGY",
        "title": "Tool Resume After Approval Strategy",
        "context": """
When a tool exits with code 90 (waiting_approval), the user approves it, and the tool needs to resume.
We must decide how to restart the tool with the approval decision.
        """,
        "problem": "How do tools resume after user approves?",
        "options": [
            {
                "name": "polling_worker",
                "description": "Background worker polls approvals table, restarts tools on approval",
                "pros": [
                    "Simple to implement",
                    "Works with existing architecture",
                    "No persistent connection needed",
                ],
                "cons": [
                    "Polling delay (5 second intervals)",
                    "Resource usage (constant polling)",
                ],
                "recommendation": "RECOMMENDED for MVP",
            },
            {
                "name": "event_driven",
                "description": "DB triggers or pub/sub system notifies supervisor of approval",
                "pros": [
                    "Instant notification (no polling delay)",
                    "More efficient (no wasted polling)",
                ],
                "cons": [
                    "SQLite doesn't support triggers for external notifications",
                    "Requires message queue (Redis, RabbitMQ) - added complexity",
                    "Overkill for MVP",
                ],
                "recommendation": "Future enhancement for production",
            },
            {
                "name": "tool_stays_running",
                "description": "Tool polls DB itself while waiting for approval",
                "pros": [
                    "No supervisor involvement needed",
                    "Tool can resume immediately",
                ],
                "cons": [
                    "Tool process stays alive (resource usage)",
                    "Complex failure handling (what if tool crashes?)",
                    "Duplicates polling logic in every tool",
                ],
                "recommendation": "AVOID - Tool should exit cleanly",
            },
        ],
        "chosen_option": "Polling background worker with tool restart",
        "rationale": "Simplest approach for MVP. 5-second delay is acceptable. Can optimize to event-driven later if needed.",
        "positive_consequences": [
            "Simple implementation",
            "Tools exit cleanly (no hanging processes)",
            "Centralized resume logic (in supervisor)",
        ],
        "negative_consequences": [
            "5-second delay before tool resumes",
            "Polling overhead (mitigated by short query)",
        ],
        "risks": [
            "Tool restart could fail (mitigate: retry logic, mark as failed after 3 attempts)"
        ],
        "implementation_notes": """
Phase 3.5, CRIT-003 implementation:

approval_resume_worker():
1. Run as daemon thread in supervisor
2. Poll interval: 5 seconds (configurable in supervision.yaml)
3. Query: SELECT * FROM tool_runs WHERE status='waiting_approval'
4. For each: check approvals WHERE tool_run_id=... AND status!='pending'
5. If approved:
   - Re-run tool with env var: AUTO_APPROVAL=<chosen_value>
   - OR pass as arg: --approval-decision=<chosen_value>
6. If rejected/expired:
   - Mark tool_run as 'failed'
   - Log event
7. Error handling:
   - Tool restart failure: retry 3x, then mark failed
   - DB error: log, continue to next
   - Concurrent approval: use WHERE status='pending' in UPDATE

Tool contract (for custom tools):
- Check os.environ.get('AUTO_APPROVAL') or argparse
- If set, use that value instead of prompting
- Tools must support this for auto-resume to work
        """,
        "implementation_start": "Phase 3.5",
        "expected_completion": "Phase 3.5 + 2 weeks",
        "related_decisions": [
            "DECISION-SUPERVISOR_DEPLOYMENT-001",
            "DESIGN-APPROVAL_DECISION_INTERFACE-001",
        ],
        "references": [
            "gui/HEADLESS_CLI_SUPERVISION_PLAN.json - Phase 3.5, CRIT-003",
            "gui/HEADLESS_CLI_SUPERVISION_GAP_ANALYSIS.md - Gap #2",
        ],
    },
]


def generate_decision_docs():
    """Generate all Phase 0 decision documents"""

    # Load template
    template_path = Path("templates/decision_log_template.md")
    if not template_path.exists():
        print(f"❌ Template not found: {template_path}")
        print("   Run this script from repo root")
        return 1

    template = Template(template_path.read_text())

    # Generate metadata
    date = datetime.now().strftime("%Y-%m-%d")
    author = "AI Development Team"
    status = "proposed"

    # Generate each decision doc
    generated = []
    for decision in DECISIONS:
        # Add common fields
        decision.update(
            {"date": date, "author": author, "status": status, "version": "1.0.0"}
        )

        # Render template
        content = template.render(**decision)

        # Determine output filename
        if decision["topic"].startswith("DESIGN"):
            filename = f"DESIGN_{decision['topic']}.md"
        else:
            filename = f"DECISION_LOG_{decision['topic']}.md"

        output_path = Path(filename)

        # Write file (UTF-8 encoding for special characters)
        output_path.write_text(content, encoding="utf-8")
        generated.append(output_path)
        print(f"✅ Generated: {output_path}")

    # Verify all files exist (ground truth)
    print("\n🔍 Verifying...")
    expected_count = len(DECISIONS)
    actual_count = len([p for p in generated if p.exists()])

    if actual_count == expected_count:
        print(f"✅ All {expected_count} decision documents created successfully")
        return 0
    else:
        print(f"❌ Expected {expected_count} files, found {actual_count}")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(generate_decision_docs())
