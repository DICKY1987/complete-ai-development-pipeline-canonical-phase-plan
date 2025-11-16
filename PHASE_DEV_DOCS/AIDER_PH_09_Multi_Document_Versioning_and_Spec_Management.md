---
workstream_id: ph-09-spec-management
phase: PH-09
difficulty: hard
version_target: v1.0
depends_on: []
writable_globs:
  - "tools/spec_indexer/**/*.py"
  - "tools/spec_resolver/**/*.py"
  - "tools/spec_patcher/**/*.py"
  - "tools/spec_renderer/**/*.py"
  - "tools/spec_guard/**/*.py"
  - "schema/sidecar_metadata.schema.yaml"
  - "docs/SPEC_MANAGEMENT_CONTRACT.md"
  - "docs/source/**/*.md"
  - "docs/source/**/*.sidecar.yaml"
  - "templates/docs/*.template"
  - "scripts/spec_tools.py"
  - "tests/tools/test_spec_*.py"
readonly_globs:
  - "docs/ARCHITECTURE.md"
  - "docs/PHASE_PLAN.md"
  - "../Complete AI Development Pipeline – Canonical Phase Plan/Multi-Document Versioning Automation final_spec_docs/**/*"
---

# PH-09 – Multi-Document Versioning & Spec Management (Aider Workstream)

## 1. HEADER SUMMARY

**Workstream ID:** ph-09-spec-management
**Phase Reference:** PH-09
**Difficulty:** hard
**Version Target:** v1.0
**Dependencies:** None (operates on documentation layer)

## 2. ROLE & OBJECTIVE

Implement a multi-document versioning system with sidecar metadata files (.sidecar.yaml) that tracks document versions, resolves cross-document references, and validates conformance to templates. This file governs only the artifacts listed in Scope.

**Mission:** Create spec management tools (indexer, resolver, patcher, renderer, guard) that enable deterministic documentation versioning, cross-document linking via IDX tags, and automated conformance validation—making the documentation layer auditable and AI-agent-friendly.

## 3. SCOPE & FILE BOUNDARIES

### Writable Paths
```
tools/spec_indexer/indexer.py
tools/spec_indexer/__init__.py
tools/spec_resolver/resolver.py
tools/spec_resolver/__init__.py
tools/spec_patcher/patcher.py
tools/spec_patcher/__init__.py
tools/spec_renderer/renderer.py
tools/spec_renderer/__init__.py
tools/spec_guard/guard.py
tools/spec_guard/__init__.py
schema/sidecar_metadata.schema.yaml
docs/SPEC_MANAGEMENT_CONTRACT.md
docs/source/01-architecture/*.md
docs/source/01-architecture/*.sidecar.yaml
templates/docs/architecture.md.template
templates/docs/operating-contract.md.template
templates/docs/plugin-contract.md.template
templates/docs/data-contracts.md.template
templates/docs/process.md.template
templates/docs/conformance.md.template
templates/docs/policy.md.template
templates/docs/ci-cd-gates.md.template
templates/docs/observability-slos.md.template
templates/docs/reference.md.template
templates/docs/developer-experience.md.template
templates/docs/security-supply-chain.md.template
templates/docs/implementation-checklists.md.template
scripts/spec_tools.py
tests/tools/test_spec_indexer.py
tests/tools/test_spec_resolver.py
tests/tools/test_spec_patcher.py
tests/tools/test_spec_renderer.py
tests/tools/test_spec_guard.py
```

### Read-only Reference Paths
```
docs/ARCHITECTURE.md
docs/PHASE_PLAN.md
../Complete AI Development Pipeline – Canonical Phase Plan/Multi-Document Versioning Automation final_spec_docs/docs/source/**/*
```

### Explicitly Out of Scope
- **Do NOT** modify phase plan documents (PH-00 through PH-08)
- **Do NOT** modify code files in src/pipeline/
- **Do NOT** modify existing ARCHITECTURE.md or PHASE_PLAN.md (only append sections)
- **Do NOT** create new documentation categories beyond the 13 defined templates

**Note:** All non-listed files must remain unchanged.

## 4. ENVIRONMENT & PRECONDITIONS

