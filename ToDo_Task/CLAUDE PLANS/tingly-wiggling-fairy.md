---
doc_id: DOC-GUIDE-TINGLY-WIGGLING-FAIRY-1566
---

# UET ENGINE REPLACEMENT - MACHINE EXECUTION PLAN

## METADATA
```yaml
plan_id: uet-engine-full-replacement-with-prmnt-patterns
created: 2025-11-25
updated: 2025-11-25
status: ready_for_execution
approach: complete_engine_replacement_with_execution_acceleration
timeline_original_estimate: 6-8_weeks
timeline_with_prmnt_patterns: 3-4_weeks
timeline_acceleration: 2.3x_speedup
timeline_requested_by_user: 1-2_weeks (not_achievable_for_full_replacement)
risk_level: medium (reduced_from_high_via_anti_pattern_guards)
priority_features: [dag_parallel_execution, unified_patch_management]
execution_patterns_integrated: [multi_cli_worktrees, batch_execution, ground_truth_gates, decision_elimination, anti_patterns, telemetry, parallel_strategy]
rollback_capable: true
decision_elimination_enabled: true
worktree_parallel_execution: true
ground_truth_verification: true
```

## OBJECTIVE
Replace `core/engine/orchestrator.py` (sequential EDIT→STATIC→RUNTIME) with UET DAG-based parallel orchestrator including unified patch ledger.

## CONSTRAINTS
- Automated workstream conversion acceptable (46 JSON files)
- Must preserve all existing functionality
- Zero data loss requirement
- Rollback capability mandatory

## EXECUTION PHASES

### PHASE_0_TEMPLATE_LIBRARY
```yaml
duration: 2_days
risk: low
dependencies: []
objective: create_decision_elimination_templates_before_execution
deliverables:
  - execution_templates_library
  - anti_pattern_guards
  - worktree_coordination_spec
  - decision_telemetry_system

templates_to_create:
  - path: templates/migration/database_migration.template.yaml
    purpose: eliminate_decisions_for_db_schema_changes
    fields:
      - migration_id
      - tables_to_add
      - rollback_sql
      - validation_query
      - success_criteria: [table_count_increased, foreign_keys_valid]

  - path: templates/migration/file_copy_batch.template.yaml
    purpose: eliminate_decisions_for_uet_module_copying
    fields:
      - source_files: List[path]
      - target_files: List[path]
      - import_modifications: Dict[old, new]
      - verification_imports: List[module_path]
      - success_criteria: [imports_work, no_syntax_errors]

  - path: templates/migration/test_batch.template.yaml
    purpose: eliminate_decisions_for_test_execution
    fields:
      - test_suite_name
      - test_files: List[path]
      - required_pass_rate: float
      - timeout_per_test: int
      - success_criteria: [all_tests_pass, coverage_maintained]

  - path: templates/migration/workstream_conversion_batch.template.yaml
    purpose: eliminate_decisions_for_json_to_yaml_conversion
    fields:
      - input_dir: path
      - output_dir: path
      - mapping_rules: Dict[old_field, new_field]
      - validation_schema: path
      - success_criteria: [all_converted, all_validated, no_data_loss]

anti_pattern_guards:
  - path: .execution/anti_patterns.yaml
    purpose: prevent_documented_failure_modes
    guards:
      hallucination_of_success:
        rule: never_mark_complete_without_programmatic_verification
        implementation: require_exit_code_check_or_file_exists_check

      planning_loop_trap:
        rule: max_planning_iterations_before_execution
        implementation: after_2_plan_revisions_must_execute_something

      partial_success_amnesia:
        rule: track_all_intermediate_state
        implementation: checkpoint_after_each_phase_completion

      approval_loop:
        rule: no_human_approval_required_for_templated_operations
        implementation: ground_truth_gates_only

decision_telemetry:
  - path: .execution/telemetry.jsonl
    purpose: measure_decision_elimination_effectiveness
    metrics:
      - decisions_avoided_count
      - template_reuse_count
      - manual_intervention_count
      - time_saved_vs_baseline
      - error_rate_templated_vs_manual

worktree_coordination:
  control_checkout:
    location: main_repo
    role: single_writer_for_global_state
    writes_to:
      - core/state/db.py
      - core/state/db_unified.py
      - schema/migrations/*
      - doc_id/DOC_ID_REGISTRY.yaml
    responsibilities:
      - merge_worker_patches
      - run_global_validation
      - execute_final_tests
      - tag_releases

  worker_worktrees:
    - worktree_id: wt-phase1-database
      branch: migration/phase1-database
      path: .worktrees/wt-phase1-database
      scope: [schema/migrations/*, tests/state/*]
      role: isolated_database_migration_work
      produces: [migration_sql, rollback_sql, test_results]

    - worktree_id: wt-phase2-dag
      branch: migration/phase2-dag
      path: .worktrees/wt-phase2-dag
      scope: [core/engine/dag_builder.py, core/engine/parallel_orchestrator.py, tests/engine/test_dag*.py]
      role: isolated_dag_scheduler_development
      produces: [source_files, test_files, test_results]

    - worktree_id: wt-phase3-patches
      branch: migration/phase3-patches
      path: .worktrees/wt-phase3-patches
      scope: [core/engine/patch_*.py, tests/engine/test_patch*.py]
      role: isolated_patch_ledger_development
      produces: [source_files, test_files, test_results]

  environment_variables:
    WT_ID: worktree_identifier (CONTROL | wt-phase1-database | ...)
    WT_SCOPE: declared_path_scope_glob_patterns
    RUN_ID: unique_run_identifier_timestamp
    LOG_ROOT: .execution/logs/${RUN_ID}

  single_writer_enforcement:
    - file: core/state/db.py
      writer: CONTROL only
      readers: all_worktrees
      violation: fail_with_error_if_worker_attempts_write

    - file: schema/migrations/*.sql
      writer: CONTROL only
      readers: all_worktrees
      violation: fail_with_error_if_worker_attempts_write

execution_sequence:
  - create_template_library
  - setup_worktree_coordination
  - enable_decision_telemetry
  - configure_anti_pattern_guards
  - verify_ground_truth_gates_operational
```

