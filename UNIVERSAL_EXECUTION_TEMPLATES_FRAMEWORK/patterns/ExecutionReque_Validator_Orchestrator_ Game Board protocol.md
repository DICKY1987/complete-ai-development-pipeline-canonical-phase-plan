---
doc_id: DOC-PAT-EXECUTIONREQUE-VALIDATOR-ORCHESTRATOR-747
---



So I’ll treat this as:

> “Design the *ExecutionRequest + Validator + Orchestrator* system **using the Game Board protocol on itself**.”

Below is that plan.

---

## 0. Overview: What We’re Building

Target system:

* A **strict execution gateway** that sits between “user intent” and “AI coding tools”.
* It enforces:

  * A structured `ExecutionRequest` / `PhaseSpec` object.
  * Validation against schema + guard rules.
  * Automatic generation of strict-mode prompts for AIs.
* If required elements are missing, **no execution happens**; the AI responds with `VALIDATION_ERROR` instead.

We’ll build this system in phases, and **each phase is described using the Universal Phase Spec logic**.

---

## PH-00 – Governance Bootstrap & Repo Baseline

### Phase Spec

```yaml
phase:
  id: "PH-00"
  workstream_id: "ws-governance-00-bootstrap"
  title: "Governance Bootstrap & Baseline Layout"
  objective: >
    Establish the minimal repo structure and baseline artifacts needed to
    host ExecutionRequest schemas, validator code, and Game Board rules.

  phase_type: "implementation"

  dependencies:
    depends_on: []
    may_run_parallel_with: []

  file_scope:
    create:
      - ".tasks/inbox/.gitkeep"
      - ".tasks/running/.gitkeep"
      - ".tasks/done/.gitkeep"
      - ".tasks/failed/.gitkeep"
      - ".ledger/patches/.gitkeep"
      - ".runs/.gitkeep"
      - "schema/execution_request.schema.json"
      - "schema/phase_spec.schema.json"
      - "config/router.config.yaml"
      - "docs/GAME_BOARD_PROTOCOL.md"
    modify: []
    read_only: []

  tools:
    primary_language: "python"
    secondary_language: "powershell"
    test_runners:
      - "python -m pytest -q"
    shell:
      preferred: "pwsh"

  acceptance:
    powershell:
      - name: "Standard directories exist"
        command: >
          @(
            '.tasks\inbox\.gitkeep',
            '.tasks\running\.gitkeep',
            '.tasks\done\.gitkeep',
            '.tasks\failed\.gitkeep',
            '.ledger\patches\.gitkeep',
            '.runs\.gitkeep'
          ) | ForEach-Object {
            if (-not (Test-Path $_)) { throw "Missing required path: $_" }
          }
      - name: "Schema and config stubs exist"
        command: >
          @(
            'schema\execution_request.schema.json',
            'schema\phase_spec.schema.json',
            'config\router.config.yaml'
          ) | ForEach-Object {
            if (-not (Test-Path $_)) { throw "Missing required file: $_" }
          }
    python: []
```

**Intent:** PH-00 is the baseline – it creates the **“board”** this system will play on. No semantics yet, just structure.

---

## PH-01A – Define ExecutionRequest & PhaseSpec Schemas

**Goal:** Turn the narrative rules into **formal JSON/YAML schemas** that machines can validate.

### Phase Spec

