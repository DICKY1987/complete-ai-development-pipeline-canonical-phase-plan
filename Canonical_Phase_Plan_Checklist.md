### Phase 00 – Baseline & Project Skeleton
- [ ] Create required folders: `docs/`, `plans/`, `scripts/`, `tests/`, `assets/`.
- [ ] Add or update `AGENTS.md` and `README.md`.
- [ ] Seed `scripts/bootstrap.ps1` and `scripts/test.ps1`.
- [ ] Confirm `pwsh ./scripts/test.ps1` executes.
- [ ] Commit with Conventional Commit (e.g., `chore: scaffold repository skeleton`).
- [ ] Ensure directory skeleton exists and matches the plan.
- [ ] Document build/test commands in `AGENTS.md` and verify them locally.
- [ ] Ensure linting/testing (if configured) runs without errors.
- [ ] Verify no secrets or large binaries are committed.

### Phase 01 – Spec Alignment & Index Mapping
- [ ] Define the canonical Python module layout for the pipeline (e.g., `src/pipeline/db.py`, `orchestrator.py`).
- [ ] Scan specification documents for `[IDX-...]` tags.
- [ ] Generate and maintain a spec index mapping file (`docs/spec/spec_index_map.md`).
- [ ] Create a re-runnable index generator script (`scripts/generate_spec_index.py`).
- [ ] Update `docs/ARCHITECTURE.md` with a "Spec Mapping & IDX Index" section.
- [ ] Update `docs/PHASE_PLAN.md` to reflect the outputs of PH-01.
- [ ] (Optional) Add tests for the index generator.

### Phase 02 – Data Model, SQLite State Layer & State Machine
- [ ] Define and create the SQLite schema in `schema/schema.sql` (tables: `runs`, `workstreams`, `step_attempts`, `errors`, `events`, `schema_meta`).
- [ ] Implement the `src/pipeline/db.py` data-access layer with functions like `init_db()`, `create_run()`, etc.
- [ ] Implement a formal state machine for workstreams with `validate_state_transition()`.
- [ ] Document the state machine in `docs/state_machine.md`.
- [ ] Provide database management scripts (`scripts/init_db.py`, `scripts/db_inspect.py`).
- [ ] Add tests for schema correctness and state transitions in `tests/pipeline/test_db_state.py`.
- [ ] Update `docs/ARCHITECTURE.md` with a "State & Persistence" section.

### Phase 03 – Tool Profiles & Adapter Layer
- [ ] Define a declarative tool profile format in `config/tool_profiles.json`.
- [ ] Implement the `src/pipeline/tools.py` adapter with a single `run_tool()` entry point.
- [ ] Integrate with the database layer to log events and errors.
- [ ] Add tests for the tool adapter in `tests/pipeline/test_tools.py`.
- [ ] Update `docs/ARCHITECTURE.md` with a "Tool Profiles & Adapter Layer" section.

### Phase 03.5 – Aider Integration Contract & Prompt Template System
- [ ] Define a precise, written integration contract for the Aider CLI in `docs/aider_contract.md`.
- [ ] Implement a prompt engine in `src/pipeline/prompts.py` using Jinja templates located in `aider/templates/prompts/`.
- [ ] Wire Aider through the existing `run_tool()` adapter.
- [ ] Add sandbox repositories (`sandbox_repos/`) and integration tests (`tests/integration/test_aider_sandbox.py`) to validate Aider behavior.
- [ ] Update `docs/ARCHITECTURE.md` with an "Aider Integration & Prompt Engine" section.

### Phase 04 – Workstream Bundle Parsing & Validation
- [ ] Define a JSON Schema for workstream bundles in `schema/workstream.schema.json`.
- [ ] Implement `src/pipeline/bundles.py` to load, validate, and analyze workstream bundles.
- [ ] Build a dependency DAG from bundles and detect cycles.
- [ ] Detect and report conflicting file scopes between workstreams.
- [ ] (Optional) Implement logic to sync validated bundles into the database.
- [ ] Create a validation script `scripts/validate_workstreams.py`.
- [ ] Add tests for bundle loading and validation in `tests/pipeline/test_bundles.py`.
- [ ] Update `docs/ARCHITECTURE.md` with a "Workstream Bundles & Validation" section.

### Phase 04.5 – Git Worktree Lifecycle Management
- [ ] Implement `src/pipeline/worktree.py` to manage the lifecycle of git worktrees (create, inspect, validate, clean).
- [ ] Enforce file-scope rules by implementing `validate_scope()`.
- [ ] Provide CLI scripts for worktree management (`scripts/worktrees.py`).
- [ ] Add tests for the worktree lifecycle in `tests/pipeline/test_worktree.py`.
- [ ] Update `docs/ARCHITECTURE.md` with a "Git Worktree Lifecycle & Scope Enforcement" section.