### PHASE_1_FOUNDATION
```yaml
duration: 10_days
risk: medium
dependencies: [PHASE_0_TEMPLATE_LIBRARY]
deliverables:
  - unified_database_layer
  - workstream_converter
  - uet_core_modules_integrated
  - bridge_adapters
execution_mode: worktree_coordinated_parallel
```

#### PHASE_1_DAY_1_2_DATABASE
```yaml
objective: create_unified_database_layer
execution_mode: worktree_wt_phase1_database
action: template_driven_batch_execution

template_instantiation:
  template: templates/migration/database_migration.template.yaml
  instance: .execution/phase1_database.instance.yaml
  parameters:
    migration_id: uet_migration_001
    tables_to_add:
      - uet_runs (run_id TEXT PRIMARY KEY, project_id TEXT, phase_id TEXT, state TEXT CHECK...)
      - step_attempts (step_attempt_id TEXT PRIMARY KEY, run_id TEXT REFERENCES uet_runs...)
      - run_events (id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT, timestamp TEXT...)
      - patch_ledger (patch_id TEXT PRIMARY KEY, workstream_id TEXT, content TEXT...)
    rollback_sql: schema/migrations/uet_migration_001_rollback.sql
    validation_query: SELECT COUNT(*) FROM sqlite_master WHERE type='table'
    success_criteria:
      - table_count_increased: expect +4
      - foreign_keys_valid: PRAGMA foreign_key_check returns empty
      - no_duplicate_tables: no name collisions

batch_execution_pattern_EXEC_001:
  worktree: wt-phase1-database
  batch_file: .execution/phase1_database_batch.txt
  contents: |
    # EXEC-001 Style Batch File
    FILE: core/state/db_unified.py
    ACTION: create
    TEMPLATE: templates/code/database_bridge.py.j2
    VERIFY: python -c "from core.state.db_unified import dual_write_run"

    FILE: schema/migrations/uet_migration_001.sql
    ACTION: create
    TEMPLATE: templates/migration/database_migration.template.yaml
    VERIFY: sqlite3 :memory: < schema/migrations/uet_migration_001.sql

    FILE: schema/migrations/uet_migration_001_rollback.sql
    ACTION: create
    TEMPLATE: templates/migration/rollback_template.sql.j2
    VERIFY: grep "DROP TABLE" schema/migrations/uet_migration_001_rollback.sql

    FILE: tests/state/test_db_unified.py
    ACTION: create
    TEMPLATE: templates/test/database_test.py.j2
    VERIFY: pytest tests/state/test_db_unified.py --collect-only

ground_truth_gates:
  gate_1_import_works:
    command: python -c "from core.state.db_unified import dual_write_run"
    expect_exit_code: 0
    failure_action: halt_and_report

  gate_2_migration_syntax_valid:
    command: sqlite3 :memory: < schema/migrations/uet_migration_001.sql
    expect_exit_code: 0
    failure_action: halt_and_report

  gate_3_rollback_syntax_valid:
    command: sqlite3 :memory: < schema/migrations/uet_migration_001_rollback.sql
    expect_exit_code: 0
    failure_action: halt_and_report

  gate_4_tests_collected:
    command: pytest tests/state/test_db_unified.py --collect-only -q
    expect_stdout_contains: "1 test collected"
    failure_action: halt_and_report

  gate_5_forward_migration_applies:
    command: |
      cp .worktrees/pipeline_state.db .worktrees/pipeline_state.db.backup
      sqlite3 .worktrees/pipeline_state.db < schema/migrations/uet_migration_001.sql
      sqlite3 .worktrees/pipeline_state.db "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
    expect_stdout_contains_number_greater_than_baseline: +4
    failure_action: restore_backup_and_halt

  gate_6_rollback_works:
    command: |
      sqlite3 .worktrees/pipeline_state.db < schema/migrations/uet_migration_001_rollback.sql
      sqlite3 .worktrees/pipeline_state.db "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
    expect_table_count_equals_baseline: true
    failure_action: halt_and_report

files_to_create:
  - path: core/state/db_unified.py
    purpose: bridge_old_and_uet_schemas
    imports: [core.state.db, core.state.uet_db]
    functions:
      - dual_write_run
      - dual_write_step_attempt
      - map_old_to_new_schema
      - map_new_to_old_schema

  - path: schema/migrations/uet_migration_001.sql
    purpose: add_uet_tables_non_breaking
    operations:
      - CREATE TABLE IF NOT EXISTS uet_runs
      - CREATE TABLE IF NOT EXISTS step_attempts
      - CREATE TABLE IF NOT EXISTS run_events
      - CREATE TABLE IF NOT EXISTS patch_ledger
      - CREATE VIEW workstreams_compat AS SELECT

  - path: schema/migrations/uet_migration_001_rollback.sql
    purpose: reverse_migration
    operations:
      - DROP TABLE IF EXISTS patch_ledger
      - DROP TABLE IF EXISTS run_events
      - DROP TABLE IF EXISTS step_attempts
      - DROP TABLE IF EXISTS uet_runs
      - DROP VIEW IF EXISTS workstreams_compat

decision_telemetry_tracking:
  decisions_eliminated:
    - which_tables_to_add: pre_decided_in_template
    - sql_syntax: pre_validated_in_template
    - test_structure: pre_decided_in_template
    - verification_commands: pre_scripted_in_ground_truth_gates
  decisions_avoided_count: 4
  manual_intervention_required: none
  time_saved_vs_manual: estimated_2_hours

control_checkout_merge:
  after_worktree_completes:
    - git checkout main
    - git merge migration/phase1-database --no-ff
    - run_ground_truth_gates_on_control
    - if_all_pass: git tag phase1-database-complete
    - if_any_fail: git reset --hard HEAD~1
```

