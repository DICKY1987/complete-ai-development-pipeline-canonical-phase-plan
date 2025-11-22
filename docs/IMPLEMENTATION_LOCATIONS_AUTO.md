# Implementation Locations - AI Development Pipeline

**Last Updated**: 2025-11-22  
**Purpose**: Map every specialized term to exact code locations (file:line)  
**Auto-Generated**: By `scripts/generate_implementation_map.py`  

> **Usage**: AI agents can use this to quickly locate implementations of any specialized term.  
> **Format**: `Term → File:Line → Description`

---

## 📋 Quick Lookup Table

| Term | Primary Location | Category | Locations Found |
|------|------------------|----------|-----------------|
| [Workstream](#1-workstream) | `tasks.py:22` | Core Engine | 68 |
| [Step](#2-step) | `pm\event_handler.py:381` | Core Engine | 28 |
| [Bundle](#3-bundle) | `tests\test_prompt_engine.py:19` | Core Engine | 26 |
| [Orchestrator](#4-orchestrator) | `core\config_loader.py:51` | Core Engine | 29 |
| [Executor](#5-executor) | `AGENTIC_DEV_PROTOTYPE\tests\test_dependency_resolution.py:188` | Core Engine | 6 |
| [Scheduler](#6-scheduler) | `core\engine\scheduler.py:45` | Core Engine | 4 |
| [Tool Profile](#7-tool-profile) | `core\engine\context_estimator.py:12` | Core Engine | 10 |
| [Circuit Breaker](#8-circuit-breaker) | `core\config_loader.py:99` | Core Engine | 22 |
| [Retry Logic](#9-retry-logic) | `tests\test_job_wrapper.py:124` | Core Engine | 22 |
| [Recovery Strategy](#10-recovery-strategy) | `core\engine\recovery_manager.py:11` | Core Engine | 1 |
| [Timeout Handling](#11-timeout-handling) | `aim\exceptions.py:99` | Core Engine | 28 |
| [Dependency Resolution](#12-dependency-resolution) | `tests\test_job_wrapper.py:162` | Core Engine | 31 |
| [Error Engine](#13-error-engine) | `core\config_loader.py:83` | Error Detection | 3 |
| [Error Plugin](#14-error-plugin) | `scripts\migrate_plugins_to_invoke.py:39` | Error Detection | 76 |
| [Detection Rule](#15-detection-rule) | `aim\bridge.py:95` | Error Detection | 39 |
| [Error State Machine](#16-error-state-machine) | `AGENTIC_DEV_PROTOTYPE\tests\test_orchestrator_core.py:18` | Error Detection | 7 |
| [Fix Strategy](#17-fix-strategy) | `aider\engine.py:126` | Error Detection | 27 |
| [Incremental Detection](#18-incremental-detection) | `tests\test_incremental_cache.py:8` | Error Detection | 18 |
| [File Hash Cache](#19-file-hash-cache) | `tests\test_incremental_cache.py:8` | Error Detection | 1 |
| [Error Escalation](#20-error-escalation) | `tests\test_escalation.py:12` | Error Detection | 22 |
| [Plugin Manifest](#21-plugin-manifest) | `tests\test_ccpm_openspec_integration.py:78` | Error Detection | 24 |
| [Error Context](#22-error-context) | `core\state\db.py:78` | Error Detection | 5 |
| [OpenSpec](#23-openspec) | `pm\bridge.py:24` | Specifications | 9 |
| [Specification Index](#24-specification-index) | `tasks.py:129` | Specifications | 2 |
| [Spec Resolver](#25-spec-resolver) | `AGENTIC_DEV_PROTOTYPE\src\spec_resolver.py:43` | Specifications | 7 |
| [Spec Guard](#26-spec-guard) | `AGENTIC_DEV_PROTOTYPE\tests\test_guard_rules.py:16` | Specifications | 5 |
| [Spec Patcher](#27-spec-patcher) | *Not found* | Specifications | 0 |
| [Change Proposal](#28-change-proposal) | `core\tool_instrumentation.py:221` | Specifications | 10 |
| [Spec Bridge](#29-spec-bridge) | `pm\bridge.py:324` | Specifications | 1 |
| [URI Resolution](#30-uri-resolution) | *Not found* | Specifications | 0 |
| [Pipeline Database](#31-pipeline-database) | `core\engine\hardening.py:139` | State Management | 7 |
| [Worktree Management](#32-worktree-management) | `core\state\worktree.py:35` | State Management | 3 |
| [State Transition](#33-state-transition) | `tests\test_worker_lifecycle.py:104` | State Management | 29 |
| [Checkpoint](#34-checkpoint) | *Not found* | State Management | 0 |
| [Archive](#35-archive) | `core\planning\archive.py:7` | State Management | 1 |
| [CRUD Operations](#36-crud-operations) | `aim\bridge.py:31` | State Management | 357 |
| [Bundle Loading](#37-bundle-loading) | `core\state\bundles.py:160` | State Management | 6 |
| [Sidecar Metadata](#38-sidecar-metadata) | `.migration_backup_20251120_144334\spec\tools\spec_indexer\indexer.py:90` | State Management | 8 |
| [AIM Bridge](#39-aim-bridge) | *Not found* | Integrations | 0 |
| [CCPM Integration](#40-ccpm-integration) | `tests\test_ccpm_openspec_integration.py:10` | Integrations | 2 |
| [Aider Adapter](#41-aider-adapter) | `aider\engine.py:159` | Integrations | 30 |
| [Git Adapter](#42-git-adapter) | `scripts\test_adapters.py:179` | Integrations | 2 |
| [Test Adapter](#43-test-adapter) | `scripts\test_adapters.py:15` | Integrations | 7 |
| [Tool Registry](#44-tool-registry) | `aim\bridge.py:31` | Integrations | 22 |
| [Profile Matching](#45-profile-matching) | *Not found* | Integrations | 0 |
| [Compensation Action](#46-compensation-action) | *Not found* | Integrations | 0 |
| [Rollback Strategy](#47-rollback-strategy) | `AGENTIC_DEV_PROTOTYPE\src\patch_manager.py:269` | Integrations | 7 |

---

## Core Engine

### 1. Workstream

| Location | Type | Description |
|----------|------|-------------|
| `core\engine\metrics.py:35` | Class | Class definition: WorkstreamMetrics |
| `core\state\bundles.py:51` | Class | Class definition: WorkstreamBundle |
| `core\ui_models.py:169` | Class | Class definition: WorkstreamStatus |
| `core\ui_models.py:181` | Class | Class definition: WorkstreamProgress |
| `core\ui_models.py:195` | Class | Class definition: WorkstreamRecord |
| `pm\bridge.py:150` | Class | Class definition: EpicToWorkstreamConverter |
| `pm\bridge.py:272` | Class | Class definition: WorkstreamStatusSync |
| `pm\models.py:289` | Class | Class definition: WorkstreamEvent |
| `scripts\spec_to_workstream.py:172` | Class | Class definition: WorkstreamGenerator |
| `docs\workstream_authoring_guide.md:1` | Doc | Documentation: workstream_authoring_guide.md |
| `AGENTIC_DEV_PROTOTYPE\src\schema_generator.py:254` | Function | Function: generate_workstream_schema() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_schema_generator.py:111` | Function | Function: test_generate_workstream_schema() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_schema_validator.py:174` | Function | Function: test_validate_workstream_id_pattern() |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\schema_generator.py:254` | Function | Function: generate_workstream_schema() |
| `core\engine\compensation.py:10` | Function | Function: rollback_workstream() |
| `core\engine\integration_worker.py:46` | Function | Function: merge_workstream_results() |
| `core\engine\metrics.py:163` | Function | Function: compute_workstream_metrics() |
| `core\engine\orchestrator.py:325` | Function | Function: run_workstream() |
| `core\engine\orchestrator.py:470` | Function | Function: run_single_workstream_from_bundle() |
| `core\engine\orchestrator.py:485` | Function | Function: execute_workstreams_parallel() |
| `core\engine\orchestrator.py:665` | Function | Function: _execute_workstream_thread() |
| `core\planning\ccpm_integration.py:20` | Function | Function: task_to_workstream() |
| `core\planning\ccpm_integration.py:113` | Function | Function: epic_to_workstream_bundle() |
| `core\planning\ccpm_integration.py:153` | Function | Function: sync_workstream_result() |
| `core\planning\ccpm_integration.py:198` | Function | Function: generate_workstreams_from_epic() |
| `core\planning\ccpm_integration.py:224` | Function | Function: update_task_from_workstream() |
| `core\planning\planner.py:9` | Function | Function: plan_workstreams_from_spec() |
| `core\state\bundles.py:142` | Function | Function: get_workstream_dir() |
| `core\state\crud.py:206` | Function | Function: create_workstream() |
| `core\state\crud.py:252` | Function | Function: get_workstream() |
| `core\state\crud.py:290` | Function | Function: get_workstreams_for_run() |
| `core\state\crud.py:343` | Function | Function: update_workstream_status() |
| `core\ui_cli.py:122` | Function | Function: cmd_workstreams() |
| `core\ui_cli.py:151` | Function | Function: cmd_workstream_counts() |
| `core\ui_clients.py:195` | Function | Function: get_workstream() |
| `core\ui_clients.py:258` | Function | Function: list_workstreams() |
| `core\ui_clients.py:292` | Function | Function: get_workstream_counts_by_status() |
| `engine\interfaces\state_interface.py:47` | Function | Function: list_workstreams() |
| `engine\interfaces\state_interface.py:51` | Function | Function: get_workstream() |
| `engine\state_store\job_state_store.py:332` | Function | Function: list_workstreams() |
| `engine\state_store\job_state_store.py:373` | Function | Function: get_workstream() |
| `pm\bridge.py:465` | Function | Function: epic_to_workstreams() |
| `pm\bridge.py:471` | Function | Function: sync_workstream_status() |
| `pm\bridge.py:183` | Function | Function: _task_to_workstream() |
| `pm\bridge.py:278` | Function | Function: sync_workstream_to_task() |
| `pm\bridge.py:358` | Function | Function: epic_to_workstreams() |
| `pm\bridge.py:367` | Function | Function: sync_workstream_status() |
| `pm\bridge.py:372` | Function | Function: openspec_to_workstreams() |
| `pm\bridge.py:420` | Function | Function: save_workstreams() |
| `pm\event_handler.py:375` | Function | Function: emit_workstream_start() |
| `pm\event_handler.py:387` | Function | Function: emit_workstream_complete() |
| `pm\event_handler.py:393` | Function | Function: emit_workstream_blocked() |
| `pm\event_handler.py:399` | Function | Function: emit_workstream_failed() |
| `pm\event_handler.py:91` | Function | Function: on_workstream_start() |
| `pm\event_handler.py:151` | Function | Function: on_workstream_complete() |
| `pm\event_handler.py:185` | Function | Function: on_workstream_blocked() |
| `pm\event_handler.py:216` | Function | Function: on_workstream_failed() |
| `tasks.py:22` | Function | Function: validate_workstreams() |
| `tasks.py:92` | Function | Function: run_workstream() |
| `tests\integration\test_aim_orchestrator_integration.py:231` | Function | Function: test_workstream_schema_allows_capability() |
| `tests\orchestrator\test_parallel_src.py:38` | Function | Function: test_run_many_missing_workstream() |
| `tests\orchestrator\test_parallel_src.py:22` | Function | Function: fake_run_workstream() |
| `tests\pipeline\test_workstream_authoring.py:25` | Function | Function: workstream_schema() |
| `tests\pipeline\test_workstream_authoring.py:31` | Function | Function: workstream_template_raw() |
| `tests\pipeline\test_workstream_authoring.py:39` | Function | Function: temp_workstream_dir() |
| `tests\test_openspec_convert.py:32` | Function | Function: test_change_to_workstream_roundtrip() |
| `AGENTIC_DEV_PROTOTYPE\schemas\generated\workstream.schema.json:1` | Schema | Schema definition: workstream.schema.json |
| `schema\workstream.schema.json:1` | Schema | Schema definition: workstream.schema.json |

---

### 2. Step

| Location | Type | Description |
|----------|------|-------------|
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\state_machine.py:21` | Class | Class definition: StepState |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\state_machine.py:105` | Class | Class definition: StepStateMachine |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_run_lifecycle.py:147` | Class | Class definition: TestStepAttempts |
| `core\engine\orchestrator.py:46` | Class | Class definition: StepResult |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\bootstrap\orchestrator.py:213` | Function | Function: _generate_next_steps() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\orchestrator.py:210` | Function | Function: create_step_attempt() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\orchestrator.py:260` | Function | Function: complete_step_attempt() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\orchestrator.py:324` | Function | Function: get_run_steps() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\state\db.py:219` | Function | Function: create_step_attempt() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\state\db.py:248` | Function | Function: get_step_attempt() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\state\db.py:263` | Function | Function: update_step_attempt() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\state\db.py:289` | Function | Function: list_step_attempts() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_run_lifecycle.py:150` | Function | Function: test_create_step_attempt() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_run_lifecycle.py:174` | Function | Function: test_complete_step_success() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_run_lifecycle.py:195` | Function | Function: test_complete_step_failure() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_run_lifecycle.py:215` | Function | Function: test_multiple_steps() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_run_lifecycle.py:271` | Function | Function: test_step_events() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_run_lifecycle.py:347` | Function | Function: test_step_state_transitions() |
| `core\engine\circuit_breakers.py:127` | Function | Function: for_step() |
| `core\engine\orchestrator.py:57` | Function | Function: run_edit_step() |
| `core\engine\orchestrator.py:133` | Function | Function: run_static_step() |
| `core\engine\orchestrator.py:175` | Function | Function: run_runtime_step() |
| `core\state\crud.py:388` | Function | Function: record_step_attempt() |
| `core\state\crud.py:437` | Function | Function: get_step_attempts() |
| `pm\event_handler.py:381` | Function | Function: emit_step_complete() |
| `pm\event_handler.py:117` | Function | Function: on_step_complete() |
| `AGENTIC_DEV_PROTOTYPE\schemas\generated\workstream.schema.json:1` | Schema | Schema definition: workstream.schema.json |
| `schema\workstream.schema.json:1` | Schema | Schema definition: workstream.schema.json |

---

### 3. Bundle

| Location | Type | Description |
|----------|------|-------------|
| `core\state\bundles.py:51` | Class | Class definition: WorkstreamBundle |
| `core\state\bundles.py:76` | Class | Class definition: BundleValidationError |
| `core\state\bundles.py:80` | Class | Class definition: BundleDependencyError |
| `core\state\bundles.py:84` | Class | Class definition: BundleCycleError |
| `AGENTIC_DEV_PROTOTYPE\src\spec_renderer.py:248` | Function | Function: bundle_sections() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_spec_renderer.py:124` | Function | Function: test_bundle_sections() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_spec_renderer.py:134` | Function | Function: test_bundle_sections_empty_list() |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\spec_renderer.py:248` | Function | Function: bundle_sections() |
| `core\engine\orchestrator.py:470` | Function | Function: run_single_workstream_from_bundle() |
| `core\planning\ccpm_integration.py:113` | Function | Function: epic_to_workstream_bundle() |
| `core\state\bundles.py:160` | Function | Function: load_bundle_file() |
| `core\state\bundles.py:180` | Function | Function: validate_bundle_data() |
| `core\state\bundles.py:295` | Function | Function: load_and_validate_bundles() |
| `core\state\bundles.py:440` | Function | Function: sync_bundles_to_db() |
| `tests\orchestrator\test_parallel_src.py:9` | Function | Function: _make_bundle() |
| `tests\orchestrator\test_parallel_src.py:19` | Function | Function: fake_load_and_validate_bundles() |
| `tests\pipeline\test_bundles.py:16` | Function | Function: write_bundle() |
| `tests\pipeline\test_bundles.py:24` | Function | Function: test_valid_bundles_no_cycles_no_overlaps() |
| `tests\pipeline\test_fix_loop.py:20` | Function | Function: bundle_ws() |
| `tests\pipeline\test_openspec_parser_src.py:49` | Function | Function: test_load_bundle_from_yaml_items_tags_when_then() |
| `tests\pipeline\test_openspec_parser_src.py:77` | Function | Function: test_load_bundle_from_change() |
| `tests\pipeline\test_openspec_parser_src.py:106` | Function | Function: test_write_bundle_and_main_flow() |
| `tests\pipeline\test_orchestrator_single.py:21` | Function | Function: bundle_ws() |
| `tests\pipeline\test_workstream_authoring.py:45` | Function | Function: create_bundle_file() |
| `tests\test_prompt_engine.py:19` | Function | Function: sample_bundle() |
| `tests\test_validators.py:38` | Function | Function: sample_bundle() |

---

### 4. Orchestrator

| Location | Type | Description |
|----------|------|-------------|
| `AGENTIC_DEV_PROTOTYPE\src\orchestrator\core.py:23` | Class | Class definition: OrchestratorCore |
| `AGENTIC_DEV_PROTOTYPE\tests\test_orchestrator_core.py:117` | Class | Class definition: TestOrchestratorCore |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\orchestrator\core.py:23` | Class | Class definition: OrchestratorCore |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\bootstrap\orchestrator.py:18` | Class | Class definition: BootstrapOrchestrator |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\orchestrator.py:27` | Class | Class definition: Orchestrator |
| `core\engine\pipeline_plus_orchestrator.py:16` | Class | Class definition: PipelinePlusOrchestrator |
| `engine\interfaces\orchestrator_interface.py:12` | Class | Class definition: OrchestratorInterface |
| `engine\orchestrator\orchestrator.py:29` | Class | Class definition: Orchestrator |
| `examples\orchestrator_integration_demo.py:11` | Class | Class definition: EnhancedOrchestrator |
| `tests\integration\test_aim_orchestrator_integration.py:189` | Class | Class definition: TestOrchestratorAIMIntegration |
| `tests\integration\test_aim_orchestrator_integration.py:228` | Class | Class definition: TestAIMEndToEndWithOrchestrator |
| `devdocs\archive\2025-11\error_legacy\ARCHITECTURE.md:1` | Doc | Documentation: ARCHITECTURE.md |
| `docs\ARCHITECTURE.md:1` | Doc | Documentation: ARCHITECTURE.md |
| `AGENTIC_DEV_PROTOTYPE\tests\test_orchestrator_core.py:121` | Function | Function: orchestrator() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_run_lifecycle.py:27` | Function | Function: orchestrator() |
| `core\config_loader.py:51` | Function | Function: get_orchestrator_config() |
| `examples\orchestrator_integration_demo.py:202` | Function | Function: demonstrate_orchestrator_integration() |
| `scripts\test_adapters.py:157` | Function | Function: test_orchestrator_registration() |
| `scripts\test_state_store.py:194` | Function | Function: test_orchestrator_integration() |
| `scripts\validate_engine.py:132` | Function | Function: test_orchestrator_instance() |
| `scripts\validate_engine.py:185` | Function | Function: test_orchestrator_with_state() |
| `tests\integration\test_aim_orchestrator_integration.py:194` | Function | Function: test_orchestrator_uses_capability() |
| `tests\test_integration.py:8` | Function | Function: orchestrator() |
| `tests\test_integration.py:11` | Function | Function: test_orchestrator_initialization() |
| `tests\test_integration.py:20` | Function | Function: test_orchestrator_has_all_adapters() |
| `tests\test_integration.py:25` | Function | Function: test_orchestrator_adapter_configuration() |
| `tests\test_integration.py:43` | Function | Function: test_orchestrator_default_config() |
| `tests\test_invoke_config.py:48` | Function | Function: test_get_orchestrator_config() |
| `tests\test_worker_pool.py:29` | Function | Function: mock_orchestrator() |

---

### 5. Executor

| Location | Type | Description |
|----------|------|-------------|
| `AGENTIC_DEV_PROTOTYPE\src\orchestrator\parallel_executor.py:17` | Class | Class definition: ParallelExecutor |
| `AGENTIC_DEV_PROTOTYPE\tests\test_dependency_resolution.py:188` | Class | Class definition: TestParallelExecutor |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\orchestrator\parallel_executor.py:17` | Class | Class definition: ParallelExecutor |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\resilient_executor.py:11` | Class | Class definition: ResilientExecutor |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\resilience\test_resilient_executor.py:14` | Class | Class definition: TestResilientExecutor |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\resilience\test_resilient_executor.py:17` | Function | Function: test_create_executor() |

---

### 6. Scheduler

| Location | Type | Description |
|----------|------|-------------|
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\scheduler.py:30` | Class | Class definition: ExecutionScheduler |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_scheduling.py:50` | Class | Class definition: TestSchedulerBasics |
| `core\engine\scheduler.py:45` | Class | Class definition: TaskScheduler |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_scheduling.py:53` | Function | Function: test_create_scheduler() |

---

### 7. Tool Profile

| Location | Type | Description |
|----------|------|-------------|
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\bootstrap\selector.py:12` | Class | Class definition: ProfileSelector |
| `core\engine\context_estimator.py:12` | Class | Class definition: ContextProfile |
| `core\engine\performance.py:15` | Class | Class definition: PerformanceProfile |
| `core\planning\parallelism_detector.py:16` | Class | Class definition: ParallelismProfile |
| `invoke.yaml:1` | Config | Configuration file: invoke.yaml |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\bootstrap\selector.py:19` | Function | Function: _load_profiles() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\bootstrap\test_validator.py:239` | Function | Function: test_profile_id_mismatch() |
| `core\engine\performance.py:41` | Function | Function: profile_operation() |
| `core\engine\tools.py:55` | Function | Function: load_tool_profiles() |
| `core\engine\tools.py:96` | Function | Function: get_tool_profile() |

---

### 8. Circuit Breaker

| Location | Type | Description |
|----------|------|-------------|
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\circuit_breaker.py:12` | Class | Class definition: CircuitBreakerState |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\circuit_breaker.py:19` | Class | Class definition: CircuitBreaker |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\circuit_breaker.py:174` | Class | Class definition: CircuitBreakerOpen |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\resilience\test_circuit_breaker.py:14` | Class | Class definition: TestCircuitBreaker |
| `core\engine\hardening.py:60` | Class | Class definition: CircuitBreaker |
| `core\engine\hardening.py:130` | Class | Class definition: CircuitBreakerError |
| `core\engine\validators.py:33` | Class | Class definition: CircuitBreakerTrip |
| `core\engine\validators.py:212` | Class | Class definition: CircuitBreaker |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\resilience\test_circuit_breaker.py:17` | Function | Function: test_create_circuit_breaker() |
| `core\config_loader.py:99` | Function | Function: get_circuit_breaker_config() |
| `tests\test_integration.py:65` | Function | Function: test_circuit_breaker_integration() |
| `tests\test_invoke_config.py:66` | Function | Function: test_get_circuit_breaker_config() |
| `tests\test_invoke_config.py:140` | Function | Function: test_circuit_breaker_config_migration() |
| `tests\test_validators.py:28` | Function | Function: circuit_breaker() |
| `tests\test_validators.py:78` | Function | Function: test_circuit_breaker_trip_creation() |
| `tests\test_validators.py:191` | Function | Function: test_circuit_breaker_max_attempts() |
| `tests\test_validators.py:205` | Function | Function: test_circuit_breaker_within_attempts() |
| `tests\test_validators.py:217` | Function | Function: test_circuit_breaker_from_config() |
| `tests\test_validators.py:232` | Function | Function: test_circuit_breaker_from_config_defaults() |
| `tests\test_validators.py:267` | Function | Function: test_circuit_breaker_initialization() |
| `tests\test_validators.py:301` | Function | Function: test_circuit_breaker_trip_with_error_signature() |
| `tests\test_validators.py:313` | Function | Function: test_circuit_breaker_trip_with_diff_hash() |

---

### 9. Retry Logic

| Location | Type | Description |
|----------|------|-------------|
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\retry.py:12` | Class | Class definition: RetryStrategy |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\retry.py:75` | Class | Class definition: SimpleRetry |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\retry.py:138` | Class | Class definition: RetryExhausted |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\resilience\test_retry.py:19` | Class | Class definition: TestSimpleRetry |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\resilience\test_retry.py:167` | Class | Class definition: TestRetryExhausted |
| `engine\queue\retry_policy.py:23` | Class | Class definition: RetryPolicy |
| `AGENTIC_DEV_PROTOTYPE\tests\test_orchestrator_core.py:73` | Function | Function: test_retry_after_failure() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\resilience\test_resilient_executor.py:62` | Function | Function: test_retry_on_failure() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\resilience\test_retry.py:22` | Function | Function: test_create_simple_retry() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\resilience\test_retry.py:49` | Function | Function: test_retry_after_failure() |
| `core\engine\hardening.py:18` | Function | Function: retry_with_backoff() |
| `engine\queue\job_wrapper.py:101` | Function | Function: mark_retry() |
| `engine\queue\job_wrapper.py:112` | Function | Function: can_retry() |
| `engine\queue\retry_policy.py:54` | Function | Function: should_retry() |
| `tests\test_job_wrapper.py:124` | Function | Function: test_mark_retry() |
| `tests\test_job_wrapper.py:146` | Function | Function: test_can_retry() |
| `tests\test_retry_policy.py:20` | Function | Function: test_retry_policy_defaults() |
| `tests\test_retry_policy.py:30` | Function | Function: test_should_retry() |
| `tests\test_retry_policy.py:146` | Function | Function: test_default_retry_policy() |
| `tests\test_retry_policy.py:153` | Function | Function: test_fast_retry_policy() |
| `tests\test_retry_policy.py:160` | Function | Function: test_slow_retry_policy() |
| `tests\test_retry_policy.py:168` | Function | Function: test_no_retry_policy() |

---

### 10. Recovery Strategy

| Location | Type | Description |
|----------|------|-------------|
| `core\engine\recovery_manager.py:11` | Class | Class definition: RecoveryManager |

---

### 11. Timeout Handling

| Location | Type | Description |
|----------|------|-------------|
| `aim\exceptions.py:99` | Class | Class definition: AIMAdapterTimeoutError |
| `core\engine\validators.py:23` | Class | Class definition: TimeoutResult |
| `core\engine\validators.py:104` | Class | Class definition: TimeoutMonitor |
| `core\state\task_queue.py:34` | Class | Class definition: TaskTimeouts |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\adapters\base.py:39` | Function | Function: get_timeout() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\adapters\base.py:120` | Function | Function: get_timeout() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\adapters\test_base.py:63` | Function | Function: test_get_timeout_default() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\adapters\test_base.py:74` | Function | Function: test_get_timeout_custom() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\adapters\test_subprocess_adapter.py:109` | Function | Function: test_execute_timeout() |
| `core\engine\adapters\base.py:64` | Function | Function: get_default_timeout() |
| `error\shared\utils\security.py:219` | Function | Function: get_timeout() |
| `tests\error\unit\test_agent_adapters.py:44` | Function | Function: test_invocation_with_custom_timeout() |
| `tests\integration\test_aim_orchestrator_integration.py:166` | Function | Function: test_execute_with_aim_timeout_payload() |
| `tests\pipeline\test_aim_bridge.py:158` | Function | Function: test_timeout_handling() |
| `tests\plugins\test_cross_cutting.py:234` | Function | Function: test_timeout_enforcement() |
| `tests\plugins\test_cross_cutting.py:349` | Function | Function: test_timeout_enforcement() |
| `tests\plugins\test_integration.py:292` | Function | Function: test_subprocess_has_timeout() |
| `tests\plugins\test_python_fix.py:194` | Function | Function: test_execute_with_timeout() |
| `tests\test_adapters.py:70` | Function | Function: test_adapter_get_default_timeout() |
| `tests\test_escalation.py:105` | Function | Function: test_should_escalate_timeout() |
| `tests\test_invoke_config.py:158` | Function | Function: test_tool_timeout_consistency() |
| `tests\test_invoke_utils.py:68` | Function | Function: test_run_command_with_timeout() |
| `tests\test_validators.py:22` | Function | Function: timeout_monitor() |
| `tests\test_validators.py:66` | Function | Function: test_timeout_result_creation() |
| `tests\test_validators.py:160` | Function | Function: test_timeout_monitor_no_timeout() |
| `tests\test_validators.py:178` | Function | Function: test_timeout_monitor_record_output() |
| `tests\test_validators.py:280` | Function | Function: test_timeout_monitor_initialization() |
| `tests\test_validators.py:343` | Function | Function: test_timeout_result_defaults() |

---

### 12. Dependency Resolution

| Location | Type | Description |
|----------|------|-------------|
| `AGENTIC_DEV_PROTOTYPE\src\orchestrator\dependency_resolver.py:16` | Class | Class definition: DependencyResolver |
| `AGENTIC_DEV_PROTOTYPE\tests\test_dependency_resolution.py:17` | Class | Class definition: TestDependencyResolver |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\orchestrator\dependency_resolver.py:16` | Class | Class definition: DependencyResolver |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_scheduling.py:97` | Class | Class definition: TestDependencyManagement |
| `core\state\bundles.py:80` | Class | Class definition: BundleDependencyError |
| `AGENTIC_DEV_PROTOTYPE\src\orchestrator\dependency_resolver.py:212` | Function | Function: get_dependency_info() |
| `AGENTIC_DEV_PROTOTYPE\src\prompt_renderer.py:243` | Function | Function: _render_dependencies() |
| `AGENTIC_DEV_PROTOTYPE\src\validators\guard_rules_engine.py:129` | Function | Function: check_dependencies_valid() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_dependency_resolution.py:64` | Function | Function: test_dependency_graph_building() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_dependency_resolution.py:175` | Function | Function: test_get_dependency_info() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_guard_rules.py:80` | Function | Function: test_check_dependencies_valid() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_guard_rules.py:101` | Function | Function: test_check_circular_dependencies() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_guard_rules.py:235` | Function | Function: test_invalid_dependency_format() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_prompt_renderer.py:129` | Function | Function: test_render_dependencies() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_validation_gateway.py:88` | Function | Function: test_validate_dependency_violations() |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\orchestrator\dependency_resolver.py:212` | Function | Function: get_dependency_info() |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\prompt_renderer.py:243` | Function | Function: _render_dependencies() |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\validators\guard_rules_engine.py:129` | Function | Function: check_dependencies_valid() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_scheduling.py:23` | Function | Function: test_task_with_dependencies() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_scheduling.py:100` | Function | Function: test_simple_dependency() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_scheduling.py:112` | Function | Function: test_multiple_dependencies() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_scheduling.py:143` | Function | Function: test_no_dependencies_ready_immediately() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_scheduling.py:361` | Function | Function: test_batches_with_dependencies() |
| `core\state\bundles.py:354` | Function | Function: build_dependency_graph() |
| `tests\orchestrator\test_parallel_src.py:13` | Function | Function: test_run_many_respects_dependencies() |
| `tests\pipeline\test_bundles.py:93` | Function | Function: test_missing_dependency_raises() |
| `tests\pipeline\test_workstream_authoring.py:251` | Function | Function: test_validator_dependency_failure() |
| `tests\test_job_wrapper.py:162` | Function | Function: test_is_ready_no_dependencies() |
| `tests\test_job_wrapper.py:170` | Function | Function: test_is_ready_with_dependencies() |
| `tests\test_parallel_dependencies.py:6` | Function | Function: test_dependency_ordering_within_target_set() |
| `tests\test_parallelism_detection.py:103` | Function | Function: test_dependency_levels() |

---

## Error Detection

### 13. Error Engine

| Location | Type | Description |
|----------|------|-------------|
| `docs\plugin-ecosystem-summary.md:1` | Doc | Documentation: plugin-ecosystem-summary.md |
| `core\config_loader.py:83` | Function | Function: get_error_engine_config() |
| `tests\test_invoke_config.py:74` | Function | Function: test_get_error_engine_config() |

---

### 14. Error Plugin

| Location | Type | Description |
|----------|------|-------------|
| `error\engine\plugin_manager.py:17` | Class | Class definition: PluginManager |
| `error\engine\plugin_manager.py:111` | Class | Class definition: BasePlugin |
| `error\plugins\codespell\plugin.py:13` | Class | Class definition: CodespellPlugin |
| `error\plugins\echo\plugin.py:9` | Class | Class definition: EchoPlugin |
| `error\plugins\gitleaks\plugin.py:13` | Class | Class definition: GitleaksPlugin |
| `error\plugins\js_eslint\plugin.py:13` | Class | Class definition: ESLintPlugin |
| `error\plugins\js_prettier_fix\plugin.py:12` | Class | Class definition: PrettierFixPlugin |
| `error\plugins\json_jq\plugin.py:12` | Class | Class definition: JsonJqPlugin |
| `error\plugins\md_markdownlint\plugin.py:14` | Class | Class definition: MarkdownlintPlugin |
| `error\plugins\md_mdformat_fix\plugin.py:12` | Class | Class definition: MdformatFixPlugin |
| `error\plugins\powershell_pssa\plugin.py:13` | Class | Class definition: PSScriptAnalyzerPlugin |
| `error\plugins\python_bandit\plugin.py:13` | Class | Class definition: BanditPlugin |
| `error\plugins\python_black_fix\plugin.py:12` | Class | Class definition: BlackFixPlugin |
| `error\plugins\python_isort_fix\plugin.py:12` | Class | Class definition: IsortFixPlugin |
| `error\plugins\python_mypy\plugin.py:13` | Class | Class definition: MypyPlugin |
| `error\plugins\python_pylint\plugin.py:16` | Class | Class definition: PylintPlugin |
| `error\plugins\python_pyright\plugin.py:13` | Class | Class definition: PyrightPlugin |
| `error\plugins\python_ruff\plugin.py:13` | Class | Class definition: RuffPlugin |
| `error\plugins\python_safety\plugin.py:27` | Class | Class definition: SafetyPlugin |
| `error\plugins\semgrep\plugin.py:13` | Class | Class definition: SemgrepPlugin |
| `error\plugins\yaml_yamllint\plugin.py:13` | Class | Class definition: YamllintPlugin |
| `error\shared\utils\types.py:9` | Class | Class definition: PluginIssue |
| `error\shared\utils\types.py:21` | Class | Class definition: PluginResult |
| `error\shared\utils\types.py:32` | Class | Class definition: PluginManifest |
| `tests\plugins\test_cross_cutting.py:71` | Class | Class definition: TestCodespellPlugin |
| `tests\plugins\test_cross_cutting.py:150` | Class | Class definition: TestSemgrepPlugin |
| `tests\plugins\test_cross_cutting.py:254` | Class | Class definition: TestGitleaksPlugin |
| `tests\plugins\test_integration.py:12` | Class | Class definition: TestPluginDiscovery |
| `tests\plugins\test_integration.py:41` | Class | Class definition: TestPluginOrdering |
| `tests\plugins\test_markup_data.py:48` | Class | Class definition: TestYamllintPlugin |
| `tests\plugins\test_markup_data.py:133` | Class | Class definition: TestMdformatFixPlugin |
| `tests\plugins\test_markup_data.py:180` | Class | Class definition: TestMarkdownlintPlugin |
| `tests\plugins\test_markup_data.py:257` | Class | Class definition: TestJsonJqPlugin |
| `tests\plugins\test_powershell_js.py:68` | Class | Class definition: TestPSScriptAnalyzerPlugin |
| `tests\plugins\test_powershell_js.py:155` | Class | Class definition: TestPrettierFixPlugin |
| `tests\plugins\test_powershell_js.py:203` | Class | Class definition: TestESLintPlugin |
| `tests\plugins\test_python_fix.py:52` | Class | Class definition: TestIsortFixPlugin |
| `tests\plugins\test_python_fix.py:124` | Class | Class definition: TestBlackFixPlugin |
| `tests\plugins\test_python_lint.py:68` | Class | Class definition: TestRuffPlugin |
| `tests\plugins\test_python_lint.py:175` | Class | Class definition: TestPylintPlugin |
| `tests\plugins\test_python_security.py:74` | Class | Class definition: TestBanditPlugin |
| `tests\plugins\test_python_security.py:170` | Class | Class definition: TestSafetyPlugin |
| `tests\plugins\test_python_type.py:54` | Class | Class definition: TestMypyPlugin |
| `tests\plugins\test_python_type.py:154` | Class | Class definition: TestPyrightPlugin |
| `tests\test_ccpm_openspec_integration.py:66` | Class | Class definition: TestPathStandardizerPlugin |
| `error\engine\pipeline_engine.py:138` | Function | Function: _run_plugins() |
| `error\engine\plugin_manager.py:48` | Function | Function: get_plugins_for_file() |
| `error\engine\plugin_manager.py:73` | Function | Function: _load_plugin() |
| `error\engine\plugin_manager.py:92` | Function | Function: run_plugins() |
| `scripts\migrate_plugins_to_invoke.py:39` | Function | Function: migrate_plugin() |
| `tests\error\conftest.py:36` | Function | Function: mock_plugin_manager() |
| `tests\plugins\conftest.py:54` | Function | Function: assert_plugin_result_valid() |
| `tests\plugins\test_cross_cutting.py:74` | Function | Function: test_plugin_has_required_attributes() |
| `tests\plugins\test_cross_cutting.py:153` | Function | Function: test_plugin_has_required_attributes() |
| `tests\plugins\test_cross_cutting.py:257` | Function | Function: test_plugin_has_required_attributes() |
| `tests\plugins\test_integration.py:19` | Function | Function: test_plugin_discovery_finds_all_plugins() |
| `tests\plugins\test_integration.py:32` | Function | Function: test_missing_tool_plugin_skipped() |
| `tests\plugins\test_markup_data.py:51` | Function | Function: test_plugin_has_required_attributes() |
| `tests\plugins\test_markup_data.py:136` | Function | Function: test_plugin_has_required_attributes() |
| `tests\plugins\test_markup_data.py:183` | Function | Function: test_plugin_has_required_attributes() |
| `tests\plugins\test_markup_data.py:260` | Function | Function: test_plugin_has_required_attributes() |
| `tests\plugins\test_powershell_js.py:71` | Function | Function: test_plugin_has_required_attributes() |
| `tests\plugins\test_powershell_js.py:158` | Function | Function: test_plugin_has_required_attributes() |
| `tests\plugins\test_powershell_js.py:206` | Function | Function: test_plugin_has_required_attributes() |
| `tests\plugins\test_python_fix.py:55` | Function | Function: test_plugin_has_required_attributes() |
| `tests\plugins\test_python_fix.py:127` | Function | Function: test_plugin_has_required_attributes() |
| `tests\plugins\test_python_lint.py:71` | Function | Function: test_plugin_has_required_attributes() |
| `tests\plugins\test_python_lint.py:178` | Function | Function: test_plugin_has_required_attributes() |
| `tests\plugins\test_python_security.py:77` | Function | Function: test_plugin_has_required_attributes() |
| `tests\plugins\test_python_security.py:173` | Function | Function: test_plugin_has_required_attributes() |
| `tests\plugins\test_python_type.py:57` | Function | Function: test_plugin_has_required_attributes() |
| `tests\plugins\test_python_type.py:157` | Function | Function: test_plugin_has_required_attributes() |
| `tests\test_agent_coordinator.py:4` | Function | Function: dummy_plugin() |
| `tests\test_ccpm_openspec_integration.py:69` | Function | Function: test_plugin_structure() |
| `tests\test_ccpm_openspec_integration.py:78` | Function | Function: test_plugin_manifest() |
| `tests\test_ccpm_openspec_integration.py:90` | Function | Function: test_plugin_executable() |

---

### 15. Detection Rule

| Location | Type | Description |
|----------|------|-------------|
| `AGENTIC_DEV_PROTOTYPE\src\validators\guard_rules_engine.py:17` | Class | Class definition: GuardRulesEngine |
| `AGENTIC_DEV_PROTOTYPE\tests\test_guard_rules.py:16` | Class | Class definition: TestGuardRulesEngine |
| `AGENTIC_DEV_PROTOTYPE\tests\test_guard_rules.py:257` | Class | Class definition: TestGuardRulesIntegration |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\validators\guard_rules_engine.py:17` | Class | Class definition: GuardRulesEngine |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_scheduling.py:219` | Class | Class definition: TestCycleDetection |
| `tests\pipeline\test_aim_bridge.py:101` | Class | Class definition: TestLoadCoordinationRules |
| `AGENTIC_DEV_PROTOTYPE\scripts\validate_phase_spec.py:111` | Function | Function: _validate_business_rules() |
| `AGENTIC_DEV_PROTOTYPE\src\schema_generator.py:184` | Function | Function: generate_validation_rules_schema() |
| `AGENTIC_DEV_PROTOTYPE\src\validators\guard_rules_engine.py:38` | Function | Function: _load_rules() |
| `AGENTIC_DEV_PROTOTYPE\src\validators\guard_rules_engine.py:243` | Function | Function: check_all_rules() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_guard_rules.py:29` | Function | Function: test_load_rules() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_guard_rules.py:156` | Function | Function: test_check_all_rules() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_schema_generator.py:81` | Function | Function: test_generate_validation_rules_schema() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_schema_generator.py:92` | Function | Function: test_validation_rules_severity_enum() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_schema_generator.py:101` | Function | Function: test_validation_rules_category_enum() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_validation_gateway.py:67` | Function | Function: test_validate_guard_rule_violations() |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\schema_generator.py:184` | Function | Function: generate_validation_rules_schema() |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\validators\guard_rules_engine.py:38` | Function | Function: _load_rules() |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\validators\guard_rules_engine.py:243` | Function | Function: check_all_rules() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\router.py:78` | Function | Function: _matches_rule() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_routing.py:124` | Function | Function: test_routing_rules_loaded() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_run_lifecycle.py:339` | Function | Function: test_terminal_state_detection() |
| `aim\bridge.py:95` | Function | Function: load_coordination_rules() |
| `engine\queue\escalation.py:194` | Function | Function: add_rule() |
| `engine\queue\escalation.py:204` | Function | Function: get_rule() |
| `tests\integration\test_aim_end_to_end.py:38` | Function | Function: test_coordination_rules_load() |
| `tests\integration\test_aim_end_to_end.py:44` | Function | Function: test_tool_detection() |
| `tests\integration\test_aim_end_to_end.py:117` | Function | Function: test_capability_routing_follows_rules() |
| `tests\orchestrator\test_parallel_src.py:47` | Function | Function: test_run_many_cycle_detection() |
| `tests\pipeline\test_aim_bridge.py:105` | Function | Function: test_loads_valid_rules() |
| `tests\test_ccpm_openspec_integration.py:45` | Function | Function: test_rules_installed() |
| `tests\test_escalation.py:12` | Function | Function: test_default_escalation_rules() |
| `tests\test_escalation.py:22` | Function | Function: test_aider_escalation_rule() |
| `tests\test_escalation.py:41` | Function | Function: test_custom_rules() |
| `tests\test_escalation.py:56` | Function | Function: test_should_escalate_no_rule() |
| `tests\test_escalation.py:117` | Function | Function: test_create_escalation_job_no_rule() |
| `tests\test_escalation.py:245` | Function | Function: test_add_rule() |
| `tests\test_escalation.py:260` | Function | Function: test_get_rule() |
| `tests\test_parallelism_detection.py:11` | Function | Function: test_simple_parallel_detection() |

---

### 16. Error State Machine

| Location | Type | Description |
|----------|------|-------------|
| `AGENTIC_DEV_PROTOTYPE\src\orchestrator\state_machine.py:29` | Class | Class definition: StateMachine |
| `AGENTIC_DEV_PROTOTYPE\tests\test_orchestrator_core.py:18` | Class | Class definition: TestStateMachine |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\orchestrator\state_machine.py:29` | Class | Class definition: StateMachine |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\state_machine.py:29` | Class | Class definition: RunStateMachine |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\state_machine.py:105` | Class | Class definition: StepStateMachine |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_run_lifecycle.py:322` | Class | Class definition: TestStateMachine |
| `docs\state_machine.md:1` | Doc | Documentation: state_machine.md |

---

### 17. Fix Strategy

| Location | Type | Description |
|----------|------|-------------|
| `core\engine\circuit_breakers.py:134` | Class | Class definition: FixLoopState |
| `error\plugins\js_prettier_fix\plugin.py:12` | Class | Class definition: PrettierFixPlugin |
| `error\plugins\md_mdformat_fix\plugin.py:12` | Class | Class definition: MdformatFixPlugin |
| `error\plugins\python_black_fix\plugin.py:12` | Class | Class definition: BlackFixPlugin |
| `error\plugins\python_isort_fix\plugin.py:12` | Class | Class definition: IsortFixPlugin |
| `tests\plugins\test_integration.py:103` | Class | Class definition: TestMechanicalAutofix |
| `tests\plugins\test_markup_data.py:133` | Class | Class definition: TestMdformatFixPlugin |
| `tests\plugins\test_powershell_js.py:155` | Class | Class definition: TestPrettierFixPlugin |
| `tests\plugins\test_python_fix.py:52` | Class | Class definition: TestIsortFixPlugin |
| `tests\plugins\test_python_fix.py:124` | Class | Class definition: TestBlackFixPlugin |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\bootstrap\validator.py:172` | Function | Function: _auto_fix_common_issues() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\bootstrap\test_validator.py:16` | Function | Function: setup_fixtures() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\bootstrap\test_validator.py:209` | Function | Function: test_missing_defaults_autofix() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_routing.py:206` | Function | Function: test_fixed_strategy() |
| `aider\engine.py:126` | Function | Function: build_fix_prompt() |
| `aider\engine.py:210` | Function | Function: run_aider_fix() |
| `core\engine\circuit_breakers.py:157` | Function | Function: allow_fix_attempt() |
| `core\engine\orchestrator.py:222` | Function | Function: run_static_with_fix() |
| `core\engine\orchestrator.py:278` | Function | Function: run_runtime_with_fix() |
| `error\engine\error_pipeline_service.py:33` | Function | Function: execute_fix_state() |
| `error\engine\error_pipeline_service.py:84` | Function | Function: run_error_pipeline_with_fixes() |
| `tests\error\unit\test_state_machine.py:69` | Function | Function: test_mechanical_fix_to_recheck() |
| `tests\pipeline\test_fix_loop.py:37` | Function | Function: test_static_fix_succeeds() |
| `tests\pipeline\test_fix_loop.py:63` | Function | Function: test_runtime_fix_exhausts() |
| `tests\plugins\test_integration.py:110` | Function | Function: test_fix_then_recheck_workflow() |
| `tests\plugins\test_integration.py:230` | Function | Function: test_fixes_in_temp_directory() |
| `tests\test_prompt_engine.py:167` | Function | Function: test_infer_classification_operation_bugfix() |

---

### 18. Incremental Detection

| Location | Type | Description |
|----------|------|-------------|
| `error\engine\file_hash_cache.py:16` | Class | Class definition: FileHashCache |
| `.migration_backup_20251120_144334\spec\tools\spec_guard\guard.py:18` | Function | Function: compute_hash() |
| `.migration_backup_20251120_144334\spec\tools\spec_indexer\indexer.py:43` | Function | Function: compute_hash() |
| `.migration_backup_20251120_144334\spec\tools\spec_patcher\patcher.py:19` | Function | Function: compute_hash() |
| `aim\environment\scanner.py:112` | Function | Function: _hash_file() |
| `aim\tests\environment\test_scanner.py:123` | Function | Function: test_hash_file() |
| `aim\tests\environment\test_scanner.py:139` | Function | Function: test_hash_file_different_content() |
| `aim\tests\environment\test_scanner.py:152` | Function | Function: test_hash_file_nonexistent() |
| `core\engine\circuit_breakers.py:147` | Function | Function: compute_diff_hash() |
| `core\engine\orchestrator.py:218` | Function | Function: _diff_hash_from_tool_result() |
| `core\state\crud.py:846` | Function | Function: get_patches_by_hash() |
| `specifications\tools\guard\guard.py:18` | Function | Function: compute_hash() |
| `specifications\tools\indexer\indexer.py:43` | Function | Function: compute_hash() |
| `specifications\tools\patcher\patcher.py:19` | Function | Function: compute_hash() |
| `tests\error\unit\test_security.py:126` | Function | Function: test_redact_git_hashes() |
| `tests\test_incremental_cache.py:8` | Function | Function: test_file_hash_cache_roundtrip() |
| `tests\test_patch_manager.py:298` | Function | Function: test_patch_hash_consistency() |
| `tests\test_validators.py:313` | Function | Function: test_circuit_breaker_trip_with_diff_hash() |

---

### 19. File Hash Cache

| Location | Type | Description |
|----------|------|-------------|
| `tests\test_incremental_cache.py:8` | Function | Function: test_file_hash_cache_roundtrip() |

---

### 20. Error Escalation

| Location | Type | Description |
|----------|------|-------------|
| `engine\queue\escalation.py:40` | Class | Class definition: EscalationManager |
| `engine\queue\escalation.py:59` | Function | Function: should_escalate() |
| `engine\queue\escalation.py:85` | Function | Function: create_escalation_job() |
| `engine\queue\escalation.py:172` | Function | Function: get_escalation_chain() |
| `engine\queue\job_wrapper.py:106` | Function | Function: mark_escalated() |
| `tests\test_escalation.py:12` | Function | Function: test_default_escalation_rules() |
| `tests\test_escalation.py:22` | Function | Function: test_aider_escalation_rule() |
| `tests\test_escalation.py:33` | Function | Function: test_codex_no_escalation() |
| `tests\test_escalation.py:56` | Function | Function: test_should_escalate_no_rule() |
| `tests\test_escalation.py:68` | Function | Function: test_should_escalate_no_target() |
| `tests\test_escalation.py:81` | Function | Function: test_should_escalate_not_enough_retries() |
| `tests\test_escalation.py:93` | Function | Function: test_should_escalate_enough_retries() |
| `tests\test_escalation.py:105` | Function | Function: test_should_escalate_timeout() |
| `tests\test_escalation.py:117` | Function | Function: test_create_escalation_job_no_rule() |
| `tests\test_escalation.py:130` | Function | Function: test_create_escalation_job_no_target() |
| `tests\test_escalation.py:143` | Function | Function: test_create_escalation_job_aider_to_codex() |
| `tests\test_escalation.py:198` | Function | Function: test_escalation_priority() |
| `tests\test_escalation.py:212` | Function | Function: test_get_escalation_chain_single() |
| `tests\test_escalation.py:221` | Function | Function: test_get_escalation_chain_multi() |
| `tests\test_escalation.py:231` | Function | Function: test_get_escalation_chain_circular() |
| `tests\test_escalation.py:299` | Function | Function: test_escalation_job_metadata() |
| `tests\test_job_wrapper.py:135` | Function | Function: test_mark_escalated() |

---

### 21. Plugin Manifest

| Location | Type | Description |
|----------|------|-------------|
| `error\shared\utils\types.py:32` | Class | Class definition: PluginManifest |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\MANIFEST.json:1` | Config | Configuration file: manifest.json |
| `error\plugins\codespell\manifest.json:1` | Config | Configuration file: manifest.json |
| `error\plugins\echo\manifest.json:1` | Config | Configuration file: manifest.json |
| `error\plugins\gitleaks\manifest.json:1` | Config | Configuration file: manifest.json |
| `error\plugins\js_eslint\manifest.json:1` | Config | Configuration file: manifest.json |
| `error\plugins\js_prettier_fix\manifest.json:1` | Config | Configuration file: manifest.json |
| `error\plugins\json_jq\manifest.json:1` | Config | Configuration file: manifest.json |
| `error\plugins\md_markdownlint\manifest.json:1` | Config | Configuration file: manifest.json |
| `error\plugins\md_mdformat_fix\manifest.json:1` | Config | Configuration file: manifest.json |
| `error\plugins\path_standardizer\manifest.json:1` | Config | Configuration file: manifest.json |
| `error\plugins\powershell_pssa\manifest.json:1` | Config | Configuration file: manifest.json |
| `error\plugins\python_bandit\manifest.json:1` | Config | Configuration file: manifest.json |
| `error\plugins\python_black_fix\manifest.json:1` | Config | Configuration file: manifest.json |
| `error\plugins\python_isort_fix\manifest.json:1` | Config | Configuration file: manifest.json |
| `error\plugins\python_mypy\manifest.json:1` | Config | Configuration file: manifest.json |
| `error\plugins\python_pylint\manifest.json:1` | Config | Configuration file: manifest.json |
| `error\plugins\python_pyright\manifest.json:1` | Config | Configuration file: manifest.json |
| `error\plugins\python_ruff\manifest.json:1` | Config | Configuration file: manifest.json |
| `error\plugins\python_safety\manifest.json:1` | Config | Configuration file: manifest.json |
| `error\plugins\semgrep\manifest.json:1` | Config | Configuration file: manifest.json |
| `error\plugins\test_runner\manifest.json:1` | Config | Configuration file: manifest.json |
| `error\plugins\yaml_yamllint\manifest.json:1` | Config | Configuration file: manifest.json |
| `tests\test_ccpm_openspec_integration.py:78` | Function | Function: test_plugin_manifest() |

---

### 22. Error Context

| Location | Type | Description |
|----------|------|-------------|
| `core\state\db.py:78` | Function | Function: get_error_context() |
| `core\state\db.py:94` | Function | Function: save_error_context() |
| `core\state\db_sqlite.py:69` | Function | Function: get_error_context() |
| `core\state\db_sqlite.py:84` | Function | Function: save_error_context() |
| `tests\error\conftest.py:43` | Function | Function: error_context() |

---

## Specifications

### 23. OpenSpec

| Location | Type | Description |
|----------|------|-------------|
| `pm\bridge.py:24` | Class | Class definition: OpenSpecToPRDConverter |
| `scripts\spec_to_workstream.py:30` | Class | Class definition: OpenSpecParser |
| `docs\Project_Management_docs\QUICKSTART_OPENSPEC.md:1` | Doc | Documentation: QUICKSTART_OPENSPEC.md |
| `docs\Project_Management_docs\openspec_bridge.md:1` | Doc | Documentation: openspec_bridge.md |
| `.migration_backup_20251120_144334\spec\tools\spec_renderer\renderer.py:63` | Function | Function: render_openspec_specs() |
| `pm\bridge.py:453` | Function | Function: openspec_to_prd() |
| `pm\bridge.py:339` | Function | Function: openspec_to_prd() |
| `pm\bridge.py:372` | Function | Function: openspec_to_workstreams() |
| `specifications\tools\renderer\renderer.py:63` | Function | Function: render_openspec_specs() |

---

### 24. Specification Index

| Location | Type | Description |
|----------|------|-------------|
| `tools\hardcoded_path_indexer.py:77` | Class | Class definition: HardcodedPathIndexer |
| `tasks.py:129` | Function | Function: generate_spec_index() |

---

### 25. Spec Resolver

| Location | Type | Description |
|----------|------|-------------|
| `AGENTIC_DEV_PROTOTYPE\src\orchestrator\dependency_resolver.py:16` | Class | Class definition: DependencyResolver |
| `AGENTIC_DEV_PROTOTYPE\src\spec_resolver.py:43` | Class | Class definition: SpecResolver |
| `AGENTIC_DEV_PROTOTYPE\tests\test_dependency_resolution.py:17` | Class | Class definition: TestDependencyResolver |
| `AGENTIC_DEV_PROTOTYPE\tests\test_spec_resolver.py:25` | Class | Class definition: TestSpecResolver |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\orchestrator\dependency_resolver.py:16` | Class | Class definition: DependencyResolver |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\spec_resolver.py:43` | Class | Class definition: SpecResolver |
| `AGENTIC_DEV_PROTOTYPE\tests\test_spec_resolver.py:17` | Function | Function: resolver() |

---

### 26. Spec Guard

| Location | Type | Description |
|----------|------|-------------|
| `AGENTIC_DEV_PROTOTYPE\src\validators\guard_rules_engine.py:17` | Class | Class definition: GuardRulesEngine |
| `AGENTIC_DEV_PROTOTYPE\tests\test_guard_rules.py:16` | Class | Class definition: TestGuardRulesEngine |
| `AGENTIC_DEV_PROTOTYPE\tests\test_guard_rules.py:257` | Class | Class definition: TestGuardRulesIntegration |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\validators\guard_rules_engine.py:17` | Class | Class definition: GuardRulesEngine |
| `AGENTIC_DEV_PROTOTYPE\tests\test_validation_gateway.py:67` | Function | Function: test_validate_guard_rule_violations() |

---

### 27. Spec Patcher

*No implementation locations found for this term.*

---

### 28. Change Proposal

| Location | Type | Description |
|----------|------|-------------|
| `core\engine\integration_worker.py:192` | Function | Function: _get_changed_files() |
| `core\tool_instrumentation.py:221` | Function | Function: emit_file_state_change() |
| `error\engine\file_hash_cache.py:43` | Function | Function: has_changed() |
| `pm\bridge.py:79` | Function | Function: _parse_proposal() |
| `scripts\spec_to_workstream.py:277` | Function | Function: list_changes() |
| `scripts\spec_to_workstream.py:53` | Function | Function: _parse_proposal() |
| `tests\pipeline\test_openspec_parser_src.py:77` | Function | Function: test_load_bundle_from_change() |
| `tests\test_engine_determinism.py:10` | Function | Function: test_engine_skip_on_unchanged() |
| `tests\test_openspec_convert.py:9` | Function | Function: _write_change() |
| `tests\test_openspec_convert.py:32` | Function | Function: test_change_to_workstream_roundtrip() |

---

### 29. Spec Bridge

| Location | Type | Description |
|----------|------|-------------|
| `pm\bridge.py:324` | Class | Class definition: BridgeAPI |

---

### 30. URI Resolution

*No implementation locations found for this term.*

---

## State Management

### 31. Pipeline Database

| Location | Type | Description |
|----------|------|-------------|
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\state\db.py:14` | Class | Class definition: Database |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\state\db.py:365` | Function | Function: init_db() |
| `core\engine\hardening.py:139` | Function | Function: check_database() |
| `core\state\db.py:44` | Function | Function: init_db() |
| `engine\queue\job_queue.py:47` | Function | Function: _init_db() |
| `tests\pipeline\test_fix_loop.py:11` | Function | Function: init_db_tmp() |
| `tests\pipeline\test_orchestrator_single.py:12` | Function | Function: init_db_tmp() |

---

### 32. Worktree Management

| Location | Type | Description |
|----------|------|-------------|
| `core\state\worktree.py:35` | Function | Function: get_worktrees_base() |
| `core\state\worktree.py:39` | Function | Function: get_worktree_path() |
| `core\state\worktree.py:43` | Function | Function: create_worktree_for_ws() |

---

### 33. State Transition

| Location | Type | Description |
|----------|------|-------------|
| `AGENTIC_DEV_PROTOTYPE\src\orchestrator\state_machine.py:24` | Class | Class definition: StateTransitionError |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\orchestrator\state_machine.py:24` | Class | Class definition: StateTransitionError |
| `tests\error\unit\test_state_machine.py:24` | Class | Class definition: TestStateTransitions |
| `AGENTIC_DEV_PROTOTYPE\src\orchestrator\state_machine.py:46` | Function | Function: can_transition() |
| `AGENTIC_DEV_PROTOTYPE\src\orchestrator\state_machine.py:62` | Function | Function: transition() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_orchestrator_core.py:31` | Function | Function: test_valid_transition_not_started_to_queued() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_orchestrator_core.py:40` | Function | Function: test_valid_transition_queued_to_running() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_orchestrator_core.py:48` | Function | Function: test_valid_transition_running_to_complete() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_orchestrator_core.py:57` | Function | Function: test_invalid_transition_queued_to_complete() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_orchestrator_core.py:64` | Function | Function: test_invalid_transition_from_complete() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_orchestrator_core.py:83` | Function | Function: test_transition_history() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_task_queue.py:223` | Function | Function: test_task_state_transitions() |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\orchestrator\state_machine.py:46` | Function | Function: can_transition() |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\orchestrator\state_machine.py:62` | Function | Function: transition() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\circuit_breaker.py:136` | Function | Function: _transition_to_open() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\circuit_breaker.py:142` | Function | Function: _transition_to_half_open() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\circuit_breaker.py:147` | Function | Function: _transition_to_closed() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\state_machine.py:60` | Function | Function: can_transition() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\state_machine.py:80` | Function | Function: validate_transition() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\state_machine.py:126` | Function | Function: can_transition() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\state_machine.py:146` | Function | Function: validate_transition() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_run_lifecycle.py:128` | Function | Function: test_invalid_state_transition() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_run_lifecycle.py:325` | Function | Function: test_valid_run_transitions() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_run_lifecycle.py:333` | Function | Function: test_invalid_run_transitions() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_run_lifecycle.py:347` | Function | Function: test_step_state_transitions() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\resilience\test_circuit_breaker.py:89` | Function | Function: test_circuit_transitions_to_half_open() |
| `core\engine\worker.py:274` | Function | Function: _transition() |
| `engine\queue\job_queue.py:242` | Function | Function: _update_status_in_db() |
| `tests\test_worker_lifecycle.py:104` | Function | Function: test_invalid_state_transition() |

---

### 34. Checkpoint

*No implementation locations found for this term.*

---

### 35. Archive

| Location | Type | Description |
|----------|------|-------------|
| `core\planning\archive.py:7` | Function | Function: auto_archive() |

---

### 36. CRUD Operations

| Location | Type | Description |
|----------|------|-------------|
| `AGENTIC_DEV_PROTOTYPE\src\orchestrator\core.py:214` | Function | Function: get_status() |
| `AGENTIC_DEV_PROTOTYPE\src\orchestrator\core.py:277` | Function | Function: _update_ledger() |
| `AGENTIC_DEV_PROTOTYPE\src\orchestrator\dependency_resolver.py:177` | Function | Function: get_blocked_phases() |
| `AGENTIC_DEV_PROTOTYPE\src\orchestrator\dependency_resolver.py:212` | Function | Function: get_dependency_info() |
| `AGENTIC_DEV_PROTOTYPE\src\orchestrator\dependency_resolver.py:147` | Function | Function: get_level() |
| `AGENTIC_DEV_PROTOTYPE\src\orchestrator\parallel_executor.py:140` | Function | Function: get_execution_log() |
| `AGENTIC_DEV_PROTOTYPE\src\orchestrator\state_machine.py:98` | Function | Function: get_state() |
| `AGENTIC_DEV_PROTOTYPE\src\orchestrator\state_machine.py:102` | Function | Function: get_history() |
| `AGENTIC_DEV_PROTOTYPE\src\patch_manager.py:156` | Function | Function: create_backup() |
| `AGENTIC_DEV_PROTOTYPE\src\spec_renderer.py:59` | Function | Function: _get_spec_type() |
| `AGENTIC_DEV_PROTOTYPE\src\spec_resolver.py:225` | Function | Function: get_all_section_ids() |
| `AGENTIC_DEV_PROTOTYPE\src\task_queue.py:267` | Function | Function: get_task() |
| `AGENTIC_DEV_PROTOTYPE\src\task_queue.py:304` | Function | Function: get_stats() |
| `AGENTIC_DEV_PROTOTYPE\src\validators\schema_validator.py:144` | Function | Function: get_detailed_errors() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_dependency_resolution.py:147` | Function | Function: test_get_blocked_phases() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_dependency_resolution.py:175` | Function | Function: test_get_dependency_info() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_orchestrator_core.py:205` | Function | Function: test_get_status() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_orchestrator_core.py:215` | Function | Function: test_get_status_nonexistent_phase() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_patch_manager.py:121` | Function | Function: test_create_backup() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_patch_manager.py:143` | Function | Function: test_create_backup_nonexistent_file() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_schema_validator.py:141` | Function | Function: test_get_detailed_errors() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_spec_renderer.py:42` | Function | Function: test_get_spec_type_ups() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_spec_renderer.py:47` | Function | Function: test_get_spec_type_pps() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_spec_renderer.py:52` | Function | Function: test_get_spec_type_dr() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_spec_renderer.py:58` | Function | Function: test_get_spec_type_invalid() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_spec_resolver.py:68` | Function | Function: test_get_all_section_ids() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_task_queue.py:183` | Function | Function: test_get_task() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_task_queue.py:193` | Function | Function: test_get_task_not_found() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_task_queue.py:209` | Function | Function: test_get_stats() |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\orchestrator\core.py:214` | Function | Function: get_status() |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\orchestrator\core.py:277` | Function | Function: _update_ledger() |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\orchestrator\dependency_resolver.py:177` | Function | Function: get_blocked_phases() |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\orchestrator\dependency_resolver.py:212` | Function | Function: get_dependency_info() |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\orchestrator\dependency_resolver.py:147` | Function | Function: get_level() |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\orchestrator\parallel_executor.py:140` | Function | Function: get_execution_log() |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\orchestrator\state_machine.py:98` | Function | Function: get_state() |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\orchestrator\state_machine.py:102` | Function | Function: get_history() |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\patch_manager.py:156` | Function | Function: create_backup() |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\spec_renderer.py:59` | Function | Function: _get_spec_type() |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\spec_resolver.py:225` | Function | Function: get_all_section_ids() |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\task_queue.py:267` | Function | Function: get_task() |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\task_queue.py:304` | Function | Function: get_stats() |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\validators\schema_validator.py:144` | Function | Function: get_detailed_errors() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\adapters\base.py:39` | Function | Function: get_timeout() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\adapters\base.py:45` | Function | Function: get_max_parallel() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\adapters\base.py:120` | Function | Function: get_timeout() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\adapters\registry.py:96` | Function | Function: get_config() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\execution_request_builder.py:95` | Function | Function: create_execution_request() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\monitoring\progress_tracker.py:93` | Function | Function: update_task_progress() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\monitoring\progress_tracker.py:125` | Function | Function: get_completion_percent() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\monitoring\progress_tracker.py:144` | Function | Function: get_elapsed_time() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\monitoring\progress_tracker.py:155` | Function | Function: get_estimated_remaining_time() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\monitoring\progress_tracker.py:177` | Function | Function: get_estimated_completion_time() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\monitoring\progress_tracker.py:189` | Function | Function: get_snapshot() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\monitoring\run_monitor.py:82` | Function | Function: get_run_metrics() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\monitoring\run_monitor.py:163` | Function | Function: get_summary() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\orchestrator.py:35` | Function | Function: create_run() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\orchestrator.py:210` | Function | Function: create_step_attempt() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\orchestrator.py:308` | Function | Function: get_run_status() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\orchestrator.py:324` | Function | Function: get_run_steps() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\orchestrator.py:328` | Function | Function: get_run_events() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\circuit_breaker.py:160` | Function | Function: get_state() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\resilient_executor.py:89` | Function | Function: get_tool_state() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\resilient_executor.py:112` | Function | Function: get_all_states() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\retry.py:20` | Function | Function: get_delay() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\retry.py:87` | Function | Function: get_delay() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\retry.py:117` | Function | Function: get_delay() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\router.py:193` | Function | Function: create_router() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\router.py:155` | Function | Function: get_tool_config() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\router.py:159` | Function | Function: get_tool_command() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\router.py:166` | Function | Function: get_tool_limits() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\router.py:185` | Function | Function: get_capabilities() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\scheduler.py:259` | Function | Function: create_task_from_spec() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\scheduler.py:52` | Function | Function: get_ready_tasks() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\scheduler.py:115` | Function | Function: get_execution_order() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\scheduler.py:153` | Function | Function: get_parallel_batches() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\scheduler.py:194` | Function | Function: get_task() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\scheduler.py:198` | Function | Function: get_dependent_tasks() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\scheduler.py:216` | Function | Function: get_blocking_tasks() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\scheduler.py:228` | Function | Function: get_stats() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\state\db.py:356` | Function | Function: get_db() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\state\db.py:106` | Function | Function: create_run() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\state\db.py:132` | Function | Function: get_run() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\state\db.py:148` | Function | Function: update_run() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\state\db.py:175` | Function | Function: delete_run() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\state\db.py:219` | Function | Function: create_step_attempt() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\state\db.py:248` | Function | Function: get_step_attempt() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\state\db.py:263` | Function | Function: update_step_attempt() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\state\db.py:311` | Function | Function: create_event() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\adapters\test_base.py:16` | Function | Function: test_create_tool_config() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\adapters\test_base.py:63` | Function | Function: test_get_timeout_default() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\adapters\test_base.py:74` | Function | Function: test_get_timeout_custom() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\adapters\test_base.py:86` | Function | Function: test_get_max_parallel_default() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\adapters\test_base.py:97` | Function | Function: test_get_max_parallel_custom() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\adapters\test_base.py:113` | Function | Function: test_create_success_result() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\adapters\test_base.py:127` | Function | Function: test_create_failure_result() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\adapters\test_registry.py:20` | Function | Function: test_create_empty_registry() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\adapters\test_registry.py:42` | Function | Function: test_get_nonexistent_adapter() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\adapters\test_registry.py:67` | Function | Function: test_get_config() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\adapters\test_subprocess_adapter.py:17` | Function | Function: test_create_adapter() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_routing.py:231` | Function | Function: test_get_tool_config() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_routing.py:238` | Function | Function: test_get_tool_command() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_routing.py:243` | Function | Function: test_get_tool_limits() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_routing.py:249` | Function | Function: test_get_tool_limits_with_defaults() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_routing.py:255` | Function | Function: test_get_capabilities() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_run_lifecycle.py:35` | Function | Function: test_create_run() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_run_lifecycle.py:150` | Function | Function: test_create_step_attempt() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_scheduling.py:15` | Function | Function: test_create_task() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_scheduling.py:33` | Function | Function: test_create_from_spec() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_scheduling.py:53` | Function | Function: test_create_scheduler() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_scheduling.py:82` | Function | Function: test_get_task() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_scheduling.py:91` | Function | Function: test_get_nonexistent_task() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_scheduling.py:125` | Function | Function: test_get_dependent_tasks() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_scheduling.py:199` | Function | Function: test_get_blocking_tasks() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\engine\test_scheduling.py:414` | Function | Function: test_get_stats() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\monitoring\test_progress_tracker.py:16` | Function | Function: test_create_tracker() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\monitoring\test_run_monitor.py:16` | Function | Function: test_create_monitor() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\monitoring\test_run_monitor.py:22` | Function | Function: test_get_summary_empty() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\monitoring\test_run_monitor.py:39` | Function | Function: test_get_metrics_for_run() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\resilience\test_circuit_breaker.py:17` | Function | Function: test_create_circuit_breaker() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\resilience\test_circuit_breaker.py:162` | Function | Function: test_get_state() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\resilience\test_resilient_executor.py:17` | Function | Function: test_create_executor() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\resilience\test_resilient_executor.py:128` | Function | Function: test_get_tool_state() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\resilience\test_resilient_executor.py:139` | Function | Function: test_get_nonexistent_tool_state() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\resilience\test_resilient_executor.py:170` | Function | Function: test_get_all_states() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\resilience\test_retry.py:22` | Function | Function: test_create_simple_retry() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\resilience\test_retry.py:29` | Function | Function: test_get_delay_is_constant() |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\resilience\test_retry.py:88` | Function | Function: test_create_exponential_backoff() |
| `aim\bridge.py:31` | Function | Function: get_aim_registry_path() |
| `aim\bridge.py:418` | Function | Function: get_tool_version() |
| `aim\cli\commands\secrets.py:62` | Function | Function: get_secret() |
| `aim\cli\commands\secrets.py:144` | Function | Function: delete_secret() |
| `aim\environment\audit.py:376` | Function | Function: get_audit_logger() |
| `aim\environment\audit.py:287` | Function | Function: get_recent_events() |
| `aim\environment\audit.py:319` | Function | Function: get_stats() |
| `aim\environment\health.py:326` | Function | Function: _get_required_commands() |
| `aim\environment\health.py:357` | Function | Function: _get_timestamp() |
| `aim\environment\secrets.py:191` | Function | Function: get_secrets_manager() |
| `aim\environment\secrets.py:94` | Function | Function: get_secret() |
| `aim\environment\secrets.py:108` | Function | Function: delete_secret() |
| `aim\environment\secrets.py:185` | Function | Function: _get_timestamp() |
| `aim\environment\version_control.py:261` | Function | Function: update_config_pins() |
| `aim\registry\config_loader.py:213` | Function | Function: get_config_loader() |
| `aim\registry\config_loader.py:154` | Function | Function: get_registry() |
| `aim\registry\config_loader.py:164` | Function | Function: get_environment() |
| `aim\registry\config_loader.py:174` | Function | Function: get_audit() |
| `aim\registry\config_loader.py:184` | Function | Function: get_tool() |
| `aim\registry\config_loader.py:196` | Function | Function: get_capability() |
| `aim\tests\environment\test_audit.py:190` | Function | Function: test_get_recent_events() |
| `aim\tests\environment\test_audit.py:201` | Function | Function: test_get_stats() |
| `aim\tests\environment\test_audit.py:217` | Function | Function: test_get_stats_empty_log() |
| `aim\tests\environment\test_audit.py:247` | Function | Function: test_get_audit_logger_singleton() |
| `aim\tests\environment\test_audit.py:255` | Function | Function: test_get_audit_logger_with_path() |
| `aim\tests\environment\test_secrets.py:34` | Function | Function: test_set_and_get_secret() |
| `aim\tests\environment\test_secrets.py:44` | Function | Function: test_get_nonexistent_secret() |
| `aim\tests\environment\test_secrets.py:49` | Function | Function: test_delete_secret() |
| `aim\tests\environment\test_secrets.py:61` | Function | Function: test_delete_nonexistent_secret() |
| `aim\tests\environment\test_version_control.py:356` | Function | Function: test_update_config_pins() |
| `aim\tests\environment\test_version_control.py:369` | Function | Function: test_update_config_pins_creates_structure() |
| `aim\tests\registry\test_config_loader.py:168` | Function | Function: test_get_registry() |
| `aim\tests\registry\test_config_loader.py:177` | Function | Function: test_get_environment() |
| `aim\tests\registry\test_config_loader.py:185` | Function | Function: test_get_audit() |
| `aim\tests\registry\test_config_loader.py:193` | Function | Function: test_get_tool() |
| `aim\tests\registry\test_config_loader.py:202` | Function | Function: test_get_nonexistent_tool() |
| `aim\tests\registry\test_config_loader.py:209` | Function | Function: test_get_capability() |
| `aim\tests\registry\test_config_loader.py:217` | Function | Function: test_get_nonexistent_capability() |
| `aim\tests\registry\test_config_loader.py:228` | Function | Function: test_get_config_loader_singleton() |
| `core\config_loader.py:34` | Function | Function: get_tool_config() |
| `core\config_loader.py:51` | Function | Function: get_orchestrator_config() |
| `core\config_loader.py:67` | Function | Function: get_paths_config() |
| `core\config_loader.py:83` | Function | Function: get_error_engine_config() |
| `core\config_loader.py:99` | Function | Function: get_circuit_breaker_config() |
| `core\engine\adapters\base.py:64` | Function | Function: get_default_timeout() |
| `core\engine\adapters\base.py:67` | Function | Function: get_model_name() |
| `core\engine\aim_integration.py:54` | Function | Function: get_health_monitor() |
| `core\engine\aim_integration.py:62` | Function | Function: get_aim_audit_logger() |
| `core\engine\context_estimator.py:162` | Function | Function: get_file_statistics() |
| `core\engine\cost_tracker.py:83` | Function | Function: get_total_cost() |
| `core\engine\cost_tracker.py:120` | Function | Function: _emit_budget_warning() |
| `core\engine\cost_tracker.py:136` | Function | Function: _handle_budget_exceeded() |
| `core\engine\cost_tracker.py:165` | Function | Function: get_budget_status() |
| `core\engine\integration_worker.py:192` | Function | Function: _get_changed_files() |
| `core\engine\patch_manager.py:292` | Function | Function: get_patch_stats() |
| `core\engine\recovery_manager.py:79` | Function | Function: get_recoverable_runs() |
| `core\engine\scheduler.py:53` | Function | Function: get_next_tasks() |
| `core\engine\test_gates.py:189` | Function | Function: create_default_gates() |
| `core\engine\test_gates.py:177` | Function | Function: get_blocking_failures() |
| `core\engine\tools.py:96` | Function | Function: get_tool_profile() |
| `core\engine\tools.py:292` | Function | Function: _get_repo_root() |
| `core\engine\worker.py:203` | Function | Function: get_idle_worker() |
| `core\error_records.py:31` | Function | Function: create_error_record() |
| `core\error_records.py:133` | Function | Function: update_error_record() |
| `core\error_records.py:220` | Function | Function: get_errors_by_category() |
| `core\error_records.py:253` | Function | Function: get_error_statistics() |
| `core\error_records.py:298` | Function | Function: get_top_errors() |
| `core\file_lifecycle.py:91` | Function | Function: update_file_state() |
| `core\file_lifecycle.py:301` | Function | Function: update_file_metadata() |
| `core\file_lifecycle.py:336` | Function | Function: get_files_by_state() |
| `core\invoke_utils.py:217` | Function | Function: create_test_context() |
| `core\planning\ccpm_integration.py:224` | Function | Function: update_task_from_workstream() |
| `core\planning\ccpm_integration.py:229` | Function | Function: get_epic_metadata() |
| `core\state\audit_logger.py:226` | Function | Function: get_patch() |
| `core\state\audit_logger.py:250` | Function | Function: get_history() |
| `core\state\bundles.py:142` | Function | Function: get_workstream_dir() |
| `core\state\crud.py:23` | Function | Function: create_run() |
| `core\state\crud.py:66` | Function | Function: get_run() |
| `core\state\crud.py:105` | Function | Function: update_run_status() |
| `core\state\crud.py:206` | Function | Function: create_workstream() |
| `core\state\crud.py:252` | Function | Function: get_workstream() |
| `core\state\crud.py:290` | Function | Function: get_workstreams_for_run() |
| `core\state\crud.py:343` | Function | Function: update_workstream_status() |
| `core\state\crud.py:437` | Function | Function: get_step_attempts() |
| `core\state\crud.py:573` | Function | Function: get_errors() |
| `core\state\crud.py:678` | Function | Function: get_events() |
| `core\state\crud.py:799` | Function | Function: get_patches_by_ws() |
| `core\state\crud.py:846` | Function | Function: get_patches_by_hash() |
| `core\state\crud.py:890` | Function | Function: update_patch_status() |
| `core\state\db.py:34` | Function | Function: get_connection() |
| `core\state\db.py:78` | Function | Function: get_error_context() |
| `core\state\db.py:160` | Function | Function: get_recent_events() |
| `core\state\db.py:165` | Function | Function: get_all_events() |
| `core\state\db.py:170` | Function | Function: get_events_since() |
| `core\state\db_sqlite.py:69` | Function | Function: get_error_context() |
| `core\state\task_queue.py:123` | Function | Function: _get_task_file() |
| `core\state\task_queue.py:128` | Function | Function: _get_lock_file() |
| `core\state\task_queue.py:285` | Function | Function: get_status() |
| `core\state\worktree.py:26` | Function | Function: get_repo_root() |
| `core\state\worktree.py:35` | Function | Function: get_worktrees_base() |
| `core\state\worktree.py:39` | Function | Function: get_worktree_path() |
| `core\state\worktree.py:43` | Function | Function: create_worktree_for_ws() |
| `core\tool_instrumentation.py:308` | Function | Function: update_tool_health_status() |
| `core\tool_instrumentation.py:123` | Function | Function: _update_tool_metrics() |
| `core\ui_clients.py:40` | Function | Function: _get_conn() |
| `core\ui_clients.py:47` | Function | Function: get_file_lifecycle() |
| `core\ui_clients.py:169` | Function | Function: get_file_counts_by_state() |
| `core\ui_clients.py:195` | Function | Function: get_workstream() |
| `core\ui_clients.py:292` | Function | Function: get_workstream_counts_by_status() |
| `core\ui_clients.py:314` | Function | Function: get_error_record() |
| `core\ui_clients.py:409` | Function | Function: get_pipeline_summary() |
| `core\ui_clients.py:479` | Function | Function: _get_conn() |
| `core\ui_clients.py:482` | Function | Function: get_tool_health() |
| `core\ui_clients.py:547` | Function | Function: get_tools_summary() |
| `core\ui_settings.py:254` | Function | Function: get_settings_manager() |
| `core\ui_settings.py:44` | Function | Function: _get_default_config_path() |
| `core\ui_settings.py:66` | Function | Function: _get_default_settings() |
| `core\ui_settings.py:93` | Function | Function: get_interactive_tool() |
| `core\ui_settings.py:120` | Function | Function: get_available_interactive_tools() |
| `core\ui_settings.py:156` | Function | Function: get_tool_mode() |
| `core\ui_settings.py:168` | Function | Function: get_tool_config() |
| `core\ui_settings.py:181` | Function | Function: get_startup_config() |
| `core\ui_settings.py:204` | Function | Function: get_auto_launch_headless_tools() |
| `core\ui_settings.py:214` | Function | Function: get_interactive_layout() |
| `core\ui_settings.py:233` | Function | Function: get_settings_summary() |
| `core\ui_settings_cli.py:115` | Function | Function: cmd_get_mode() |
| `engine\adapters\aider_adapter.py:116` | Function | Function: get_tool_info() |
| `engine\adapters\codex_adapter.py:121` | Function | Function: get_tool_info() |
| `engine\adapters\git_adapter.py:122` | Function | Function: get_tool_info() |
| `engine\adapters\tests_adapter.py:130` | Function | Function: get_tool_info() |
| `engine\interfaces\adapter_interface.py:46` | Function | Function: get_tool_info() |
| `engine\interfaces\orchestrator_interface.py:46` | Function | Function: get_job_status() |
| `engine\interfaces\state_interface.py:15` | Function | Function: create_run() |
| `engine\interfaces\state_interface.py:19` | Function | Function: get_run() |
| `engine\interfaces\state_interface.py:23` | Function | Function: update_run_status() |
| `engine\interfaces\state_interface.py:31` | Function | Function: update_job_result() |
| `engine\interfaces\state_interface.py:39` | Function | Function: get_job() |
| `engine\interfaces\state_interface.py:51` | Function | Function: get_workstream() |
| `engine\orchestrator\orchestrator.py:126` | Function | Function: get_job_status() |
| `engine\queue\escalation.py:85` | Function | Function: create_escalation_job() |
| `engine\queue\escalation.py:172` | Function | Function: get_escalation_chain() |
| `engine\queue\escalation.py:204` | Function | Function: get_rule() |
| `engine\queue\job_queue.py:242` | Function | Function: _update_status_in_db() |
| `engine\queue\job_queue.py:260` | Function | Function: get_stats() |
| `engine\queue\queue_manager.py:146` | Function | Function: get_job_status() |
| `engine\queue\queue_manager.py:187` | Function | Function: get_queue_stats() |
| `engine\queue\retry_policy.py:66` | Function | Function: get_delay() |
| `engine\queue\worker_pool.py:157` | Function | Function: get_status() |
| `engine\state_store\job_state_store.py:44` | Function | Function: create_run() |
| `engine\state_store\job_state_store.py:68` | Function | Function: get_run() |
| `engine\state_store\job_state_store.py:80` | Function | Function: update_run_status() |
| `engine\state_store\job_state_store.py:123` | Function | Function: update_job_result() |
| `engine\state_store\job_state_store.py:261` | Function | Function: get_job() |
| `engine\state_store\job_state_store.py:373` | Function | Function: get_workstream() |
| `engine\state_store\job_state_store.py:419` | Function | Function: get_job_status() |
| `error\engine\agent_adapters.py:286` | Function | Function: get_agent_adapter() |
| `error\engine\error_context.py:54` | Function | Function: update_error_reports() |
| `error\engine\plugin_manager.py:48` | Function | Function: get_plugins_for_file() |
| `error\shared\utils\security.py:219` | Function | Function: get_timeout() |
| `examples\orchestrator_integration_demo.py:49` | Function | Function: _get_headless_flags() |
| `examples\orchestrator_integration_demo.py:69` | Function | Function: _get_interactive_flags() |
| `pm\epic.py:570` | Function | Function: create_epic_from_prd() |
| `pm\epic.py:37` | Function | Function: create_epic_from_prd() |
| `pm\epic.py:230` | Function | Function: update_task_status() |
| `pm\event_handler.py:355` | Function | Function: get_event_handler() |
| `pm\event_handler.py:247` | Function | Function: _update_task_status() |
| `pm\models.py:255` | Function | Function: get_task() |
| `pm\prd.py:332` | Function | Function: create_prd() |
| `pm\prd.py:37` | Function | Function: create_prd() |
| `pm\prd.py:157` | Function | Function: update_prd() |
| `pm\prd.py:185` | Function | Function: delete_prd() |
| `scripts\migrate_spec_folders.py:60` | Function | Function: get_repo_root() |
| `scripts\migrate_spec_folders.py:66` | Function | Function: create_directory_structure() |
| `scripts\migrate_spec_folders.py:134` | Function | Function: update_imports() |
| `scripts\migrate_spec_folders.py:173` | Function | Function: create_readme() |
| `scripts\migrate_spec_folders.py:254` | Function | Function: create_tool_inits() |
| `scripts\migrate_spec_folders.py:274` | Function | Function: create_gitignore() |
| `scripts\migrate_spec_folders.py:293` | Function | Function: create_backup() |
| `scripts\normalize_paths.py:80` | Function | Function: iter_target_files() |
| `scripts\test_state_store.py:42` | Function | Function: test_run_crud() |
| `scripts\update_markdown_paths.py:5` | Function | Function: get_repo_root() |
| `scripts\update_markdown_paths.py:57` | Function | Function: update_markdown_paths() |
| `tests\error\unit\test_agent_adapters.py:32` | Function | Function: test_create_invocation() |
| `tests\error\unit\test_agent_adapters.py:59` | Function | Function: test_create_result() |
| `tests\error\unit\test_agent_adapters.py:276` | Function | Function: test_get_aider_adapter() |
| `tests\error\unit\test_agent_adapters.py:283` | Function | Function: test_get_codex_adapter() |
| `tests\error\unit\test_agent_adapters.py:290` | Function | Function: test_get_claude_adapter() |
| `tests\error\unit\test_agent_adapters.py:297` | Function | Function: test_get_adapter_case_insensitive() |
| `tests\error\unit\test_agent_adapters.py:305` | Function | Function: test_get_adapter_with_config() |
| `tests\error\unit\test_agent_adapters.py:312` | Function | Function: test_get_unknown_adapter_raises() |
| `tests\integration\test_aim_end_to_end.py:145` | Function | Function: test_get_registry_path_raises_clear_error() |
| `tests\integration\test_aim_end_to_end.py:155` | Function | Function: test_get_tool_version_returns_none_when_registry_unavailable() |
| `tests\pipeline\test_workstream_authoring.py:45` | Function | Function: create_bundle_file() |
| `tests\plugins\conftest.py:47` | Function | Function: create_sample_file() |
| `tests\plugins\test_cross_cutting.py:287` | Function | Function: test_parse_gitleaks_json_filters_to_target_file() |
| `tests\test_adapters.py:70` | Function | Function: test_adapter_get_default_timeout() |
| `tests\test_adapters.py:74` | Function | Function: test_adapter_get_model_name() |
| `tests\test_audit_logger.py:229` | Function | Function: test_get_patch() |
| `tests\test_audit_logger.py:251` | Function | Function: test_get_patch_not_found() |
| `tests\test_audit_logger.py:257` | Function | Function: test_get_history() |
| `tests\test_audit_logger.py:280` | Function | Function: test_get_history_empty() |
| `tests\test_cost_tracking.py:37` | Function | Function: test_get_total_cost() |
| `tests\test_escalation.py:117` | Function | Function: test_create_escalation_job_no_rule() |
| `tests\test_escalation.py:130` | Function | Function: test_create_escalation_job_no_target() |
| `tests\test_escalation.py:143` | Function | Function: test_create_escalation_job_aider_to_codex() |
| `tests\test_escalation.py:212` | Function | Function: test_get_escalation_chain_single() |
| `tests\test_escalation.py:221` | Function | Function: test_get_escalation_chain_multi() |
| `tests\test_escalation.py:231` | Function | Function: test_get_escalation_chain_circular() |
| `tests\test_escalation.py:260` | Function | Function: test_get_rule() |
| `tests\test_invoke_config.py:29` | Function | Function: test_get_tool_config_aider() |
| `tests\test_invoke_config.py:39` | Function | Function: test_get_tool_config_pytest() |
| `tests\test_invoke_config.py:48` | Function | Function: test_get_orchestrator_config() |
| `tests\test_invoke_config.py:57` | Function | Function: test_get_paths_config() |
| `tests\test_invoke_config.py:66` | Function | Function: test_get_circuit_breaker_config() |
| `tests\test_invoke_config.py:74` | Function | Function: test_get_error_engine_config() |
| `tests\test_invoke_utils.py:119` | Function | Function: test_create_test_context() |
| `tests\test_parallel_dependencies.py:6` | Function | Function: test_dependency_ordering_within_target_set() |
| `tests\test_patch_manager.py:264` | Function | Function: test_get_patch_stats() |
| `tests\test_task_queue.py:150` | Function | Function: test_get_status_not_found() |
| `tests\test_ui_settings.py:58` | Function | Function: test_get_interactive_tool() |
| `tests\test_ui_settings.py:110` | Function | Function: test_get_tool_mode() |
| `tests\test_ui_settings.py:121` | Function | Function: test_get_tool_config() |
| `tests\test_ui_settings.py:129` | Function | Function: test_get_startup_config() |
| `tests\test_ui_settings.py:146` | Function | Function: test_get_auto_launch_headless_tools() |
| `tests\test_ui_settings.py:155` | Function | Function: test_get_interactive_layout() |
| `tests\test_ui_settings.py:173` | Function | Function: test_get_settings_summary() |
| `tests\test_ui_settings.py:196` | Function | Function: test_singleton_get_settings_manager() |
| `tests\test_validators.py:103` | Function | Function: test_validate_patch_scope_create_file() |
| `tests\test_worker_lifecycle.py:66` | Function | Function: test_get_idle_worker() |

---

### 37. Bundle Loading

| Location | Type | Description |
|----------|------|-------------|
| `core\state\bundles.py:160` | Function | Function: load_bundle_file() |
| `core\state\bundles.py:180` | Function | Function: validate_bundle_data() |
| `core\state\bundles.py:295` | Function | Function: load_and_validate_bundles() |
| `tests\orchestrator\test_parallel_src.py:19` | Function | Function: fake_load_and_validate_bundles() |
| `tests\pipeline\test_openspec_parser_src.py:49` | Function | Function: test_load_bundle_from_yaml_items_tags_when_then() |
| `tests\pipeline\test_openspec_parser_src.py:77` | Function | Function: test_load_bundle_from_change() |

---

### 38. Sidecar Metadata

| Location | Type | Description |
|----------|------|-------------|
| `.migration_backup_20251120_144334\spec\tools\spec_indexer\indexer.py:90` | Function | Function: ensure_sidecar() |
| `.migration_backup_20251120_144334\spec\tools\spec_patcher\patcher.py:51` | Function | Function: load_sidecar() |
| `.migration_backup_20251120_144334\spec\tools\spec_patcher\patcher.py:56` | Function | Function: save_sidecar() |
| `.migration_backup_20251120_144334\spec\tools\spec_resolver\resolver.py:28` | Function | Function: load_sidecar() |
| `specifications\tools\indexer\indexer.py:90` | Function | Function: ensure_sidecar() |
| `specifications\tools\patcher\patcher.py:51` | Function | Function: load_sidecar() |
| `specifications\tools\patcher\patcher.py:56` | Function | Function: save_sidecar() |
| `specifications\tools\resolver\resolver.py:28` | Function | Function: load_sidecar() |

---

## Integrations

### 39. AIM Bridge

*No implementation locations found for this term.*

---

### 40. CCPM Integration

| Location | Type | Description |
|----------|------|-------------|
| `core\planning\ccpm_integration.py:172` | Class | Class definition: CCPMIntegration |
| `tests\test_ccpm_openspec_integration.py:10` | Class | Class definition: TestCCPMComponents |

---

### 41. Aider Adapter

| Location | Type | Description |
|----------|------|-------------|
| `AGENTIC_DEV_PROTOTYPE\src\adapters\aider_adapter.py:18` | Class | Class definition: AiderConfig |
| `AGENTIC_DEV_PROTOTYPE\src\adapters\aider_adapter.py:29` | Class | Class definition: AiderAdapter |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\adapters\aider_adapter.py:18` | Class | Class definition: AiderConfig |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\adapters\aider_adapter.py:29` | Class | Class definition: AiderAdapter |
| `core\engine\adapters\aider_adapter.py:6` | Class | Class definition: AiderAdapter |
| `engine\adapters\aider_adapter.py:22` | Class | Class definition: AiderAdapter |
| `error\engine\agent_adapters.py:83` | Class | Class definition: AiderAdapter |
| `tests\error\unit\test_agent_adapters.py:126` | Class | Class definition: TestAiderAdapter |
| `AGENTIC_DEV_PROTOTYPE\src\adapters\aider_adapter.py:36` | Function | Function: _find_aider() |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\adapters\aider_adapter.py:36` | Function | Function: _find_aider() |
| `aider\engine.py:159` | Function | Function: prepare_aider_prompt_file() |
| `aider\engine.py:168` | Function | Function: run_aider_edit() |
| `aider\engine.py:210` | Function | Function: run_aider_fix() |
| `engine\adapters\aider_adapter.py:155` | Function | Function: run_aider_job() |
| `engine\queue\escalation.py:144` | Function | Function: _convert_aider_to_codex() |
| `tests\error\unit\test_agent_adapters.py:129` | Function | Function: test_aider_adapter_creation() |
| `tests\error\unit\test_agent_adapters.py:136` | Function | Function: test_aider_with_config() |
| `tests\error\unit\test_agent_adapters.py:276` | Function | Function: test_get_aider_adapter() |
| `tests\integration\test_aider_sandbox.py:18` | Function | Function: _have_aider() |
| `tests\integration\test_aider_sandbox.py:29` | Function | Function: test_aider_edit_invocation_and_prompt_file() |
| `tests\test_adapters.py:11` | Function | Function: aider_config() |
| `tests\test_adapters.py:20` | Function | Function: test_aider_adapter_init() |
| `tests\test_adapters.py:25` | Function | Function: test_aider_build_prompt_command() |
| `tests\test_adapters.py:34` | Function | Function: test_aider_build_command_with_prompt_file() |
| `tests\test_adapters.py:85` | Function | Function: test_aider_patch_apply_mode() |
| `tests\test_escalation.py:22` | Function | Function: test_aider_escalation_rule() |
| `tests\test_escalation.py:143` | Function | Function: test_create_escalation_job_aider_to_codex() |
| `tests\test_escalation.py:170` | Function | Function: test_aider_to_codex_conversion() |
| `tests\test_invoke_config.py:29` | Function | Function: test_get_tool_config_aider() |
| `tests\test_prompt_engine.py:250` | Function | Function: test_select_template_aider() |

---

### 42. Git Adapter

| Location | Type | Description |
|----------|------|-------------|
| `engine\adapters\git_adapter.py:28` | Class | Class definition: GitAdapter |
| `scripts\test_adapters.py:179` | Function | Function: test_git_adapter_execution() |

---

### 43. Test Adapter

| Location | Type | Description |
|----------|------|-------------|
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\adapters\test_registry.py:17` | Class | Class definition: TestAdapterRegistry |
| `scripts\test_adapters.py:15` | Function | Function: test_adapter_imports() |
| `scripts\test_adapters.py:40` | Function | Function: test_adapter_interface() |
| `scripts\validate_engine.py:102` | Function | Function: test_adapter_interface() |
| `tests\test_adapters.py:70` | Function | Function: test_adapter_get_default_timeout() |
| `tests\test_adapters.py:74` | Function | Function: test_adapter_get_model_name() |
| `tests\test_adapters.py:99` | Function | Function: test_adapter_name_inference() |

---

### 44. Tool Registry

| Location | Type | Description |
|----------|------|-------------|
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\adapters\registry.py:13` | Class | Class definition: AdapterRegistry |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\adapters\test_registry.py:17` | Class | Class definition: TestAdapterRegistry |
| `aim\exceptions.py:15` | Class | Class definition: AIMRegistryNotFoundError |
| `aim\exceptions.py:24` | Class | Class definition: AIMRegistryLoadError |
| `tests\pipeline\test_aim_bridge.py:32` | Class | Class definition: TestGetAimRegistryPath |
| `tests\pipeline\test_aim_bridge.py:57` | Class | Class definition: TestLoadAimRegistry |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\tests\adapters\test_registry.py:20` | Function | Function: test_create_empty_registry() |
| `aim\bridge.py:31` | Function | Function: get_aim_registry_path() |
| `aim\bridge.py:73` | Function | Function: load_aim_registry() |
| `aim\registry\config_loader.py:154` | Function | Function: get_registry() |
| `aim\tests\registry\test_config_loader.py:168` | Function | Function: test_get_registry() |
| `tests\integration\test_aim_end_to_end.py:32` | Function | Function: test_aim_registry_loads() |
| `tests\integration\test_aim_end_to_end.py:145` | Function | Function: test_get_registry_path_raises_clear_error() |
| `tests\integration\test_aim_end_to_end.py:150` | Function | Function: test_detect_tool_returns_false_when_registry_unavailable() |
| `tests\integration\test_aim_end_to_end.py:155` | Function | Function: test_get_tool_version_returns_none_when_registry_unavailable() |
| `tests\integration\test_aim_orchestrator_integration.py:20` | Function | Function: test_is_aim_available_when_registry_exists() |
| `tests\pipeline\test_aim_bridge.py:61` | Function | Function: test_loads_valid_registry() |
| `tests\pipeline\test_aim_bridge.py:77` | Function | Function: test_raises_on_missing_registry_file() |
| `tests\pipeline\test_aim_bridge.py:402` | Function | Function: test_handles_missing_registry_gracefully() |
| `tests\test_path_registry.py:14` | Function | Function: write_registry() |
| `tests\test_path_registry.py:20` | Function | Function: monkeypatch_registry() |
| `tests\test_path_registry.py:114` | Function | Function: test_missing_registry_file() |

---

### 45. Profile Matching

*No implementation locations found for this term.*

---

### 46. Compensation Action

*No implementation locations found for this term.*

---

### 47. Rollback Strategy

| Location | Type | Description |
|----------|------|-------------|
| `AGENTIC_DEV_PROTOTYPE\src\patch_manager.py:269` | Function | Function: rollback() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_patch_manager.py:180` | Function | Function: test_rollback_latest() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_patch_manager.py:198` | Function | Function: test_rollback_specific_backup() |
| `AGENTIC_DEV_PROTOTYPE\tests\test_patch_manager.py:211` | Function | Function: test_rollback_nonexistent_backup() |
| `PROCESS_DEEP_DIVE_OPTOMIZE\raw_data\sessions\session_3_m5_m6_completion\src_snapshot\patch_manager.py:269` | Function | Function: rollback() |
| `core\engine\compensation.py:10` | Function | Function: rollback_workstream() |
| `core\engine\compensation.py:16` | Function | Function: rollback_phase() |

---

## 📊 Statistics

**Total Terms**: 47  
**Total Locations Found**: 1012  
**Terms with Locations**: 41  

**Coverage by Category**:
- **Core Engine**: 12 terms, 275 locations
- **Error Detection**: 10 terms, 222 locations
- **Specifications**: 8 terms, 34 locations
- **State Management**: 8 terms, 411 locations
- **Integrations**: 9 terms, 70 locations

---

## 🔄 Maintenance

**Auto-Generated**: This file is automatically generated. Do not edit manually.

**Update Commands**:
```bash
# Regenerate implementation map
python scripts/generate_implementation_map.py
```

**Update Schedule**:
- **Weekly**: Automatically regenerated
- **On PR**: Regenerated if Python files changed

---

**Last Generated**: 2025-11-22 12:52:51 UTC  
**Generator**: `scripts/generate_implementation_map.py`