```yaml
phase:
  id: "PH-01A"
  workstream_id: "ws-governance-01a-schemas"
  title: "ExecutionRequest & PhaseSpec Schema Definition"
  objective: >
    Define strict JSON schemas for ExecutionRequest and PhaseSpec that encode
    all required fields (phase_id, workstream_id, file_scope, acceptance, etc.)
    so that invalid requests can be rejected mechanically.

  phase_type: "implementation"

  dependencies:
    depends_on:
      - "ws-governance-00-bootstrap"
    may_run_parallel_with:
      - "ws-governance-01b-guard-rules"

  file_scope:
    create:
      - "tests/test_execution_request_schema.py"
      - "tests/test_phase_spec_schema.py"
    modify:
      - "schema/execution_request.schema.json"
      - "schema/phase_spec.schema.json"
    read_only:
      - "docs/GAME_BOARD_PROTOCOL.md"

  tools:
    primary_language: "python"
    test_runners:
      - "python -m pytest -q tests/test_execution_request_schema.py tests/test_phase_spec_schema.py"
    shell:
      preferred: "pwsh"

  acceptance:
    python:
      - name: "Schema tests pass"
        command: >
          python -m pytest -q tests/test_execution_request_schema.py
          tests/test_phase_spec_schema.py
        success_pattern: "passed"
        max_failures: 0
    powershell:
      - name: "Schemas are valid JSON"
        command: >
          Get-Content schema\execution_request.schema.json | Out-Null;
          Get-Content schema\phase_spec.schema.json | Out-Null;
```

**Key idea:** This is where **“required fields” move from prose to machine-checkable schemas.**

---

## PH-01B – Encode Guard Rules as Code (Non-Negotiables Library)

**Goal:** Turn the Game Board “MUST/FORBIDDEN” rules into a **GuardRule library** (e.g., pure Python functions) that can be run against an `ExecutionRequest`.

### Phase Spec

```yaml
phase:
  id: "PH-01B"
  workstream_id: "ws-governance-01b-guard-rules"
  title: "Guard Rule Library (Non-Negotiables as Code)"
  objective: >
    Implement a GuardRule library that enforces non-negotiable rules such as:
    required acceptance tests, mandatory file_scope, and prohibition of
    giant refactors or missing phase_id/workstream_id.

  phase_type: "implementation"

  dependencies:
    depends_on:
      - "ws-governance-00-bootstrap"
    may_run_parallel_with:
      - "ws-governance-01a-schemas"

  file_scope:
    create:
      - "src/guardrails/rules.py"
      - "tests/test_guard_rules_basic.py"
      - "tests/fixtures/sample_valid_execution_request.json"
      - "tests/fixtures/sample_invalid_execution_request_missing_acceptance.json"
    modify: []
    read_only:
      - "docs/GAME_BOARD_PROTOCOL.md"
      - "schema/execution_request.schema.json"
      - "schema/phase_spec.schema.json"

  tools:
    primary_language: "python"
    test_runners:
      - "python -m pytest -q tests/test_guard_rules_basic.py"
    shell:
      preferred: "pwsh"

  acceptance:
    python:
      - name: "Guard rules enforce must-have fields and reject bad specs"
        command: "python -m pytest -q tests/test_guard_rules_basic.py"
        success_pattern: "passed"
        max_failures: 0
```

**Intent:** After PH-01A + PH-01B, we have:

* **Schemas** (shape & required fields).
* **Guard rules** (deep semantics: “no acceptance tests → reject”, “no file_scope → reject”).

They can run in parallel (1A/1B) because they read only common docs + baseline.

---

## PH-02 – Validation Engine (ExecutionRequest Validator)

**Goal:** Build the **validator service** that takes an `ExecutionRequest` object and decides:

* `VALID` → allowed to generate a prompt / execute.
* `INVALID` → produce a structured error and stop.

### Phase Spec

```yaml
phase:
  id: "PH-02"
  workstream_id: "ws-governance-02-validator-engine"
  title: "ExecutionRequest Validation Engine"
  objective: >
    Implement a validation engine that combines JSON schema validation and
    GuardRule checks, returning structured VALIDATION_ERROR responses when
    requirements are not met.

  phase_type: "implementation"

  dependencies:
    depends_on:
      - "ws-governance-01a-schemas"
      - "ws-governance-01b-guard-rules"
    may_run_parallel_with: []

  file_scope:
    create:
      - "src/validator/engine.py"
      - "src/validator/errors.py"
      - "tests/test_validator_engine.py"
      - "tests/fixtures/sample_valid_phase_spec.json"
      - "tests/fixtures/sample_invalid_phase_spec_no_file_scope.json"
    modify: []
    read_only:
      - "schema/execution_request.schema.json"
      - "schema/phase_spec.schema.json"
      - "src/guardrails/rules.py"

  tools:
    primary_language: "python"
    test_runners:
      - "python -m pytest -q tests/test_validator_engine.py"
    shell:
      preferred: "pwsh"

  acceptance:
    python:
      - name: "Validator correctly accepts or rejects ExecutionRequests"
        command: "python -m pytest -q tests/test_validator_engine.py"
        success_pattern: "passed"
        max_failures: 0
```