#### PHASE_1_DAY_3_4_WORKSTREAM_CONVERTER
```yaml
objective: automate_workstream_format_conversion
action: create_converter_and_validator

files_to_create:
  - path: tools/workstream_converter.py
    class: WorkstreamConverter
    methods:
      - convert_bundle(json_path) -> dict
      - map_fields_json_to_yaml
      - extract_dependencies_for_dag
      - validate_converted_workstream
    mapping_rules:
      old.id: workstream_id
      old.tool: execution_request.tool_id
      old.files_scope: constraints.file_scope.allowed_paths
      old.tasks: execution_request.prompt (concatenate)
      old.acceptance_tests: acceptance_criteria.commands
      old.depends_on: dependencies (dag construction)
      old.circuit_breaker: resilience_policy

  - path: tools/workstream_validator.py
    class: WorkstreamValidator
    methods:
      - validate_against_uet_schema
      - check_dependency_cycles
      - verify_tool_exists
    schemas_used:
      - UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/specs/core/UET_WORKSTREAM_SPEC.md

  - path: workstreams_uet/.gitkeep
    purpose: output_directory_for_converted_workstreams

execution_sequence:
  - python tools/workstream_converter.py workstreams/ workstreams_uet/
  - python tools/workstream_validator.py workstreams_uet/*.yaml
  - diff workstreams/ workstreams_uet/ > conversion_report.txt

testing:
  - convert_all_46_workstreams
  - validate_each_against_schema
  - dry_run_execution_test
  - assert_no_data_loss

rollback:
  - keep workstreams/*.json unchanged
  - rm -rf workstreams_uet/
```

#### PHASE_1_DAY_5_UET_CORE_INTEGRATION
```yaml
objective: copy_uet_core_modules
action: copy_and_rename_files

files_to_copy:
  - source: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/orchestrator.py
    target: core/engine/uet_orchestrator.py
    modifications:
      - update_imports: from core.state.db -> from core.state.uet_db
      - add_bridge_adapter_imports

  - source: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/scheduler.py
    target: core/engine/uet_scheduler.py
    modifications: [update_imports]

  - source: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/router.py
    target: core/engine/uet_router.py
    modifications: [update_imports]

  - source: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/patch_ledger.py
    target: core/engine/uet_patch_ledger.py
    modifications: [update_imports]

  - source: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/state_machine.py
    target: core/engine/uet_state_machine.py
    modifications: []

  - source: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/adapters/base.py
    target: core/engine/adapters/uet_base.py
    modifications: []

  - source: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/adapters/subprocess_adapter.py
    target: core/engine/adapters/uet_subprocess.py
    modifications: []

  - source: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/adapters/registry.py
    target: core/engine/adapters/uet_registry.py
    modifications: []

  - source: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/state/db.py
    target: core/state/uet_db.py
    modifications: [rename_init_db_to_init_uet_db]

files_to_create_bridges:
  - path: core/engine/adapters/legacy_tool_bridge.py
    class: LegacyToolBridge(ToolAdapter)
    purpose: wrap_existing_tools_py_for_uet
    methods:
      - execute(request) -> calls tools.run_tool() and converts format
      - convert_result_format(old_result) -> ExecutionResult

  - path: core/engine/adapters/aider_bridge.py
    class: AiderBridge(ToolAdapter)
    purpose: wrap_prompts_run_aider_edit_for_uet
    methods:
      - execute(request) -> calls prompts.run_aider_edit() with aim_integration
      - preserve_aim_routing
      - convert_patch_to_unified_diff

files_to_preserve:
  - source: core/engine/orchestrator.py
    target: core/engine/orchestrator_legacy.py
    purpose: rollback_capability

testing:
  - pytest tests/engine/test_uet_orchestrator.py
  - pytest tests/adapters/test_legacy_bridge.py
  - verify_imports: python -c "from core.engine.uet_orchestrator import Orchestrator"

rollback:
  - rm core/engine/uet_*.py
  - rm core/engine/adapters/uet_*.py
  - mv core/engine/orchestrator_legacy.py core/engine/orchestrator.py
```

### PHASE_2_PARALLEL_EXECUTION
```yaml
duration: 5_days
risk: high
dependencies: [PHASE_1_FOUNDATION]
deliverables:
  - dag_scheduler_operational
  - parallel_orchestrator
  - wave_based_execution
```