**Project Root:** C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan
**Operating System:** Windows 10/11
**Python Version:** 3.12+
**Shell:** PowerShell 7+
**Version Control:** git

**Required Tools:**
- python (3.12+)
- pytest
- PyYAML (for sidecar parsing)
- jsonschema (for validation)
- markdown library (for parsing, optional)

**Required Prior Phases:**
- None (this phase operates on documentation layer)

**External Resources:**
- Multi-Document Versioning submodule at: `../Complete AI Development Pipeline – Canonical Phase Plan/Multi-Document Versioning Automation final_spec_docs`
- Contains example docs with sidecars

**Dependency Check:**
If Multi-Doc submodule missing:
- Can still implement tools
- Use placeholder examples
- Document in README that submodule provides reference implementation

## 5. TARGET ARTIFACTS & ACCEPTANCE CRITERIA

### [ARTIFACT] docs/SPEC_MANAGEMENT_CONTRACT.md
**Type:** doc
**Purpose:** Document multi-document versioning system
**Must Provide:**
- Overview of sidecar metadata system
- Sidecar format (.sidecar.yaml structure)
- Document categories (13 defined types)
- Cross-document linking (IDX tags, document_id references)
- Versioning scheme (semver for docs)
- Tools overview (indexer, resolver, patcher, renderer, guard)
- Contract version (SPEC_MGMT_V1)

**Must Not:**
- Specify implementation details of tools
- Mandate specific UI or rendering targets

**Acceptance Tests:**
- Doc exists with all 7 sections
- Contract version documented

**Determinism:**
- Sections ordered consistently
- Examples use stable data

---

### [ARTIFACT] schema/sidecar_metadata.schema.yaml
**Type:** schema
**Purpose:** YAML Schema for .sidecar.yaml validation
**Must Provide:**
- Required fields:
  - document_id: string (unique identifier)
  - title: string
  - version: string (semver format)
  - category: enum [13 categories]
  - last_updated: ISO 8601 timestamp
  - authors: array of strings
- Optional fields:
  - tags: array of strings
  - depends_on: array of document_ids
  - status: enum [draft, review, approved, deprecated]
  - checksum: string (SHA-256 of content)

**Must Not:**
- Allow arbitrary fields (additionalProperties: false)
- Permit invalid semver in version field

**Acceptance Tests:**
- Schema validates valid sidecar
- Schema rejects invalid sidecar (missing required fields)

**Determinism:**
- Fields ordered: required first, then optional

---

### [ARTIFACT] tools/spec_indexer/indexer.py
**Type:** code
**Purpose:** Discover and index all documentation
**Must Provide:**
- Functions:
  - get_docs_directory() -> Path
  - discover_documents(source_dir) -> list[Path]
  - load_sidecar(md_file) -> dict
  - validate_sidecar(sidecar_data) -> bool
  - generate_missing_sidecar(md_file) -> dict
  - build_index(source_dir) -> dict
  - write_index(index_data, output_path) -> None

**Must Not:**
- Modify source documents
- Crash on malformed sidecar (log error, skip doc)

**Acceptance Tests:**
- test_discover_documents
- test_load_sidecar_valid
- test_validate_sidecar_invalid
- test_generate_missing_sidecar
- test_build_index

**Determinism:**
- Index entries sorted by document_id
- Generated sidecars have stable default values

---

### [ARTIFACT] tools/spec_resolver/resolver.py
**Type:** code
**Purpose:** Resolve cross-document references
**Must Provide:**
- Functions:
  - load_index(index_path) -> dict
  - resolve_reference(ref, index) -> dict | None (returns {document_id, title, version, path})
  - find_broken_references(md_file, index) -> list[str]
  - inline_reference_content(ref, index) -> str | None

**Must Not:**
- Modify index or source documents

**Acceptance Tests:**
- test_resolve_reference_valid
- test_resolve_reference_invalid
- test_find_broken_references
- test_inline_reference_content

**Determinism:**
- Reference resolution deterministic (same ref → same result)

---

### [ARTIFACT] tools/spec_patcher/patcher.py
**Type:** code
**Purpose:** Apply structured patches to docs/sidecars
**Must Provide:**
- Functions:
  - load_patch(patch_path) -> dict
  - validate_patch(patch_data) -> bool
  - apply_version_bump(md_file, level) -> None (major|minor|patch)
  - apply_metadata_update(md_file, updates) -> None
  - apply_section_add(md_file, section_heading, content, position) -> None
  - apply_section_remove(md_file, section_heading) -> None

