---
doc_id: DOC-GUIDE-OPINIONATED-PLANNING-FRAMEWORK-1117
---

Below is a comprehensive, opinionated planning framework you can use to rewrite your project plan so it is:

1. Directly actionable by Aider (clear prompts, file scoping, acceptance criteria).
2. Mapped cleanly to GitHub constructs (issues, milestones, projects, labels).
3. Structured for traceability from Vision → Goals → Milestones → Epics → Issues → Tasks.
4. Optimized for incremental AI-assisted implementation with minimal ambiguity.

If you paste your existing plan afterward, I can transform it into this structure.

---

## 0. Quick Start Summary (Executive Snapshot)
Use this as the top of your main planning document (e.g., PROJECT_PLAN.md).

| Element | Value (Example) |
|---------|------------------|
| Vision | Deliver an AI-augmented CLI+API developer assistant that supports multi-model strategy and extensible tooling. |
| Primary Metrics | Time-to-implement features (median), % AI-generated code accepted, test coverage delta, issue cycle time. |
| Release Cadence | Biweekly tagged releases |
| Current Phase | Foundation / Internal Refactors |
| Upcoming Milestone | M2: Config & Extensibility |
| Aider Usage Pattern | Focus AI sessions on refactors & adding well-scoped features with explicit file targeting and test-first acceptance criteria. |

---

## 1. Vision
Single paragraph: What long-term transformation this project creates and for whom.

Example:
Aider will evolve into an extensible, scriptable developer co-pilot that safely performs multi-step refactors, generates testable feature increments, and integrates with project governance (linting, tests, dependency maps) to reduce context-switching and cognitive load.

---

## 2. Strategic Goals (6–12 month horizon)
Write each goal as an outcome with a measurable leading or lagging indicator.

Format:
- G1: Improve reliability of AI code edits (Target: <2% reverted commits per release by R6).
- G2: Enable plugin-like extension system (≥5 community extensions by month 4).
- G3: Reduce average issue cycle time from open → merged (Baseline X days → Target Y days).
- G4: Provide full multi-model fallback with graceful degradation (95% task completion availability).
- G5: Strengthen test coverage for core modules (Core modules >85% branch coverage).

Traceability Rule:
Each Goal must map to at least one Milestone and multiple Epics.

---

## 3. Milestones (Concrete Release Groupings)
Milestones collect Epics. Each should be time-bound and have exit criteria.

Example format:

| Milestone | Target Date | Exit Criteria | Metrics Impacted | Risks |
|-----------|-------------|---------------|------------------|-------|
| M1 Core Stability | 2025-01-15 | Baseline test suite + lint auto-fix integrated with Aider; refactor critical command parsing | G1, G5 | Hidden coupling in legacy paths |
| M2 Config & Extensibility | 2025-02-05 | Pluggable config loader; initial extension API | G2 | API surface churn |
| M3 Multi-LLM Robustness | 2025-03-01 | Fallback across top 4 providers; error resilience harness | G4 | Rate limit variance |
| M4 Developer UX Polish | 2025-03-25 | Prompt templates, improved diff summarization, doc alignment | G1 | Scope creep |
| M5 Ecosystem & Community | 2025-04-20 | 5 external extensions + docs + examples repo | G2 | Low contributor onboarding |

Exit criteria should be worded so Aider can help implement them (ie: “Add test coverage for X”, “Refactor Y file into Z modules”, etc.).

---

## 4. Epics (Theme-level bodies of work)
Epic Format (Markdown section or separate file EPIC_<slug>.md):

```
Epic: Multi-Model Fallback Engine
Code Domains: aider/llm.py, aider/models/, aider/config/
Goal Link: G4
Milestone: M3
Narrative:
Implement orchestrator that selects best available model by capability, cost, latency, and context size, with retry/fallback strategy.

Business Value:
Reduces failure rate & increases task completion reliability.

Success Metrics:
- ≥95% successful execution of AI edit sessions with >=2 model fallback tiers.
- Model selection decisions logged & inspectable.

Risks & Mitigations:
- Risk: API schema drift → Mitigation: abstraction layer w/ versioned adapters.
- Risk: Latency spikes → Mitigation: concurrency + speculative parallel first-token critics (future).

Out of Scope:
Training custom models, advanced RL scheduling.

Dependencies:
- Needs baseline config refactor (Epic: Unified Config Loader).
```

Each Epic should list the initial Issue stubs (convertible later):

| Issue Key | Title | Type | Rough Estimate | Priority | Depends On |
|-----------|-------|------|----------------|----------|------------|
| MMF-1 | Define model capability taxonomy | Research/Design | 2d | High | - |
| MMF-2 | Implement provider adapter interface | Feature | 3d | High | CFG-2 |
| MMF-3 | Add fallback selection logic w/ scoring | Feature | 4d | High | MMF-2 |
| MMF-4 | Logging & telemetry integration | Feature | 2d | Medium | MMF-3 |
| MMF-5 | Doc page: multi-model strategy | Docs | 1d | Medium | MMF-3 |
| MMF-6 | Tests: simulated degraded provider states | Test | 2d | High | MMF-3 |