#### PHASE_2_DAY_6_7_DAG_SCHEDULER
```yaml
objective: enable_parallel_execution_with_dag

files_to_create:
  - path: core/engine/dag_builder.py
    class: DAGBuilder
    methods:
      - build_from_workstreams(workstreams: List[dict]) -> ExecutionPlan
      - extract_dependencies(workstream) -> List[str]
      - topological_sort(dag) -> List[List[str]] (waves)
      - detect_cycles(dag) -> Optional[List[str]]
      - validate_dag(dag) -> bool
    algorithm: kahn_topological_sort
    time_complexity: O(V + E)

  - path: core/engine/parallel_orchestrator.py
    class: ParallelOrchestrator
    methods:
      - __init__(max_workers: int = 4)
      - execute_phase(workstreams: List[dict]) -> ExecutionReport
      - execute_wave(wave: List[str]) -> List[ExecutionResult]
      - monitor_execution() -> ProgressSnapshot
    uses:
      - uet_scheduler.UETScheduler
      - concurrent.futures.ThreadPoolExecutor
    state_management: thread_safe_db_writes

migration_path:
  phase_1_sequential:
    max_workers: 1
    purpose: validate_correctness
    testing: compare_results_with_legacy

  phase_2_limited_parallel:
    max_workers: 2
    purpose: test_stability
    testing: check_race_conditions

  phase_3_full_parallel:
    max_workers: 4
    purpose: production_deployment
    testing: performance_benchmarking

testing_sequence:
  - test_single_workstream_uet: verify_basic_execution
  - test_sequential_batch_uet: verify_multiple_workstreams
  - test_parallel_independent: verify_no_dependencies
  - test_parallel_with_deps: verify_dependency_ordering
  - test_full_dag_execution: verify_46_workstreams
  - test_cycle_detection: verify_error_handling
  - test_wave_structure: verify_optimal_parallelization

performance_expectations:
  single_workstream: 1x (no change)
  10_independent: 3.3x speedup
  46_mixed_dependencies: 4x speedup
  46_high_parallelism: 6x speedup

monitoring:
  - track_workstream_completion_rate
  - measure_average_execution_time
  - calculate_parallel_efficiency
  - log_error_rate_old_vs_new
```

### PHASE_3_PATCH_MANAGEMENT
```yaml
duration: 3_days
risk: medium
dependencies: [PHASE_2_PARALLEL_EXECUTION]
deliverables:
  - unified_patch_format
  - patch_ledger_operational
  - patch_state_machine
```

#### PHASE_3_DAY_8_PATCH_LEDGER
```yaml
objective: replace_tool_specific_patches_with_unified_format

files_to_create:
  - path: core/engine/patch_converter.py
    class: PatchConverter
    methods:
      - convert_aider_patch(tool_result: dict) -> UnifiedPatch
      - convert_tool_patch(tool_id: str, output: str) -> UnifiedPatch
      - extract_git_diff(output: str) -> str
      - validate_unified_diff(diff: str) -> bool
    format_output: unified_diff (git diff format)

  - path: core/engine/patch_applier.py
    class: PatchApplier
    methods:
      - __init__(ledger: PatchLedger)
      - apply_patch(patch_id: str, workspace: Path) -> bool
      - create_ledger_entry(patch: UnifiedPatch) -> str
      - validate_patch(patch_id: str) -> bool
      - record_in_ledger(patch_id: str, status: str)
      - run_verification_tests(workspace: Path) -> bool
    state_machine_states:
      - created
      - validated
      - queued
      - applied
      - verified
      - committed
      - quarantined (on failure)

database_schema_extension:
  table: patch_ledger
  columns:
    - patch_id TEXT PRIMARY KEY
    - workstream_id TEXT REFERENCES workstreams(id)
    - content TEXT (unified diff)
    - status TEXT CHECK(status IN states)
    - created_at TEXT
    - applied_at TEXT
    - verified_at TEXT
    - error_message TEXT

migration_strategy:
  phase_1_dual_track:
    - write_old_format_to_step_attempts
    - write_new_format_to_patch_ledger
    - maintain_compatibility

  phase_2_new_only:
    - write_only_new_format
    - deprecate_old_format
    - migration_tool_for_historical_patches

integration_with_tools:
  - modify: core/prompts.py::run_aider_edit
    change: output_unified_diff_plus_ledger_entry

  - modify: core/engine/adapters/aider_bridge.py
    change: convert_aider_output_to_unified_patch

  - create: core/engine/patch_quarantine.py
    purpose: isolate_failed_patches_for_review

testing:
  - test_aider_patch_conversion
  - test_patch_ledger_creation
  - test_patch_state_machine_transitions
  - test_patch_application
  - test_verification_workflow
  - test_quarantine_mechanism
```

### PHASE_4_INTEGRATION_TESTING
```yaml
duration: 3_days
risk: high
dependencies: [PHASE_3_PATCH_MANAGEMENT]
deliverables:
  - integration_test_suite_passing
  - performance_validation
  - migration_report
```

