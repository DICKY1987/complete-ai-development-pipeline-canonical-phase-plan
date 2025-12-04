---
decision_id: DECISION-SUPERVISOR_DEPLOYMENT-001
date: 2025-12-03
status: proposed
author: AI Development Team
---

# Decision: Supervisor Deployment Mode

## Context


The CLI supervisor needs to run continuously to monitor tools and handle approvals.
We must decide whether it runs as part of the orchestrator process, as a separate daemon, or on-demand.


## Problem Statement

How should cli_supervisor run: embedded, daemon, or on-demand?

## Options Considered


### Option 1: embedded_in_orchestrator

**Description**: Supervisor runs as part of orchestrator process

**Pros**:

- Simple deployment - one process to manage

- Shared state - direct access to orchestrator data

- No IPC overhead

- Easier to debug


**Cons**:

- Orchestrator crash kills supervisor

- Tightly coupled - harder to scale independently

- Resource contention in single process


**Recommendation**: RECOMMENDED for MVP


### Option 2: separate_daemon

**Description**: Supervisor runs as independent background service

**Pros**:

- Independent lifecycle - survives orchestrator restarts

- Can scale independently

- Better fault isolation


**Cons**:

- Deployment complexity - two processes to manage

- IPC required for communication

- Extra monitoring and health checks needed


**Recommendation**: Future enhancement for production


### Option 3: on_demand_per_tool

**Description**: Spawn supervisor instance for each tool execution

**Pros**:

- No persistent process - clean isolation

- Simple process model


**Cons**:

- Startup overhead per tool

- No shared state between tools

- Process sprawl with many concurrent tools


**Recommendation**: AVOID - Too complex, poor performance



## Decision

**Chosen Option**: TBD - Team decision required

**Rationale**: Decision pending team discussion of MVP vs production requirements

## Consequences

### Positive

- TBD after decision


### Negative

- TBD after decision


### Risks

- TBD after decision


## Implementation Notes


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


## Timeline

- **Decision Date**: 2025-12-03
- **Implementation Start**: TBD
- **Expected Completion**: TBD

## Related Decisions


- DECISION-DATABASE_STRATEGY-001


## References


- gui/HEADLESS_CLI_SUPERVISION_PLAN.json - Phase 0

- gui/EXECUTION_PATTERN_ANALYSIS.md
