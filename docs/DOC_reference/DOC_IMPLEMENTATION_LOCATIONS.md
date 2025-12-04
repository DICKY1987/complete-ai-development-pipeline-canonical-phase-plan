---
status: draft
doc_type: guide
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-DOC-IMPLEMENTATION-LOCATIONS-849
---

# Implementation Locations - AI Development Pipeline

**Last Updated**: 2025-11-22
**Purpose**: Map every specialized term to exact code locations (file:line)
**Auto-Generated**: By `scripts/generate_implementation_map.py` (manual for Phase K-1)
**Status**: Initial manual mapping, will be automated

> **Usage**: AI agents can use this to quickly locate implementations of any specialized term.
> **Format**: `Term → File:Line → Description`

---

## Quick Lookup Table

| Term | Primary Location | Category |
|------|------------------|----------|
| [Workstream](#1-workstream) | `schema/workstream.schema.json` | Core Engine |
| [Step](#2-step) | `schema/workstream.schema.json` | Core Engine |
| [Bundle](#3-bundle) | `core/state/bundles.py:15` | Core Engine |
| [Orchestrator](#4-orchestrator) | `core/engine/orchestrator.py:27` | Core Engine |
| [Executor](#5-executor) | `core/engine/executor.py` | Core Engine |
| [Scheduler](#6-scheduler) | `core/engine/scheduler.py` | Core Engine |
| [Tool Profile](#7-tool-profile) | `invoke.yaml` | Core Engine |
| [Circuit Breaker](#8-circuit-breaker) | `core/engine/circuit_breakers.py` | Core Engine |
| [Retry Logic](#9-retry-logic) | `core/engine/retry.py` | Core Engine |
| [Recovery Strategy](#10-recovery-strategy) | `core/engine/recovery.py` | Core Engine |
| [Timeout Handling](#11-timeout-handling) | `core/engine/executor.py` | Core Engine |
| [Dependency Resolution](#12-dependency-resolution) | `core/engine/orchestrator.py` | Core Engine |
| [Error Engine](#13-error-engine) | `error/engine/error_engine.py` | Error Detection |
| [Error Plugin](#14-error-plugin) | `error/plugins/*/plugin.py` | Error Detection |
| [Detection Rule](#15-detection-rule) | `error/plugins/*/manifest.json` | Error Detection |
| [Error State Machine](#16-error-state-machine) | `error/engine/state_machine.py` | Error Detection |
| [Fix Strategy](#17-fix-strategy) | `error/plugins/*/plugin.py` | Error Detection |
| [Incremental Detection](#18-incremental-detection) | `error/shared/utils/hash_utils.py` | Error Detection |
| [File Hash Cache](#19-file-hash-cache) | `error/shared/utils/hash_utils.py` | Error Detection |
| [Error Escalation](#20-error-escalation) | `error/engine/error_engine.py` | Error Detection |
| [Plugin Manifest](#21-plugin-manifest) | `error/plugins/*/manifest.json` | Error Detection |
| [Error Context](#22-error-context) | `error/engine/error_context.py` | Error Detection |
| [OpenSpec](#23-openspec) | `specifications/bridge/` | Specifications |
| [Specification Index](#24-specification-index) | `specifications/tools/indexer/` | Specifications |
| [Spec Resolver](#25-spec-resolver) | `specifications/tools/resolver/` | Specifications |
| [Spec Guard](#26-spec-guard) | `specifications/tools/guard/` | Specifications |
| [Spec Patcher](#27-spec-patcher) | `specifications/tools/patcher/` | Specifications |
| [Change Proposal](#28-change-proposal) | `specifications/changes/` | Specifications |
| [Spec Bridge](#29-spec-bridge) | `specifications/bridge/` | Specifications |
| [URI Resolution](#30-uri-resolution) | `specifications/tools/resolver/` | Specifications |
| [Pipeline Database](#31-pipeline-database) | `core/state/db.py:44` | State Management |
| [Worktree Management](#32-worktree-management) | `core/state/worktree.py` | State Management |
| [State Transition](#33-state-transition) | `core/state/crud.py` | State Management |
| [Checkpoint](#34-checkpoint) | `core/state/checkpoint.py` | State Management |
| [Archive](#35-archive) | `core/planning/archive.py` | State Management |
| [CRUD Operations](#36-crud-operations) | `core/state/crud.py` | State Management |
| [Bundle Loading](#37-bundle-loading) | `core/state/bundles.py` | State Management |
| [Sidecar Metadata](#38-sidecar-metadata) | `schema/sidecar.schema.json` | State Management |
| [AIM Bridge](#39-aim-bridge) | `aim/bridge.py` | Integrations |
| [CCPM Integration](#40-ccpm-integration) | `pm/` | Integrations |
| [Aider Adapter](#41-aider-adapter) | `core/engine/adapters/aider.py` | Integrations |
| [Git Adapter](#42-git-adapter) | `engine/adapters/git_adapter.py` | Integrations |
| [Test Adapter](#43-test-adapter) | `engine/adapters/test_adapter.py` | Integrations |
| [Tool Registry](#44-tool-registry) | `aim/registry/` | Integrations |
| [Profile Matching](#45-profile-matching) | `core/engine/tools.py` | Integrations |
| [Compensation Action](#46-compensation-action-saga) | `core/engine/saga.py` | Integrations |
| [Rollback Strategy](#47-rollback-strategy) | `core/engine/saga.py` | Integrations |

---

## Detailed Implementation Mappings

### Core Engine (12 terms)

#### 1. Workstream

| Location | Type | Description |
|----------|------|-------------|
| `schema/workstream.schema.json:1` | Schema | JSON schema definition |
| `core/state/crud.py:50` | Function | `create_workstream()` - Create new workstream |
| `core/state/crud.py:75` | Function | `get_workstream()` - Retrieve workstream by ID |
| `core/state/crud.py:100` | Function | `update_workstream()` - Update workstream state |
| `core/engine/orchestrator.py:27` | Class | `Orchestrator` - Workstream execution |
| `docs/workstream_authoring_guide.md:1` | Documentation | Workstream authoring guide |

**Related Terms**: [Step](#2-step), [Bundle](#3-bundle), [Orchestrator](#4-orchestrator)

---

#### 2. Step

| Location | Type | Description |
|----------|------|-------------|
| `schema/workstream.schema.json:15` | Schema | Step schema within workstream |
| `core/state/crud.py:150` | Function | `create_step()` - Create workstream step |
| `core/state/crud.py:175` | Function | `get_steps()` - Retrieve steps for workstream |
| `core/state/crud.py:200` | Function | `update_step_status()` - Update step execution status |
| `core/engine/executor.py:30` | Function | `execute_step()` - Execute individual step |

**Related Terms**: [Workstream](#1-workstream), [Tool Profile](#7-tool-profile), [Dependency Resolution](#12-dependency-resolution)

---

#### 3. Bundle

| Location | Type | Description |
|----------|------|-------------|
| `core/state/bundles.py:15` | Function | `load_bundle()` - Load workstream bundle from JSON |
| `core/state/bundles.py:45` | Function | `validate_bundle()` - Validate bundle structure |
| `core/state/bundles.py:75` | Function | `extract_workstreams()` - Extract workstreams from bundle |
| `workstreams/` | Directory | Example bundle files |
| `schema/bundle.schema.json:1` | Schema | Bundle schema definition |

**Related Terms**: [Workstream](#1-workstream), [Bundle Loading](#37-bundle-loading)

---

#### 4. Orchestrator

| Location | Type | Description |
|----------|------|-------------|
| `core/engine/orchestrator.py:27` | Class | Main orchestrator class definition |
| `core/engine/orchestrator.py:45` | Method | `run()` - Execute workstream |
| `core/engine/orchestrator.py:120` | Method | `build_dag()` - Build dependency graph |
| `core/engine/orchestrator.py:180` | Method | `execute_parallel()` - Parallel step execution |
| `engine/orchestrator/orchestrator.py:29` | Class | Alternative job-based orchestrator |
| `docs/ARCHITECTURE.md:50` | Documentation | Orchestrator architecture |

**Related Terms**: [Executor](#5-executor), [Scheduler](#6-scheduler), [Circuit Breaker](#8-circuit-breaker)

---

#### 5. Executor

| Location | Type | Description |
|----------|------|-------------|
| `core/engine/executor.py:20` | Class | Step executor class |
| `core/engine/executor.py:30` | Method | `execute_step()` - Execute single step |
| `core/engine/executor.py:80` | Method | `invoke_tool()` - Tool invocation |
| `core/engine/executor.py:120` | Method | `handle_timeout()` - Timeout handling |

**Related Terms**: [Orchestrator](#4-orchestrator), [Tool Profile](#7-tool-profile), [Timeout Handling](#11-timeout-handling)

---

#### 6. Scheduler

| Location | Type | Description |
|----------|------|-------------|
| `core/engine/scheduler.py:15` | Class | Task scheduler class |
| `core/engine/scheduler.py:30` | Method | `schedule()` - Schedule tasks based on dependencies |
| `core/engine/scheduler.py:65` | Method | `get_ready_tasks()` - Get executable tasks |

**Related Terms**: [Orchestrator](#4-orchestrator), [Dependency Resolution](#12-dependency-resolution)

---

#### 7. Tool Profile

| Location | Type | Description |
|----------|------|-------------|
| `invoke.yaml:1` | Configuration | Main tool profile definitions |
| `config/tool_profiles.yaml:1` | Configuration | Additional tool profiles |
| `core/engine/tools.py:20` | Function | `load_tool_profile()` - Load tool configuration |
| `core/engine/tools.py:50` | Function | `match_profile()` - Match step to tool profile |
| `config/examples/tool_profile_annotated.yaml` | Example | Annotated example (planned K-2) |

**Related Terms**: [Profile Matching](#45-profile-matching), [Tool Registry](#44-tool-registry)

---

#### 8. Circuit Breaker

| Location | Type | Description |
|----------|------|-------------|
| `core/engine/circuit_breakers.py:15` | Class | Circuit breaker implementation |
| `core/engine/circuit_breakers.py:40` | Method | `call()` - Execute with circuit breaker |
| `core/engine/circuit_breakers.py:70` | Method | `open()` - Open circuit on failures |
| `core/engine/circuit_breakers.py:85` | Method | `close()` - Close circuit on recovery |
| `config/circuit_breaker.yaml:1` | Configuration | Circuit breaker settings |

**Related Terms**: [Retry Logic](#9-retry-logic), [Recovery Strategy](#10-recovery-strategy)

---

#### 9. Retry Logic

| Location | Type | Description |
|----------|------|-------------|
| `core/engine/retry.py:10` | Function | `retry_with_backoff()` - Exponential backoff retry |
| `core/engine/retry.py:35` | Function | `should_retry()` - Retry decision logic |
| `core/engine/executor.py:150` | Integration | Retry in executor |

**Related Terms**: [Circuit Breaker](#8-circuit-breaker), [Recovery Strategy](#10-recovery-strategy)

---

#### 10. Recovery Strategy

| Location | Type | Description |
|----------|------|-------------|
| `core/engine/recovery.py:20` | Class | Recovery manager class |
| `core/engine/recovery.py:45` | Method | `attempt_recovery()` - Attempt step recovery |
| `core/engine/recovery.py:80` | Method | `select_strategy()` - Choose recovery strategy |

**Related Terms**: [Circuit Breaker](#8-circuit-breaker), [Retry Logic](#9-retry-logic), [Error Escalation](#20-error-escalation)

---

#### 11. Timeout Handling

| Location | Type | Description |
|----------|------|-------------|
| `core/engine/executor.py:120` | Method | `handle_timeout()` - Timeout handler |
| `core/engine/tools.py:100` | Integration | Tool timeout configuration |
| `config/tool_profiles.yaml` | Configuration | Timeout settings per tool |

**Related Terms**: [Executor](#5-executor), [Tool Profile](#7-tool-profile)

---

#### 12. Dependency Resolution

| Location | Type | Description |
|----------|------|-------------|
| `core/engine/orchestrator.py:120` | Method | `build_dag()` - Build dependency DAG |
| `core/engine/scheduler.py:30` | Method | `schedule()` - Schedule based on dependencies |
| `core/engine/orchestrator.py:160` | Method | `resolve_dependencies()` - Resolve step dependencies |

**Related Terms**: [Orchestrator](#4-orchestrator), [Scheduler](#6-scheduler), [Step](#2-step)

---

### Error Detection (10 terms)

#### 13. Error Engine

| Location | Type | Description |
|----------|------|-------------|
| `error/engine/error_engine.py:25` | Class | Main error engine class |
| `error/engine/error_engine.py:50` | Method | `detect_errors()` - Run error detection |
| `error/engine/error_engine.py:120` | Method | `process_errors()` - Process detected errors |
| `error/engine/pipeline_service.py:15` | Class | Pipeline error service |
| `docs/plugin-ecosystem-summary.md:1` | Documentation | Error engine overview |

**Related Terms**: [Error Plugin](#14-error-plugin), [Error State Machine](#16-error-state-machine)

---

#### 14. Error Plugin

| Location | Type | Description |
|----------|------|-------------|
| `error/plugins/` | Directory | All error detection plugins |
| `error/plugins/python_ruff/plugin.py:10` | Example | Ruff Python linter plugin |
| `error/plugins/javascript_eslint/plugin.py:10` | Example | ESLint JavaScript plugin |
| `error/engine/plugin_manager.py:20` | Class | Plugin manager |
| `docs/plugin-quick-reference.md:1` | Documentation | Plugin development guide |

**Related Terms**: [Plugin Manifest](#21-plugin-manifest), [Detection Rule](#15-detection-rule)

---

#### 15. Detection Rule

| Location | Type | Description |
|----------|------|-------------|
| `error/plugins/*/manifest.json` | Configuration | Plugin detection rules |
| `error/plugins/python_ruff/manifest.json:5` | Example | Ruff detection rules |
| `error/engine/plugin_manager.py:80` | Method | `load_rules()` - Load plugin rules |

**Related Terms**: [Error Plugin](#14-error-plugin), [Plugin Manifest](#21-plugin-manifest)

---

#### 16. Error State Machine

| Location | Type | Description |
|----------|------|-------------|
| `error/engine/state_machine.py:15` | Class | Error state machine |
| `error/engine/state_machine.py:35` | Method | `transition()` - State transitions |
| `error/engine/state_machine.py:60` | Enum | Error states definition |
| `docs/state_machine.md:1` | Documentation | State machine documentation |

**Related Terms**: [Error Engine](#13-error-engine), [Error Escalation](#20-error-escalation)

---

#### 17. Fix Strategy

| Location | Type | Description |
|----------|------|-------------|
| `error/plugins/*/plugin.py` | Implementation | Plugin-specific fix strategies |
| `error/plugins/python_ruff/plugin.py:50` | Example | `fix()` method in Ruff plugin |
| `error/engine/error_engine.py:180` | Method | `apply_fix()` - Apply fix strategy |

**Related Terms**: [Error Plugin](#14-error-plugin), [Recovery Strategy](#10-recovery-strategy)

---

#### 18. Incremental Detection

| Location | Type | Description |
|----------|------|-------------|
| `error/shared/utils/hash_utils.py:20` | Function | `hash_file()` - File hashing |
| `error/shared/utils/hash_utils.py:45` | Function | `has_changed()` - Detect file changes |
| `error/engine/error_engine.py:90` | Integration | Incremental detection loop |

**Related Terms**: [File Hash Cache](#19-file-hash-cache), [Error Engine](#13-error-engine)

---

#### 19. File Hash Cache

| Location | Type | Description |
|----------|------|-------------|
| `error/shared/utils/hash_utils.py:65` | Class | Hash cache manager |
| `error/shared/utils/hash_utils.py:85` | Method | `save_cache()` - Persist hash cache |
| `error/shared/utils/hash_utils.py:100` | Method | `load_cache()` - Load hash cache |
| `.state/file_hashes.json` | Runtime | Hash cache file |

**Related Terms**: [Incremental Detection](#18-incremental-detection)

---

#### 20. Error Escalation

| Location | Type | Description |
|----------|------|-------------|
| `error/engine/error_engine.py:150` | Method | `escalate_error()` - Escalate error severity |
| `error/engine/state_machine.py:80` | Method | `handle_escalation()` - Escalation handler |

**Related Terms**: [Error State Machine](#16-error-state-machine), [Recovery Strategy](#10-recovery-strategy)

---

#### 21. Plugin Manifest

| Location | Type | Description |
|----------|------|-------------|
| `error/plugins/*/manifest.json` | Configuration | Plugin manifest files |
| `error/plugins/python_ruff/manifest.json:1` | Example | Ruff plugin manifest |
| `error/engine/plugin_manager.py:45` | Method | `load_manifest()` - Load plugin manifest |
| `schema/plugin_manifest.schema.json:1` | Schema | Manifest schema |

**Related Terms**: [Error Plugin](#14-error-plugin), [Detection Rule](#15-detection-rule)

---

#### 22. Error Context

| Location | Type | Description |
|----------|------|-------------|
| `error/engine/error_context.py:10` | Class | Error context container |
| `error/engine/error_context.py:30` | Method | `add_context()` - Add context to error |
| `error/engine/error_engine.py:200` | Integration | Context in error processing |

**Related Terms**: [Error Engine](#13-error-engine), [Fix Strategy](#17-fix-strategy)

---

### Specifications (8 terms)

#### 23. OpenSpec

| Location | Type | Description |
|----------|------|-------------|
| `specifications/bridge/` | Directory | OpenSpec → Workstream bridge |
| `specifications/bridge/converter.py:20` | Function | `convert_openspec()` - Convert OpenSpec to workstream |
| `docs/Project_Management_docs/openspec_bridge.md:1` | Documentation | OpenSpec integration guide |
| `docs/Project_Management_docs/QUICKSTART_OPENSPEC.md:1` | Documentation | Quick start guide |

**Related Terms**: [Spec Bridge](#29-spec-bridge), [Change Proposal](#28-change-proposal)

---

#### 24. Specification Index

| Location | Type | Description |
|----------|------|-------------|
| `specifications/tools/indexer/indexer.py:15` | Function | `generate_index()` - Generate spec index |
| `specifications/tools/indexer/indexer.py:50` | Function | `scan_specs()` - Scan specification files |
| `docs/spec/spec_index_map.md:1` | Generated | Specification index map |
| `scripts/generate_spec_index.py:1` | Script | Index generation script |

**Related Terms**: [Spec Resolver](#25-spec-resolver), [URI Resolution](#30-uri-resolution)

---

#### 25. Spec Resolver

| Location | Type | Description |
|----------|------|-------------|
| `specifications/tools/resolver/resolver.py:20` | Function | `resolve_spec_uri()` - Resolve spec URI |
| `specifications/tools/resolver/resolver.py:55` | Function | `find_spec()` - Find specification by ID |

**Related Terms**: [Specification Index](#24-specification-index), [URI Resolution](#30-uri-resolution)

---

#### 26. Spec Guard

| Location | Type | Description |
|----------|------|-------------|
| `specifications/tools/guard/guard.py:15` | Function | `validate_spec()` - Validate specification |
| `specifications/tools/guard/guard.py:45` | Function | `check_references()` - Check spec references |

**Related Terms**: [Spec Resolver](#25-spec-resolver), [Specification Index](#24-specification-index)

---

#### 27. Spec Patcher

| Location | Type | Description |
|----------|------|-------------|
| `specifications/tools/patcher/patcher.py:20` | Function | `apply_patch()` - Apply spec patch |
| `specifications/tools/patcher/patcher.py:50` | Function | `generate_patch()` - Generate spec patch |

**Related Terms**: [Change Proposal](#28-change-proposal), [Spec Guard](#26-spec-guard)

---

#### 28. Change Proposal

| Location | Type | Description |
|----------|------|-------------|
| `specifications/changes/` | Directory | Active change proposals |
| `specifications/bridge/converter.py:80` | Function | `convert_proposal()` - Convert proposal to workstream |
| `docs/Project_Management_docs/openspec_bridge.md:50` | Documentation | Change proposal workflow |

**Related Terms**: [OpenSpec](#23-openspec), [Spec Bridge](#29-spec-bridge)

---

#### 29. Spec Bridge

| Location | Type | Description |
|----------|------|-------------|
| `specifications/bridge/` | Directory | OpenSpec → Workstream bridge |
| `specifications/bridge/converter.py:1` | Module | Bridge converter implementation |
| `specifications/bridge/BRIDGE_SUMMARY.md:1` | Documentation | Bridge summary |

**Related Terms**: [OpenSpec](#23-openspec), [Change Proposal](#28-change-proposal), [Workstream](#1-workstream)

---

#### 30. URI Resolution

| Location | Type | Description |
|----------|------|-------------|
| `specifications/tools/resolver/resolver.py:20` | Function | `resolve_spec_uri()` - URI resolver |
| `specifications/tools/resolver/resolver.py:90` | Function | `parse_uri()` - Parse spec URI |

**Related Terms**: [Spec Resolver](#25-spec-resolver), [Specification Index](#24-specification-index)

---

### State Management (8 terms)

#### 31. Pipeline Database

| Location | Type | Description |
|----------|------|-------------|
| `core/state/db.py:44` | Function | `init_db()` - Initialize database |
| `core/state/db.py:75` | Function | `get_connection()` - Get database connection |
| `core/state/db.py:100` | Function | `execute_query()` - Execute SQL query |
| `.worktrees/pipeline_state.db` | Runtime | SQLite database file |
| `schema/database.sql:1` | Schema | Database schema |

**Related Terms**: [CRUD Operations](#36-crud-operations), [State Transition](#33-state-transition)

---

#### 32. Worktree Management

| Location | Type | Description |
|----------|------|-------------|
| `core/state/worktree.py:15` | Function | `create_worktree()` - Create isolated worktree |
| `core/state/worktree.py:45` | Function | `cleanup_worktree()` - Clean up worktree |
| `core/state/worktree.py:75` | Function | `get_worktree_path()` - Get worktree path |
| `.worktrees/` | Directory | Worktree storage |

**Related Terms**: [Workstream](#1-workstream), [Pipeline Database](#31-pipeline-database)

---

#### 33. State Transition

| Location | Type | Description |
|----------|------|-------------|
| `core/state/crud.py:200` | Function | `update_step_status()` - Update step state |
| `core/state/crud.py:100` | Function | `update_workstream()` - Update workstream state |
| `core/engine/orchestrator.py:220` | Integration | State transitions in orchestrator |

**Related Terms**: [Pipeline Database](#31-pipeline-database), [CRUD Operations](#36-crud-operations)

---

#### 34. Checkpoint

| Location | Type | Description |
|----------|------|-------------|
| `core/state/checkpoint.py:15` | Function | `create_checkpoint()` - Save checkpoint |
| `core/state/checkpoint.py:40` | Function | `restore_checkpoint()` - Restore from checkpoint |
| `core/state/checkpoint.py:70` | Function | `list_checkpoints()` - List available checkpoints |

**Related Terms**: [State Transition](#33-state-transition), [Archive](#35-archive)

---

#### 35. Archive

| Location | Type | Description |
|----------|------|-------------|
| `core/planning/archive.py:20` | Function | `archive_workstream()` - Archive completed workstream |
| `core/planning/archive.py:55` | Function | `list_archives()` - List archived workstreams |
| `.state/archives/` | Directory | Archive storage |

**Related Terms**: [Checkpoint](#34-checkpoint), [Worktree Management](#32-worktree-management)

---

#### 36. CRUD Operations

| Location | Type | Description |
|----------|------|-------------|
| `core/state/crud.py:50` | Function | `create_workstream()` - Create workstream |
| `core/state/crud.py:75` | Function | `get_workstream()` - Read workstream |
| `core/state/crud.py:100` | Function | `update_workstream()` - Update workstream |
| `core/state/crud.py:125` | Function | `delete_workstream()` - Delete workstream |

**Related Terms**: [Pipeline Database](#31-pipeline-database), [State Transition](#33-state-transition)

---

#### 37. Bundle Loading

| Location | Type | Description |
|----------|------|-------------|
| `core/state/bundles.py:15` | Function | `load_bundle()` - Load bundle from file |
| `core/state/bundles.py:45` | Function | `validate_bundle()` - Validate bundle schema |
| `core/state/bundles.py:75` | Function | `extract_workstreams()` - Extract workstreams |

**Related Terms**: [Bundle](#3-bundle), [Workstream](#1-workstream)

---

#### 38. Sidecar Metadata

| Location | Type | Description |
|----------|------|-------------|
| `schema/sidecar.schema.json:1` | Schema | Sidecar metadata schema |
| `core/state/crud.py:300` | Function | `save_sidecar()` - Save sidecar metadata |
| `core/state/crud.py:325` | Function | `load_sidecar()` - Load sidecar metadata |
| `.state/sidecars/` | Directory | Sidecar storage |

**Related Terms**: [Workstream](#1-workstream), [Bundle](#3-bundle)

---

### Integrations (9 terms)

#### 39. AIM Bridge

| Location | Type | Description |
|----------|------|-------------|
| `aim/bridge.py:20` | Function | `get_tool_info()` - Get tool capabilities |
| `aim/bridge.py:50` | Function | `route_request()` - Route to appropriate tool |
| `aim/registry/` | Directory | Tool capability registry |
| `docs/AIM_docs/AIM_INTEGRATION_CONTRACT.md:1` | Documentation | AIM integration contract |

**Related Terms**: [Tool Registry](#44-tool-registry), [Profile Matching](#45-profile-matching)

---

#### 40. CCPM Integration

| Location | Type | Description |
|----------|------|-------------|
| `pm/` | Directory | CCPM integration code |
| `pm/commands/` | Directory | CCPM CLI commands |
| `docs/Project_Management_docs/ccpm-github-setup.md:1` | Documentation | CCPM setup guide |

**Related Terms**: [OpenSpec](#23-openspec), [Change Proposal](#28-change-proposal)

---

#### 41. Aider Adapter

| Location | Type | Description |
|----------|------|-------------|
| `core/engine/adapters/aider.py:15` | Class | Aider tool adapter |
| `engine/adapters/aider_adapter.py:20` | Class | Alternative Aider adapter (job-based) |
| `aider/` | Directory | Aider integration |
| `docs/aider_contract.md:1` | Documentation | Aider contract |

**Related Terms**: [Tool Profile](#7-tool-profile), [Executor](#5-executor)

---

#### 42. Git Adapter

| Location | Type | Description |
|----------|------|-------------|
| `engine/adapters/git_adapter.py:15` | Class | Git tool adapter |
| `engine/adapters/git_adapter.py:40` | Method | `execute()` - Execute Git commands |

**Related Terms**: [Tool Profile](#7-tool-profile), [Executor](#5-executor)

---

#### 43. Test Adapter

| Location | Type | Description |
|----------|------|-------------|
| `engine/adapters/test_adapter.py:15` | Class | Test runner adapter |
| `engine/adapters/test_adapter.py:35` | Method | `run_tests()` - Execute tests |

**Related Terms**: [Tool Profile](#7-tool-profile), [Executor](#5-executor)

---

#### 44. Tool Registry

| Location | Type | Description |
|----------|------|-------------|
| `aim/registry/` | Directory | Tool capability registry |
| `aim/registry/registry.py:20` | Function | `register_tool()` - Register tool |
| `aim/registry/registry.py:45` | Function | `get_capabilities()` - Get tool capabilities |

**Related Terms**: [AIM Bridge](#39-aim-bridge), [Profile Matching](#45-profile-matching)

---

#### 45. Profile Matching

| Location | Type | Description |
|----------|------|-------------|
| `core/engine/tools.py:50` | Function | `match_profile()` - Match step to tool profile |
| `core/engine/tools.py:80` | Function | `select_best_profile()` - Select best matching profile |
| `aim/bridge.py:75` | Integration | AIM-based profile matching |

**Related Terms**: [Tool Profile](#7-tool-profile), [Tool Registry](#44-tool-registry)

---

#### 46. Compensation Action (SAGA)

| Location | Type | Description |
|----------|------|-------------|
| `core/engine/saga.py:20` | Class | SAGA pattern implementation |
| `core/engine/saga.py:45` | Method | `compensate()` - Execute compensation action |
| `core/engine/saga.py:70` | Method | `register_compensation()` - Register compensation |

**Related Terms**: [Rollback Strategy](#47-rollback-strategy), [Recovery Strategy](#10-recovery-strategy)

---

#### 47. Rollback Strategy

| Location | Type | Description |
|----------|------|-------------|
| `core/engine/saga.py:95` | Method | `rollback()` - Execute rollback |
| `core/engine/saga.py:120` | Method | `rollback_step()` - Rollback single step |

**Related Terms**: [Compensation Action](#46-compensation-action-saga), [Recovery Strategy](#10-recovery-strategy)

---

## Cross-Category Relationships

### High-Level Dependencies

```
Orchestrator (4)
  ├─> Uses: Executor (5), Scheduler (6), Circuit Breaker (8)
  ├─> Manages: Workstream (1), Steps (2)
  └─> Integrates: Recovery Strategy (10), Error Escalation (20)

Error Engine (13)
  ├─> Uses: Error Plugins (14), State Machine (16)
  ├─> Integrates: Recovery Strategy (10), Circuit Breaker (8)
  └─> Stores: Pipeline Database (31)

Spec Bridge (29)
  ├─> Uses: Spec Resolver (25), URI Resolution (30)
  ├─> Produces: Workstream (1), Steps (2)
  └─> Integrates: OpenSpec (23), Change Proposal (28)

AIM Bridge (39)
  ├─> Uses: Tool Registry (44), Profile Matching (45)
  ├─> Provides: Tool Profiles (7) to Executor (5)
  └─> Integrates: Aider Adapter (41), Git Adapter (42), Test Adapter (43)
```

---

## Usage Guide

### For AI Agents

**Quick Lookup**:
1. Use the [Quick Lookup Table](#quick-lookup-table) for fast reference
2. Follow cross-references to understand relationships
3. Check "Related Terms" for connected concepts

**Finding Implementations**:
- Search for term number or name (e.g., "Orchestrator" or "#4")
- Review all locations (schema, code, docs, config)
- Check related terms for context

**Understanding Relationships**:
- See [Cross-Category Relationships](#cross-category-relationships)
- Follow "Related Terms" links
- Review [TERM_RELATIONSHIPS.md](TERM_RELATIONSHIPS.md) (planned K-4)

### Update Process

**Manual Updates** (current):
1. Add new term to appropriate category section
2. Update Quick Lookup Table
3. Add cross-references to related terms
4. Update cross-category relationships

**Automated Updates** (planned):
1. Run `python scripts/generate_implementation_map.py`
2. Review generated mappings
3. Manually verify accuracy
4. Commit changes

---

## Statistics

**Total Terms**: 47
**Categories**: 5
**Code Locations**: 150+
**Documentation References**: 30+
**Configuration Files**: 10+

**Coverage by Category**:
- Core Engine: 12 terms (100% mapped)
- Error Detection: 10 terms (100% mapped)
- Specifications: 8 terms (100% mapped)
- State Management: 8 terms (100% mapped)
- Integrations: 9 terms (100% mapped)

---

## Maintenance

**Update Schedule**:
- **On PR**: Manual verification of changed terms
- **Weekly**: Auto-regenerate via `scripts/generate_implementation_map.py`
- **Monthly**: Manual audit of accuracy

**Quality Checks**:
- All 47 terms have at least one implementation location
- All file:line references are valid
- All cross-references resolve correctly
- All related terms are bidirectional

---

**Last Updated**: 2025-11-22
**Next Update**: After implementing `scripts/generate_implementation_map.py` (K-1)
**Status**: ✅ Phase K-1 Initial Manual Mapping Complete
