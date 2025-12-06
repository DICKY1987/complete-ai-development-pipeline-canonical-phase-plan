---
doc_id: DOC-GUIDE-PHASE-COORDINATOR-234
---

# Phase Coordinator Architecture

## Overview

The Phase Coordinator is the central orchestration service that automates the complete data flow between Phase 4 (Routing), Phase 5 (Execution), and Phase 6 (Error Recovery). It eliminates manual intervention and creates a fully automated pipeline for task execution and error handling.

## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                     PHASE COORDINATOR SERVICE                   │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Phase 4      │→ │ Phase 5      │→ │ Phase 6      │          │
│  │ Router       │  │ Executor     │  │ Error        │          │
│  │              │  │              │  │ Recovery     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         ↓                 ↓                  ↓                   │
│  ┌──────────────────────────────────────────────────────┐       │
│  │           EVENT BUS (Database-backed)                │       │
│  │  Events: ROUTING_COMPLETE, TASK_FAILED, FIX_APPLIED │       │
│  └──────────────────────────────────────────────────────┘       │
│         ↓                 ↓                  ↓                   │
│  ┌──────────────────────────────────────────────────────┐       │
│  │        STATE FILE MANAGER                            │       │
│  │  .state/routing_decisions.json                       │       │
│  │  .state/execution_results.json                       │       │
│  │  .state/error_analysis.json                          │       │
│  └──────────────────────────────────────────────────────┘       │
└────────────────────────────────────────────────────────────────┘
```

## Key Files

- **Implementation**: `core/engine/phase_coordinator.py`
- **Tests**: `tests/engine/test_phase_coordinator.py`
- **Configuration**: `config/coordinator_config.yaml`

## Status: ✅ COMPLETE

All Phase 4→5→6 automation is now fully implemented and tested.
