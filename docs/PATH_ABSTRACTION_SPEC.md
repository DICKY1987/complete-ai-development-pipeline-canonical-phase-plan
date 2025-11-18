# Path abstraction and indirection layer

This document defines the key→path indirection layer used by scripts and tools to
avoid hard‑coding repository paths. It complements `HARDCODED_PATH_INDEXER.md` and the
Section‑Aware Refactor plan.

## Goals

- Refer to important resources by stable keys, not physical paths.
- Centralize path changes in `config/path_index.yaml`.
- Provide a small Python resolver and a CLI to query keys.

## Artifacts

- Registry: `config/path_index.yaml` (authoritative mapping)
- Library: `src/path_registry.py` (load, cache, resolve, list)
- CLI: `scripts/paths_resolve_cli.py` (`resolve`, `list`, `debug`)

## Key format

- Dotted, namespaced keys: `namespace.item`, e.g. `phase_docs.ph02_state_layer_spec`.
- Namespaces group related keys (e.g., `phase_docs`, `docs`, `aider`, `error_docs`).

## Registry schema (YAML)

```yaml
paths:
  namespace:
    item:
      path: "repo/relative/path.ext"
      section: "section-name"
      description: "human description"
```

See current examples in `config/path_index.yaml`.

## Python usage

```python
from src.path_registry import resolve_path, list_paths

spec = resolve_path("phase_docs.ph02_state_layer_spec")
print(spec)

for key, path in list_paths(section="aider").items():
    print(key, path)
```

## CLI usage

```bash
python scripts/paths_resolve_cli.py resolve phase_docs.ph02_state_layer_spec
python scripts/paths_resolve_cli.py list --section aider
python scripts/paths_resolve_cli.py debug error_docs.operating_contract
```

## Error handling

- Unknown key → non‑zero exit and message `Unknown path key: ...`.
- Missing or malformed registry → clear error referencing expected location.

## Integration guidelines

- Do not introduce new hard‑coded paths in scripts. Add a registry key and use the resolver.
- When moving files during refactors, update only `config/path_index.yaml` and leave callers
  unchanged.
- Use the indexer (`scripts/paths_index_cli.py`) to find legacy hard‑coded paths and replace
  them progressively based on value/risk.