**Outcome:** Now we can **mechanically reject incomplete/unsafe execution instructions** before they reach any AI tool.

---

## PH-03 – Strict-Mode Prompt Renderer

**Goal:** Implement a renderer that takes a **valid ExecutionRequest** and produces a **strict-mode AI prompt** with:

* `<PHASE_SPEC>…</PHASE_SPEC>` block.
* `<REPO_CONTEXT>…</REPO_CONTEXT>`.
* A **self-check checklist**.
* Instructions to emit `VALIDATION_ERROR` if anything is missing.

### Phase Spec

```yaml
phase:
  id: "PH-03"
  workstream_id: "ws-governance-03-prompt-renderer"
  title: "Strict-Mode Prompt Renderer"
  objective: >
    Implement a deterministic renderer that converts a validated ExecutionRequest
    into a structured strict-mode prompt for coding AIs, including a self-check
    block that forces the model to reject incomplete PHASE_SPECs.

  phase_type: "implementation"

  dependencies:
    depends_on:
      - "ws-governance-02-validator-engine"
    may_run_parallel_with: []

  file_scope:
    create:
      - "src/renderer/prompt_renderer.py"
      - "tests/test_prompt_renderer.py"
      - "tests/fixtures/sample_execution_request_valid.json"
      - "tests/fixtures/expected_prompt_output.txt"
    modify: []
    read_only:
      - "docs/GAME_BOARD_PROTOCOL.md"
      - "schema/execution_request.schema.json"

  tools:
    primary_language: "python"
    test_runners:
      - "python -m pytest -q tests/test_prompt_renderer.py"
    shell:
      preferred: "pwsh"

  acceptance:
    python:
      - name: "Renderer generates prompts with strict-mode self-check"
        command: "python -m pytest -q tests/test_prompt_renderer.py"
        success_pattern: "passed"
        max_failures: 0
```

**Key behavior:**

* The rendered prompt will explicitly instruct the AI to:

  * Parse `<PHASE_SPEC>`.
  * Verify required fields.
  * Respond with `VALIDATION_ERROR` and **no commands** if anything is missing.

So you get **double enforcement**: external validator + model self-check.

---

## PH-04 – Orchestrator & Tool Adapters

**Goal:** Build the glue that:

* Accepts raw user intent.
* Turns it into an `ExecutionRequest`.
* Validates it.
* Renders a prompt.
* Calls the chosen AI tool (Aider/Codex/etc.) with that prompt.

### Phase Spec

```yaml
phase:
  id: "PH-04"
  workstream_id: "ws-governance-04-orchestrator"
  title: "Execution Orchestrator & Tool Adapters"
  objective: >
    Implement an orchestrator that consumes user intent, constructs an
    ExecutionRequest, validates it via the validator engine, renders a
    strict-mode prompt, and dispatches it to the appropriate coding tool
    adapter (Aider, Codex, etc.).

  phase_type: "implementation"

  dependencies:
    depends_on:
      - "ws-governance-02-validator-engine"
      - "ws-governance-03-prompt-renderer"
    may_run_parallel_with: []

  file_scope:
    create:
      - "src/orchestrator/orchestrator.py"
      - "src/adapters/aider_adapter.py"
      - "src/adapters/codex_adapter.py"
      - "tests/test_orchestrator_happy_path.py"
      - "tests/test_orchestrator_rejects_invalid_requests.py"
    modify:
      - "config/router.config.yaml"
    read_only:
      - "schema/execution_request.schema.json"
      - "src/validator/engine.py"
      - "src/renderer/prompt_renderer.py"

  tools:
    primary_language: "python"
    test_runners:
      - "python -m pytest -q tests/test_orchestrator_happy_path.py tests/test_orchestrator_rejects_invalid_requests.py"
    shell:
      preferred: "pwsh"

  acceptance:
    python:
      - name: "Orchestrator accepts valid request and rejects invalid"
        command: >
          python -m pytest -q tests/test_orchestrator_happy_path.py
          tests/test_orchestrator_rejects_invalid_requests.py
        success_pattern: "passed"
        max_failures: 0
```