**Must Not:**
- Apply patches without validation
- Lose original content on error

**Acceptance Tests:**
- test_apply_version_bump
- test_apply_metadata_update
- test_apply_section_add
- test_apply_section_remove

**Determinism:**
- Same patch → same result
- Preserve line endings and formatting

---

### [ARTIFACT] tools/spec_renderer/renderer.py
**Type:** code
**Purpose:** Render unified documentation views
**Must Provide:**
- Functions:
  - render_category(index, category) -> str (markdown)
  - generate_toc(documents) -> str
  - resolve_inline_refs(content, index) -> str
  - render_to_format(content, format) -> str (markdown|html)

**Must Not:**
- Modify source documents
- Require external rendering services

**Acceptance Tests:**
- test_render_category
- test_generate_toc
- test_resolve_inline_refs

**Determinism:**
- TOC entries sorted by document_id
- Rendered output stable (same input → same output)

---

### [ARTIFACT] tools/spec_guard/guard.py
**Type:** code
**Purpose:** Validate document conformance
**Must Provide:**
- Functions:
  - check_required_sections(md_file, category) -> list[str] (missing sections)
  - check_cross_references(md_file, index) -> list[str] (broken refs)
  - check_version_conflicts(index) -> dict (conflicts)
  - generate_health_report(source_dir, index) -> dict

**Must Not:**
- Auto-fix errors (report only)
- Modify documents

**Acceptance Tests:**
- test_check_required_sections
- test_check_cross_references
- test_check_version_conflicts
- test_generate_health_report

**Determinism:**
- Reports sorted by document_id
- Stable error message format

---

### [ARTIFACT] templates/docs/*.template (13 templates)
**Type:** templates
**Purpose:** Document templates for each category
**Must Provide:**
- One .md.template for each of 13 categories:
  - architecture, operating-contract, plugin-contract, data-contracts, process, conformance, policy, ci-cd-gates, observability-slos, reference, developer-experience, security-supply-chain, implementation-checklists
- Each template includes:
  - Required section headings
  - Placeholder content with instructions
  - Example sidecar metadata in front-matter comment

**Must Not:**
- Enforce rigid structure (templates are guidelines)

**Acceptance Tests:**
- All 13 templates exist
- Each has required headings

---

### [ARTIFACT] docs/source/01-architecture/*.md + *.sidecar.yaml
**Type:** doc
**Purpose:** Sample documents with sidecars
**Must Provide:**
- Migrate or create 2 sample docs:
  - 00-overview.md + .sidecar.yaml
  - 01-microkernel-plugins.md + .sidecar.yaml
- Use content from Multi-Document Versioning submodule as reference

**Must Not:**
- Create extensive documentation (2 samples sufficient)

**Acceptance Tests:**
- Files exist and parse successfully
- Sidecars validate against schema

---

### [ARTIFACT] scripts/spec_tools.py
**Type:** script
**Purpose:** Unified CLI for all spec tools
**Must Provide:**
- Subcommands:
  - index: run spec_indexer
  - resolve: run spec_resolver
  - patch: run spec_patcher
  - render: run spec_renderer
  - guard: run spec_guard
- Usage: `python scripts/spec_tools.py <subcommand> [options]`

**Must Not:**
- Require interactive input (scriptable)

**Acceptance Tests:**
- `python scripts/spec_tools.py --help` shows usage
- Each subcommand runs without error

---

### [ARTIFACT] tests/tools/test_spec_*.py (5 test files)
**Type:** test
**Purpose:** Unit tests for spec tools
**Must Provide:**
- One test file per tool
- Use temp directories for test docs
- Coverage ≥ 80% for each tool module

**Acceptance Tests:**
- `pytest tests/tools/ -v` passes

## 6. OPERATIONS SEQUENCE (Atomic Steps)

