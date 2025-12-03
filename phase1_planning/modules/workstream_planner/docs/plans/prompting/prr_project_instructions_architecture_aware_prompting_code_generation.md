---
doc_id: DOC-GUIDE-PRR-PROJECT-INSTRUCTIONS-ARCHITECTURE-441
---

# PRR Project Instructions — Architecture‑Aware Prompting & Code Generation

**Purpose.** Provide a single, machine‑readable set of instructions that every AI task follows to (1) create high‑quality prompts that respect project architecture and (2) generate production‑ready code that conforms to PRR enterprise best practices.

**Canonical References (load before execution).**
- PRR_ai_prompt_engineering_reference.md (Prompt frameworks)
- PRR_ai_usage_instructions.md (Build order, validation gates, decision tree)
- PRR_enterprise_software_guide.md (Architecture, SDLC guardrails)

---

## 0) Hard Defaults (never skip)
1) **Classify the task** using the Decision Tree and set the proper framework set.
2) **If ambiguity detected**, output only a `<clarification_request>` (schema below) and stop.
3) **All code work** must be architecture‑aware (Hexagonal, Bounded Contexts, Event‑Driven where applicable) and **Contract‑First** before implementation.
4) **Every change** ships behind a **feature flag**, with tests, telemetry, rollback plan, and runbook notes.

---

## 1) Intake & Analysis (MANDATORY)
Produce a structured task analysis and map it to frameworks.

```xml
<task_analysis>
  <original_request>{user_input}</original_request>
  <specificity_transformation>
    <objective>{specific_measurable_goal}</objective>
    <methodology>{step_by_step_approach}</methodology>
    <success_criteria>{quantifiable_completion_criteria}</success_criteria>
  </specificity_transformation>
  <classification>
    <complexity>{simple|moderate|complex|enterprise}</complexity>
    <domain>{financial|technical|creative|analytical|general}</domain>
    <quality>{standard|high|critical|production}</quality>
    <time_constraint>{immediate|standard|flexible|none}</time_constraint>
  </classification>
  <required_sections>{derived_from_decision_tree}</required_sections>
</task_analysis>
```

**Ambiguity rule:** If confidence < 0.9 in any success criterion, output only:

```xml
<clarification_request>
  <missing_detail>{question_1}</missing_detail>
  <missing_detail>{question_2}</missing_detail>
  <blocking_reason>{why_execution_would_be_risky}</blocking_reason>
</clarification_request>
```

---

## 2) Prompt Construction (REQUIRED)
Build an explicit, parseable prompt using the PRR XML structure and personas.

**Role & Persona**
```xml
<role_assignment priority="critical">
  <primary_role>{domain_expert_title}</primary_role>
  <expertise_areas>
    <domain_knowledge years="{years}" depth="{expert_level}"/>
    <quality_standards>
      <professional_bar>{industry_standard_reference}</professional_bar>
      <accuracy_requirement threshold="{>=minimum_accuracy_percentage}"/>
    </quality_standards>
  </expertise_areas>
</role_assignment>
```

**Constraint Architecture**
```xml
<constraints enforcement="strict">
  <mandatory_actions>
    - follow_decision_tree
    - generate_validation_and_tests
    - align_with_architecture_guardrails
  </mandatory_actions>
  <prohibited_behaviors>
    - vague_specs
    - missing_examples
    - shipping_without_validation
  </prohibited_behaviors>
  <quality_gates>
    - structure_validation
    - content_validation
    - production_readiness_if_enterprise
  </quality_gates>
</constraints>
```

**Prompt Skeleton**
```xml
<prompt_structure>
  <instructions>{clear_directives}</instructions>
  <context>{background_and_assumptions}</context>
  <examples>{3_to_5_diverse_examples_covering_edges}</examples>
  <constraints>{boundaries_and_qa_gates}</constraints>
  <output_format>{schemas_or_contracts_expected}</output_format>
</prompt_structure>
```

**Reasoning Activation (for complex/enterprise)**
```xml
<reasoning_activation>
  <thinking_requirement>
    Think step-by-step:
    1. Decompose problem
    2. Analyze inputs and constraints
    3. Propose solution alternatives and choose
    4. Validate against success criteria
  </thinking_requirement>
</reasoning_activation>
```

---

## 3) Architecture‑Aware Code Plan (BEFORE writing code)
Create a change plan that locks contracts and guardrails.

**3.1 Contract‑First Artifacts**
- OpenAPI/AsyncAPI spec(s) and/or event schema(s)
- Consumer‑driven contract tests (CDC)
- Versioning strategy (URL/header/event‑version)

**3.2 System Boundaries & Patterns**
- Bounded Contexts and ownership
- Hexagonal architecture: domain (ports) separated from adapters (DB/HTTP/Queue)
- Event‑Driven and idempotent consumers where async fits

**3.3 Data Change Plan (Expand‑Migrate‑Contract)**
- Expand: additive schema changes with safe defaults
- Migrate: backfill and dual‑read/write under a flag
- Contract: remove old usage after telemetry proves zero consumers

**3.4 Delivery Safety**
- Feature flag scaffolding and rollout stages
- Observability: RED metrics, structured logs, traces
- Canary plan + automatic rollback triggers

**3.5 CI/CD & Security**
- CI gates: lint, coverage, integration & contract tests, SCA/SAST
- SBOM, secret scanning, least‑privilege creds

