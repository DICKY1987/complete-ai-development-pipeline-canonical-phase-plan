---
doc_id: DOC-GUIDE-PH-09-MULTI-DOCUMENT-VERSIONING-AND-1239
---

TITLE: PH-09 – Multi-Document Versioning & Spec Management (Codex Autonomous Phase Executor)

ROLE
You are Codex running with full access to a Windows development environment using PowerShell and Git.
Your job is to COMPLETELY IMPLEMENT phase PH-09 (Multi-Document Versioning & Spec Management) for the AI Development Pipeline project, end-to-end, without requiring further user input.

You will:
- Implement a documentation versioning system with sidecar metadata files.
- Create tools for spec indexing, resolving, patching, rendering, and validation.
- Enable cross-document linking and version synchronization.
- Add schema validation for documentation conformance.
- Generate unified documentation views from multi-part specs.
- Keep the system deterministic, auditable, and AI-agent-friendly.

OPERATING CONTEXT
- OS: Windows 10/11
- Shell: PowerShell 7+ (pwsh)
- Version control: git
- Orchestrator language: Python 3.12+
- Previous phases:
  - PH-00: project skeleton, docs, CI.
  - PH-01: spec index & canonical module layout.
  - PH-02: SQLite DB + state machine (db.py).
  - PH-03: Tool profiles & adapter layer.
  - PH-03.5: Aider integration & prompt engine.
  - PH-04: Workstream bundle parsing & validation.
  - PH-04.5: Git worktree lifecycle.
  - PH-05: Orchestrator core loop.
  - PH-05.5: Workstream authoring & validation.
  - PH-06: Circuit breakers, retries & fix loop.

PROJECT ROOT (IMPORTANT)
- Expected project root: C:/Users/richg/ALL_AI/AI_Dev_Pipeline
- Multi-Doc Versioning source: C:/Users/richg/ALL_AI/Complete AI Development Pipeline – Canonical Phase Plan/Multi-Document Versioning Automation final_spec_docs

If project root does NOT exist:
- Stop and write a clear, prominent note into docs/PHASE_PLAN.md under PH-09 that PH-00–PH-06 must be completed first.
- Do NOT attempt to implement spec management elsewhere.

If it DOES exist:
- cd into that folder and proceed.

====================================
HIGH-LEVEL GOAL OF PH-09
====================================

Create a **multi-document versioning and spec management system** that:

1) **Tracks document versions** using sidecar YAML metadata files (.sidecar.yaml).
2) **Indexes all specs** with structured metadata (title, version, category, dependencies).
3) **Resolves cross-document references** (e.g., IDX-DB-001 → db.py design doc).
4) **Patches documents** to update versions, add/remove sections, sync changes.
5) **Renders unified views** from multi-part specs (e.g., combine architecture docs).
6) **Validates conformance** to templates and schemas.
7) **Supports AI agents** with clear, deterministic metadata and linking.

This system manages the **documentation layer** above all phase plans, architecture docs, contracts, and specifications.

====================================
REQUIRED OUTPUTS OF THIS PHASE
====================================

By the end of PH-09, the repo MUST have at minimum:

1) SPEC MANAGEMENT CONTRACT DOCUMENT
- docs/SPEC_MANAGEMENT_CONTRACT.md
  - Explains the multi-document versioning system.
  - Documents:
    - Sidecar metadata format (.sidecar.yaml).
    - Document categories (architecture, operating-contract, plugin-contract, etc.).
    - Cross-document linking conventions (IDX tags, references).
    - Versioning scheme (semver for docs).
    - Tools overview (indexer, resolver, patcher, renderer, guard).
    - Contract version (e.g., "SPEC_MGMT_V1").

2) SIDECAR METADATA SCHEMA
- schema/sidecar_metadata.schema.yaml
  - YAML Schema (or JSON Schema) defining structure of .sidecar.yaml files.
  - Required fields:
    - document_id: unique identifier (e.g., "01-architecture/00-overview")
    - title: human-readable title
    - version: semver string (e.g., "1.0.0")
    - category: category name (from docs/source/ structure)
    - last_updated: ISO 8601 timestamp
    - authors: list of author names/IDs
  - Optional fields:
    - tags: list of strings
    - depends_on: list of document_ids this doc references
    - status: draft|review|approved|deprecated
    - checksum: hash of document content (for change detection)
  - Validation rules for each field.