### Step 1: Design Spec Management System
**Intent:** Plan tool architecture
**Files:** /read-only ../Complete AI Development Pipeline – Canonical Phase Plan/Multi-Document Versioning Automation final_spec_docs/
**Command:** `/architect`
**Prompt:**
```
Design multi-document versioning system with:

1. Sidecar metadata format (.sidecar.yaml)
2. Index structure (JSON with all doc metadata)
3. Cross-document references (IDX tags, document_id)
4. Tool responsibilities:
   - Indexer: discover, validate, build index
   - Resolver: resolve refs, find broken links
   - Patcher: version bump, section add/remove
   - Renderer: combine docs, generate views
   - Guard: validate conformance, health report

Constraints:
- Sidecar files version-controlled with .md files
- Deterministic (stable ordering, timestamps)
- No modification of source docs except by patcher

Output: Data structures + tool APIs
```
**Expected Outcome:** Architecture design
**Commit:** N/A (design step)

---

### Step 2: Implement Spec Management Contract
**Intent:** Document system overview
**Files:** /add docs/SPEC_MANAGEMENT_CONTRACT.md
**Command:** `/code`
**Prompt:**
```
Create docs/SPEC_MANAGEMENT_CONTRACT.md:

Sections:
1. Overview (multi-document versioning purpose)
2. Sidecar Metadata Format (required/optional fields)
3. Document Categories (13 types listed)
4. Cross-Document Linking (IDX tags, document_id refs)
5. Versioning Scheme (semver for docs)
6. Tools Overview (brief description of each tool)
7. Contract Version (SPEC_MGMT_V1)

Constraints:
- Markdown format
- Code blocks for YAML examples
- Clear field descriptions

Determinism:
- Sections in order listed
- Stable examples
```
**Expected Outcome:** Contract document
**Commit:** `docs(ph-09): add spec management contract`

---

### Step 3: Implement Sidecar Schema
**Intent:** Define metadata validation
**Files:** /add schema/sidecar_metadata.schema.yaml
**Command:** `/code`
**Prompt:**
```
Create schema/sidecar_metadata.schema.yaml:

YAML Schema (or JSON Schema in YAML format):

Required:
- document_id: string (pattern: ^[0-9]{2}-[a-z-]+/[0-9]{2}-[a-z-]+$)
- title: string
- version: string (semver pattern: ^\d+\.\d+\.\d+$)
- category: enum [architecture, operating-contract, plugin-contract, data-contracts, process, conformance, policy, ci-cd-gates, observability-slos, reference, developer-experience, security-supply-chain, implementation-checklists]
- last_updated: string (ISO 8601)
- authors: array of strings

Optional:
- tags, depends_on, status, checksum

additionalProperties: false

Constraints:
- Valid YAML syntax
- Clear descriptions for each field
```
**Expected Outcome:** Sidecar schema
**Commit:** `schema(ph-09): add sidecar metadata schema`

---

### Step 4: Implement Spec Indexer (Part 1)
**Intent:** Document discovery and sidecar loading
**Files:** /add tools/spec_indexer/indexer.py, tools/spec_indexer/__init__.py
**Command:** `/code`
**Prompt:**
```
Implement tools/spec_indexer/indexer.py:

Functions:

1. get_docs_directory() -> Path:
   - Return Path("docs/source")

2. discover_documents(source_dir: Path) -> list[Path]:
   - Walk source_dir recursively
   - Find all *.md files
   - Return sorted list

3. load_sidecar(md_file: Path) -> dict:
   - Check for md_file.with_suffix(".md.sidecar.yaml")
   - If exists: load YAML, return dict
   - If not: return None

Constraints:
- Use pathlib.Path
- Import yaml (PyYAML)
- Handle YAML parse errors (log, return None)
```
**Expected Outcome:** Indexer part 1 (discovery, loading)
**Commit:** `feat(ph-09): implement spec indexer discovery`

---