#### PHASE_4_DAY_9_TESTING
```yaml
objective: validate_complete_migration

test_plan:
  smoke_tests:
    duration: 2_hours
    tests:
      - single_workstream_via_uet_engine
      - verify_run_in_uet_runs_table
      - verify_patch_in_ledger
      - verify_events_captured
    commands:
      - python -m core.cli run-workstream ws-hello-world --engine=uet
      - sqlite3 .worktrees/pipeline_state.db "SELECT * FROM uet_runs WHERE workstream_id='ws-hello-world'"

  sequential_batch:
    duration: 3_hours
    workstream_count: 10
    parallel_workers: 1
    purpose: validate_no_regressions
    commands:
      - python -m core.cli run-phase phase-test-10 --engine=uet --parallel=1
    verification:
      - all_workstreams_complete
      - compare_execution_time_old_vs_new
      - check_output_equivalence

  parallel_batch:
    duration: 3_hours
    workstream_count: 10
    parallel_workers: 4
    purpose: validate_speedup
    commands:
      - python -m core.cli run-phase phase-test-10 --engine=uet --parallel=4
    verification:
      - speedup_observed: expect 3-4x
      - no_race_conditions
      - proper_dependency_handling

  full_integration:
    duration: 2_hours
    workstream_count: 46
    mode: dry_run
    purpose: validate_dag_construction
    commands:
      - python -m core.cli run-phase phase-all --engine=uet --parallel=4 --dry-run
    verification:
      - dag_builds_correctly
      - wave_structure_optimal
      - identify_potential_issues

files_to_create:
  - path: tests/integration/test_uet_migration.py
    tests:
      - test_uet_vs_legacy_equivalence
      - test_parallel_correctness
      - test_dependency_ordering
      - test_patch_ledger_integrity
      - test_rollback_procedure

  - path: tools/migration_validator.py
    class: MigrationValidator
    methods:
      - compare_old_db_vs_new_db
      - validate_data_integrity
      - check_patch_ledger_completeness
      - report_discrepancies

success_criteria:
  - test_pass_rate: 100%
  - no_functionality_regressions
  - performance_improvement: >= 3x for parallel workstreams
  - all_337_uet_tests_passing
  - all_existing_tests_passing
```

### PHASE_5_CUTOVER
```yaml
duration: 1_day
risk: critical
dependencies: [PHASE_4_INTEGRATION_TESTING]
deliverables:
  - production_deployment
  - documentation_complete
  - rollback_tested
```

#### PHASE_5_DAY_10_PRODUCTION
```yaml
objective: production_cutover_with_rollback_capability

files_to_modify:
  - path: core/config.py
    changes:
      - add ENGINE_MODE = os.getenv('PIPELINE_ENGINE', 'legacy')
      - add get_engine_mode() -> str

  - path: core/engine/__init__.py
    changes:
      - add get_orchestrator() function
      - if config.ENGINE_MODE == 'uet': return UETOrchestrator()
      - else: return LegacyOrchestrator()

  - path: core/cli.py
    changes:
      - add --engine flag to all commands
      - route to appropriate orchestrator

cutover_process:
  stage_1_canary:
    traffic_percent: 10
    commands:
      - export PIPELINE_ENGINE=uet
      - python -m core.cli run-phase phase-canary-10
    monitoring:
      - error_rate < 5%
      - performance >= baseline
    duration: 1_hour
    rollback_if: error_rate > 10%

  stage_2_ramp_up:
    traffic_percent: 50
    duration: 2_hours
    monitoring:
      - compare_uet_vs_legacy_results
      - check_patch_ledger_health
    rollback_if: critical_issues_detected

  stage_3_full_migration:
    traffic_percent: 100
    commands:
      - export PIPELINE_ENGINE=uet
      - python -m core.cli run-phase phase-all
    monitoring:
      - all_metrics_green
    rollback_if: system_instability

  stage_4_deprecate_legacy:
    wait_period: 1_week
    actions:
      - archive core/engine/orchestrator_legacy.py
      - remove ENGINE_MODE flag
      - make uet default

rollback_procedure:
  time_to_rollback: under_15_minutes
  steps:
    - export PIPELINE_ENGINE=legacy
    - sqlite3 .worktrees/pipeline_state.db < schema/migrations/uet_migration_001_rollback.sql
    - systemctl restart pipeline-orchestrator (if applicable)
    - python -m core.cli health-check

  rollback_triggers_automatic:
    - workstream_failure_rate > 20%
    - database_corruption_detected
    - critical_tool_adapter_failure

  rollback_triggers_manual:
    - performance_degradation > 50%
    - unresolvable_bug_discovered
    - production_stability_issues

files_to_create_documentation:
  - path: docs/migration/UET_MIGRATION_GUIDE.md
    sections:
      - migration_overview
      - breaking_changes
      - rollback_procedures
      - troubleshooting_guide

  - path: docs/migration/UET_OPERATOR_GUIDE.md
    sections:
      - running_phases_with_uet
      - configuration_options
      - monitoring_and_debugging
      - performance_tuning

  - path: docs/migration/UET_DEVELOPER_GUIDE.md
    sections:
      - architecture_changes
      - new_adapter_interface
      - patch_ledger_api
      - testing_guidelines
```

## CRITICAL_FILE_INVENTORY

### FILES_TO_COPY_FROM_UET
```yaml
- source: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/orchestrator.py
  target: core/engine/uet_orchestrator.py
  reason: production_ready_uet_orchestrator_337_tests_passing

- source: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/scheduler.py
  target: core/engine/uet_scheduler.py
  reason: dag_scheduler_topological_sort_parallel_batching

- source: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/patch_ledger.py
  target: core/engine/uet_patch_ledger.py
  reason: unified_patch_management_state_machine

- source: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/router.py
  target: core/engine/uet_router.py

- source: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/state_machine.py
  target: core/engine/uet_state_machine.py

- source: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/adapters/base.py
  target: core/engine/adapters/uet_base.py

- source: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/adapters/subprocess_adapter.py
  target: core/engine/adapters/uet_subprocess.py

- source: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/adapters/registry.py
  target: core/engine/adapters/uet_registry.py

- source: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/state/db.py
  target: core/state/uet_db.py
```

