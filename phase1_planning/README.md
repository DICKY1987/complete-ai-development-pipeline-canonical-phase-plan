# Phase 1 – Planning & Spec Alignment

**Purpose**: Take OpenSpec + PM epics + plan docs → workstreams + phase plans.

## Current Components
- See `specifications/` for spec content
- See `SPEC_tools/` for spec processing tools
- See `plans/` for phase plans

## Main Operations
- Ingest OpenSpec, PM epics, phase docs
- Validate specs & build spec index + dependency graph
- Convert accepted specs into workstream JSON
- Link specs and workstreams back to CCPM/PM issues

## Related Code
- `core/openspec_parser.py`, `openspec_convert.py`, `spec_index.py`
- `specifications/` content
- `specs_index.json`, `specs_mapping.json`
