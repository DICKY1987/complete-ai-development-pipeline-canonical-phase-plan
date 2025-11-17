
     ╭─────────────────────────────────────────────────────────────────────────╮
     │ Section-Aware Repo Refactor: Workstream Plan                            │
     │                                                                         │
     │ Strategy Overview                                                       │
     │                                                                         │
     │ Following the spec's recommendation: Build the Path Indexer first, then │
     │ use it to execute a data-driven section refactor across 20+ workstreams │
     │ organized into 9 execution phases.                                      │
     │                                                                         │
     │ Key Principles                                                          │
     │                                                                         │
     │ - Data-driven: Indexer provides ground truth for all hardcoded paths    │
     │ - Parallelization: 7-9 workstreams can run concurrently in Groups 1-2   │
     │ - Risk management: Low-risk isolated sections first, high-risk core last│
     │ - Dependency ordering: 6 sequential phases for tightly coupled          │
     │ components                                                              │
     │ - Continuous verification: Each workstream includes tests               │
     │                                                                         │
     │ ---                                                                     │
     │ Phase 1: Foundation (Indexer Implementation)                            │
     │                                                                         │
     │ WS-01: Hardcoded Path Index System ⚙️                                   │
     │                                                                         │
     │ Scope: Implement Part B entirely - scanner + SQLite database            │
     │ Files Created:                                                          │
     │ - tools/hardcoded_path_indexer.py - Scanner implementation              │
     │ - scripts/paths_index_cli.py - CLI interface                            │
     │ - refactor_paths.db - SQLite database with schema                       │
     │ - docs/HARDCODED_PATH_INDEXER.md - Usage documentation                  │
     │                                                                         │
     │ Key Features:                                                           │
     │ - Scan Python imports, filesystem calls, configs, CI, docs              │
     │ - Classify occurrences by kind (code_import, config_path, etc.)         │
     │ - Track patterns: src/pipeline, MOD_ERROR_PIPELINE, PHASE_DEV_DOCS, etc.│
     │ - CLI: scan, report, summary, export                                    │
     │                                                                         │
     │ Deliverables: Working indexer + initial full scan results               │
     │ Risk: LOW (new code, no conflicts)                                      │
     │ Estimated Effort: 8-12 hours                                            │
     │                                                                         │
     │ ---                                                                     │
     │ Phase 2: Planning & Configuration                                       │
     │                                                                         │
     │ WS-02: Section Mapping Configuration 📋                                 │
     │                                                                         │
     │ Scope: Define target directory structure                                │
     │ Dependencies: WS-01 (uses scan results)                                 │
     │ Files Created:                                                          │
     │ - config/section_map.yaml - Authoritative section mapping               │
     │ - docs/SECTION_REFACTOR_PLAN.md - Refactor execution plan               │
     │                                                                         │
     │ Analysis: Use indexer scan to identify:                                 │
     │ - Highest-impact patterns (most occurrences)                            │
     │ - Section boundary violations                                           │
     │ - Circular dependencies                                                 │
     │                                                                         │
     │ Deliverables: Complete section mapping with old→new path translations   │
     │ Risk: LOW (planning only)                                               │
     │ Estimated Effort: 4-6 hours                                             │
     │                                                                         │
     │ ---                                                                     │
     │ Phase 3: Isolated Sections (Parallel Group 1)                           │
     │                                                                         │
     │ Can execute WS-03, WS-04, WS-05 in parallel after WS-02.                │
     │                                                                         │
     │ WS-03: Refactor Meta Section 📚                                         │
     │                                                                         │
     │ Target: meta/ ← PHASE_DEV_DOCS/, plans/, Coordination Mechanisms/       │
     │ Files: 50+ markdown files (phase plans, coordination docs)              │
     │ Changes: Update path references in docs only                            │
     │ Risk: LOW (no code)                                                     │
     │ Effort: 4-6 hours                                                       │
     │                                                                         │
     │ WS-04: Refactor GUI Section 🖥                                          │
     │                                                                         │
     │ Target: gui/ ← GUI_PIPELINE/, GUI docs                                  │
     │ Files: GUI planning directory (stub implementation)                     │
     │ Changes: Move directory, update doc references                          │
     │ Risk: LOW (no real implementation yet)                                  │
     │ Effort: 2-4 hours                                                       │
     │                                                                         │
     │ WS-05: Refactor Infra Section - CI Foundation ⚡                        │
     │                                                                         │
     │ Target: infra/ci/ ← .github/workflows/, test configs                    │
     │ Files: CI workflows, pytest.ini, requirements.txt, sandbox_repos/       │
     │ Changes: Move configs, update workflow paths                            │
     │ Risk: LOW-MEDIUM (CI important but isolated)                            │
     │ Effort: 4-6 hours                                                       │
     │                                                                         │
     │ ---                                                                     │
     │ Phase 4: Moderately Isolated Sections (Parallel Group 2)                │
     │                                                                         │
     │ Can execute WS-06, WS-07, WS-08 in parallel after Phase 3.              │
     │                                                                         │
     │ WS-06: Refactor AIM Section 🔧                                          │
     │                                                                         │
     │ Target: aim/ ← src/pipeline/aim_bridge.py, .AIM_ai-tools-registry/      │
     │ Files: AIM bridge (469 LOC), registry, 2 scripts, config                │
     │ Changes:                                                                │
     │ - Move aim_bridge.py → aim/bridge.py                                    │
     │ - Update imports in tools.py                                            │
     │ - Update AIM scripts                                                    │
     │ Risk: MEDIUM (clear interface)                                          │
     │ Effort: 6-8 hours                                                       │
     │                                                                         │
     │ WS-07: Refactor PM Section - CCPM 📊                                    │
     │                                                                         │
     │ Target: pm/ ← ccpm/ (70+ files), src/integrations/github_sync.py        │
     │ Files: CCPM commands/agents/rules, GitHub sync, PM scripts              │
     │ Changes:                                                                │
     │ - Move entire ccpm/ directory                                           │
     │ - Move github_sync.py → pm/integrations/                                │
     │ - Update CCPM install/update scripts                                    │
     │ Risk: MEDIUM (large but self-contained)                                 │
     │ Effort: 8-10 hours                                                      │
     │                                                                         │
     │ WS-08: Refactor Aider Section 🤖                                        │
     │                                                                         │
     │ Target: aider/ ← src/pipeline/prompts.py, templates/, AIDER_PROMNT_HELP/│
     │ Files: Prompts module (212 LOC), Jinja2 templates, help docs            │
     │ Changes:                                                                │
     │ - Move prompts.py → aider/engine.py                                     │
     │ - Move templates → aider/templates/                                     │
     │ - Update orchestrator imports                                           │
     │ Risk: MEDIUM (used by orchestrator)                                     │
     │ Effort: 6-8 hours                                                       │
     │                                                                         │
     │ ---                                                                     │
     │ Phase 5: Spec Tooling (Sequential)                                      │
     │                                                                         │
     │ WS-09 → WS-10 → WS-11 must run sequentially due to internal             │
     │ dependencies.                                                           │
     │                                                                         │
     │ WS-09: Refactor Spec Section - Tools Foundation 🛠                      │
     │                                                                         │
     │ Target: spec/tools/ ← tools/ (5 spec modules)                           │
     │ Files: indexer, resolver, renderer, patcher, guard                      │
     │ Changes: Move tools, update spec scripts                                │
     │ Risk: MEDIUM (used by parser/scripts)                                   │
     │ Effort: 6-8 hours                                                       │
     │                                                                         │
     │ WS-10: Refactor Spec Section - OpenSpec Integration 📝                  │
     │                                                                         │
     │ Target: spec/ ← OpenSpec parser/converter, openspec/, bundles/          │
     │ Dependencies: WS-09 (spec tools)                                        │
     │ Files: openspec_parser.py (312 LOC), openspec_convert.py (104 LOC),     │
     │ spec_index.py (331 LOC)                                                 │
     │ Changes:                                                                │
     │ - Move parser/converter → spec/engine/                                  │
     │ - Update CCPM integration                                               │
     │ - Update spec scripts (3 files)                                         │
     │ Risk: MEDIUM-HIGH (used by CCPM workflow)                               │
     │ Effort: 10-12 hours                                                     │
     │                                                                         │
     │ WS-11: Refactor Spec Section - Documentation 📖                         │
     │                                                                         │
     │ Target: spec/docs/ ← Multi-Document Versioning Automation               │
     │ final_spec_docs/                                                        │
     │ Dependencies: WS-10                                                     │
     │ Files: Complete spec documentation directory                            │
     │ Changes: Move directory, update references in docs                      │
     │ Risk: LOW (docs only)                                                   │
     │ Effort: 3-4 hours                                                       │
     │                                                                         │
     │ ---                                                                     │
     │ Phase 6: Error Pipeline (Sequential)                                    │
     │                                                                         │
     │ WS-12 → WS-13 → WS-14 must run sequentially. Critical decision point at │
     │ WS-12.                                                                  │
     │                                                                         │
     │ WS-12: Refactor Error Section - Shared Utilities 🔄                     │
     │                                                                         │
     │ Target: shared/utils/ OR error/shared/utils/ ← src/utils/               │
     │ Files: types.py, time.py, hashing.py, jsonl_manager.py, env.py          │
     │ Impact: 30+ import updates across ALL plugins and pipeline modules      │
     │                                                                         │
     │ Decision Required:                                                      │
     │ - Option A: Keep at top level as shared/utils/ (less churn)             │
     │ - Option B: Move to error/shared/utils/ (true section isolation)        │
     │                                                                         │
     │ Risk: VERY HIGH (affects everything)                                    │
     │ Effort: 8-10 hours                                                      │
     │                                                                         │
     │ WS-13: Refactor Error Section - Plugins 🔌                              │
     │                                                                         │
     │ Target: error/plugins/ ← src/plugins/ (21 plugins)                      │
     │ Dependencies: WS-12 (utils path must be stable)                         │
     │ Files: 21 plugin packages, plugin docs                                  │
     │ Changes: Update all imports from utils, update plugin manager           │
     │ Risk: HIGH (21 plugins, extensive testing needed)                       │
     │ Effort: 12-16 hours                                                     │
     │                                                                         │
     │ WS-14: Refactor Error Section - Engine Consolidation ⚠️                 │
     │                                                                         │
     │ Target: error/engine/ ← MOD_ERROR_PIPELINE/, src/pipeline/error_*.py    │
     │ Dependencies: WS-12, WS-13                                              │
     │ Files: Consolidate 8 error modules from 2 locations                     │
     │ Changes:                                                                │
     │ - Merge MOD_ERROR_PIPELINE/ → error/engine/                             │
     │ - Move error_*.py → error/engine/                                       │
     │ - Update orchestrator imports                                           │
     │ Risk: HIGH (used by core)                                               │
     │ Effort: 10-12 hours                                                     │
     │                                                                         │
     │ ---                                                                     │
     │ Phase 7: Core Pipeline (Sequential - Highest Risk)                      │
     │                                                                         │
     │ WS-15 → WS-16 → WS-17 must run sequentially. Save for last.             │
     │                                                                         │
     │ WS-15: Refactor Core Section - State & Data 💾                          │
     │                                                                         │
     │ Target: core/state/ ← DB, bundles, worktree modules                     │
     │ Dependencies: ALL previous sections                                     │
     │ Files: db.py, crud_operations.py, bundles.py, worktree.py, schemas      │
     │ Changes: Update 50+ imports across scripts/tests                        │
     │ Risk: VERY HIGH (foundation for orchestration)                          │
     │ Effort: 12-16 hours                                                     │
     │                                                                         │
     │ WS-16: Refactor Core Section - Orchestration 🎯                         │
     │                                                                         │
     │ Target: core/engine/ ← Orchestrator, scheduler, executor, tools         │
     │ Dependencies: WS-15, ALL previous sections                              │
     │ Files: orchestrator.py, scheduler.py, executor.py, tools.py,            │
     │ circuit_breakers.py, recovery.py, parallel.py                           │
     │ Changes: Update 40+ imports, critical path testing                      │
     │ Risk: VERY HIGH (heart of the system)                                   │
     │ Effort: 16-20 hours                                                     │
     │                                                                         │
     │ WS-17: Refactor Core Section - Planning 📅                              │
     │                                                                         │
     │ Target: core/planning/ ← planner.py, archive.py                         │
     │ Dependencies: WS-16                                                     │
     │ Files: Planner and archive utilities (stubs)                            │
     │ Changes: Update imports                                                 │
     │ Risk: MEDIUM (not heavily used)                                         │
     │ Effort: 3-4 hours                                                       │
     │                                                                         │
     │ ---                                                                     │
     │ Phase 8: Integration Layer (Can partially parallelize)                  │
     │                                                                         │
     │ WS-18: Update Infrastructure Scripts 📜                                 │
     │                                                                         │
     │ Target: infra/scripts/ OR keep at top-level scripts/                    │
     │ Dependencies: ALL previous workstreams                                  │
     │ Files: 30 script files (15 Python + 15 PowerShell/Bash)                 │
     │ Changes: Update all imports to new section paths                        │
     │ Risk: HIGH (integration points)                                         │
     │ Effort: 10-14 hours                                                     │
     │                                                                         │
     │ WS-19: Test Suite Updates ✅                                            │
     │                                                                         │
     │ Target: Keep at top-level tests/                                        │
     │ Dependencies: ALL previous workstreams                                  │
     │ Files: 20+ test files across 3 subdirectories                           │
     │ Changes: Update imports, fixtures, test data paths                      │
     │ Risk: HIGH (validates entire refactor)                                  │
     │ Effort: 12-16 hours                                                     │
     │                                                                         │
     │ Note: WS-18 and WS-19 can partially overlap if careful about file       │
     │ conflicts.                                                              │
     │                                                                         │
     │ ---                                                                     │
     │ Phase 9: Documentation & Enforcement                                    │
     │                                                                         │
     │ WS-20: Final Documentation & Mapping 📋                                 │
     │                                                                         │
     │ Dependencies: ALL workstreams                                           │
     │ Deliverables:                                                           │
     │ - docs/SECTION_REFACTOR_MAPPING.md - Complete old→new path mapping      │
     │ - docs/SECTION_REFACTOR_VERIFICATION.md - Test results, validation log  │
     │ - Update CLAUDE.md, README.md, AGENTS.md with new structure             │
     │ - Update all architectural docs                                         │
     │                                                                         │
     │ Risk: MEDIUM (comprehensive but docs only)                              │
     │ Effort: 8-10 hours                                                      │
     │                                                                         │
     │ WS-21: CI Gate for Path Standards (Optional) 🚦                         │
     │                                                                         │
     │ Target: .github/workflows/path_standards.yml                            │
     │ Dependencies: WS-01, all refactor workstreams                           │
     │ Purpose: Prevent regression - fail CI on deprecated path patterns       │
     │ Risk: LOW (new file)                                                    │
     │ Effort: 3-4 hours                                                       │
     │                                                                         │
     │ ---                                                                     │
     │ Execution Summary                                                       │
     │                                                                         │
     │ Parallelization Opportunities                                           │
     │                                                                         │
     │ - Group 1 (3 parallel): WS-03, WS-04, WS-05 (Meta, GUI, Infra)          │
     │ - Group 2 (3 parallel): WS-06, WS-07, WS-08 (AIM, PM, Aider)            │
     │ - Sequential phases: Spec (3), Error (3), Core (3), Integration (2)     │
     │                                                                         │
     │ Total Workstreams: 21                                                   │
     │                                                                         │
     │ - Parallel-capable: 6 workstreams                                       │
     │ - Sequential-required: 15 workstreams                                   │
     │ - Execution waves: ~12-14 waves with optimal parallelization            │
     │                                                                         │
     │ Estimated Total Effort                                                  │
     │                                                                         │
     │ - Optimistic (with parallelization): 120-140 hours                      │
     │ - Realistic (sequential + some parallel): 160-200 hours                 │
     │ - Per workstream average: 6-10 hours                                    │
     │                                                                         │
     │ Critical Decisions                                                      │
     │                                                                         │
     │ 1. WS-12: Shared utils placement (shared/utils/ vs error/shared/utils/) │
     │ 2. WS-18: Scripts location (infra/scripts/ vs top-level scripts/)       │
     │ 3. Verification strategy: Test after each workstream vs batch testing   │
     │                                                                         │
     │ Success Criteria                                                        │
     │                                                                         │
     │ - ✅ All tests pass after refactor                                      │
     │ - ✅ Zero occurrences of deprecated paths in indexer                    │
     │ - ✅ CI enforces path standards                                         │
     │ - ✅ Complete mapping documentation                                     │
     │ - ✅ Behavioral equivalence verified                                    │
     │                                                                         │
     │                                                                         │
     │                                                                         │
     │                                                                         │
     │                                                                         │
     │                                                                         │
     ╰─────────────────────────────────────────────────────────────────────────╯