### Phase 05 – Orchestrator Core Loop (Single Workstream)
- [ ] Implement the core orchestrator loop in `src/pipeline/orchestrator.py` for a single workstream (EDIT → STATIC → RUNTIME).
- [ ] Integrate existing modules: `db.py`, `bundles.py`, `worktree.py`, `tools.py`, and Aider integration.
- [ ] Record all state transitions and step attempts in the database.
- [ ] Provide a CLI script to run a single workstream (`scripts/run_workstream.py`).
- [ ] Add tests to verify the orchestrator's behavior in `tests/pipeline/test_orchestrator_single.py`.
- [ ] Update `docs/ARCHITECTURE.md` with an "Orchestrator Core Loop" section.

### Phase 05.5 – Workstream Bundle Generator
- [ ] Create a comprehensive authoring guide for workstream bundles in `docs/workstream_authoring_guide.md`.
- [ ] Provide a canonical JSON template for new workstreams in `aider/templates/workstream_template.json`.
- [ ] Implement an authoring-focused validation script `scripts/validate_workstreams_authoring.py`.
- [ ] (Optional) Scaffold an automated planner module `src/pipeline/planner.py` and `config/decomposition_rules.yaml`.
- [ ] Add tests for the authoring and validation workflow in `tests/pipeline/test_workstream_authoring.py`.
- [ ] Update `docs/ARCHITECTURE.md` with a "Workstream Authoring & Generation" section.

### Phase 06 – Circuit Breakers, Retries & Fix Loop
- [ ] Implement a generic circuit breaker module in `src/pipeline/circuit_breakers.py` with configuration in `config/circuit_breakers.yaml`.
- [ ] Add FIX loops around STATIC and RUNTIME steps in the orchestrator.
- [ ] Use error signatures and attempt counts from the database to decide whether to retry.
- [ ] Implement oscillation detection using diff hashes to prevent infinite loops.
- [ ] Add tests for the circuit breaker logic and the FIX loop (`tests/pipeline/test_circuit_breakers.py`, `tests/pipeline/test_orchestrator_fix_loop.py`).
- [ ] Update `docs/ARCHITECTURE.md` with a "Circuit Breakers & FIX Loop" section.

### Phase 07 – GUI Layer & Plugin System
- [ ] Implement a PyQt6-based GUI shell with a plugin architecture in `src/gui/shell.py`.
- [ ] Define and enforce a strict permissions matrix in `docs/GUI_PERMISSIONS_MATRIX.md`.
- [ ] Implement a service locator pattern and service clients for GUI-backend communication in `src/gui/services/`.
- [ ] Create core panel plugins (Dashboard, Runs, Workstreams, Tools, Logs, Terminal) in `src/gui/panels/`.
- [ ] Add GUI configuration (`config/gui_config.yaml`) and plugin manifests.
- [ ] Add tests for GUI components, services, and plugin loading in `tests/gui/`.
- [ ] Update `docs/ARCHITECTURE.md` with a "GUI Layer & Plugin System" section.

### Phase 08 – AIM Tool Registry Integration
- [ ] Integrate the `.AIM_ai-tools-registry` system into the pipeline.
- [ ] Implement a Python-to-PowerShell bridge in `src/pipeline/aim_bridge.py` to invoke AIM adapters.
- [ ] Add capability-based tool routing with fallback chains.
- [ ] Implement audit logging for all tool invocations.
- [ ] Extend `config/tool_profiles.json` with AIM-specific metadata.
- [ ] Add tests for the AIM bridge and integration (`tests/pipeline/test_aim_bridge.py`, `tests/integration/test_aim_end_to_end.py`).
- [ ] Update `docs/ARCHITECTURE.md` with an "AIM Tool Registry Integration" section.

### Phase 09 – Multi-Document Versioning and Spec Management
- [ ] Implement a documentation versioning system using sidecar metadata files (`.sidecar.yaml`).
- [ ] Create a suite of tools for spec management: `spec_indexer`, `spec_resolver`, `spec_patcher`, `spec_renderer`, and `spec_guard`.
- [ ] Enable cross-document linking and version synchronization using `IDX-` tags.
- [ ] Add schema validation for documentation conformance (`schema/sidecar_metadata.schema.yaml`).
- [ ] Implement functionality to render unified documentation views from multi-part specs.
- [ ] Add tests for all spec management tools in `tests/tools/`.
- [ ] Update `docs/ARCHITECTURE.md` with a "Multi-Document Versioning & Spec Management" section.

