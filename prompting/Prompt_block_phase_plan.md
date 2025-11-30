---
doc_id: DOC-GUIDE-PROMPT-BLOCK-PHASE-PLAN-438
---

# Prompt Block Development Phase Plan

This document tracks every phase of the prompt-block initiative in a consistent, patch-friendly format. Use Markdown-aware diffs (`apply_patch`) to update statuses, add deliverables, or append new phases without disturbing earlier history.

## Editing Notes
- Keep section order stable; append new phases at the end.
- Update the **Phase Index** table when adding or renaming phases.
- Use checkboxes to reflect completion so reviewers can see changes inline.
- Reference concrete repo paths (for traceability) when a deliverable lands.

## Phase Index
| Phase ID | Name | Goal | Status |
| --- | --- | --- | --- |
| PB-PHASE-00 | Inventory & Alignment | Capture current research + constraints | ✅ Complete |
| PB-PHASE-01 | Schema & Template Baseline | Define canonical PromptBlock schema + template references | 🔄 In Progress |
| PB-PHASE-02 | Registry Integration | Wire prompt blocks into pattern/template registry artifacts | ⏳ Planned |
| PB-PHASE-03 | Block Authoring Wave 1 | Produce initial prompt blocks for priority patterns/tools | ⏳ Planned |
| PB-PHASE-04 | Execution & QA Tooling | Automate rendering, validation, and regression tests | ⏳ Planned |
| PB-PHASE-05 | Rollout & Iteration | Embed in workflows, collect metrics, iterate | ⏳ Planned |

---

### Phase PB-PHASE-00 — Inventory & Alignment
**Goal:** Understand existing guidance, docs, and requirements surrounding prompt blocks.  
**Status:** ✅ Complete  
**Inputs:** `prompting/README.md`, `prompting/Promnt_Block/Prompt_block_ideas_1.md`, broader prompting references.  
**Deliverables:**
- [x] Summarize industry terms and desired structure (`Prompt_block_ideas_1.md`).
- [x] Document current directories and reference sources (`prompting/README.md`).
**Notes:** Provides the conceptual baseline that future phases build upon; no further action unless scope changes.

---

### Phase PB-PHASE-01 — Schema & Template Baseline
**Goal:** Define a machine-validated schema + canonical template for PromptBlock artifacts.  
**Status:** 🔄 In Progress  
**Focus Areas:**
1. Draft JSON Schema capturing sections described in `Prompt_block_ideas_1.md` (meta, context, inputs/outputs, guardrails, prompt template, etc.).
2. Map schema fields to execution pattern IDs (`PATTERN_INDEX.yaml`) and template IDs.
3. Provide example JSON + rendered markdown to act as reference implementations.
**Deliverables:**
- [ ] `prompting/Promnt_Block/schema/prompt_block.schema.json` (validated via `python -m jsonschema` or repo script).
- [ ] `prompting/Promnt_Block/templates/prompt_block_example.claude.json`.
- [ ] Authoring guide (`prompting/Promnt_Block/AUTHORING_NOTES.md`) describing required fields, versioning, and diff practices.
**Dependencies:** Needs confirmation of field names from pattern registry maintainers (`core/engine` + `patterns/registry`).  
**Exit Criteria:** Schema approved + referenced by at least one template file; validation command documented.

---

### Phase PB-PHASE-02 — Registry Integration
**Goal:** Connect prompt blocks to the existing registry/index artifacts so orchestrators can discover them automatically.  
**Status:** ⏳ Planned  
**Focus Areas:**
1. Extend registry documents (e.g., add `prompt_blocks` section to the pattern registry YAML).
2. Implement loader logic under `core/planning` or `core/engine` that resolves block metadata using `doc_id`, `pattern_id`, `template_id`, and `target_tool`.
3. Ensure Codebase Index references new files so other agents can locate them.
**Deliverables:**
- [ ] Updated registry file (likely `patterns/registry/PATTERN_INDEX.yaml`) with prompt block entries.
- [ ] Loader utility (`core/engine/prompt_blocks/loader.py` or similar) plus minimal tests in `tests/core/engine`.
- [ ] Documentation snippet in `docs/SECTION_REFACTOR_MAPPING.md` or dedicated README explaining lookup flow.
**Dependencies:** Requires Phase 01 schema + template definitions to be stable.  
**Exit Criteria:** Registry query returns prompt block metadata for at least one pattern/tool combo.

---

### Phase PB-PHASE-03 — Block Authoring Wave 1
**Goal:** Produce production-quality prompt blocks for the highest-value patterns and tools.  
**Status:** ⏳ Planned  
**Focus Areas:**
1. Prioritize `operation_kind`s (e.g., `CREATE_FILE`, `RUN_TESTS`, `PLAN_WORKSTREAM`) based on pipeline usage.
2. Author prompt block JSON per pattern/tool (Claude Code, Codex CLI, Copilot CLI, etc.).
3. Provide rendered prompt previews inside `prompting/Promnt_Block/rendered/` for human review.
**Deliverables:**
- [ ] Minimum of three prompt blocks covering distinct patterns (e.g., atomic create, worktree lifecycle, validation).
- [ ] Review checklist ensuring guardrails, context references, and expected outputs align with schema.
- [ ] Optional: helper script to render blocks to Markdown for reviewers.
**Dependencies:** Registry integration so orchestrators know where to find the blocks.  
**Exit Criteria:** Blocks referenced in live workstreams with positive review feedback.

---

### Phase PB-PHASE-04 — Execution & QA Tooling
**Goal:** Automate usage and validation to keep prompt blocks deterministic and regressions-free.  
**Status:** ⏳ Planned  
**Focus Areas:**
1. Add renderer utility (Python) that expands block JSON into final tool prompts; integrate into pipeline CLI.
2. Build regression harness (e.g., `tests/prompt_blocks/test_prompt_blocks.py`) with mocked inputs/outputs.
3. Hook into `scripts/validate_acs_conformance.py` or new script to ensure schema compliance pre-commit.
**Deliverables:**
- [ ] Renderer module stored under `core/engine/prompt_blocks/renderer.py`.
- [ ] Automated tests verifying schema validation + rendering accuracy.
- [ ] CI hook or script entry for `python scripts/validate_prompt_blocks.py`.
**Dependencies:** Requires stable set of authored blocks (Phase 03).  
**Exit Criteria:** CI fails if prompt blocks break schema or rendering; renderer is reusable by other tools.

---

### Phase PB-PHASE-05 — Rollout & Iteration
**Goal:** Embed prompt blocks in daily workflows, collect telemetry/feedback, and iterate.  
**Status:** ⏳ Planned  
**Focus Areas:**
1. Update documentation (`docs/`, `prompting/README.md`) with adoption guidance and troubleshooting.
2. Capture usage metrics or qualitative feedback from agents (Codex CLI, Claude Code, etc.).
3. Maintain backlog of improvements or new blocks based on pipeline evolution.
**Deliverables:**
- [ ] Updated docs with rollout instructions + FAQ.
- [ ] Feedback log (`prompting/Promnt_Block/feedback/feedback.md`) containing insights + action items.
- [ ] Versioned change log for prompt block schema/templates.
**Dependencies:** Requires execution tooling to be operational (Phase 04).  
**Exit Criteria:** Rollout docs published; improvement loop running with tracked metrics.

---

### Future Extensions / Parking Lot
- Potential `Phase 06` for cross-repo sharing if prompt blocks become multi-pipeline assets.
- Explore conversion to `.jsonl` or database-backed registry if counts grow large.
- Investigate automated linting for guardrails or blocked instructions.

