---
doc_id: DOC-GUIDE-DECISION-LOG-APPROVAL-DECISION-INTERFACE-490
decision_id: DECISION-APPROVAL_DECISION_INTERFACE-001
date: 2025-12-03
status: proposed
author: AI Development Team
---

# Decision: Approval Decision Mechanism Design

## Context


Users need a way to approve/reject pending approvals from tools running in headless mode.
The solution must work when no terminal is available and support both interactive and scripted workflows.


## Problem Statement

How do users approve/reject pending approvals?

## Options Considered


### Option 1: tui_interactive

**Description**: Keybindings in TUI approvals panel

**Pros**:

- Visual and intuitive

- Quick keyboard navigation

- Real-time feedback


**Cons**:

- Requires TUI to be running

- Not scriptable


**Recommendation**: Must-have for interactive use


### Option 2: cli_commands

**Description**: Command-line approval interface

**Pros**:

- Scriptable and automatable

- Works in headless environments

- Can be called from scripts/CI


**Cons**:

- Less intuitive than TUI

- Requires remembering commands


**Recommendation**: Must-have for automation


### Option 3: http_api

**Description**: REST API for external integrations

**Pros**:

- Enables web UI

- Supports remote approval

- Integrates with external tools


**Cons**:

- Adds deployment complexity (web server)

- Security considerations (auth, TLS)

- Not needed for MVP


**Recommendation**: Nice-to-have for future (Phase 9)



## Decision

**Chosen Option**: Multi-modal: TUI + CLI (MVP), HTTP API (future)

**Rationale**: Both TUI and CLI are needed to support interactive and scripted workflows. HTTP API deferred to future phase.

## Consequences

### Positive

- Supports both interactive and automated approval

- Flexible deployment (can use TUI or CLI as needed)

- No web server complexity in MVP


### Negative

- Must maintain two interfaces (TUI + CLI)

- Remote approval requires SSH access (until HTTP API added)


### Risks

- CLI and TUI implementations could drift (mitigate: shared backend logic)


## Implementation Notes


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


## Timeline

- **Decision Date**: 2025-12-03
- **Implementation Start**: Phase 3.5
- **Expected Completion**: Phase 3.5 + 2 weeks

## Related Decisions


- DECISION-SUPERVISOR_DEPLOYMENT-001


## References


- gui/HEADLESS_CLI_SUPERVISION_PLAN.json - Phase 3.5, CRIT-001, CRIT-002

- gui/HEADLESS_CLI_SUPERVISION_GAP_ANALYSIS.md - Gap #1
