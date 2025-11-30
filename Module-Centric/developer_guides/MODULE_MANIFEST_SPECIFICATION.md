---
doc_id: DOC-GUIDE-MODULE-MANIFEST-SPECIFICATION-1451
---

# Module Manifest Specification

Canonical format for `modules/<module>/module.manifest.json|yaml`. One manifest per module; it is
the source of truth for identity, dependencies, and artifacts.

## File Naming
- Preferred: `module.manifest.json` (or `.yaml`), stored at the module root.
- ULID artifacts share the same 6-char prefix; manifest lists them explicitly.

## Required Fields
- `module_id` (string): import-safe name, e.g., `core-engine`.
- `ulid_prefix` (string): 6-char ULID prefix, e.g., `010001`.
- `version` (string): semantic version of the module contract.
- `description` (string): short human-readable summary.
- `owners` (list[string]): emails/handles.
- `dependencies.modules` (list[string]): other module_ids.
- `artifacts.code` (list[path]): ULID-prefixed code files.
- `artifacts.tests` (list[path]): colocated tests.
- `artifacts.schemas` (list[path]): JSON/YAML schemas.
- `artifacts.docs` (list[path]): README/notes for this module.
- `state.current` (path): path to `.state/current.json`.
- `entry_points` (optional, list[object]):
  - `name` (string), `path` (string), `type` (enum: cli | api | task | worker).
- `tags` (optional, list[string]): e.g., `layer:domain`, `type:plugin`.

## Constraints and Validation
- `module_id` must match directory name and `__init__.py` package name.
- `ulid_prefix` must match all ULID-prefixed artifacts listed.
- Dependencies must resolve to existing module_ids in `MODULES_INVENTORY.yaml`.
- Artifacts must be relative to the module root and exist (or be generated in the same PR).
- `state.current` must live under the module’s `.state/`.

## Example (JSON)
```json
{
  "module_id": "core-engine",
  "ulid_prefix": "010001",
  "version": "1.0.0",
  "description": "Execution engine orchestrator",
  "owners": ["team-core@example.com"],
  "dependencies": {
    "modules": ["core-state", "core-planning", "aim-environment"]
  },
  "artifacts": {
    "code": ["010001_orchestrator.py", "010001_scheduler.py"],
    "tests": ["010001_orchestrator.test.py"],
    "schemas": [],
    "docs": ["010001_README.md"]
  },
  "state": {
    "current": ".state/current.json"
  },
  "entry_points": [
    {"name": "orchestrate", "path": "010001_orchestrator.py", "type": "api"}
  ],
  "tags": ["layer:domain"]
}
```

## Lifecycle
- Author/update manifest before generating DAGs.
- Validate: `python scripts/validate_modules.py modules`
- Regenerate DAGs after manifest changes: `python scripts/refresh_repo_dag.py`