3) SPEC INDEXER
- tools/spec_indexer/indexer.py
  - Responsibilities:
    - Walk docs/source/ directory tree.
    - For each .md file:
      - Check for corresponding .sidecar.yaml.
      - If missing, generate default sidecar with placeholders.
      - If present, validate against schema.
    - Build global index:
      - index.json with list of all documents and their metadata.
    - Detect orphan sidecars (sidecar without .md file).
    - Detect missing sidecars (.md without sidecar).

  - CLI:
    - python tools/spec_indexer/indexer.py --source docs/source --output docs/index.json
    - Options:
      - --validate-only: validate sidecars without writing index
      - --generate-missing: create default sidecars for docs without them
      - --strict: fail on any validation error

4) SPEC RESOLVER
- tools/spec_resolver/resolver.py
  - Responsibilities:
    - Resolve cross-document references.
    - Parse IDX tags (e.g., IDX-DB-001) or document_id references.
    - Look up metadata from index.json.
    - Return path, title, version for referenced doc.
    - Detect broken references (target doc not found).
    - Optionally inline referenced content (for rendering).

  - CLI:
    - python tools/spec_resolver/resolver.py --index docs/index.json --ref "IDX-DB-001"
    - Options:
      - --format: output format (json|markdown|text)
      - --inline: include content of referenced doc in output

5) SPEC PATCHER
- tools/spec_patcher/patcher.py
  - Responsibilities:
    - Apply structured patches to documents and sidecars.
    - Patch types:
      - version_bump: increment version (major|minor|patch)
      - update_metadata: change fields in sidecar (e.g., status, authors)
      - add_section: insert new section at specified location
      - remove_section: delete section by heading
      - sync_dependency: update depends_on list
    - Validate patch operations against schema.
    - Optionally create git commit for each patch.

  - CLI:
    - python tools/spec_patcher/patcher.py --doc docs/source/01-architecture/00-overview.md --patch patch.json
    - patch.json example:
      ```json
      {
        "type": "version_bump",
        "level": "minor"
      }
      ```
    - Options:
      - --dry-run: show what would change without modifying files
      - --commit: create git commit after patch

6) SPEC RENDERER
- tools/spec_renderer/renderer.py
  - Responsibilities:
    - Render unified documentation views.
    - Combine multiple docs based on category or depends_on graph.
    - Generate table of contents with cross-links.
    - Apply templates (e.g., wrap content in HTML/PDF template).
    - Resolve IDX tags inline (replace with links or content).
    - Output formats: markdown, HTML, PDF (via markdown-to-pdf).

  - CLI:
    - python tools/spec_renderer/renderer.py --index docs/index.json --category architecture --output docs/rendered/architecture.md
    - Options:
      - --template: template file for output format
      - --include-toc: generate table of contents
      - --resolve-refs: inline resolve all IDX tags
      - --format: output format (markdown|html|pdf)

7) SPEC GUARD
- tools/spec_guard/guard.py
  - Responsibilities:
    - Validate document conformance to templates.
    - Check that required sections are present.
    - Verify cross-references are valid (no broken links).
    - Enforce naming conventions (file names match document_id).
    - Detect version conflicts (two docs claiming same version).
    - Report on documentation health (coverage, staleness, broken links).

  - CLI:
    - python tools/spec_guard/guard.py --source docs/source --index docs/index.json
    - Options:
      - --check-sections: validate required sections per category
      - --check-refs: validate all cross-references
      - --check-versions: detect version conflicts
      - --report: output validation report (json|markdown)

8) DOCUMENT TEMPLATES
- templates/docs/
  - Template files for each category:
    - architecture.md.template
    - operating-contract.md.template
    - plugin-contract.md.template
    - data-contracts.md.template
    - process.md.template
    - conformance.md.template
    - policy.md.template
    - ci-cd-gates.md.template
    - observability-slos.md.template
    - reference.md.template
    - developer-experience.md.template
    - security-supply-chain.md.template
    - implementation-checklists.md.template

  - Each template includes:
    - Required section headings.
    - Placeholder content with instructions.
    - Sidecar metadata example.

9) SAMPLE DOCUMENTATION WITH SIDECARS
- Migrate existing docs to new system:
  - docs/source/01-architecture/00-overview.md + .sidecar.yaml
  - docs/source/01-architecture/01-microkernel-plugins.md + .sidecar.yaml

  - Use Multi-Document Versioning submodule content as examples.

10) UNIT TESTS
- tests/tools/test_spec_indexer.py
  - Test indexer with temp docs directory.
  - Test:
    - Indexing docs with sidecars.
    - Generating missing sidecars.
    - Detecting orphan sidecars.
    - Validating against schema.

