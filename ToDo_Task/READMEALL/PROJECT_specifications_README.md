# Specifications Directory

This directory contains all specification documents and tools for managing them.

## Structure

- **`content/`** - Specification documents organized by domain
  - `orchestration/` - Pipeline orchestration specs
  - `plugin-system/` - Plugin architecture specs
  - `validation-pipeline/` - Validation flow specs

- **`changes/`** - Active OpenSpec change proposals
  - Each change has `proposal.md`, `tasks.md`, and modified specs

- **`archive/`** - Completed and historical changes

- **`tools/`** - Specification processing utilities
  - `indexer/` - Generate indices and sidecars
  - `resolver/` - Resolve spec URIs (spec://, specid://)
  - `guard/` - Validate consistency
  - `patcher/` - Update paragraphs by ID
  - `renderer/` - Render specs to Markdown

- **`.index/`** - Generated index files (gitignored)
  - `suite-index.yaml` - Main specification index
  - `document-index.json` - Document metadata

- **`bridge/`** - OpenSpec → Workstream integration
  - Documentation on converting specs to workstreams

- **`schemas/`** - Metadata validation schemas

## Workflow

1. **Create change proposal**: `/openspec:proposal "Feature description"`
2. **Convert to workstream**: `python scripts/spec_to_workstream.py --interactive`
3. **Execute**: `python scripts/run_workstream.py --ws-id ws-feature-x`
4. **Archive**: After completion, move from `changes/` to `archive/`

## Tools Usage

```bash
# Generate indices
python specifications/tools/indexer/indexer.py --source specifications/content

# Resolve spec URI
python specifications/tools/resolver/resolver.py spec://VOLUME/SECTION

# Validate consistency
python specifications/tools/guard/guard.py

# Render to Markdown
python specifications/tools/renderer/renderer.py --output rendered_spec.md
```

## Import Paths

```python
from specifications.tools.indexer.indexer import generate_index
from specifications.tools.resolver.resolver import resolve_spec_uri
from specifications.tools.guard.guard import validate_suite
```

## Migration

This directory was created by consolidating:
- `openspec/` - Specification content and change management
- `spec/` - Specification processing tools

See `scripts/migrate_spec_folders.py` for migration details.
