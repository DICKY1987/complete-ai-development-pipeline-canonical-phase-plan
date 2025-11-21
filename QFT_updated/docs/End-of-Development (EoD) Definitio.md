# End-of-Development (EoD) Definition — “Recommended Next Steps” Section

> Scope: This EoD governs the “Recommended Next Steps” section you just approved (plan scaffolding, governance, schemas, CI/CD, AC mandates, Projects wiring, and Aider usage docs). It is **strict, machine-verifiable**, and intended to be enforced by CI.

---

## 1) Explicit Deliverables (files, artifacts, docs, contracts)

### 1.1 Planning & Governance

* `plan/README.md` — the 10-step gated checklist; links to all referenced files.
* `plan/file-map.yaml` — canonical file inventory for this section.
* `plan/rtm.yaml` — Requirements Traceability Matrix (PBS→DDS→Tests→CI jobs).
* `CHANGE_SPEC.yaml` — feature flag (`enable_qft_orchestrator`), rollout gates, rollback rules.
* `plan/phase_plan.yaml` — minimal, runnable plan with ≥1 `dependsOn`.

### 1.2 Schemas & Contracts

* `schemas/PlanFile.schema.json` — JSON Schema for `plan/phase_plan.yaml` (via YAML→JSON parse).
* `schemas/DependencyFile.schema.json` — JSON Schema for any optional dependency file.
* `schemas/rtm.schema.json` — schema for `plan/rtm.yaml`.
* `schemas/change_spec.schema.json` — schema for `CHANGE_SPEC.yaml`.

### 1.3 Project & Contributor UX

* `.github/ISSUE_TEMPLATE.md` — **mandatory AC block** + “Suggested Aider Prompt”.
* `docs/USING_AIDER.md` — slash-command flow, session rules, examples.
* `README.md` (top level) — “Portfolio overview” paragraph linking this section.

### 1.4 CI/CD & Evidence Artifacts (produced by pipeline)

* `artifacts/schema_validation_report.json`
* `artifacts/tests-junit.xml` (and/or `TestResults.xml` for Pester)
* `artifacts/coverage.xml` (Cobertura/JaCoCo-compatible) — overall ≥ **85%** for code touched by this section’s utilities/tests.
* `artifacts/lint_report.json` (ScriptAnalyzer, markdownlint, yamllint, actionlint)
* `artifacts/docs_build_log.txt`
* `artifacts/conformance_report.json` (contract checks; see §4)
* `artifacts/traceability_report.json` (RTM completeness)
* `artifacts/eod_proof.json` — single machine-verifiable summary (boolean gates + hashes of inputs).

---

## 2) Acceptance Criteria (BDD/ATDD)

### AC-1 — Plan & Schema Valid

* **Given** the repo at HEAD,
* **When** CI runs `validate:schemas`,
* **Then** `plan/phase_plan.yaml`, `plan/rtm.yaml`, `CHANGE_SPEC.yaml` validate against their schemas and `artifacts/schema_validation_report.json` shows `"errors": []`.

### AC-2 — Mandatory Artifacts Exist & Are Linked

* **Given** the section files,
* **When** CI runs `check:presence+links`,
* **Then** every file in §1 exists **and** `plan/README.md` contains working relative links to each; `artifacts/traceability_report.json.files_present == true`.

### AC-3 — Acceptance-Criteria Enforcement

* **Given** `.github/ISSUE_TEMPLATE.md`,
* **When** CI runs `lint:issues` on open PR issue references,
* **Then** each referenced issue includes a non-empty **AC block** (regex-verified) and the job passes.

### AC-4 — Tests & Coverage

* **Given** unit/integration tests for this section,
* **When** CI runs `test` jobs,
* **Then** all tests are green and `artifacts/coverage.xml` reports **≥85%** line coverage for changed/added modules; job fails below threshold.

### AC-5 — Lint, Static, Docs

* **Given** code/docs in this section,
* **When** CI runs `lint` and `docs:build`,
* **Then** ScriptAnalyzer/markdownlint/yamllint/actionlint have **0 errors** (warnings allowed ≤ 5 total), and docs build succeeds with `artifacts/docs_build_log.txt` containing “Build succeeded”.

### AC-6 — Change-Spec Flagging & Rollback Ready

* **Given** `CHANGE_SPEC.yaml`,
* **When** CI runs `governance:change-spec`,
* **Then** the orchestrator feature is **default=off**, rollout gates are enumerated, and a rollback action is declared; `artifacts/conformance_report.json.change_spec.compliant == true`.

### AC-7 — Traceability PBS→DDS→RTM

* **Given** `plan/rtm.yaml`,
* **When** CI runs `trace:rtm`,
* **Then** every PBS item in scope maps to at least one DDS, test ID, and CI job; `coverage_of_requirements == 100%`.

### AC-8 — Portfolio & Aider Docs

* **Given** `README.md` and `docs/USING_AIDER.md`,
* **When** CI runs `links:check` and `docs:lint`,
* **Then** no dead links; the Aider session table renders; `artifacts/lint_report.json.docs.errors == 0`.

---

## 3) Evidence of Completion

To mark EoD, CI must publish:

* **JUnit/Pester** results: `artifacts/tests-junit.xml` (all pass).
* **Coverage**: `artifacts/coverage.xml` (overall ≥85%; per-file ≥70% for added files).
* **Schema**: `artifacts/schema_validation_report.json` (no errors).
* **Traceability**: `artifacts/traceability_report.json` with:

  * `pbs_count`, `dds_count`, `tests_linked`, `ci_jobs_linked`, `coverage_of_requirements: 100`.