---

## 5. Issue Structure (Optimized for Aider & GitHub)
Use a consistent template so Aider can ingest, reason, and act. Keep scope small enough for a single AI edit session when possible.

Issue Title Pattern:
[Area] Concise action with target file(s)
Example: [LLM Orchestrator] Implement provider abstraction in aider/models/base.py

Recommended Labels:
- area/<domain> (eg: area/llm, area/config, area/cli)
- type/feature, type/refactor, type/test, type/docs, type/research
- size/s, size/m, size/l (define heuristics: S ≤1 AI session, M 2–3 sessions, L >3)
- priority/p0…p3
- status/blocked (optional workflow)
- risk/<descriptor> (only if unusually risky)

Issue Template (GitHub ISSUE_TEMPLATE/feature.md):

````markdown
## Summary
Short imperative: Refactor aider/config.py to support layered config precedence (env > user > project).

## Context
Files: aider/config.py, aider/__init__.py
Related Epics: Config Layering (CFG)
Linked Goals: G2

## Current Behavior
- Single flat loader with duplicated parsing logic.
- No environment override granularity.

## Desired Behavior
Layered resolution order:
1. Environment variables (AIDER_* namespace)
2. User global config (~/.aider/config.toml)
3. Project local config (.aider/config.toml)
4. CLI flags (highest precedence)

## Constraints
- Must not break existing public CLI flags.
- Backward compatible defaults.

## Acceptance Criteria
- Tests: tests/config/test_precedence.py demonstrating all 4 layers.
- New function load_config(precedence: list[str]) documented.
- Lint passes (ruff) & test suite green.
- Log summary of final resolved keys when verbose enabled.

## Implementation Hints (Optional)
Refactor into ConfigResolver class.
Use dataclass for normalized config state.

## Out of Scope
Plugin registration, dynamic reloading.

## Dependencies
CFG-1 (taxonomy)
None blocking.

## Risks
Subtle precedence bugs → mitigate via explicit test matrix.

## Suggested Aider Prompt
Refactor aider/config.py to implement layered config precedence across env, user, project, CLI inputs. Update or create tests/config/test_precedence.py with matrix coverage for overrides. Preserve existing public CLI behavior. Provide final diff only.

````

Aider Prompt Section (optional) is GOLD—it accelerates usage directly.

---

## 6. Task Decomposition Guidelines
When writing issues, ensure each can produce a measurable artifact:

- Add / Modify / Remove specific functions (list names).
- Introduce new module with path & provisional API.
- Implement test(s) with explicit test file path & scenario list.
- Apply refactor using explicit rename/move semantics.

Bad: “Improve config system.”
Good: “Split aider/config.py into aider/config/resolver.py & aider/config/types.py; move parse_env() & parse_file() into resolver; add ConfigState dataclass.”

---

## 7. File & Code Referencing Best Practices (for Aider)
To maximize usefulness of Aider’s code mapping:

Include in issue body:
```
Target Files:
- aider/config.py (refactor loader into resolver)
- aider/models/base.py (add abstract method select() for fallback)
New Files:
- aider/models/selector.py
```

Prefer explicit function signatures:
- New: def select_model(models: list[ModelInfo], request: RequestContext) -> SelectedModel
- Modify: aider/llm.py:L145-L210 (wrap existing call chain with fallback handler)

---

## 8. Label & Workflow Conventions
Suggested GitHub Project Board Columns:
- Backlog
- Ready
- In Progress
- Review / AI Proposed
- Merged
- Verify (post-merge validation)
- Done

Automation Idea:
Use “AI Proposed” when PR/commit authored by Aider session (commit message prefix: Aider: …).

Commit Message Convention for Aider Sessions:
Aider: <area>: <short action>
Examples:
Aider: config: implement layered precedence resolution
Aider: tests: add degraded provider simulation

---

## 9. Branching & Integration Strategy
- Main: Always green, protected (CI: lint + tests).
- Feature Branch Naming: feat/<epic-key>/<short-desc> (feat/MMF/fallback-logic)
- AI session ephemeral branches (optional): ai/<issue-key>/<timestamp> merged via fast-forward or squash.
- Merge Policy: Squash merges for AI-generated multi-file edits; conventional merges for manual large feature streams.

---

## 10. Testing & Quality Gates
Introduce explicit test categories:
- unit/
- integration/
- scenario/ (AI multi-step flows)
Define in planning doc:
| Gate | Tool | Threshold |
|------|------|-----------|
| Lint | ruff | 0 errors |
| Type Check | mypy (if adopted) | strict in core modules |
| Tests | pytest | ≥95% pass |
| Coverage | coverage.py | core modules ≥85% |

Aider Issue Example for Test Gap:
[Tests] Add scenario tests for multi-model fallback under provider failure cascade.

---

## 11. Risk Register (Optional Section)
Keep brief; only include those affecting planning.

| Risk ID | Description | Impact | Likelihood | Mitigation | Owner |
|---------|-------------|--------|------------|------------|-------|
| R1 | Provider API schema changes | High | Medium | Adapter layer + contract tests | Core |
| R2 | Over-refactoring slows velocity | Medium | Medium | Enforce size labels & WIP limits | Lead |
| R3 | Insufficient community extension uptake | Medium | Low | Early example repos | Community |

