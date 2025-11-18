 Refactoring Project Completion Plan                             │
     │                                                                 │
     │ Pre-Execution: Resolve Blockers (4-6 hours)                     │
     │                                                                 │
     │ 1. Complete WS-08 Validation                                    │
     │                                                                 │
     │ - Run validation tasks from docs/WS-08-COMPLETION-PLAN.md       │
     │ - Confirm all 4 regression fixes work                           │
     │ - Mark WS-08 as complete                                        │
     │                                                                 │
     │ 2 Skip WS-10                                       │
     │                                                                 │
     │ Recommendation: Manual implementation (Option A)                │
     │ - Aider Windows/Unicode issues not worth debugging              │
     │ - 4-6 hours vs potentially much longer                          │
     │                                                                 │
     │ 3. Create Missing Workstream Bundles                            │
     │                                                                 │
     │ Create stub bundles for: WS-03, WS-04, WS-05, WS-06, WS-07,     │
     │ WS-09, WS-13, WS-14, WS-15, WS-16, WS-17                        │
     │ - Use scope from REFACTOR_PROJECT/Section_Aware Repo            │
     │ Refactor_Workstream Plan.md                                     │
     │                                                                 │
     │ ---                                                             │
     │ Phase 1-2: Foundation ✅ COMPLETE                               │
     │                                                                 │
     │ - WS-01: Hardcoded Path Indexer (done)                          │
     │ - WS-02: Section Mapping (done)                                 │
     │                                                                 │
     │ ---                                                             │
     │ Phase 3: Isolated Sections (10-16 hours)                        │
     │                                                                 │
     │ Execute in parallel - LOW RISK                                  │
     │                                                                 │
     │ | WS    | Target    | Key Tasks                              |  │
     │ |-------|-----------|----------------------------------------|  │
     │ | WS-03 | meta/     | Move remaining docs, update references |  │
     │ | WS-04 | gui/      | Complete stub implementation           |  │
     │ | WS-05 | infra/ci/ | Verify CI workflows                    |  │
     │                                                                 │
     │ Validation: Doc link checker, CI workflow tests                 │
     │                                                                 │
     │ ---                                                             │
     │ Phase 4: Moderately Isolated (14-22 hours)                      │
     │                                                                 │
     │ Execute in parallel - MEDIUM RISK                               │
     │                                                                 │
     │ | WS    | Target | Key Tasks                                    │
     │    |                                                            │
     │ |-------|--------|----------------------------------------------│
     │ ---|                                                            │
     │ | WS-06 | aim/   | Move src/pipeline/aim_bridge.py →            │
     │ aim/bridge.py |                                                 │
     │ | WS-07 | pm/    | Verify CCPM structure (70+ files)            │
     │    |                                                            │
     │ | WS-08 | aider/ | Complete validation (in progress)            │
     │    |                                                            │
     │                                                                 │
     │ Validation: pytest tests/pipeline/test_aim_bridge.py, pytest    │
     │ tests/aider/                                                    │
     │                                                                 │
     │ ---                                                             │
     │ Phase 5: Spec Tooling (13-18 hours)                             │
     │                                                                 │
     │ Sequential execution - MEDIUM RISK                              │
     │                                                                 │
     │ | Order | WS    | Target      | Key Tasks                       │
     │               |                                                 │
     │ |-------|-------|-------------|---------------------------------│
     │ --------------|                                                 │
     │ | 1     | WS-09 | spec/tools/ | Move tools/spec_* modules       │
     │               |                                                 │
     │ | 2     | WS-10 | OpenSpec    | Manual implementation of        │
     │ OpenSpec integration |                                          │
     │ | 3     | WS-11 | spec/docs/  | Move spec documentation         │
     │               |                                                 │
     │                                                                 │
     │ Validation: python scripts/generate_spec_index.py, OpenSpec     │
     │ round-trip test                                                 │
     │                                                                 │
     │ ---                                                             │
     │ Phase 6: Error Pipeline (30-38 hours)                           │
     │                                                                 │
     │ Sequential execution - HIGH RISK                                │
     │                                                                 │
     │ | Order | WS    | Target         | Key Tasks                    │
     │                   |                                             │
     │ |-------|-------|----------------|------------------------------│
     │ ------------------|                                             │
     │ | 1     | WS-12 | shared/utils/  | CRITICAL - Move src/utils/,  │
     │ update 30+ imports |                                            │
     │ | 2     | WS-13 | error/plugins/ | Move 21 plugins from         │
     │ src/plugins/              |                                     │
     │ | 3     | WS-14 | error/engine/  | Consolidate                  │
     │ MOD_ERROR_PIPELINE/                |                            │
     │                                                                 │
     │ Decision Required: Shared utils placement                       │
     │ - Option A: shared/utils/ (top-level, less churn) ← Recommended │
     │ - Option B: error/shared/utils/ (true isolation)                │
     │                                                                 │
     │ Validation: pytest -k error, pytest tests/plugins/              │
     │                                                                 │
     │ ---                                                             │
     │ Phase 7: Core Pipeline (31-40 hours)                            │
     │                                                                 │
     │ Sequential execution - VERY HIGH RISK ⚠️                        │
     │                                                                 │
     │ | Order | WS    | Target         | Key Tasks                    │
     │                            |                                    │
     │ |-------|-------|----------------|------------------------------│
     │ ---------------------------|                                    │
     │ | 1     | WS-15 | core/state/    | Move db.py, bundles.py,      │
     │ crud_operations.py, worktree.py |                               │
     │ | 2     | WS-16 | core/engine/   | Move orchestrator.py,        │
     │ scheduler.py, executor.py         |                             │
     │ | 3     | WS-17 | core/planning/ | Move planner.py (stub)       │
     │                            |                                    │
     │                                                                 │
     │ Critical: Convert re-export stubs to actual implementations     │
     │ - Currently 21 files in core/ are just from src.pipeline.X      │
     │ import *                                                        │
     │ - Must move actual code, update 50+ imports                     │
     │                                                                 │
     │ Validation: python scripts/init_db.py, python                   │
     │ scripts/run_workstream.py --dry-run                             │
     │                                                                 │
     │ ---                                                             │
     │ Phase 8: Integration (22-30 hours)                              │
     │                                                                 │
     │ Can overlap - HIGH RISK                                         │
     │                                                                 │
     │ | WS    | Target   | Key Tasks                                 |│
     │ |-------|----------|-------------------------------------------|│
     │ | WS-18 | scripts/ | Update 30+ script imports                 |│
     │ | WS-19 | tests/   | Update all test imports, verify 100% pass |│
     │                                                                 │
     │ Validation: pwsh scripts/test.ps1, python -m pytest tests/ -q   │
     │                                                                 │
     │ ---                                                             │
     │ Phase 9: Documentation & Enforcement (11-14 hours)              │
     │                                                                 │
     │ | WS    | Target  | Key Tasks                                   │
     │           |                                                     │
     │ |-------|---------|---------------------------------------------│
     │ ----------|                                                     │
     │ | WS-20 | docs    | Create SECTION_REFACTOR_MAPPING.md,         │
     │ verification docs |                                             │
     │ | WS-21 | CI gate | Optional - enforce path standards in CI     │
     │           |                                                     │
     │                                                                 │
     │ ---                                                             │
     │ Summary                                                         │
     │                                                                 │
     │ | Metric            | Value                     |               │
     │ |-------------------|---------------------------|               │
     │ | Total Workstreams | 21                        |               │
     │ | Completed         | 5 (WS-01, 02, 03, 04, 05) |               │
     │ | Remaining         | 16                        |               │
     │ | Estimated Hours   | 131-178 hours             |               │
     │ | Files to Move     | ~70                       |               │
     │ | Imports to Update | 105+ across 47+ files     |               │
     │                                                                 │
     │ Critical Path                                                   │
     │                                                                 │
     │ WS-08 → WS-09 → WS-10 → WS-12 → WS-13 → WS-14 → WS-15 → WS-16 → │
     │ WS-19                                                           │
     │                                                                 │
     │ Rollback Strategy                                               │
     │                                                                 │
     │ - Git tag before each phase: pre-phase-N-baseline               │
     │ - Current stubs support safe rollback                           │
     │ - Test diff comparison pre/post migratio