**This is where the whole system “comes alive.”**

---

## PH-05 – Operator Execution Tests (End-to-End “Game Board” Scenarios)

**Goal:** Test the **entire pipeline** end-to-end with realistic scenarios:

* Valid ExecutionRequest → AI tool runs Phase 0/1A/1B correctly.
* Invalid ExecutionRequest → immediate `VALIDATION_ERROR`, no execution.

### Phase Spec

```yaml
phase:
  id: "PH-05"
  workstream_id: "ws-governance-05-e2e-tests"
  title: "End-to-End Operator Execution Scenarios"
  objective: >
    Validate that the complete stack (validator + renderer + orchestrator +
    adapters) enforces the Game Board rules in realistic scenarios, including
    rejection of incomplete specs and successful execution of valid ones.

  phase_type: "validation_only"

  dependencies:
    depends_on:
      - "ws-governance-04-orchestrator"
    may_run_parallel_with: []

  file_scope:
    create:
      - "tests/e2e/test_valid_phase_execution.py"
      - "tests/e2e/test_reject_incomplete_phase_spec.py"
      - "tests/fixtures/e2e_valid_phase_request.json"
      - "tests/fixtures/e2e_incomplete_phase_request.json"
    modify: []
    read_only:
      - "src/orchestrator/orchestrator.py"
      - "src/validator/engine.py"
      - "src/renderer/prompt_renderer.py"

  tools:
    primary_language: "python"
    test_runners:
      - "python -m pytest -q tests/e2e"
    shell:
      preferred: "pwsh"

  acceptance:
    python:
      - name: "E2E tests enforce Game Board rules"
        command: "python -m pytest -q tests/e2e"
        success_pattern: "passed"
        max_failures: 0
```

**Outcome:** After PH-05, you have **proof** that:

* Good requests succeed.
* Bad requests never reach the coding tools.

---

## PH-06 – Integration with Existing Pipelines & Tools

**Goal:** Wire this governance system into your actual stack (Codex CLI, Aider, Gemini CLI, etc.) so all future “execution prompts” must flow through it.

Conceptually:

* Update your PowerShell functions / wrappers (`Use-AIStack-Codex`, `Use-AIStack-Aider`) to:

  * Construct an `ExecutionRequest`.
  * Call the validator + renderer + orchestrator.
  * Never directly send raw user prompts to coding tools.

You can model PH-06 as an implementation + migration phase similar to PH-04/05, with acceptance tests that:

* Confirm the old direct calls are no longer reachable.
* Confirm the new wrappers route through the governance system.

---

## How This “Uses the Framework to Build Itself”

* Every phase above is expressed in the **same structure** we just defined:

  * `phase_id`, `workstream_id`, `objective`, `file_scope`, `dependencies`, `acceptance`.
* The system’s **first order of business** (PH-01A/01B/02) is to turn those specs into:

  * JSON schemas, and
  * Guard rules that enforce them.
* Once built, **any future execution request** (including future evolution of this system) must:

  * Provide a valid **PhaseSpec/ExecutionRequest**.
  * Pass validation.
  * Be rendered into a strict prompt that tells the AI to self-reject if fields are missing.

So the development process is:

1. **Design the phases using the Game Board rules.**
2. **Implement schemas and validators that encode those rules.**
3. **Route all future prompts through those validators.**

That’s exactly “using the framework to create itself.”
