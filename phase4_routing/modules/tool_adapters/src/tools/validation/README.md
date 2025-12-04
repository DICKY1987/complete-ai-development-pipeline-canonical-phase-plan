---
doc_id: DOC-CORE-README-756
---

# Validation Tools

User-facing validation tools for checking repository health and conformance.

## Scripts

- **validate_acs_conformance.py** - Check AI Codebase Structure compliance
- **validate_workstreams.py** - Validate workstream JSON files
- **validate_engine.py** - Validate engine configuration
- **validate_diagrams.py** - Validate Mermaid diagrams
- **validate_plan.py** - Validate phase plans

## Usage

`ash
python tools/validation/validate_acs_conformance.py
python tools/validation/validate_workstreams.py
`
"@

    "tools\generation\README.md" = @"
# Generation Tools

Tools for generating documentation, indexes, and project artifacts.

## Scripts

- **generate_spec_index.py** - Generate specification index
- **generate_doc_index.py** - Generate documentation index
- **generate_workstreams.py** - Generate workstreams from specs
- **generate_repo_summary.py** - Generate repository summary

## Usage

`ash
python tools/generation/generate_spec_index.py
python tools/generation/generate_doc_index.py
`
"@

    "tools\pattern-extraction\README.md" = @"
# Pattern Extraction Tools

Extract execution patterns from CLI logs (Claude, Copilot, Aider) and generate UET templates.

## From UET Framework

These tools were migrated from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/pattern_extraction/

## Usage

See docs/uet/ for documentation on pattern extraction workflow.