- tests/tools/test_spec_resolver.py
  - Test resolver with temp index.
  - Test:
    - Resolving valid references.
    - Detecting broken references.
    - Inlining content.

- tests/tools/test_spec_patcher.py
  - Test patcher with temp docs.
  - Test:
    - Version bumps (major, minor, patch).
    - Metadata updates.
    - Section add/remove.
    - Dry-run mode.

- tests/tools/test_spec_renderer.py
  - Test renderer with temp docs.
  - Test:
    - Rendering single category.
    - Combining multiple docs.
    - Generating TOC.
    - Resolving refs inline.

- tests/tools/test_spec_guard.py
  - Test guard with temp docs.
  - Test:
    - Section validation.
    - Cross-reference checking.
    - Version conflict detection.

11) CLI WRAPPER
- scripts/spec_tools.py
  - Unified CLI for all spec tools.
  - Subcommands:
    - index: run spec_indexer
    - resolve: run spec_resolver
    - patch: run spec_patcher
    - render: run spec_renderer
    - guard: run spec_guard
  - Example:
    - python scripts/spec_tools.py index --source docs/source --output docs/index.json
    - python scripts/spec_tools.py guard --source docs/source --index docs/index.json --report markdown

12) DOCUMENTATION UPDATES
- docs/ARCHITECTURE.md:
  - Add "Multi-Document Versioning & Spec Management" section describing:
    - Role of sidecar metadata.
    - Spec tools (indexer, resolver, patcher, renderer, guard).
    - Cross-document linking conventions.
    - Versioning scheme for documentation.
    - Integration with phase plans and contracts.

- docs/PHASE_PLAN.md:
  - Flesh out PH-09 section with:
    - Summary of spec management system.
    - List of artifacts:
      - docs/SPEC_MANAGEMENT_CONTRACT.md
      - schema/sidecar_metadata.schema.yaml
      - tools/spec_indexer/
      - tools/spec_resolver/
      - tools/spec_patcher/
      - tools/spec_renderer/
      - tools/spec_guard/
      - templates/docs/
      - scripts/spec_tools.py
      - tests/tools/test_spec_*.py
    - Note: This system manages documentation layer above code artifacts.

13) GIT COMMIT
- Stage all new/modified files.
- Commit with message:
  - "PH-09: multi-document versioning and spec management"
- Do NOT push (remote configuration is out of scope).

====================================
CONSTRAINTS & PRINCIPLES
====================================

- Do NOT break or remove outputs from PH-00–PH-06; only extend them.
- Sidecar files are version-controlled alongside .md files.
- Deterministic metadata:
  - Timestamps use ISO 8601 UTC with "Z" suffix.
  - Checksums use SHA-256.
  - Sorting: always alphabetical or version order.
- Cross-document references:
  - Use IDX tags or document_id references (not relative file paths).
  - Validate all references before commit.
- Templates are guidelines, not rigid schemas:
  - Docs may deviate from templates if justified.
  - Guard should warn, not fail, on minor deviations.
- Keep tools modular:
  - Each tool (indexer, resolver, etc.) is independent.
  - Tools use index.json as shared data structure.
- Support both manual and automated workflows:
  - Tools have CLI for manual use.
  - Tools have Python APIs for automation.

Implementation details:
- Use YAML for sidecar metadata (human-friendly, comment support).
- Use JSON for index.json (machine-friendly, fast parsing).
- Use PyYAML for YAML parsing.
- Use jsonschema for schema validation.
- Use pathlib.Path for all file paths.
- For markdown parsing: use markdown library or simple regex for headings.
- For PDF rendering: use markdown-pdf or weasyprint (optional; document if not implemented).

====================================
EXECUTION PLAN (WHAT YOU SHOULD DO)
====================================

You should:

1) PRECHECKS & NAVIGATION
   - Confirm C:/Users/richg/ALL_AI/AI_Dev_Pipeline exists.
   - cd C:/Users/richg/ALL_AI/AI_Dev_Pipeline
   - Confirm Multi-Document Versioning submodule exists at expected location.
   - Confirm docs/, tools/, schema/, templates/ exist; if not, create them.

2) WRITE SPEC MANAGEMENT CONTRACT DOC
   - Create docs/SPEC_MANAGEMENT_CONTRACT.md with:
     - Overview of multi-document versioning.
     - Sidecar metadata format.
     - Document categories.
     - Cross-document linking.
     - Versioning scheme.
     - Tools overview.
     - Contract version.