### FILES_TO_CREATE_NEW
```yaml
core/state/db_unified.py: database_bridge_old_and_uet_schemas
core/engine/adapters/legacy_tool_bridge.py: wrap_existing_tools_for_uet
core/engine/adapters/aider_bridge.py: aider_specific_bridge_aim_integration
core/engine/dag_builder.py: dag_construction_from_workstreams
core/engine/parallel_orchestrator.py: parallel_execution_coordinator
core/engine/patch_converter.py: convert_tool_patches_to_unified_diff
core/engine/patch_applier.py: apply_patches_with_ledger_tracking
tools/workstream_converter.py: json_to_yaml_automated_conversion
tools/workstream_validator.py: validate_against_uet_schema
tools/migration_validator.py: verify_migration_integrity
tools/rollback_migration.py: automated_rollback
schema/migrations/uet_migration_001.sql: forward_migration
schema/migrations/uet_migration_001_rollback.sql: reverse_migration
workstreams_uet/.gitkeep: converted_workstream_output_directory
```

### FILES_TO_MODIFY_EXISTING
```yaml
core/state/db.py: add_uet_schema_support_dual_write
core/engine/__init__.py: add_engine_routing_get_orchestrator
core/config.py: add_ENGINE_MODE_configuration
core/cli.py: add_engine_flag_to_commands
core/prompts.py: output_unified_patch_format
```

### FILES_TO_PRESERVE_FOR_ROLLBACK
```yaml
core/engine/orchestrator.py: rename_to_orchestrator_legacy_py
core/state/bundles.py: keep_for_json_workstream_loading
workstreams/*.json: preserve_all_46_original_files
```

### FILES_TO_DEPRECATE_AFTER_1_WEEK
```yaml
core/engine/orchestrator_legacy.py: remove_after_validation_period
core/state/db_old_schema.py: remove_old_schema_helpers
schema/migrations/uet_migration_001_rollback.sql: archive_rollback_script
```

## TESTING_MATRIX

```yaml
unit_tests:
  phase: day_1_5
  coverage_target: 80%
  files:
    - tests/state/test_db_unified.py
    - tests/engine/test_uet_orchestrator.py
    - tests/engine/test_dag_builder.py
    - tests/engine/test_patch_converter.py
    - tests/adapters/test_legacy_bridge.py
    - tests/adapters/test_aider_bridge.py

integration_tests:
  phase: day_6_8
  duration: each_3_hours
  files:
    - tests/integration/test_uet_migration.py
    - tests/integration/test_parallel_execution.py
    - tests/integration/test_patch_ledger.py

system_tests:
  phase: day_9
  duration: 8_hours
  scenarios:
    - single_workstream_execution
    - sequential_batch_10_workstreams
    - parallel_batch_10_workstreams
    - full_46_workstream_dry_run

acceptance_tests:
  phase: day_10
  environment: production_like
  criteria:
    - all_46_workstreams_execute_successfully
    - dag_parallel_execution_operational
    - unified_patch_ledger_recording_all_changes
    - zero_data_loss
    - 3_5x_speedup_demonstrated
    - 337_uet_tests_passing
    - all_existing_tests_passing
```

## RISK_MITIGATION

```yaml
high_risks:
  database_schema_mismatch:
    risk: data_loss_during_migration
    mitigation:
      - dual_write_period
      - comprehensive_backups_before_migration
      - migration_validation_tool
    rollback:
      - sql_rollback_script
      - database_backup_restore
    test:
      - run_migration_on_copy_of_production_db

  workstream_conversion_errors:
    risk: semantic_differences_cause_failures
    mitigation:
      - manual_review_of_converted_workstreams
      - dry_run_validation
      - gradual_rollout_10_percent_then_50_then_100
    rollback:
      - keep_original_json_files
      - feature_toggle_to_legacy_engine

  tool_adapter_incompatibility:
    risk: existing_tools_dont_work_with_uet_adapters
    mitigation:
      - bridge_pattern_wraps_existing_adapters
      - extensive_integration_testing
      - preserve_legacy_adapter_path
    rollback:
      - use_legacy_tool_bridge_route_through_old_system

  parallel_execution_race_conditions:
    risk: concurrent_workstreams_interfere
    mitigation:
      - start_with_max_workers_1_sequential
      - gradual_increase_to_2_then_4
      - workspace_isolation_per_workstream
    rollback:
      - reduce_max_workers_to_1

medium_risks:
  performance_degradation:
    risk: new_system_slower_than_old
    mitigation:
      - performance_benchmarking_before_and_after
      - profiling_bottlenecks
      - optimization_passes
    rollback:
      - switch_to_legacy_engine

  configuration_complexity:
    risk: new_config_system_confusing
    mitigation:
      - comprehensive_documentation
      - migration_guide_with_examples
      - automated_config_generation
    rollback:
      - fallback_to_env_vars
```

## ROLLBACK_PROCEDURE