### Step 5: Implement Spec Indexer (Part 2)
**Intent:** Validation and index building
**Files:** /add tools/spec_indexer/indexer.py
**Command:** `/code`
**Prompt:**
```
Add to tools/spec_indexer/indexer.py:

4. validate_sidecar(sidecar_data: dict) -> bool:
   - Load schema from schema/sidecar_metadata.schema.yaml
   - Use jsonschema to validate
   - Return True if valid, False otherwise

5. generate_missing_sidecar(md_file: Path) -> dict:
   - Return default sidecar dict:
     - document_id: derive from path (e.g., "01-architecture/00-overview")
     - title: extract from first # heading in .md file
     - version: "1.0.0"
     - category: infer from directory name
     - last_updated: now (ISO 8601 UTC)
     - authors: ["pipeline"]

6. build_index(source_dir: Path) -> dict:
   - discover_documents()
   - For each doc: load_sidecar()
   - If no sidecar: generate_missing_sidecar()
   - Validate all sidecars
   - Build index dict: {"documents": [list of sidecar dicts]}
   - Return index

7. write_index(index_data: dict, output_path: Path) -> None:
   - Write as JSON with indent=2

Constraints:
- Use jsonschema for validation
- Deterministic field order in generated sidecars
```
**Expected Outcome:** Complete indexer
**Commit:** `feat(ph-09): complete spec indexer with validation`

---

### Step 6: Test Spec Indexer
**Intent:** Validate indexer functionality
**Files:** /add tests/tools/test_spec_indexer.py
**Command:** `/test`
**Prompt:**
```
Create tests/tools/test_spec_indexer.py:

Tests:
- test_discover_documents: temp dir with .md files
- test_load_sidecar_valid: load valid .sidecar.yaml
- test_load_sidecar_missing: returns None if no sidecar
- test_validate_sidecar_valid: valid sidecar passes
- test_validate_sidecar_invalid: invalid sidecar fails
- test_generate_missing_sidecar: creates default
- test_build_index: builds complete index

Run: pytest tests/tools/test_spec_indexer.py -v

Constraints:
- Use temp directories (pytest tmp_path)
- Mock schema validation if needed
```
**Expected Outcome:** All tests pass
**Commit:** `test(ph-09): add spec indexer tests`

---

### Step 7-11: Implement Remaining Tools
**Intent:** Create resolver, patcher, renderer, guard
**Files:** /add tools/spec_resolver/resolver.py, tools/spec_patcher/patcher.py, tools/spec_renderer/renderer.py, tools/spec_guard/guard.py
**Command:** `/code` (for each tool)
**Prompt Template:**
```
Implement tools/spec_<tool_name>/<tool_name>.py:

Functions: [list from acceptance criteria]

Logic:
- [Specific implementation details]

Constraints:
- [File scope, imports]

Determinism:
- [Ordering rules]
```
**Expected Outcome:** 4 additional tool modules
**Commit:** `feat(ph-09): implement spec <tool_name>`

---

### Step 12-16: Test Remaining Tools
**Intent:** Validate all tools
**Files:** /add tests/tools/test_spec_resolver.py, test_spec_patcher.py, test_spec_renderer.py, test_spec_guard.py
**Command:** `/test`
**Prompt:** Similar to Step 6 for each tool
**Expected Outcome:** All tests pass
**Commit:** `test(ph-09): add tests for spec <tool_name>`

---

### Step 17: Create Document Templates
**Intent:** Provide templates for each category
**Files:** /add templates/docs/architecture.md.template (and 12 others)
**Command:** `/code`
**Prompt:**
```
Create templates/docs/<category>.md.template for each of 13 categories:

Categories:
1. architecture
2. operating-contract
3. plugin-contract
4. data-contracts
5. process
6. conformance
7. policy
8. ci-cd-gates
9. observability-slos
10. reference
11. developer-experience
12. security-supply-chain
13. implementation-checklists

Template Structure:
- # [Title]
- ## Required Section 1
- [Placeholder content with instructions]
- ## Required Section 2
- [Placeholder content]
- <!-- Sidecar metadata example in comment -->

Constraints:
- Each template ≤ 100 lines
- Clear placeholder instructions
```
**Expected Outcome:** 13 template files
**Commit:** `feat(ph-09): add document templates for all categories`

---

