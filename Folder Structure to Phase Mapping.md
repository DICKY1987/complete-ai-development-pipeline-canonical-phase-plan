 Folder Structure to Phase Mapping

 Task

 Map the current folder structure and subfolders to the 8 phases (0-7) described in "Phase-Based AI Dev Pipeline (0–7)
 – Coherent Process.md"

 ---
 Complete Folder-to-Phase Mapping

 PHASE 0: Bootstrap & Initialization

 Purpose: Detect repo, pick profile, validate baseline, generate PROJECT_PROFILE.yaml + router_config.json

 Primary Folders

 - core/bootstrap/ - ✅ Complete (100%)
   - orchestrator.py - 4-step bootstrap orchestrator
   - discovery.py - ProjectScanner (repo detection)
   - selector.py - Profile selection (5 profiles)
   - generator.py - Artifact generation
   - validator.py - Baseline validation

 Supporting Folders

 - schema/ - JSON schemas (17 files) for validation
 - config/ - Profile configurations

 Test Coverage

 - 8 passing tests

 ---
 PHASE 1: Planning & Spec Alignment

 Purpose: Load specs, validate, convert specs → workstreams, attach patterns

 Primary Folders

 - core/planning/ - ⚠️ Partial (40%)
   - planner.py - Workstream planner (STUB)
   - ccpm_integration.py - CCPM/PM integration (partial)
   - archive.py - Historical archival
 - specifications/specs/ - ✅ Specification files
   - Core specs (10 files)
   - Planning docs (4 files)
   - Instance examples (2 files)
 - UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/specs/ - ✅ Framework specs
   - specs/core/ - 10 production specs:
       - UET_BOOTSTRAP_SPEC.md
     - UET_COOPERATION_SPEC.md
     - UET_PHASE_SPEC_MASTER.md
     - UET_WORKSTREAM_SPEC.md
     - UET_TASK_ROUTING_SPEC.md
     - UET_PROMPT_RENDERING_SPEC.md
     - UET_PATCH_MANAGEMENT_SPEC.md
     - UET_CLI_TOOL_EXECUTION_SPEC.md
     - UTE_ID_SYSTEM_SPEC.md
     - UET_EXECUTION_KERNEL_PARALLELISM_STRATEGY_SPEC_V2.md
   - specs/instances/ - Example instances
   - specs/planning/ - Planning documentation
   - specs/archive/ - Historical specs

 Supporting Folders

 - patterns/ - Pattern library and templates
   - EXECUTION_PATTERNS_LIBRARY.md
   - EXECUTION_ACCELERATION_ANALYSIS.md
   - ANTI_PATTERN_GUARDS.md
   - examples/, decisions/, automation/, executors/, metrics/
 - aim/ - AI tool capability matching bridge

 Test Coverage

 - 0 tests (no implementation)

 ---
 PHASE 2: Request Building & Run Creation

 Purpose: Build ExecutionRequest, validate schema, create run records in DB

 Primary Folders

 - core/engine/ - ✅ Complete (100%)
   - execution_request_builder.py - Fluent API for requests
 - core/state/ - ✅ Complete (100%)
   - db.py - SQLite database singleton
   - db_unified.py - Unified DB interface
   - crud.py - CRUD operations
   - bundles.py - Run/workstream bundles
   - task_queue.py - Task queue
   - worktree.py - Worktree state
   - audit_logger.py - Audit trail

 Supporting Folders

 - schema/ - Validation schemas
   - execution_request.v1.json
   - run_record.v1.json
   - workstream_spec.v1.json
   - step_attempt.v1.json
   - run_event.v1.json
 - .state/ - Working state
   - orchestrator.db, orchestration.db
   - transitions.jsonl
 - .ledger/ - Audit ledger
   - framework.db

 Test Coverage

 - ~50 tests for state management

 ---
 PHASE 3: Scheduling & Task Graph

 Purpose: Load workstreams, build DAG, resolve dependencies, fill task queue

 Primary Folders

 - core/engine/ - ✅ Complete (100%)
   - scheduler.py - DAG-based task scheduler
   - dag_builder.py - DAG construction
   - state_machine.py - Task lifecycle states
 - core/state/ - ✅ Complete (100%)
   - dag_utils.py - Cycle detection, topological sort
   - task_queue.py - FIFO queue for tasks

 Specifications

 - UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/uet/uet_v2/
   - DAG_SCHEDULER.md - DAG scheduling details
   - STATE_MACHINES.md - State machine definitions
 - specifications/specs/
   - UET_EXECUTION_KERNEL_PARALLELISM_STRATEGY_SPEC_V2.md

 Test Coverage

 - ~92 tests for engine components

 ---
 PHASE 4: Tool Routing & Adapter Selection

 Purpose: Match task → tool profiles, select adapter, validate tool config

 Primary Folders

 - core/engine/ - ⚠️ Partial (60%)
   - router.py - Task routing logic
   - tools.py - Tool registry and selection
 - core/adapters/ - ⚠️ Partial (60%)
   - base.py - ToolAdapter base class
   - registry.py - AdapterRegistry
   - subprocess_adapter.py - Basic subprocess adapter
   - MISSING: ToolProcessPool, ClusterManager, Aider adapter, Codex adapter

 Supporting Folders

 - aim/ - AI tool capability matching
   - bridge/ - Capability matching algorithms
   - capabilities/ - Tool capability definitions
 - config/ - Tool profiles
   - UTE_QUALITY_GATE.yaml - Validation gates

 Specifications

 - UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/uet/uet_v2/
   - COMPONENT_CONTRACTS.md - Tool contracts
 - specifications/specs/
   - UET_TASK_ROUTING_SPEC.md

 Test Coverage

 - ~27 tests for adapters

 ---
 PHASE 5: Execution & Validation

 Purpose: Invoke adapter, run tool, capture output, run acceptance tests, update state

 Primary Folders

 - core/engine/ - ⚠️ Partial (50%)
   - executor.py - Main executor (STUB - TODO only!)
   - process_spawner.py - Subprocess management ✅
   - integration_worker.py - Worker integration ✅
   - test_gate.py - Acceptance test framework ✅
   - recovery.py - Recovery handlers ✅
   - patch_ledger.py - Patch tracking ✅
   - patch_converter.py - Patch conversion ✅
 - core/engine/resilience/ - ✅ Complete (100%)
   - circuit_breaker.py - Circuit breaker (CLOSED/OPEN/HALF_OPEN)
   - retry.py - Exponential backoff, retry logic
   - resilient_executor.py - Resilient execution wrapper
 - core/engine/monitoring/ - ✅ Complete (100%)
   - progress_tracker.py - Task progress tracking
   - run_monitor.py - Run-level monitoring

 Supporting Folders

 - error/engine/ - Error detection hooks
   - error_engine.py - Error detection (shim)
   - plugin_manager.py - Plugin orchestration
 - core/state/ - State updates
   - audit_logger.py - Execution audit

 Test Coverage

 - ~32 tests for resilience patterns

 ---
 PHASE 6: Error Analysis, Auto-Fix & Escalation

 Purpose: Detect errors via plugins, classify, auto-fix, circuit breaker, escalate

 Primary Folders

 - error/engine/ - ⚠️ Partial (60%)
   - error_engine.py - Main error engine (SHIM - imports from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK)
   - error_state_machine.py - Error lifecycle ✅
   - error_context.py - Error context capture ✅
   - pipeline_engine.py - Error pipeline orchestration ✅
   - plugin_manager.py - Plugin discovery/loading ✅
   - file_hash_cache.py - Change detection ✅
 - error/plugins/ - ✅ 21 plugins (100%)
   - Python: python_ruff/, python_mypy/, python_pylint/, python_pyright/, python_bandit/, python_safety/,
 python_black_fix/, python_isort_fix/
   - JavaScript: js_eslint/, js_prettier_fix/
   - Markdown: md_markdownlint/, md_mdformat_fix/
   - YAML: yaml_yamllint/
   - PowerShell: powershell_pssa/
   - Security: semgrep/, gitleaks/
   - Utilities: path_standardizer/, test_runner/, codespell/, json_jq/
 - error/shared/ - ✅ Shared utilities
   - utils/ - Common error functions

 Supporting Folders

 - core/engine/resilience/ - Fault tolerance
   - circuit_breaker.py - Protection from runaway retries
   - retry.py - Retry strategies
 - core/engine/recovery.py - Recovery logic

 Test Coverage

 - ~50+ tests for plugins and pipeline

 ---
 PHASE 7: Monitoring, Completion & Archival

 Purpose: Live monitoring, dashboards, run completion, artifact archival, reporting

 Primary Folders

 - core/ - ⚠️ Partial (30%)
   - ui_cli.py - CLI dashboard interface (minimal)
   - ui_models.py - UI data models ✅
   - ui_settings.py - UI configuration ✅
   - ui_settings_cli.py - CLI settings ✅
 - core/engine/monitoring/ - ✅ Complete (100%)
   - progress_tracker.py - Progress visualization
   - run_monitor.py - Run status tracking
 - core/planning/ - ✅ Archival
   - archive.py - Artifact archival

 Supporting Folders

 - gui/ - ⚠️ Partial GUI implementations
   - ui_infrastructure_usage.py - Infrastructure dashboard
   - ui_tool_selection_demo.py - Tool selection UI
 - docs/ - Documentation output
 - patterns/docs/ - Pattern documentation

 Missing Components

 - ❌ Dashboard/TUI (rich CLI)
 - ❌ Web UI
 - ❌ Artifact compression
 - ❌ Report generation templates
 - ❌ Metrics export (Prometheus, etc.)
 - ❌ Historical run analysis

 Test Coverage

 - ~15 tests for monitoring components

 ---
 CROSS-CUTTING FOLDERS (Support Multiple Phases)

 Schema Layer (Foundation for All Phases)

 schema/ - ✅ 17 JSON schemas (100%)
 - ai_module_manifest.schema.json - Module identification
 - bootstrap_discovery.v1.json - Bootstrap (Phase 0)
 - execution_request.v1.json - Request building (Phase 2)
 - execution_pattern.v1.json - Patterns
 - patch_artifact.v1.json, patch_ledger_entry.v1.json - Patches (Phase 5)
 - pattern_spec.v1.json, pattern_instance.v1.json - Patterns
 - phase_spec.v1.json, phase_template.v1.json - Phases (Phase 1)
 - project_profile.v1.json - Profiles (Phase 0)
 - router_config.v1.json - Routing (Phase 4)
 - run_record.v1.json, run_event.v1.json - Runs (Phase 2)
 - step_attempt.v1.json - Steps (Phase 2)
 - task_spec.v1.json - Tasks (Phase 3)
 - test_gate.v1.json - Validation (Phase 5)
 - verification_template.v1.json - Verification (Phase 5)
 - worker_lifecycle.v1.json - Workers (Phase 5)
 - workstream_spec.v1.json - Workstreams (Phase 1)

 Type: Data contracts (zero dependencies)

 ---
 Patterns Library (Templates Across All Phases)

 patterns/ - ✅ Complete pattern system
 - EXECUTION_PATTERNS_LIBRARY.md - 24,524 bytes of patterns
 - EXECUTION_ACCELERATION_ANALYSIS.md - Analysis and extraction
 - ANTI_PATTERN_GUARDS.md - Anti-patterns to avoid
 - examples/ - Pattern examples
 - decisions/ - Decision patterns
 - automation/ - Automation patterns
 - executors/ - Executor patterns
 - metrics/ - Metrics and telemetry patterns
 - docs/ - Pattern documentation

 Phases Used: All (0-7)

 ---
 Tools & Specifications (Tooling for Framework)

 tools/ - Specification management tools
 - guard/ - Schema validation
 - indexer/ - Index generation
 - patcher/ - Patch application
 - renderer/ - Template rendering
 - resolver/ - Dependency resolution
 - validation/ - Validation tools
 - generation/ - Code generation

 SPEC_tools/ - Additional spec tools

 specifications/specs/ - Executable specs and documentation

 Phases Used: Primarily Phase 1 (Planning)

 ---
 AIM (AI Tool Matching Bridge)

 aim/ - Tool capability matching
 - bridge/ - Capability matching algorithms
 - capabilities/ - Tool capability definitions
 - audit.py - Audit and logging
 - exceptions.py - Custom exceptions
 - pipeline_phase_plan_files.txt - Phase reference

 Phases Used: Phase 4 (Tool Routing), Phase 5 (Execution)

 ---
 Configuration (Framework-Wide Settings)

 config/ - Shared configuration
 - UTE_ai_policies.yaml - AI policies and restrictions
 - UTE_QUALITY_GATE.yaml - Validation gates
 - pyproject.toml - Python project config
 - .invoke.yaml.example - Invoke task config

 .claude/ - Claude Code settings
 .github/ - GitHub CI/CD, Copilot instructions

 Phases Used: All (0-7)

 ---
 Documentation & References

 UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/ - Framework documentation
 - specs/ - Specification tier system (Tier 1-4)
 - uet/ - Implementation guides
   - integration/ - Integration documentation
   - planning/ - Analysis and planning
   - uet_v2/ - Component contracts
 - README.md - Master index

 docs/ - Project documentation
 glossary/ - Terminology reference
 specifications/specs/planning/ - Phase planning docs

 Phases Used: All (reference material)

 ---
 Testing Infrastructure

 tests/ - Test suite
 - Test organization mirrors core/ structure
 - Markers: @pytest.mark.unit, .integration, .bootstrap, .engine, .adapter, .resilience, .slow
 - 196 passing tests (for implemented features)

 Phases Tested: 0, 2, 3, 4, 5, 6, 7

 ---
 Scripts & Automation

 scripts/ - Operational scripts
 - validate_workstreams.py - DAG validation (Phase 3)
 - validate_all_schemas.py - Schema validation (Phase 0, 2)
 - run_quality_gates.py - Multi-gate validation (Phase 5)
 - pattern_discovery.py - Pattern extraction (Phase 1)
 - extract_patterns_from_logs.py - Log analysis (Phase 7)
 - validate_extracted_templates.py - Template validation (Phase 1)
 - SCRIPT_INDEX.yaml - Script inventory

 Phases Used: Multiple (operational tooling)

 ---
 State & Persistence

 .state/ - Working state directory
 - orchestrator.db, orchestration.db - SQLite databases
 - transitions.jsonl - State transition log

 .ledger/ - Audit trail
 - framework.db - Ledger database

 Phases Used: 2, 3, 5, 6, 7 (data storage)

 ---
 Workspace Management

 .uet/ - UET workspace
 state/ - Alternative state directory
 plans/ - Plan files (CCPM/phase plans)
 aider/ - Aider configuration

 Phases Used: All (workspace management)

 ---
 MISSING PIECES / ADDITIONAL FINDINGS

 modules/ Directory - CRITICAL FINDING

 Location: C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\modules

 Status: ⚠️ Parallel Implementation / Legacy Code

 This directory contains an alternative implementation with module-based naming (m010001_, m010002_, etc.) that
 duplicates functionality in core/, error/, aim/, and tools/.

 Contents (9 subdirectories)

 1. modules/core-engine/ - 33 files with m010001_ prefix
   - m010001_orchestrator.py, m010001_executor.py, m010001_scheduler.py
   - m010001_dag_builder.py, m010001_process_spawner.py
   - Duplicates Phase 3, 5 functionality from core/engine/
 2. modules/core-state/ - State management with m010003_ prefix
   - Duplicates Phase 2 functionality from core/state/
 3. modules/core-planning/ - Planning modules with m010002_ prefix
   - Duplicates Phase 1 functionality from core/planning/
 4. modules/core-ast/ - AST analysis modules
   - Not mapped to phases; additional tooling
 5. modules/error-engine/ - Error engine with m010004_ prefix
   - Duplicates Phase 6 functionality from error/engine/
 6. modules/error-plugin-*/ - 21 error plugin directories
   - Duplicates Phase 6 plugins from error/plugins/
 7. modules/error-shared/ - Shared error utilities
   - Duplicates error/shared/
 8. modules/pm-integrations/ - Project management integrations
   - Cross-cutting functionality
 9. modules/specifications-tools/ - Spec tools
   - Duplicates tools/ and SPEC_tools/

 Module ID System

 All modules use a structured ID prefix:
 - m010001_* - Core engine modules (Phase 3, 5)
 - m010002_* - Core planning modules (Phase 1)
 - m010003_* - Core state modules (Phase 2)
 - m010004_* - Error engine modules (Phase 6)
 - m010005_* - Error plugins (Phase 6)
 - m020001_* - AIM modules (Phase 4)
 - m030001_* - PM integrations (cross-cutting)

 Duplication Analysis

 | Phase | Primary Location              | Duplicate in modules/                            | Status
      |
 |-------|-------------------------------|--------------------------------------------------|--------------------------
 -----|
 | 0     | core/bootstrap/               | ❌ Not duplicated                                 | Clean
       |
 | 1     | core/planning/                | ✅ modules/core-planning/                         | DUPLICATE
       |
 | 2     | core/state/                   | ✅ modules/core-state/                            | DUPLICATE
       |
 | 3     | core/engine/scheduler.py      | ✅ modules/core-engine/m010001_scheduler.py       | DUPLICATE
       |
 | 4     | core/adapters/, aim/          | ⚠️ Partial in modules/aim-*/                     | PARTIAL DUPLICATE
      |
 | 5     | core/engine/executor.py       | ✅ modules/core-engine/m010001_executor.py        | DUPLICATE (both may be
 stubs) |
 | 6     | error/engine/, error/plugins/ | ✅ modules/error-engine/, modules/error-plugin-*/ | DUPLICATE
       |
 | 7     | core/ui_cli.py                | ❌ Not duplicated                                 | Clean
       |

 Impact on Phase Mapping

 The modules/ directory represents a parallel codebase that was likely:
 1. An earlier implementation with module IDs
 2. Being migrated to the cleaner core/, error/, aim/ structure
 3. Not fully deprecated/removed yet

 Recommendation:
 - DOCUMENT this duplication in the phase mapping
 - VERIFY which implementation is authoritative (likely core/ over modules/)
 - DEPRECATE or ARCHIVE the modules/ directory if core/ is production
 - CONSOLIDATE if both contain unique functionality

 Missing from Original Plan

 The original folder-to-phase mapping completely missed the modules/ directory (86 files, 9 subdirectories). This is a
 significant oversight showing:
 - 📁 Phase 1 has duplicate code in modules/core-planning/
 - 📁 Phase 2 has duplicate code in modules/core-state/
 - 📁 Phase 3 has duplicate scheduler in modules/core-engine/
 - 📁 Phase 5 has duplicate executor in modules/core-engine/
 - 📁 Phase 6 has duplicate error system in modules/error-*/

 ---
 _ARCHIVE/ Directory - RESIDUAL ARCHIVE

 Location: C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\_ARCHIVE

 Status: ⚠️ Partially Cleaned

 According to ARCHIVE_LOCATION.md, most archive content (456 files, ~68 MB) was moved to external storage on
 2025-12-02:
 - External: C:\Users\richg\ALL_AI\Archives\Complete_AI_Development_Pipeline_Archive_2025-12-02/
 - Remaining in repo: _ARCHIVE/patterns/legacy_atoms/ (86 files)

 Contents Still in Repo:
 - _ARCHIVE/patterns/legacy_atoms/ - Legacy pattern atoms

 Impact: Minimal; mostly cleaned up

 ---
 DEPRECATED/ARCHIVE FOLDERS

 _ARCHIVE/ - Residual archived materials (86 files remaining, mostly cleaned)
 modules/ - ⚠️ DUPLICATE/LEGACY module-based implementation (86 files, 9 subdirectories)
 .git/ - Git metadata

 ---
 ORGANIZATIONAL OBSERVATIONS

 ✅ Strengths

 1. Clear Phase Separation (0-3): Phases 0-3 have distinct folders with complete implementations
 2. Comprehensive Schema Layer: 17 schemas provide solid contracts across all phases
 3. Rich Error Plugin System: 21 plugins with unified interface (Phase 6)
 4. Strong Specification Base: 10 core production specs (Phase 1)
 5. Cross-Cutting Patterns: Well-established pattern library

 ⚠️ Areas for Improvement

 1. Phase 5 Executor Missing: core/engine/executor.py is just a TODO stub - critical blocker
 2. Phase 1 Automation Gaps: core/planning/planner.py has stub functions; no OpenSpec parser
 3. Phase 4 Pooling Missing: No ToolProcessPool or ClusterManager for multi-instance management
 4. Phase 7 UI Missing: No dashboard/TUI; only basic monitoring
 5. Phase 6 Dependency: Error engine is borrowed from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK

 🔄 Migration/Duplication Issues

 1. Error Module Duplication:
   - error/engine/ vs error/error-engine/ (with m010004 prefixes)
   - Migration in progress; newer version is error/plugins/
 2. Tools Folder Complexity:
   - tools/guard/ vs tools/spec_guard/
   - Similar duplication for indexer, patcher, renderer, resolver
 3. Specifications Split:
   - specifications/specs/ (active)
   - UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/specs/ (structured reference)
   - Both seem active; consolidation may be needed
 4. State Management:
   - Multiple databases: .state/orchestrator.db, .state/orchestration.db, .ledger/framework.db
   - Indicates evolving architecture

 ---
 QUICK PHASE LOOKUP TABLE

 | Phase         | Primary Folders                                        | Status | Entry Point
   |
 |---------------|--------------------------------------------------------|--------|-----------------------------------
 --|
 | 0             | core/bootstrap/, schema/                               | ✅ 100% | core/bootstrap/orchestrator.py
    |
 | 1             | core/planning/, specifications/, patterns/             | ⚠️ 40% | core/planning/planner.py
   |
 | 2             | core/state/, core/engine/execution_request_builder.py  | ✅ 100% | core/state/db.py
    |
 | 3             | core/engine/scheduler.py, core/engine/dag_builder.py   | ✅ 100% | core/engine/scheduler.py
    |
 | 4             | core/engine/router.py, core/adapters/, aim/            | ⚠️ 60% | core/engine/router.py
   |
 | 5             | core/engine/executor.py, core/engine/monitoring/       | ⚠️ 50% | core/engine/executor.py (STUB)
   |
 | 6             | error/engine/, error/plugins/, core/engine/resilience/ | ⚠️ 60% | error/engine/error_engine.py
 (SHIM) |
 | 7             | core/ui_cli.py, core/engine/monitoring/, docs/         | ⚠️ 30% | core/ui_cli.py
   |
 | Cross-Cutting | schema/, patterns/, config/, tools/, tests/            | ✅ 100% | N/A
    |

 ---
 FOLDER COUNT BY PHASE

 Phase Distribution

 - Phase 0: 2 primary folders + 2 supporting = 4 folders
 - Phase 1: 4 primary folders + 2 supporting = 6 folders
 - Phase 2: 2 primary folders + 4 supporting = 6 folders
 - Phase 3: 2 primary folders + 1 supporting = 3 folders
 - Phase 4: 2 primary folders + 2 supporting = 4 folders
 - Phase 5: 4 primary folders + 2 supporting = 6 folders
 - Phase 6: 4 primary folders + 2 supporting = 6 folders
 - Phase 7: 3 primary folders + 3 supporting = 6 folders
 - Cross-Cutting: 10+ folders (schema, patterns, tools, tests, config, docs, scripts, state, aim, specifications)

 Total Folder Count

 - Phase-Specific: ~35 folders
 - Cross-Cutting: ~15 folders
 - Total: ~50 folders (organized into logical phase structure)

 ---
 SUMMARY

 The folder structure closely aligns with the 8-phase pipeline architecture described in the document. The codebase
 demonstrates:

 1. Clear Separation of Concerns: Each phase has dedicated folders
 2. Layered Architecture: Schema → State → Domain → Orchestration
 3. Cross-Cutting Support: Shared folders (schema, patterns, tools) properly support all phases
 4. Specification-Driven: Specs in specifications/ and UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/ drive implementation

 Main Gaps:
 - Phase 1 automation (planner stubs)
 - Phase 4 pooling (ToolProcessPool/ClusterManager)
 - Phase 5 executor (stub only)
 - Phase 7 dashboards (minimal UI)

 CRITICAL FINDING - Code Duplication:
 - ⚠️ modules/ directory contains a parallel implementation with module IDs (m010001_, m010002_, etc.)
 - Duplicates functionality across Phases 1, 2, 3, 5, 6
 - Represents ~86 files in 9 subdirectories
 - Likely legacy code being migrated to core/, error/, aim/ structure
 - Recommendation: Verify authoritative implementation, deprecate/archive modules/

 Archive Status:
 - ✅ Most historical code moved to external storage (456 files, ~68 MB on 2025-12-02)
 - ⚠️ Residual _ARCHIVE/patterns/legacy_atoms/ remains (86 files)
 - ⚠️ modules/ directory should likely be archived as well

 The folder organization is mature and well-structured, with Phases 0-3 being production-ready and Phases 4-7 requiring
  completion work. However, the modules/ directory duplication should be resolved to avoid confusion and maintenance
 burden.
╌╌╌╌╌╌╌╌╌