* **Conformance**: `artifacts/conformance_report.json` with:

  * `plan_schema:true`, `dependency_schema:true`, `rtm_schema:true`, `change_spec_schema:true`, `feature_flag.default:false`, `rollback.defined:true`.
* **EoD proof**: `artifacts/eod_proof.json` with:

  * `all_gates_green:true`, SHA-256 of each required file, CI run ID, timestamp (UTC), SemVer tag, ULID (see §8).

---

## 4) Contract & Interface Conformance

**Authoritative Schemas & Protocols**

* `schemas/PlanFile.schema.json` — applies to `plan/phase_plan.yaml` (YAML parsed to JSON).
* `schemas/DependencyFile.schema.json` — applies if a dependency file is present.
* `schemas/rtm.schema.json` — applies to `plan/rtm.yaml`.
* `schemas/change_spec.schema.json` — applies to `CHANGE_SPEC.yaml`.

**Validation Method**

* CI job runs `ajv` (or equivalent) with `--strict` against each file; results must be **zero-error** and recorded in `artifacts/conformance_report.json`.

---

## 5) File-Level Definition of Done (role • tests • quality gates)

| File                        | Role                              | Required Tests                                      | Quality Gates                             |
| --------------------------- | --------------------------------- | --------------------------------------------------- | ----------------------------------------- |
| `plan/README.md`            | Canonical 10-step gated checklist | Markdown link check; presence of required anchors   | markdownlint: 0 errors; links 100% valid  |
| `plan/file-map.yaml`        | Inventory of required files       | YAML parse; presence check against §1               | yamllint: 0 errors; matches on-disk files |
| `plan/rtm.yaml`             | PBS→DDS→Tests→CI mapping          | Schema validate; RTM completeness calc              | RTM coverage 100%                         |
| `CHANGE_SPEC.yaml`          | Feature flag + rollout + rollback | Schema validate; policy lints                       | Flag default=false; rollback defined      |
| `plan/phase_plan.yaml`      | Runnable minimal plan             | Schema validate; **orchestrator dry-run** returns 0 | ≥1 `dependsOn`; no cyclic deps            |
| `.github/ISSUE_TEMPLATE.md` | Enforce AC block                  | Regex match for AC section; link check              | 0 lint errors; AC block non-empty         |
| `docs/USING_AIDER.md`       | Aider session playbook            | Link check; renderable table check                  | 0 doc lint errors                         |
| `schemas/*.json`            | Contract sources                  | Self-test with positive/negative samples            | All tests green                           |
| `README.md` (root)          | Portfolio overview                | Link check to plan/docs                             | 0 lint errors                             |

---

## 6) Traceability Requirements

* **Front-matter IDs**: Each artifact in §1 includes front-matter fields:
  `doc_key`, `semver`, `ulid`, `effective_date`, `supersedes_version?`.
* **RTM completeness**: Every PBS item → ≥1 DDS → ≥1 Test ID → ≥1 CI job.
  Calculated in `artifacts/traceability_report.json` (`coverage_of_requirements: 100`).
* **Commit discipline**: All commits that add/modify these files reference **Issue IDs** and include a **ULID** in the footer: `Refs: #<issue>, ULID:<ulid>`.

---

## 7) CI/CD Gate Criteria (must be green)

1. `validate:schemas` — all schema validations pass (strict mode).
2. `lint:all` — ScriptAnalyzer/markdownlint/yamllint/actionlint with **0 errors**.
3. `test` — all tests pass; publish `tests-junit.xml`.
4. `coverage` — overall ≥85%, new files ≥70%.
5. `docs:build` — succeeds; logs published.
6. `trace:rtm` — 100% requirement coverage; no orphan DDS/tests.
7. `governance:change-spec` — flag default=false; rollback defined.
8. `links:check` — no dead relative links in docs/plan/README.
9. `bundle:evidence` — produce `eod_proof.json` with hashes & CI ID.

> **Rule:** The PR cannot merge unless **all** above jobs succeed.

---

## 8) Versioning & Reproducibility

* **Versioning**:

  * Tag this section’s completion as `docs-ops.<major>.<minor>.<patch>` (SemVer).
  * Each artifact carries `semver` and a content ULID (e.g., `01J...`).
* **Reproducibility**:

  * Running `pwsh -File scripts/bootstrap_ci.ps1` on a clean Windows runner yields identical CI outcomes (idempotent).
  * Every evidence artifact includes SHA-256 hashes of its inputs.
  * The CI job archives `artifacts/*` and attaches them to the release for audit.

---

## 9) Completion Decision (single machine check)

Development for this section is **complete** when:

* The default branch contains **all files** listed in §1, and
* A CI run on the merge commit produces `artifacts/eod_proof.json` with:

  ```json
  {
    "all_gates_green": true,
    "schema_errors": 0,
    "tests": {"passed": true},
    "coverage": {"overall": 0.85, "new_files_min": 0.70},
    "rtm_coverage": 1.0,
    "change_spec": {"default_off": true, "rollback_defined": true},
    "hashes": {"plan/README.md": "…", "plan/rtm.yaml": "…"},
    "ci_run_id": "<provider-run-id>",
    "ulid": "<section-ulid>",
    "semver": "docs-ops.X.Y.Z",
    "timestamp_utc": "YYYY-MM-DDTHH:MM:SSZ"
  }
  ```
* And the release `docs-ops.X.Y.Z` is created with the CI artifacts attached.

> Passing the above machine check constitutes the authoritative EoD signal for this scope.
