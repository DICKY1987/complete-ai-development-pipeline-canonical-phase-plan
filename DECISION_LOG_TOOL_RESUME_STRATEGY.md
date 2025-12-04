---
decision_id: DECISION-TOOL_RESUME_STRATEGY-001
date: 2025-12-03
status: proposed
author: AI Development Team
---

# Decision: Tool Resume After Approval Strategy

## Context


When a tool exits with code 90 (waiting_approval), the user approves it, and the tool needs to resume.
We must decide how to restart the tool with the approval decision.


## Problem Statement

How do tools resume after user approves?

## Options Considered


### Option 1: polling_worker

**Description**: Background worker polls approvals table, restarts tools on approval

**Pros**:

- Simple to implement

- Works with existing architecture

- No persistent connection needed


**Cons**:

- Polling delay (5 second intervals)

- Resource usage (constant polling)


**Recommendation**: RECOMMENDED for MVP


### Option 2: event_driven

**Description**: DB triggers or pub/sub system notifies supervisor of approval

**Pros**:

- Instant notification (no polling delay)

- More efficient (no wasted polling)


**Cons**:

- SQLite doesn't support triggers for external notifications

- Requires message queue (Redis, RabbitMQ) - added complexity

- Overkill for MVP


**Recommendation**: Future enhancement for production


### Option 3: tool_stays_running

**Description**: Tool polls DB itself while waiting for approval

**Pros**:

- No supervisor involvement needed

- Tool can resume immediately


**Cons**:

- Tool process stays alive (resource usage)

- Complex failure handling (what if tool crashes?)

- Duplicates polling logic in every tool


**Recommendation**: AVOID - Tool should exit cleanly



## Decision

**Chosen Option**: Polling background worker with tool restart

**Rationale**: Simplest approach for MVP. 5-second delay is acceptable. Can optimize to event-driven later if needed.

## Consequences

### Positive

- Simple implementation

- Tools exit cleanly (no hanging processes)

- Centralized resume logic (in supervisor)


### Negative

- 5-second delay before tool resumes

- Polling overhead (mitigated by short query)


### Risks

- Tool restart could fail (mitigate: retry logic, mark as failed after 3 attempts)


## Implementation Notes


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


## Timeline

- **Decision Date**: 2025-12-03
- **Implementation Start**: Phase 3.5
- **Expected Completion**: Phase 3.5 + 2 weeks

## Related Decisions


- DECISION-SUPERVISOR_DEPLOYMENT-001

- DESIGN-APPROVAL_DECISION_INTERFACE-001


## References


- gui/HEADLESS_CLI_SUPERVISION_PLAN.json - Phase 3.5, CRIT-003

- gui/HEADLESS_CLI_SUPERVISION_GAP_ANALYSIS.md - Gap #2