---

## 12. Metrics & Observability Planning
Define instrumentation tasks as issues:
- MET-1 Add structured logs for model selection decisions.
- MET-2 Emit timing metrics around prompt/response cycle (prometheus exporter).
- MET-3 Track revert ratio of AI commits via git notes / label.

Each metric should have:
- Name
- Collection Mechanism
- Raw Unit
- Aggregation Dashboard (eg: Grafana panel ID)

---

## 13. Documentation Alignment
For each Epic, list required doc updates:
| Doc Page | Change Type | Trigger Issue |
|----------|-------------|---------------|
| docs/llms.html | Add fallback description | MMF-3 |
| docs/config.html | Precedence table | CFG-2 |
| HISTORY.html | Release note entry | Release Automation Issue |

---

## 14. Project Plan Master File Layout
Consider a single PROJECT_PLAN.md with anchor links:

```
# Project Plan
## 0 Snapshot
## 1 Vision
## 2 Goals
## 3 Milestones
## 4 Epics (index)
### Epic MMF
### Epic CFG
...
## 5 Issue Template
## 6 Decomposition Guidelines
## 7 Code Referencing
## 8 Workflow & Labels
## 9 Branching Strategy
## 10 Quality Gates
## 11 Risk Register
## 12 Metrics
## 13 Documentation Alignment
## 14 Glossary
```

Add Glossary for consistent naming:
- “Fallback”: automatic model selection after failure.
- “Resolver”: component that assembles final config state.
- etc.

---

## 15. Converting Existing Plan → This Format (Workflow)
1. Extract all existing goals → classify into Strategic Goals.
2. Group related intended features → Epics.
3. Assign Epics to Milestones based on sequencing & dependency.
4. For each Epic, generate initial Issue grid (3–10 issues).
5. For each Issue, apply template; add Suggested Aider Prompt.
6. Create labels & update or add GitHub Issue Templates.
7. Backfill risk, metrics, docs, glossary.

If you give me your current raw plan, I will:
- Normalize language (imperative, outcome-driven).
- Break vague items into atomic issue candidates.
- Add acceptance criteria suitable for AI execution.
- Produce ready-to-paste issue markdown bodies.

---

## 16. Example Full Issue (End-to-End)

````markdown
Title: [LLM] Add model capability taxonomy (MMF-1)

Summary:
Define a structured taxonomy describing LLM capabilities (context size, reasoning tier, cost bucket, tools supported) to enable fallback selection logic.

Context:
Goal: G4 (Reliability)
Epic: Multi-Model Fallback (MMF)
Milestone: M3

Files (new & existing):
- New: aider/models/capabilities.py
- Modify: aider/models/__init__.py (export registry)
- Future consumer: aider/llm.py (selection logic placeholder)

Acceptance Criteria:
- capabilities.py defines ModelCapability dataclass with fields:
  name: str
  max_context_tokens: int
  reasoning_tier: Literal["basic","advanced","reasoning"]
  cost_bucket: Literal["low","medium","high"]
  supports_images: bool
  supports_tools: bool
- Registry: get_model_capabilities() returns dict keyed by model slug.
- Include stubs for: sonnet, deepseek, gpt-4o, o3-mini.
- Unit tests: tests/models/test_capabilities_registry.py with at least:
  - test_registry_contains_expected_models
  - test_reasoning_tier_values
- Lint & tests pass.

Constraints:
No network calls; static definitions only.

Suggested Aider Prompt:
Create aider/models/capabilities.py implementing ModelCapability dataclass & get_model_capabilities() registry for 4 initial models: sonnet, deepseek, gpt-4o, o3-mini. Add tests in tests/models/test_capabilities_registry.py validating registry content & field constraints. Update aider/models/__init__.py to export get_model_capabilities. Keep all other files unchanged.

Dependencies:
None.

Risk:
Low.

Labels:
area/llm, type/feature, size/s, priority/p1
````

---

## 17. Validation Checklist Before Using Aider
Use this quick checklist to make sure an issue is “Aider-ready”:

- [ ] Scope ≤ ~3 functions or ≤ 2 files changed (for S/M size).
- [ ] Files explicitly named.
- [ ] Function/class signatures defined for new additions.
- [ ] Tests or acceptance criteria specify paths & scenarios.
- [ ] No ambiguous adjectives (“better”, “optimize”) without quantification.
- [ ] Dependencies listed if blocked.
- [ ] Suggested Aider Prompt included.

---

## 18. Optional: JSON/YAML for Automation
You can also maintain a machine-readable index for syncing into a GitHub Project or automations.

Example YAML (epic index):

```yaml
epics:
  - key: MMF
    title: Multi-Model Fallback Engine
    milestone: M3
    goal_links: [G4]
    issues:
      - key: MMF-1
        title: Define model capability taxonomy
        size: S
        priority: P1
        status: backlog
      - key: MMF-2
        title: Implement provider adapter interface
        size: M
        priority: P0
        status: backlog
```

---