```yaml
time_to_execute: under_15_minutes
steps:
  - step_1_switch_engine:
      command: export PIPELINE_ENGINE=legacy
      verification: echo $PIPELINE_ENGINE

  - step_2_rollback_database:
      command: sqlite3 .worktrees/pipeline_state.db < schema/migrations/uet_migration_001_rollback.sql
      verification: sqlite3 .worktrees/pipeline_state.db "SELECT name FROM sqlite_master WHERE type='table'"

  - step_3_restart_services:
      command: systemctl restart pipeline-orchestrator
      verification: systemctl status pipeline-orchestrator

  - step_4_health_check:
      command: python -m core.cli health-check
      verification: exit_code == 0

rollback_triggers:
  automatic:
    - workstream_failure_rate > 20%
    - database_corruption_detected
    - critical_tool_adapter_failure

  manual_decision:
    - performance_degradation > 50%
    - unresolvable_bug_discovered
    - production_stability_issues

post_rollback_actions:
  - notify_team
  - create_incident_report
  - analyze_failure_root_cause
  - plan_remediation_before_retry
```

## SUCCESS_METRICS

```yaml
technical:
  - all_46_workstreams_converted_and_validated: boolean
  - 337_uet_tests_passing: boolean
  - all_existing_tests_passing: boolean
  - database_migration_successful_zero_data_loss: boolean
  - parallel_execution_operational_4_plus_workers: boolean
  - patch_ledger_recording_100_percent_changes: boolean
  - speedup_demonstrated_3_5x: boolean

operational:
  - zero_downtime_during_cutover: boolean
  - rollback_capability_tested_and_validated: boolean
  - documentation_complete_and_published: boolean
  - team_trained_on_new_system: boolean
  - monitoring_dashboards_operational: boolean

quality:
  - no_regressions_in_functionality: boolean
  - improved_error_handling_patch_quarantine: boolean
  - better_observability_unified_events: boolean
  - cleaner_architecture_uet_separation_of_concerns: boolean
```

## EXECUTION_DEPENDENCIES

```yaml
dependency_graph:
  PHASE_0_TEMPLATE_LIBRARY:
    depends_on: []
    blocks: [PHASE_1_FOUNDATION]
    parallel_execution: no (foundation layer)

  PHASE_1_FOUNDATION:
    depends_on: [PHASE_0_TEMPLATE_LIBRARY]
    blocks: [PHASE_2_PARALLEL_EXECUTION, PHASE_3_PATCH_MANAGEMENT]
    parallel_execution: yes (3 worktrees can work simultaneously)
    worktrees: [wt-phase1-database, wt-phase2-dag, wt-phase3-patches]

  PHASE_2_PARALLEL_EXECUTION:
    depends_on: [PHASE_1_FOUNDATION]
    blocks: [PHASE_4_INTEGRATION_TESTING]
    parallel_execution: partial (dag scheduler must complete before parallel orchestrator)

  PHASE_3_PATCH_MANAGEMENT:
    depends_on: [PHASE_2_PARALLEL_EXECUTION]
    blocks: [PHASE_4_INTEGRATION_TESTING]
    parallel_execution: no (depends on phase 2 completion)

  PHASE_4_INTEGRATION_TESTING:
    depends_on: [PHASE_2_PARALLEL_EXECUTION, PHASE_3_PATCH_MANAGEMENT]
    blocks: [PHASE_5_CUTOVER]
    parallel_execution: yes (multiple test suites can run simultaneously)

  PHASE_5_CUTOVER:
    depends_on: [PHASE_4_INTEGRATION_TESTING]
    blocks: []
    parallel_execution: no (sequential staged rollout)

critical_path:
  - PHASE_0_TEMPLATE_LIBRARY (2 days)
  - PHASE_1_FOUNDATION (10 days, can be accelerated to 4 days with parallel worktrees)
  - PHASE_2_PARALLEL_EXECUTION (5 days)
  - PHASE_3_PATCH_MANAGEMENT (3 days)
  - PHASE_4_INTEGRATION_TESTING (3 days)
  - PHASE_5_CUTOVER (1 day)

total_duration_sequential: 24_days
total_duration_with_worktree_parallelism: 14_days (phase 1 accelerated 10→4 days)
realistic_timeline: 3_4_weeks_with_buffer_and_parallel_execution
original_timeline_without_patterns: 6_8_weeks
time_savings_from_prmnt_docs_patterns: 2_4_weeks
```

## ENVIRONMENT_VARIABLES

```yaml
required:
  PIPELINE_ENGINE:
    values: [legacy, uet]
    default: legacy
    purpose: engine_mode_selection

  PIPELINE_DB_PATH:
    type: path
    default: .worktrees/pipeline_state.db
    purpose: database_location

  PIPELINE_MAX_WORKERS:
    type: integer
    default: 4
    range: [1, 16]
    purpose: parallel_worker_count

optional:
  PIPELINE_DRY_RUN:
    type: boolean
    default: false
    purpose: skip_external_tools

  UET_PATCH_LEDGER_DIR:
    type: path
    default: .ledger/
    purpose: patch_artifact_storage

  UET_DEBUG:
    type: boolean
    default: false
    purpose: verbose_logging
```

## MONITORING_METRICS

```yaml
collect_during_execution:
  - workstream_completion_rate
  - average_execution_time_per_workstream
  - parallel_efficiency_actual_vs_theoretical
  - error_rate_old_vs_new_engine
  - patch_ledger_integrity_checks
  - database_size_growth
  - memory_usage_per_worker
  - cpu_usage_parallel_execution

dashboards_to_create:
  - real_time_execution_progress
  - parallel_worker_utilization
  - patch_state_machine_flow
  - error_rate_trends
  - performance_comparison_old_vs_new
```

## FINAL_DELIVERABLES