### Step 18: Create Sample Documents
**Intent:** Migrate sample docs from submodule
**Files:** /add docs/source/01-architecture/00-overview.md, 00-overview.md.sidecar.yaml, 01-microkernel-plugins.md, 01-microkernel-plugins.md.sidecar.yaml
**Command:** `/code`
**Prompt:**
```
Create sample documents in docs/source/01-architecture/:

1. 00-overview.md:
   - Copy structure from Multi-Doc submodule
   - Adapt content to pipeline context
   - Keep brief (overview only)

2. 00-overview.md.sidecar.yaml:
   - document_id: "01-architecture/00-overview"
   - title: "Architecture Overview"
   - version: "1.0.0"
   - category: "architecture"
   - last_updated: [current ISO timestamp]
   - authors: ["pipeline"]

3. 01-microkernel-plugins.md:
   - Second architecture doc
   - References 00-overview

4. 01-microkernel-plugins.md.sidecar.yaml:
   - Similar structure
   - depends_on: ["01-architecture/00-overview"]

Constraints:
- Validate sidecars against schema
- Keep content concise (examples, not full docs)
```
**Expected Outcome:** 4 files (2 docs + 2 sidecars)
**Commit:** `docs(ph-09): add sample architecture documents`

---

### Step 19: Implement Spec Tools CLI
**Intent:** Unified interface for all tools
**Files:** /add scripts/spec_tools.py
**Command:** `/code`
**Prompt:**
```
Implement scripts/spec_tools.py:

Subcommands:
- index: calls spec_indexer.build_index()
  - Args: --source DIR, --output FILE
- resolve: calls spec_resolver.resolve_reference()
  - Args: --index FILE, --ref REF
- patch: calls spec_patcher.apply_* functions
  - Args: --doc FILE, --patch PATCH_JSON
- render: calls spec_renderer.render_category()
  - Args: --index FILE, --category CAT, --output FILE
- guard: calls spec_guard.generate_health_report()
  - Args: --source DIR, --index FILE, --report markdown|json

Use argparse for CLI parsing

Constraints:
- Clear help messages
- Exit codes: 0 success, 1 error
```
**Expected Outcome:** Unified CLI
**Commit:** `feat(ph-09): add spec tools CLI wrapper`

---

### Step 20: Update Documentation
**Intent:** Document spec management layer
**Files:** /add docs/ARCHITECTURE.md (append), docs/PHASE_PLAN.md (append)
**Command:** `/code`
**Prompt:**
```
Update docs/ARCHITECTURE.md:

Add section "Multi-Document Versioning & Spec Management":
- Role of sidecar metadata
- Spec tools overview (indexer, resolver, patcher, renderer, guard)
- Cross-document linking conventions
- Versioning scheme for docs
- Integration with phase plans

Update docs/PHASE_PLAN.md:

Add PH-09 section with:
- Summary
- Artifacts list
- Note: manages documentation layer
```
**Expected Outcome:** Documentation updated
**Commit:** `docs(ph-09): document spec management architecture`

---

### Step 21: Final Validation
**Intent:** Ensure all criteria met
**Command:** `/test`
**Run:**
```bash
pytest tests/tools/ -v
python scripts/spec_tools.py index --source docs/source --output docs/index.json
python scripts/spec_tools.py guard --source docs/source --index docs/index.json
```
**Expected Outcome:** Tests pass, tools run successfully

---

## 7. SLASH COMMAND PLAYBOOK

| Action | Command | Usage |
|--------|---------|-------|
| Design architecture | `/architect` | With requirements |
| Implement code | `/code` | Add files first |
| Inspect changes | `/diff` | After each step |
| Lint Python | `/lint` | After implementation |
| Run tests | `/test` | With pytest |
| Undo change | `/undo` | If wrong scope |
| Add reference | `/read-only` | For submodule |

## 8. PROMPT TEMPLATES

### Implementation Prompt
```
Implement [function_name] in tools/spec_<tool>/<tool>.py:

Logic:
- [Step-by-step algorithm]

Constraints:
- [Import restrictions]
- [File scope]

Determinism:
- [Ordering, formatting]
```

### Test Prompt
```
Test [tool_name]:

Test Cases:
- [List from criteria]

Setup:
- [Temp directories, fixtures]

Run: pytest tests/tools/test_spec_<tool>.py -v

Expected: All pass
```

## 9. SAFETY & GUARDRAILS

**Path Allowlist:**
- Only modify tools/, docs/source/, templates/docs/, tests/tools/

**No Edits to:**
- Phase plan documents (PH-00 through PH-08)
- Code in src/pipeline/