**Change Spec (fill this every time)**
```yaml
change_id: CHG-YYYY-NNNN
summary: "<short title>"
context: { service: <name>, bounded_context: <name>, owner_team: <name>, related_tickets: [TKT-1234] }
intent:
  goals: ["<measurable>"]
  non_goals: ["<explicitly out>"]
constraints:
  invariants: ["<must always hold>"]
  performance: { p95_latency_ms: <target>, error_rate_pct: <max> }
  security: ["<e.g., PCI scope unchanged>"]
contracts:
  api: { spec: openapi.yaml#/paths/~1foo, change_type: [additive|breaking] }
  events: [{ name: <Event>, version: v1, change_type: additive }]
feature_flag:
  key: <flag_key>
  default: off
  rollout: { stages: [1,10,100], hold_minutes: [60,120] }
verification:
  test_plan: { unit: ["..."], integration: ["..."], e2e: ["..."] }
  observability: { metrics: ["..."], logs: ["..."], traces: ["..."] }
rollback:
  trigger: { error_rate_pct: "> 0.2", p95_latency_ms: "> 300" }
  steps: ["flip flag off", "revert deployment"]
operations:
  runbook_updates: true
  oncall_notified: true
approvals: { code_owner: <name>, architect: <name>, security: <name> }
```

---

## 4) Code Generation Blueprint
Follow this order of execution; do not proceed if a gate fails.

1) **Scaffold** a service using Hexagonal layout:
   - `/domain` (entities, value objects, ports)
   - `/application` (use cases)
   - `/adapters` (db/http/queue, config)
   - `/infra` (container, feature flags, telemetry)
2) **Contracts**: place OpenAPI + event schemas in `/contracts/` and generate CDC tests.
3) **DB Changes**: create migration scripts for expand phase; add backfill job; wire dual‑write under flag.
4) **Tests**: implement testing pyramid (unit, integration, e2e). Minimum coverage and critical‑path 100%.
5) **Observability**: add RED metrics, structured logging with correlation IDs, and tracing spans.
6) **CI/CD**: author pipeline with required gates; include SAST/SCA + SBOM.
7) **Rollout**: create canary plan and automatic rollback triggers.

> **Output Pack** (suggested tree)
```
/contracts/*.yaml
/src/domain/*
/src/application/*
/src/adapters/db/*
/src/adapters/http/*
/src/adapters/queue/*
/feature-flags/*
/migrations/* (expand -> migrate -> contract)
/tests/unit/*  /tests/integration/*  /tests/e2e/*  /tests/contracts/*
/ops/runbook.md  /ops/dashboards.json  /ops/alerts.yaml
/.github/workflows/ci.yml  /security/sbom.json
```

---

## 5) Prompt + Code Validation (Self‑Healing Loop)
Run a bounded iteration loop until quality gates pass or max iterations reached.

```json
{
  "self_healing_loop": {
    "max_iterations": 5,
    "confidence_threshold": 0.9,
    "error_detection": "detect_errors(outputs)",
    "correction_process": "apply_fixes(errors)",
    "validation": "validate_fixes(corrected_outputs)",
    "termination_conditions": [
      "all_errors_resolved",
      "max_iterations_reached",
      "quality_score_achieved"
    ]
  }
}
```

**Validation requirements**
- **Input**: schema compliance, data quality, security screening.
- **Output**: format compliance, completeness, accuracy.
- **Production‑readiness** (enterprise only): monitoring integrated, alerts defined, audit trail, scalability & cost checks.

**Quality checklists to enforce**
- Structure Validation: role assignment, measurable objectives, constraints with gates, proper XML hierarchy, format schemas.
- Content Validation: chain‑of‑thought (complex+), diverse examples, explicit success criteria & validation, error handling, security.
- CI/CD Gates: lint, coverage thresholds, integration + contract tests, dependency scans, artifact build.
- Deployment Readiness: code review complete, rollback tested, monitoring/alerting configured, runbook updated, on‑call notified.

---

## 6) Runtime Safety & Operations
- Always instrument RED (Rate, Errors, Duration) metrics.
- Use JSON structured logs with correlation IDs; ensure PII policy compliance.
- Add tracing (parent/child spans, async links, exemplars).
- Canary by traffic stages (1%→10%→100%) with verification checks between steps; auto‑rollback on breach.
- Security: SAST, SCA, secret scanning, SBOM; least‑privilege credentials with rotation.

---

## 7) Prohibited Behaviors (hard fail)
- Skipping contract definitions or tests
- Long‑lived feature branches
- Shared mutable state across modules, singletons, or shared DB schemas across services
- Shipping without observability or rollback

---

## 8) Final Deliverables (per task)
1) `prompt/` folder with the finalized XML prompt and example set
2) `contracts/` (OpenAPI/events) + CDC tests
3) `src/` hexagonal service scaffold with feature flags enabled
4) `migrations/` EMC plan (expand scripts + backfill job + retirement note)
5) `tests/` per pyramid + coverage report summary
6) `ops/` runbook, dashboards, alerts, canary & rollback plan
7) `CHANGE_SPEC.yaml` completed and linked in README

---

### Appendix A — Minimal Prompt Template
```xml
<prompt>
  <role_assignment>...</role_assignment>
  <constraints>...</constraints>
  <prompt_structure>...</prompt_structure>
  <reasoning_activation>...</reasoning_activation>
  <quality>production</quality>
</prompt>
```

### Appendix B — Minimal CI Workflow (skeleton)
```yaml
name: ci
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make verify  # lint + unit + integration + contracts + security
```

---

**Execution note:** Prefer configuration‑driven stability for orchestration; allow meta‑prompting only to specialize prompt templates, not to bypass guardrails.