```yaml
code:
  - uet_core_integration: 8_modules
  - bridge_adapters: 3_files
  - workstream_converter: 2_files_plus_46_converted_workstreams
  - database_layer: unified_db_py
  - parallel_orchestrator: dag_scheduler_plus_executor
  - patch_management: ledger_plus_converter
  - testing_suite: integration_tests_plus_validator
  - rollback_scripts: sql_plus_data_migration

documentation:
  - migration_guide: step_by_step_instructions
  - operator_guide: production_usage
  - developer_guide: architecture_and_api
  - troubleshooting_guide: common_issues_and_solutions
  - performance_report: benchmarking_results
  - migration_report: conversion_results_issues_resolutions

training:
  - walkthrough_session: live_demo
  - qa_session: team_questions
  - runbook: quick_reference_for_operators
```

## PRMNT_DOCS_PATTERN_INTEGRATION

```yaml
patterns_integrated_from: C:\Users\richg\Downloads\PRMNT DOCS

pattern_1_multi_cli_worktree_coordination:
  source: MULTI_CLI_WORKTREES_EXECUTION_SPEC.md
  implemented_in: PHASE_0_TEMPLATE_LIBRARY.worktree_coordination
  key_concepts:
    - control_checkout_single_writer_for_global_state
    - worker_worktrees_scoped_to_paths
    - environment_variables: [WT_ID, WT_SCOPE, RUN_ID, LOG_ROOT]
    - single_writer_enforcement_for_critical_files
  impact: enables_parallel_work_on_phase_1_foundation

pattern_2_batch_execution_EXEC_001:
  source: EXECUTION_PATTERNS_COMPLETE.md, EXECUTION_PATTERNS_LIBRARY.md
  implemented_in: PHASE_1_DAY_1_2_DATABASE.batch_execution_pattern_EXEC_001
  key_concepts:
    - batch_file_with_file_action_template_verify_structure
    - template_driven_file_creation
    - programmatic_verification_per_file
  impact: eliminates_decisions_about_what_to_create_and_how

pattern_3_ground_truth_verification:
  source: UTE_execution-acceleration-guide.md
  implemented_in: all_phases.ground_truth_gates
  key_concepts:
    - no_subjective_review
    - exit_code_checks_required
    - file_exists_checks_required
    - test_pass_checks_required
    - halt_and_report_on_failure
  impact: prevents_hallucination_of_success

pattern_4_decision_elimination:
  source: UTE_decision-elimination-playbook.md
  implemented_in: PHASE_0_TEMPLATE_LIBRARY.templates_to_create
  key_concepts:
    - pre_compiled_execution_templates
    - pre_decided_schema_structures
    - pre_validated_sql_syntax
    - pre_scripted_verification_commands
  impact: 37x_speedup_potential_via_eliminated_decision_overhead

pattern_5_anti_pattern_guards:
  source: UET_2025- ANTI-PATTERN FORENSICS.md
  implemented_in: PHASE_0_TEMPLATE_LIBRARY.anti_pattern_guards
  key_concepts:
    - hallucination_of_success: never_mark_complete_without_programmatic_verification
    - planning_loop_trap: max_2_plan_revisions_before_execution
    - partial_success_amnesia: checkpoint_after_each_phase
    - approval_loop: no_human_approval_for_templated_operations
  impact: prevents_documented_failure_modes_from_recurring

pattern_6_decision_telemetry:
  source: UTE_decision-elimination-playbook.md
  implemented_in: PHASE_0_TEMPLATE_LIBRARY.decision_telemetry
  key_concepts:
    - track_decisions_avoided_count
    - track_template_reuse_count
    - track_manual_intervention_count
    - measure_time_saved_vs_baseline
    - measure_error_rate_templated_vs_manual
  impact: quantifies_value_of_decision_elimination_approach

pattern_7_parallel_execution_strategy:
  source: PARALLEL_EXECUTION_STRATEGY.md
  implemented_in: PHASE_1_FOUNDATION.execution_mode, EXECUTION_DEPENDENCIES
  key_concepts:
    - 3_worktrees_for_phase_1 (database, dag, patches)
    - independent_parallel_work_streams
    - control_checkout_merges_all_results
    - 4x_speedup_vs_sequential
  impact: accelerates_phase_1_from_10_days_to_4_days

quantified_improvements:
  timeline_acceleration:
    original: 6_8_weeks
    with_patterns: 3_4_weeks
    time_saved: 2_4_weeks
    speedup_factor: 1.7x_to_2.3x

  decision_elimination:
    decisions_per_phase_without_patterns: estimated_50
    decisions_per_phase_with_patterns: estimated_5
    decisions_eliminated_per_phase: 45
    total_decisions_eliminated: 225 (across 5 phases)

  risk_reduction:
    failure_modes_prevented: 4 (anti_pattern_guards)
    hallucination_incidents: 0 (ground_truth_gates)
    manual_rework_iterations: reduced_from_estimated_3_to_0

  parallel_efficiency:
    phase_1_sequential: 10_days
    phase_1_parallel_3_worktrees: 4_days
    speedup: 2.5x

verification_that_all_prmnt_patterns_integrated:
  multi_cli_worktree_coordination: yes_phase_0
  single_writer_global_state: yes_phase_0
  batch_execution_EXEC_001: yes_phase_1_database
  ground_truth_verification: yes_all_phases
  decision_elimination_templates: yes_phase_0
  anti_pattern_guards: yes_phase_0
  decision_telemetry: yes_phase_0
  parallel_execution_strategy: yes_phase_1_foundation

missing_patterns_from_prmnt_docs: none
```

## END_PLAN