**Fail-Fast:**
- If Multi-Doc submodule missing: note in README, use placeholders

**Scope Violation:**
- If diff includes src/pipeline/ or phase plans: `/undo`

**Rollback Triggers:**
- Test failure: fix, re-test
- Invalid schema: revert schema changes

## 10. DETERMINISM & REPRODUCIBILITY

**Index Ordering:**
- Documents sorted by document_id

**Timestamps:**
- ISO 8601 UTC with "Z" suffix
- Only in sidecar last_updated field

**Generated Sidecars:**
- Stable default values
- Predictable document_id from path

**TOC Generation:**
- Entries sorted by document_id
- Stable heading format

## 11. TEST & VALIDATION MATRIX

| Criterion | Verification | Artifacts | Failure Handling |
|-----------|--------------|-----------|------------------|
| Indexer works | `pytest tests/tools/test_spec_indexer.py -v` | indexer.py | Fix discovery/validation |
| Resolver works | `pytest tests/tools/test_spec_resolver.py -v` | resolver.py | Fix reference resolution |
| Patcher works | `pytest tests/tools/test_spec_patcher.py -v` | patcher.py | Fix patch application |
| Renderer works | `pytest tests/tools/test_spec_renderer.py -v` | renderer.py | Fix rendering |
| Guard works | `pytest tests/tools/test_spec_guard.py -v` | guard.py | Fix validation |
| CLI runs | `python scripts/spec_tools.py --help` | spec_tools.py | Fix argument parsing |
| Schema validates | Validate sample sidecars | sidecar_metadata.schema.yaml | Fix schema |

## 12. COMPLETION CHECKLIST

- [ ] docs/SPEC_MANAGEMENT_CONTRACT.md exists with 7 sections
- [ ] schema/sidecar_metadata.schema.yaml defines metadata structure
- [ ] tools/spec_indexer/indexer.py implements 7 functions
- [ ] tools/spec_resolver/resolver.py implements 4 functions
- [ ] tools/spec_patcher/patcher.py implements 6 functions
- [ ] tools/spec_renderer/renderer.py implements 4 functions
- [ ] tools/spec_guard/guard.py implements 4 functions
- [ ] templates/docs/ contains 13 category templates
- [ ] docs/source/01-architecture/ has 2 sample docs with sidecars
- [ ] scripts/spec_tools.py provides unified CLI with 5 subcommands
- [ ] tests/tools/test_spec_*.py (5 files) all pass
- [ ] docs/ARCHITECTURE.md has spec management section
- [ ] docs/PHASE_PLAN.md has PH-09 section
- [ ] Git commit: `feat(ph-09): multi-document versioning and spec management`

**Final Commit Message:**
```
feat(ph-09): multi-document versioning and spec management

- Implement sidecar metadata system (.sidecar.yaml)
- Add 5 spec tools: indexer, resolver, patcher, renderer, guard
- Create 13 document category templates
- Enable cross-document linking via IDX tags
- Add version synchronization and conformance validation
- Provide unified CLI for all spec operations

🤖 Generated with Aider

Co-Authored-By: Aider <noreply@aider.com>
```

## 13. APPENDIX

### Crosswalk: Codex → Aider
| Codex | Aider |
|-------|-------|
| ROLE | Role & Objective |
| OPERATING CONTEXT | Environment & Preconditions |
| REQUIRED OUTPUTS | Target Artifacts |
| EXECUTION PLAN | Operations Sequence |
| CONSTRAINTS | Safety & Guardrails |

### Document Categories
```
13 categories (from Multi-Doc submodule):
01. architecture
02. operating-contract
03. plugin-contract
04. data-contracts
05. process
06. conformance
07. policy
08. ci-cd-gates
09. observability-slos
10. reference
11. developer-experience
12. security-supply-chain
13. implementation-checklists
```

### Sidecar Example
```yaml
document_id: "01-architecture/00-overview"
title: "Architecture Overview"
version: "1.0.0"
category: "architecture"
last_updated: "2025-01-16T12:00:00Z"
authors: ["pipeline"]
tags: ["overview", "system-design"]
depends_on: []
status: "approved"
checksum: "sha256:abc123..."
```

END OF WORKSTREAM