3) CREATE SIDECAR METADATA SCHEMA
   - Create schema/sidecar_metadata.schema.yaml with:
     - Required and optional fields.
     - Validation rules.

4) IMPLEMENT SPEC INDEXER
   - Create tools/spec_indexer/indexer.py with:
     - Document discovery.
     - Sidecar validation.
     - Index generation.
     - CLI interface.

5) IMPLEMENT SPEC RESOLVER
   - Create tools/spec_resolver/resolver.py with:
     - Reference resolution.
     - Broken link detection.
     - Content inlining.
     - CLI interface.

6) IMPLEMENT SPEC PATCHER
   - Create tools/spec_patcher/patcher.py with:
     - Version bumping.
     - Metadata updates.
     - Section manipulation.
     - Dry-run mode.
     - CLI interface.

7) IMPLEMENT SPEC RENDERER
   - Create tools/spec_renderer/renderer.py with:
     - Category-based rendering.
     - TOC generation.
     - Reference resolution.
     - Output formats (markdown, HTML).
     - CLI interface.

8) IMPLEMENT SPEC GUARD
   - Create tools/spec_guard/guard.py with:
     - Section validation.
     - Reference checking.
     - Version conflict detection.
     - Health reporting.
     - CLI interface.

9) CREATE DOCUMENT TEMPLATES
   - Create templates/docs/ directory.
   - Create template files for each category.
   - Include sidecar examples.

10) MIGRATE SAMPLE DOCS
    - Copy sample docs from Multi-Document Versioning submodule to docs/source/.
    - Ensure each has corresponding .sidecar.yaml.
    - Run indexer to validate.

11) ADD TESTS
    - Implement tests/tools/test_spec_indexer.py.
    - Implement tests/tools/test_spec_resolver.py.
    - Implement tests/tools/test_spec_patcher.py.
    - Implement tests/tools/test_spec_renderer.py.
    - Implement tests/tools/test_spec_guard.py.

12) CREATE CLI WRAPPER
    - Create scripts/spec_tools.py with subcommands for all tools.

13) RUN TESTS
    - From project root:
      - Run: pytest tests/tools/
    - Fix any failing tests before marking PH-09 complete.

14) UPDATE DOCS
    - Update docs/ARCHITECTURE.md with spec management section.
    - Update docs/PHASE_PLAN.md with detailed PH-09 description.

15) GIT COMMIT
    - Stage and commit with message:
      - "PH-09: multi-document versioning and spec management"

====================================
PHASE COMPLETION CHECKLIST
====================================

Before you consider PH-09 done, ensure all of the following are true:

[ ] docs/SPEC_MANAGEMENT_CONTRACT.md exists and documents sidecar format, categories, linking, versioning, tools, and contract version
[ ] schema/sidecar_metadata.schema.yaml exists and defines sidecar structure with validation rules
[ ] tools/spec_indexer/indexer.py implements document discovery, sidecar validation, and index generation
[ ] tools/spec_resolver/resolver.py implements reference resolution and broken link detection
[ ] tools/spec_patcher/patcher.py implements version bumping, metadata updates, and section manipulation
[ ] tools/spec_renderer/renderer.py implements category-based rendering, TOC generation, and output formats
[ ] tools/spec_guard/guard.py implements section validation, reference checking, and health reporting
[ ] templates/docs/ contains template files for all document categories
[ ] docs/source/ contains sample documents with .sidecar.yaml files
[ ] scripts/spec_tools.py provides unified CLI for all spec tools
[ ] tests/tools/test_spec_indexer.py exists and passes
[ ] tests/tools/test_spec_resolver.py exists and passes
[ ] tests/tools/test_spec_patcher.py exists and passes
[ ] tests/tools/test_spec_renderer.py exists and passes
[ ] tests/tools/test_spec_guard.py exists and passes
[ ] docs/ARCHITECTURE.md has a "Multi-Document Versioning & Spec Management" section
[ ] docs/PHASE_PLAN.md has an updated PH-09 section listing artifacts and behavior
[ ] A git commit with message like "PH-09: multi-document versioning and spec management" has been created

====================================
INTERACTION STYLE
====================================

- Do NOT ask the user questions unless you are completely blocked.
- Make reasonable assumptions and document them in:
  - docs/SPEC_MANAGEMENT_CONTRACT.md
  - schema/sidecar_metadata.schema.yaml
  - docs/PHASE_PLAN.md (PH-09 section)
- When you output your response, clearly separate:
  - PowerShell commands you would run.
  - Python, YAML, JSON, and Markdown file contents you would create or modify.

END OF PROMPT
