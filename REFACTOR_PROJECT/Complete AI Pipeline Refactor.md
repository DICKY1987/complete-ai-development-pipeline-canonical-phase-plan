  Phase Plan: Complete AI Pipeline Refactor

  Current State

  - WS-08 (Aider): ✅ COMPLETED - Shim pattern established
  - Core shims: Re-export stubs in place for all 22 modules
  - Remaining: WS-06, WS-07, WS-09 through WS-21

  ---
  Execution Phases

  PHASE A: Section Consolidations (Low-Medium Risk)

  Can run in parallel after pre-checks

  | WS    | Task        | Risk | Key Moves                                                 |
  |-------|-------------|------|-----------------------------------------------------------|
  | WS-06 | AIM section | MED  | src/pipeline/aim_bridge.py → aim/bridge.py, shim original |
  | WS-07 | PM/CCPM     | MED  | src/integrations/github_sync.py → pm/integrations/        |
  | WS-09 | Spec tools  | MED  | tools/spec_*/ → spec/tools/ (5 directories)               |

  Validation: Run python scripts/aim_status.py, spec generation scripts

  ---
  PHASE B: OpenSpec Integration (Medium Risk)

  Sequential, soft dependencies

  | WS    | Task                 | Risk | Key Work                                                  |
  |-------|----------------------|------|-----------------------------------------------------------|
  | WS-10 | OpenSpec integration | MED  | Validate parser/converter alignment, run acceptance tests |
  | WS-11 | Spec docs            | LOW  | Update docs/spec/ references, regenerate indices          |

  Validation: python scripts/generate_spec_index.py, python scripts/generate_spec_mapping.py

  ---
  PHASE C: Error Subsystem (VERY HIGH Risk)

  STRICTLY SEQUENTIAL - most impactful changes

  | WS    | Task          | Risk      | Key Moves                                                         |
  |-------|---------------|-----------|-------------------------------------------------------------------|
  | WS-12 | Planning ADR  | LOW       | No code moves - analysis only                                     |
  | WS-13 | Error plugins | VERY HIGH | src/plugins/ (21 plugins) → error/plugins/, update 60+ imports    |
  | WS-14 | Error engine  | VERY HIGH | MOD_ERROR_PIPELINE/*.py + src/pipeline/error_*.py → error/engine/ |

  Validation per step:
  - WS-13: python -m pytest tests/plugins/ -v
  - WS-14: python -m pytest tests/test_engine_determinism.py tests/plugins/test_integration.py

  ---
  PHASE D: Core Extraction (VERY HIGH Risk)

  STRICTLY SEQUENTIAL - foundation chain

  | WS    | Task          | Risk      | Key Moves                                                                                             | Lines |
  |-------|---------------|-----------|-------------------------------------------------------------------------------------------------------|-------|
  | WS-15 | Core state    | VERY HIGH | db.py, db_sqlite.py, crud_operations.py, bundles.py, worktree.py → core/state/                        | 1,541 |
  | WS-16 | Core engine   | VERY HIGH | orchestrator.py, tools.py, scheduler.py, executor.py, circuit_breakers.py, recovery.py → core/engine/ | 932   |
  | WS-17 | Core planning | MED       | planner.py, archive.py → core/planning/                                                               | 70    |

  Critical path: WS-15 → WS-16 → WS-17 (state → engine → planning)

  Validation per step:
  - WS-15: python scripts/init_db.py && python scripts/validate_workstreams.py
  - WS-16: python scripts/run_workstream.py --dry-run --ws-id <test>
  - WS-17: Full test suite

  ---
  PHASE E: Post-Refactor Cleanup (Medium Risk)

  Can parallelize after WS-17

  | WS    | Task                   | Risk | Key Work                                     |
  |-------|------------------------|------|----------------------------------------------|
  | WS-18 | Infrastructure scripts | MED  | Update all scripts/*.py imports to new paths |
  | WS-19 | Test suite updates     | MED  | Update all tests/*.py imports to new paths   |
  | WS-20 | Final doc mapping      | LOW  | Update docs/ references                      |
  | WS-21 | CI gate standards      | LOW  | Update GitHub workflows, CI path validation  |

  Validation: Full CI run with pwsh ./scripts/test.ps1

  ---
  Risk Mitigation Strategy

  Pre-Flight Checks (Before Each WS)

  1. Run baseline tests: python -m pytest -q
  2. Verify no uncommitted changes: git status
  3. Review workstream JSON for exact file list

  Shim Pattern (During Moves)

  # Original file becomes shim
  from core.state.db import *  # type: ignore F401,F403

  Rollback Plan

  - Keep original files as shims (not deleted)
  - Git commit after each WS completion
  - Can revert individual WS if needed

  ---
  Execution Order

  PHASE A (parallel): WS-06 | WS-07 | WS-09
           ↓
  PHASE B (sequential): WS-10 → WS-11
           ↓
  PHASE C (sequential): WS-12 → WS-13 → WS-14
           ↓
  PHASE D (sequential): WS-15 → WS-16 → WS-17
           ↓
  PHASE E (parallel): WS-18 | WS-19 | WS-20 | WS-21

  ---
  Estimated Effort by Phase

  | Phase | Workstreams | Risk Level | Import Updates | Test Updates |
  |-------|-------------|------------|----------------|--------------|
  | A     | 3           | Medium     | ~15            | ~5           |
  | B     | 2           | Medium     | ~10            | ~3           |
  | C     | 3           | Very High  | ~80            | ~25          |
  | D     | 3           | Very High  | ~100           | ~30          |
  | E     | 4           | Medium     | ~40            | ~20          |

  ---
  Next Actions

  Ready to begin Phase A: WS-06, WS-07, WS-09 can execute in parallel.